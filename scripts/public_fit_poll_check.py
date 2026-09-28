#!/usr/bin/env python3
"""Post-deploy check for unit 2 (long fits via start-then-poll), THROUGH THE
PUBLIC URL — the path a student's browser takes, where Cloudflare ends a
single request at ~100 s (HTTP 524).

It does what the page does for Run Fit: upload, POST /api/fit/start, poll
GET /api/fit/progress every 0.5 s until the job leaves "running"; it records
the duration of EVERY request. PASS = the job finishes "done" with
success true, and no request took longer than MAX_REQUEST_S.

Usage:
  python scripts/public_fit_poll_check.py targets.json [BASE_URL] [target_id ...]

targets.json: the optimizer-disagreement target file (branch
investigate-optimizer-disagreement, docs/findings/optimizer-disagreement/
targets.json). Default targets: the five largest committed C 1s models,
the ones that took 183-256 s even without restarts.
"""
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

MAX_REQUEST_S = 10.0
HEARTBEAT_LOST_S = 30.0      # as the page: a record whose heartbeat stopped is a lost fit
DEADLINE_S = 20 * 60         # per target: never poll forever
DEFAULT_TARGETS = ["edf39ecb66ce", "d2bd62d2f976", "496c4edd97af", "0a5f464daf3d", "8b4c2f656a80"]


def _req(url, data=None, headers=None, method=None, timeout=60):
    t0 = time.time()
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "xps-poll-check", **(headers or {})}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body, status = r.read(), r.status
    except urllib.error.HTTPError as e:
        body, status = e.read(), e.code
    return status, body, time.time() - t0


def run(base, t):
    durations = []
    csv = "\n".join(f"{a:.4f},{b:.4f}" for a, b in zip(t["be"], t["inten"])).encode()
    bnd = uuid.uuid4().hex
    form = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.csv\"\r\n"
            f"Content-Type: text/csv\r\n\r\n").encode() + csv + f"\r\n--{bnd}--\r\n".encode()
    st, body, d = _req(base + "/api/upload", form, {"Content-Type": f"multipart/form-data; boundary={bnd}"})
    durations.append(("upload", st, d))
    sid = json.loads(body)["session_id"]
    bg = t["background"]
    payload = {"session_id": sid, "background": {k: bg[k] for k in ("method", "start_idx", "end_idx", "endpoint_avg")},
               "peaks": t["specs"], "fit_method": "basinhopping", "n_perturb": 3, "n_starts": 3}
    st, body, d = _req(base + "/api/fit/start", json.dumps(payload).encode(), {"Content-Type": "application/json"})
    durations.append(("start", st, d))
    if st != 202:
        return {"id": t["id"], "verdict": "FAIL", "why": f"start returned {st}: {body[:200]!r}", "durations": durations}
    job = json.loads(body)["job_id"]
    t0 = time.time()
    while True:
        time.sleep(0.5)
        st, body, d = _req(base + f"/api/fit/progress/{job}")
        durations.append(("poll", st, d))
        rec = json.loads(body) if st == 200 else {"status": f"http {st}"}
        if rec.get("status") not in ("running", "queued"):
            break
        hb = rec.get("heartbeat_age_sec")
        if isinstance(hb, (int, float)) and hb > HEARTBEAT_LOST_S:
            rec = {"status": "lost", "error": f"heartbeat stopped {hb:.0f} s ago (worker restarted?)"}
            break
        if time.time() - t0 > DEADLINE_S:
            _req(base + f"/api/fit/cancel/{job}", b"", method="POST")
            rec = {"status": "deadline", "error": f"no result after {DEADLINE_S} s"}
            break
    longest = max(x[2] for x in durations)
    res = rec.get("result") or {}
    ok = rec.get("status") == "done" and res.get("success") is True and longest <= MAX_REQUEST_S
    return {"id": t["id"], "verdict": "PASS" if ok else "FAIL", "status": rec.get("status"),
            "success": res.get("success"), "chi2r": (res.get("statistics") or {}).get("reduced_chi_square"),
            "fit_wall_s": round(time.time() - t0, 1), "n_requests": len(durations),
            "longest_request_s": round(longest, 2), "error": rec.get("error")}


def main():
    targets = json.load(open(sys.argv[1]))
    base = sys.argv[2] if len(sys.argv) > 2 else "https://xps.fortierlab.org"
    ids = sys.argv[3:] or DEFAULT_TARGETS
    by_id = {t["id"]: t for t in targets}
    results = [run(base, by_id[i]) for i in ids]
    for r in results:
        print(json.dumps(r))
    print("OVERALL:", "PASS" if all(r["verdict"] == "PASS" for r in results) else "FAIL")


if __name__ == "__main__":
    main()
