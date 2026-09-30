"""The same-fit comparison (tests/fit_equality.py) accepts two presses of one
request and REJECTS a fit that landed in a different minimum (owner condition,
unit A2, 2026-09-29: the rewritten reproducibility tests must still fail if a
fit lands in a different minimum). Codex A2 round 1: the proofs pin one seed,
so a rejection can only come from the fitted quantities, and they include a
small component beside a dominant one."""
import copy

import numpy as np
import pytest

import fitting
from fit_equality import OBJECTIVE_REL, SAME_MINIMUM_REL, assert_same_fit
import test_fit_reproducibility as R
import test_scattered_starts as SS

SEED = {"seed": 123}


def _rejects(a, b, *fields):
    assert a["random_seed"] == b["random_seed"]            # the seed cannot be what differs
    with pytest.raises(AssertionError, match="not the same fit") as e:
        assert_same_fit(a, b)
    msg = str(e.value)
    assert "random_seed" not in msg
    for f in fields:
        assert f in msg, msg


def test_the_tolerances_are_the_certificates_own_scales():
    assert SAME_MINIMUM_REL == pytest.approx(10 * fitting.CERTIFY_FTOL ** 0.5)
    assert OBJECTIVE_REL == pytest.approx(10 * fitting.CERTIFY_FTOL)


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
    # solution, same method, same seed, returns that other minimum.
    x, y, specs = SS._two_basin_problem()
    fit = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    alt = fit["starts"]["alternatives"][0]
    # the same seed for the second fit: only the fitted quantities can differ
    kw = dict(n_starts=6, fit_kws={"method": "leastsq", "fit_kws": {"seed": fit["random_seed"]}}, **SS.KW)
    other = fitting.run_fit(x, y, _from_alternative(specs, alt), **kw)
    assert other["statistics"]["reduced_chi_square"] == pytest.approx(alt["chi2r"], rel=1e-3)
    _rejects(fit, other, "reduced_chi_square", "individual_peaks")


def test_the_nearest_distinct_minima_of_the_crowded_model_are_told_apart():
    # Levenberg-Marquardt and Trust-Region stop in different certified minima
    # (chi2r 1.324 vs 1.444); the seed pinned, the method-dependent message ignored.
    x, y, specs = R._crowded_c1s()
    lm = fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq", "fit_kws": SEED})
    tr = fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3, fit_kws={"method": "least_squares", "fit_kws": SEED})
    assert lm["certificate"]["certified"] and tr["certificate"]["certified"]
    _rejects(lm, tr, "reduced_chi_square")


def _small_beside_dominant(centre):
    # Codex A2 round 1 (run A): a held dominant line and a small one (1/2000 of
    # its height, 0.3 eV wide) in its tail, where two equal true lines 1 eV apart
    # give the small component two certified minima. On the whole signal's scale
    # (1e6 counts) the two fits look alike; on the component's own scale not.
    x = np.linspace(-500.0, 500.0, 20001)
    rng = np.random.default_rng(7)
    g = lambda c, a, w: a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
    y = rng.poisson(g(0.0, 1e6, 300.0) + g(399.5, 500, 0.3) + g(400.5, 500, 0.3) + 50).astype(float)
    specs = [{"id": 1, "shape": "gaussian", "center": 0.0, "amplitude": 1e6, "fwhm": 300.0, "fix_center": True, "fix_amplitude": True, "fix_fwhm": True},
             {"id": 2, "shape": "gaussian", "center": centre, "amplitude": 400.0, "fwhm": 0.3, "amplitude_min": 0}]
    return fitting.run_fit(x, y, specs, background_method="none", n_perturb=0, fit_kws={"method": "leastsq", "fit_kws": SEED})


def test_a_small_component_relocated_beside_a_dominant_one_is_caught():
    a, b = _small_beside_dominant(399.4), _small_beside_dominant(400.6)
    assert a["certificate"]["certified"] and b["certificate"]["certified"]
    ca, cb = (r["individual_peaks"][1]["params"]["center"]["value"] for r in (a, b))
    assert abs(ca - 399.5) < 0.05 and abs(cb - 400.5) < 0.05          # two certified minima, 1 eV apart
    d = float(np.max(np.abs(np.asarray(a["fitted_y"]) - np.asarray(b["fitted_y"]))))
    assert d < SAME_MINIMUM_REL * 1e6                                    # invisible on the signal's scale
    _rejects(a, b, "individual_peaks.1.y", "individual_peaks.1.params.center")


def test_two_minor_components_that_swap_places_are_caught():
    # Codex A2 round 1 (run B): a dominant line and two minor ones 0.15 eV
    # apart; swapping the minor ones' parameters is a different decomposition.
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq", "fit_kws": SEED})
    b = copy.deepcopy(a)
    p, q = b["individual_peaks"]
    p["params"], q["params"] = q["params"], p["params"]
    p["y"], q["y"] = q["y"], p["y"]
    _rejects(a, b, "individual_peaks")


def test_a_centre_moved_by_a_small_fraction_of_its_width_is_caught():
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    b = copy.deepcopy(a)
    b["individual_peaks"][0]["params"]["center"]["value"] += 0.01       # 1 % of a 1.1 eV line
    _rejects(a, b, "center")


@pytest.mark.parametrize("bad", [float("nan"), None, float("inf")])
@pytest.mark.parametrize("where", ["fitted_y", "residuals", "component"])
def test_a_non_finite_or_missing_value_in_a_curve_is_caught(bad, where):
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    b = copy.deepcopy(a)
    (b["individual_peaks"][0]["y"] if where == "component" else b[where])[5] = bad
    _rejects(a, b, "non-finite")


def test_an_unsupported_component_is_compared_by_its_verdict_only():
    # its parameters are undetermined — that is what "not supported" says
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    b = copy.deepcopy(a)
    for r in (a, b):
        r["individual_peaks"][1]["support"]["supported"] = False
    b["individual_peaks"][1]["params"]["center"]["value"] += 2.0
    assert_same_fit(a, b)
    b["individual_peaks"][1]["support"]["supported"] = True
    _rejects(a, b, "individual_peaks.1")
