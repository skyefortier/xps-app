"""Seal 1a′: how far do the reported statistics move when they are formed from the returned
arrays (V6.6) instead of lmfit's minimiser residual? Measured on the 202 committed targets, ONE
fit each — lmfit's values and the array-formed ones of the SAME fit, side by side — so the
difference is the change itself, not optimiser jitter. Also: is result.nvarys the roles count,
and does the in-process verification (fitting.verify_fit) call the response consistent?

The request is what the page sends: full-precision arrays, the target's background, Trust-Region
(the page's default), n_perturb 3. Resumable JSONL.

Usage (cwd = the branch checkout): python scripts/seal_1a_statistics_measure.py OUT.jsonl [METHOD]
"""
import json
import os
import sys

sys.path.insert(0, ".")
import numpy as np  # noqa: E402
import fitting  # noqa: E402

TARGETS = ("/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/"
           "docs/findings/optimizer-disagreement/targets.json")
OUT = sys.argv[1]
METHOD = sys.argv[2] if len(sys.argv) > 2 else "least_squares"

captured = {}
_orig = fitting._fit_statistics


def _capture(y_sub, fitted_sub, weights, n_varys):
    res = sys._getframe(1).f_locals.get("result")      # run_fit's returned lmfit result (the verifier has none)
    if res is None:
        return _orig(y_sub, fitted_sub, weights, n_varys)
    captured.update(lmfit={"chi_square": float(res.chisqr), "reduced_chi_square": float(res.redchi),
                           "aic": float(res.aic), "bic": float(res.bic)},
                    nvarys=int(res.nvarys), n_varys=int(n_varys),
                    best_fit_is_fitted_sub=bool(np.array_equal(res.best_fit, fitted_sub)))
    return _orig(y_sub, fitted_sub, weights, n_varys)


fitting._fit_statistics = _capture


def rel(a, b):
    return None if a is None or b is None else (0.0 if a == b else abs(a - b) / max(abs(a), abs(b)))


T = json.load(open(TARGETS))
done = {json.loads(l)["id"] for l in open(OUT)} if os.path.exists(OUT) else set()
for t in T:
    if t["id"] in done:
        continue
    bg = t["background"]
    args = dict(energy=np.asarray(t["be"], float), counts=np.asarray(t["inten"], float), peak_specs=t["specs"],
                background_method=bg["method"], bg_start_idx=bg["start_idx"], bg_end_idx=bg["end_idx"],
                endpoint_avg=bg["endpoint_avg"], n_perturb=3, fit_kws={"method": METHOD})
    captured.clear()
    try:
        r = fitting.run_fit(**args)
        s = r["statistics"]
        lm = captured["lmfit"]
        O = json.loads(json.dumps(r))
        v = fitting.verify_fit(O, **{**args, "peak_specs": json.loads(json.dumps(t["specs"]))})
        rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "shapes": sorted(set(t["shapes"])),
               "success": r["success"], "n_data": s["n_data"],
               "lmfit": lm, "reported": {k: s[k] for k in lm},
               "rel": {k: rel(lm[k], s[k]) for k in lm},
               "abs_aic": abs(lm["aic"] - s["aic"]), "abs_bic": abs(lm["bic"] - s["bic"]),
               "nvarys_equal": captured["nvarys"] == captured["n_varys"],
               "best_fit_is_fitted_sub": captured["best_fit_is_fitted_sub"],
               "verify": v["state"], "verify_check": v["check"]}
    except Exception as e:  # noqa: BLE001
        rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "error": f"{type(e).__name__}: {e}"[:300]}
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
