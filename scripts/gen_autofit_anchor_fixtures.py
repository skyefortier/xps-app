#!/usr/bin/env python3
"""Generate tests/js/fixtures/autofit_anchor.json: real fitting.run_fit responses
(trimmed to what _autoFitGraphiteIsSupported reads) for every case the Codex
reviews of the Auto-Fit zero-amplitude charge-reference fix produced, plus two
committed-style controls. The Node test asserts the shipped JS rule on them.

Inputs are rounded to 2 dp exactly as uploadToBackend does. Trust-Region is not
bitwise repeatable, so regenerating changes low-order digits; the committed
file is what the test uses. Usage: python scripts/gen_autofit_anchor_fixtures.py
"""
import json
import sys
import warnings
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import fitting  # noqa: E402

warnings.filterwarnings("ignore")
LN2 = np.log(2)


def agl(x, a, c, w):
    return fitting._SHAPE_FUNCS["asymmetric_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=0.3, asymmetry=0.25)


def gl(x, a, c, w):
    return fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=0.3)


def gauss(x, a, c, w):
    return a * np.exp(-4 * LN2 * ((x - c) / w) ** 2)


SIDE = [(285.3, 0.8), (286.2, 0.8), (287.8, 0.8), (291.0, 1.0)]


def five(x, a):
    return agl(x, a, 284.5, 0.7) + sum(gl(x, 0.2 * a, c, w) for c, w in SIDE)


def model(amp, n=5):
    out = []
    for i, (c, w) in enumerate([(284.5, 0.7)] + SIDE):
        s = {"id": str(i + 1), "shape": "asymmetric_gl" if i == 0 else "pseudo_voigt_gl", "center": c,
             "amplitude": max(amp * (1 if i == 0 else 0.2), 1e-3), "fwhm": w, "gl_ratio": 0.3,
             "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0}
        if i == 0:
            s.update(center_min=284.2, center_max=284.8, asymmetry=0.25, asymmetry_min=0.1, asymmetry_max=0.5)
        out.append(s)
    return out[:n]


x = np.round(np.arange(280.0, 295.0001, 0.05), 4)
rng = np.random.default_rng(0)
spiky = 1000 + five(x, 10000)
spiky[int(np.argmin(np.abs(x - 284.5)))] += 300000
CASES = [
    # name, supported?, y, specs, background, manual anchors
    ("residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)", False,
     1e7 + gauss(x, 1e-4, 284.5, 0.4), model(30), "manual", [[280, 1e7], [295, 1e7]]),
    ("residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)", False,
     10.009999 + gauss(x, 1e-4, 284.5, 0.4), model(30), "manual", [[280, 10.009999], [295, 10.009999]]),
    ("residue: 10 + 1e-4 bump, linear background (round 2)", False,
     10 + gauss(x, 1e-4, 284.5, 0.4), model(30), "linear", None),
    ("collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)", False,
     1000 + gauss(x, 30, 284.5, 0.3), model(30), "manual", [[280, 1020], [295, 1020]]),
    ("resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)", True,
     agl(x, 0.0058, 284.5, 0.7), model(0.0058, 1), "manual", [[280, 0], [295, 0]]),
    ("resolved 50-count line on a noise-free 1e6 background (round 4)", True,
     1e6 + five(x, 50), model(50), "manual", [[280, 1e6], [295, 1e6]]),
    ("resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)", True,
     rng.poisson((100000 + 15000 * (x - 278) + agl(x, 10000, 284.5, 0.7)) * 100) / 100.0, model(10000, 1), "linear", None),
    ("resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)", True,
     spiky, model(10000), "linear", None),
    ("ordinary C 1s: 86 000-count graphite line with Poisson noise", True,
     rng.poisson(1500 + five(x, 86000)).astype(float), model(80000), "shirley", None),
]


def trim(res, gid):
    ip = next(p for p in res["individual_peaks"] if str(p["id"]) == gid)
    return {"success": res["success"], "counts": res["counts"], "fitted_y": res["fitted_y"],
            "statistics": {"n_free_params": res["statistics"]["n_free_params"], "reduced_chi_square": res["statistics"]["reduced_chi_square"]},
            "individual_peaks": [{"id": ip["id"], "y": ip["y"],
                                  "params": {k: {"value": v["value"], "stderr": v.get("stderr"), "vary": v.get("vary"), "expr": v.get("expr")}
                                             for k, v in ip["params"].items()}}]}


out = []
for name, supported, y, specs, bg, manual in CASES:
    res = fitting.run_fit(x, np.round(y, 2), specs, background_method=bg, manual_bg=manual, n_perturb=3,
                          fit_kws={"method": "least_squares"})
    g = next(p for p in res["individual_peaks"] if str(p["id"]) == "1")["params"]
    out.append({"name": name, "supported": supported,
                "graphite": {"id": "1", "amplitude": g["amplitude"]["value"], "center": g["center"]["value"]},
                "json": trim(res, "1")})
    print(f"{'SUPPORTED  ' if supported else 'unsupported'} amp {g['amplitude']['value']:12.6g}  centre {g['center']['value']:.4f}  {name}")
dest = ROOT / "tests/js/fixtures/autofit_anchor.json"
dest.write_text(json.dumps(out))
print("wrote", dest, dest.stat().st_size // 1024, "KB")
