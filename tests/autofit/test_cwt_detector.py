"""
CWT ridge detector (`autofit.candidates`) — the ONE new detector of the
candidate-generation layer (goal: candidate-generation fix, 2026-07-10).

Detection physics: a Ricker (Mexican-hat) wavelet is a band-limited
negative-second-derivative probe; a SHOULDER — a component with NO local
maximum in the composite signal — still produces a local maximum of the CWT
coefficient row at scales near its own width.  Gating is a PROMINENCE-z
statistic: the coefficient local-max prominence normalized by the
Poisson-propagated coefficient sigma sqrt((w^2 * y)), so the gate is a pure
counting-statistics anomaly measure (baseline curvature offsets cancel in
the prominence).

ALL tunables here were calibrated on SYNTHETIC batteries only
(scripts/calibrate_cwt_detector.py); the real ds7/ds8 scans are held-out
confirmation and are never a tuning target (anti-overfit rail).

Every test is deterministic (fixed seeds).
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import _pv  # noqa: E402  (shared synthetic lineshape)

from autofit.candidates import (  # noqa: E402
    CWT_PROM_Z_MIN,
    cwt_ridge_features,
)

ETA = 0.30


def _flat_plus(x, sig, level, seed):
    rng = np.random.default_rng(seed)
    return rng.poisson(np.maximum(sig + level, 0.0)).astype(float)


def _has_local_max_near(x, y, center, half=0.45):
    d = np.diff(y)
    idx = np.where((d[:-1] > 0) & (d[1:] <= 0))[0] + 1
    return bool(np.any(np.abs(x[idx] - center) < half))


# ── shoulder-class detection (the class-defining fix) ─────────────────────

def test_detects_shoulder_without_local_max():
    """A 30%-of-main component at 0.9×FWHM separation produces NO local max
    in the composite — invisible to any local-maximum detector by
    construction — but must be found by the CWT ridge channel."""
    x = np.arange(190.0, 205.0, 0.05)
    c, f, h = 197.0, 1.2, 40000.0
    sh = c + 0.9 * f
    sig = _pv(x, h, c, f, ETA) + _pv(x, 0.3 * h, sh, f, ETA)
    assert not _has_local_max_near(x, sig, sh), \
        "case must be shoulder-class (no local max) to test the fix"
    y = _flat_plus(x, sig, 300.0, seed=100)
    feats = cwt_ridge_features(x, y)
    hits = [ft for ft in feats if abs(ft.center_be - sh) < 0.35]
    assert hits, f"shoulder at {sh} not detected; got centers " \
                 f"{[round(ft.center_be, 2) for ft in feats]}"
    assert hits[0].prom_z >= CWT_PROM_Z_MIN


def test_detects_shoulder_on_real_grid_geometry():
    """Same shoulder class on the coarse real-instrument grid geometry
    (0.1 eV step, ~191 points): scales are eV-anchored, so detection must
    not depend on the grid step."""
    x = np.arange(274.4, 293.5, 0.1)[:191]
    c, f, h = 283.0, 1.2, 40000.0
    sh = c - 0.9 * f                       # low-BE-side shoulder (ds8 class)
    sig = _pv(x, h, c, f, ETA) + _pv(x, 0.3 * h, sh, f, ETA)
    assert not _has_local_max_near(x, sig, sh)
    y = _flat_plus(x, sig, 2000.0, seed=101)
    feats = cwt_ridge_features(x, y)
    assert any(abs(ft.center_be - sh) < 0.35 for ft in feats), \
        f"low-BE shoulder missed on 0.1 eV grid; got " \
        f"{[round(ft.center_be, 2) for ft in feats]}"


def test_close_doublet_both_detected():
    """Two near-equal local maxima at 0.7×FWHM separation — the resolved-
    close-pair class the blunt 1.0 eV duplicate suppression discards —
    must both appear as ridge features."""
    x = np.arange(190.0, 205.0, 0.05)
    c1, f = 197.0, 1.2
    c2 = c1 + 0.7 * f
    sig = _pv(x, 20000.0, c1, f, ETA) + _pv(x, 16000.0, c2, f, ETA)
    y = _flat_plus(x, sig, 300.0, seed=600)
    feats = cwt_ridge_features(x, y)
    assert any(abs(ft.center_be - c1) < 0.3 for ft in feats)
    assert any(abs(ft.center_be - c2) < 0.3 for ft in feats)


# ── negative controls (deterministic seeds; statistical FP rates live in
#    the committed calibration script) ─────────────────────────────────────

def test_flat_noise_yields_no_features():
    x = np.arange(190.0, 205.0, 0.05)
    for seed in range(5):
        y = _flat_plus(x, np.zeros_like(x), 500.0, seed=1000 + seed)
        assert cwt_ridge_features(x, y) == []


def test_linear_drift_yields_no_features():
    """The Ricker kernel is exactly zero-mean and symmetric, so constant and
    linear backgrounds cancel identically — drift must produce nothing."""
    x = np.arange(190.0, 205.0, 0.05)
    for seed in range(5):
        drift = 300.0 + 40.0 * (x - x[0])
        y = _flat_plus(x, drift - 300.0, 300.0, seed=1100 + seed)
        assert cwt_ridge_features(x, y) == []


def test_single_broad_peak_no_offcenter_features():
    """A single BROAD peak (fwhm beyond the scale ladder) must not shatter
    into spurious sub-features: its plateau-top noise maxima have small
    prominence-z by construction."""
    x = np.arange(190.0, 205.0, 0.05)
    for seed in range(5):
        sig = _pv(x, 30000.0, 197.5, 3.5, ETA)
        y = _flat_plus(x, sig, 300.0, seed=2000 + seed)
        feats = cwt_ridge_features(x, y)
        off = [ft for ft in feats if abs(ft.center_be - 197.5) > 0.5]
        assert off == [], f"spurious off-center features: " \
                          f"{[round(ft.center_be, 2) for ft in off]}"


# ── invariances ────────────────────────────────────────────────────────────

def test_descending_grid_equivalence():
    """Real raw_be grids DESCEND — detection must be order-invariant
    (np.interp-class bug family)."""
    x = np.arange(190.0, 205.0, 0.05)
    c, f, h = 197.0, 1.2, 40000.0
    sh = c + 0.9 * f
    sig = _pv(x, h, c, f, ETA) + _pv(x, 0.3 * h, sh, f, ETA)
    y = _flat_plus(x, sig, 300.0, seed=100)
    asc = cwt_ridge_features(x, y)
    desc = cwt_ridge_features(x[::-1], y[::-1])
    assert len(asc) == len(desc) >= 1
    for a, d in zip(asc, desc):
        assert a.center_be == pytest.approx(d.center_be, abs=1e-9)
        assert a.prom_z == pytest.approx(d.prom_z, rel=1e-9)


def test_prom_z_scales_with_sqrt_counts():
    """prom_z is a counting-statistics z: quadrupling every count must
    roughly double the shoulder's z (ratio in [1.5, 3])."""
    x = np.arange(190.0, 205.0, 0.05)
    c, f = 197.0, 1.2
    sh = c + 1.1 * f

    def z_at(h, seed):
        sig = _pv(x, h, c, f, ETA) + _pv(x, 0.3 * h, sh, f, ETA)
        y = _flat_plus(x, sig, h / 100.0, seed=seed)
        feats = [ft for ft in cwt_ridge_features(x, y, prom_z_min=3.0)
                 if abs(ft.center_be - sh) < 0.35]
        return max(ft.prom_z for ft in feats)

    ratio = z_at(40000.0, seed=5) / z_at(10000.0, seed=5)
    assert 1.5 <= ratio <= 3.0, f"z ratio {ratio:.2f} not ~2 (sqrt scaling)"


def test_edge_features_excluded_and_no_crash():
    """Per-scale convolution edge margins: no feature may be reported inside
    the largest-scale margin, and edge-adjacent structure must not crash."""
    x = np.arange(190.0, 205.0, 0.05)
    sig = _pv(x, 30000.0, 190.3, 1.2, ETA)     # peak hard against the edge
    y = _flat_plus(x, sig, 300.0, seed=7)
    feats = cwt_ridge_features(x, y)
    for ft in feats:
        assert x[0] + 0.5 < ft.center_be < x[-1] - 0.5


def test_short_input_returns_empty():
    x = np.arange(199.0, 200.0, 0.1)
    y = np.full_like(x, 100.0)
    assert cwt_ridge_features(x, y) == []


def test_input_shorter_than_largest_kernel_no_crash():
    """A window longer than the 16-point floor but shorter than the
    largest-scale kernel (np.convolve 'same' returns the KERNEL length
    when the kernel is longer — shape mismatch crash): oversized scales
    must be skipped, not crash the layer."""
    x = np.arange(195.0, 198.0, 0.1)          # 30 points
    y = np.random.default_rng(5).poisson(
        np.full_like(x, 500.0)).astype(float)
    assert cwt_ridge_features(x, y) == []      # noise only, no features
    # and a real feature in a short window still detects or stays silent
    # without crashing
    sig = _pv(x, 20000.0, 196.5, 0.8, ETA)
    y2 = _flat_plus(x, sig, 300.0, seed=6)
    feats = cwt_ridge_features(x, y2)          # must simply not raise
    for ft in feats:
        assert x[0] < ft.center_be < x[-1]


def test_feature_fields_populated():
    """Every reported feature carries the honesty-surface fields."""
    x = np.arange(190.0, 205.0, 0.05)
    sig = _pv(x, 40000.0, 197.0, 1.2, ETA)
    y = _flat_plus(x, sig, 300.0, seed=3)
    feats = cwt_ridge_features(x, y)
    assert feats, "isolated strong peak must be detected"
    ft = max(feats, key=lambda f: f.prom_z)
    assert abs(ft.center_be - 197.0) < 0.2
    assert ft.prom_z >= CWT_PROM_Z_MIN
    assert ft.ridge_length >= 2
    assert 0.2 < ft.scale_fwhm_ev < 3.0
    assert 0.2 < ft.fwhm_est_ev < 3.0
