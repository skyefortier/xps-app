#!/usr/bin/env python3
"""Byte-identity proof for the DS+G guarded branch (2026-09-25).

The server's _ds_g_dscore_gauss gained ONE guarded branch: a centre outside
the padded grid is normalised by the curve's maximum. For every centre
INSIDE the padded grid the output must be byte-identical to the function
before the change. This script loads the pre-change module (fitting.py as
committed on main, given as argv[1]) beside the current one and compares
np.array_equal (exact bytes, NaN-free) on:
  1. the parity box alpha {0, 0.25, 0.49} x beta {0.05, 0.7, 2} x m {0.001,
     0.05, 0.4, 2, 4} on eight grids (steps 0.02-0.5 eV, ascending and
     descending, off-grid centres, short windows), centres at the window
     centre, at each window edge, and just inside each PADDED edge;
  2. 2000 random draws over the fit's bounds with centres uniform inside the
     padded grid;
  3. run_fit on the committed UCl4-graphite C1s Scan with the Graphite line
     as DS+G at Find Peaks' parameters (the model of the browser check),
     n_perturb 0 and 3: the whole JSON response, byte for byte;
  4. and, for the record, the cases OUTSIDE the padded grid where the two
     functions differ (the guarded branch doing its job).
Usage: python scripts/dsg_outside_centre_identity.py /path/to/fitting_main.py
"""
import copy
import importlib.util
import json
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")   # the kernel-underflow zone (plan §3a) divides by zero on purpose
sys.path.insert(0, ".")
import fitting  # noqa: E402

spec = importlib.util.spec_from_file_location("fitting_main", sys.argv[1])
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
f_new, f_old = fitting._SHAPE_FUNCS["ds_g"], old._SHAPE_FUNCS["ds_g"]


def padded_range(x, beta, m):
    step = max(float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 0.05, 1e-6)
    n_pad = max(int(np.ceil(max(10.0 * m, 20.0 * max(beta, 1e-6)) / step)), 1)
    lo, hi = (min(x[0], x[-1]) - n_pad * step, max(x[0], x[-1]) + n_pad * step)
    return lo, hi


grids = []
for step, n in ((0.02, 500), (0.05, 200), (0.0503, 181), (0.1, 120), (0.1, 30), (0.5, 21), (0.2, 61)):
    x = 284.5 - step * n / 2 + step * np.arange(n)
    grids.append(("asc %.4g x%d" % (step, n), x))
    grids.append(("desc %.4g x%d" % (step, n), x[::-1].copy()))
identical = differ = 0
worst = 0.0
for label, x in grids:
    for a in (0.0, 0.25, 0.49):
        for b in (0.05, 0.7, 2.0):
            for m in (0.001, 0.05, 0.4, 2.0, 4.0):
                lo, hi = padded_range(x, b, m)
                for c in (284.5, 284.525, x.min(), x.max(), lo + 1e-9, hi - 1e-9):
                    y0 = f_old(x, amplitude=1.0, center=c, alpha=a, beta=b, m_gauss=m)
                    y1 = f_new(x, amplitude=1.0, center=c, alpha=a, beta=b, m_gauss=m)
                    if np.array_equal(y0, y1):
                        identical += 1
                    else:
                        differ += 1
                        worst = max(worst, float(np.max(np.abs(y0 - y1))))
print(f"1. box x grids x centres inside the padded grid: {identical} byte-identical, {differ} differ (worst |delta| {worst:.3g})")

rng = np.random.default_rng(20260925)
identical = differ = 0
for _ in range(2000):
    step = float(rng.choice([0.02, 0.05, 0.1, 0.2]))
    n = int(rng.integers(20, 400))
    x = 284.5 - step * n / 2 + step * np.arange(n)
    if rng.random() < 0.5:
        x = x[::-1].copy()
    a, b, m = rng.uniform(0, 0.495), rng.uniform(0.05, 2.0), rng.uniform(0.001, 4.0)
    lo, hi = padded_range(x, b, m)
    c = rng.uniform(lo, hi)
    amp = float(rng.uniform(1, 1e5))
    y0 = f_old(x, amplitude=amp, center=c, alpha=a, beta=b, m_gauss=m)
    y1 = f_new(x, amplitude=amp, center=c, alpha=a, beta=b, m_gauss=m)
    if np.array_equal(y0, y1):
        identical += 1
    else:
        differ += 1
print(f"2. 2000 random draws, centre inside the padded grid: {identical} byte-identical, {differ} differ")

from autofit.reference import load_reference_fits, peak_to_backend_spec  # noqa: E402
rf = [r for r in load_reference_fits("docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip") if r.name == "C1s Scan"][0]
peaks = copy.deepcopy(rf.peaks)
g = [p for p in peaks if "raph" in p["name"]][0]
g.update(shape="DSG_LA", laAlpha=0.2, laBeta=0.05, laM=0.8)
specs = [peak_to_backend_spec(p, peaks) for p in peaks]
i0, i1 = rf.bg_indices()
for n_perturb in (0, 3):
    kw = dict(background_method=rf.bg_method, bg_start_idx=i0, bg_end_idx=i1, endpoint_avg=rf.endpoint_avg, n_perturb=n_perturb, fit_kws={"method": "leastsq"})
    r_new = json.dumps(fitting.run_fit(rf.roi_be, np.round(rf.roi_intensity, 2), specs, **kw), sort_keys=True)
    r_old = json.dumps(old.run_fit(rf.roi_be, np.round(rf.roi_intensity, 2), specs, **kw), sort_keys=True)
    print(f"3. run_fit (leastsq, n_perturb {n_perturb}) on the C1s Scan with a DS+G Graphite line: {'byte-identical JSON' if r_new == r_old else 'DIFFERS'} ({len(r_new)} bytes)")

for label, x, c in (("centre 10 eV outside [-5, 5]", (np.arange(200) - 99.5) * 0.05, 10.0), ("centre -10 eV, low-BE side", np.linspace(-5, 5, 201), -10.0)):
    y0 = f_old(x, amplitude=1.0, center=c, alpha=0.49, beta=0.05, m_gauss=0.05)
    y1 = f_new(x, amplitude=1.0, center=c, alpha=0.49, beta=0.05, m_gauss=0.05)
    print(f"4. {label}: old max {np.max(np.abs(y0)):.3g}, new max {np.max(np.abs(y1)):.3g} (the guarded branch)")
