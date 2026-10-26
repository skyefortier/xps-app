"""Unit B: every candidate noise estimator (scripts/noise_estimators.py) against spectra whose noise is KNOWN.

Ground truth only: each synthetic spectrum is a noise-free signal s (background + peaks) plus noise drawn from a
stated model, so the true per-point variance σ_i² is known exactly. No fit and no expert reference is used.

Per spectrum and estimator:
  scale  = median(σ̂_i² / σ_i²)                — 1 when the estimator recovers the variance's level
  chi2r_true = Σ (y_i − s_i)² / σ̂_i² / n       — the reduced χ² of the TRUE signal under the estimated noise:
                                                  what a fit that explains the data down to the noise would show;
                                                  the target is 1
  spread = 90th / 10th percentile of σ̂_i² / σ_i²   — 1 when the estimator also gets the SHAPE of the variance
                                                    (its dependence on intensity) right

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
    "interp_half": np.array([0.5, 0.5]),                            # linear interpolation onto a half-step grid
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
    {"name": "interpolated (half step)", "kind": "smoothed", "filter": "interp_half", "t": 1.0},
]
SHAPES = [(w, b) for w in ("sharp", "typical", "wide") for b in ("flat", "slope", "step")]
LEVELS = [300.0, 3e3, 3e4, 3e5]


def run(seeds):
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
                        v = model.variance(y)
                        ratio = v / var
                        rows.append({"case": case["name"], "width": shape[0], "bg": shape[1], "level": level, "seed": seed,
                                     "estimator": name, "scale": float(np.median(ratio)),
                                     "chi2r_true": float(np.mean((y - truth) ** 2 / v)),
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
        c = np.array([r["chi2r_true"] for r in rs])
        per_width = {w: float(np.median([r["chi2r_true"] for r in rs if r["width"] == w])) for w in ("sharp", "typical", "wide")}
        per_level = {str(int(L)): float(np.median([r["chi2r_true"] for r in rs if r["level"] == L])) for L in LEVELS}
        out.setdefault(case, {})[est] = {"chi2r_true_median": float(np.median(c)),
                                         "chi2r_true_p05": float(np.percentile(c, 5)), "chi2r_true_p95": float(np.percentile(c, 95)),
                                         "spread_median": float(np.median([r["spread"] for r in rs])),
                                         "per_width": per_width, "per_level": per_level}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--json")
    a = ap.parse_args()
    rows = run(a.seeds)
    summary = summarise(rows)
    for case, d in summary.items():
        print(f"\n{case}   (rho1 d1 {d['_diagnostics']['rho1_d1_median']:+.2f} [white -0.50], d4 {d['_diagnostics']['rho1_d4_median']:+.2f} [white -0.80]; lag profile "
              + " ".join(f"{v:.2f}" for v in d['_diagnostics']['lag_profile_median']) + ")")
        for est, m in d.items():
            if est.startswith("_"):
                continue
            pw = " ".join(f"{w[:5]} {v:6.2f}" for w, v in m["per_width"].items())
            print(f"  {est:20s} chi2r_true {m['chi2r_true_median']:7.3f}  [{m['chi2r_true_p05']:7.3f}, {m['chi2r_true_p95']:7.3f}]"
                  f"  shape-spread {m['spread_median']:6.2f}   by width: {pw}")
    if a.json:
        json.dump({"cases": CASES, "shapes": SHAPES, "levels": LEVELS, "seeds": a.seeds, "summary": summary},
                  open(a.json, "w"), indent=1)


if __name__ == "__main__":
    main()
