"""PeakFitMethod seam tests: registry, baseline, IC method, stubs."""

import numpy as np
import pytest

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import available_methods, get_method

GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")


def _synthetic_c1s(seed=1):
    rng = np.random.default_rng(seed)
    x = np.arange(280.0, 294.0, 0.1)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = 400 + g(284.4, 12000, 0.8) + g(286.2, 1500, 1.2) + g(290.8, 600, 2.0)
    y = y + rng.normal(0, 20, len(x))
    return x, y


def test_registry_shape():
    menu = available_methods()
    ids = [m["id"] for m in menu]
    assert ids == ["least_squares", "ic_model_comparison", "bayesian_exchange_mc",
                   "sparse_map", "multivariate_mcr", "max_entropy"]
    implemented = {m["id"] for m in menu if m["implemented"]}
    assert implemented == {"least_squares", "ic_model_comparison"}


@pytest.mark.parametrize("stub_id", ["bayesian_exchange_mc", "sparse_map",
                                     "multivariate_mcr", "max_entropy"])
def test_stubs_raise_with_pointer(stub_id):
    with pytest.raises(NotImplementedError, match="decision-matrix"):
        get_method(stub_id).run(None, None)


def test_unknown_method():
    with pytest.raises(KeyError, match="available"):
        get_method("nonexistent")


def test_least_squares_baseline():
    x, y = _synthetic_c1s()
    specs = [{"id": "1", "shape": "gaussian", "center": 284.6, "amplitude": 9000,
              "fwhm": 1.0},
             {"id": "2", "shape": "gaussian", "center": 286.4, "amplitude": 1000,
              "fwhm": 1.2},
             {"id": "3", "shape": "gaussian", "center": 290.6, "amplitude": 500,
              "fwhm": 2.0}]
    m = get_method("least_squares")
    res = m.run(x, y, peak_specs=specs, options={"background_method": "shirley"})
    assert res.success
    by_id = {p["id"]: p for p in res.peaks}
    assert by_id["1"]["center"] == pytest.approx(284.4, abs=0.05)
    assert by_id["2"]["center"] == pytest.approx(286.2, abs=0.1)
    conf = res.confidence["1"]
    assert conf["sigma_stat"]["uncertainty_kind"] == "covariance"
    assert conf["sigma_stat"]["values"]["center"] is not None
    # σ_stat and reference sensitivity stay separate fields (no quadrature)
    assert conf["reference_sensitivity_range"]["kind"] == "unavailable_single_fit"
    with pytest.raises(ValueError, match="unknown least_squares options"):
        m.run(x, y, peak_specs=specs, options={"bogus": 1})
    with pytest.raises(ValueError, match="peak_specs"):
        m.run(x, y)


def test_ic_model_comparison_end_to_end():
    x, y = _synthetic_c1s()
    grammar = resolve([GRAPHITE], "C 1s")
    m = get_method("ic_model_comparison")
    res = m.run(x, y, grammar=grammar, options={
        "n_refits": 4, "noise_floor": 25.0,
        "candidate_filter": ["A1_linked", "AG1_linked", "B2_linked"],
    })
    assert res.success
    assert res.diagnostics["winner"]
    roles = {p["role"] for p in res.peaks}
    assert "main_graphitic" in roles
    main = next(p for p in res.peaks if p["role"] == "main_graphitic")
    assert main["center"] == pytest.approx(284.4, abs=0.05)
    assert main["phase_id"] == "graphite" and main["region"] == "C 1s"

    # analysis payload: regenerable candidate record + criteria panel
    a = res.analysis
    assert a["method"] == "ic_model_comparison"
    assert {c["name"] for c in a["candidates"]} >= {"A1_linked", "AG1_linked"}
    panel = a["criteria_panel"]
    assert "not independent tests" in panel["statement"]
    assert isinstance(panel["bic_ambiguous"], bool)
    assert isinstance(panel["criteria_conflict"], bool)
    assert panel["top_by_bic_star"] == res.diagnostics["winner"]

    # the analysis namespace must be JSON-serializable by definition
    # (it goes straight into the .proj v3 `analysis` key)
    import json
    json.dumps(a)
    json.dumps({k: v for k, v in res.confidence.items()})

    # per-slot confidence vectors with typed uncertainty kinds
    conf = res.confidence["main_graphitic"]
    assert conf["sigma_stat"]["uncertainty_kind"] in (
        "covariance", "stability_mad", "unavailable")
    assert conf["stability"]["persistence"] >= 0.7
    assert conf["detectability"]["status"] == "above_floor"

    with pytest.raises(ValueError, match="requires a resolved grammar"):
        m.run(x, y)
    with pytest.raises(ValueError, match="unknown ic_model_comparison options"):
        m.run(x, y, grammar=grammar, options={"bogus": 1})


def test_ic_no_survivor_is_honest():
    """A grammar whose windows exclude the actual peak → no survivor, not a
    forced answer (diagnostic-not-prescriptive)."""
    x, y = _synthetic_c1s()
    grammar = resolve([GRAPHITE], "C 1s")
    m = get_method("ic_model_comparison")
    # B-family symmetric models on a spectrum whose main is at 284.4 with a
    # satellite: give the engine only clearly-wrong candidates
    res = m.run(x[:30], np.full(30, 400.0), grammar=grammar, options={
        "n_refits": 2, "noise_floor": 25.0,
        "candidate_filter": ["B2_linked"], "enable_proposal_pass": False,
    })
    assert not res.success
    assert res.peaks == []
    assert "no candidate survived" in res.message
