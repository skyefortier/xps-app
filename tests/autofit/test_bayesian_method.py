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


def test_free_energy_error_bar_and_selection_warning():
    """Split-half F error bars + the UNRESOLVED-selection warning (added after
    the real-data U 4f finding: seed-to-seed F spread flipped the winner while
    |ΔF| ~ 3 — silently, before this machinery).  K1-vs-K2 is decisive
    (ΔF ≈ 500): the warning must NOT fire.  (K2-vs-K3 legitimately CAN fire
    at reduced sweeps — the honest behavior, exercised by the twin test.)"""
    x, y = _spectrum()
    res = get_method("bayesian_exchange_mc").run(
        x, y, grammar=_grammar(),
        options={**OPTS, "candidate_filter": ["K1", "K2"]})
    scored = [c for c in res.analysis["candidates"] if "free_energy" in c]
    assert len(scored) == 2
    for c in scored:
        assert c["free_energy_split_half_error"] is None or \
            c["free_energy_split_half_error"] >= 0.0
        assert c["posterior_weight_reliable"] is True
    assert res.analysis["model_selection_warning"] is None
    assert res.diagnostics["model_selection_warning"] is None
    assert res.analysis["free_energy_is_relative"] is True


def test_sigma_stat_reliability_contract(result):
    """Re-check MAJOR: the consumer-visible CI reliability fields must be
    regression-pinned — sigma_stat carries reliability + note + per-interval
    ess (Codex Stage-5 blocker #2 fix)."""
    for role, conf in result.confidence.items():
        stat = conf["sigma_stat"]
        assert stat["reliability"] in ("ok", "low_ess", "stuck_chain"), role
        assert "reliability_note" in stat
        if stat["reliability"] != "ok":
            assert stat["reliability_note"]
        for pname, iv in (stat["values"] or {}).items():
            assert "ess" in iv, (role, pname)


def test_zero_variance_ess_is_stuck_not_perfect():
    """Re-check MAJOR: a sampled parameter that never moves must report
    ESS=0 (stuck chain), never ESS=n (Codex Stage-5 finding #3)."""
    from autofit.methods.bayesian_exchange_mc import _effective_sample_sizes
    n = 64
    samples = np.column_stack([
        np.full(n, 3.7),                      # stuck: zero variance
        np.random.default_rng(0).normal(size=n),  # healthy
    ])
    ess = _effective_sample_sizes(samples)
    assert ess[0] == 0.0
    assert ess[1] > 0.0


def test_analytic_evidence_flat_model():
    """Codex Stage-5 finding #4: peak-count recovery can pass while the
    evidence math is subtly wrong.  Pin the estimator against an ANALYTIC
    marginal likelihood: constant model f(x)=μ, uniform prior μ∈[a,b],
    σ-marginalized Gaussian likelihood ⇒

        Z = (1/V) ∫ RSS(μ)^(−n/2) dμ,   RSS(μ) = S + n(μ−ȳ)²

    (a Student-t kernel), computed by high-precision quadrature.  Two prior
    widths verify the prior-volume Occam factor flows through Z(0)."""
    from scipy.integrate import quad

    from autofit.methods.bayesian_exchange_mc import run_exchange_mc

    rng = np.random.default_rng(11)
    x = np.arange(0.0, 20.0, 0.1)
    y = 50.0 + rng.normal(0.0, 4.0, len(x))
    n = len(y)
    ybar = float(np.mean(y))
    S = float(np.sum((y - ybar) ** 2))

    def f_ref(a, b):
        # F = −log Z on the same "−(n/2)·log RSS" scale the sampler uses
        l_star = -(n / 2.0) * np.log(S)
        integ, _ = quad(lambda u: (1.0 + n * (u - ybar) ** 2 / S) ** (-n / 2.0),
                        a, b, epsabs=1e-14, epsrel=1e-12)
        return -(l_star + np.log(integ) - np.log(b - a))

    class _FlatSpace:
        names = ["mu"]

        def __init__(self, a, b):
            self.lows = np.array([a])
            self.highs = np.array([b])

        def model_eval(self, xx, theta):
            return np.full(len(xx), theta[0])

    results = {}
    for a, b in ((ybar - 2.0, ybar + 2.0), (ybar - 8.0, ybar + 8.0)):
        run = run_exchange_mc(x, y, _FlatSpace(a, b),
                              n_replicas=12, n_sweeps=4000, rng_seed=0)
        results[(a, b)] = (run["free_energy"], f_ref(a, b),
                           run["free_energy_split_half_error"])

    for (a, b), (f_est, f_exact, err) in results.items():
        assert f_est == pytest.approx(f_exact, abs=0.3), (
            f"width {b-a:.0f}: estimator {f_est:.3f} vs analytic {f_exact:.3f} "
            f"(split-half err {err})")
    (f1, r1, _), (f2, r2, _) = results.values()
    # Occam factor: widening the prior 4× must raise F by ~log 4 (the
    # likelihood mass is inside both windows) — matched analytically
    assert (f2 - f1) == pytest.approx(r2 - r1, abs=0.3)
    assert (r2 - r1) == pytest.approx(np.log(4.0), abs=0.05)


def test_seed_replicates_identity_and_mean_semantics():
    """Re-check #2 major: seed_replicates=1 must be IDENTICAL to omitting
    the option; k=2 reports F as the replicate mean with consumer-visible
    flags that only the evidence (not the posterior summary) is replicated."""
    x, y = _spectrum()
    m = get_method("bayesian_exchange_mc")
    base = m.run(x, y, grammar=_grammar(),
                 options={**OPTS, "candidate_filter": ["K2"]})
    k1 = m.run(x, y, grammar=_grammar(),
               options={**OPTS, "candidate_filter": ["K2"], "seed_replicates": 1})
    assert base.analysis == k1.analysis
    assert base.diagnostics == k1.diagnostics
    c = next(c for c in base.analysis["candidates"] if "free_energy" in c)
    assert c["free_energy_is_replicate_mean"] is False

    k2 = m.run(x, y, grammar=_grammar(),
               options={**OPTS, "candidate_filter": ["K2"], "seed_replicates": 2})
    c2 = next(c for c in k2.analysis["candidates"] if "free_energy" in c)
    assert c2["free_energy_is_replicate_mean"] is True
    reps = c2["free_energy_replicates"]
    assert len(reps) == 2
    assert c2["free_energy"] == pytest.approx(np.mean(reps))
    assert k2.analysis["posterior_summary_replicated"] is False
    assert k2.analysis["posterior_samples_seed"] == OPTS["rng_seed"]
    # base-seed replicate equals the k=1 evidence (same rng path)
    assert reps[0] == pytest.approx(
        next(c["free_energy"] for c in k1.analysis["candidates"]
             if "free_energy" in c))


def test_selection_warning_fires_on_twin_models():
    """Two structurally identical candidates have ΔF ≈ 0 by construction —
    the unresolved-selection warning MUST fire."""
    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
                            slots=(_slot("p1", (99.0, 101.0)),
                                   _slot("p2", (101.5, 103.5))))
    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
                            slots=(_slot("p1", (99.0, 101.0)),
                                   _slot("p2", (101.5, 103.5))))
    grammar = CandidateGrammar(regions=("T",), phase_ids=("t",),
                               candidates=[twin_a, twin_b],
                               diagnostic_windows={}, provenance={})
    x, y = _spectrum()
    res = get_method("bayesian_exchange_mc").run(x, y, grammar=grammar,
                                                 options=OPTS)
    assert res.success
    warning = res.analysis["model_selection_warning"]
    assert warning and "UNRESOLVED" in warning


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
