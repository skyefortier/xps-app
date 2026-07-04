"""
Sparse/MAP method validation (decision-matrix entry 4; STAM:Methods 2024,
Tibshirani 1996).

Synthetic ground truth in the method's OWN regime (few separated peaks,
Gaussian shapes): the L1 path + debiased-BIC selection must recover the
peak count without inventing extras, with grid-limited center accuracy and
debiased (not L1-shrunk) amplitudes.
"""

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

TRUE_PEAKS = [(100.2, 2000.0, 1.1), (102.6, 900.0, 1.3)]
TRUE_SIGMA = 12.0


def _slot(role, window, shape=LineShape.GAUSSIAN):
    return ComponentSlot(role=role, region="T", phase_id="t",
                         be_window=window, line_shape=shape,
                         fwhm_range=(0.6, 2.2))


def _grammar(shape=LineShape.GAUSSIAN):
    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
                           slots=(_slot("p1", (99.0, 101.2), shape),
                                  _slot("p2", (101.6, 103.8), shape)))
    return CandidateGrammar(regions=("T",), phase_ids=("t",),
                            candidates=[model],
                            diagnostic_windows={}, provenance={})


def _spectrum(seed=5):
    rng = np.random.default_rng(seed)
    x = np.arange(97.0, 106.0, 0.05)
    y = np.full_like(x, 250.0)
    for c, a, w in TRUE_PEAKS:
        y = y + a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
    return x, y + rng.normal(0, TRUE_SIGMA, len(x))


@pytest.fixture(scope="module")
def result():
    x, y = _spectrum()
    return get_method("sparse_map").run(x, y, grammar=_grammar())


def test_recovers_peak_count_without_invention(result):
    assert result.success, result.message
    assert result.diagnostics["n_peaks"] == 2, (
        f"expected 2 peaks, got {result.diagnostics['n_peaks']} "
        f"(λ={result.diagnostics['selected_lambda']:.3g})")


def test_centers_grid_accurate_and_amplitudes_debiased(result):
    peaks = sorted(result.peaks, key=lambda p: p["center"])
    for p, (c, a, w) in zip(peaks, TRUE_PEAKS):
        # centers are grid-quantized (0.05 eV step) + cluster-averaged
        assert p["center"] == pytest.approx(c, abs=0.15)
        # debiased NNLS amplitudes — NOT L1-shrunk (which would bias low)
        assert p["amplitude"] == pytest.approx(a, rel=0.15)
        assert p["fwhm"] == pytest.approx(w, rel=0.4)   # width-ladder quantized


def test_roles_assigned_from_grammar_windows(result):
    roles = {p["role"] for p in result.peaks}
    assert roles == {"p1", "p2"}


def test_uncertainty_is_honestly_unavailable(result):
    for role, conf in result.confidence.items():
        stat = conf["sigma_stat"]
        assert stat["uncertainty_kind"] == "unavailable_post_selection"
        assert stat["values"] is None
        assert "not calibrated" in stat["note"]


def test_analysis_payload_documents_method_and_tunables(result):
    a = result.analysis
    assert "10.1080/27660400.2024.2373046" in a["basis"]
    assert a["dictionary"]["atom_shape"].startswith("gaussian")
    assert a["unverified_tunables"]          # spec §9 discipline
    assert any(r["bic"] is not None for r in a["lambda_path"])
    assert a["limitations"]
    import json
    json.dumps(a)                            # JSON-safe


def test_asymmetric_slots_flagged():
    x, y = _spectrum()
    res = get_method("sparse_map").run(x, y, grammar=_grammar(LineShape.ASYM_GL))
    assert res.success
    assert set(res.analysis["dictionary"]["asymmetric_slots_not_expressible"]) \
        == {"p1", "p2"}


def test_deterministic_no_rng():
    x, y = _spectrum()
    m = get_method("sparse_map")
    r1 = m.run(x, y, grammar=_grammar())
    r2 = m.run(x, y, grammar=_grammar())
    assert r1.diagnostics == r2.diagnostics
    assert r1.peaks == r2.peaks


def test_nn_lasso_cd_analytic_solution():
    """Codex Stage-7 finding #6: end-to-end tests can pass with a subtly
    wrong solver. Pin _nn_lasso_cd on an analytic problem: A = I,
    y = [2, -2, 0.3], λ = 0.5 ⇒ a* = [1.5, 0, 0] (the non-negative clamp
    must kill the negative-correlation coordinate; plain soft-thresholding
    would return -1.5 there)."""
    from autofit.methods.sparse_map import _nn_lasso_cd
    A = np.eye(3)
    y = np.array([2.0, -2.0, 0.3])
    a, kkt = _nn_lasso_cd(A, y, 0.5, np.zeros(3), tol=1e-12, max_iter=100)
    assert np.allclose(a, [1.5, 0.0, 0.0], atol=1e-10)
    assert kkt <= 1e-10


def test_lambda_max_boundary_behavior():
    """λ ≥ max(Aᵀy) ⇒ empty support; λ just below activates exactly the
    max-correlation atom (non-negative variant thresholds at the MAX, not
    max-|·|)."""
    from autofit.methods.sparse_map import _nn_lasso_cd
    rng = np.random.default_rng(3)
    A = rng.normal(size=(40, 5))
    A /= np.linalg.norm(A, axis=0)
    y = rng.normal(size=40)
    lam_max = float(np.max(A.T @ y))
    a, _ = _nn_lasso_cd(A, y, lam_max * 1.0000001, np.zeros(5),
                        tol=1e-12, max_iter=200)
    assert np.all(a == 0.0)
    a, _ = _nn_lasso_cd(A, y, lam_max * 0.999, np.zeros(5),
                        tol=1e-12, max_iter=200)
    assert np.count_nonzero(a) == 1
    assert a[int(np.argmax(A.T @ y))] > 0


def test_kkt_and_convergence_surfaced(result):
    assert "path_fully_converged" in result.analysis
    assert result.diagnostics["converged"] is True
    assert result.diagnostics["kkt_violation"] >= 0.0
    for r in result.analysis["lambda_path"]:
        assert "kkt_violation" in r and "converged" in r
        assert "n_atoms_active" in r


def test_slot_variant_union_flags_asymmetry():
    """Blocker #1 pin: a role that is Gaussian in one candidate and ASYM_GL
    in another must still be flagged not-expressible."""
    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
                        slots=(_slot("p1", (99.0, 101.2), LineShape.GAUSSIAN),))
    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
                        slots=(_slot("p1", (99.5, 101.5), LineShape.ASYM_GL),))
    g = CandidateGrammar(regions=("T",), phase_ids=("t",), candidates=[m1, m2],
                         diagnostic_windows={}, provenance={})
    x, y = _spectrum()
    res = get_method("sparse_map").run(x, y, grammar=g)
    assert res.analysis["dictionary"]["asymmetric_slots_not_expressible"] == ["p1"]


def test_option_validation():
    x, y = _spectrum()
    m = get_method("sparse_map")
    with pytest.raises(ValueError, match="unknown sparse_map options"):
        m.run(x, y, grammar=_grammar(), options={"bogus": 1})
    with pytest.raises(ValueError, match="requires a resolved grammar"):
        m.run(x, y)


def test_fixed_lambda_override():
    x, y = _spectrum()
    res = get_method("sparse_map").run(
        x, y, grammar=_grammar(),
        options={"lambda_fixed": 1.0})
    assert res.success
    assert len(res.analysis["lambda_path"]) == 1
