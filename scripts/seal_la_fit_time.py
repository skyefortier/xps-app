"""The LA unit: wall time of committed LA Run Fit requests (seal 1b's records) on the checkout given.

    venv/bin/python scripts/seal_la_fit_time.py <checkout> <records.jsonl> <ids.json>
"""
import io, json, sys, tempfile, time
sys.path.insert(0, sys.argv[1])
from app import create_app
app = create_app(upload_folder=tempfile.mkdtemp()); app.config["TESTING"] = True
recs = [json.loads(l) for l in open(sys.argv[2])]
la = [r for r in recs if any(ip["shape"] == "la_casaxps" for ip in r["O"]["individual_peaks"]) and r["id"] in set(json.loads(open(sys.argv[3]).read()))][:12]
out = []
with app.test_client() as c:
    for r in la:
        R = r["R"]
        csv = "\n".join(f"{float(e)!r},{float(v)!r}" for e, v in zip(R["energies"], R["counts"]))
        sid = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
        t0 = time.perf_counter()
        resp = c.post("/api/fit", json={**R["request"], "session_id": sid})
        out.append(round(time.perf_counter() - t0, 2))
print(json.dumps(out))
