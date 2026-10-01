"""Background-math implementation (2026-10-01): the background's effect on FITS alone,
without the request seed's redraw. The request seed hashes the computed background, so
any background change redraws the perturbed restarts and can send a fit on a
several-minima target to another basin (measured: every target that moved > 1 pp did
so, and reproduced main to <= 0.006 pp with main's seed). Here main records each
target's seed and the branch refits under main's seed. Calls fitting.run_fit directly
with the arguments /api/fit builds (the route does not forward a caller's seed).
Resumable JSONL.

Usage (cwd = the checkout under test):
  python bg_math_impl_seeded.py OUT.jsonl record [AVG]            # main: record seeds
  python bg_math_impl_seeded.py OUT.jsonl force SEEDS.jsonl [AVG] # branch: main's seeds
"""
import json
import os
import sys

sys.path.insert(0, ".")
import numpy as np  # noqa: E402
import fitting  # noqa: E402

OUT, MODE = sys.argv[1], sys.argv[2]
SEEDS = {}
if MODE == "force":
    SEEDS = {json.loads(l)["id"]: json.loads(l)["seed"] for l in open(sys.argv[3])}
    AVG = int(sys.argv[4]) if len(sys.argv) > 4 else None
else:
    AVG = int(sys.argv[3]) if len(sys.argv) > 3 else None
T = json.load(open("/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json"))
done = {json.loads(l)["id"] for l in open(OUT)} if os.path.exists(OUT) else set()
for t in T:
    if t["id"] in done:
        continue
    bg = t["background"]
    x = np.round(np.asarray(t["be"], float), 4)
    y = np.round(np.asarray(t["inten"], float), 4)
    kw = {"method": "least_squares"}
    if MODE == "force":
        kw["fit_kws"] = {"seed": SEEDS[t["id"]]}
    try:
        r = fitting.run_fit(x, y, t["specs"], background_method=bg["method"], bg_start_idx=bg["start_idx"],
                            bg_end_idx=bg["end_idx"], endpoint_avg=AVG or bg["endpoint_avg"], n_perturb=3, fit_kws=kw)
        names = {str(s["id"]): s.get("name") for s in t["specs"]}
        comps = [{"id": str(p.get("id")), "name": names.get(str(p.get("id"))), "center": p["params"]["center"]["value"],
                  "area": p["params"]["area"]["value"], "supported": (p.get("support") or {}).get("supported")}
                 for p in r["individual_peaks"]]
        rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "method": bg["method"],
               "endpoint_avg": AVG or bg["endpoint_avg"], "success": r.get("success"), "seed": r.get("random_seed"),
               "chi2r": r["statistics"]["reduced_chi_square"], "components": comps}
    except Exception as e:  # noqa: BLE001
        rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "success": False, "error": str(e)[:200], "seed": None, "components": []}
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
