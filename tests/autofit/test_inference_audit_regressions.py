"""Independent scientific counterexamples from the September 2026 audit."""
from dataclasses import replace

import numpy as np
import pytest

from autofit.criteria import build_criteria_panel, f_test, is_nested
from autofit.methods.bayesian_exchange_mc import (
    BayesianExchangeMCMethod, _posterior_peaks, run_exchange_mc,
)
from autofit.methods.multivariate_mcr import MultivariateMCRMethod
from autofit.reference import peak_to_backend_spec
from tests.autofit.test_criteria import _report
from tests.autofit.test_bayesian_method import _grammar, _spectrum


def test_added_peak_has_no_uncalibrated_f_probability():
    a = _report(["main"], rss=100, k=4)
    b = _report(["main", "extra"], rss=50, k=8)
    res = f_test(a, b)
    assert res.f_stat > 0 and res.p_value is None
    assert not res.rejects_extra_peak and not res.calibrated
    panel = build_criteria_panel([a, b], [a, b])
    assert panel["f_tests"][0]["p_value"] is None
    assert "boundary null" in panel["f_tests"][0]["reason"]


@pytest.mark.parametrize("change", [
    {"be_window": (20, 30)}, {"fwhm_range": (4, 5)},
    {"fixed_params": (("fwhm", 1.0),)},
    {"fwhm_linked_to": "common_width"},
    {"param_ranges": (("gl_ratio", (.2, .4)),)},
])
def test_structural_nesting_includes_bounds_and_linkage(change):
    a, b = _report(["main"], 100, 4), _report(["main", "extra"], 80, 8)
    b.model = replace(b.model, slots=(replace(b.model.slots[0], **change), b.model.slots[1]))
    assert not is_nested(a, b)
    assert f_test(a, b) is None


def test_added_peak_tied_to_shared_parent_cannot_vanish():
    a, b = _report(["main"], 100, 4), _report(["main", "extra"], 80, 8)
    b.model = replace(b.model, slots=(b.model.slots[0], replace(
        b.model.slots[1], linked_to="main", area_ratio=.5)))
    assert not is_nested(a, b)


@pytest.mark.parametrize("closure", [False, True])
def test_rank_retains_constant_spectrum(closure):
    x = np.arange(7.)
    a, b = np.array([0, 1, 4, 9, 4, 1, 0]), np.array([0, 0, 0, 0, 0, 1, 4])
    for matrix, rank in [(np.tile(a, (3, 1)), 1),
                         (a + np.arange(1., 5.)[:, None] * b, 2)]:
        out = MultivariateMCRMethod().run(x, matrix, options={"closure": closure})
        assert out.analysis["rank"] == rank
        assert out.analysis["lack_of_fit"] < 1e-6
        assert not out.analysis["closure_enforced"]
        assert "not a chemical species count" in out.analysis["rank_interpretation"]


@pytest.mark.parametrize("option,value", [
    ("n_replicas", 2), ("n_replicas", 65), ("n_replicas", 3.5),
    ("n_sweeps", 2), ("n_sweeps", 100001), ("n_sweeps", True),
    ("beta_min", 0), ("beta_min", 1), ("beta_min", float("nan")),
    ("burn_fraction", 0), ("burn_fraction", 1),
    ("exchange_every", 0), ("exchange_every", 1000),
    ("ci_level", 0), ("ci_level", 1), ("ci_level", float("nan")),
    ("seed_replicates", 0), ("seed_replicates", 17),
    ("rng_seed", -1),
])
def test_bayesian_rejects_invalid_options_before_sampling(option, value):
    x, y = _spectrum()
    with pytest.raises(ValueError, match=option):
        BayesianExchangeMCMethod().run(x, y, grammar=_grammar(), options={
            "n_sweeps": 20, option: value})


def test_sampler_ladder_reaches_posterior_and_requires_samples():
    class FlatSpace:
        names = ["mean"]
        lows, highs = np.array([0.]), np.array([2.])
        def model_eval(self, x, theta):
            return np.full_like(x, theta[0])
    x = np.arange(10.)
    y = np.linspace(.5, 1.5, 10)
    run = run_exchange_mc(x, y, FlatSpace(), n_replicas=3, n_sweeps=20)
    assert run["betas"][0] == 0 and run["betas"][-1] == 1
    assert run["n_post"] == 10 and len(run["ess"]) == 1
    with pytest.raises(ValueError, match="post-burn"):
        run_exchange_mc(x, y, FlatSpace(), n_sweeps=20, burn_fraction=.9)


@pytest.mark.parametrize("alias,canonical,backend", [
    ("LA", "DSG_LA", "ds_g"), ("DSG", "DS", "doniach_sunjic")])
def test_saved_legacy_shapes_migrate_without_mutation(alias, canonical, backend):
    peak = dict(id=1, center=100, amplitude=100, fwhm=1, shape=alias,
                laAlpha=.2, laBeta=.3, laM=.4, dsAlpha=.15)
    actual = peak_to_backend_spec(peak, [peak])
    expected = peak_to_backend_spec({**peak, "shape": canonical}, [])
    assert actual == expected and actual["shape"] == backend
    assert peak["shape"] == alias


def test_unknown_saved_shape_is_not_silently_gaussian():
    with pytest.raises(ValueError, match="unknown saved peak shape"):
        peak_to_backend_spec(dict(id=1, center=100, amplitude=10, fwhm=1,
                                  shape="new_unknown"), [])


def test_missing_sampler_diagnostics_never_marked_reliable(monkeypatch):
    import autofit.methods.bayesian_exchange_mc as bayes
    original = bayes.run_exchange_mc
    def missing(*args, **kwargs):
        result = original(*args, **kwargs)
        result["ess"] = []
        result["free_energy_split_half_error"] = None
        return result
    monkeypatch.setattr(bayes, "run_exchange_mc", missing)
    x, y = _spectrum()
    out = BayesianExchangeMCMethod().run(x, y, grammar=_grammar(), options={
        "n_replicas": 3, "n_sweeps": 20, "candidate_filter": ["K1"]})
    assert out.success
    assert out.analysis["model_selection_warning"]
    assert out.analysis["candidates"][0]["posterior_weight_reliable"] is False
    assert all(c["sigma_stat"]["reliability"] == "unavailable"
               for c in out.confidence.values())


def test_manual_wrapper_honors_empirical_weights():
    from autofit.methods.least_squares import LeastSquaresMethod
    x = np.linspace(-2, 2, 51)
    g = np.exp(-4 * np.log(2) * (x / .8)**2)
    y = 10 * g + np.linspace(0, 3, len(x))
    weights = np.linspace(.1, 2, len(x))
    expected = np.sum(weights**2 * g * y) / np.sum(weights**2 * g**2)
    out = LeastSquaresMethod().run(x, y, weights=weights, peak_specs=[dict(
        id=1, shape="gaussian", amplitude=8, center=0, fwhm=.8,
        fix_center=True, fix_fwhm=True)], options={"background_method": "none"})
    assert out.success
    assert out.peaks[0]["amplitude"] == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize("diagnostic_gap", ["large_error", "missing_error", "missing_ess"])
def test_every_evidence_replicate_contributes_to_reliability(monkeypatch, diagnostic_gap):
    """Independent runs may agree in mean F while one run has serious drift.
    Evidence means from that run must not lose its error/ESS diagnostic."""
    import autofit.methods.bayesian_exchange_mc as bayes
    original = bayes.run_exchange_mc
    def controlled(x, y, space, **kwargs):
        result = original(x, y, space, **kwargs)
        # K1 wins by10, much larger than the base-seed errors of0.1 each.
        result["free_energy"] = 0. if len(space.names) == 3 else 10.
        result["free_energy_split_half_error"] = .1
        result["ess"] = [100.] * len(space.names)
        if kwargs["rng_seed"] == 1 and len(space.names) == 3:
            if diagnostic_gap == "large_error":
                result["free_energy_split_half_error"] = 10.
            elif diagnostic_gap == "missing_error":
                result["free_energy_split_half_error"] = None
            else:
                result["ess"] = []
        return result
    monkeypatch.setattr(bayes, "run_exchange_mc", controlled)
    x, y = _spectrum()
    result = bayes.BayesianExchangeMCMethod().run(x, y, grammar=_grammar(), options={
        "n_replicas": 3, "n_sweeps": 20, "seed_replicates": 2,
        "candidate_filter": ["K1", "K2"]})
    assert result.success
    assert "UNRESOLVED" in result.analysis["model_selection_warning"]
    candidates = result.analysis["candidates"]
    assert all(c["posterior_weight_reliable"] is False for c in candidates)
    k1 = next(c for c in candidates if c["name"] == "K1")
    assert k1["free_energy_replicate_spread"] == 0
    assert k1["free_energy_replicate_diagnostics"][1]["seed"] == 1
    if diagnostic_gap == "large_error":
        assert k1["free_energy_mc_error"] == 10
    else:
        assert k1["evidence_diagnostics_complete"] is False
