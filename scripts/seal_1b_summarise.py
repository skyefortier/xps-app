"""Seal 1b: the numbers in docs/findings/seal-1b/README.md, from the JSONL beside it.

Usage: python scripts/seal_1b_summarise.py [docs/findings/seal-1b]
"""
import json
import os
import sys
from collections import Counter

D = sys.argv[1] if len(sys.argv) > 1 else "docs/findings/seal-1b"


def rows(name):
    p = os.path.join(D, name)
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def kind(r):
    return "synthetic" if str(r["id"]).startswith("syn-") else "committed"


rec = rows("records_index.jsonl")
if rec:
    print(f"== records: {len(rec)} ({Counter(kind(r) for r in rec)}); HTTP status {Counter(r['status'] for r in rec)}; "
          f"converged {sum(1 for r in rec if r.get('success'))}")

for name in ("verify_fresh_1.jsonl", "verify_fresh_2.jsonl", "verify_shake.jsonl", "verify_gunicorn.jsonl"):
    R = rows(name)
    if not R:
        continue
    print(f"== {name}: {len(R)}")
    for k in ("committed", "synthetic"):
        sub = [r for r in R if kind(r) == k]
        print(f"   {k}: {dict(Counter((r['state'], r['check']) for r in sub))}")
    not_ok = Counter(tuple(r["shapes"]) for r in R if r["state"] != "consistent")
    print(f"   not consistent, by lineshapes: {dict(not_ok)}")
    by_shape = {}
    for r in R:
        for s in r["shapes"]:
            by_shape.setdefault(s, Counter())[r["state"]] += 1
    print(f"   by lineshape present: {{{', '.join(f'{s}: {dict(c)}' for s, c in sorted(by_shape.items()))}}}")

S = rows("sizes.jsonl")
if S:
    for k in ("R_bytes", "O_bytes", "R_gzip", "O_gzip"):
        v = sorted(r[k] for r in S if kind(r) == "committed")
        print(f"== size {k} (committed): median {v[len(v) // 2]}, max {v[-1]}, total {sum(v)}")

B = rows("background_twin.jsonl")
if B:
    for k in ("committed", "synthetic"):
        sub = [b for b in B if kind(b) == k]
        print(f"== background twin {k}: {len(sub)}; window recovered {sum(b['window_recovered'] for b in sub)}; "
              f"bit-identical {sum(bool(b.get('identical')) for b in sub)}; by method "
              f"{dict(Counter((b['method'], b.get('identical')) for b in sub))}; differing "
              f"{[(b['tab'], b['method'], b.get('n_differ'), b.get('max_abs')) for b in sub if b.get('window_recovered') and not b.get('identical')][:10]}")

P = rows("replay.jsonl")
if P:
    for k in ("committed", "synthetic"):
        sub = [p for p in P if kind(p) == k]
        print(f"== replay {k}: {len(sub)}; {dict(Counter(p['outcome'] for p in sub))}; byte-identical "
              f"{sum(bool(p.get('identical')) for p in sub)}")
        diff = [(p["tab"], p["shapes"], (p.get("detail") or "")[:120]) for p in sub if p["outcome"] != "reproduced"]
        for d in diff[:12]:
            print(f"   {d}")
