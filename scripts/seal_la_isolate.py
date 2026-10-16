"""The LA unit's diagnosis (2026-10-15): per process, digests of LA's base curve (np.power), its kernel, np.convolve's
output and a fixed-order convolution of the same inputs, over seal 1b's recorded LA components. Run in several fresh
processes: only np.convolve's digest changed.

    venv/bin/python scripts/seal_la_isolate.py <records.jsonl>
"""
import hashlib, json, sys
import numpy as np
def fixed_conv(b, kr):
    n, h = len(b), len(kr) // 2
    pad = np.concatenate([np.zeros(h), b, np.zeros(h)])
    out = np.zeros(n)
    for j in range(len(kr)):
        out += kr[len(kr) - 1 - j] * pad[j:j + n]
    return out
H = {k: hashlib.sha256() for k in ("base", "kern", "npconv", "fixed")}
for line in open(sys.argv[1]):
    O = json.loads(line)["O"]
    x = np.asarray(O["energy"], float)
    for ip in O["individual_peaks"]:
        if ip["shape"] != "la_casaxps":
            continue
        p = {k: v["value"] for k, v in ip["params"].items() if k != "area"}
        m = max(0.0, min(499.0, float(p["m"])))
        if m < 1e-3:
            continue
        eps = x - p["center"]; fw = max(float(p["fwhm"]), 1e-9)
        L = 1.0 / (1.0 + 4.0 * (eps / fw) ** 2)
        base = np.where(eps >= 0, np.power(L, max(float(p["alpha"]), 1e-3)), np.power(L, max(float(p["beta"]), 1e-3)))
        s = m / 3.0; half = max(1, int(np.ceil(3.5 * s))); k = np.arange(-half, half + 1, dtype=float)
        kern = np.exp(-(k ** 2) / (2.0 * s ** 2)); kern = kern / kern.sum()
        H["base"].update(base.tobytes()); H["kern"].update(kern.tobytes())
        if len(kern) <= len(base):
            H["npconv"].update(np.convolve(base, kern, mode="same").tobytes())
            H["fixed"].update(fixed_conv(base, kern).tobytes())
print(" ".join(f"{k}={v.hexdigest()[:10]}" for k, v in H.items()))
