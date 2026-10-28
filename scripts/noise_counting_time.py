"""Unit B, counting time: is a committed VGD's stored intensity (Counts / s) a whole number of counts divided by
one effective counting time T? Read-only measurement over every committed .VGD (275 files).

1. The acquisition parameters each file records (scripts/vgd_properties.py): dwell, scans, pass energy, step,
   points, start / end — and how the elapsed time relates to points × dwell × scans (least squares).
2. An EXACT test, no search heuristic: the values are counts / T for a common T in a range iff there are integers
   N_i with |y_i − N_i / T| ≤ δ_i for every point, δ_i = 2 ulp(y_i) (up to four half-ulp roundings of the
   division). Every constraint is applied in exact rational arithmetic (fractions.Fraction) to the set of
   admissible T — a union of intervals — first each gap between neighbouring distinct values (a gap must be
   a positive multiple of 1/T: narrows T cheaply), then each value (pins the lattice at 0). An empty set
   proves no such T exists in the range (under that δ); a non-empty one lists every admissible T.
   Ranges: (a) every T up to the acquisition's own elapsed time + 1 s (timestamps are whole seconds): one
   energy can be counted for at most the time the acquisition lasted, whatever the detector does in
   parallel; (b) each decoded candidate T = c × scans × dwell, c = 1 … 1024 (a channel or pass count),
   whatever its length, in a band covering the float32 dwell and its decimal.
3. "Integer-like" (approximate), at each candidate T: the Rayleigh statistic R = |mean exp(2πi y T)| over the
   m points with y·T ≤ 1e5 (≈ 1 for near-integers; for phases with no structure m·R² is asymptotically Exp(1),
   p = exp(−m R²)); the family of 1024 candidates is judged by Bonferroni: integer-like at 1 % iff
   1024 · min p < 0.01.
4. Does each region's estimated noise scale k (variance = k·y, scripts/noise_estimators.py) follow 1/(dwell ×
   scans), as counting noise over those times would?

    venv/bin/python scripts/noise_counting_time.py [--json OUT.json] > OUT.txt
"""
import argparse
import collections
import json
import math
import os
import re
import subprocess
import sys
from fractions import Fraction

import numpy as np
import olefile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import noise_estimators as ne  # noqa: E402
import vgd_parser  # noqa: E402
import vgd_properties as vp  # noqa: E402

C_MAX = 1024
RAYLEIGH_U_MAX = 1e5
NOMINAL_DWELL = {np.float32(0.05): Fraction(1, 20), np.float32(0.01): Fraction(1, 100)}
INTERVAL_CAP = 200_000          # a constraint that would split the set into more pieces is deferred


def _merge(iv):
    iv.sort()
    out = []
    for lo, hi in iv:
        if out and lo <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], hi))
        else:
            out.append((lo, hi))
    return out


def _apply(iv, v, d, n_min):
    """Intersect the admissible-T set with {T: some integer N ≥ n_min has |v·T − N| ≤ d·T}, i.e.
    T ∈ [N/(v+d), N/(v−d)] (exact). Returns None when the constraint would split too finely (deferred)."""
    lo_v, hi_v = v - d, v + d
    count = sum(max(0, math.floor(hi_v * hi) - max(n_min, math.ceil(lo_v * lo)) + 1) for lo, hi in iv)
    if count > INTERVAL_CAP:
        return None
    out = []
    for lo, hi in iv:
        for n in range(max(n_min, math.ceil(lo_v * lo)), math.floor(hi_v * hi) + 1):
            a = Fraction(n) / hi_v
            b = Fraction(n) / lo_v if lo_v > 0 else hi
            a, b = max(a, lo), min(b, hi)
            if a <= b:
                out.append((a, b))
    return _merge(out)


def admissible_times(y, ranges):
    """Every T in ``ranges`` (list of (lo, hi) Fractions) for which each y_i is within δ_i = 2 ulp(y_i) of a
    whole number / T. Exact; [] proves there is none. Returns (intervals, constraints applied, deferred)."""
    y = np.asarray(y, float)
    if (y < 0).any():
        return [], 0, 0                                           # a count is never negative
    vals = [Fraction(float(v)) for v in np.unique(y)]
    dlt = [Fraction(float(2 * np.spacing(float(v)))) for v in np.unique(y)]
    gaps = sorted(((vals[i + 1] - vals[i], dlt[i] + dlt[i + 1]) for i in range(len(vals) - 1)),
                  key=lambda g: g[0])
    cons = [(g, e, 1) for g, e in gaps if g > e]                    # a resolvable gap: a positive multiple of 1/T
    cons += sorted(((v, e, 0) for v, e in zip(vals, dlt) if v > e), key=lambda c: c[0])
    iv = _merge([(Fraction(lo), Fraction(hi)) for lo, hi in ranges])
    applied, pending = 0, cons
    while pending and iv:
        later = []
        for v, e, n_min in pending:
            new = _apply(iv, v, e, n_min)
            if new is None:
                later.append((v, e, n_min))
                continue
            iv, applied = new, applied + 1
            if not iv:
                break
        if len(later) == len(pending):
            return iv, applied, len(later)                         # nothing narrowed further: report what is left
        pending = later
    return iv, applied, 0


def gap_bound(y):
    """Smallest T compatible with the smallest resolvable gap (exact): T ≥ 1 / (gap + δ_a + δ_b)."""
    u = np.unique(np.asarray(y, float))
    best = None
    for a, b in zip(u[:-1], u[1:]):
        g = Fraction(float(b)) - Fraction(float(a))
        e = Fraction(float(2 * np.spacing(float(a)))) + Fraction(float(2 * np.spacing(float(b))))
        if g > e:
            t = 1 / (g + e)
            best = t if best is None or t > best else best
    return best


def rayleigh(y, t):
    u = np.asarray(y, float) * float(t)
    u = u[u <= RAYLEIGH_U_MAX]
    if u.size < 10:
        return None, int(u.size)
    frac = u - np.floor(u)
    return float(abs(np.mean(np.exp(2j * np.pi * frac)))), int(u.size)


def _files():
    out = subprocess.run(["git", "ls-files", "*.VGD"], capture_output=True, text=True, cwd=ROOT).stdout.split("\n")
    return [f for f in out if f]


def measure(path):
    P = vp.main_properties(os.path.join(ROOT, path))
    be, y = vgd_parser.parse_vgd(os.path.join(ROOT, path))
    y = np.asarray(y, float)
    dwell32 = np.float32(P[305][1])
    dwell = NOMINAL_DWELL.get(dwell32)
    scans = int(P[306][1])
    t0, t1 = P[303][1][1], P[304][1][1]
    elapsed = (t1 - t0) / 1e7
    name = os.path.basename(path)
    nums = [v[1] for v in P.values() if isinstance(v, tuple) and isinstance(v[1], (int, float)) and not isinstance(v[1], bool)]
    row = {"n_properties": len(P), "any_property_equals_128": any(v == 128 for v in nums), "file": path, "region": "Survey" if "Survey" in name else name.split(" ")[0], "n": int(y.size),
           "step_ev": round(abs(be[1] - be[0]), 6), "dwell_s": float(dwell32), "scans": scans,
           "scans_328": int(P[328][1]), "pass_energy_ev": float(P[404][1]), "photon_energy_ev": float(P[105][1]),
           "prop_406": float(P[406][1]), "elapsed_s": elapsed, "y_min": float(y.min()), "y_max": float(y.max())}
    b = gap_bound(y)
    row["gap_bound_s"] = float(b) if b is not None else None
    ceiling = Fraction(int(t1 - t0) + 10_000_000, 10_000_000)       # elapsed + 1 s
    iv, applied, deferred = admissible_times(y, [(Fraction(1, 10**9), ceiling)])
    row["any_T_up_to_elapsed"] = {"ceiling_s": float(ceiling), "admissible": [[float(a), float(c)] for a, c in iv[:5]],
                                  "n_intervals": len(iv), "constraints_applied": applied, "deferred": deferred}
    lo32, nom = Fraction(float(dwell32)), (dwell if dwell is not None else Fraction(float(dwell32)))
    lo_d, hi_d = min(lo32, nom), max(lo32, nom)
    band = Fraction(1, 10**9)
    cands = [(c * scans * lo_d * (1 - band), c * scans * hi_d * (1 + band)) for c in range(1, C_MAX + 1)]
    iv, applied, deferred = admissible_times(y, cands)
    row["decoded_candidates"] = {"admissible_c": sorted({round(float((a + c) / 2) / float(scans * nom))
                                                         for a, c in iv}), "n_intervals": len(iv),
                                 "constraints_applied": applied, "deferred": deferred}
    rs = []
    for c in range(1, C_MAX + 1):
        r, m = rayleigh(y, c * scans * nom)
        if r is not None:
            rs.append((math.exp(-m * r * r), c, r, m))
    if rs:
        p, c, r, m = min(rs)
        row["rayleigh_best"] = {"p": p, "family_p": min(1.0, p * C_MAX), "c": c, "R": r, "points": m,
                                "candidates_tested": len(rs),
                                "R_at_c1": next((x[2] for x in rs if x[1] == 1), None),
                                "R_at_c128": next((x[2] for x in rs if x[1] == 128), None)}
    else:
        row["rayleigh_best"] = None
    # by-product (not noise): the chart sidecar's "Binding Energy (eV)" axis against hv − KE and against the app's reader
    with open(os.path.join(ROOT, path[:-4] + ".xml"), encoding="utf-8", errors="replace") as fh:
        ax = re.search(r'<AxisX [^>]*Title="Binding Energy \(eV\)"[^>]*Maximum="([-0-9.Ee]+)" Minimum="([-0-9.Ee]+)"', fh.read())
    with olefile.OleFileIO(os.path.join(ROOT, path)) as ole:
        start, step = vgd_parser._find_ke_axis(ole.openstream("VGSpaceAxes").read())
    ke = start + np.arange(y.size) * step
    if ax:
        amax, amin = float(ax.group(1)), float(ax.group(2))
        hv = 1486.68                                                # property 105 is float32(1486.68)
        row["sidecar_be_axis"] = [amin, amax]
        row["sidecar_minus_hv_minus_ke"] = max(abs(amax - (hv - ke.min())), abs(amin - (hv - ke.max())))
        row["sidecar_minus_app_be"] = [amax - max(be), amin - min(be)]
    m = ne.ESTIMATORS["scaled_d4"](y)
    row["k_scaled_d4"] = m.k
    row["k_varmean"] = ne.ESTIMATORS["varmean"](y).k
    row["rho1_d4"] = ne.correlation_diagnostics(y)["rho1_d4"]
    return row


def report(rows):
    lines = []
    q = lambda v: (float(np.percentile(v, 10)), float(np.median(v)), float(np.percentile(v, 90)))
    lines.append(f"{len(rows)} committed VGD files")
    combos = collections.Counter((r["dwell_s"], r["scans"], r["scans_328"], r["pass_energy_ev"], r["step_ev"]) for r in rows)
    for (d, s, s2, pe, st), n in sorted(combos.items()):
        regions = sorted({r["region"] for r in rows if (r["dwell_s"], r["scans"], r["pass_energy_ev"], r["step_ev"]) == (d, s, pe, st)})
        lines.append(f"  dwell {d:.6g} s, scans {s} (328: {s2}), pass energy {pe:g} eV, step {st:g} eV: {n} files ({', '.join(regions)})")
    x = np.array([r["n"] * r["dwell_s"] * r["scans"] for r in rows])
    t = np.array([r["elapsed_s"] for r in rows])
    A = np.vstack([x, np.ones_like(x)]).T
    (slope, icpt), *_ = np.linalg.lstsq(A, t, rcond=None)
    res = t - (slope * x + icpt)
    lines.append(f"elapsed (303→304) vs points × dwell × scans: slope {slope:.4f}, intercept {icpt:.2f} s, "
                 f"residual {res.min():+.2f} … {res.max():+.2f} s; elapsed − points×dwell×scans "
                 f"{(t - x).min():.1f} … {(t - x).max():.1f} s")
    photon = sorted({round(r["photon_energy_ev"], 6) for r in rows})
    lines.append(f"photon energy (105): {photon}; property 406: {sorted({round(r['prop_406'], 6) for r in rows})}")
    gb = [r["gap_bound_s"] for r in rows if r["gap_bound_s"] is not None]
    above = sum(1 for r in rows if r["gap_bound_s"] and r["gap_bound_s"] > r["any_T_up_to_elapsed"]["ceiling_s"])
    lines.append(f"gap bound T ≥ 1/(gap + δ): {min(gb):.4g} … {max(gb):.4g} s (median {np.median(gb):.4g}); "
                 f"above the file's own elapsed + 1 s in {above} of {len(rows)} files")
    a = [r for r in rows if r["any_T_up_to_elapsed"]["n_intervals"]]
    dfr = [r for r in rows if r["any_T_up_to_elapsed"]["deferred"]]
    lines.append(f"EXACT, any common T ≤ elapsed + 1 s: admissible T in {len(a)} of {len(rows)} files; "
                 f"files left with deferred constraints: {len(dfr)}")
    for r in a[:10]:
        lines.append(f"    {r['file']}: {r['any_T_up_to_elapsed']['admissible']}")
    c = [r for r in rows if r["decoded_candidates"]["n_intervals"]]
    dfr = [r for r in rows if r["decoded_candidates"]["deferred"]]
    lines.append(f"EXACT, T = c × scans × dwell, c = 1…{C_MAX}: admissible in {len(c)} of {len(rows)} files; "
                 f"deferred: {len(dfr)}")
    for r in c[:10]:
        lines.append(f"    {r['file']}: c = {r['decoded_candidates']['admissible_c']}")
    rb = [r["rayleigh_best"] for r in rows if r["rayleigh_best"]]
    over = sum(1 for z in rb if z["family_p"] < 0.01)
    fam = sorted(z["family_p"] for z in rb)
    lines.append(f"integer-like (Rayleigh, points with y·T ≤ {RAYLEIGH_U_MAX:g}, Bonferroni over {C_MAX} candidates): "
                 f"tested in {len(rb)} files; integer-like at 1 % in {over}; smallest family p {fam[0]:.3g}, "
                 f"median {np.median(fam):.3g}; R at c = 1: max {max((z['R_at_c1'] or 0) for z in rb):.3f}; "
                 f"c = 128: max {max((z['R_at_c128'] or 0) for z in rb):.3f}")
    lines.append(f"main property set: {sorted(collections.Counter(r['n_properties'] for r in rows).items())} (properties: files); "
                 f"files with any numeric property equal to 128: {sum(r['any_property_equals_128'] for r in rows)}")
    sx = [r for r in rows if "sidecar_be_axis" in r]
    off = sorted({round(v, 9) for r in sx for v in r["sidecar_minus_app_be"]})
    lines.append(f"by-product — the chart sidecar's Binding Energy axis: in {len(sx)} of {len(rows)} files; equals 1486.68 − KE over the "
                 f"data to {max(r['sidecar_minus_hv_minus_ke'] for r in sx):.2g} eV; the app's VGD reader (hv 1486.6, work function 4.5) "
                 f"is lower by {off} eV")
    lines.append("noise scale vs counting time (counting noise over T_eff = f × dwell × scans predicts k × dwell × scans = 1/f, "
                 "the same in every region):")
    by = collections.defaultdict(list)
    for r in rows:
        by[r["region"]].append(r)
    for region, rs in sorted(by.items()):
        ds = rs[0]["dwell_s"] * rs[0]["scans"]
        k4, kv = q([r["k_scaled_d4"] for r in rs]), q([r["k_varmean"] for r in rs])
        lines.append(f"  {region:7s} {len(rs):3d} files  dwell×scans {ds:.3g} s  PE {rs[0]['pass_energy_ev']:g}  step {rs[0]['step_ev']:g}  "
                     f"k scaled_d4 {k4[1]:.3f} [{k4[0]:.3f}, {k4[2]:.3f}]  k×dwell×scans {k4[1] * ds:.4f}  "
                     f"(varmean {kv[1]:.3f}, ×dwell×scans {kv[1] * ds:.4f})  rho1_d4 {np.median([r['rho1_d4'] for r in rs]):+.3f} (white −0.80)")
    return "\n".join(lines)


def project_charge_shifts():
    """Every saved tab's charge-correction shift in the committed projects, rounded to 0.01 eV: {shift: tabs}."""
    import glob
    import zipfile
    out = collections.Counter()
    for z in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip"))):
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if not name.endswith(".json") or name == "manifest.json":
                    continue
                d = json.loads(zf.read(name))
                for t in (d.get("tabs") if isinstance(d, dict) and "tabs" in d else [d]):
                    if isinstance(t, dict) and t.get("ccShift") is not None:
                        out[round(float(t["ccShift"]), 2)] += 1
    return dict(sorted(out.items()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = [measure(f) for f in _files()]
    print(report(rows))
    cc = project_charge_shifts()
    print(f"committed projects' charge shifts (eV: tabs): {cc}")
    if a.json:
        json.dump(rows, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
