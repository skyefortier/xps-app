"""Background-math implementation (2026-10-01) measurement: the 202 committed targets
(the optimizer-disagreement target file), each through /api/fit exactly as the page
sends it, plus its net area on its own background window — run from the checkout
under test (cwd). Resumable JSONL.

Usage: python bg_math_impl_measure.py OUT.jsonl VARIANT [METHOD] [AVG]
  VARIANT  main        — run from a checkout of main (the old reading and stop)
           item1_only  — run from the branch: main's own algorithms with ONLY the levels
                         reading (scripts/bg_math_impl_item1_only.py), no certificate:
                         owner item (1) alone
           both        — the branch at round 17: items (1) + (3) and the certificate, the
                         page's old 2-dp upload
           final       — the branch after the owner's 2026-10-03 changes: the request seed
                         from INPUTS, the FULL-PRECISION upload, linear on averaged levels
  METHOD   lmfit method, default least_squares (the page's default)
  AVG      override every target's endpoint averaging (e.g. 3, the page's default since
           2026-09: most committed fits were saved at 1, where item (1) changes nothing)
"""
import io
import json
import os
import sys
import time

sys.path.insert(0, ".")
import numpy as np  # noqa: E402

OUT, VARIANT = sys.argv[1], sys.argv[2]
METHOD = sys.argv[3] if len(sys.argv) > 3 else "least_squares"
AVG = int(sys.argv[4]) if len(sys.argv) > 4 else None
import fitting  # noqa: E402

if VARIANT == "item1_only":
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import bg_math_impl_item1_only as I1
    for _name in ("shirley_background", "smart_background", "smart_experimental_background",
                  "shirley_linear_background", "tougaard_background"):
        setattr(fitting, _name, getattr(I1, _name))
    _fns = {"shirley": I1.shirley_background, "smart": I1.smart_background,
            "smart_exp": I1.smart_experimental_background, "shirley_linear": I1.shirley_linear_background,
            "tougaard": I1.tougaard_background}
    fitting.compute_background = lambda x, y, m, n_avg=1: _fns[m.lower()](np.asarray(x, float), np.asarray(y, float), n_avg=n_avg)
    fitting.background_certificate = lambda *a, **k: {"converged": True, "residual": None, "reason": None}
elif VARIANT not in ("main", "both", "final"):
    raise SystemExit("unknown variant " + VARIANT)

FUNCS = {"shirley": "shirley_background", "smart": "smart_background",
         "smart_exp": "smart_experimental_background", "shirley_linear": "shirley_linear_background",
         "tougaard": "tougaard_background"}

from app import create_app  # noqa: E402

app = create_app()
cl = app.test_client()
T = json.load(open("/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json"))
done = set()
if os.path.exists(OUT):
    for line in open(OUT):
        done.add(json.loads(line)["id"])
for t in T:
    if t["id"] in done:
        continue
    bg = dict(t["background"])
    if AVG is not None:
        bg["endpoint_avg"] = AVG
    x = np.asarray(t["be"], float)
    # what the server receives: the page's uploadToBackend sent 2 dp; full precision since 2026-10-03
    y = np.asarray(t["inten"] if VARIANT == "final" else [float(f"{v:.2f}") for v in t["inten"]], float)
    i0, i1 = int(bg["start_idx"]), int(bg["end_idx"])
    xw, yw = x[i0:i1], y[i0:i1]
    try:
        B = getattr(fitting, FUNCS[bg["method"]])(xw, yw, n_avg=int(bg["endpoint_avg"]))
        net = float(abs(np.trapezoid(yw - B, xw)))
        cert = fitting.background_certificate(xw, yw, B, bg["method"], int(bg["endpoint_avg"])) if hasattr(fitting, "background_certificate") else None
        bgrec = {"net_area": net, "converged": None if cert is None else cert["converged"], "bg": [float(v) for v in B]}
    except Exception as e:  # noqa: BLE001
        bgrec = {"error": str(e)[:200]}
    if VARIANT == "final":       # uploadToBackend since 2026-10-03: String(v), the shortest round-trip text
        csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(t["be"], t["inten"])).encode()
    else:                        # uploadToBackend before: toFixed(4), toFixed(2)
        csv = "\n".join(f"{a:.4f},{b:.2f}" for a, b in zip(t["be"], t["inten"])).encode()
    sid = cl.post("/api/upload", data={"file": (io.BytesIO(csv), "t.csv")}, content_type="multipart/form-data").get_json()["session_id"]
    body = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
            "peaks": t["specs"], "fit_method": METHOD, "n_perturb": 3, "n_starts": 3}
    t0 = time.perf_counter()
    r = cl.post("/api/fit", json=body)
    sec = time.perf_counter() - t0
    j = r.get_json(silent=True) or {}
    names = {str(s["id"]): s.get("name") for s in t["specs"]}
    comps = [{"id": str(p.get("id")), "name": names.get(str(p.get("id"))),
              "center": (p.get("params") or {}).get("center", {}).get("value"),
              "area": (p.get("params") or {}).get("area", {}).get("value"),
              "supported": (p.get("support") or {}).get("supported")}
             for p in (j.get("individual_peaks") or [])]
    rec = {"id": t["id"], "project": t["project"], "tab": t["tab"], "kind": t["kind"], "variant": VARIANT,
           "method": bg["method"], "endpoint_avg": bg["endpoint_avg"], "http": r.status_code,
           "success": j.get("success"), "error": j.get("error"), "message": (j.get("message") or "")[:160],
           "chi2r": (j.get("statistics") or {}).get("reduced_chi_square"), "sec": round(sec, 3),
           "components": comps, "background": bgrec, "server_bg": j.get("background_y") or j.get("background"),
           "starts": None if not isinstance(j.get("starts"), dict) else {
               k: j["starts"].get(k) for k in ("ran", "n_converged", "n_same_as_fit", "n_not_better_elsewhere", "n_in_alternatives")}
               | {"n_alternatives": len(j["starts"].get("alternatives") or [])},
           "random_seed": j.get("random_seed")}
    with open(OUT, "a") as f:
        f.write(json.dumps(rec) + "\n")
    cl.delete(f"/api/session/{sid}")
