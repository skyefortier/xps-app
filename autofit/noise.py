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
acquisition grid (the labeled projects carry n=3–10 such replicates;
descending BE grids are reversed internally — np.interp silently breaks on
them otherwise).  For each adjacent scan pair the difference d = y_a − y_b
cancels the static signal exactly; two honest corrections remain:

- SHIFT DRIFT: each scan charge-references slightly differently (measured
  ccShift spreads ~0.01–0.06 eV), so the true spectra are BE-shifted and
  d leaks the signal derivative: d ≈ ΔBE·(dy/dE) + noise.  We regress the
  gradient of the ensemble-mean spectrum out of each pair difference (the
  fitted coefficient IS the pair's relative shift — reported, and
  cross-checkable against the saved ccShift differences).
- SCALE DRIFT: source-intensity drift between scans scales the signal;
  we regress out the mean-spectrum component as well.

The drift removal + high-pass form an explicit linear operator T, and the
fit uses the COVARIANCE-EXACT per-point transmission through T and the
interpolation matrix P:  E[r_i²] = a·u_i + b·w_i with
u = (T² + (TP)²)·1 and w = (T² + (TP)²)·I  (see ``_transmission_uw`` —
the only documented estimator form; any scalar/diagonal interpolation
factor is the rejected approximation, since linear interpolation gives
adjacent aligned samples covariance f(1−f)σ² that no diagonal can carry).
σ²(I)=a+b·I is fitted per point by IRLS with prediction-based weights
(per-bin aggregation and observed-value weighting each bias the slope low
~10-15% — measured; documented at the fit).  For raw counts the truth is (a=0,
b=1); for a rate/gain-scaled export b recovers the effective gain; ``a``
absorbs additive (detector/readout) noise.  Known second-order residuals
(finite-sample IRLS, clamped-edge leakage through the global hat matrix
at O(edge/n), 1/k-suppressed registration-sign selection) are documented
at the implementation.

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


def _interp_matrix(x: np.ndarray, shift: float) -> np.ndarray:
    """P with (P @ yb) ≡ np.interp(x, x + shift, yb) — built by
    searchsorted (non-uniform-grid safe, clamped edges).  Module-level so
    the transmission pin tests exercise the PRODUCTION operator."""
    n = len(x)
    P = np.zeros((n, n))
    src = x + shift
    for i in range(n):
        q = x[i]
        if q <= src[0]:
            P[i, 0] = 1.0
        elif q >= src[-1]:
            P[i, -1] = 1.0
        else:
            j = int(np.searchsorted(src, q)) - 1
            f_ij = (q - src[j]) / (src[j + 1] - src[j])
            P[i, j] = 1.0 - f_ij
            P[i, j + 1] = f_ij
    return P


def _residual_operator(x: np.ndarray, mean_scan: np.ndarray,
                       k: int) -> tuple:
    """(T, S, basis): the estimator's residual-maker T = (I − S)(I − H)
    with H the drift-basis hat matrix and S the edge-normalized moving-
    average smoother.  Module-level so the pin tests exercise the
    PRODUCTION operator."""
    n = len(x)
    grad = np.gradient(mean_scan, x)
    curv = np.gradient(grad, x)
    basis = np.column_stack([grad, curv, mean_scan, np.ones(n)])
    Q, _ = np.linalg.qr(basis)
    H = Q @ Q.T
    half = k // 2
    S = np.zeros((n, n))
    for i in range(n):
        lo, hi = max(0, i - half), min(n, i + half + 1)
        S[i, lo:hi] = 1.0 / (hi - lo)
    T = (np.eye(n) - S) @ (np.eye(n) - H)
    return T, S, basis


def _transmission_uw(T: np.ndarray, P: "np.ndarray | None",
                     intensity: np.ndarray) -> tuple:
    """The covariance-exact per-point transmission of d = ya − P·yb through
    the residual-maker T, for diagonal per-scan covariances σ²(I):

        E[r_i²] = a·u_i + b·w_i,
        u = (T² + (TP)²) · 1,   w = (T² + (TP)²) · I     (² elementwise)

    P=None means the unaligned pair (P = identity).  This is the ONLY
    documented estimator form — the scalar/diagonal interpolation factor
    (1−f)²+f² is the REJECTED round-2 approximation (it cannot carry the
    adjacent-sample covariance linear interpolation creates)."""
    G2 = T * T
    Gp2 = G2 if P is None else (T @ P) * (T @ P)
    both = G2 + Gp2
    return both @ np.ones(len(intensity)), both @ intensity


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
    dx = np.diff(x)
    if np.all(dx < 0):
        # real XPS BE grids are often DESCENDING; np.interp silently
        # returns garbage on a descending source grid (Codex re-check
        # blocker — the first survey's registration was invalid on real
        # data because of this).  Reverse internally; a/b are
        # order-independent, pair shifts flip sign (reported in the
        # reversed = ascending frame).
        x = x[::-1].copy()
        ys = [s[::-1].copy() for s in ys]
    elif not np.all(dx > 0):
        raise ValueError("x must be strictly monotonic")

    mean_scan = np.mean(ys, axis=0)

    flags: list[str] = []
    shifts = []
    raw_var = removed_var = 0.0
    k = min(LOCAL_DETREND_POINTS, max(5, n // 4) | 1)
    half = k // 2
    step = float(np.median(np.abs(np.diff(x)))) or 1.0

    # The full residual-maker as an EXPLICIT operator (Codex noise-review
    # blocker: scalar corrections are wrong after the drift-regression /
    # high-pass stack — leverage and filter-edge transmission are point-
    # dependent).  r = T d with T = (I − S)(I − H):
    #   H = hat matrix of the drift basis [y′, y″, mean, 1]
    #   S = edge-normalized moving-average smoother (row i averages its
    #       clipped window: weights 1/(hi−lo))
    # For diagonal input covariance Var(d_j) = c_j σ²(I_j), the response is
    # EXACT per point:  E[r_i²] = a·Σ_j T_ij² c_j + b·Σ_j T_ij² c_j I_j —
    # so the fit regresses r² on the T²-transformed design (u, w).
    T, S, basis = _residual_operator(x, mean_scan, k)

    # Registration transmission is COVARIANCE-EXACT (Codex re-check
    # blocker: linear interpolation gives adjacent aligned samples the
    # covariance f(1−f)σ² — no diagonal factor can represent that;
    # a diagonal approximation was the REJECTED round-2 design): with
    # d = ya − P yb (P = the interpolation matrix), Σ_d = D_a + P D_b Pᵀ,
    # so with the module-level helpers (shared with the pin tests so the
    # PRODUCTION path is what gets tested),
    #   E[r_i²] = a·u_i + b·w_i,  (u, w) from _transmission_operators.
    # Remaining KNOWN second-order effects, accepted and documented rather
    # than silently absorbed: (a) IRLS with fitted weights is consistent,
    # not finite-sample unbiased; (b) interp-CLAMPED edge points are
    # excluded by mask, but the global hat matrix lets them perturb the 4
    # regression coefficients at O(edge_points/n); (c) the registration
    # sign/refinement selects among a handful of candidates using the
    # residual-shift coefficient — a near-deterministic statistic.
    r2_l, u_l, w_l, Ie_l = [], [], [], []
    for a_i in range(len(ys) - 1):
        ya, yb = ys[a_i], ys[a_i + 1]
        d0 = ya - yb
        raw_var += float(np.var(d0))
        coef, *_ = np.linalg.lstsq(basis, d0, rcond=None)
        s_hat = float(coef[0])

        # registration: try both shift signs; judge by the RESIDUAL SHIFT
        # COEFFICIENT after alignment — the correct sign leaves ~0 (the
        # coefficient's own standard error, ~0.001 eV here) while the wrong
        # sign leaves ≈ 2ŝ.  (A smoothed-residual-variance criterion was
        # tried first and is TOO WEAK at small shifts: the wrong-sign
        # leakage power is comparable to the smoothed noise floor σ²/k, so
        # pairs mis-selected — measured, hence this discriminator.)
        d_chosen, s_used = d0, 0.0
        best_residual_shift = abs(s_hat)
        if abs(s_hat) >= 1e-4 * step:
            for s_try in (s_hat, -s_hat):
                yb_al = np.interp(x, x + s_try, yb)
                d_al = ya - yb_al
                c2, *_ = np.linalg.lstsq(basis, d_al, rcond=None)
                if abs(float(c2[0])) < best_residual_shift:
                    best_residual_shift = abs(float(c2[0]))
                    d_chosen, s_used = d_al, s_try
        # Newton refinement: at shifts ≳ 4 grid steps the first-order ŝ
        # biases low (Taylor validity), leaving flank leakage that over-
        # counts b ~20% (measured) — re-estimate the residual shift from
        # the aligned difference and re-align until it vanishes (sign
        # resolved by trial, as above)
        if s_used != 0.0:
            for _ in range(3):
                cr, *_ = np.linalg.lstsq(basis, d_chosen, rcond=None)
                delta = float(cr[0])
                if abs(delta) < 1e-3 * step:
                    break
                improved = False
                for s_new in (s_used + delta, s_used - delta):
                    yb_al = np.interp(x, x + s_new, yb)
                    c3, *_ = np.linalg.lstsq(basis, ya - yb_al, rcond=None)
                    if abs(float(c3[0])) < abs(delta):
                        s_used, d_chosen = s_new, ya - yb_al
                        improved = True
                        break
                if not improved:
                    break
        shifts.append(s_used if s_used != 0.0 else s_hat)

        r = T @ d_chosen
        removed_var += float(np.var(d0) - np.var(r))
        # covariance-exact transmission (see the operator note above).
        # σ²(I) is assigned from the ENSEMBLE MEAN intensity: per-scan
        # (smoothed) intensities were tried and are WRONG — they share
        # noise with the response r², and that regressor-response
        # correlation collapses the slope (measured b→0.38 on pure
        # Poisson).  The mean-assignment residual error is flank
        # misassignment at multi-grid-step shifts (measured: b
        # understates ~18% at 6-step / 0.3 eV shifts) — flagged below
        # rather than silently absorbed.
        P = _interp_matrix(x, s_used) if s_used != 0.0 else None
        u, w = _transmission_uw(T, P, mean_scan)
        if abs(s_used) > 2.0 * step and not any(
                f.startswith("intensity_assignment_degraded") for f in flags):
            flags.append(
                "intensity_assignment_degraded: pair shifts exceed ~2 grid "
                "steps — σ²(I) is assigned from the ensemble mean, which "
                "misassigns flank variance there (measured: b understates "
                "~18% at 6-step shifts); treat b as a lower bound")
        # mask: interp-clamped points (np.interp holds edge values beyond
        # the shifted support) contaminate every T row whose smoother
        # window touches them — exclude ceil(|s|/step)+1 edge points plus
        # the half-window on each side (Codex noise review: edge_drop=3
        # was insufficient for the survey's ~0.3 eV shifts)
        edge_excl = (int(np.ceil(abs(s_used) / step)) + 1 if s_used else 1)
        drop = edge_excl + half
        if drop > n // 4 or 2 * drop >= n - 8:
            # refusing beats silent under-masking (Codex re-check): a shift
            # this large relative to the window is not a registration case
            flags.append(f"pair_excluded: |shift|={abs(s_used):.3g} eV "
                         "needs an edge mask wider than n/4 — pair dropped")
            continue
        m = np.ones(n, bool)
        m[:drop] = m[-drop:] = False
        r2_l.append((r * r)[m]); u_l.append(u[m]); w_l.append(w[m])
        Ie_l.append(mean_scan[m])
    drift_fraction = removed_var / raw_var if raw_var > 0 else 0.0
    if drift_fraction > DRIFT_DOMINANT_FRACTION:
        flags.append(
            f"drift_dominated: {drift_fraction:.0%} of the pair-difference "
            "variance was drift — the σ(I) fit rests on the residual; "
            "treat with caution")

    if sum(len(r) for r in r2_l) < 24:      # < ~12 samples per fitted param
        # refusal must carry its own diagnostics, not a generic
        # concatenate error or a NaN "fit" (Codex round-3 major)
        raise ValueError(
            "too few variance samples after pair exclusion/masking: "
            + ("; ".join(f for f in flags if f.startswith("pair_excluded"))
               or f"{sum(len(r) for r in r2_l)} samples"))
    R2 = np.concatenate(r2_l)
    U = np.concatenate(u_l)
    Wd = np.concatenate(w_l)
    I = np.concatenate(Ie_l)
    if float(np.ptp(I)) <= 0:
        raise ValueError("not enough intensity spread for a variance fit")

    # IRLS fit of E[r²] = a·u + b·w.  Var(r²) ≈ 2·E[r²]² (χ²₁-like), so
    # weights come from FITTED values — weighting by the observed samples
    # correlates weights with their own noise and biases the slope low
    # ~10-15% (measured; same reason per-bin aggregation was dropped).
    M = np.column_stack([U, Wd])
    Wt = np.ones_like(R2)
    coef = np.zeros(2)
    for _ in range(4):
        MtW = M.T * Wt
        coef = np.linalg.solve(MtW @ M, MtW @ R2)
        pred_it = np.maximum(M @ coef, 1e-9)
        Wt = 1.0 / pred_it ** 2
    a_fit, b_fit = float(coef[0]), float(coef[1])

    # per-bin summary for DIAGNOSTICS/reporting only: bins of effective
    # intensity I_eff = w/u vs implied variance r²/u (χ²₁-median-corrected
    # medians) — never used in the fit
    I_eff = Wd / np.maximum(U, 1e-12)
    V_imp = R2 / np.maximum(U, 1e-12)
    order = np.argsort(I_eff)
    Is, Vs = I_eff[order], V_imp[order]
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
    if len(bi_a) == 0:
        # too few samples for even one diagnostic bin — the FIT above ran
        # on the per-point samples; only the summary is unavailable
        flags.append("no_diagnostic_bins: too few samples for the binned "
                     "summary (fit used the per-point samples)")
        resid_rel = None
        bi_a = bv_a = np.asarray([])
        pred = np.asarray([])
    else:
        pred = a_fit + b_fit * bi_a
        resid_rel = float(np.sqrt(np.mean(
            ((bv_a - pred) / np.maximum(pred, 1e-12)) ** 2)))
    if resid_rel is not None and resid_rel > 0.5:
        flags.append(f"poor_variance_fit: rel residual {resid_rel:.2f} — "
                     "σ²(I) = a + b·I may be the wrong family here")

    # (pair shifts are in eV directly: the coefficient of dy/dE)
    return NoiseModel(
        kind="replicate_difference", a=a_fit, b=b_fit, sigma_global=None,
        n_replicates=len(ys), n_pairs=len(r2_l),
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
