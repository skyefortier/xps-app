"""
Empirical noise estimation (run-brief item 3a; fitalg LIMITATIONS §8,
spec §9).

THE PROBLEM: every per-point-weighted path in this engine uses
``1/sqrt(max(y,1))`` (``methods.base.poisson_like_weights``), which is the
correct Poisson σ ONLY for raw integer counts.  Real exports are often
PROCESSED intensities — count rates (counts/s ≠ counts), scan-averaged,
transmission-corrected, or rescaled — where σ² = a + b·I with b ≠ 1 (and
the Bayesian method separately assumes homoscedastic noise).  Agreement
between methods under a shared wrong noise model is shared bias, not
corroboration.

THE ESTIMATOR (replicates): repeat scans of the same region on the SAME
acquisition grid (the labeled projects carry n=3–10 such replicates).  For
each adjacent scan pair the difference d = y_a − y_b cancels the static
signal exactly; two honest corrections remain:

- SHIFT DRIFT: each scan charge-references slightly differently (measured
  ccShift spreads ~0.01–0.06 eV), so the true spectra are BE-shifted and
  d leaks the signal derivative: d ≈ ΔBE·(dy/dE) + noise.  We regress the
  gradient of the ensemble-mean spectrum out of each pair difference (the
  fitted coefficient IS the pair's relative shift — reported, and
  cross-checkable against the saved ccShift differences).
- SCALE DRIFT: source-intensity drift between scans scales the signal;
  we regress out the mean-spectrum component as well.

After drift removal, Var(d) = 2σ²(I) pointwise.  We bin d²/2 by the local
mean intensity (robust median × 1.4826² per bin) and fit
``σ²(I) = a + b·I`` by weighted least squares.  For raw counts the truth
is (a=0, b=1); for a rate/gain-scaled export b recovers the effective
gain; ``a`` absorbs additive (detector/readout) noise.

SINGLE-SPECTRUM FALLBACK: robust MAD of the second difference (the
``max_entropy`` method's estimator, factored here) — a GLOBAL σ, biased
upward near sharp peaks; flagged accordingly.

Everything returns a NoiseModel carrying its diagnostics and honesty
flags; nothing here silently replaces the engine's default weights —
consumers OPT IN by passing ``model.weights(y)`` through the existing
``weights=`` seam of every PeakFitMethod.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

# ── tunables (UNVERIFIED, spec §9: overridable, echoed in diagnostics) ──
N_BINS = 12                # intensity bins for the DIAGNOSTIC summary
MIN_PAIR_POINTS = 50       # refuse pairs shorter than this
DRIFT_DOMINANT_FRACTION = 0.5   # flag when drift removed > this fraction
                                # of the raw pair-difference variance
# local detrend window (points): pair differences are additionally
# high-passed with a moving average of this length, removing residual
# SMOOTH drift the global shift/scale regression cannot (measured on the
# real replicate groups: 71-98% of pair variance is drift).  White noise
# passes the high-pass with the EXACT factor (1 - 1/k), which the variance
# samples are corrected by — no bias for iid noise, slight noise UNDER-
# counting only for noise correlated on scales ≥ k points.
LOCAL_DETREND_POINTS = 31


@dataclass
class NoiseModel:
    """σ(I) model + full estimation diagnostics."""
    kind: str                       # 'replicate_difference' | 'second_difference'
    a: float                        # additive variance term (counts²)
    b: float                        # multiplicative term (variance per count)
    sigma_global: Optional[float]   # single-σ fallback value (kind 2 only)
    n_replicates: int
    n_pairs: int
    drift_fraction: float           # variance fraction removed as drift
    pair_shifts_ev: list = field(default_factory=list)
    bin_intensity: list = field(default_factory=list)
    bin_variance: list = field(default_factory=list)
    fit_residual_rel: Optional[float] = None
    flags: list = field(default_factory=list)

    def variance(self, y: np.ndarray) -> np.ndarray:
        y = np.asarray(y, dtype=float)
        if self.kind == "second_difference":
            return np.full_like(y, float(self.sigma_global) ** 2)
        return np.maximum(self.a + self.b * np.maximum(y, 0.0), 1e-12)

    def sigma(self, y: np.ndarray) -> np.ndarray:
        return np.sqrt(self.variance(y))

    def weights(self, y: np.ndarray) -> np.ndarray:
        """Drop-in for the ``weights=`` seam of every PeakFitMethod."""
        return 1.0 / self.sigma(y)

    def summary(self) -> dict:
        return {
            "kind": self.kind, "a": self.a, "b": self.b,
            "sigma_global": self.sigma_global,
            "n_replicates": self.n_replicates, "n_pairs": self.n_pairs,
            "drift_fraction": self.drift_fraction,
            "pair_shifts_ev": list(self.pair_shifts_ev),
            "fit_residual_rel": self.fit_residual_rel,
            "flags": list(self.flags),
            "tunables": {"n_bins": N_BINS,
                         "drift_dominant_fraction": DRIFT_DOMINANT_FRACTION,
                         "local_detrend_points": LOCAL_DETREND_POINTS},
        }


def estimate_noise_from_replicates(
    x: np.ndarray, scans: "list[np.ndarray]",
    n_bins: int = N_BINS,
) -> NoiseModel:
    """
    σ²(I) = a + b·I from same-grid repeat scans (≥ 2).

    Raises ValueError on mismatched grids/shapes; flags (never hides)
    drift-dominated pairs and poor regression fits.
    """
    x = np.asarray(x, dtype=float)
    ys = [np.asarray(s, dtype=float) for s in scans]
    if len(ys) < 2:
        raise ValueError("need >= 2 replicate scans")
    n = len(x)
    if any(len(s) != n for s in ys):
        raise ValueError("replicate scans must share one acquisition grid")
    if n < MIN_PAIR_POINTS:
        raise ValueError(f"replicates too short (< {MIN_PAIR_POINTS} points)")

    mean_scan = np.mean(ys, axis=0)
    grad = np.gradient(mean_scan, x)
    curv = np.gradient(grad, x)

    flags: list[str] = []
    diffs = []
    var_corrections = []
    shifts = []
    raw_var = removed_var = 0.0
    k = min(LOCAL_DETREND_POINTS, max(5, n // 4) | 1)
    kernel = np.ones(k) / k
    edge = np.convolve(np.ones(n), kernel, mode="same")
    step = float(np.median(np.abs(np.diff(x)))) or 1.0
    edge_drop = 3            # interp-clamped edge points excluded per pair
    sample_masks = []
    for a_i in range(len(ys) - 1):
        ya, yb = ys[a_i], ys[a_i + 1]
        d0 = ya - yb
        raw_var += float(np.var(d0))
        # 1) estimate the pair's relative BE shift from the Taylor leakage
        # (d ≈ Δs·y′ + …), then REGISTER the pair by interpolation — the
        # discrete-grid Taylor basis alone leaves ~50% excess variance on
        # the flanks at shifts ≈ one grid step (measured); align-then-
        # difference removes it.  Both shift signs are tried and the lower-
        # residual one kept (sidesteps gradient/差 sign conventions).
        basis = np.column_stack([grad, curv, mean_scan, np.ones(n)])
        coef, *_ = np.linalg.lstsq(basis, d0, rcond=None)
        s_hat = float(coef[0])
        d_clean = d0 - basis @ coef
        best_resid = float(np.var(d_clean))
        s_used = 0.0
        pair_var_factor = 2.0            # Var(ya − yb) = 2σ²
        if abs(s_hat) >= 1e-4 * step:
            for s_try in (s_hat, -s_hat):
                yb_al = np.interp(x, x + s_try, yb)
                c2, *_ = np.linalg.lstsq(basis, ya - yb_al, rcond=None)
                resid = ya - yb_al - basis @ c2
                if float(np.var(resid)) < best_resid:
                    best_resid = float(np.var(resid))
                    d_clean = resid
                    s_used = s_try
                    # linear-interp noise transmission: Var(yb_al) = σ²·rf
                    # with rf = (1−f)² + f², f = fractional grid offset
                    f = (abs(s_try) / step) % 1.0
                    pair_var_factor = 1.0 + (1.0 - f) ** 2 + f ** 2
        shifts.append(s_used if s_used != 0.0 else s_hat)
        # 2) local high-pass: remove residual smooth drift; white noise
        # passes with variance factor exactly (1 − 1/k)
        d_hp = d_clean - np.convolve(d_clean, kernel, mode="same") / edge
        removed_var += float(np.var(d0) - np.var(d_hp))
        diffs.append(d_hp)
        var_corrections.append(pair_var_factor * (1.0 - 1.0 / k))
        m = np.ones(n, bool)
        m[:edge_drop] = m[-edge_drop:] = False
        sample_masks.append(m)
    drift_fraction = removed_var / raw_var if raw_var > 0 else 0.0
    if drift_fraction > DRIFT_DOMINANT_FRACTION:
        flags.append(
            f"drift_dominated: {drift_fraction:.0%} of the pair-difference "
            "variance was drift — the σ(I) fit rests on the residual; "
            "treat with caution")

    # pointwise variance samples: d²/2 at the local mean intensity —
    # E[d²/2 | I] = σ²(I) exactly, so the regression runs PER POINT (any
    # binning aggregates a skewed within-bin intensity mixture and biases
    # the slope low ~10-15%, measured).  Var(d²/2) = 2σ⁴, handled by IRLS
    # weights 1/pred² (from FITTED values — weighting by the observed
    # samples correlates weights with their own noise, also biasing low).
    I = np.concatenate([mean_scan[m] for m in sample_masks])
    V = np.concatenate([(d * d / c)[m]
                        for d, c, m in zip(diffs, var_corrections,
                                           sample_masks)])
    if float(np.ptp(I)) <= 0:
        raise ValueError("not enough intensity spread for a variance fit")

    A = np.column_stack([np.ones_like(I), I])
    W = np.ones_like(V)
    coef = np.zeros(2)
    for _ in range(4):
        AtW = A.T * W
        coef = np.linalg.solve(AtW @ A, AtW @ V)
        pred_it = np.maximum(A @ coef, 1e-9)
        W = 1.0 / pred_it ** 2
    a_fit, b_fit = float(coef[0]), float(coef[1])

    # per-bin summary for DIAGNOSTICS/reporting only (equal-count bins,
    # χ²₁-median-corrected) — never used in the fit
    order = np.argsort(I)
    Is, Vs = I[order], V[order]
    edges = np.linspace(0, len(Is), n_bins + 1).astype(int)
    bi_a, bv_a = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        if hi - lo < 8:
            continue
        bi_a.append(float(np.mean(Is[lo:hi])))
        bv_a.append(float(np.median(Vs[lo:hi]) / 0.454936))
    bi_a, bv_a = np.asarray(bi_a), np.asarray(bv_a)
    if b_fit <= 0:
        flags.append("nonpositive_slope: σ² does not grow with intensity "
                     "here — additive-noise regime or estimation failure")
        b_fit = max(b_fit, 0.0)
    if a_fit < 0:
        # a small negative intercept is estimation noise; clamp + flag
        flags.append(f"negative_intercept_clamped: a={a_fit:.3g} -> 0")
        a_fit = 0.0
    pred = a_fit + b_fit * bi_a
    resid_rel = float(np.sqrt(np.mean(((bv_a - pred) / np.maximum(pred, 1e-12)) ** 2)))
    if resid_rel > 0.5:
        flags.append(f"poor_variance_fit: rel residual {resid_rel:.2f} — "
                     "σ²(I) = a + b·I may be the wrong family here")

    # (pair shifts are in eV directly: the coefficient of dy/dE)
    return NoiseModel(
        kind="replicate_difference", a=a_fit, b=b_fit, sigma_global=None,
        n_replicates=len(ys), n_pairs=len(diffs),
        drift_fraction=drift_fraction, pair_shifts_ev=shifts,
        bin_intensity=list(map(float, bi_a)), bin_variance=list(map(float, bv_a)),
        fit_residual_rel=resid_rel, flags=flags,
    )


def estimate_noise_single_spectrum(y: np.ndarray) -> NoiseModel:
    """GLOBAL σ from the MAD of the second difference (the max_entropy
    method's estimator, factored here).  Biased UPWARD near sharp peaks —
    flagged; prefer replicates whenever they exist."""
    y = np.asarray(y, dtype=float)
    if len(y) < 8:
        raise ValueError("spectrum too short")
    d2 = np.diff(y, 2)
    sigma = float(1.4826 * np.median(np.abs(d2 - np.median(d2))) / np.sqrt(6.0))
    sigma = max(sigma, 1e-12)
    return NoiseModel(
        kind="second_difference", a=0.0, b=0.0, sigma_global=sigma,
        n_replicates=1, n_pairs=0, drift_fraction=0.0,
        flags=["single_spectrum_global_sigma: biased upward near sharp "
               "peaks (curvature leaks into the second difference); "
               "UNCALIBRATED for per-point weighting — prefer "
               "estimate_noise_from_replicates when repeat scans exist"],
    )
