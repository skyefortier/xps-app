#!/usr/bin/env python3
"""Restore the gitignored .stage9/extract_claude/<El>_nist.html artifacts from
their recorded Internet Archive snapshot URLs.

No-invention: every URL comes from committed provenance
(data/xps/elements-machine.provenance.json) or the Stage-9 observations file
(.stage9/extract_claude/observations_4a.json). Where a committed sha256 exists
(emitted records) it is verified; the remaining artifacts are verified by the
byte-identical regeneration test (gen_machine_tier build vs committed outputs).
"""
import hashlib
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEST = os.path.join(HERE, "extract_claude")
UA = "Mozilla/5.0 (xps-reference-research; artifact-restoration)"


def http_get(url, timeout=60, retries=4):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(4 * (i + 1))
    raise last


def main():
    prov = json.load(open(os.path.join(REPO, "data", "xps", "elements-machine.provenance.json")))
    obs = json.load(open(os.path.join(DEST, "observations_4a.json")))["observations"]

    # artifact -> (url, sha256 or None)
    plan = {}
    for p in prov["transitions"]:
        if p.get("acquisition"):
            continue  # expansion artifacts live in expand_artifacts/ and exist
        ns = p["nominal_source"]
        plan[ns["source_artifact"]] = (ns["source_url"], ns["source_artifact_sha256"])
    for o in obs:
        el = o.get("element") or o.get("field_id", "").split("-")[0]
        art = f"{el}_nist.html"
        if art not in plan and o.get("source_url"):
            plan.setdefault(art, (o["source_url"], None))

    ok, bad = [], []
    for art, (url, sha) in sorted(plan.items()):
        path = os.path.join(DEST, art)
        if os.path.exists(path):
            if sha is None or hashlib.sha256(open(path, "rb").read()).hexdigest() == sha:
                ok.append((art, "already-present"))
                continue
        try:
            raw = http_get(url)
        except Exception as e:
            bad.append((art, f"fetch-failed: {e}"))
            print(f"FAIL {art}: {e}", flush=True)
            continue
        got = hashlib.sha256(raw).hexdigest()
        if sha is not None and got != sha:
            bad.append((art, f"sha256 mismatch: got {got[:12]} want {sha[:12]}"))
            print(f"HASH-MISMATCH {art}", flush=True)
            continue
        with open(path, "wb") as f:
            f.write(raw)
        ok.append((art, "restored" + ("+sha-verified" if sha else "")))
        print(f"OK {art} ({len(raw)} bytes){' sha-verified' if sha else ''}", flush=True)
        time.sleep(1.5)

    print(f"\nDONE: {len(ok)} ok, {len(bad)} failed")
    for a, r in bad:
        print(f"  FAILED {a}: {r}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
