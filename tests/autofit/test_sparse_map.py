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
