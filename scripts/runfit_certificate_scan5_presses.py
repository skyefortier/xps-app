"""A2: twenty presses of 8-JT C1s Scan_5 (Trust-Region) at shifted memory alignments in one process; prints the returned chi2r and the scattered-starts report. Run from a checkout: python scripts/runfit_certificate_scan5_presses.py | sort | uniq -c"""
import sys, io, json; sys.path.insert(0, '.')
import numpy as np
from app import create_app
app = create_app(); cl = app.test_client()
t = next(t for t in json.load(open('/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json')) if t["id"] == "d3f78df20301")
csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
keep = []
for k in range(20):
    keep.append(np.empty(1 + 37 * k))                  # shift where later arrays land
    sid = cl.post("/api/upload", data={"file": (io.BytesIO(csv), "t.csv")}, content_type="multipart/form-data").get_json()["session_id"]
    bg = t["background"]
    j = cl.post("/api/fit", json={"session_id": sid, "background": {kk: bg[kk] for kk in ("method", "start_idx", "end_idx", "endpoint_avg")},
                                  "peaks": t["specs"], "fit_method": "least_squares", "n_perturb": 3, "n_starts": 3}).get_json()
    st = j["starts"]
    print(json.dumps({"returned": round(j["statistics"]["reduced_chi_square"], 2), "same": st["n_same_as_fit"],
                      "not_better": [round(c, 2) for c in st["not_better_chi2r"]], "alternatives": [round(a["chi2r"], 2) for a in st["alternatives"]]}), flush=True)
