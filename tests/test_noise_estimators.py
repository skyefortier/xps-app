"""Unit B (design + measurement only): the candidate noise estimators' arithmetic, on noise whose variance is known.
Not used by the application; docs/findings/noise-estimator/README.md."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import noise_estimators as ne  # noqa: E402


def _flat(level, n=40000):
    return np.full(n, float(level))


@pytest.mark.parametrize("t", [0.1, 1.0, 10.0])
@pytest.mark.parametrize("name", ["scaled_d1", "scaled_d2", "scaled_d4", "flat_ends"])
def test_a_scaled_poisson_level_is_recovered_on_a_flat_spectrum(name, t):
    """counts / t has variance k·y with k = 1/t: every scaled estimator recovers k on a flat signal (4 %; the sampling error at n = 40 000 is ~1.5 %)."""
    rng = np.random.default_rng(1)
    y = rng.poisson(_flat(5000) * t) / t
    assert ne.ESTIMATORS[name](y).k == pytest.approx(1 / t, rel=0.04)


def test_the_regression_separates_a_constant_term_from_shot_noise():
    rng = np.random.default_rng(2)
    s = np.linspace(1000, 20000, 6000)
    y = rng.poisson(s) + rng.normal(0, 60.0, s.size)
    m = ne.variance_mean_regression(y)
    assert m.k == pytest.approx(1.0, rel=0.1) and m.a == pytest.approx(3600.0, rel=0.35)


def test_the_constant_estimator_recovers_gaussian_noise():
    rng = np.random.default_rng(3)
    y = 1000.0 + rng.normal(0, 7.0, 5000)
    assert ne.constant_second_difference(y).a == pytest.approx(49.0, rel=0.05)


def test_the_white_noise_correlation_of_each_difference_filter():
    assert ne.WHITE_RHO1[1] == pytest.approx(-0.5) and ne.WHITE_RHO1[2] == pytest.approx(-2 / 3) and ne.WHITE_RHO1[4] == pytest.approx(-0.8)
    rng = np.random.default_rng(4)
    d = ne.correlation_diagnostics(rng.poisson(_flat(4000)).astype(float))
    assert d["rho1_d1"] == pytest.approx(-0.5, abs=0.04) and d["rho1_d4"] == pytest.approx(-0.8, abs=0.04)
    assert all(v == pytest.approx(1.0, abs=0.08) for v in d["lag_profile"])


def test_smoothing_hides_noise_from_differences_and_shows_in_the_lag_profile():
    """The failure the findings report: a 5-point moving average divides the second-difference k by ~10 while the
    true variance falls only 5-fold; the lag profile rises from lag 1."""
    rng = np.random.default_rng(5)
    raw = rng.poisson(_flat(4000, 8000)).astype(float)
    y = np.convolve(raw, np.ones(5) / 5, mode="valid")
    assert ne.scaled_poisson_differences(y, 2).k < 0.5 * (1 / 5)
    assert ne.correlation_diagnostics(y)["lag_profile"][1] > 1.5          # independent noise: ≈ 1.0


def test_the_reduced_chi2_definition():
    r = np.array([1.0, -2.0, 2.0, 0.0])
    assert ne.reduced_chi2(r, np.full(4, 2.0), 1) == pytest.approx((1 + 4 + 4) / 2 / 3)
