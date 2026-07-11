"""
Stage-2 completeness recalibration pins (2026-07-10) — the measured
chokepoints from the Step-1 diagnosis (PROGRESS.md "Stage-2 calibration —
STEP-1 DIAGNOSIS"), fixed and pinned:

Chokepoint 2 — F2 proposal eligibility keyed on WINDOW MEMBERSHIP, so a
residual inside a canonical window was blocked even when the current
model had no slot there (measured: ds8 winner B3 lacks a satellite slot;
the 290.76 eV satellite intensity was detected at prom_z 23 and
permanently unreachable).  New rule: a residual cluster is blocked only
by (i) proximity to a FITTED component (0.5 × that component's own
fitted width — transferable units) or (ii) sitting inside a POPULATED
slot's window (that slot owns its window's residuals — this preserves
the distributed-mismatch honesty behavior: a lineshape-mismatch tail
inside an occupied window must surface as flags, never as an invented
tail-fixer peak).

All synthetic, deterministic.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import (  # noqa: E402
    _cand,
    _grammar,
    _linear_bg,
    _noisy,
    _pv,
    _slot,
)

import autofit.engine as eng  # noqa: E402
from autofit.methods import get_method  # noqa: E402
from autofit.methods.base import poisson_like_weights  # noqa: E402

ETA = 0.30
IC_OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": True}


def _fit_base(x, y, grammar):
    w = poisson_like_weights(y)
    res = eng.compare_models(x, y, w, grammar, n_refits=2, rng_seed=0,
                             enable_proposal_pass=False,
                             enable_preseed=False)
    rep = res.reports[0]
    y_fit = rep.primary_fit.lmfit_result.best_fit + rep.primary_fit.background
    return rep, y_fit


def test_proposal_eligible_when_model_lacks_the_slot():
    """A canonical window EXISTS for the region but THIS candidate has no
    slot there: residual intensity inside that window must be proposal-
    eligible (the old window-membership test blocked it — chokepoint 2)."""
    x = np.arange(190.0, 206.0, 0.05)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)
           + _pv(x, 2600.0, 203.0, 1.4, ETA))     # inside the 202-204 window
    y = _noisy(sig + _linear_bg(x), 41)
    grammar = _grammar(
        [_cand("P1", [_slot("main_a", (195.5, 197.5))])],
        windows={"SYN:main_a": (195.5, 197.5),
                 "SYN:satellite": (202.0, 204.0)})   # no P1 slot here
    rep, y_fit = _fit_base(x, y, grammar)
    specs = eng._detect_residual_proposals(
        x, y, y_fit, 1.0, rep.model,
        fitted_components=rep.primary_fit.components)
    assert any(abs(s.center_init - 203.0) < 0.5 for s in specs), (
        "unmodeled intensity inside an unpopulated canonical window must "
        f"be proposal-eligible; got {[round(s.center_init, 2) for s in specs]}")


def test_proposal_blocked_inside_populated_window():
    """Residual structure INSIDE a populated slot's window (a lineshape /
    width mismatch flank) stays proposal-INELIGIBLE: that slot owns its
    window's residuals, and the mismatch must surface as flags, not as an
    invented tail-fixer peak."""
    x = np.arange(190.0, 206.0, 0.05)
    # truth: main + a flank bump INSIDE the main window, 0.9 eV from the
    # main center (outside the 0.5×fwhm proximity zone — only the
    # populated-window rule can block it)
    sig = (_pv(x, 9000.0, 196.3, 1.2, ETA)
           + _pv(x, 1400.0, 197.2, 0.9, ETA))
    y = _noisy(sig + _linear_bg(x), 43)
    grammar = _grammar([_cand("P1", [_slot("main_a", (195.5, 197.5))])],
                       windows={"SYN:main_a": (195.5, 197.5)})
    rep, y_fit = _fit_base(x, y, grammar)
    comp = next(c for c in rep.primary_fit.components
                if c.slot_role == "main_a")
    assert abs(197.2 - comp.position) > 0.5 * comp.fwhm, \
        "test geometry must isolate the populated-window rule"
    specs = eng._detect_residual_proposals(
        x, y, y_fit, 1.0, rep.model,
        fitted_components=rep.primary_fit.components)
    assert not any(abs(s.center_init - 197.2) < 0.4 for s in specs), (
        "in-populated-window residual must stay the slot's job; got "
        f"{[round(s.center_init, 2) for s in specs]}")


def test_proposal_blocked_near_fitted_component():
    """Proximity rule in transferable units: a residual argmax within
    0.5 × the fitted component's own width is that component's business
    (position/width refinement), never a new-peak proposal."""
    x = np.arange(190.0, 206.0, 0.05)
    sig = _pv(x, 9000.0, 196.5, 1.6, ETA)
    y = _noisy(sig + _linear_bg(x), 47)
    grammar = _grammar([_cand("P1", [_slot("main_a", (195.5, 197.5))])])
    rep, y_fit = _fit_base(x, y, grammar)
    comp = next(c for c in rep.primary_fit.components
                if c.slot_role == "main_a")
    # synthetic residual cluster right on the component's flank
    y_fit_deficit = np.array(y_fit)
    flank = comp.position + 0.4 * comp.fwhm
    mask = np.abs(x - flank) < 0.15
    y_fit_deficit[mask] -= 12.0 * np.sqrt(np.maximum(y[mask], 1.0))
    specs = eng._detect_residual_proposals(
        x, y, y_fit_deficit, 1.0, rep.model,
        fitted_components=rep.primary_fit.components)
    assert not any(abs(s.center_init - flank) < 0.3 for s in specs), (
        f"flank residual at {flank:.2f} (0.4×fwhm from the component) must "
        "be blocked by proximity")


def test_e2e_winner_lacks_slot_rescued_by_proposal():
    """End-to-end chokepoint-2 pin: a candidate family WITHOUT a slot for
    real in-window intensity must gain it through the proposal pass, and
    the emitted model must carry the component."""
    x = np.arange(190.0, 206.0, 0.05)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)
           + _pv(x, 2600.0, 203.0, 1.4, ETA))
    y = _noisy(sig + _linear_bg(x), 41)
    grammar = _grammar(
        [_cand("P1", [_slot("main_a", (195.5, 197.5))])],
        windows={"SYN:main_a": (195.5, 197.5),
                 "SYN:satellite": (202.0, 204.0)})
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar,
        options={**IC_OPTS, "enable_preseed": False})
    emitted = [p for p in res.peaks if abs(p["center"] - 203.0) < 0.5]
    assert emitted, (
        "satellite-window intensity missing from the final model: "
        f"{[(p['role'], round(p['center'], 2)) for p in res.peaks]}")


# ── Detection-driven candidate family (Stage-2, chokepoint 5) ──────────────
# Measured motivation: seeding every grammar family with up to 6 slots made
# ALL 29 screen fits blow the 6000-nfev cap on the diagnosis scans (0
# converged -> no survivor).  The detection family carries the full
# detected structure in ONE candidate with detection-quality inits;
# grammar families keep a light seed load.  Built ONLY when detection
# finds structure the grammar cannot express (covered spectra unchanged).

def test_detection_family_built_and_competes():
    """Spectrum with out-of-grammar structure: the sweep must include a
    `D0_detected` candidate whose slots sit at the detected features, all
    region-unassigned and absent-eligible."""
    x = np.arange(186.0, 206.0, 0.05)
    sig = (_pv(x, 40000.0, 191.0, 1.2, ETA)          # OOG dominant
           + _pv(x, 12000.0, 189.9, 1.2, ETA)        # OOG shoulder
           + _pv(x, 9000.0, 196.5, 1.2, ETA))        # in-window main
    y = _noisy(sig + _linear_bg(x), 42)
    grammar = _grammar([_cand("P1", [_slot("main_a", (195.5, 197.5),
                                           fwhm=(0.6, 2.0))])],
                       windows={"SYN:main_a": (195.5, 197.5)})
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar, options=dict(IC_OPTS))
    names = [c["name"] for c in res.analysis["candidates"]]
    names += list(res.analysis.get("non_converged", []))
    assert any(n.startswith("D0_detected") for n in names), names
    d0 = next(c for c in res.analysis["candidates"]
              if c["name"].startswith("D0_detected"))
    assert d0["n_components"] >= 3          # dominant + shoulder + main


def test_no_detection_family_on_covered_spectrum():
    """Grammar-covered spectrum: NO detection family (candidate set byte-
    identical — the F1 no-op rail extends to Stage 2)."""
    x = np.arange(190.0, 205.0, 0.05)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)
           + _pv(x, 4000.0, 199.5, 1.4, ETA))
    y = _noisy(sig + _linear_bg(x), 11)
    grammar = _grammar([_cand("P2", [_slot("main_a", (195.5, 197.5)),
                                     _slot("comp_b", (198.5, 200.5))])],
                       windows={"SYN:main_a": (195.5, 197.5),
                                "SYN:comp_b": (198.5, 200.5)})
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar, options=dict(IC_OPTS))
    names = [c["name"] for c in res.analysis["candidates"]]
    names += list(res.analysis.get("non_converged", []))
    scr = res.analysis.get("screen") or []
    names += [s["name"] for s in scr]
    assert not any(n.startswith("D0_detected") for n in names), names
    assert res.analysis["preseeded_features"] == []


def test_zero_grammar_candidates_run_detection_only():
    """The across-the-periodic-table path (Fe 2p class): a grammar with
    ZERO candidates (structural fallback) must still fit — the detection
    family IS the model space.  All roles unassigned; honesty message
    intact; no hallucinated extras beyond the detected structure."""
    from autofit.grammar import CandidateGrammar

    x = np.arange(700.0, 740.0, 0.1)
    # a broad doublet, Fe-2p-like widths on a coarse grid
    sig = (_pv(x, 30000.0, 711.0, 3.0, ETA)
           + _pv(x, 15000.0, 724.5, 3.4, ETA))
    y = _noisy(sig + _linear_bg(x, 2000.0), 77)
    grammar = CandidateGrammar(
        regions=("Fe 2p",), phase_ids=("sample",), candidates=[],
        diagnostic_windows={}, notes=["synthetic structural fallback"],
        provenance={}, structural_only=("Fe 2p",))
    res = get_method("ic_model_comparison").run(
        x, y, grammar=grammar, options=dict(IC_OPTS))
    assert res.success, res.message
    assert res.diagnostics["winner"].startswith("D0_detected")
    centers = sorted(p["center"] for p in res.peaks)
    assert any(abs(c - 711.0) < 0.8 for c in centers)
    assert any(abs(c - 724.5) < 0.8 for c in centers)
    assert all(p["region"] == "unassigned" for p in res.peaks)
    assert "human review" in res.message
    # widths scale with the detected features (transferable bounds) — the
    # 3 eV mains must NOT be crushed to the 2.0 C1s-ish ordinary cap
    for p in res.peaks:
        assert p["fwhm"] > 2.2, f"broad main crushed: {p}"


# ── Last-resort tier (Stage-2, measured on real low-res Fe 2p) ─────────────
# D0 on Ugly_Fe_2p_2 CONVERGED (chi2r 7.9) but died on plausibility
# (orphan_peaks from cross-refit label instability, min persistence 0.5)
# and the conditional tier deliberately never promotes stability failures
# -> the sweep emitted NOTHING.  For a suggest-a-profile tool an empty
# answer is the worst answer: when NO candidate survives any tier, the
# best CONVERGED model is emitted loudly flagged UNSTABLE — never
# preferred over clean or conditional survivors.

def _real_report():
    from stress_cases import isolated_missing_peak_case
    from autofit.methods.base import poisson_like_weights
    case = isolated_missing_peak_case(seed=71)
    res = eng.compare_models(case.x, case.y, poisson_like_weights(case.y),
                             case.grammar, n_refits=2, rng_seed=0,
                             enable_proposal_pass=False, enable_preseed=False)
    return res.reports[0]


def _destabilized(report):
    import dataclasses
    bad_slots = {role: eng.SlotStability(
        role=role, persistence=0.4, position_median=None, position_mad=None,
        fwhm_median=None, fwhm_mad=None, amplitude_median=None)
        for role in (s.role for s in report.model.slots)}
    stab = dataclasses.replace(report.stability, per_slot=bad_slots,
                               orphan_rate=0.5)
    plaus = eng.PlausibilityFlags(boundary_hits=[], unphysical_widths=[],
                                  orphan_peaks=True)
    return dataclasses.replace(report, stability=stab, plausibility=plaus)


def test_last_resort_tier_emits_best_converged_when_nothing_survives():
    unstable = _destabilized(_real_report())
    res = eng.rank_and_filter([unstable], allow_last_resort=True)
    assert res.survivors, "last resort must emit the best converged model"
    assert res.conditional is True
    assert res.conditional_reason == "unstable_last_resort"


def test_last_resort_never_preferred_over_survivors():
    clean = _real_report()
    unstable = _destabilized(_real_report())
    res = eng.rank_and_filter([clean, unstable], allow_last_resort=True)
    assert res.conditional_reason != "unstable_last_resort"
    assert res.survivors[0].model.name == clean.model.name


# ── PHYSICAL bar: effective width incl. DS+G (Stage-2) ────────────────────

def test_dsg_effective_width_flagged():
    """DS+G's width lives in TWO params (beta = Lorentzian HWHM eV,
    m_gauss = Gaussian FWHM); comp.fwhm carries only m_gauss, so a DS+G
    component could be effectively ~3.3 eV wide while every width check
    saw 1.0 (the goal's 'NO neighbor broadened to hide a missed peak,
    incl. DS+G m').  Effective FWHM via the Olivero–Longbothum Voigt
    approximation must drive the flag."""
    from autofit.grammar import (BackgroundType, CandidateModel,
                                 ComponentSlot, LineShape)
    from autofit.engine import FittedComponent

    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
                         be_window=(199.0, 201.0), line_shape=LineShape.DS_G,
                         fwhm_range=(0.5, 2.0))
    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
                       slots=(slot,))
    fat = FittedComponent(slot_role="main_g", position=200.0, fwhm=1.0,
                          amplitude=1e3, shape_params={"beta": 1.5},
                          line_shape=LineShape.DS_G)
    flags = eng._unphysical_width_flags([fat], m)
    assert flags and "effective" in flags[0], flags
    thin = FittedComponent(slot_role="main_g", position=200.0, fwhm=0.8,
                           amplitude=1e3, shape_params={"beta": 0.2},
                           line_shape=LineShape.DS_G)
    assert eng._unphysical_width_flags([thin], m) == []


def test_detection_slot_absorbing_width_flagged():
    """A detection-family component fitted at ≥70% of its scale-relative
    ceiling (= 1.75× its detected width) is absorbing neighbors — the
    papering-over signature in transferable units.  Below that: clean."""
    from autofit.grammar import (BackgroundType, CandidateModel,
                                 ComponentSlot, LineShape)
    from autofit.engine import FittedComponent

    slot = ComponentSlot(role="detected_peak_0", region="unassigned",
                         phase_id="unassigned", be_window=(199.0, 201.0),
                         line_shape=LineShape.PSEUDO_VOIGT,
                         fwhm_range=(0.5, 5.0))
    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
                       slots=(slot,))
    def comp(w):
        return FittedComponent(slot_role="detected_peak_0", position=200.0,
                               fwhm=w, amplitude=1e3, shape_params={},
                               line_shape=LineShape.PSEUDO_VOIGT)
    assert eng._unphysical_width_flags([comp(4.0)], m), "4.0 ≥ 0.7×5.0"
    assert eng._unphysical_width_flags([comp(3.0)], m) == []


# ── Codex Stage-2 review findings (NO-GO ×2), pinned closed ────────────────

def test_last_resort_never_fires_without_detection_evidence():
    """Codex BLOCKER (both runs; fixed pre-review by a6c9734, pinned here):
    the last-resort tier must NEVER fire unless the caller supplies
    detection evidence — a converged flat-noise grammar fit stays an
    honest no-survivor."""
    unstable = _destabilized(_real_report())
    res = eng.rank_and_filter([unstable])          # default: no evidence
    assert res.survivors == []
    assert res.conditional_reason is None


def test_last_resort_never_preferred_over_conditional_survivor():
    """Codex run B MINOR: pin the CONDITIONAL-survivor interaction, not
    just the clean one — a stable-but-boundary-limited candidate must win
    over an unstable last-resort candidate."""
    import dataclasses
    cond = _real_report()
    cond = dataclasses.replace(
        cond, plausibility=eng.PlausibilityFlags(
            boundary_hits=["main_a:center@min"], unphysical_widths=[],
            orphan_peaks=False))
    unstable = _destabilized(_real_report())
    res = eng.rank_and_filter([cond, unstable], allow_last_resort=True)
    assert res.conditional_reason == "no_clean_survivor"
    assert res.survivors[0].model.name == cond.model.name


def test_asym_gl_effective_width_flagged():
    """Codex run A MAJOR: asym-GL's high-BE side is fwhm×(1+asymmetry)
    (fitting.py convention) — mean effective width fwhm×(1+asym/2) must
    drive the ordinary-cap flag, closing the remaining papering-over
    channel."""
    from autofit.grammar import (BackgroundType, CandidateModel,
                                 ComponentSlot, LineShape)
    from autofit.engine import FittedComponent

    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
                         be_window=(199.0, 201.0), line_shape=LineShape.ASYM_GL,
                         fwhm_range=(0.5, 2.0))
    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
                       slots=(slot,))
    fat = FittedComponent(slot_role="main_g", position=200.0, fwhm=1.7,
                          amplitude=1e3, shape_params={"asymmetry": 0.5},
                          line_shape=LineShape.ASYM_GL)
    flags = eng._unphysical_width_flags([fat], m)   # eff = 1.7×1.25 = 2.13
    assert flags and "effective" in flags[0], flags
    ok = FittedComponent(slot_role="main_g", position=200.0, fwhm=1.5,
                         amplitude=1e3, shape_params={"asymmetry": 0.2},
                         line_shape=LineShape.ASYM_GL)
    assert eng._unphysical_width_flags([ok], m) == []   # eff = 1.65


def test_detection_model_overflow_is_loud():
    """Codex MAJOR (both runs): DETECTION_MODEL_MAX_SLOTS truncation must
    be surfaced — the dropped features are named, never silently gone."""
    x = np.arange(180.0, 220.0, 0.05)
    sig = sum(_pv(x, 30000.0 - 2200.0 * i, 183.0 + 3.4 * i, 1.1, ETA)
              for i in range(10))                   # 10 resolvable peaks
    y = _noisy(sig + _linear_bg(x), 87)
    from autofit.grammar import BackgroundType
    import autofit.engine as e2
    from autofit.candidates import (DETECTION_MODEL_MAX_SLOTS,
                                    build_candidate_pool,
                                    build_detection_candidate)
    dom = e2.detect_out_of_grammar_dominants(x, y, e2._compute_background(
        x, y, BackgroundType.LINEAR), [], {})
    pool = build_candidate_pool(
        x, y, np.zeros_like(x), all_windows=[], labeled_windows={},
        dominant_seeds=[s.payload() for s in dom],
        min_fraction_of_max=0.02, amplitude_snr=5.0, coincidence_ev=0.5,
        max_total_seeds=6, smooth_points=5, fwhm_clip=(0.5, 2.0))
    model, dropped = build_detection_candidate(
        pool, BackgroundType.LINEAR, step_ev=0.05)
    assert model is not None
    assert len(model.slots) == DETECTION_MODEL_MAX_SLOTS
    assert dropped, "overflow must be reported"
    assert all("center_be" in d and "amplitude_net" in d for d in dropped)
