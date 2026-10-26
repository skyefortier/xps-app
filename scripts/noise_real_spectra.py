"""Unit B: what each candidate noise estimator (scripts/noise_estimators.py) gives on the committed real spectra —
every Thermo VGD under docs/autofit/test_data/*.DATA (read by the app's own vgd_parser, as /api/parse-vgd reads
them), whole spectra, grouped by region. A report, not a reference: nothing here is ground truth.

    venv/bin/python scripts/noise_real_spectra.py [--json OUT]
"""
import argparse
import collections
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [HERE, ROOT]
import noise_estimators as ne  # noqa: E402
import vgd_parser  # noqa: E402


def _projects_vs_vgds(vgd_values):
    """Which committed project spectra are, value for value, a committed VGD's intensities (in either order)."""
    import zipfile
    keys = {}
    for f, y in vgd_values.items():
        keys[np.asarray(y, float).tobytes()] = f
        keys[np.asarray(y, float)[::-1].tobytes()] = f
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip"))):
        z = zipfile.ZipFile(p)
        for nm in z.namelist():
            if not nm.endswith(".json") or "manifest" in nm:
                continue
            t = json.loads(z.read(nm))
            y = t.get("rawIntensity")
            if not y:
                continue
            y = np.asarray(y, float)
            out.append({"project": os.path.basename(p), "tab": t.get("name"), "n": int(y.size),
                        "matches_vgd": keys.get(y.tobytes()), "non_integer_fraction": float(np.mean(np.abs(y - np.round(y)) > 1e-9)),
                        "common_quantum": ne.common_quantum(y)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    rows, values = [], {}
    for f in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.DATA/*.VGD"))):
        be, y = vgd_parser.parse_vgd(f)
        y = np.asarray(y, float)
        values[os.path.relpath(f, ROOT)] = y
        name = os.path.basename(f)
        region = "Survey" if "Survey" in name else name.split(" ")[0]
        row = {"file": os.path.relpath(f, ROOT), "region": region, "n": int(y.size), "step_ev": float(abs(be[1] - be[0])),
               "min": float(y.min()), "max": float(y.max()), **ne.correlation_diagnostics(y),
               "non_integer_fraction": float(np.mean(np.abs(y - np.round(y)) > 1e-9)),
               "common_quantum": ne.common_quantum(y), "smallest_gap": float(np.diff(np.unique(y)).min())}
        for est, fn in ne.ESTIMATORS.items():
            m = fn(y)
            row[est] = {"a": m.a, "k": m.k, "a_over_median_y": m.a / float(np.median(y))}
        rows.append(row)
    by = collections.defaultdict(list)
    for r in rows:
        by[r["region"]].append(r)
    q = lambda v: (float(np.percentile(v, 10)), float(np.median(v)), float(np.percentile(v, 90)))
    summary = {}
    for region, rs in sorted(by.items()):
        s = {"files": len(rs), "points": int(np.median([r["n"] for r in rs])), "step_ev": float(np.median([r["step_ev"] for r in rs])),
             "rho1_d1": q([r["rho1_d1"] for r in rs]), "rho1_d4": q([r["rho1_d4"] for r in rs]),
             "lag_profile": [float(np.median([r["lag_profile"][i] for r in rs])) for i in range(4)]}
        for est in ("scaled_d1", "scaled_d2", "scaled_d4", "scaled_d2_lag3", "flat_ends", "varmean", "der_snr", "constant_d4"):
            s[est + "_k"] = q([r[est]["a_over_median_y"] if est in ("der_snr", "constant_d4") else r[est]["k"] for r in rs])
        s["non_integer_fraction_min"] = float(min(r["non_integer_fraction"] for r in rs))
        s["files_with_a_common_quantum"] = int(sum(r["common_quantum"] is not None for r in rs))
        s["smallest_gap_median"] = float(np.median([r["smallest_gap"] for r in rs]))
        s["varmean_a_over_median_y"] = q([r["varmean"]["a_over_median_y"] for r in rs])
        summary[region] = s
        print(f"\n{region}: {len(rs)} files, {s['points']} points, step {s['step_ev']:.2f} eV")
        print(f"  rho1 d1 {s['rho1_d1'][1]:+.2f} [{s['rho1_d1'][0]:+.2f}, {s['rho1_d1'][2]:+.2f}] (white -0.50);"
              f" d4 {s['rho1_d4'][1]:+.2f} [{s['rho1_d4'][0]:+.2f}, {s['rho1_d4'][2]:+.2f}] (white -0.80);"
              f" lag profile " + " ".join(f"{v:.2f}" for v in s["lag_profile"]))
        print(f"  non-integer values: at least {s['non_integer_fraction_min']:.1%} of every file's points;"
              f" files where the heuristic grid search accepted a candidate: {s['files_with_a_common_quantum']}"
              f" (median smallest gap {s['smallest_gap_median']:.3g} CPS)")
        for est in ("scaled_d1", "scaled_d2", "scaled_d4", "scaled_d2_lag3", "flat_ends", "varmean", "der_snr", "constant_d4"):
            lo, md, hi = s[est + "_k"]
            unit = "a/median(y)" if est in ("der_snr", "constant_d4") else "k"
            print(f"  {est:16s} {unit} median {md:8.3f}   10-90 % [{lo:8.3f}, {hi:8.3f}]")
        lo, md, hi = s["varmean_a_over_median_y"]
        print(f"  varmean intercept a / median(y): median {md:8.3f}   10-90 % [{lo:8.3f}, {hi:8.3f}]")
    g = np.array([r["smallest_gap"] for r in rows]); npts = np.array([r["n"] for r in rows])
    # were the values counts / t, every gap would be ≥ 1/t; for STORED (rounded) values the gap may read up to the
    # two endpoints' rounding smaller, so the bound uses gap + 2 ulp(max)
    t = 1.0 / (g + 2 * np.spacing(np.array([r["max"] for r in rows])))
    print(f"\nsmallest gap between a file's values: {g.min():.3g} - {g.max():.3g} CPS. Were the values counts / t,"
          f" t >= 1/(gap + rounding): {t.min():.3g} - {t.max():.3g} s per point (median {np.median(t):.3g} s)."
          f" Counted point by point, points x t >= {(npts * t).min():.0f} s for every file; with 128 channels counting"
          f" in parallel (an assumed acquisition model) the lower bound points x t / 128 is < 120 s for {(npts * t / 128 < 120).sum()}"
          f" of {len(t)} files (< 60 s for {(npts * t / 128 < 60).sum()})")
    proj = _projects_vs_vgds(values)
    matched = sum(1 for r in proj if r["matches_vgd"])
    print(f"\ncommitted project spectra: {len(proj)}; identical to a committed VGD's values: {matched};"
          f" non-integer in every spectrum: {all(r['non_integer_fraction'] > 0.99 for r in proj)};"
          f" heuristic grid search accepted a candidate in: {sum(r['common_quantum'] is not None for r in proj)}")
    if a.json:
        json.dump({"rows": rows, "summary": summary, "projects": proj}, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
