"""How far apart are the page's background (computed on the raw counts) and the server's
(computed on the counts as uploadToBackend sends them: energies toFixed(4), intensities
toFixed(2))? Codex impl round 9, finding A2: on an ill-conditioned constructed Tougaard
case they differed by most of the span; Run Fit freezes the page's curve beside the
server's envelope. Measured on the 202 committed targets, every method, averaging 1 / 3 /
10, as the max |B_page - B_server| over the window as a fraction of the window's span.

    venv/bin/python scripts/bg_math_upload_rounding_gap.py [--json OUT]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import fitting  # noqa: E402

T = json.load(open("/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json"))
ap = argparse.ArgumentParser()
ap.add_argument("--json")
a = ap.parse_args()
rows = []
for t in T:
    bg = t["background"]
    i0, i1 = int(bg["start_idx"]), int(bg["end_idx"])
    x = np.asarray(t["be"], float)[i0:i1]
    y = np.asarray(t["inten"], float)[i0:i1]
    xs = np.asarray([float(f"{v:.4f}") for v in x])
    ys = np.asarray([float(f"{v:.2f}") for v in y])
    span = float(np.max(y) - np.min(y))
    for m in ("shirley", "smart", "smart_exp", "tougaard"):
        for n in (1, 3, 10):
            try:
                bp = fitting.compute_background(x, y, m, n_avg=n)
            except fitting.BackgroundNotConverged:
                bp = None
            try:
                bs = fitting.compute_background(xs, ys, m, n_avg=n)
            except fitting.BackgroundNotConverged:
                bs = None
            gap = None if bp is None or bs is None else float(np.max(np.abs(bp - bs)) / span)
            rows.append({"id": t["id"], "method": m, "n_avg": n, "page_ok": bp is not None, "server_ok": bs is not None, "gap": gap})
gaps = [r["gap"] for r in rows if r["gap"] is not None]
disagree = [r for r in rows if r["page_ok"] != r["server_ok"]]
print(f"{len(rows)} cases ({len(T)} targets x 4 methods x 3 averagings); both converged on {len(gaps)}")
print(f"gap (max |page - server| / span): median {np.median(gaps):.2e}, 99th pct {np.percentile(gaps, 99):.2e}, max {max(gaps):.2e}")
print(f"verdicts disagree on {len(disagree)}")
for m in ("shirley", "smart", "smart_exp", "tougaard"):
    g = [r["gap"] for r in rows if r["gap"] is not None and r["method"] == m]
    print(f"  {m:10s} max {max(g):.2e}  median {np.median(g):.2e}")
if a.json:
    json.dump(rows, open(a.json, "w"))
