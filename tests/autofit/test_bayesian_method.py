"""
Bayesian exchange-MC method validation (decision-matrix entry 3;
Nagata/Sugita/Okada 2012, Tokuda 2017).

Synthetic ground-truth battery: known peak count, positions, and noise.
Reduced sampler settings keep runtime test-loop-sized (~5 s); production
defaults are larger.
"""

import json

import numpy as np
import pytest

from autofit.grammar import (
    BackgroundType,
    CandidateGrammar,
    CandidateModel,
    ComponentSlot,
    LineShape,
)
from autofit.methods import get_method

TRUE_SIGMA = 15.0
TRUE_PEAKS = [(100.2, 2000.0, 1.1), (102.4, 800.0, 1.4)]


def _slot(role, window):
    return ComponentSlot(role=role, region="T", phase_id="t",
                         be_window=window, line_shape=LineShape.GAUSSIAN,
                         fwhm_range=(0.5, 2.5))


def _grammar():
    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
                         slots=(_slot("p1", (99.0, 101.0)),))
    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
                         slots=(_slot("p1", (99.0, 101.0)),
                                _slot("p2", (101.5, 103.5))))
    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
                           slots=(_slot("p1", (99.0, 101.0)),
                                  _slot("p2", (101.5, 103.5)),
                                  _slot("p3", (103.8, 105.5))))
    return CandidateGrammar(regions=("T",), phase_ids=("t",),
                            candidates=[one, two, three],
                            diagnostic_windows={}, provenance={})


def _spectrum(seed=7):
    rng = np.random.default_rng(seed)
    x = np.arange(97.0, 106.0, 0.05)
    y = np.full_like(x, 300.0)
    for c, a, w in TRUE_PEAKS:
        y = y + a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
    return x, y + rng.normal(0, TRUE_SIGMA, len(x))


OPTS = {"n_replicas": 8, "n_sweeps": 500, "rng_seed": 0}


@pytest.fixture(scope="module")
def result():
    x, y = _spectrum()
    return get_method("bayesian_exchange_mc").run(x, y, grammar=_grammar(),
                                                  options=OPTS)


def test_selects_true_peak_count(result):
    assert result.success
    assert result.diagnostics["winner"] == "K2"
    by_name = {c["name"]: c for c in result.analysis["candidates"]
               if "free_energy" in c}
    # under-specified K1 decisively rejected; over-specified K3 penalized
    assert by_name["K1"]["free_energy"] > by_name["K2"]["free_energy"] + 10
    assert by_name["K3"]["free_energy"] >= by_name["K2"]["free_energy"]
    assert result.diagnostics["posterior_weight"] > 0.5


def test_posterior_recovers_truth(result):
    by_role = {p["role"]: p for p in result.peaks}
    for role, (c, a, w) in zip(("p1", "p2"), TRUE_PEAKS):
        p = by_role[role]
        assert p["center"] == pytest.approx(c, abs=0.05)
        assert p["amplitude"] == pytest.approx(a, rel=0.05)
        assert p["fwhm"] == pytest.approx(w, rel=0.10)


def test_noise_estimated(result):
    assert result.diagnostics["sigma_hat"] == pytest.approx(TRUE_SIGMA, rel=0.3)


def test_uncertainty_typed_and_honest(result):
    conf = result.confidence["p1"]
    stat = conf["sigma_stat"]
    assert stat["uncertainty_kind"] == "posterior_ci"
    ci = stat["values"]["center"]
    assert ci["ci_low"] <= ci["median"] <= ci["ci_high"]
    # ESS honesty machinery present: every scored candidate reports it and
    # carries the reliability warning field (possibly None)
    for c in result.analysis["candidates"]:
        if "free_energy" in c:
            assert "min_effective_sample_size" in c
            assert "ci_reliability_warning" in c
    # separate systematic field, never combined
    assert conf["reference_sensitivity_range"]["kind"] == "unavailable_single_fit"


def test_payload_json_safe_and_documented(result):
    json.dumps(result.analysis)
    json.dumps(result.confidence)
    assert "gaussian_sigma_marginalized" in result.analysis["likelihood"]
    assert result.analysis["priors"] == "uniform within grammar bounds"
    assert "stepping-stone" in result.analysis["model_selection"]


def test_determinism_and_option_validation():
    x, y = _spectrum()
    m = get_method("bayesian_exchange_mc")
    r1 = m.run(x, y, grammar=_grammar(),
               options={**OPTS, "candidate_filter": ["K2"]})
    r2 = m.run(x, y, grammar=_grammar(),
               options={**OPTS, "candidate_filter": ["K2"]})
    assert r1.diagnostics["free_energy"] == r2.diagnostics["free_energy"]
    with pytest.raises(ValueError, match="unknown bayesian_exchange_mc options"):
        m.run(x, y, grammar=_grammar(), options={"bogus": 1})
    with pytest.raises(ValueError, match="requires a resolved grammar"):
        m.run(x, y)
