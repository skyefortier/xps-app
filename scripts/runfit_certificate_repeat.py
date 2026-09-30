"""A2: two presses of the identical request — how reproducible is each configuration?
Usage: python runfit_certificate_repeat.py FIRST.jsonl SECOND.jsonl  (records from runfit_certificate_measure.py)."""
import json, sys
import numpy as np
L = lambda f: {json.loads(l)["id"]: json.loads(l) for l in open(f)}
A, B = L(sys.argv[1]), L(sys.argv[2])
same = diff = 0; dpp = []; worst = []
for i, b in B.items():
    a = A.get(i)
    if a is None or not (a["success"] and b["success"]):
        continue
    ident = a["chi2"] == b["chi2"] and [c["values"] for c in a["components"]] == [c["values"] for c in b["components"]]
    same += ident; diff += not ident
    def frac(r):
        sup = [c for c in r["components"] if c["supported"] is not False]
        t = sum(c["area"] for c in sup)
        return {c["id"]: 100 * c["area"] / t for c in sup}
    fa, fb = frac(a), frac(b)
    m = max(abs(fa.get(k, 0) - fb.get(k, 0)) for k in set(fa) | set(fb))
    dpp.append(m); worst.append((m, i, a["tab"], a["chi2r"], b["chi2r"]))
d = np.array(dpp)
print(json.dumps({"compared": len(d), "byte_identical": same, "differ": diff, "max_pp": float(d.max()),
                  "over_0_01pp": int((d > 0.01).sum()), "over_0_1pp": int((d > 0.1).sum()), "over_1pp": int((d > 1).sum()),
                  "worst": [[round(w[0], 3), w[1], w[2], round(w[3], 4), round(w[4], 4)] for w in sorted(worst, reverse=True)[:5]]}, indent=1))
