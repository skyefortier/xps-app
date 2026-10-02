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
from _legacy_line import legacy_line  # noqa: F401,E402  (autouse: the fixtures' background arithmetic)

SEED = {"seed": 123}


def _rejects(a, b, *fields):
    assert a["random_seed"] == b["random_seed"]            # the seed cannot be what differs
    with pytest.raises(AssertionError, match="not the same fit") as e:
        assert_same_fit(a, b)
    msg = str(e.value)
    assert "random_seed" not in msg
    for f in fields:
        assert f in msg, msg


def _set_shape(resp, k, shape, params):
    """Give returned component k (and every scattered-start alternative's component of the same
    id) a lineshape consistently: its parameters, and its curve computed from them."""
    x = np.asarray(resp["energy"], float)
    pk = resp["individual_peaks"][k]
    func = fitting._SHAPE_FUNCS[shape]
    pk["shape"] = shape
    pk["params"] = {name: {"value": float(v), "stderr": None, "vary": True, "expr": None, "min": None, "max": None}
                    for name, v in params.items()} | {"area": pk["params"]["area"]}
    pk["y"] = list(np.asarray(func(x, **params), float))
    for alt in (resp.get("starts") or {}).get("alternatives") or []:
        for c in alt["components"]:
            if str(c["id"]) == str(pk["id"]):
                c["params"] = dict(params, center=c["params"]["center"])


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


def test_an_alternatives_centres_are_scaled_by_its_own_widths():
    # Codex A2 round 4 (run A): an alternative's narrow line took the returned
    # fit's broad width as its scale, so two alternatives 0.24 eV apart passed
    x, y, specs = SS._two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    b = copy.deepcopy(a)
    for r in (a, b):
        for c in r["starts"]["alternatives"][0]["components"]:
            c["params"]["fwhm"] = 0.04
    comp = b["starts"]["alternatives"][0]["components"][0]
    comp["params"]["center"] += 0.24
    comp["center_shift_from_start"] += 0.24
    _rejects(a, b, "starts.alternatives.0.components.0")


def test_a_linked_parameter_is_judged_on_its_masters_span():
    # Codex A2 round 4 (runs A, B): recorded same-minimum presses of an LA doublet move m
    # 0.477 -> 0.001 inside its 0-499 span; the master passed, its linked copy (expr, no
    # bounds of its own) was compared relatively and failed
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    for r in (a,):
        m = r["individual_peaks"][0]["params"]["fwhm"]; m.update(min=0.0, max=499.0)
        c = r["individual_peaks"][1]["params"]["fwhm"]; c.update(expr=f"p{r['individual_peaks'][0]['id']}_fwhm", min=None, max=None, vary=False)
        c["value"] = m["value"]
    b = copy.deepcopy(a)
    for pk in b["individual_peaks"]:
        pk["params"]["fwhm"]["value"] += 0.4                 # inside 1e-3 of the master's 499 span
    assert_same_fit(a, b)
    for pk in b["individual_peaks"]:
        pk["params"]["fwhm"]["value"] += 0.2                 # beyond it
    _rejects(a, b, "individual_peaks.1.params.fwhm")


def test_an_alternative_without_a_fwhm_parameter_is_scaled_by_its_own_curve():
    # Codex A2 round 5 (runs A, B): a DS+G alternative (alpha, beta, m_gauss — no fwhm)
    # fell back to the returned fit's width
    x, y, specs = SS._two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    c0 = a["individual_peaks"][0]["params"]["center"]["value"]
    _set_shape(a, 0, "ds_g", {"amplitude": 500.0, "center": c0, "alpha": 0.0, "beta": 0.05, "m_gauss": 0.0})
    b = copy.deepcopy(a)
    assert_same_fit(a, b)
    comp = b["starts"]["alternatives"][0]["components"][0]
    comp["params"]["center"] += 0.24
    comp["center_shift_from_start"] += 0.24
    _rejects(a, b, "starts.alternatives.0.components.0.params.center")

def test_a_chain_of_links_is_judged_on_the_bounded_masters_span():
    # Codex A2 round 5 (runs A, B): p4_m -> p3_m -> p2_m — the grandchild fell back to a
    # relative allowance
    x, y, specs = R._crowded_c1s()
    a = fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=0, fit_kws={"method": "leastsq"})
    ids = [pk["id"] for pk in a["individual_peaks"]]
    root = a["individual_peaks"][0]["params"]["fwhm"]; root.update(min=0.0, max=499.0)
    for k in (1, 2):
        c = a["individual_peaks"][k]["params"]["fwhm"]
        c.update(expr=f"p{ids[k - 1]}_fwhm", min=None, max=None, vary=False, value=root["value"])
    b = copy.deepcopy(a)
    for k in (0, 1, 2):
        b["individual_peaks"][k]["params"]["fwhm"]["value"] += 0.4        # inside 1e-3 of the root's 499 span
    assert_same_fit(a, b)
    for k in (0, 1, 2):
        b["individual_peaks"][k]["params"]["fwhm"]["value"] += 0.2
    _rejects(a, b, "individual_peaks.2.params.fwhm")


def test_an_alternatives_bounded_parameter_uses_the_models_bounds():
    # Codex A2 round 6 (runs A, B): an alternative's parameters are bare values; its LA m
    # (bounds 0-499) was compared relatively, and equivalent alternatives (m 0.001 vs 0.300,
    # below one data point: identical curves) were rejected
    x, y, specs = SS._two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    c0 = a["individual_peaks"][0]["params"]["center"]["value"]
    _set_shape(a, 0, "la_casaxps", {"amplitude": 3000.0, "center": c0, "fwhm": 1.5, "alpha": 1.0, "beta": 1.0, "m": 0.001})
    a["individual_peaks"][0]["params"]["m"].update(min=0.0, max=499.0)
    b = copy.deepcopy(a)
    b["starts"]["alternatives"][0]["components"][0]["params"]["m"] = 0.300
    assert_same_fit(a, b)

def test_an_alternatives_curve_is_compared_against_its_own_height():
    # Codex A2 round 7 (run B): parameters inside their span, the reconstructed curve changed
    # by more than 1e-3 of its height — accepted, because alternatives' curves were not compared
    x, y, specs = SS._two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    a["individual_peaks"][0]["params"]["fwhm"].update(min=0.0, max=499.0)
    b = copy.deepcopy(a)
    b["starts"]["alternatives"][0]["components"][0]["params"]["fwhm"] += 0.3   # inside 1e-3 of the 499 span
    _rejects(a, b, "starts.alternatives.0.components.0.curve")


def test_a_narrow_bound_far_from_zero_is_judged_on_its_span():
    # Codex A2 round 7 (run A): widths bounded to [1.1, 1.101], two certified minima with
    # the widths swapped; max(span, |value|) allowed 0.0011 where the span allows 1e-6
    x = np.linspace(-50.0, 50.0, 2001)
    g = lambda w: 100 * np.exp(-4 * np.log(2) * (x / w) ** 2)
    y = g(1.1003) + g(1.1007) + 1.0 * (np.abs(x) > 20)

    def fit(w1, w2):
        specs = [{"id": i, "shape": "gaussian", "center": 0.0, "amplitude": 100.0, "fwhm": w, "fix_center": True, "fix_amplitude": True,
                  "fwhm_min": 1.1, "fwhm_max": 1.101} for i, w in ((1, w1), (2, w2))]
        return fitting.run_fit(x, y, specs, background_method="none", n_perturb=0, fit_kws={"method": "leastsq", "fit_kws": SEED})
    a, b = fit(1.1003, 1.1007), fit(1.1007, 1.1003)
    assert a["certificate"]["certified"] and b["certificate"]["certified"]
    wa = [pk["params"]["fwhm"]["value"] for pk in a["individual_peaks"]]
    wb = [pk["params"]["fwhm"]["value"] for pk in b["individual_peaks"]]
    assert abs(wa[0] - wb[0]) > 1e-4                       # the widths stayed swapped: two minima
    _rejects(a, b, "params.fwhm")


def test_a_link_to_a_master_whose_id_has_underscores_is_resolved():
    # Codex A2 round 6 (run B): proot_1_m was not recognised as a parameter name
    x, y, specs = R._two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    a["individual_peaks"][0]["id"] = "root_1"
    root = a["individual_peaks"][0]["params"]["fwhm"]; root.update(min=0.0, max=499.0)
    c = a["individual_peaks"][1]["params"]["fwhm"]; c.update(expr="proot_1_fwhm", min=None, max=None, vary=False, value=root["value"])
    b = copy.deepcopy(a)
    for k in (0, 1):
        b["individual_peaks"][k]["params"]["fwhm"]["value"] += 0.4
    assert_same_fit(a, b)


def test_a_lorentzian_alternative_is_not_judged_by_a_gaussian_twin():
    # Codex A2 round 8 (runs A, B): gaussian and lorentzian share parameter names; both curves
    # were reconstructed and compared, and a Lorentzian inside the resolution was rejected by
    # its fictitious Gaussian twin. The lineshape is the one reproducing the returned component.
    x, y, specs = SS._two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    c0 = a["individual_peaks"][0]["params"]["center"]["value"]
    _set_shape(a, 0, "lorentzian", {"amplitude": 3000.0, "center": c0, "fwhm": 1.0})
    xs = np.asarray(a["energy"], float)
    alt0 = a["starts"]["alternatives"][0]["components"][0]["params"]
    def rel_diff(f, d):
        u = f(xs, 3000.0, alt0["center"], 1.0); v = f(xs, 3000.0, alt0["center"] + d, 1.0)
        return np.max(np.abs(u - v)) / np.max(np.abs(u))
    d = next(d for d in np.linspace(1e-5, 9e-4, 400)
             if rel_diff(fitting._lorentzian, d) < 0.98e-3 < 1.02e-3 < rel_diff(fitting._gaussian, d))
    b = copy.deepcopy(a)
    b["starts"]["alternatives"][0]["components"][0]["params"]["center"] += d
    b["starts"]["alternatives"][0]["components"][0]["center_shift_from_start"] += d
    assert_same_fit(a, b)                                   # its own (Lorentzian) curve is within 1e-3


def test_an_alternative_whose_curve_cannot_be_reconstructed_fails_closed(monkeypatch):
    # Codex A2 round 8 (runs A, B): an evaluation that raised removed the curve check silently
    x, y, specs = SS._two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    b = copy.deepcopy(a)
    assert_same_fit(a, b)
    def broken(*args, **kw):
        raise ValueError("evaluation failed")
    monkeypatch.setitem(fitting._SHAPE_FUNCS, "gaussian", broken)
    monkeypatch.setitem(fitting._SHAPE_FUNCS, "pseudo_voigt_gl", broken)
    with pytest.raises(AssertionError, match="cannot be reconstructed"):
        assert_same_fit(a, b)


def test_one_ulp_inside_a_very_narrow_bound_is_the_same_fit():
    # Codex A2 round 8 (run B): amplitude bounded to [100, 100 + 1.1e-11]; two certified fits one
    # ULP apart were rejected by the span-only rule — a machine-precision floor, not a wider span
    x = np.linspace(-50.0, 50.0, 2001)
    y = 100.0 * np.exp(-4 * np.log(2) * (x / 1.1) ** 2) + 1.0 * (np.abs(x) > 20)

    def fit(amp):
        specs = [{"id": 1, "shape": "gaussian", "center": 0.0, "amplitude": amp, "fwhm": 1.1, "fix_center": True, "fix_fwhm": True,
                  "amplitude_min": 100.0, "amplitude_max": 100.0 + 1.1e-11}]
        return fitting.run_fit(x, y, specs, background_method="none", n_perturb=0, fit_kws={"method": "leastsq", "fit_kws": SEED})
    start = 100.0000000000055
    a, b = fit(start), fit(float(np.nextafter(start, np.inf)))
    assert a["certificate"]["certified"] and b["certificate"]["certified"]
    assert_same_fit(a, b)


def test_an_ambiguous_broad_component_is_identified_by_its_shape_not_its_curve():
    # Codex A2 round 9 (runs A, B): a very broad Gaussian and Lorentzian agree to 1e-13 on the
    # grid, so identification from the curve was ambiguous and a byte-identical copy failed
    # closed. The response carries the lineshape.
    x, y, specs = SS._two_basin_problem()
    specs = specs + [{"id": 9, "shape": "gaussian", "center": 287.0, "amplitude": 1.0, "fwhm": 1e7,
                      "fix_center": True, "fix_amplitude": True, "fix_fwhm": True}]
    a = fitting.run_fit(x, y + 1.0, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    assert [pk["shape"] for pk in a["individual_peaks"]] == [s_["shape"] for s_ in specs]
    assert_same_fit(a, copy.deepcopy(a))


def test_a_non_finite_reconstruction_fails_closed(monkeypatch):
    # Codex A2 round 9 (run B): an evaluator returning NaN at the alternative's parameters passed
    x, y, specs = SS._two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **SS.KW)
    b = copy.deepcopy(a)
    real = fitting._SHAPE_FUNCS["gaussian"]
    alt_centres = {c["params"]["center"] for alt in a["starts"]["alternatives"] for c in alt["components"]}
    def nan_at_alternatives(x_, amplitude, center, fwhm):
        return np.full_like(np.asarray(x_, float), np.nan) if center in alt_centres else real(x_, amplitude, center, fwhm)
    monkeypatch.setitem(fitting._SHAPE_FUNCS, "gaussian", nan_at_alternatives)
    with pytest.raises(AssertionError, match="cannot be reconstructed"):
        assert_same_fit(a, b)
