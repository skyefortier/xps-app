"""Scope check: do Run Fit's fits (main, perturbed restarts, scattered starts) end AT a minimum when they report success?
Every lmfit Model.fit call inside /api/fit is intercepted; each result is refined from its end point by a fresh
least_squares fit (same model, data, weights, bounds) and the relative chi2 drop recorded. Usage: OUT.jsonl METHOD"""
import sys, os, io, json, time
sys.path.insert(0, '.')
import numpy as np, lmfit
OUT, METHOD = sys.argv[1], sys.argv[2]
from app import create_app
app = create_app(); cl = app.test_client()
T = json.load(open('/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json'))
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)['id'])
orig = lmfit.Model.fit
calls = []
def fit(self, data, params=None, *a, **k):
    r = orig(self, data, params, *a, **k)
    if not calls or calls[-1] is not None:
        try:
            k2 = {kk: vv for kk, vv in k.items() if kk not in ('method', 'fit_kws', 'max_nfev', 'iter_cb')}
            calls.append(None)                     # refinement below must not be recorded
            ref = orig(self, data, r.params.copy(), *a, method='least_squares', **k2)
            calls.pop()
            calls.append({"method": k.get('method'), "success": bool(r.success), "nfev": int(r.nfev), "nvarys": int(r.nvarys),
                          "chisqr": float(r.chisqr), "refined": float(ref.chisqr), "redchi": float(r.redchi) if r.redchi is not None else None})
        except Exception as e:
            if calls and calls[-1] is None: calls.pop()
            calls.append({"method": k.get('method'), "error": str(e)[:80]})
    return r
lmfit.Model.fit = fit
A, B = (int(v) for v in os.environ.get('SCOPE_SLICE', '0:100000').split(':'))
for t in T[A:B]:
    if t['id'] in done: continue
    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
    r = cl.post("/api/upload", data={"file": (io.BytesIO(csv), "t.csv")}, content_type="multipart/form-data")
    sid = r.get_json()["session_id"]
    bg = t["background"]
    body = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
            "peaks": t["specs"], "fit_method": METHOD, "n_perturb": 3, "n_starts": 3}
    calls.clear(); t0 = time.time()
    resp = cl.post("/api/fit", json=body).get_json() or {}
    st = resp.get("starts") or {}
    with open(OUT, 'a') as f:
        f.write(json.dumps({"id": t["id"], "success": resp.get("success"), "starts_ran": st.get("ran"), "sec": round(time.time() - t0, 1),
                            "calls": [c for c in calls if c is not None]}) + "\n")
