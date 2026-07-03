"""Engine tests for spin-orbit doublet linkage (amplitude ratio + offset).

C 1s never exercises the area-ratio expression path; U 4f and Cl 2p will.
These tests pin it on a synthetic doublet before those modules land.
"""

import numpy as np
import pytest

from autofit.engine import fit_candidate, run_stability_analysis
from autofit.grammar import (
    BackgroundType,
    CandidateModel,
    ComponentSlot,
    LineShape,
)

SPLIT = 1.6
RATIO = 0.5


def _doublet_model(ratio=RATIO, ratio_range=None):
    p32 = ComponentSlot(
        role="main_p32", region="T 2p", phase_id="t",
        be_window=(196.5, 199.0), line_shape=LineShape.PSEUDO_VOIGT,
        fwhm_range=(0.6, 2.2),
    )
    p12 = ComponentSlot(
        role="main_p12", region="T 2p", phase_id="t",
        be_window=(198.0, 201.0), line_shape=LineShape.PSEUDO_VOIGT,
        fwhm_range=(0.6, 2.2),
        linked_to="main_p32", linked_offset_range=(SPLIT - 0.1, SPLIT + 0.1),
        area_ratio=ratio, area_ratio_range=ratio_range,
        fwhm_linked_to="s_main_p32_fwhm",
    )
    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
                          slots=(p32, p12))


def _doublet_spectrum(ratio=RATIO, seed=3):
    rng = np.random.default_rng(seed)
    x = np.arange(194.0, 204.0, 0.05)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = 200 + g(197.9, 8000, 1.1) + g(197.9 + SPLIT, 8000 * ratio, 1.1)
    return x, y + rng.normal(0, 12, len(x))


def test_fixed_ratio_doublet():
    x, y = _doublet_spectrum()
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model()
    out = fit_candidate(x, y, w, model)
    assert out.converged
    by_role = {c.slot_role: c for c in out.components}
    p32, p12 = by_role["main_p32"], by_role["main_p12"]
    assert p32.position == pytest.approx(197.9, abs=0.03)
    assert p12.position - p32.position == pytest.approx(SPLIT, abs=0.1)
    # amplitude expression enforced exactly
    assert p12.amplitude == pytest.approx(p32.amplitude * RATIO, rel=1e-9)
    # linked fwhm shared
    assert p12.fwhm == pytest.approx(p32.fwhm, rel=1e-9)


def test_relaxed_ratio_doublet_recovers_true_ratio():
    true_ratio = 0.65
    x, y = _doublet_spectrum(ratio=true_ratio)
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model(ratio=0.75, ratio_range=(0.55, 0.85))
    out = fit_candidate(x, y, w, model)
    assert out.converged
    by_role = {c.slot_role: c for c in out.components}
    fitted_ratio = by_role["main_p12"].amplitude / by_role["main_p32"].amplitude
    assert fitted_ratio == pytest.approx(true_ratio, abs=0.02)


def test_relaxed_ratio_at_bound_is_boundary_hit():
    # true ratio far below the allowed window → ratio pegs at min → counted
    x, y = _doublet_spectrum(ratio=0.2)
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model(ratio=0.75, ratio_range=(0.55, 0.85))
    out = fit_candidate(x, y, w, model)
    assert out.converged
    assert any(h.startswith("main_p12:ratio@min") for h in out.boundary_hits), \
        out.boundary_hits


def test_doublet_stability_persistence():
    x, y = _doublet_spectrum()
    w = 1 / np.sqrt(np.maximum(y, 1))
    model = _doublet_model()
    primary = fit_candidate(x, y, w, model)
    stab = run_stability_analysis(x, y, w, model, primary,
                                  noise_floor=15.0, n_refits=6, rng_seed=0)
    assert stab.per_slot["main_p32"].persistence == 1.0
    assert stab.per_slot["main_p12"].persistence == 1.0
    assert stab.per_slot["main_p32"].position_mad < 0.02


def test_proposed_slot_is_phase_unassigned():
    """Codex Stage-2 blocker #2: proposals must not inherit region/phase."""
    from autofit.engine import ProposalSpec, _augmented_candidate

    base = _doublet_model()
    spec = ProposalSpec(
        role="proposed_peak_0", detection_windows=["proposal_x"],
        detection_energy=10.0, detection_ratio=6.0,
        center_init=202.0, fwhm_init=1.0, amplitude_init=500.0,
        line_shape=LineShape.PSEUDO_VOIGT,
    )
    aug = _augmented_candidate(base, spec)
    prop = aug.slot_by_role("proposed_peak_0")
    assert prop.region == "unassigned"
    assert prop.phase_id == "unassigned"


def test_absent_normalization_is_region_scoped():
    """Codex Stage-3 finding #2: a huge foreign main in a joint co-fit must
    not dilute another region's satellite below the absent threshold."""
    from autofit.engine import (FitOutcome, ModelStability, SlotStability,
                                _identify_absent_slots)
    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot

    def s(role, region, phase, main=False):
        return ComponentSlot(
            role=role, region=region, phase_id=phase,
            be_window=(0.0, 10.0), line_shape=LineShape.PSEUDO_VOIGT,
            fwhm_range=(0.5, 3.0),
        )

    model = CandidateModel(
        name="joint", background=BackgroundType.SHIRLEY,
        slots=(s("main_u", "U 4f", "UCl4"),
               s("satellite_u", "U 4f", "UCl4"),
               s("main_n", "N 1s", "BN")),
    )
    # U satellite = 5% of the U main (clearly real), but only 0.5% of the
    # joint main total once the huge N main is included.
    areas = {"main_u": 1000.0, "satellite_u": 50.0, "main_n": 9000.0}
    fit = FitOutcome(converged=True, components=[], residual_sum_sq=1.0,
                     weighted_chi_sq=1.0, n_params=9, n_data=100)
    stability = ModelStability(
        per_slot={"satellite_u": SlotStability(
            role="satellite_u", persistence=0.5,  # below threshold
            position_median=None, position_mad=None, fwhm_median=None,
            fwhm_mad=None, amplitude_median=None)},
        orphan_rate=0.0, convergence_rate=1.0)

    absent = _identify_absent_slots(model, stability, areas, fit)
    assert absent == [], (
        "region-scoped normalization must keep the 5%-of-its-own-main "
        f"satellite; got {absent}"
    )
