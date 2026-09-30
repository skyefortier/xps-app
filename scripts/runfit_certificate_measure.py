"""A2 (unit A2, 2026-09-29) measurement: every committed target through /api/fit exactly as the page sends it
run from the CURRENT checkout (cwd). Resumable JSONL. Usage: python a2_measure.py OUT.jsonl METHOD [SLICE a:b]"""
import sys, os, io, json, time
sys.path.insert(0, '.')
OUT, METHOD = sys.argv[1], sys.argv[2]
A, B = (int(v) for v in (sys.argv[3] if len(sys.argv) > 3 else '0:100000').split(':'))
import fitting
if os.environ.get('A2_VARIANT') == 'V2': fitting._CERTIFY_PERTURBED = False
from app import create_app
app = create_app(); cl = app.test_client()
T = json.load(open('/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json'))
done = set()
if os.path.exists(OUT):
    for l in open(OUT): done.add(json.loads(l)['id'])
for t in T[A:B]:
    if t['id'] in done: continue
    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
    sid = cl.post("/api/upload", data={"file": (io.BytesIO(csv), "t.csv")}, content_type="multipart/form-data").get_json()["session_id"]
    bg = t["background"]
    body = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
            "peaks": t["specs"], "fit_method": METHOD, "n_perturb": 3, "n_starts": 3}
    t0 = time.perf_counter()
    r = cl.post("/api/fit", json=body); sec = time.perf_counter() - t0
    j = r.get_json(silent=True) or {}
    names = {str(s["id"]): s.get("name") for s in t["specs"]}
    comps = [{"id": str(p.get("id")), "name": names.get(str(p.get("id"))), "center": (p.get("params") or {}).get("center", {}).get("value"),
              "area": (p.get("params") or {}).get("area", {}).get("value"),
              "values": {k: v.get("value") for k, v in (p.get("params") or {}).items()},
              "stderr": {k: v.get("stderr") for k, v in (p.get("params") or {}).items()},
              "supported": (p.get("support") or {}).get("supported"), "follows": (p.get("support") or {}).get("follows")}
             for p in (j.get("individual_peaks") or [])]
    st = j.get("starts") or {}
    rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"], "http": r.status_code,
           "success": j.get("success"), "message": (j.get("message") or "")[:160], "chi2r": (j.get("statistics") or {}).get("reduced_chi_square"),
           "sec": round(sec, 3), "random_seed": j.get("random_seed"), "chi2": (j.get("statistics") or {}).get("chi_square"), "components": comps, "certificate": j.get("certificate"),
           "starts": {k: st.get(k) for k in ("ran", "reason", "n_run", "n_converged", "n_same_as_fit", "n_in_alternatives", "n_not_better_elsewhere")}
                     | {"n_alternatives": len(st.get("alternatives") or [])}}
    with open(OUT, 'a') as f: f.write(json.dumps(rec) + "\n")
    cl.delete(f"/api/session/{sid}")
