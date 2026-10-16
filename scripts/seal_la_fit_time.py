"""The LA unit: wall time of every seal-1b request holding LA(α,β,m) (107: 89 committed, 18 synthetic), through the
real /api/fit route in process, on the checkout given. Every response must be HTTP 200 with success true.

    venv/bin/python scripts/seal_la_fit_time.py <checkout> <seal-1b records.jsonl> <out.json>

Writes {checkout commit, per record: id, seconds, components, LA kernel taps of the widest LA component}.
"""
import io
import json
import subprocess
import sys
import tempfile
import time

CODE, SRC, OUT = sys.argv[1:4]
sys.path.insert(0, CODE)
from app import create_app  # noqa: E402

app = create_app(upload_folder=tempfile.mkdtemp())
app.config["TESTING"] = True
rows = []
with app.test_client() as c:
    for line in open(SRC):
        r = json.loads(line)
        la = [ip for ip in r["O"]["individual_peaks"] if ip["shape"] == "la_casaxps"]
        if not la:
            continue
        R = r["R"]
        csv = "\n".join(f"{float(e)!r},{float(v)!r}" for e, v in zip(R["energies"], R["counts"]))
        sid = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
        t0 = time.perf_counter()
        resp = c.post("/api/fit", json={**R["request"], "session_id": sid})
        dt = time.perf_counter() - t0
        body = resp.get_json()
        assert resp.status_code == 200 and body["success"] is True, (r["id"], resp.status_code, body.get("message"))
        m = max(ip["params"]["m"]["value"] for ip in body["individual_peaks"] if ip["shape"] == "la_casaxps")
        taps = 0 if m < 1e-3 else 2 * max(1, -(-3.5 * m // 3)) + 1
        rows.append({"id": r["id"], "seconds": round(dt, 3), "components": len(body["individual_peaks"]),
                     "widest_la_taps": int(taps)})
commit = subprocess.run(["git", "-C", CODE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
json.dump({"commit": commit, "records": rows}, open(OUT, "w"), indent=1)
s = sorted(x["seconds"] for x in rows)
print(len(s), "fits; median", (s[len(s) // 2] + s[(len(s) - 1) // 2]) / 2, "max", s[-1], "total", round(sum(s), 1))
