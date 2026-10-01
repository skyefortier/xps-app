#!/usr/bin/env python3
"""Backend bridge for tests/js/background_parity.test.js (unit 4, 2026-09-27).

stdin {"mode": "cases"} -> the spectra the parity test runs on: seeded
synthetic spectra (a narrow C 1s, a wide U 4f doublet) and the committed real
U 4f Scan_0 (1-GTA UCl4-graphite project), each ascending AND descending.
stdin {"mode": "mean", "arrays": [[...]...]} -> np.mean of each (the page's
_npMean must equal it bit for bit).
stdin {"mode": "cert", "items": [...as "bg"]} -> fitting.background_certificate's
verdict {converged, reason} on that background (background math, 2026-10-01).
stdin {"mode": "bg", "items": [{"method", "be", "inten", "n_avg", "n_iter"?}...]} -> the
background fitting.py's OWN function returns for each (the functions run_fit
calls for the anchor window, never a reimplementation).
"""
import io
import json
import os
import sys
import zipfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
import fitting  # noqa: E402

FUNCS = {
    "shirley": lambda x, y, n, it: fitting.shirley_background(x, y, n_iter=it, n_avg=n),
    "smart": lambda x, y, n, it: fitting.smart_background(x, y, n_iter=it, n_avg=n),
    "smart_exp": lambda x, y, n, it: fitting.smart_experimental_background(x, y, n_iter=it, n_avg=n),
    "shirley_linear": lambda x, y, n, it: fitting.shirley_linear_background(x, y, n_iter=it, n_avg=n),
    "tougaard": lambda x, y, n, it: fitting.tougaard_background(x, y, n_avg=n),
    "linear": lambda x, y, n, it: fitting.linear_background(x, y),
}


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _shirley_step(x, c, a, w, h):
    # a loss step under each line, high-BE side (makes Shirley non-trivial)
    return h * a / (1 + np.exp(-(x - c) / (0.4 * w)))


def cases():
    rng = np.random.default_rng(20260927)
    out = []
    x = np.linspace(280.0, 295.0, 101)
    y = rng.poisson(400 + _g(x, 284.5, 6000, 1.0) + _g(x, 286.3, 1200, 1.2) + _shirley_step(x, 284.5, 6000, 1.0, 0.06)).astype(float)
    out.append(("synthetic C 1s, 101 pts", x, y))
    x = np.linspace(370.0, 405.0, 351)
    y = rng.poisson(2000 + _g(x, 380.9, 20000, 1.6) + _g(x, 391.8, 15000, 1.6)
                    + _shirley_step(x, 380.9, 20000, 1.6, 0.08) + _shirley_step(x, 391.8, 15000, 1.6, 0.08)).astype(float)
    out.append(("synthetic U 4f doublet, 351 pts", x, y))
    proj = os.path.join(ROOT, "docs", "autofit", "test_data", "1-GTA UCl4-graphite one set of U doublets.proj.zip")
    if os.path.exists(proj):
        with zipfile.ZipFile(proj) as z:
            man = json.loads(z.read("manifest.json"))
            for sp in man.get("spectra", []):
                if sp.get("name") == "U4f Scan_0":
                    rec = json.loads(z.read(sp["filename"]))
                    be = np.asarray(rec["rawBE"], float) - float(rec.get("ccShift") or 0)
                    out.append(("real U 4f Scan_0 (committed project)", be, np.asarray(rec["rawIntensity"], float)))
                    break
    res = []
    for label, x, y in out:
        asc = np.argsort(x)
        res.append({"label": label + ", ascending", "be": x[asc].tolist(), "inten": y[asc].tolist()})
        res.append({"label": label + ", descending", "be": x[asc][::-1].tolist(), "inten": y[asc][::-1].tolist()})
    return res


def main():
    req = json.load(sys.stdin)
    if req["mode"] == "cases":
        json.dump(cases(), sys.stdout)
        return
    if req["mode"] == "mean":
        json.dump([float(np.mean(np.asarray(a, float))) for a in req["arrays"]], sys.stdout)
        return
    if req["mode"] == "cert":
        res = []
        for it in req["items"]:
            x, y = np.asarray(it["be"], float), np.asarray(it["inten"], float)
            bg = FUNCS[it["method"]](x, y, int(it["n_avg"]), int(it.get("n_iter", 200)))
            c = fitting.background_certificate(x, y, bg, it["method"], int(it["n_avg"]))
            res.append({"converged": bool(c["converged"]), "reason": c["reason"]})
        json.dump(res, sys.stdout)
        return
    out = []
    for it in req["items"]:
        x = np.asarray(it["be"], float)
        y = np.asarray(it["inten"], float)
        out.append([float(v) for v in FUNCS[it["method"]](x, y, int(it["n_avg"]), int(it.get("n_iter", 200)))])
    json.dump(out, sys.stdout)


if __name__ == "__main__":
    main()
