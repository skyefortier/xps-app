"""The LA unit's diagnosis (2026-10-15): recompute every recorded LA component of seal 1b's records from its recorded
parameters, compare bit for bit with the recorded curve, and print a digest of all outputs. Run it in several fresh
processes: before the fix the digest differed in every run.

    venv/bin/python scripts/seal_la_recompute.py <records.jsonl> <checkout>
"""
import hashlib, json, sys
sys.path.insert(0, sys.argv[2])
import numpy as np
import fitting
h, n, diff = hashlib.sha256(), 0, 0
for line in open(sys.argv[1]):
    O = json.loads(line)["O"]
    x = np.asarray(O["energy"], float)
    for ip in O["individual_peaks"]:
        if ip["shape"] != "la_casaxps":
            continue
        p = {k: v["value"] for k, v in ip["params"].items() if k != "area"}
        y = fitting._la_casaxps_true(x, **p)
        n += 1
        diff += not np.array_equal(y, np.asarray(ip["y"], float))
        h.update(y.tobytes())
print(f"LA components {n}, differ from the record {diff}, digest {h.hexdigest()[:16]}")
