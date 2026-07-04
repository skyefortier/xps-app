"""
Empirical noise model (autofit/noise.py) — ground-truth validation.

The canonical 1/sqrt(counts) weights are correct ONLY for raw counts; the
replicate-difference estimator must recover the true σ²(I) = a + b·I on
synthetic ground truth (pure Poisson b=1; gain-scaled b=g; additive floor
a=s²), remove BE-shift drift honestly (recovering the injected shifts),
and expose its own failure modes as flags rather than silence.
"""

import numpy as np
import pytest

from autofit.methods.base import poisson_like_weights
from autofit.noise import (
    estimate_noise_from_replicates,
    estimate_noise_single_spectrum,
)

X = np.arange(190.0, 205.0, 0.05)


def _truth(height=50000.0):
    g = np.exp(-4 * np.log(2) * ((X - 197.5) / 1.4) ** 2)
    return 400.0 + height * g


def _poisson_reps(n, seed, gain=1.0, floor_sigma=0.0, height=50000.0):
    rng = np.random.default_rng(seed)
    I = _truth(height)
    reps = []
    for _ in range(n):
        y = gain * rng.poisson(I / gain)
        if floor_sigma:
            y = y + rng.normal(0.0, floor_sigma, len(X))
        reps.append(y.astype(float))
    return reps


def test_pure_poisson_recovers_unit_slope():
    m = estimate_noise_from_replicates(X, _poisson_reps(8, seed=1))
    assert m.kind == "replicate_difference"
    assert m.b == pytest.approx(1.0, rel=0.15)
    # additive term small relative to the baseline variance (~400)
    assert m.a < 0.2 * 400.0
    assert not [f for f in m.flags if f.startswith("drift_dominated")]


@pytest.mark.parametrize("gain", [0.25, 4.0])
def test_gain_scaled_counts_recover_gain(gain):
    """Rate-like exports: y = g·Poisson(I/g) has σ² = g·I — exactly the
    case where 1/sqrt(y) is wrong by a factor sqrt(g).  Measured estimator
    spread at n=8 replicates: single draws wobble up to ~20% at gain 4
    (χ²₁-noise on the sparse peak-top samples), unbiased across draws — so
    the pin is median-of-3-seeds tight + each single draw loose."""
    bs = [estimate_noise_from_replicates(
              X, _poisson_reps(8, seed=s, gain=gain)).b
          for s in (2, 12, 22)]
    assert float(np.median(bs)) == pytest.approx(gain, rel=0.15)
    for b in bs:
        assert b == pytest.approx(gain, rel=0.3)


def test_additive_floor_recovered():
    s = 60.0
    m = estimate_noise_from_replicates(
        X, _poisson_reps(8, seed=3, floor_sigma=s))
    assert m.b == pytest.approx(1.0, rel=0.25)
    assert m.a == pytest.approx(s * s, rel=0.5)


def test_weights_correct_where_poisson_like_is_wrong():
    """At gain 4, poisson_like_weights over-weights every point by ~2×;
    the empirical model's weights are right (ratio ≈ sqrt(gain))."""
    gain = 4.0
    reps = _poisson_reps(8, seed=4, gain=gain)
    m = estimate_noise_from_replicates(X, reps)
    y = reps[0]
    hi = _truth() > 10000.0          # peak region, far from the 1-count clamp
    ratio = poisson_like_weights(y)[hi] / m.weights(y)[hi]
    assert np.median(ratio) == pytest.approx(np.sqrt(gain), rel=0.2)


def test_shift_drift_removed_and_recovered():
    """Replicates whose truth is BE-shifted (charging drift): the gradient
    regression must recover each pair's relative shift and the slope must
    stay ≈1 (drift not counted as noise)."""
    rng = np.random.default_rng(5)
    shifts = [0.00, 0.03, -0.02, 0.05]   # eV, one per scan
    reps = []
    for s in shifts:
        I = 400.0 + 50000.0 * np.exp(-4 * np.log(2) * ((X - 197.5 - s) / 1.4) ** 2)
        reps.append(rng.poisson(I).astype(float))
    m = estimate_noise_from_replicates(X, reps)
    assert m.b == pytest.approx(1.0, rel=0.25)
    # pair shifts: y_a − y_b leaks (s_a − s_b)·dy/dE; sign convention aside,
    # magnitudes must match the injected pair deltas
    truth_pair = [abs(shifts[i] - shifts[i + 1]) for i in range(3)]
    got_pair = [abs(v) for v in m.pair_shifts_ev]
    assert got_pair == pytest.approx(truth_pair, abs=0.01)


def test_drift_dominated_flag_fires():
    """Huge shift + tiny counting noise: most pair variance is drift — the
    estimator must SAY so."""
    rng = np.random.default_rng(6)
    reps = []
    for s in (0.0, 0.5):                 # half-eV lurch between scans
        I = 400.0 + 50000.0 * np.exp(-4 * np.log(2) * ((X - 197.5 - s) / 1.4) ** 2)
        reps.append(rng.poisson(I).astype(float))
    m = estimate_noise_from_replicates(X, reps)
    assert any(f.startswith("drift_dominated") for f in m.flags)


def test_monte_carlo_centering_small_and_large_shifts():
    """Codex noise-review demand: predeclared-seed Monte Carlo centering
    of the slope under realistic drift.  Measured 2026-07-04 (seeds 1-10,
    n=8 replicates at 50k counts): small shifts (0.02-0.06 eV) median
    1.033; large shifts (0.25-0.30 eV — interp-clamp + Newton-refinement
    territory) median 0.954.  The residual +3-7% pure-case finite-sample
    IRLS bias is documented in the module docstring and shrinks with
    replicate count (16 reps → +2.9%)."""
    cases = (
        ("small", [0.00, 0.03, -0.02, 0.05, 0.01, -0.04, 0.02, 0.06],
         0.95, 1.12, 0.8, 1.3, None),
        # multi-grid-step shifts: σ²(I) assignment from the ensemble mean
        # UNDERSTATES b there (measured median 0.82) — the estimator must
        # SAY so (intensity_assignment_degraded), never a clean number
        ("large", [0.0, 0.30, -0.25, 0.30, 0.05, -0.30], 0.72, 1.05,
         0.5, 1.3, "intensity_assignment_degraded"),
    )
    for label, shift_set, lo, hi, slo, shi, req_flag in cases:
        bs, flags = [], set()
        for seed in range(1, 11):
            rng = np.random.default_rng(seed)
            reps = [rng.poisson(
                        400.0 + 50000.0 * np.exp(
                            -4 * np.log(2) * ((X - 197.5 - s) / 1.4) ** 2)
                    ).astype(float) for s in shift_set]
            m = estimate_noise_from_replicates(X, reps)
            bs.append(m.b)
            flags |= {f.split(":")[0] for f in m.flags}
        med = float(np.median(bs))
        assert lo <= med <= hi, (label, med, bs)
        assert all(slo <= b <= shi for b in bs), (label, bs)
        if req_flag:
            assert req_flag in flags, (label, flags)
        else:
            assert "intensity_assignment_degraded" not in flags, (label, flags)


def test_transmission_is_covariance_exact_pointwise():
    """Matrix-level pin (Codex re-check demand): for a KNOWN white noise σ
    and a fixed fractional registration shift, the implemented per-point
    predictor u must satisfy E[r²]ᵢ = σ²·uᵢ INCLUDING the interpolation
    covariance (a diagonal-only correction fails this by ~f(1−f) terms).
    Verified against 3000 Monte Carlo draws through the exact operator."""
    from autofit.noise import LOCAL_DETREND_POINTS
    n = 120
    x = np.linspace(0.0, 10.0, n)
    mean_scan = np.full(n, 100.0)
    grad = np.gradient(mean_scan, x)
    curv = np.gradient(grad, x)
    basis = np.column_stack([grad, curv, mean_scan, np.ones(n)])
    Q, _ = np.linalg.qr(basis)
    H = Q @ Q.T
    k = min(LOCAL_DETREND_POINTS, max(5, n // 4) | 1)
    half = k // 2
    S = np.zeros((n, n))
    for i in range(n):
        lo_i, hi_i = max(0, i - half), min(n, i + half + 1)
        S[i, lo_i:hi_i] = 1.0 / (hi_i - lo_i)
    T = (np.eye(n) - S) @ (np.eye(n) - H)
    step = x[1] - x[0]
    s = 1.5004 * step                      # deliberately fractional
    P = np.zeros((n, n))
    src = x + s
    for i in range(n):
        q = x[i]
        if q <= src[0]:
            P[i, 0] = 1.0
        elif q >= src[-1]:
            P[i, -1] = 1.0
        else:
            j = int(np.searchsorted(src, q)) - 1
            f = (q - src[j]) / (src[j + 1] - src[j])
            P[i, j], P[i, j + 1] = 1.0 - f, f
    Gp = T @ P
    u = (T * T) @ np.ones(n) + (Gp * Gp) @ np.ones(n)
    sig = 3.0
    acc = np.zeros(n)
    n_draws = 3000
    for t in range(n_draws):
        ra = np.random.default_rng(t).normal(0, sig, n)
        rb = np.random.default_rng(50000 + t).normal(0, sig, n)
        r = T @ (ra - P @ rb)
        acc += r * r
    ratio = (acc / n_draws) / (sig * sig * u)
    interior = slice(20, n - 20)
    assert float(np.mean(ratio[interior])) == pytest.approx(1.0, abs=0.02)
    assert float(np.max(np.abs(ratio[interior] - 1.0))) < 0.10


def test_descending_grid_equivalence():
    """Real XPS BE grids are DESCENDING; np.interp silently breaks on a
    descending source grid (Codex re-check blocker — the first real-data
    survey's registration was invalid because of this).  The estimator
    must reverse internally: identical a/b either way."""
    rng = np.random.default_rng(3)
    reps = [rng.poisson(400.0 + 50000.0 * np.exp(
                -4 * np.log(2) * ((X - 197.5 - s) / 1.4) ** 2)
            ).astype(float) for s in (0.0, 0.05, -0.03, 0.04)]
    m_asc = estimate_noise_from_replicates(X, reps)
    m_desc = estimate_noise_from_replicates(
        X[::-1].copy(), [r[::-1].copy() for r in reps])
    assert m_desc.b == pytest.approx(m_asc.b, rel=1e-9)
    assert m_desc.a == pytest.approx(m_asc.a, abs=1e-6)


def test_input_validation():
    with pytest.raises(ValueError, match=">= 2 replicate"):
        estimate_noise_from_replicates(X, [_truth()])
    with pytest.raises(ValueError, match="share one acquisition grid"):
        estimate_noise_from_replicates(X, [_truth(), _truth()[:-1]])
    with pytest.raises(ValueError, match="too short"):
        estimate_noise_from_replicates(X[:10], [X[:10] * 0 + 1, X[:10] * 0 + 2])


def test_single_spectrum_fallback_flagged():
    rng = np.random.default_rng(7)
    y = 500.0 + rng.normal(0, 20.0, 400)
    m = estimate_noise_single_spectrum(y)
    assert m.kind == "second_difference"
    assert m.sigma_global == pytest.approx(20.0, rel=0.2)
    assert any("single_spectrum" in f for f in m.flags)
    assert np.allclose(m.weights(y), 1.0 / m.sigma_global)


def test_real_replicates_smoke():
    """The labeled set's real repeat scans (B4C U 4f, n=10, one shared raw
    grid): the estimator must run, produce a positive slope, and report
    drift honestly.  The measured values are EVIDENCE (logged in
    PROGRESS/report), not pinned physics."""
    import os
    from autofit.reference import load_reference_fits
    path = os.path.join(os.path.dirname(__file__), "..", "..",
                        "docs", "autofit", "test_data", "B4C-UCl4.proj.zip")
    fits = [rf for rf in load_reference_fits(path) if rf.name.startswith("U4f")]
    assert len(fits) >= 3
    x = fits[0].raw_be
    m = estimate_noise_from_replicates(x, [rf.raw_intensity for rf in fits])
    assert m.b > 0
    assert 0.0 <= m.drift_fraction <= 1.0
    assert m.n_pairs == len(fits) - 1
    s = m.summary()
    assert s["kind"] == "replicate_difference" and "tunables" in s
