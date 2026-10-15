"""Seal 1d (docs/superpowers/plans/2026-10-15-seal-1d-rerun.md, "Measured before review"): what "Re-run this fit"
says on the committed fits.

For each committed record of seal 1b's run v2 (R = the request Run Fit sent, its uploaded samples; O = the reply), the
page's re-run through the app's own routes, in process: the samples uploaded (`/api/upload`, full precision), R's
request with `seed: O.random_seed` (`/api/fit`), and the two replies judged by `/api/compare-fits`. Reports how many
reproduce, reach a different solution, differ only in their starts, run under other numerics or fail.

    venv/bin/python scripts/seal_1d_rerun_measure.py <records.jsonl> <targets.json> [--json OUT]
"""
import argparse
import io
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import create_app  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records")
    ap.add_argument("targets")
    ap.add_argument("--json")
    a = ap.parse_args()
    committed = {t["id"] for t in json.load(open(a.targets))}
    app = create_app(upload_folder=tempfile.mkdtemp(prefix="seal1d-"))
    app.config["TESTING"] = True
    rows = []
    with app.test_client() as c:
        for line in open(a.records):
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec["id"] not in committed:
                continue
            R, O = rec["R"], rec["O"]
            t0 = time.time()
            csv = "\n".join(f"{float(e)!r},{float(v)!r}" for e, v in zip(R["energies"], R["counts"]))
            up = c.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
            row = {"id": rec["id"], "project": rec["project"], "tab": rec["tab"], "shapes": rec.get("shapes")}
            if up.status_code != 200:
                row.update(outcome="failed", reason=f"upload HTTP {up.status_code}")
            else:
                r = c.post("/api/fit", json={**R["request"], "session_id": up.get_json()["session_id"], "seed": O["random_seed"]})
                O2 = r.get_json()
                if r.status_code != 200 or not isinstance(O2, dict) or O2.get("success") is not True:
                    row.update(outcome="failed", reason=f"fit HTTP {r.status_code}: {(O2 or {}).get('error') or (O2 or {}).get('message')}")
                else:
                    cmp_ = c.post("/api/compare-fits", json={"a": O, "b": O2})
                    v = cmp_.get_json()
                    if cmp_.status_code != 200:
                        row.update(outcome="failed", reason=f"compare HTTP {cmp_.status_code}: {v}")
                    else:
                        row.update(outcome="reproduced" if v["same"] else "different solution", problems=v["problems"],
                                   n_problems=v["n_problems"], starts_same=v["starts"]["same"],
                                   starts_problems=v["starts"]["problems"], numerics_same=v["numerics"]["same"])
            row["seconds"] = round(time.time() - t0, 2)
            rows.append(row)
            print(f"{len(rows):3d} {row['outcome']:18s} starts {'same' if row.get('starts_same') else 'DIFFER' if 'starts_same' in row else '-':6s} "
                  f"{row['seconds']:6.1f}s  {row['project'][:40]} / {row['tab']}", flush=True)
    n = len(rows)
    by = {}
    for r in rows:
        by[r["outcome"]] = by.get(r["outcome"], 0) + 1
    print(f"\n{n} committed records re-run: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))
    print(f"  starts differ (fit reproduced): {sum(1 for r in rows if r['outcome'] == 'reproduced' and r.get('starts_same') is False)}")
    print(f"  other numerics: {sum(1 for r in rows if r.get('numerics_same') is False)}")
    for r in rows:
        if r["outcome"] != "reproduced":
            print(f"  {r['outcome']}: {r['project']} / {r['tab']} {r.get('shapes')}: {(r.get('problems') or [r.get('reason')])[:2]}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(rows, fh, indent=1)


if __name__ == "__main__":
    main()
