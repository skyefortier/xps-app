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
3. "Integer-like" (approximate), at each decoded candidate T of range (b) only: the alignment of y·T with the
   integers, V = mean cos(2π y T) over the m ≥ 10 points with y·T ≤ 1e5 (V = 1 for exact integers, −1 for a
   half-integer lattice; for independent uniform phases V·√(2m) is asymptotically N(0, 1), one-sided
   p = Φ(−V√(2m))). The 1024 candidates of a file are one family, judged by Bonferroni: integer-like at 1 % iff
   1024 · min p < 0.01 — a perfect lattice on 10 points reaches 1024·Φ(−√20) = 0.004 (round 1: the Rayleigh
   |mean exp(2πi y T)| first used here ignored the phase's direction and needed ≥ 12 exact points).
4. Does each region's estimated noise scale k (variance = k·y, scripts/noise_estimators.py) follow 1/(dwell ×
   scans)? Poisson counts over f × dwell × scans times a deterministic correction a give k × dwell × scans = a/f.
5. The files' own property names (each set's dictionary), the corrections they record, the sidecars' intensity-axis
   titles, and (a by-product) the sidecars' energy axis against the app's VGD reader.

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
    non-negative whole number / T — exact rational arithmetic. Returns a dict:

    status       'excluded'   — the set is empty: no such T exists in the ranges (a proof, under δ);
                 'admissible' — every constraint was applied: ``intervals`` is every admissible T;
                 'unresolved' — some constraints were deferred (they would split the set into more than
                                INTERVAL_CAP pieces): ``intervals`` is a SUPERSET, not an admissible set.
    excluded_by  for 'excluded': which constraint emptied the set — ('gap', rank among the gaps, smallest
                 first), ('value', rank, smallest first) or ('negative', None) for a value below −δ.
    applied, deferred — constraint counts."""
    y = np.asarray(y, float)
    u = np.unique(y)
    dlt = [Fraction(float(2 * np.spacing(abs(float(v))))) for v in u]
    vals = [Fraction(float(v)) for v in u]
    if any(v < -e for v, e in zip(vals, dlt)):
        return {"intervals": [], "status": "excluded", "excluded_by": ("negative", None), "applied": 0, "deferred": 0}
    gaps = sorted(((vals[i + 1] - vals[i], dlt[i] + dlt[i + 1]) for i in range(len(vals) - 1)), key=lambda g: g[0])
    # a resolvable gap is a positive multiple of 1/T (implied by the value constraints: it only narrows sooner);
    # a value within δ of 0 is met by N = 0 and constrains nothing
    cons = [("gap", r, g, e, 1) for r, (g, e) in enumerate(gp for gp in gaps if gp[0] > gp[1])]
    cons += [("value", r, v, e, 0) for r, (v, e) in enumerate(sorted(((v, e) for v, e in zip(vals, dlt) if v > e),
                                                                   key=lambda c: c[0]))]
    iv = _merge([(Fraction(lo), Fraction(hi)) for lo, hi in ranges])
    applied, pending = 0, cons
    while pending:
        later = []
        for kind, rank, v, e, n_min in pending:
            new = _apply(iv, v, e, n_min)
            if new is None:
                later.append((kind, rank, v, e, n_min))
                continue
            iv, applied = new, applied + 1
            if not iv:
                return {"intervals": [], "status": "excluded", "excluded_by": (kind, rank), "applied": applied,
                        "deferred": 0}
        if not later:
            break
        if len(later) == len(pending):                              # nothing narrowed further
            return {"intervals": iv, "status": "unresolved", "excluded_by": None, "applied": applied,
                    "deferred": len(later)}
        pending = later
    if not iv:
        return {"intervals": [], "status": "excluded", "excluded_by": ("range", None), "applied": applied, "deferred": 0}
    return {"intervals": iv, "status": "admissible", "excluded_by": None, "applied": applied, "deferred": 0}


def gap_bound(y):
    """Smallest T compatible with the smallest resolvable gap (exact): T ≥ 1 / (gap + δ_a + δ_b)."""
    u = np.unique(np.asarray(y, float))
    best = None
    for a, b in zip(u[:-1], u[1:]):
        g = Fraction(float(b)) - Fraction(float(a))
        e = Fraction(float(2 * np.spacing(abs(float(a))))) + Fraction(float(2 * np.spacing(abs(float(b)))))
        if g > e:
            t = 1 / (g + e)
            best = t if best is None or t > best else best
    return best


def integer_alignment(y, t):
    """(V, m): V = mean cos(2π y·T) over the m points with y·T ≤ RAYLEIGH_U_MAX; (None, m) when m < 10."""
    u = np.asarray(y, float) * float(t)
    u = u[u <= RAYLEIGH_U_MAX]
    if u.size < 10:
        return None, int(u.size)
    frac = u - np.floor(u)
    return float(np.mean(np.cos(2 * np.pi * frac))), int(u.size)


def alignment_p(v, m):
    """One-sided p of V under independent uniform phases (asymptotic): Φ(−V·√(2m))."""
    return 0.5 * math.erfc(v * math.sqrt(2 * m) / math.sqrt(2))


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
    names = vp.main_property_names(os.path.join(ROOT, path))
    row = {"n_properties": len(P), "any_property_equals_128": any(v == 128 for v in nums),
           "names_as_expected": all(names.get(k) == v for k, v in vp.ACQUISITION.items()),
           "n_named": len(names),
           "corrections": {vp.ACQUISITION[k]: P[k][1] for k in (311, 313, 415, 416, 413, 417, 850, 982)},
           "txfn_coeffs": [P[k][1] for k in range(100000, 100004)],
           "psf_coeffs": [P[k][1] for k in range(300000, 300008)],
           "file": path, "region": "Survey" if "Survey" in name else name.split(" ")[0], "n": int(y.size),
           "step_ev": round(abs(be[1] - be[0]), 6), "dwell_s": float(dwell32), "scans": scans,
           "scans_328": int(P[328][1]), "pass_energy_ev": float(P[404][1]), "photon_energy_ev": float(P[105][1]),
           "prop_406": float(P[406][1]), "elapsed_s": elapsed, "y_min": float(y.min()), "y_max": float(y.max())}
    b = gap_bound(y)
    row["gap_bound_s"] = float(b) if b is not None else None
    ceiling = Fraction(int(t1 - t0) + 10_000_000, 10_000_000)       # elapsed + 1 s
    res = admissible_times(y, [(Fraction(1, 10**9), ceiling)])
    row["any_T_up_to_elapsed"] = {"ceiling_s": float(ceiling), "status": res["status"],
                                  "excluded_by": res["excluded_by"],
                                  "intervals": [[float(a), float(c)] for a, c in res["intervals"][:5]],
                                  "n_intervals": len(res["intervals"]), "constraints_applied": res["applied"],
                                  "deferred": res["deferred"]}
    lo32, nom = Fraction(float(dwell32)), (dwell if dwell is not None else Fraction(float(dwell32)))
    lo_d, hi_d = min(lo32, nom), max(lo32, nom)
    band = Fraction(1, 10**9)
    cands = [(c * scans * lo_d * (1 - band), c * scans * hi_d * (1 + band)) for c in range(1, C_MAX + 1)]
    res = admissible_times(y, cands)
    row["decoded_candidates"] = {"status": res["status"], "excluded_by": res["excluded_by"],
                                 "c_in_intervals": sorted({round(float((a + c) / 2) / float(scans * nom))
                                                           for a, c in res["intervals"]}),
                                 "n_intervals": len(res["intervals"]), "constraints_applied": res["applied"],
                                 "deferred": res["deferred"]}
    rs = []
    for c in range(1, C_MAX + 1):
        v, m = integer_alignment(y, c * scans * nom)
        if v is not None:
            rs.append((alignment_p(v, m), c, v, m))
    if rs:
        p, c, v, m = min(rs)
        row["alignment_best"] = {"p": p, "family_p": min(1.0, p * C_MAX), "c": c, "V": v, "points": m,
                                 "candidates_tested": len(rs), "min_points": min(x[3] for x in rs),
                                 "V_at_c1": next((x[2] for x in rs if x[1] == 1), None),
                                 "V_at_c128": next((x[2] for x in rs if x[1] == 128), None)}
    else:
        row["alignment_best"] = None
    # by-product (not noise): the chart sidecar's "Binding Energy (eV)" axis against hv − KE and against the app's reader
    with open(os.path.join(ROOT, path[:-4] + ".xml"), encoding="utf-8", errors="replace") as fh:
        xml = fh.read()
    ty = re.search(r'<AxisY [^>]*Title="([^"]*)"', xml)
    row["sidecar_y_title"] = ty.group(1) if ty else None
    row["non_integer_fraction"] = float(np.mean(np.abs(y - np.round(y)) > 0))
    ax = re.search(r'<AxisX [^>]*Title="Binding Energy \(eV\)"[^>]*Maximum="([-0-9.Ee]+)" Minimum="([-0-9.Ee]+)"', xml)
    with olefile.OleFileIO(os.path.join(ROOT, path)) as ole:
        start, step = vgd_parser._find_ke_axis(ole.openstream("VGSpaceAxes").read())
    ke = start + np.arange(y.size) * step
    if ax:
        amax, amin = float(ax.group(1)), float(ax.group(2))
        hv = 1486.68                                                # property 105 is float32(1486.68)
        row["sidecar_be_axis"] = [amin, amax]                      # identity checked against the decimal 1486.68
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
    for key, label in (("any_T_up_to_elapsed", "EXACT, range (a): any common T in [1e-9 s, elapsed + 1 s]"),
                       ("decoded_candidates", f"EXACT, range (b): T = c × scans × dwell, c = 1…{C_MAX}")):
        st = collections.Counter(r[key]["status"] for r in rows)
        by = collections.Counter(tuple(r[key]["excluded_by"]) for r in rows if r[key]["status"] == "excluded")
        lines.append(f"{label}: status {dict(sorted(st.items()))}; excluded by {dict(sorted(by.items()))} "
                     f"(kind, rank — rank 0 = the smallest gap / value)")
        for r in rows:
            if r[key]["status"] != "excluded":
                lines.append(f"    {r['file']}: {r[key]['status']} {r[key].get('intervals', r[key].get('c_in_intervals'))}")
    rb = [r["alignment_best"] for r in rows if r["alignment_best"]]
    over = sum(1 for z in rb if z["family_p"] < 0.01)
    fam = sorted(z["family_p"] for z in rb)
    tested = [z["candidates_tested"] for z in rb]
    lines.append(f"integer-like (alignment V = mean cos 2πyT) at the decoded candidates of range (b) only, points with "
                 f"y·T ≤ {RAYLEIGH_U_MAX:g}, a candidate needing ≥ 10 such points; Bonferroni over {C_MAX}: tested in "
                 f"{len(rb)} files (candidates evaluated per file {min(tested)} … {max(tested)}; all {C_MAX} in "
                 f"{sum(1 for t in tested if t == C_MAX)}; fewest points at any evaluated candidate "
                 f"{min(z['min_points'] for z in rb)}); integer-like at 1 % in {over}; smallest family p {fam[0]:.3g}, "
                 f"median {np.median(fam):.3g}; V at c = 1: {min(z['V_at_c1'] for z in rb):+.3f} … "
                 f"{max(z['V_at_c1'] for z in rb):+.3f}; best V over all candidates and files {max(z['V'] for z in rb):+.3f}")
    hit = [(r["file"], r["alignment_best"]) for r in rows if r["alignment_best"] and r["alignment_best"]["family_p"] < 0.01]
    lines.append(f"  expected by chance at the per-file 1 % level over {len(rb)} files: {0.01 * len(rb):.2f}; across all files "
                 f"(Bonferroni {len(rb)} × {C_MAX}): smallest p {min(1.0, fam[0] * len(rb)):.3g}")
    for f, z in hit:
        lines.append(f"    {f}: c = {z['c']}, V = {z['V']:+.3f} on {z['points']} points, family p {z['family_p']:.3g}")
    lines.append(f"property names: {sum(r['names_as_expected'] for r in rows)} of {len(rows)} files name every id this "
                 f"unit reads as scripts/vgd_properties.ACQUISITION does; dictionary entries "
                 f"{sorted(collections.Counter(r['n_named'] for r in rows).items())} (entries: files)")
    corr = collections.Counter(tuple(sorted(r["corrections"].items())) for r in rows)
    for c, n in corr.items():
        lines.append(f"  corrections recorded ({n} files): {dict(c)}")
    tx = collections.Counter(tuple(round(v, 9) for v in r["txfn_coeffs"]) for r in rows)
    ps = collections.Counter((r["pass_energy_ev"], tuple(round(v, 9) for v in r["psf_coeffs"])) for r in rows)
    lines.append(f"  unnamed 100000-100003 (4 values; NumberOfTXFNCoeffs = 4): {dict(tx)}")
    lines.append(f"  unnamed 300000-300007 (8 values; NumberOfPSFCoeffs = 8), by pass energy: {dict(ps)}")
    yt = collections.Counter(r["sidecar_y_title"] for r in rows)
    lines.append(f"sidecar intensity-axis titles: {dict(yt)}; files whose stored values are all integers: "
                 f"{sum(1 for r in rows if r['non_integer_fraction'] == 0)}; non-integer fraction of the 'Counts'-titled files: "
                 f"{sorted(round(r['non_integer_fraction'], 4) for r in rows if r['sidecar_y_title'] == 'Counts')}")
    sx = [r for r in rows if "sidecar_be_axis" in r]
    off = sorted({round(v, 9) for r in sx for v in r["sidecar_minus_app_be"]})
    lines.append(f"by-product — the chart sidecar's Binding Energy axis: in {len(sx)} of {len(rows)} files; equals the decimal 1486.68 (property 105 is its float32) − KE over the "
                 f"data to {max(r['sidecar_minus_hv_minus_ke'] for r in sx):.2g} eV; the app's VGD reader (hv 1486.6, work function 4.5) "
                 f"is lower by {off} eV")
    lines.append("noise scale vs counting time (Poisson counts over T_eff = f × dwell × scans, times a deterministic correction a, "
                 "give k × dwell × scans = a/f: the same in every region only if a/f is):")
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
