"""The LA unit's acceptance matrix (Codex LA round 1, both runs): the 107 seal-1b records holding LA(α,β,m),
REGENERATED from their own requests by the code under test, then verified in seal 1b's four settings.

1b's records were made with np.convolve, so a verification by the fixed-order convolution reads them as a different
evaluation; the requests are the corpus. Each phase is the 1b harness's (scripts/seal_1b_measure.py on branch
seal-1b-measure, a46cd3f), with the request's session replaced by a fresh full-precision upload of R's own data.

  record   RECORDS_1B OUT.jsonl              every 1b record whose O holds a la_casaxps component, re-fitted through
                                             the REAL /api/fit route with its own request (fresh upload)
  verify   RECORDS OUT.jsonl [--shake] [--url URL]
                                             POST /api/verify-fit for every record in THIS (fresh) process, or against
                                             a running server (--url: a 4-worker gunicorn); --shake allocates arrays of
                                             random size between verifications (the allocation history changes)
  provenance RECORDS OUT.json                the commit and cleanliness of this checkout, the software identity every
                                             record carries, and per record sha256 of R and O as JSON

Run it once against the checkout BEFORE the unit (np.convolve) and once from the unit's; both start from the same 1b
records. Every phase is resumable (JSONL keyed by record id). The run script is docs/findings/seal-la/matrix/run.sh.
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import urllib.request

# the checkout whose code is measured (SEAL_LA_CODE: the "before" checkout has no copy of this script)
ROOT = os.environ.get("SEAL_LA_CODE") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path[:0] = [ROOT, os.path.join(ROOT, "tests")]
import numpy as np  # noqa: E402


def done_ids(out):
    return {json.loads(l)["id"] for l in open(out)} if os.path.exists(out) else set()


def append(out, rec):
    with open(out, "a") as f:
        f.write(json.dumps(rec) + "\n")


def records(path):
    with open(path) as f:
        for line in f:
            yield json.loads(line)


def client():
    import tempfile
    from app import create_app
    app = create_app(upload_folder=tempfile.mkdtemp(prefix="seal-la-"))
    app.config["TESTING"] = True
    return app.test_client()


def holds_la(rec):
    return any(ip.get("shape") == "la_casaxps" for ip in (rec.get("O") or {}).get("individual_peaks") or [])


def record(src, out):
    c = client()
    done = done_ids(out)
    for rec in records(src):
        if rec["id"] in done or not holds_la(rec):
            continue
        x, y = rec["R"]["energies"], rec["R"]["counts"]
        csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(x, y))     # what the page uploads: full precision
        sid = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
        req = {**rec["R"]["request"], "session_id": sid}
        r = c.post("/api/fit", json=req)
        append(out, {"id": rec["id"], "project": rec["project"], "tab": rec["tab"], "shapes": rec["shapes"],
                     "status": r.status_code, "R": {"request": req, "energies": x, "counts": y}, "O": r.get_json()})


def verify(recs, out, shake=False, url=None):
    c = None if url else client()
    rng = np.random.default_rng(0)
    done = done_ids(out)
    keep = []
    for rec in records(recs):
        if rec["id"] in done or rec["status"] != 200:
            continue
        if shake:
            keep = [np.ones(int(rng.integers(1, 5000))) for _ in range(int(rng.integers(1, 20)))]
        body = {"R": rec["R"], "O": rec["O"]}
        if url:
            req = urllib.request.Request(url.rstrip("/") + "/api/verify-fit", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            v = json.loads(urllib.request.urlopen(req, timeout=300).read())
        else:
            v = c.post("/api/verify-fit", json=body).get_json()
        append(out, {"id": rec["id"], "tab": rec["tab"], "shapes": rec["shapes"], "state": v["state"],
                     "check": v["check"], "reason": v["reason"], "pid": os.getpid(), "shake": shake, "url": url})
    del keep


def _sha(o):
    return hashlib.sha256(json.dumps(o).encode()).hexdigest()


def provenance(recs, out):
    git = lambda *a: subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, check=True).stdout.strip()
    rows, identities = [], set()
    for rec in records(recs):
        sw = (rec.get("O") or {}).get("software")
        identities.add(json.dumps(sw, sort_keys=True))
        rows.append({"id": rec["id"], "status": rec["status"], "success": (rec.get("O") or {}).get("success"),
                     "R_sha256": _sha(rec["R"]), "O_sha256": _sha(rec["O"])})
    json.dump({"commit": git("rev-parse", "HEAD"), "dirty_lines": len(git("status", "--porcelain").splitlines()),
               "software_identities": [json.loads(s) for s in sorted(identities)],
               "records": rows}, open(out, "w"), indent=1)


if __name__ == "__main__":
    phase, args = sys.argv[1], sys.argv[2:]
    if phase == "record":
        record(args[0], args[1])
    elif phase == "verify":
        url = args[args.index("--url") + 1] if "--url" in args else None
        verify(args[0], args[1], shake="--shake" in args, url=url)
    elif phase == "provenance":
        provenance(args[0], args[1])
    else:
        sys.exit(__doc__)
