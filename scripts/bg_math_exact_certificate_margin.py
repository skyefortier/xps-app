"""How close are the committed backgrounds to the limit of a double-precision certificate?
(background math, Codex impl round 13.) For each committed target window and each
Shirley-family method, the background as computed (float iteration, certified in float)
is checked against its defining relation in EXACT rational arithmetic — exact edge
levels, exact trapezoid integral, exact map — and the exact residual is reported as a
multiple of the predicate (BG_REL_TOL x the window's span): < 1 means the float
certificate's verdict is right exactly. Also the window's precision ratio
eps * max|I| / (BG_REL_TOL * span): how near double precision itself comes to the
predicate's resolution.

    venv/bin/python scripts/bg_math_exact_certificate_margin.py [--json OUT]
"""
import argparse
import json
import os
import sys
from fractions import Fraction as F

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fitting  # noqa: E402

T = json.load(open("/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json"))


def exact_residual(x, y, bg, method, n_avg):
    xa, ya, flipped = fitting._ascending(x, y)
    Ba = bg[::-1] if flipped else bg
    xs, ys, B = [F(v) for v in xa], [F(v) for v in ya], [F(v) for v in Ba]
    n = len(ys)
    k = max(1, min(int(n_avg), n // 4)) if n >= 4 else 1
    b_low, b_high = sum(ys[:k]) / k, sum(ys[-k:]) / k
    if b_low == b_high:
        Tm = [b_low] * n
    else:
        s = [max(ys[i] - B[i], F(0)) for i in range(n)]
        cum = [F(0)] * n
        for i in range(n - 2, -1, -1):
            cum[i] = cum[i + 1] + (s[i] + s[i + 1]) * (xs[i + 1] - xs[i]) / 2
        if cum[0] <= 0:
            return None
        Tm = [b_high + (b_low - b_high) * c / cum[0] for c in cum]
    if method in ("smart", "smart_exp"):
        Tm = [min(t, ys[i]) for i, t in enumerate(Tm)]
    return max(abs(B[i] - Tm[i]) for i in range(n))


ap = argparse.ArgumentParser()
ap.add_argument("--json")
a = ap.parse_args()
rows = []
for t in T:
    bgs = t["background"]
    i0, i1 = int(bgs["start_idx"]), int(bgs["end_idx"])
    x = np.asarray(t["be"], float)[i0:i1]
    y = np.asarray([float(f"{v:.2f}") for v in t["inten"]], float)[i0:i1]   # what the server fits
    span = float(np.max(y) - np.min(y))
    prec = float(np.finfo(float).eps * np.max(np.abs(y)) / (fitting.BG_REL_TOL * span))
    for m in ("shirley", "smart", "smart_exp"):
        for n_avg in (1, 3):
            try:
                bg = fitting.compute_background(x, y, m, n_avg=n_avg)
            except fitting.BackgroundNotConverged:
                rows.append({"id": t["id"], "method": m, "n_avg": n_avg, "refused": True})
                continue
            r = exact_residual(x, y, bg, m, n_avg)
            rows.append({"id": t["id"], "method": m, "n_avg": n_avg, "refused": False, "n": len(x),
                         "exact_over_predicate": None if r is None else float(r / (F(fitting.BG_REL_TOL) * F(span))),
                         "precision_ratio": prec})
ok = [r for r in rows if not r["refused"] and r["exact_over_predicate"] is not None]
ratios = [r["exact_over_predicate"] for r in ok]
prec = sorted({(r["id"], r["precision_ratio"]) for r in ok}, key=lambda p: p[1])
print(f"{len(rows)} cases, {len(ok)} certified; exact residual / predicate: median {np.median(ratios):.3g}, "
      f"99th pct {np.percentile(ratios, 99):.3g}, max {max(ratios):.3g}; over 1: {sum(v > 1 for v in ratios)}")
print(f"precision ratio eps*max|I|/(tol*span) over the {len(prec)} windows: median {np.median([p[1] for p in prec]):.3g}, max {prec[-1][1]:.3g}")
print("largest exact residual / predicate:", sorted(ok, key=lambda r: -r["exact_over_predicate"])[:3])
if a.json:
    json.dump(rows, open(a.json, "w"))
