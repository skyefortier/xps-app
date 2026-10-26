"""Unit B: every candidate noise estimator (scripts/noise_estimators.py) against spectra whose noise is KNOWN.

Ground truth only: each synthetic spectrum is a noise-free signal s (background + peaks) plus noise drawn from a
stated model, so the true per-point variance σ_i² is known exactly. No fit and no expert reference is used.

Per spectrum and estimator — the estimated variance model v̂ evaluated two ways: at the TRUE signal, v̂(s), which
isolates the estimation error, and at the observed y, v̂(y), the plug-in a fit's weights use today (fitting.py:3006
weights by the observed intensity):
  scale = median(v̂(s)_i / σ_i²)                 — the estimator's error in the variance's LEVEL; 1 is right
  spread = 90th / 10th percentile of v̂(s)/σ²     — its error in the variance's SHAPE across the window; 1 is right
  chi2r_est = Σ (y − s)² / v̂(s) / n              — the reduced χ² of the TRUE signal under the estimate
  chi2r_plugin = Σ (y − s)² / v̂(y) / n           — the same with the plug-in weights (differs at low counts, where
                                                   the observed y in the denominator correlates with the numerator)
A chi2r near 1 alone does not establish a correct variance (level and shape errors can cancel in the sum); the
scale and spread are the direct errors.

    venv/bin/python scripts/noise_synthetic_benchmark.py [--seeds 30] [--json OUT]
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import noise_estimators as ne  # noqa: E402


def gl(x, c, fwhm, h, eta=0.3):
    g = np.exp(-4 * np.log(2) * ((x - c) / fwhm) ** 2)
    lo = 1.0 / (1.0 + 4 * ((x - c) / fwhm) ** 2)
    return h * ((1 - eta) * g + eta * lo)


def signal(shape, level, n=241):
    """A C 1s-like window: n points; `shape` sets the peak width in points and the background.
    level = the tallest peak's height above the background, in counts at counting time 1."""
    x = np.arange(n, dtype=float)
    width = {"sharp": 3.0, "typical": 10.0, "wide": 30.0}[shape[0]]
    base = 0.08 * level
    if shape[1] == "flat":
        bg = np.full(n, base)
    elif shape[1] == "slope":
        bg = base * (1.0 + 0.6 * x / n)
    else:                                                       # a Shirley-like step under the peaks
        bg = base * (1.0 + 0.5 / (1.0 + np.exp(-(x - 0.45 * n) / (0.03 * n))))
    peaks = gl(x, 0.40 * n, width, level) + gl(x, 0.52 * n, width * 1.2, 0.35 * level) + gl(x, 0.70 * n, width * 1.5, 0.12 * level)
    return bg + peaks


SMOOTHERS = {
    "ma3": np.ones(3) / 3, "ma5": np.ones(5) / 5,
    "sg7": np.array([-2, 3, 6, 7, 6, 3, -2], float) / 21.0,        # Savitzky-Golay, 7 points, order 2
    "half_bin_shift": np.array([0.5, 0.5]),                         # adjacent means: a half-bin shift, same spacing
}


def draw(s, case, rng):
    """(y, truth signal, true variance) for noise model `case` on signal s (counts at counting time 1)."""
    kind = case["kind"]
    if kind == "poisson":                                           # raw counts
        return rng.poisson(s).astype(float), s, s.copy()
    if kind == "cps":                                               # counts / counting time t
        t = case["t"]
        return rng.poisson(s * t) / t, s, s / t
    if kind == "sweeps":                                            # the mean of m sweeps
        m = case["m"]
        return rng.poisson(s, size=(m, s.size)).mean(axis=0), s, s / m
    if kind == "gauss":                                             # constant noise, independent of intensity
        sd = case["rel"] * np.median(s)
        return s + rng.normal(0, sd, s.size), s, np.full(s.size, sd * sd)
    if kind == "mixed":                                             # shot noise + a constant term
        a = (case["rel"] * np.median(s)) ** 2
        return rng.poisson(s) + rng.normal(0, np.sqrt(a), s.size), s, s + a
    if kind == "transmission":                                      # a smooth per-point correction factor T(x)
        T = 1.0 + case["amp"] * np.linspace(-1, 1, s.size)          # counts recorded ∝ s·T, then divided by T
        return rng.poisson(s * T) / T, s, s / T
    if kind == "smoothed":                                          # scaled Poisson, then a linear smoother
        h = SMOOTHERS[case["filter"]]
        raw = rng.poisson(s * case["t"]) / case["t"]
        y = np.convolve(raw, h, mode="same")
        truth = np.convolve(s, h, mode="same")
        var = np.convolve(s / case["t"], h ** 2, mode="same")
        e = len(h) // 2 + 1                                         # the edges see a truncated filter: drop them
        return y[e:-e], truth[e:-e], var[e:-e]
    if kind == "upsampled":                                         # linear interpolation onto a grid twice as fine
        raw = rng.poisson(s * case["t"]) / case["t"]
        v = s / case["t"]
        y = np.empty(2 * s.size - 1); truth = np.empty_like(y); var = np.empty_like(y)
        y[0::2], truth[0::2], var[0::2] = raw, s, v                 # the measured points kept
        y[1::2] = (raw[:-1] + raw[1:]) / 2                           # midpoints: mean of two independent points
        truth[1::2] = (s[:-1] + s[1:]) / 2
        var[1::2] = (v[:-1] + v[1:]) / 4
        return y, truth, var
    raise ValueError(kind)


CASES = [
    {"name": "poisson counts", "kind": "poisson"},
    {"name": "cps t=0.05 s", "kind": "cps", "t": 0.05},
    {"name": "cps t=1 s", "kind": "cps", "t": 1.0},
    {"name": "cps t=20 s", "kind": "cps", "t": 20.0},
    {"name": "mean of 10 sweeps", "kind": "sweeps", "m": 10},
    {"name": "gaussian constant", "kind": "gauss", "rel": 0.02},
    {"name": "poisson + constant", "kind": "mixed", "rel": 0.05},
    {"name": "transmission ±30 %", "kind": "transmission", "amp": 0.3},
    {"name": "smoothed MA3", "kind": "smoothed", "filter": "ma3", "t": 1.0},
    {"name": "smoothed MA5", "kind": "smoothed", "filter": "ma5", "t": 1.0},
    {"name": "smoothed SG7", "kind": "smoothed", "filter": "sg7", "t": 1.0},
    {"name": "half-bin shift (adjacent means)", "kind": "smoothed", "filter": "half_bin_shift", "t": 1.0},
    {"name": "upsampled x2 (linear)", "kind": "upsampled", "t": 1.0},
]
SHAPES = [(w, b) for w in ("sharp", "typical", "wide") for b in ("flat", "slope", "step")]
LEVELS = [300.0, 3e3, 3e4, 3e5]


def run(seeds):
    np.seterr(divide="ignore", invalid="ignore")      # an estimator that returns zero variance fails: χ² = inf, recorded
    rows = []
    for ci, case in enumerate(CASES):
        for shape in SHAPES:
            for level in LEVELS:
                s0 = signal(shape, level)
                for seed in range(seeds):
                    rng = np.random.default_rng([ci, SHAPES.index(shape), LEVELS.index(level), seed])
                    y, truth, var = draw(s0, case, rng)
                    diag = ne.correlation_diagnostics(y)
                    for name, est in ne.ESTIMATORS.items():
                        model = est(y)
                        v_s, v_y = model.variance(truth), model.variance(y)
                        ratio = v_s / var
                        rows.append({"case": case["name"], "width": shape[0], "bg": shape[1], "level": level, "seed": seed,
                                     "estimator": name, "scale": float(np.median(ratio)),
                                     "chi2r_est": float(np.mean((y - truth) ** 2 / v_s)),
                                     "chi2r_plugin": float(np.mean((y - truth) ** 2 / v_y)),
                                     "spread": float(np.percentile(ratio, 90) / np.percentile(ratio, 10)),
                                     "k": model.k, "a": model.a})
                    rows.append({"case": case["name"], "width": shape[0], "bg": shape[1], "level": level, "seed": seed,
                                 "estimator": "_diagnostics", **diag})
    return rows


def summarise(rows):
    """Per case × estimator: median chi2r_true and its 5-95 % range over every shape, level and seed; then the
    worst shape for each, and per width (the peaks' sharpness is the main failure of difference estimators)."""
    out = {}
    import collections
    by = collections.defaultdict(list)
    for r in rows:
        if r["estimator"] == "_diagnostics":
            by[(r["case"], "_diagnostics")].append(r)
            continue
        by[(r["case"], r["estimator"])].append(r)
    for (case, est), rs in sorted(by.items()):
        if est == "_diagnostics":
            out.setdefault(case, {})["_diagnostics"] = {
                "rho1_d1_median": float(np.median([r["rho1_d1"] for r in rs])),
                "rho1_d4_median": float(np.median([r["rho1_d4"] for r in rs])),
                "lag_profile_median": [float(np.median([r["lag_profile"][i] for r in rs])) for i in range(4)]}
            continue
        def stats(key):
            v = np.array([r[key] for r in rs])
            return {"median": float(np.median(v)), "p05": float(np.percentile(v, 5)), "p95": float(np.percentile(v, 95)),
                    "per_width": {w: float(np.median([r[key] for r in rs if r["width"] == w])) for w in ("sharp", "typical", "wide")},
                    "per_level": {str(int(L)): float(np.median([r[key] for r in rs if r["level"] == L])) for L in LEVELS}}
        out.setdefault(case, {})[est] = {k: stats(k) for k in ("scale", "spread", "chi2r_est", "chi2r_plugin")}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--json")
    ap.add_argument("--markdown", help="write the README's tables (the variance's level error by peak level) here")
    a = ap.parse_args()
    rows = run(a.seeds)
    summary = summarise(rows)
    for case, d in summary.items():
        print(f"\n{case}   (rho1 d1 {d['_diagnostics']['rho1_d1_median']:+.2f} [white -0.50], d4 {d['_diagnostics']['rho1_d4_median']:+.2f} [white -0.80]; lag profile "
              + " ".join(f"{v:.2f}" for v in d['_diagnostics']['lag_profile_median']) + ")")
        for est, m in d.items():
            if est.startswith("_"):
                continue
            sc = m["scale"]
            pl = " ".join(f"{v:5.2f}" for v in sc["per_level"].values())
            print(f"  {est:20s} scale {sc['median']:6.2f} [{sc['p05']:5.2f}, {sc['p95']:6.2f}] by level {pl} | spread {m['spread']['median']:5.2f}"
                  f" | chi2r est {m['chi2r_est']['median']:5.2f} plug-in {m['chi2r_plugin']['median']:6.2f}")
    if a.markdown:
        cols = ["poisson_file_units", "scaled_d1", "scaled_d2", "scaled_d4", "scaled_d2_lag3", "flat_ends", "varmean",
                "der_snr", "constant_d2", "constant_d4"]
        with open(a.markdown, "w") as fh:
            fh.write("Direct error in the variance's LEVEL, median v̂(s)/σ² by peak level (300 / 3e3 / 3e4 / 3e5 counts), over "
                     "the 9 shapes and all seeds; 1 is right, below 1 the variance is underestimated:\n\n")
            fh.write("| noise (truth) | " + " | ".join(f"`{c}`" for c in cols) + " |\n|" + "---|" * (len(cols) + 1) + "\n")
            for case, d in summary.items():
                cells = []
                for c in cols:
                    pl = d[c]["scale"]["per_level"].values()
                    cells.append(" / ".join(f"{v:.2g}" for v in pl))
                fh.write(f"| {case} | " + " | ".join(cells) + " |\n")
            fh.write("\nShape error, median spread (90th / 10th percentile of v̂(s)/σ² across the window; 1 is right), and the "
                     "median χ²ᵣ of the true signal with the plug-in weights v̂(y):\n\n")
            fh.write("| noise (truth) | " + " | ".join(f"`{c}`" for c in cols) + " |\n|" + "---|" * (len(cols) + 1) + "\n")
            for case, d in summary.items():
                fh.write(f"| {case} | " + " | ".join(f"{d[c]['spread']['median']:.2g} · {d[c]['chi2r_plugin']['median']:.2g}" for c in cols) + " |\n")
    if a.json:
        json.dump({"cases": CASES, "shapes": SHAPES, "levels": LEVELS, "seeds": a.seeds, "summary": summary},
                  open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
