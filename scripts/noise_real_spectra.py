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


def _best_quantum(y):
    """Raw counts divided by a counting time t would lie on a grid of 1/t (CPS). The grid unit u in 0.5-200 CPS
    (t from 5 ms to 2 s) holding the largest fraction of the values, and that fraction."""
    best = (None, -1.0)
    for u in np.linspace(0.5, 200.0, 4000):
        frac = float(np.mean(np.abs(y / u - np.round(y / u)) < 1e-6))
        if frac > best[1]:
            best = (float(u), frac)
    return {"unit": best[0], "fraction_on_grid": best[1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.DATA/*.VGD"))):
        be, y = vgd_parser.parse_vgd(f)
        y = np.asarray(y, float)
        name = os.path.basename(f)
        region = "Survey" if "Survey" in name else name.split(" ")[0]
        row = {"file": os.path.relpath(f, ROOT), "region": region, "n": int(y.size), "step_ev": float(abs(be[1] - be[0])),
               "min": float(y.min()), "max": float(y.max()), **ne.correlation_diagnostics(y),
               "non_integer_fraction": float(np.mean(np.abs(y - np.round(y)) > 1e-9)),
               "best_quantum": _best_quantum(y)}
        for est, fn in ne.ESTIMATORS.items():
            m = fn(y)
            row[est] = {"a": m.a, "k": m.k}
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
        for est in ("scaled_d1", "scaled_d2", "scaled_d4", "scaled_d2_lag3", "flat_ends", "varmean"):
            s[est + "_k"] = q([r[est]["k"] for r in rs])
        s["non_integer_fraction_min"] = float(min(r["non_integer_fraction"] for r in rs))
        s["quantum_fraction_max"] = float(max(r["best_quantum"]["fraction_on_grid"] for r in rs))
        summary[region] = s
        print(f"\n{region}: {len(rs)} files, {s['points']} points, step {s['step_ev']:.2f} eV")
        print(f"  rho1 d1 {s['rho1_d1'][1]:+.2f} [{s['rho1_d1'][0]:+.2f}, {s['rho1_d1'][2]:+.2f}] (white -0.50);"
              f" d4 {s['rho1_d4'][1]:+.2f} [{s['rho1_d4'][0]:+.2f}, {s['rho1_d4'][2]:+.2f}] (white -0.80);"
              f" lag profile " + " ".join(f"{v:.2f}" for v in s["lag_profile"]))
        print(f"  non-integer values: at least {s['non_integer_fraction_min']:.1%} of every file's points;"
              f" the most points on any 1/t grid (t 5 ms-2 s): {s['quantum_fraction_max']:.2%}")
        for est in ("scaled_d1", "scaled_d2", "scaled_d4", "scaled_d2_lag3", "flat_ends", "varmean"):
            lo, md, hi = s[est + "_k"]
            print(f"  {est:16s} k median {md:8.3f}   10-90 % [{lo:8.3f}, {hi:8.3f}]")
    if a.json:
        json.dump({"rows": rows, "summary": summary}, open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
