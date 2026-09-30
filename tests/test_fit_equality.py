"""The same-fit comparison (tests/fit_equality.py) accepts two presses of one
request and REJECTS a fit that landed in a different minimum (owner condition,
unit A2, 2026-09-29: the rewritten reproducibility tests must still fail if a
fit lands in a different minimum)."""
import copy

import pytest

import fitting
from fit_equality import SAME_MINIMUM_REL, assert_same_fit
import test_fit_reproducibility as R
import test_scattered_starts as SS


def test_the_tolerance_is_the_certificates_own_scale():
    assert SAME_MINIMUM_REL == pytest.approx(10 * fitting.CERTIFY_FTOL ** 0.5)


def test_two_presses_of_one_request_are_the_same_fit():
    x, y, specs = R._crowded_c1s()
    kw = dict(background_method="shirley", n_perturb=3, n_starts=3, fit_kws={"method": "leastsq"})
    assert_same_fit(fitting.run_fit(x, y, specs, **kw), fitting.run_fit(x, y, specs, **kw))


def _from_alternative(specs, alt):
    out = copy.deepcopy(specs)
    for spec, comp in zip(out, alt["components"]):
        assert str(spec["id"]) == str(comp["id"])
        for k, v in comp["params"].items():
            if k in spec or k in ("center", "amplitude", "fwhm"):
                spec[k] = v
    return out


def test_a_fit_that_lands_in_a_different_minimum_is_not_the_same_fit():
    # The scattered-starts two-basin model: the student's fit is a genuine (poor)
    # minimum; one scattered start finds another. Fitting again FROM that
    # solution with the same method returns that other minimum — which the
    # comparison must reject, component curves, areas and chi-square alike.
    x, y, specs = SS._two_basin_problem()
    fit = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    alt = fit["starts"]["alternatives"][0]
    other = fitting.run_fit(x, y, _from_alternative(specs, alt), n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    assert other["statistics"]["reduced_chi_square"] == pytest.approx(alt["chi2r"], rel=1e-3)
    with pytest.raises(AssertionError, match="not the same fit"):
        assert_same_fit(fit, other)


def test_the_nearest_distinct_minima_of_the_crowded_model_are_told_apart():
    # Five overlapping components: Levenberg-Marquardt and Trust-Region stop in
    # different certified minima (chi2r 1.324 vs 1.444); the comparison sees it
    # even with the method-dependent message ignored.
    x, y, specs = R._crowded_c1s()
    kw = dict(background_method="shirley", n_perturb=3)
    lm = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **kw)
    tr = fitting.run_fit(x, y, specs, fit_kws={"method": "least_squares"}, **kw)
    assert lm["certificate"]["certified"] and tr["certificate"]["certified"]
    with pytest.raises(AssertionError, match="not the same fit"):
        assert_same_fit(lm, tr)


def test_a_centre_moved_by_a_tenth_of_an_electronvolt_is_caught():
    # the smallest move the scattered-starts check calls a different solution
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    b = copy.deepcopy(a)
    b["individual_peaks"][0]["params"]["center"]["value"] += 0.1
    with pytest.raises(AssertionError, match="center"):
        assert_same_fit(a, b)
