"""
Cl 2p independent-doublet-width machinery (adjudication 2026-07-03 #7).

The adjudication ruled: allow the Cl 2p doublet components independent
widths under the Coster-Kronig inequality fwhm(2p1/2) >= fwhm(2p3/2), with
the 2:1 statistical ratio as an AREA statement.  These tests pin the
machinery on synthetic ground truth so the REAL-anchor outcome (excess
pegged at 0, ratio still rejected — see PROGRESS.md) is interpretable as a
data statement rather than an implementation artifact:

1. parameter construction: excess param + width expression + width-aware
   area-ratio amplitude link;
2. recovery: when the true 2p1/2 IS broader at a true 2:1 area ratio, the
   free-width candidate recovers the excess and beats the shared-width
   candidates in the enumeration;
3. nested null: when the true widths are equal, the excess pegs at 0 and
   selection prefers the nested shared-width candidate;
4. validation guards (missing parent / conflicting width specs / gl_ratio
   not shared).
"""

import numpy as np
import pytest

from autofit.engine import _default_params_from_slots, fit_candidate
from autofit.grammar import (
    BackgroundType,
    CandidateModel,
    ComponentSlot,
    LineShape,
    MaterialClass,
    Phase,
    resolve,
)
from autofit.methods import get_method
from autofit.regions.cl2p import (
    CL2P_12_FWHM_EXCESS_RANGE,
    CL2P_RATIO,
)

UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
             regions=("U 4f", "Cl 2p"))
OPTIONS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": False}

SPLIT = 1.60


def _pv(x, height, center, fwhm, eta=0.3):
    g = np.exp(-4 * np.log(2) * ((x - center) / fwhm) ** 2)
    hw = fwhm / 2.0
    lo = hw ** 2 / ((x - center) ** 2 + hw ** 2)
    return height * ((1 - eta) * g + eta * lo)


def _doublet_spectrum(fwhm32=1.65, excess=0.0, area_ratio=CL2P_RATIO, seed=5):
    """Synthetic Cl 2p doublet with TRUE area ratio and width excess."""
    rng = np.random.default_rng(seed)
    x = np.arange(192.0, 205.0, 0.05)
    fwhm12 = fwhm32 + excess
    h32 = 9000.0
    # area ∝ height × fwhm (same eta) → height12 enforces the AREA ratio
    h12 = h32 * area_ratio * fwhm32 / fwhm12
    y = (300.0 + _pv(x, h32, 197.9, fwhm32) + _pv(x, h12, 197.9 + SPLIT, fwhm12))
    return x, y + rng.normal(0, 12, len(x))


def _grammar_candidates():
    return {c.name: c for c in resolve([UCL4], "Cl 2p").candidates}


def test_menu_contains_freewidth_candidates():
    names = set(_grammar_candidates())
    assert {"Cl0_doublet", "Cl0r_doublet_relaxed", "Cl0w_doublet_freewidth",
            "Cl0rw_doublet_relaxed_freewidth"} <= names


def test_freewidth_param_construction():
    cand = _grammar_candidates()["Cl0w_doublet_freewidth"]
    p = _default_params_from_slots(cand)
    exc = p["s_main_cl2p12_fwhm_excess"]
    assert exc.vary and (exc.min, exc.max) == CL2P_12_FWHM_EXCESS_RANGE
    # width is an expression: parent width + excess
    w12 = p["s_main_cl2p12_fwhm"]
    assert w12.expr == "s_main_cl2p32_fwhm + s_main_cl2p12_fwhm_excess"
    # amplitude carries the width correction (area-ratio semantics)
    a12 = p["s_main_cl2p12_amplitude"]
    assert "s_main_cl2p32_fwhm / s_main_cl2p12_fwhm" in a12.expr
    # gl_ratio shared with the parent
    assert p["s_main_cl2p12_gl_ratio"].expr == "s_main_cl2p32_gl_ratio"


def test_freewidth_recovers_true_excess_and_wins():
    """True 2p1/2 broader by 0.35 eV at a true 2:1 AREA ratio: the
    free-width fixed-ratio candidate must recover the excess and win the
    enumeration against both shared-width candidates."""
    x, y = _doublet_spectrum(excess=0.35)
    res = get_method("ic_model_comparison").run(
        x, y, grammar=resolve([UCL4], "Cl 2p"), options=OPTIONS)
    assert res.success
    assert res.diagnostics["winner"].startswith("Cl0w_doublet_freewidth")
    by_role = {p["role"]: p for p in res.peaks}
    p32, p12 = by_role["main_cl2p32"], by_role["main_cl2p12"]
    assert p12["fwhm"] - p32["fwhm"] == pytest.approx(0.35, abs=0.06)
    area_ratio = (p12["amplitude"] * p12["fwhm"]) / (p32["amplitude"] * p32["fwhm"])
    assert area_ratio == pytest.approx(CL2P_RATIO, abs=1e-6)  # held exactly
    # and the width freedom must have paid on fit quality vs shared width
    names = {c["name"]: c for c in res.analysis["candidates"]}
    assert (names["Cl0w_doublet_freewidth"]["reduced_chi_sq"]
            < names["Cl0_doublet"]["reduced_chi_sq"] * 0.8)


def test_equal_width_truth_pegs_excess_and_prefers_nested_model():
    """True equal widths: the excess pegs at its 0 bound (boundary hit) and
    the enumeration prefers a nested shared-width candidate."""
    x, y = _doublet_spectrum(excess=0.0)
    res = get_method("ic_model_comparison").run(
        x, y, grammar=resolve([UCL4], "Cl 2p"), options=OPTIONS)
    assert res.success
    names = {c["name"]: c for c in res.analysis["candidates"]}
    w = names["Cl0w_doublet_freewidth"]
    assert "main_cl2p12:fwhm_excess@min" in w["boundary_hits"]
    assert res.diagnostics["winner"].startswith(("Cl0_doublet",
                                                 "Cl0r_doublet_relaxed"))


def _slot(role, **kw):
    defaults = dict(region="T 2p", phase_id="t", be_window=(196.5, 199.0),
                    line_shape=LineShape.PSEUDO_VOIGT, fwhm_range=(0.6, 2.2))
    defaults.update(kw)
    return ComponentSlot(role=role, **defaults)


def test_excess_without_parent_raises():
    cand = CandidateModel(
        name="bad", background=BackgroundType.LINEAR,
        slots=(_slot("main", fwhm_excess_range=(0.0, 0.5)),))
    with pytest.raises(ValueError, match="no.*linked parent"):
        _default_params_from_slots(cand)


def test_excess_conflicting_width_spec_raises():
    p32 = _slot("main_p32")
    p12 = _slot("main_p12", be_window=(198.0, 201.0), linked_to="main_p32",
                linked_offset_range=(1.5, 1.7), area_ratio=0.5,
                share_parent_params=("gl_ratio", "fwhm"),
                fwhm_excess_range=(0.0, 0.5))
    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
                          slots=(p32, p12))
    with pytest.raises(ValueError, match="mutually exclusive"):
        _default_params_from_slots(cand)


def test_excess_area_link_requires_shared_gl_ratio():
    p32 = _slot("main_p32")
    p12 = _slot("main_p12", be_window=(198.0, 201.0), linked_to="main_p32",
                linked_offset_range=(1.5, 1.7), area_ratio=0.5,
                fwhm_excess_range=(0.0, 0.5))
    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
                          slots=(p32, p12))
    with pytest.raises(ValueError, match="gl_ratio"):
        _default_params_from_slots(cand)


def test_negative_or_empty_excess_range_raises():
    p32 = _slot("main_p32")
    for rng in ((-0.1, 0.5), (0.5, 0.5)):
        p12 = _slot("main_p12", be_window=(198.0, 201.0), linked_to="main_p32",
                    linked_offset_range=(1.5, 1.7), area_ratio=0.5,
                    share_parent_params=("gl_ratio",),
                    fwhm_excess_range=rng)
        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
                              slots=(p32, p12))
        with pytest.raises(ValueError, match="non-negative interval"):
            _default_params_from_slots(cand)


def test_fit_candidate_enforces_inequality_exactly():
    """Direct engine-level pin: fitted fwhm12 == fwhm32 + excess, always
    >= fwhm32, and the area ratio equals the requested constant."""
    x, y = _doublet_spectrum(excess=0.35)
    w = 1 / np.sqrt(np.maximum(y, 1))
    cand = _grammar_candidates()["Cl0w_doublet_freewidth"]
    out = fit_candidate(x, y, w, cand)
    assert out.converged
    by_role = {c.slot_role: c for c in out.components}
    p32, p12 = by_role["main_cl2p32"], by_role["main_cl2p12"]
    assert p12.fwhm >= p32.fwhm
    area_ratio = (p12.amplitude * p12.fwhm) / (p32.amplitude * p32.fwhm)
    assert area_ratio == pytest.approx(CL2P_RATIO, rel=1e-9)
