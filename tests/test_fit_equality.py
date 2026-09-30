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
    _rejects(a, b, "individual_peaks.1.params.center")


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


def _unsupported_pair(centre):
    # Codex A2 round 2 (run B): a held dominant line, two equal narrow lines at
    # +-0.25 eV and a symmetric residual; one free narrow component certifies at
    # either line — two minima five widths apart, the component NOT supported
    # (F < 10) in both. "Unsupported" does not make them one minimum.
    x = np.linspace(-500.0, 500.0, 20001)
    g = lambda c, a, w: a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
    dom = g(0.0, 1e6, 300.0)
    y = dom + g(-0.25, 500, 0.1) + g(0.25, 500, 0.1) + 5 * np.sqrt(dom) * np.cos(3 * x) * (np.abs(x) > 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 0.0, "amplitude": 1e6, "fwhm": 300.0, "fix_center": True, "fix_amplitude": True, "fix_fwhm": True},
             {"id": 2, "shape": "gaussian", "center": centre, "amplitude": 400.0, "fwhm": 0.1, "amplitude_min": 0,
              "center_min": -1.0, "center_max": 1.0, "fwhm_min": 0.05, "fwhm_max": 0.15}]
    return fitting.run_fit(x, y, specs, background_method="none", n_perturb=0, fit_kws={"method": "leastsq", "fit_kws": SEED})


def test_an_unsupported_component_at_another_minimum_is_caught():
    a, b = _unsupported_pair(-0.25), _unsupported_pair(0.25)
    assert a["certificate"]["certified"] and b["certificate"]["certified"]
    assert a["individual_peaks"][1]["support"]["supported"] is False is b["individual_peaks"][1]["support"]["supported"]
    ca, cb = (r["individual_peaks"][1]["params"]["center"]["value"] for r in (a, b))
    assert ca < -0.2 and cb > 0.2
    _rejects(a, b, "individual_peaks.1")


def test_a_statistically_indistinguishable_pair_of_minima_is_still_told_apart():
    # Codex A2 round 3 (runs A and B): the unsupported pair with both true lines
    # at height 10: the saddle between the minima is 6e-10 relative in chi2 and
    # the centre's sigma 17 eV, so no statistical criterion separates them — on
    # its own width the centre moved five widths.
    import test_fit_equality as me
    x = np.linspace(-500.0, 500.0, 20001)
    g = lambda c, a_, w: a_ * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
    dom = g(0.0, 1e6, 300.0)
    y = dom + g(-0.25, 10, 0.1) + g(0.25, 10, 0.1) + 5 * np.sqrt(dom) * np.cos(3 * x) * (np.abs(x) > 2)

    def fit(c):
        specs = [{"id": 1, "shape": "gaussian", "center": 0.0, "amplitude": 1e6, "fwhm": 300.0, "fix_center": True, "fix_amplitude": True, "fix_fwhm": True},
                 {"id": 2, "shape": "gaussian", "center": c, "amplitude": 10.0, "fwhm": 0.1, "fix_fwhm": True, "amplitude_min": 0,
                  "center_min": -1.0, "center_max": 1.0}]
        return fitting.run_fit(x, y, specs, background_method="none", n_perturb=0, fit_kws={"method": "leastsq", "fit_kws": SEED})
    a, b = fit(-0.25), fit(0.25)
    assert a["certificate"]["certified"] and b["certificate"]["certified"]
    assert a["statistics"]["chi_square"] == pytest.approx(b["statistics"]["chi_square"], rel=1e-9)
    _rejects(a, b, "individual_peaks.1.params.center", "individual_peaks.1.y")


def test_a_component_curve_or_area_regression_is_caught():
    # Codex A2 round 3: a determined component's curve and every area were unchecked
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    for mutate, field in ((lambda r: r["individual_peaks"][0]["y"].__setitem__(40, r["individual_peaks"][0]["y"][40] + 1e6), "individual_peaks.0.y"),
                          (lambda r: r["individual_peaks"][0]["params"]["area"].__setitem__("value", r["individual_peaks"][0]["params"]["area"]["value"] * 2), "area"),
                          (lambda r: r["individual_peaks"][0]["params"]["area"].__setitem__("value", float("nan")), "area")):
        b = copy.deepcopy(a); mutate(b)
        _rejects(a, b, field)


def test_matching_infinities_do_not_hide_a_finite_difference():
    # Codex A2 round 2: +inf at one sample of both copies made the scale infinite
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    b = copy.deepcopy(a)
    a["fitted_y"][3] = b["fitted_y"][3] = float("inf")
    b["fitted_y"][40] += 1e6
    _rejects(a, b, "fitted_y")
    # and in the curve of a component the fit does not determine (no sigma: its curve decides)
    a2, b2 = copy.deepcopy(a), copy.deepcopy(a)
    for r in (a2, b2):
        for info in r["individual_peaks"][0]["params"].values():
            info["stderr"] = None
    a2["individual_peaks"][0]["y"][3] = b2["individual_peaks"][0]["y"][3] = float("inf")
    b2["individual_peaks"][0]["y"][40] += 1e6
    _rejects(a2, b2, "individual_peaks.0.y")


@pytest.mark.parametrize("where", ["fit", "alternative", "not_better"])
def test_a_scattered_start_objective_is_compared_at_the_objective_scale(where):
    # Codex A2 round 2: the starts' chi2r got the parameter tolerance (+0.09 % passed)
    x, y, specs = SS._two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    b = copy.deepcopy(a)
    st = b["starts"]
    if where == "fit":
        st["fit"]["chi2r"] *= 1.0009
    elif where == "alternative":
        st["alternatives"][0]["chi2r"] *= 1.0009
    else:
        assert st["not_better_chi2r"], "the model's starts include a not-better solution"
        st["not_better_chi2r"][0] *= 1.0009
    _rejects(a, b, "starts")


def test_uncertainties_are_not_compared():
    # not reproducible within one minimum near a bound (committed evidence in fit_equality's docstring)
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    b = copy.deepcopy(a)
    b["individual_peaks"][0]["params"]["gl_ratio"]["stderr"] = 4 * (a["individual_peaks"][0]["params"]["gl_ratio"]["stderr"] or 1)
    assert_same_fit(a, b)
