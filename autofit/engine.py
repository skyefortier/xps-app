"""
Model-comparison engine — the fitalg pipeline ported onto main's fitting.py
and generalized to region-agnostic grammars (spec v2.1 §6).

Pipeline per candidate: primary fit → N perturbed refits (stability) →
slot matching by grammar role → absent-slot detection → residual
diagnostics → residual-guided proposal pass → filter-then-rank with BIC*.

Provenance: ported from the public ``xps-app-fitalg`` repo's
``model_comparison.py`` (validated there on HOPG + PET C 1s).  Changes made
in the port, besides symbol renames:

- lineshape layer rebuilt against CURRENT ``fitting.py``: fitalg's
  ``LA_ASYMMETRIC`` (α, β=Lorentzian-HWHM, m_gauss) is main's ``ds_g``; the
  true CasaXPS ``la_casaxps`` (exponent α/β + kernel-points m) is new here,
  as are ``asymmetric_gl`` / ``gaussian`` / ``lorentzian``.
- generic per-slot ``fixed_params`` / ``param_ranges`` replace the
  LA-specific ``fixed_lorentzian_hwhm`` / ``alpha_range`` fields.
- spin-orbit amplitude linkage (``area_ratio`` fixed, or
  ``area_ratio_range`` bounded-relaxed) — needed by doublet regions.
- boundary-hit shape-parameter exclusions are per-lineshape (a width-like
  ``beta`` in DS+G at a bound is a pathology; an exponent-like ``beta`` in
  LACX at a bound is a shape preference).

All numeric thresholds below are **UNVERIFIED tunables** (spec §9 —
sensitivity-test before publication claims); they carry fitalg's defaults.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from lmfit import Model, Parameters
from lmfit.model import ModelResult
from scipy.integrate import trapezoid

from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background

from .candidates import (build_candidate_pool, build_detection_candidate,
                         merge_residual_attempts)

from .grammar import (
    BACKEND_SHAPE,
    BackgroundType,
    CandidateGrammar,
    CandidateModel,
    ComponentSlot,
    LineShape,
)

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# UNVERIFIED tunables (fitalg defaults; spec §9 sensitivity-test items)
# ─────────────────────────────────────────────────────────────────────────────

ABSENT_SLOT_AREA_FRACTION = 0.02
ABSENT_SLOT_PERSISTENCE_THRESHOLD = 0.7
DEFAULT_PERSISTENCE_THRESHOLD = 0.7
DEFAULT_BIC_AMBIGUITY = 2.0
# Decisive-override DOMINANCE rule (Codex cookbook review, blockers 2–3).
# A stable-but-boundary-limited candidate is promoted ahead of the clean
# tier only when ALL of the following hold:
#   (1) it is REFIT with its pegged parameters FIXED at their bounds — the
#       Laplace-style BIC* approximation is invalid at a constraint wall,
#       and the fixed-bound refit gives an honest parameter count;
#   (2) the refit's BIC* beats the best clean candidate's by more than
#       CONDITIONAL_OVERRIDE_DELTA_BIC (10 — the conventional "very strong"
#       threshold, Kass & Raftery, JASA 90 (1995) 773; UNVERIFIED as applied
#       to this heuristic BIC* on processed XPS data — tunable);
#   (3) its reduced χ² is also strictly better (BIC* is never the sole
#       decision axis — spec §6 trust order); and
#   (4) the clean best shows residual-structure flags (autocorrelation or
#       flagged windows) — evidence that it is genuinely mis-fitting, not
#       merely losing a scalar comparison.
# The clean survivors are KEPT as ranked alternatives after the promoted
# candidate; the result carries conditional_reason='decisive_override'.
# Without any override, a clean-but-terrible fit masks a decisively better
# fit that merely brushes a constraint wall (observed on the U 4f + N 1s
# co-fit: clean χ²ᵣ 38 vs boundary-limited χ²ᵣ 7).
CONDITIONAL_OVERRIDE_DELTA_BIC = 10.0

PROPOSAL_WINDOW_WIDTH = 0.5
PROPOSAL_WINDOW_STRIDE = 0.25
PROPOSAL_FLAG_RATIO = 5.0
PROPOSAL_MERGE_BE = 1.0
PROPOSAL_FWHM_MIN = 0.5

# Relative χ² tolerance for counting multi-start fits as landing in the SAME
# basin as the best minimum (best_basin_support) — reporting-only honesty
# diagnostic, never a ranking input.  UNVERIFIED tunable.
BASIN_SUPPORT_RTOL = 1e-3
# Physical FWHM ceiling for an ORDINARY component — one with no known-broad
# justification.  Ordinary C 1s core lines sit at ≲2 eV FWHM (Biesinger,
# Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman 2020); wider is
# defensible ONLY for classes KNOWN to be broad (π→π* and other satellites,
# plasmon/loss features, or a literature-justified case).  This is the
# engine-wide default cap for REGION-UNASSIGNED components — F1 pre-seeded
# out-of-grammar slots and F2/F3 residual proposals — which by construction
# have no region module vouching for a wider physical width.  Region grammar
# slots keep their own cited ranges (C 1s satellite 5.5, U 4f mains 3.5,
# B 1s 2.5, …); those declared maxima ABOVE this ceiling mark a slot as
# grammar-sanctioned-broad and exempt it from the unphysical-width flag.  A
# proposed/pre-seeded peak that PEGS this cap (wants wider than physical with
# no known-broad justification) is NOT silently widened: the fit is held at
# the physical limit and the result is flagged (unphysical_widths →
# conditional/low-confidence), per the fit-quality rail "a defensible fit
# with physical widths beats a lower χ² bought with a fat peak".  UNVERIFIED
# numeric bound (a cap, not a target).
FWHM_MAX_ORDINARY_EV = 2.0
# The proposal/pre-seed upper FWHM bound IS the ordinary physical cap (was a
# looser 3.0 that let residual proposals grow to fat, physically indefensible
# widths — e.g. a real-data 281 eV feature fitting at 3.0 eV).
PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV
PROPOSED_PEAK_SHAPE = LineShape.PSEUDO_VOIGT
PROPOSAL_GRAMMAR_SEPARATION_FACTOR = 0.5
PROPOSAL_DELTABIC_THRESHOLD = 2.0
PROPOSAL_PERSISTENCE_THRESHOLD = ABSENT_SLOT_PERSISTENCE_THRESHOLD
PROPOSAL_AMPLITUDE_SNR = 5.0
# Unit F2 (2026-07-07): raised 1 → 3 and made ITERATIVE — after an accepted
# proposal, detection re-runs on the AUGMENTED model's residual and another
# proposal may be accepted (same gates each round: SNR, ΔBIC*, persistence,
# boundary cleanliness; same per-candidate wall budget).  Measured
# motivation (PROGRESS.md diagnosis, cause c): with the old single-accept
# break, two missing species (the real 279/281 eV pair, cluster-merged into
# one detection) could never both be modeled — the second stayed a +65σ
# residual.  fitalg's Iteration B was already capped/timeout-guarded; this
# keeps those guards and bounds the rounds.  UNVERIFIED tunable.
PROPOSAL_MAX_PER_CANDIDATE = 3
PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE = 3
# Whole ITERATIVE proposal pass per candidate (all F2 rounds share it).
# Raised 30 → 60 with F2: the pass may now legitimately do up to
# PROPOSAL_MAX_PER_CANDIDATE accepted rounds of (augmented fit + stability).
# UNVERIFIED tunable.
PROPOSAL_CANDIDATE_TIMEOUT_SEC = 60.0
# One augmented-model stability pass inside the proposal pass.  Replaces the
# old min(budget, CANDIDATE_TIMEOUT_SEC) clamp, whose 25 s ceiling cut the
# n_refits=4 stability of a slow augmented model to 3 attempts and QUANTIZED
# the persistence gate below its threshold — measured on the real C 1s
# motivating case (PROGRESS.md diagnosis follow-up): a ΔBIC* −86 proposal
# with no boundary hits was rejected at persistence 2/3 = 0.67 < 0.70 purely
# because the 4th refit never ran.  35 s fits n_refits=4 at the measured
# ~7-8 s worst-case per refit on 191-point real data.  UNVERIFIED tunable.
PROPOSAL_STABILITY_TIMEOUT_SEC = 35.0
# Minimum budget (s) that must remain before an augmented-model FIT is
# started inside the proposal pass.  A single fit_candidate at
# FIT_CANDIDATE_MAX_NFEV runs ~10-12 s worst-case on 191-point data with no
# internal wall clock, so starting one with less than this left would
# overrun TOTAL_ANALYSIS_TIMEOUT_SEC — and hence the gunicorn --timeout
# (Codex c1s-fix review, run B MAJOR).  A proposal attempt that cannot fit
# this budget fast-rejects with 'insufficient_budget'.  UNVERIFIED tunable.
PROPOSAL_MIN_FIT_BUDGET_SEC = 15.0

# See fit_candidate() docstring: deterministic per-call ceiling on lmfit's
# own effort, replacing its effectively-unbounded default.
FIT_CANDIDATE_MAX_NFEV = 18000
WARM_RESTART_MAX_NFEV = 2000     # single retry budget for a failed-but-
                                 # finite fit (measured need: ~33 evals;
                                 # generous headroom, still bounded)

# Wall-clock ceiling on ONE candidate's entire primary-fit + stability-refit
# pass (compare_models -> run_stability_analysis). Mirrors
# PROPOSAL_CANDIDATE_TIMEOUT_SEC's existing per-candidate budget for the
# later residual-proposal pass: a candidate that blows this budget stops
# taking further stability refits rather than consuming the rest of the
# request's time. FIT_CANDIDATE_MAX_NFEV already bounds any single call to
# roughly 10-12s on this pipeline's DS+G cost profile, so this allows a
# couple of such calls (primary + 1-2 refits) before cutting the rest.
CANDIDATE_TIMEOUT_SEC = 25.0

# Wall-clock ceiling on the ENTIRE compare_models sweep over all candidates
# in the grammar. Per-candidate budgets (CANDIDATE_TIMEOUT_SEC,
# PROPOSAL_CANDIDATE_TIMEOUT_SEC) bound any one candidate but not their sum
# — a 29-candidate grammar at ~7s/candidate for ordinary (non-degenerate)
# fits already runs ~3-4 minutes, and several candidates hitting the
# DS+G-style degenerate corner push that further. Checked once per outer
# loop iteration (compare_models): once exceeded, remaining candidates are
# skipped and the sweep returns best-so-far, ranked normally, with
# ComparisonResult.analysis_truncated=True — an honest partial result
# instead of a request timeout. Deliberately below the gunicorn dev
# --timeout so this truncation path always gets to run and respond before
# the worker is aborted (see DEPLOY.md / dev gunicorn --timeout).
TOTAL_ANALYSIS_TIMEOUT_SEC = 240.0
PROPOSAL_ENDPOINT_WARNING_BE = 1.0
PROPOSAL_COINCIDENCE_BE = 0.5

# Component treated as asymmetric during shape-aware slot disambiguation.
ALPHA_SYMMETRY_THRESHOLD = 0.01      # DS / DS+G α, asym-GL asymmetry
LACX_EXPONENT_ASYMMETRY = 0.02       # |α − β| for true CasaXPS LA

# ── Pre-fit out-of-grammar dominant seeding (unit F1, 2026-07-07) ──────────
# Measured motivation (PROGRESS.md "Real multi-environment C 1s — MEASURED
# DIAGNOSIS"): on real low-BE-dominant multi-environment C 1s spectra the
# dominant data feature lies OUTSIDE every grammar window, so every
# candidate faces an unfittable 40k-count residual — fits either burn
# FIT_CANDIDATE_MAX_NFEV without converging or pin their mains at window
# floors (χ²ᵣ ~656), and the post-fit proposal pass can only patch ONE
# missing feature after the damage is done.  The pre-seed pass detects
# prominent smoothed local maxima of the background-subtracted DATA that no
# grammar/diagnostic window can express and augments every candidate with
# absent-eligible, region-`unassigned` slots BEFORE fitting — the proposal
# pass's honesty contract (assignment of an out-of-grammar feature is human
# adjudication, never window inheritance), moved ahead of the fit so the
# optimization landscape is sane.  Detection is data-driven; it fires only
# when such a feature exists, so grammars whose windows cover the data are
# byte-identical (pinned).  All gates are UNVERIFIED engine tunables
# (surfaced per-feature in the result payload):
PRESEED_MIN_FRACTION_OF_MAX = 0.25   # dominance gate: smoothed net height ≥
                                     # this fraction of the global smoothed
                                     # net max (weak features stay
                                     # proposal-pass territory)
PRESEED_AMPLITUDE_SNR = PROPOSAL_AMPLITUDE_SNR   # same detection-floor SNR
PRESEED_SMOOTH_POINTS = 5            # moving-average width for maxima search
PRESEED_MAX = 2                      # most dominants seeded per sweep
PRESEED_MIN_SEPARATION_BE = 1.0      # between two accepted seeds (eV)

# ── Stage-2 curvature-seed operating point (recalibration, 2026-07-10) ────
# The Step-1 diagnosis measured the old operating point (dominance fraction
# 0.25, combined cap 2, window+margin blocking) discarding expert-modeled
# species detected at prom_z 8.5-273.  For a suggest-a-profile tool a
# MISSED resolvable shoulder costs more than a spurious candidate the
# selection layer prunes (goal ruling): curvature seeds are gated by the
# noise wall (prom_z) + detection-floor SNR, with only a TRIVIA floor on
# relative height — expert practice models discrete species down to ~5-8%
# of the window max (measured ds8 reference); below ~2% the residual pass
# remains the honest channel.  Both UNVERIFIED tunables, surfaced in the
# pool payload; selection (absent-slot / persistence / BIC*) prunes.
CURVATURE_SEED_MIN_FRACTION = 0.02   # trivia floor (was the 0.25 dominance
                                     # gate — that gate stays for the F1
                                     # dominant channel only)
SEED_MAX_TOTAL = 6                   # dominant + curvature seeds combined
                                     # (was 2; ds7/Scan_1-class spectra
                                     # carry 5-6 real detected species)
DETECTION_WIDTH_ABSORB_FRACTION = 0.7  # detection-slot papering-over flag:
                                       # fitted width ≥ this × the slot's
                                       # scale-relative ceiling (2.5× the
                                       # detected width) ⇒ ≥1.75× detected —
                                       # absorbing a neighbor.  UNVERIFIED.
GRAMMAR_AUGMENT_MAX_SEEDS = 3        # of those, at most this many augment
                                     # each GRAMMAR family (measured: the
                                     # full set made all 29 screens blow
                                     # the nfev cap); the detection family
                                     # carries the full structure instead

# ── Two-phase sweep: screen → stabilize (unit F3, 2026-07-07) ──────────────
# Measured motivation (PROGRESS.md diagnosis, cause a): a 29-candidate C 1s
# grammar at 25 s/candidate stability budgets + a 30-60 s proposal pass can
# never finish inside TOTAL_ANALYSIS_TIMEOUT_SEC (240 s, deliberately below
# the gunicorn --timeout 300) — the real spectra truncated at 8/29 with the
# expert-structure MG family (candidates #21-24) never evaluated.  When the
# candidate set is larger than SCREEN_TOP_K, compare_models first fits EVERY
# candidate once (primary fit only, SCREEN_MAX_NFEV effort cap), ranks the
# converged screens by BIC, and runs the full pipeline (stability, proposal
# pass, absent slots) ONLY for the top SCREEN_TOP_K — reusing each screen
# fit as that candidate's primary, so no work repeats.  Candidates screened
# out are reported honestly (analysis `screen` record: every candidate's
# screen BIC / non-convergence, nothing silent) and can never become
# survivors — the same contract as truncation, but deterministic and
# best-candidates-first instead of grammar-order-first.  Sweeps of
# ≤ SCREEN_TOP_K candidates (every existing gate/battery/stress case) take
# the classic single-phase path unchanged.  Both UNVERIFIED tunables.
SCREEN_MAX_NFEV = 6000     # measured: converging primaries on real 191-pt
                           # C 1s data use 3-5k evals; hopeless landscapes
                           # burn ≥ 18k without converging
SCREEN_TOP_K = 6
# The screen may spend at most this fraction of TOTAL_ANALYSIS_TIMEOUT_SEC —
# the deep phase must always retain budget, else a very large (joint) grammar
# could burn the whole sweep screening and deep-evaluate NOTHING.
SCREEN_BUDGET_FRACTION = 0.6


def _slot_prefix(role: str) -> str:
    """Slot role → lmfit parameter-name prefix (must match grammar._slot_param_prefix)."""
    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"


# ─────────────────────────────────────────────────────────────────────────────
# Background
# ─────────────────────────────────────────────────────────────────────────────

def _compute_background(
    x: np.ndarray,
    y: np.ndarray,
    bg: BackgroundType,
    endpoint_avg: int = 1,
) -> np.ndarray:
    """Background for the autofit path.

    ``endpoint_avg`` mirrors the manual /api/fit knob of the same name
    (audit F3, 2026-07-17). Every background here now takes ``n_avg``
    directly rather than requiring the caller to pre-average the array via
    _apply_endpoint_averaging — which is exactly what this function forgot
    to do, leaving Find Peaks unable to express an endpoint_avg the manual
    path honours. Default 1 (raw endpoints) matches both the previous
    behaviour of this function and app.py's own default, so wiring alone
    changes nothing.
    """
    if bg is BackgroundType.SHIRLEY:
        return shirley_background(x, y, n_avg=endpoint_avg)
    if bg is BackgroundType.SMART:
        return smart_background(x, y, n_avg=endpoint_avg)
    if bg is BackgroundType.SMART_EXP:
        from fitting import smart_experimental_background
        return smart_experimental_background(x, y, n_avg=endpoint_avg)
    if bg is BackgroundType.LINEAR:
        return linear_background(x, y)
    if bg is BackgroundType.TOUGAARD:
        from fitting import tougaard_background
        return tougaard_background(x, y, n_avg=endpoint_avg)
    raise ValueError(f"Unknown background type: {bg}")


# ─────────────────────────────────────────────────────────────────────────────
# lmfit model construction
# ─────────────────────────────────────────────────────────────────────────────

def _build_composite_model(model: CandidateModel) -> Model:
    composite: Model | None = None
    for slot in model.slots:
        shape_name = BACKEND_SHAPE[slot.line_shape]
        if shape_name not in _SHAPE_FUNCS:
            raise RuntimeError(
                f"Shape {shape_name!r} not registered in fitting._SHAPE_FUNCS"
            )
        sub = Model(_SHAPE_FUNCS[shape_name], prefix=_slot_prefix(slot.role))
        composite = sub if composite is None else composite + sub
    if composite is None:
        raise ValueError("CandidateModel has no slots")
    return composite


def _peak_estimate_in_window(
    x: np.ndarray, y_net: np.ndarray, window: tuple[float, float]
) -> float:
    mask = (x >= window[0]) & (x <= window[1])
    if mask.any():
        return max(float(np.max(y_net[mask])), 1.0)
    return max(float(np.max(y_net)) * 0.1, 1.0)


# Default (init, lo, hi) for each shape's extra parameters.  Slot-level
# fixed_params / param_ranges override these.
_SHAPE_PARAM_DEFAULTS: dict[LineShape, list[tuple[str, float, float, float]]] = {
    LineShape.GAUSSIAN: [],
    LineShape.LORENTZIAN: [],
    LineShape.PSEUDO_VOIGT: [("gl_ratio", 0.30, 0.0, 1.0)],
    LineShape.ASYM_GL: [("gl_ratio", 0.30, 0.0, 1.0), ("asymmetry", 0.10, 0.0, 1.0)],
    LineShape.DS: [("alpha", 0.10, 0.0, 0.5), ("gamma_asym", 0.0, 0.0, 1.0)],
    # DS+G: fitalg convention — slot.fwhm_range bounds m_gauss (the Gaussian
    # FWHM width knob); beta is the DS Lorentzian HWHM in eV.
    LineShape.DS_G: [("alpha", 0.10, 0.0, 0.49), ("beta", 0.30, 0.05, 2.0)],
    LineShape.LACX: [("alpha", 1.0, 0.1, 5.0), ("beta", 1.0, 0.1, 5.0),
                     ("m", 50.0, 0.0, 499.0)],
}

# Which parameter carries the slot's fwhm_range for each shape.
def _width_param(shape: LineShape) -> str:
    return "m_gauss" if shape is LineShape.DS_G else "fwhm"


def _add_shape_params(
    p: Parameters, prefix: str, slot: ComponentSlot, fwhm_init: float,
    parent_prefix: Optional[str] = None,
) -> None:
    """Width + shape-specific parameters for one slot, with bounds/overrides."""
    flo, fhi = slot.fwhm_range
    fixed = dict(slot.fixed_params)
    ranges = dict(slot.param_ranges)
    shared = set(slot.share_parent_params)
    if shared and parent_prefix is None:
        raise ValueError(
            f"slot {slot.role!r} declares share_parent_params but has no "
            "linked parent"
        )

    # Width parameter (fwhm, or m_gauss for DS+G)
    wname = _width_param(slot.line_shape)
    if slot.fwhm_excess_range is not None:
        # width-inequality linkage: width = parent width + free excess >= 0
        # (Coster-Kronig doublet broadening — grammar.ComponentSlot docs)
        if parent_prefix is None:
            raise ValueError(
                f"slot {slot.role!r} declares fwhm_excess_range but has no "
                "linked parent"
            )
        if wname in shared or wname in fixed or slot.fwhm_linked_to is not None:
            raise ValueError(
                f"slot {slot.role!r}: fwhm_excess_range is mutually exclusive "
                "with sharing/fixing/expression-linking the width"
            )
        elo, ehi = slot.fwhm_excess_range
        if not (0.0 <= elo < ehi):
            raise ValueError(
                f"slot {slot.role!r}: fwhm_excess_range must be a "
                f"non-negative interval, got {slot.fwhm_excess_range}"
            )
        p.add(f"{prefix}fwhm_excess", value=0.5 * (elo + ehi), min=elo, max=ehi)
        p.add(f"{prefix}{wname}", value=0.0,
              expr=f"{parent_prefix}{wname} + {prefix}fwhm_excess")
    elif wname in shared:
        p.add(f"{prefix}{wname}", value=0.0, expr=f"{parent_prefix}{wname}")
    elif wname in fixed:
        p.add(f"{prefix}{wname}", value=float(fixed[wname]), vary=False)
    elif slot.fwhm_linked_to is not None:
        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, flo, fhi)),
              expr=slot.fwhm_linked_to)
    else:
        wlo, whi = ranges.get(wname, (flo, fhi))
        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, wlo, whi)),
              min=wlo, max=whi)

    for name, init, lo, hi in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
        if name in shared:
            p.add(f"{prefix}{name}", value=0.0, expr=f"{parent_prefix}{name}")
            continue
        if name in fixed:
            p.add(f"{prefix}{name}", value=float(fixed[name]), vary=False)
            continue
        plo, phi = ranges.get(name, (lo, hi))
        p.add(f"{prefix}{name}", value=float(np.clip(init, plo, phi)), min=plo, max=phi)


def _full_window_bound_overrides(
    model: CandidateModel, x: Optional[np.ndarray],
) -> dict[str, tuple[float, float]]:
    """Opt-in "fit the entire window" (unit 1, 2026-07-13): per-slot center
    BOUND overrides — never the starting guess or amplitude estimate,
    both of which stay anchored to the slot's own ``be_window`` (see
    callers below). Branches on how EACH slot was solved, not on whether
    the region as a whole has curated grammar:

    - ``region == "unassigned"`` (a detection/structural-fallback slot —
      Fe 2p, an out-of-grammar preseed) has no cited per-component window
      to preserve: widens fully to the ROI on both sides.
    - Any other (curated, chemically-anchored) slot widens ONLY the outer
      envelope — the lowest-BE slot's lower bound and the highest-BE
      slot's upper bound move to the ROI edges; every interior slot (and
      the untouched side of an outer slot) keeps its literature window
      exactly, so one chemical state can never wander into a
      neighboring one's territory. A model with a single curated primary
      slot has no interior to protect, so it widens on both sides.

    Linked slots (spin-orbit partners, satellites) are never included —
    their offset from the parent is a cited physical splitting, entirely
    unrelated to ROI cropping.
    """
    if x is None or len(x) == 0:
        return {}
    roi_lo, roi_hi = float(np.min(x)), float(np.max(x))
    primary = [s for s in model.slots if s.linked_to is None]
    overrides: dict[str, tuple[float, float]] = {
        s.role: (roi_lo, roi_hi) for s in primary if s.region == "unassigned"
    }
    curated = [s for s in primary if s.region != "unassigned"]
    if curated:
        lo_role = min(curated, key=lambda s: s.be_window[0]).role
        hi_role = max(curated, key=lambda s: s.be_window[1]).role
        for s in curated:
            # min()/max() against the ORIGINAL bound (never a bare ROI edge)
            # so this can only ever widen, never narrow or invert a bound —
            # a ROI that doesn't fully contain the slot's own literature
            # window (Codex-caught: e.g. ROI 287-300 vs a slot window
            # (284, 285)) must leave that side exactly as it was, not
            # produce an inverted (min > max) or narrowed bound.
            lo = min(s.be_window[0], roi_lo) if s.role == lo_role else s.be_window[0]
            hi = max(s.be_window[1], roi_hi) if s.role == hi_role else s.be_window[1]
            overrides[s.role] = (lo, hi)
    return overrides


def _default_params_from_slots(
    model: CandidateModel,
    x: Optional[np.ndarray] = None,
    y_net: Optional[np.ndarray] = None,
    fit_full_window: bool = False,
) -> Parameters:
    """Slot midpoints as starting values, slot bounds as hard constraints.

    ``fit_full_window`` (default False — every existing caller's behavior
    is unchanged unless it opts in) relaxes the primary-slot CENTER bound
    per ``_full_window_bound_overrides``; the starting guess and the
    amplitude-estimate window always stay anchored to the slot's own
    ``be_window``, so relaxing the bound never changes where the search
    starts, only how far it may wander.
    """
    p = Parameters()

    for name, lo_b, hi_b in model.shared_fwhm_params:
        p.add(name, value=0.5 * (lo_b + hi_b), min=lo_b, max=hi_b)

    if y_net is not None and len(y_net) > 0:
        y_peak = max(float(np.max(y_net)), 1.0)
    else:
        y_peak = 1.0e5

    def _amp_bounds(window: tuple[float, float]) -> tuple[float, float]:
        if x is not None and y_net is not None:
            init = _peak_estimate_in_window(x, y_net, window)
            return init, max(2.0 * y_peak, 10.0 * init, 1.0)
        return 1000.0, 1.0e5

    bound_overrides = (_full_window_bound_overrides(model, x)
                       if fit_full_window else {})

    # Pass 1: primary (non-linked) slots
    for slot in model.slots:
        if slot.linked_to is not None:
            continue
        prefix = _slot_prefix(slot.role)
        cmid = 0.5 * (slot.be_window[0] + slot.be_window[1])
        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
        amp_init, amp_max = _amp_bounds(slot.be_window)
        bound = bound_overrides.get(slot.role, slot.be_window)
        p.add(f"{prefix}center", value=cmid, min=bound[0], max=bound[1])
        p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
        _add_shape_params(p, prefix, slot, fmid)

    # Pass 2: linked slots (satellites, chemically-shifted contaminants,
    # spin-orbit partners) — center via offset expression; amplitude either
    # free (satellite) or ratio-linked (doublet).  Processed in dependency
    # order so a chain (main ← sat7/2 ← sat5/2) resolves: lmfit exprs may
    # not reference parameters that do not exist yet.
    done_roles = {s.role for s in model.slots if s.linked_to is None}
    pending = [s for s in model.slots if s.linked_to is not None]
    ordered: list[ComponentSlot] = []
    while pending:
        ready = [s for s in pending if s.linked_to in done_roles]
        if not ready:
            raise ValueError(
                f"unresolvable linkage chain among {[s.role for s in pending]} "
                "(missing parent or cycle)"
            )
        for s in ready:
            ordered.append(s)
            done_roles.add(s.role)
            pending.remove(s)

    for slot in ordered:
        prefix = _slot_prefix(slot.role)
        parent = model.slot_by_role(slot.linked_to)
        if parent is None:
            raise ValueError(f"Slot {slot.role!r} linked to unknown role {slot.linked_to!r}")
        parent_prefix = _slot_prefix(parent.role)
        offs_lo, offs_hi = slot.linked_offset_range or (0.0, 0.0)
        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])

        if offs_hi > offs_lo:
            p.add(f"{prefix}offset", value=0.5 * (offs_lo + offs_hi),
                  min=offs_lo, max=offs_hi)
            p.add(f"{prefix}center", value=0.0,
                  expr=f"{parent_prefix}center + {prefix}offset")
        else:
            # Degenerate range = fixed offset
            p.add(f"{prefix}center", value=0.0,
                  expr=f"{parent_prefix}center + {offs_lo}")

        # Shape params (incl. the width) BEFORE the amplitude: the width-
        # aware area-ratio expression below references this slot's width.
        _add_shape_params(p, prefix, slot, fmid, parent_prefix=parent_prefix)

        # ``area_ratio`` is an AREA statement (2j+1 statistical intensity).
        # With a shared width, height ratio == area ratio and the plain
        # height link is exact.  Under width-inequality linkage
        # (fwhm_excess_range) the height link must carry the width
        # correction: same-shape peaks have area ∝ amplitude × width (the
        # lineshape factor cancels only when the mixing params are shared —
        # guarded in _add_shape_params/_validate below).
        ratio_expr: Optional[str] = None
        if slot.area_ratio_range is not None:
            rlo, rhi = slot.area_ratio_range
            rinit = slot.area_ratio if slot.area_ratio is not None else 0.5 * (rlo + rhi)
            p.add(f"{prefix}ratio", value=float(np.clip(rinit, rlo, rhi)),
                  min=rlo, max=rhi)
            ratio_expr = f"{prefix}ratio"
        elif slot.area_ratio is not None:
            ratio_expr = repr(float(slot.area_ratio))

        if ratio_expr is None:
            amp_init, amp_max = _amp_bounds(slot.be_window)
            p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
        elif slot.fwhm_excess_range is not None:
            # Area-ratio linkage under independent widths is implemented
            # ONLY for the pseudo-Voigt with a shared mixing parameter —
            # the one case where area ∝ height × width with a cancelling
            # shape factor.  Other shapes (asym-GL asymmetry, DS α/γ,
            # DS+G's m_gauss-only width, LACX α/β/m) do NOT scale that way;
            # a shape-specific area factor is FUTURE WORK, and silently
            # emitting the height×width link there would enforce a wrong
            # area ratio (Codex adjudication-unit review, both runs).
            if parent.line_shape is not slot.line_shape:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range requires the parent to share the "
                    "line shape (area ∝ amplitude × width only holds "
                    "within one shape family)"
                )
            if slot.line_shape is not LineShape.PSEUDO_VOIGT:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range is implemented only for "
                    "PSEUDO_VOIGT (shape-specific area factors for other "
                    "shapes are future work)"
                )
            if "gl_ratio" not in slot.share_parent_params:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range requires gl_ratio in "
                    "share_parent_params (the pseudo-Voigt area factor "
                    "must cancel in the ratio)"
                )
            wname = _width_param(slot.line_shape)
            p.add(f"{prefix}amplitude", value=0.0,
                  expr=(f"{parent_prefix}amplitude * {ratio_expr} * "
                        f"{parent_prefix}{wname} / {prefix}{wname}"))
        else:
            p.add(f"{prefix}amplitude", value=0.0,
                  expr=f"{parent_prefix}amplitude * {ratio_expr}")

    return p


# ─────────────────────────────────────────────────────────────────────────────
# Fit outcome + component extraction
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FittedComponent:
    slot_role: str
    position: float
    fwhm: float          # width-parameter value (m_gauss for DS+G — fitalg convention)
    amplitude: float
    shape_params: dict
    line_shape: Optional[LineShape] = None


@dataclass
class FitOutcome:
    converged: bool
    components: list[FittedComponent]
    residual_sum_sq: float
    weighted_chi_sq: float
    n_params: int
    n_data: int
    lmfit_result: Optional[ModelResult] = None
    background: Optional[np.ndarray] = None
    boundary_hits: list[str] = field(default_factory=list)


def _extract_fitted_components(
    result: ModelResult, model: CandidateModel
) -> list[FittedComponent]:
    out: list[FittedComponent] = []
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        pars = result.params
        try:
            center = float(pars[f"{prefix}center"].value)
            amplitude = float(pars[f"{prefix}amplitude"].value)
            fwhm = float(pars[f"{prefix}{_width_param(slot.line_shape)}"].value)
        except KeyError:
            continue
        shape_params = {}
        for name, _, _, _ in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
            par = pars.get(f"{prefix}{name}")
            if par is not None:
                shape_params[name] = float(par.value)
        if slot.line_shape is LineShape.DS_G:
            shape_params["m_gauss"] = fwhm
        out.append(FittedComponent(
            slot_role=slot.role, position=center, fwhm=fwhm,
            amplitude=amplitude, shape_params=shape_params,
            line_shape=slot.line_shape,
        ))
    return out


# Shape-parameter names allowed to saturate at bounds per lineshape (shape
# preference, not pathology).  Width-like params are NOT excluded.
_BOUNDARY_EXCLUDED: dict[LineShape, frozenset[str]] = {
    LineShape.GAUSSIAN: frozenset(),
    LineShape.LORENTZIAN: frozenset(),
    LineShape.PSEUDO_VOIGT: frozenset({"gl_ratio"}),
    LineShape.ASYM_GL: frozenset({"gl_ratio", "asymmetry"}),
    LineShape.DS: frozenset({"alpha", "gamma_asym"}),
    LineShape.DS_G: frozenset({"alpha"}),          # beta is a WIDTH here — counted
    LineShape.LACX: frozenset({"alpha", "beta"}),  # both are exponents here
}


def _role_for_param(pname: str, role_by_prefix: dict[str, str]) -> Optional[str]:
    for prefix in sorted(role_by_prefix, key=len, reverse=True):
        if pname.startswith(prefix):
            return role_by_prefix[prefix]
    return None


def _detect_boundary_hits(params: Parameters, model: CandidateModel) -> list[str]:
    """Varying params within 1% of a finite bound → 'role:param@min|max'."""
    hits: list[str] = []
    role_by_prefix = {_slot_prefix(s.role): s.role for s in model.slots}
    shape_by_role = {s.role: s.line_shape for s in model.slots}

    for pname, par in params.items():
        if not par.vary:
            continue
        lo, hi = par.min, par.max
        if not (np.isfinite(lo) and np.isfinite(hi)) or hi <= lo:
            continue
        tol = 0.01 * (hi - lo)
        at_min = (par.value - lo) < tol
        at_max = (hi - par.value) < tol
        if not (at_min or at_max):
            continue
        role = _role_for_param(pname, role_by_prefix)
        short = pname[len(_slot_prefix(role)):] if role is not None else pname
        shape = shape_by_role.get(role)
        if shape is not None and short in _BOUNDARY_EXCLUDED.get(shape, frozenset()):
            continue
        # amplitude at min (=0) → component absent: surfaced via stability
        if short == "amplitude" and at_min:
            continue
        # relaxed doublet ratio at a bound is a real constraint violation —
        # counted (it means the data is fighting the physical ratio window).
        hits.append(f"{role or '?'}:{short}@{'min' if at_min else 'max'}")
    return hits


def _proposed_slot_pegs(outcome: FitOutcome, role: str) -> list[str]:
    """Boundary pegs for one proposed slot, using the SAME detector (and the
    same ``_BOUNDARY_EXCLUDED`` shape-endpoint policy) as every grammar slot.

    Shape endpoints (a pure-Gaussian ``gl_ratio``=0, a pure-Lorentzian
    ``gl_ratio``=1) are LEGITIMATE physics, not constraint violations — the
    grammar excludes them from boundary hits, and treating a proposal that
    reaches one as spurious would drop real pure-Gaussian/Lorentzian peaks
    (measured: the two-narrow-peak F2 case regressed to zero accepted
    proposals when shape pegs were rejected).  So the caller tolerates
    ``{role}:fwhm@max`` (the physical-width ceiling doing its job) and any
    shape endpoint, and rejects on a SUBSTANTIVE peg — ``center`` at a window
    edge, ``amplitude`` at a wall, or ``fwhm@min`` (an implausibly narrow
    spike) (Codex fwhm-cap review, run A: the accurate statement of "which
    pegs reject").
    """
    return [h for h in outcome.boundary_hits if h.startswith(f"{role}:")]


def _unphysical_width_flags(
    components: "list[FittedComponent]", model: CandidateModel
) -> list[str]:
    """Fitted components whose width reaches the ordinary physical FWHM
    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.

    A slot whose grammar-declared ``fwhm_range`` maximum EXCEEDS the ordinary
    cap is grammar-sanctioned-broad (C 1s π→π* satellite 5.5, U 4f mains 3.5,
    B 1s 2.5, …) and is EXEMPT — its width is region physics, cited in the
    region module, not an unphysical stretch.  Any other slot — contamination,
    the aliphatic main, and the region-``unassigned`` F1 pre-seed / F2-F3
    proposal slots (all capped AT the ordinary ceiling) — that fits at/above
    the ceiling is flagged: the optimizer wanted a wider (fatter) peak than an
    ordinary component physically has, the cap held it at the limit, and the
    decomposition must be reported low-confidence (routes to the CONDITIONAL
    tier via rank_and_filter) rather than silently accepted.  Region-agnostic:
    the exemption is driven entirely by each slot's own declared range, so no
    region's cited widths are ever mis-flagged.
    """
    ranges = {s.role: s.fwhm_range for s in model.slots}
    flags: list[str] = []
    for c in components:
        rng = ranges.get(c.slot_role)
        if rng is None:
            continue
        declared_lo, declared_hi = rng
        # EFFECTIVE width (Stage-2 PHYSICAL bar): DS+G's width lives in TWO
        # params — beta (Lorentzian HWHM, eV) and m_gauss (Gaussian FWHM;
        # what comp.fwhm carries) — so the checks below must see the
        # convolved width, not the Gaussian part alone (a component could
        # otherwise be ~3+ eV wide while every width check reads 1.0:
        # exactly the 'neighbor broadened to hide a missed peak' channel).
        # Olivero & Longbothum 1977 Voigt-FWHM approximation (0.02%).
        eff_fwhm = c.fwhm
        if c.line_shape is LineShape.DS_G:
            f_l = 2.0 * float(c.shape_params.get("beta", 0.0))
            eff_fwhm = 0.5346 * f_l + np.sqrt(0.2166 * f_l ** 2 + c.fwhm ** 2)
            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and \
                    declared_hi <= FWHM_MAX_ORDINARY_EV:
                flags.append(
                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
                    f"β={c.shape_params.get('beta', 0.0):.2f} + "
                    f"m={c.fwhm:.2f}; no known-broad justification)")
                continue
        elif c.line_shape is LineShape.ASYM_GL:
            # asym-GL broadens its high-BE side to fwhm×(1+asymmetry)
            # (fitting.py convention) — the MEAN effective width
            # fwhm×(1+asym/2) closes the remaining papering-over channel
            # (Codex Stage-2 review, run A MAJOR).
            asym = float(c.shape_params.get("asymmetry", 0.0))
            eff_fwhm = c.fwhm * (1.0 + 0.5 * asym)
            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and \
                    declared_hi <= FWHM_MAX_ORDINARY_EV:
                flags.append(
                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
                    f"fwhm={c.fwhm:.2f}×(1+{asym:.2f}/2); no known-broad "
                    "justification)")
                continue
        # detection-family slots (scale-relative ceilings, usually > the
        # ordinary cap): a component at ≥ DETECTION_WIDTH_ABSORB_FRACTION
        # of its own ceiling (= 1.75× the DETECTED width via the 2.5×
        # ceiling) is absorbing neighboring intensity — the papering-over
        # signature in transferable units.
        if c.slot_role.startswith("detected_peak_"):
            if eff_fwhm >= DETECTION_WIDTH_ABSORB_FRACTION * declared_hi:
                flags.append(
                    f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥"
                    f"{DETECTION_WIDTH_ABSORB_FRACTION:.2f}×ceiling "
                    f"({declared_hi:.2f}eV) — ~1.75× its detected width; "
                    "likely absorbing a neighbor")
            continue
        if declared_hi > FWHM_MAX_ORDINARY_EV:
            continue                       # grammar-sanctioned-broad slot
        # pegging the ordinary ceiling — same 1%-of-range tol as boundary
        # detection, so a component held AT the 2.0 cap is caught
        tol = 0.01 * (declared_hi - declared_lo) if declared_hi > declared_lo else 0.0
        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
            flags.append(
                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
                "ordinary cap (no known-broad justification)")
    return flags


def fit_candidate(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    model: CandidateModel,
    initial_params: Optional[Parameters] = None,
    max_nfev: int = FIT_CANDIDATE_MAX_NFEV,
    fit_full_window: bool = False,
) -> FitOutcome:
    """One fit of ``model`` to (x, y, weights); background subtracted first.

    ``max_nfev`` bounds leastsq's own effort per call. lmfit's default
    (200000*(nvars+1), see lmfit.Minimizer) is effectively unbounded: a
    candidate whose params wander to a valid-but-degenerate corner (e.g.
    DS+G's alpha/beta pinned at their bounds — a shape preference, not a
    param error; see _BOUNDARY_EXCLUDED) produces a landscape leastsq can't
    descend, and it spins for tens of thousands of evaluations without
    terminating. Diagnostic run (2026-07-05, Suggest-peaks hang
    investigation) showed a clean bimodal split: converged fits topped out
    at nfev=14890; non-convergent ones started at nfev=21604. This cap sits
    between the two so lmfit's own AbortFitException (caught internally by
    leastsq(), surfacing as result.success=False) cuts off the latter
    deterministically, without clipping legitimate slow-but-converging fits.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    weights = np.asarray(weights, dtype=float)

    bg = _compute_background(x, y, model.background)
    y_sub = y - bg
    composite = _build_composite_model(model)
    params = initial_params if initial_params is not None else \
        _default_params_from_slots(model, x=x, y_net=y_sub,
                                   fit_full_window=fit_full_window)

    try:
        result = composite.fit(y_sub, params, x=x, weights=weights,
                               method="leastsq", nan_policy="omit",
                               max_nfev=max_nfev)
        if (not result.success and result.chisqr is not None
                and np.isfinite(result.chisqr)):
            # ONE warm restart (Stage-2, measured on the real diagnosis
            # scans): a model whose optimum sits against parameter bounds
            # stalls MINPACK on a flat transformed gradient — it reaches
            # the minimum, then burns the whole nfev budget without
            # satisfying ftol (success=False at a genuinely converged
            # χ²).  Restarting AT the exit point resets leastsq's internal
            # diag scaling and it certifies in tens of evaluations
            # (measured: 6000 nfev burned cold → 33 nfev warm, identical
            # χ²).  Fires ONLY on a failed-but-finite fit, so converging
            # fits are byte-identical; cost is bounded by one
            # WARM_RESTART_MAX_NFEV fit.
            retry = composite.fit(y_sub, result.params.copy(), x=x,
                                  weights=weights, method="leastsq",
                                  nan_policy="omit",
                                  max_nfev=WARM_RESTART_MAX_NFEV)
            if retry.success:
                result = retry
    except Exception as exc:
        log.debug("fit_candidate failed for %s: %s", model.name, exc)
        return FitOutcome(
            converged=False, components=[], residual_sum_sq=float("inf"),
            weighted_chi_sq=float("inf"),
            n_params=len([q for q in params.values() if q.vary]),
            n_data=len(y_sub), lmfit_result=None, background=bg,
        )

    unweighted_r = y_sub - result.best_fit
    return FitOutcome(
        converged=bool(result.success),
        components=_extract_fitted_components(result, model),
        residual_sum_sq=float(np.sum(unweighted_r ** 2)),
        weighted_chi_sq=float(result.chisqr) if result.chisqr is not None else float("inf"),
        n_params=result.nvarys,
        n_data=len(y_sub),
        lmfit_result=result,
        background=bg,
        boundary_hits=_detect_boundary_hits(result.params, model),
    )


def compute_slot_areas(
    model: CandidateModel, primary: FitOutcome, x: np.ndarray
) -> dict[str, float]:
    if primary.lmfit_result is None:
        return {}
    composite = primary.lmfit_result.model
    params = primary.lmfit_result.params
    out: dict[str, float] = {}
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        sub = next((c for c in composite.components if c.prefix == prefix), None)
        if sub is None:
            continue
        out[slot.role] = float(abs(trapezoid(sub.eval(params, x=x), x)))
    return out


def perturb_initial_params(
    model: CandidateModel,
    seed: int,
    position_jitter_eV: float = 0.15,
    fwhm_jitter_frac: float = 0.20,
    amplitude_jitter_frac: float = 0.30,
    x: Optional[np.ndarray] = None,
    y_net: Optional[np.ndarray] = None,
    fit_full_window: bool = False,
) -> Parameters:
    """
    Perturbed starting parameters for a multi-start refit (bounds-clipped).

    Port improvement over fitalg: when (x, y_net) are provided the defaults
    are data-informed — in particular the amplitude UPPER bound scales with
    the spectrum instead of the fixed 1e5 fallback, which silently clamped
    (and systematically failed) stability refits on peaks brighter than 1e5
    counts (e.g. the UCl4-BN N 1s line at ~1.06e5).
    """
    rng = np.random.default_rng(seed)
    params = _default_params_from_slots(model, x=x, y_net=y_net,
                                        fit_full_window=fit_full_window)

    def _clip(par, new_val: float) -> None:
        lo = par.min if np.isfinite(par.min) else -np.inf
        hi = par.max if np.isfinite(par.max) else np.inf
        par.set(value=float(np.clip(new_val, lo, hi)))

    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        if slot.linked_to is None:
            cp = params.get(f"{prefix}center")
            if cp is not None and cp.expr is None:
                _clip(cp, cp.value + rng.normal(0.0, position_jitter_eV))
        else:
            op = params.get(f"{prefix}offset")
            if op is not None:
                _clip(op, op.value + rng.normal(0.0, position_jitter_eV))

        fp = params.get(f"{prefix}{_width_param(slot.line_shape)}")
        if fp is not None and fp.expr is None and fp.vary:
            _clip(fp, fp.value * max(1.0 + rng.normal(0.0, fwhm_jitter_frac), 0.1))

        ap = params.get(f"{prefix}amplitude")
        if ap is not None and ap.expr is None:
            _clip(ap, ap.value * max(1.0 + rng.normal(0.0, amplitude_jitter_frac), 0.1))
    return params


# ─────────────────────────────────────────────────────────────────────────────
# Component ↔ slot matching
# ─────────────────────────────────────────────────────────────────────────────

def _is_asymmetric_component(comp: FittedComponent) -> bool:
    sp = comp.shape_params
    if comp.line_shape in (LineShape.DS, LineShape.DS_G):
        return float(sp.get("alpha", 0.0)) > ALPHA_SYMMETRY_THRESHOLD
    if comp.line_shape is LineShape.ASYM_GL:
        return float(sp.get("asymmetry", 0.0)) > ALPHA_SYMMETRY_THRESHOLD
    if comp.line_shape is LineShape.LACX:
        return abs(float(sp.get("alpha", 1.0)) - float(sp.get("beta", 1.0))) \
            > LACX_EXPONENT_ASYMMETRY
    return False


def _effective_be_window(
    slot: ComponentSlot, components: list[FittedComponent],
    bound_override: Optional[tuple[float, float]] = None,
) -> tuple[float, float]:
    """``bound_override`` (fit_full_window, unit 1 2026-07-13): the SAME
    widened bound the fit itself was built with
    (``_full_window_bound_overrides``) — a primary slot's fitted position
    identity-matching must agree with the bound it was actually allowed
    to search, or a component the widened fit correctly placed outside
    its ORIGINAL literature window becomes an orphan here (Codex-caught:
    tanks stability/persistence, silently rejecting the very component
    this option exists to rescue). Only applies to a primary slot
    (``linked_to is None`` — a linked slot's effective window is always
    the offset-derived one below, entirely unaffected by this option)."""
    if slot.linked_to is None or slot.linked_offset_range is None:
        return bound_override if bound_override is not None else slot.be_window
    parent = next((c for c in components if c.slot_role == slot.linked_to), None)
    if parent is None:
        return slot.be_window
    lo, hi = slot.linked_offset_range
    return (parent.position + lo, parent.position + hi)


def match_components_to_slots(
    components: list[FittedComponent],
    model: CandidateModel,
    noise_floor: float,
    bound_overrides: Optional[dict[str, tuple[float, float]]] = None,
) -> dict[str, Optional[FittedComponent]]:
    """Assign fitted peaks to grammar slots (role + effective window + width).

    ``bound_overrides`` (fit_full_window) — see ``_effective_be_window``.
    """
    slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
    orphans: list[FittedComponent] = []
    asym_shapes = {LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX}

    def _accepts(slot: ComponentSlot, comp: FittedComponent) -> bool:
        lo, hi = _effective_be_window(slot, components,
                                      (bound_overrides or {}).get(slot.role))
        return (lo <= comp.position <= hi
                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
                and comp.amplitude > noise_floor)

    def _window_center(slot: ComponentSlot) -> float:
        # NEVER the widened bound (Codex-caught, round 2): this is a
        # TIE-BREAK reference point ("how close is this component to
        # where this slot expects its peak"), not an acceptance test —
        # widening it would drag the reference point far from the
        # slot's true expected position (e.g. a curated slot's own
        # narrow window widened to a whole ROI), making a neighboring
        # slot's UNWIDENED, much-closer center win the tie-break even
        # when the component sits well inside THIS slot's own original
        # window. Acceptance (_accepts, above) is the only place the
        # widened bound belongs.
        lo, hi = _effective_be_window(slot, components)
        return 0.5 * (lo + hi)

    for comp in components:
        candidate_slots = [s for s in model.slots if _accepts(s, comp)]
        if not candidate_slots:
            orphans.append(FittedComponent(
                slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
                amplitude=comp.amplitude, shape_params=comp.shape_params,
                line_shape=comp.line_shape,
            ))
            continue

        shapes = {s.line_shape for s in candidate_slots}
        if len(shapes) > 1:
            if _is_asymmetric_component(comp):
                preferred = [s for s in candidate_slots if s.line_shape in asym_shapes]
            else:
                preferred = [s for s in candidate_slots if s.line_shape not in asym_shapes]
            if preferred:
                candidate_slots = preferred

        best_slot = min(candidate_slots, key=lambda s: abs(comp.position - _window_center(s)))
        incumbent = slot_map[best_slot.role]
        claimed = FittedComponent(
            slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,
            amplitude=comp.amplitude, shape_params=comp.shape_params,
            line_shape=comp.line_shape,
        )
        if incumbent is None:
            slot_map[best_slot.role] = claimed
        else:
            wc = _window_center(best_slot)
            if abs(comp.position - wc) < abs(incumbent.position - wc):
                orphans.append(incumbent)
                slot_map[best_slot.role] = claimed
            else:
                orphans.append(comp)

    slot_map["__orphans__"] = orphans  # type: ignore[assignment]
    return slot_map


# ─────────────────────────────────────────────────────────────────────────────
# Stability
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SlotStability:
    role: str
    persistence: float
    position_median: Optional[float]
    position_mad: Optional[float]
    fwhm_median: Optional[float]
    fwhm_mad: Optional[float]
    amplitude_median: Optional[float]
    amplitude_mad: Optional[float] = None


@dataclass
class ModelStability:
    per_slot: dict[str, SlotStability]
    orphan_rate: float
    convergence_rate: float
    # Best converged refit found during the multi-start pass (by weighted χ²).
    # Port improvement over fitalg, which always reported the primary fit even
    # when a perturbed refit found a deeper minimum: the driver promotes this
    # outcome when it beats the primary, so the report describes the best
    # minimum FOUND and the stability numbers describe its robustness.
    best_outcome: Optional[FitOutcome] = None
    # How many multi-start fits (refits + primary) landed within
    # BASIN_SUPPORT_RTOL of the best weighted χ² — an honesty diagnostic for
    # the best-minimum promotion (Codex Stage-2 re-review finding #4: a
    # one-off deeper minimum is a different product than a reproducible one).
    # Reporting-only; never used in ranking.
    best_basin_support: int = 0
    # How many of the requested n_refits were actually attempted before the
    # candidate's wall-clock budget (CANDIDATE_TIMEOUT_SEC) ran out. Equal to
    # n_refits unless timed_out is True — used as the honest denominator for
    # persistence/orphan_rate/convergence_rate instead of silently
    # understating them against the full nominal n_refits.
    n_attempted: int = 0
    timed_out: bool = False

    @property
    def min_persistence(self) -> float:
        if not self.per_slot:
            return 0.0
        return min(s.persistence for s in self.per_slot.values())


def run_stability_analysis(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    model: CandidateModel,
    primary_fit: FitOutcome,
    noise_floor: float,
    n_refits: int = 20,
    rng_seed: int = 0,
    fixed_param_values: Optional[dict[str, float]] = None,
    deadline: Optional[float] = None,
    fit_full_window: bool = False,
) -> ModelStability:
    """
    ``deadline`` is an absolute ``time.perf_counter()`` timestamp (set by
    the caller from CANDIDATE_TIMEOUT_SEC) shared across this candidate's
    primary fit + all its refits. Once passed, remaining refits are
    skipped — not run and not counted as failures — so one candidate stuck
    in a slow-but-nfev-capped region can't consume the rest of the request.
    """
    rng = np.random.default_rng(rng_seed)
    pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
    fw: dict[str, list[float]] = {s.role: [] for s in model.slots}
    am: dict[str, list[float]] = {s.role: [] for s in model.slots}
    occupied: dict[str, int] = {s.role: 0 for s in model.slots}
    n_converged = 0
    n_with_orphans = 0
    # Same widened bounds every refit was actually built with (constant
    # across this candidate's whole stability pass) — identity-matching
    # must agree with the bound the fit was allowed to search, or a
    # component correctly placed outside its ORIGINAL window becomes an
    # orphan here, tanking persistence for the very slot this option
    # exists to rescue (Codex-caught, see _effective_be_window).
    bound_overrides = _full_window_bound_overrides(model, x) if fit_full_window else None

    # Data-informed perturbation seeds (see perturb_initial_params): reuse
    # the primary fit's background rather than recomputing per refit.
    bg = primary_fit.background
    y_net = y - bg if bg is not None else None

    best_outcome: Optional[FitOutcome] = None
    refit_chis: list[float] = [float(primary_fit.weighted_chi_sq)]
    n_attempted = 0
    timed_out = False
    for _ in range(n_refits):
        if deadline is not None and time.perf_counter() >= deadline:
            timed_out = True
            log.warning(
                "run_stability_analysis: candidate %s hit its %.0fs budget "
                "after %d/%d refits — remaining refits skipped",
                model.name, CANDIDATE_TIMEOUT_SEC, n_attempted, n_refits,
            )
            break
        n_attempted += 1
        seed = int(rng.integers(0, 2**31 - 1))
        init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
                                      fit_full_window=fit_full_window)
        if fixed_param_values:
            # bound-fixed refit stability: the constrained parameters stay
            # fixed at their bounds in every multi-start refit
            for pname, val in fixed_param_values.items():
                if pname in init:
                    init[pname].set(value=float(val), vary=False)
        outcome = fit_candidate(x, y, weights, model, initial_params=init)
        if not outcome.converged:
            continue
        n_converged += 1
        refit_chis.append(float(outcome.weighted_chi_sq))
        if best_outcome is None or outcome.weighted_chi_sq < best_outcome.weighted_chi_sq:
            best_outcome = outcome
        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
                                            bound_overrides=bound_overrides)
        if slot_map.pop("__orphans__", []):
            n_with_orphans += 1
        for role, comp in slot_map.items():
            if comp is None:
                continue
            occupied[role] += 1
            pos[role].append(comp.position)
            fw[role].append(comp.fwhm)
            am[role].append(comp.amplitude)

    def _med(v):  # median or None
        return float(np.median(v)) if v else None

    def _mad(v):
        if not v:
            return None
        arr = np.asarray(v)
        return float(np.median(np.abs(arr - np.median(arr))))

    per_slot = {
        role: SlotStability(
            role=role,
            persistence=occupied[role] / max(n_attempted, 1),
            position_median=_med(pos[role]), position_mad=_mad(pos[role]),
            fwhm_median=_med(fw[role]), fwhm_mad=_mad(fw[role]),
            amplitude_median=_med(am[role]), amplitude_mad=_mad(am[role]),
        )
        for role in occupied
    }
    best_chi = min(refit_chis)
    basin_support = sum(1 for c in refit_chis
                        if c <= best_chi * (1.0 + BASIN_SUPPORT_RTOL))
    return ModelStability(
        per_slot=per_slot,
        orphan_rate=n_with_orphans / max(n_attempted, 1),
        convergence_rate=n_converged / max(n_attempted, 1),
        best_outcome=best_outcome,
        best_basin_support=basin_support,
        n_attempted=n_attempted,
        timed_out=timed_out,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Absent slots
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AbsentSlotReport:
    role: str
    persistence: float
    fitted_area: float
    main_area: float
    area_fraction: float
    threshold: float
    removed_n_params: int


def _count_slot_free_params(slot: ComponentSlot, primary: FitOutcome) -> int:
    if primary.lmfit_result is None:
        return 0
    prefix = _slot_prefix(slot.role)
    return sum(1 for pname, par in primary.lmfit_result.params.items()
               if pname.startswith(prefix) and par.vary)


def _is_main_role(role: str) -> bool:
    """Main-slot convention: bare role or region-prefixed role starts 'main'."""
    return role.split("__")[-1].startswith("main")


def _linked_groups(model: CandidateModel) -> list[list[ComponentSlot]]:
    """
    Connected components of non-main slots over ``linked_to`` edges (edges
    touching a main slot do not bind — mains are never absent-eligible, so a
    satellite linked to a main is its own group; a satellite DOUBLET
    (sat5/2 → sat7/2) is one group).
    """
    non_main = [s for s in model.slots if not _is_main_role(s.role)]
    roles = {s.role for s in non_main}
    parent_of = {s.role: s.linked_to for s in non_main
                 if s.linked_to is not None and s.linked_to in roles}

    def root(role: str) -> str:
        while role in parent_of:
            role = parent_of[role]
        return role

    groups: dict[str, list[ComponentSlot]] = {}
    for s in non_main:
        groups.setdefault(root(s.role), []).append(s)
    return list(groups.values())


def _identify_absent_slots(
    model: CandidateModel,
    stability: ModelStability,
    slot_areas: dict[str, float],
    primary: FitOutcome,
    persistence_threshold: float = ABSENT_SLOT_PERSISTENCE_THRESHOLD,
    area_fraction_threshold: float = ABSENT_SLOT_AREA_FRACTION,
) -> list[AbsentSlotReport]:
    """
    Absent classification is ATOMIC per linked group: a slot whose amplitude
    or shape is expression-tied to a partner cannot be absent while the
    partner is present (a spin-orbit satellite pair is one physical feature).
    Every member must individually meet the persistence + area criteria for
    the group to be classified absent.

    The area fraction is normalized against the mains of the SLOT'S OWN
    (region, phase) when any exist — in a joint co-fit, normalizing against
    the global main area would let a huge foreign main (e.g. the BN N 1s
    line in a U 4f + N 1s window) dilute a real satellite of the smaller
    element below the threshold (Codex Stage-3 finding #2).  Falls back to
    the global main area for slots without same-scope mains (e.g. proposals,
    which are region-unassigned).
    """
    global_main_area = sum(a for role, a in slot_areas.items() if _is_main_role(role))
    if global_main_area <= 0:
        return []

    scoped_main_area: dict[tuple[str, str], float] = {}
    for s in model.slots:
        if _is_main_role(s.role):
            key = (s.region, s.phase_id)
            scoped_main_area[key] = scoped_main_area.get(key, 0.0) \
                + float(slot_areas.get(s.role, 0.0))

    def _member_report(slot: ComponentSlot) -> Optional[AbsentSlotReport]:
        sstab = stability.per_slot.get(slot.role)
        if sstab is None or sstab.persistence >= persistence_threshold:
            return None
        main_area = scoped_main_area.get((slot.region, slot.phase_id), 0.0)
        if main_area <= 0:
            main_area = global_main_area
        area = float(slot_areas.get(slot.role, 0.0))
        frac = area / main_area
        if frac >= area_fraction_threshold:
            return None
        return AbsentSlotReport(
            role=slot.role, persistence=sstab.persistence, fitted_area=area,
            main_area=main_area, area_fraction=frac,
            threshold=area_fraction_threshold,
            removed_n_params=_count_slot_free_params(slot, primary),
        )

    absent: list[AbsentSlotReport] = []
    for group in _linked_groups(model):
        reports = [_member_report(s) for s in group]
        if all(r is not None for r in reports):
            absent.extend(reports)  # type: ignore[arg-type]
    return absent


# ─────────────────────────────────────────────────────────────────────────────
# Residual diagnostics
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ResidualDiagnostics:
    autocorrelation_lag1: float
    autocorr_flag: bool
    window_energies: dict[str, float]
    flagged_windows: list[str]


def compute_residual_diagnostics(
    x: np.ndarray,
    y: np.ndarray,
    y_fit: np.ndarray,
    noise_floor: float,
    diagnostic_windows: dict[str, tuple[float, float]],
    window_flag_ratio: float = 2.0,
) -> ResidualDiagnostics:
    r = y - y_fit
    sigma = np.sqrt(np.maximum(y, noise_floor))
    r_std = r / sigma
    num = np.sum(r_std[:-1] * r_std[1:])
    den = np.sum(r_std ** 2)
    rho_1 = float(num / den) if den > 0 else 0.0
    thr = 2.0 / np.sqrt(len(r_std)) if len(r_std) > 0 else float("inf")

    energies: dict[str, float] = {}
    for label, (lo, hi) in diagnostic_windows.items():
        mask = (x >= lo) & (x <= hi)
        energies[label] = float(np.mean(r_std[mask] ** 2)) if mask.sum() > 0 else 0.0
    gmean = float(np.mean(r_std ** 2)) if len(r_std) > 0 else 0.0
    flagged = [lbl for lbl, e in energies.items()
               if gmean > 0 and e > window_flag_ratio * gmean]
    return ResidualDiagnostics(
        autocorrelation_lag1=rho_1,
        autocorr_flag=abs(rho_1) > thr,
        window_energies=energies,
        flagged_windows=flagged,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Reports, BIC*, ranking
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PlausibilityFlags:
    boundary_hits: list[str] = field(default_factory=list)
    unphysical_widths: list[str] = field(default_factory=list)
    orphan_peaks: bool = False


@dataclass
class ProposedPeakReport:
    role: str
    detection_windows: list[str]
    detection_energy: float
    detection_ratio: float
    proposed_center_init: float
    proposed_fwhm_init: float
    proposed_amplitude_init: float
    fitted_center: Optional[float] = None
    fitted_fwhm: Optional[float] = None
    fitted_amplitude: Optional[float] = None
    persistence: Optional[float] = None
    delta_bic_vs_base: Optional[float] = None
    boundary_hits: list[str] = field(default_factory=list)
    accepted: bool = False
    rejection_reason: Optional[str] = None
    near_roi_endpoint: bool = False
    roi_bounds: Optional[tuple[float, float]] = None
    # accepted while PEGGING the ordinary FWHM ceiling — the feature is
    # broader than an ordinary component with no known-broad justification;
    # the fit is held at the physical limit and the result is CONDITIONAL
    width_capped: bool = False


@dataclass
class CoincidenceReport:
    center_be: float
    contributors: list[tuple[str, bool]]


@dataclass
class ProposalPassTiming:
    candidate_name: str
    n_flagged: int
    n_over_cap: int
    n_attempted: int
    n_fast_rejected: int
    n_stability_rejected: int
    n_accepted: int
    wall_time_sec: float
    timed_out: bool


@dataclass
class ModelReport:
    """Complete diagnostics for one candidate — no collapse to one scalar."""
    model: CandidateModel
    primary_fit: FitOutcome
    bic: float
    stability: ModelStability
    residuals: ResidualDiagnostics
    plausibility: PlausibilityFlags
    absent_slots: list[AbsentSlotReport] = field(default_factory=list)
    proposed_peaks: list[ProposedPeakReport] = field(default_factory=list)
    augmented_from: Optional[str] = None
    # Full lmfit param names fixed at their bounds by the decisive-override
    # bound-fixed refit (empty for ordinary reports).  Stability figures on
    # such a report are inherited from the free (pegged) fit — a documented
    # approximation.
    boundary_fixed_params: list[str] = field(default_factory=list)

    @property
    def reduced_chi_sq(self) -> float:
        dof = max(self.primary_fit.n_data - self.primary_fit.n_params, 1)
        return self.primary_fit.weighted_chi_sq / dof

    @property
    def adjusted_n_params(self) -> int:
        removed = sum(a.removed_n_params for a in self.absent_slots)
        return max(self.primary_fit.n_params - removed, 1)

    @property
    def bic_adjusted(self) -> float:
        """BIC* (heuristic — absent-slot params arithmetically subtracted;
        the BIC/IC math review requires the raw full-k and weighted
        counterparts REPORTED beside it: see bic_raw / bic_weighted)."""
        n = self.primary_fit.n_data
        rss = self.primary_fit.residual_sum_sq
        if n <= 0 or rss <= 0:
            return float("inf")
        return n * np.log(rss / n) + self.adjusted_n_params * np.log(n)

    @property
    def bic_raw(self) -> float:
        """Full-k, no absent-slot adjustment — reported beside the labeled
        heuristic so the adjustment can never silently decide alone
        (BIC/IC math review: 'large-model RSS with small-model penalty')."""
        return compute_bic(self.primary_fit)

    @property
    def bic_weighted(self) -> float:
        """Known-σ (weighted-χ²) FULL-k BIC: χ²_w + k·ln n with k = the
        actual free-parameter count (NO absent-slot adjustment — the
        adjustment is the labeled heuristic on BIC*; letting it into the
        companion criterion would let the heuristic shape the
        weighted-vs-RSS disagreement it exists to expose).  This is the
        criterion CONSISTENT with the Poisson-weighted fits; the ranking
        still uses BIC*, and weighted_ic_disagreement fires when the two
        criteria pick different survivors."""
        n = self.primary_fit.n_data
        chi = self.primary_fit.weighted_chi_sq
        if n <= 0 or not np.isfinite(chi):
            return float("inf")
        return chi + self.primary_fit.n_params * np.log(n)

    @property
    def n_eff_lag1(self) -> Optional[float]:
        """Effective sample size from the lag-1 autocorrelation of the
        weighted residuals: n·(1−ρ)/(1+ρ).  Oversampled/correlated spectra
        make the raw n in k·ln(n) (and the ΔBIC thresholds) overconfident
        — reported so consumers can see how far the independence
        assumption is stretched (BIC/IC math review)."""
        lm = self.primary_fit.lmfit_result
        if lm is None or getattr(lm, "residual", None) is None:
            return None
        r = np.asarray(lm.residual, dtype=float)
        if len(r) < 8 or float(np.std(r)) == 0.0:
            return None
        r = r - r.mean()
        rho = float(np.sum(r[:-1] * r[1:]) / np.sum(r * r))
        rho = min(max(rho, -0.99), 0.99)
        return float(len(r) * (1.0 - rho) / (1.0 + rho))

    @property
    def active_min_persistence(self) -> float:
        absent_roles = {a.role for a in self.absent_slots}
        active = [s for s in self.stability.per_slot.values() if s.role not in absent_roles]
        if not active:
            return 0.0
        return min(s.persistence for s in active)


def compute_bic(fit: FitOutcome) -> float:
    """fitalg likelihood convention: BIC = n·ln(RSS/n) + k·ln(n)."""
    n, rss = fit.n_data, fit.residual_sum_sq
    if n <= 0 or rss <= 0:
        return float("inf")
    return n * np.log(rss / n) + fit.n_params * np.log(n)


@dataclass
class ComparisonResult:
    reports: list[ModelReport]
    survivors: list[ModelReport]
    filtered_out: list[tuple[ModelReport, str]]
    ambiguous_pairs: list[tuple[str, str, str]]
    non_converged: list[tuple[CandidateModel, FitOutcome]] = field(default_factory=list)
    cross_candidate_coincidences: list[CoincidenceReport] = field(default_factory=list)
    proposal_pass_timings: list[ProposalPassTiming] = field(default_factory=list)
    # True when the leading survivor is constraint-limited.  Reason:
    #   'no_clean_survivor'  — nothing passed plausibility cleanly; the
    #                          stable-but-boundary-limited tier is ranked.
    #   'decisive_override'  — clean survivors exist but a bound-fixed refit
    #                          of a boundary-limited candidate dominates them
    #                          (see CONDITIONAL_OVERRIDE_DELTA_BIC); clean
    #                          survivors remain as ranked alternatives.
    # Never silent (spec stance: best-evidenced proposal + honest
    # uncertainty, not a dead end).
    conditional: bool = False
    conditional_reason: Optional[str] = None
    # The ambiguity threshold ACTUALLY used for ambiguous_pairs — consumers
    # (criteria panel) must reuse it so the payload can never disagree with
    # the ranking (Codex Stage-2 re-review finding #1).
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY
    # A filtered candidate whose BIC* beats the winner's by more than the
    # decisive threshold — {name, bic_star, delta_bic_vs_winner,
    # filter_reason} or None.  Stress-suite finding 0: evidence burial must
    # be machine-visible at the result level.
    filtered_dominant_alternative: Optional[dict] = None
    # The weighted-χ² criterion (consistent with the fit weights) prefers a
    # DIFFERENT survivor than the ranking's RSS-form BIC* — {rss_bic_top,
    # weighted_bic_top, note} or None (BIC/IC math review blocker:
    # selection must not silently rest on a likelihood the fits reject).
    weighted_ic_disagreement: Optional[dict] = None
    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
    # evaluating every candidate in the grammar. The candidates evaluated so
    # far are still ranked/reported normally (best-so-far) — this only flags
    # that the comparison is partial, so a slow/pathological spectrum
    # returns an honest incomplete result instead of a request timeout.
    analysis_truncated: bool = False
    n_candidates_evaluated: int = 0
    n_candidates_total: int = 0
    # Pre-fit out-of-grammar dominant seeding (unit F1): the detected
    # features every candidate was augmented with, incl. the gate values
    # (UNVERIFIED tunables) — empty when detection found nothing, in which
    # case the candidate set ran unmodified.
    preseeded_features: list[dict] = field(default_factory=list)
    # Two-phase sweep record (unit F3) — None when the classic single-phase
    # path ran (candidate set ≤ SCREEN_TOP_K).  Otherwise every candidate's
    # screen outcome: {name, converged, bic, selected} — screened-out
    # candidates are visible here and can never be survivors.
    screen: Optional[list[dict]] = None
    # Candidate-generation layer (autofit.candidates): the OVERCOMPLETE,
    # provenance-tagged detection pool payload — every feature any source
    # (local_max / curvature_shoulder / residual_gap / grammar) proposed,
    # with per-feature gate outcomes and seeding decisions.  None when the
    # layer did not run (enable_preseed=False or no candidates).
    candidate_pool: Optional[dict] = None


def rank_and_filter(
    reports: list[ModelReport],
    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY,
    allow_conditional: bool = True,
    allow_last_resort: bool = False,
) -> ComparisonResult:
    """
    Filter (plausibility, active persistence) then rank (χ²ᵣ, BIC*).

    Two-tier semantics (departure from fitalg, which returned zero survivors
    whenever every candidate had any boundary hit — routine on real composite
    samples): when NO candidate passes plausibility cleanly but some are
    otherwise stable, those are ranked as a CONDITIONAL tier with
    ``result.conditional = True`` and every violation preserved.  Stability
    failures are never promoted — an unstable fit is pathology, not a
    constraint conflict.
    """
    filtered_out: list[tuple[ModelReport, str]] = []
    survivors: list[ModelReport] = []
    conditional_pool: list[ModelReport] = []

    for r in reports:
        active_min = r.active_min_persistence
        stable = active_min >= persistence_threshold
        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
                or r.plausibility.orphan_peaks:
            # orphan_peaks included (Codex Stage-2 re-review finding #3):
            # refits repeatedly producing unmatched components is a
            # plausibility violation, not clean-survivor material.
            filtered_out.append((r, f"plausibility: {r.plausibility}"))
            if stable:
                conditional_pool.append(r)
            continue
        if not stable:
            absent_roles = [a.role for a in r.absent_slots]
            extra = f"  (absent slots excluded: {absent_roles})" if absent_roles else ""
            filtered_out.append((r, f"stability: active min persistence "
                                    f"{active_min:.2f} < {persistence_threshold}{extra}"))
            continue
        survivors.append(r)

    conditional = False
    conditional_reason = None
    if allow_conditional and conditional_pool and not survivors:
        survivors = conditional_pool
        conditional = True
        conditional_reason = "no_clean_survivor"
    elif allow_conditional and allow_last_resort and not survivors and reports:
        # LAST-RESORT tier (Stage-2, 2026-07-10; measured on real low-res
        # Fe 2p): fires ONLY when the caller says detection found real
        # structure (allow_last_resort = detection seeds exist) — its job
        # is rescuing DETECTED structure from selection instability, never
        # forcing an answer on featureless data (a flat-noise grammar fit
        # can converge; the honest result there stays no-survivor).
        # Every candidate failed BOTH tiers — typically cross-refit
        # label instability (orphan_peaks) on heavily-overlapped low-res
        # structure.  For a suggest-a-profile tool an EMPTY answer is the
        # worst answer: emit the single best CONVERGED model, loudly
        # flagged unstable.  This tier exists only when clean and
        # conditional are BOTH empty — stability failures are still never
        # preferred over anything (the original design rule stands).
        viable = [r for r in reports
                  if r.primary_fit.converged
                  and np.isfinite(r.bic_adjusted)]
        if viable:
            best = min(viable,
                       key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))
            survivors = [best]
            conditional = True
            conditional_reason = "unstable_last_resort"
    # NOTE: the decisive-override path (clean survivors exist but a
    # bound-fixed refit of a conditional candidate dominates) lives in
    # compare_models — it needs the spectrum to refit; rank_and_filter is
    # pure ranking.

    # BIC* is the ranking default (spec §6); χ²ᵣ breaks ties only.  fitalg
    # ranked (χ²ᵣ, BIC*) — spec-noncompliant, changed per Codex finding #3.
    survivors.sort(key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))

    ambiguous: list[tuple[str, str, str]] = []
    for i in range(len(survivors)):
        for j in range(i + 1, len(survivors)):
            a, b = survivors[i], survivors[j]
            if abs(a.bic_adjusted - b.bic_adjusted) <= bic_ambiguity_threshold \
               and a.model.n_components != b.model.n_components:
                diff = {s.role for s in a.model.slots} ^ {s.role for s in b.model.slots}
                ambiguous.append((
                    a.model.name, b.model.name,
                    f"Indistinguishable on fit quality and BIC* "
                    f"(ΔBIC*={abs(a.bic_adjusted - b.bic_adjusted):.2f}); "
                    f"structural difference: {diff}",
                ))
    return ComparisonResult(
        reports=reports, survivors=survivors,
        filtered_out=filtered_out, ambiguous_pairs=ambiguous,
        conditional=conditional, conditional_reason=conditional_reason,
        bic_ambiguity_threshold=bic_ambiguity_threshold,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pre-fit out-of-grammar dominant seeding (unit F1 — see the constants block)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PreseedSpec:
    role: str
    center_init: float
    fwhm_init: float
    amplitude_net: float          # smoothed background-subtracted height
    fraction_of_max: float        # vs the global smoothed net maximum
    local_snr: float              # amplitude_net / local Poisson σ
    # detection source: 'local_max' (the F1 dominant channel) or
    # 'curvature_shoulder' (the CWT ridge channel of autofit.candidates)
    provenance: str = "local_max"
    prom_z: Optional[float] = None    # curvature channel's prominence-z

    def payload(self) -> dict:
        rec = {
            "role": self.role,
            "center_be": round(float(self.center_init), 3),
            "amplitude_net": round(float(self.amplitude_net), 1),
            "fraction_of_max": round(float(self.fraction_of_max), 3),
            "local_snr": round(float(self.local_snr), 1),
            "fwhm_init": round(float(self.fwhm_init), 2),
            "provenance": self.provenance,
            "gates": {
                "min_fraction_of_max": PRESEED_MIN_FRACTION_OF_MAX,
                "amplitude_snr": PRESEED_AMPLITUDE_SNR,
                "note": "UNVERIFIED engine tunables — pre-seeded slots are "
                        "region-unassigned; assignment requires human review",
            },
        }
        if self.prom_z is not None:
            rec["prom_z"] = round(float(self.prom_z), 2)
        return rec


def _all_grammar_windows(
    candidates: list[CandidateModel],
    canonical_windows: dict[str, tuple[float, float]],
) -> list[tuple[float, float]]:
    wins = [s.be_window for c in candidates for s in c.slots]
    wins += list(canonical_windows.values())
    return wins


def _preseed_window_margin(candidates: list[CandidateModel]) -> float:
    """Mean main-FWHM midpoint across the candidate set × the proposal
    separation factor — the shared "too close to a grammar window to be a
    separate feature" convention (used identically by the dominant channel
    and the pool's curvature channel)."""
    mids = [_main_slot_fwhm_midpoint(c) for c in candidates] or [1.0]
    return PROPOSAL_GRAMMAR_SEPARATION_FACTOR * float(np.mean(mids))


def detect_out_of_grammar_dominants(
    x: np.ndarray,
    y: np.ndarray,
    background: np.ndarray,
    candidates: list[CandidateModel],
    canonical_windows: dict[str, tuple[float, float]],
    noise_floor: float = 1.0,
) -> list[PreseedSpec]:
    """
    Prominent smoothed local maxima of the background-subtracted data that
    lie outside EVERY grammar slot window and diagnostic window (+ the same
    separation margin the proposal pass uses).  Conservative by design —
    dominance (fraction-of-max) AND detection-floor SNR gates — so ordinary
    grammar-covered spectra return [] and small out-of-window features stay
    the residual-proposal pass's job.
    """
    if len(x) < max(PRESEED_SMOOTH_POINTS + 4, 8):
        return []
    # real raw_be grids DESCEND — normalize (np.interp-class bug family)
    if x[0] > x[-1]:
        x_asc, y_asc, bg_asc = x[::-1], y[::-1], background[::-1]
    else:
        x_asc, y_asc, bg_asc = x, y, background
    y_net = y_asc - bg_asc
    k = PRESEED_SMOOTH_POINTS
    kernel = np.ones(k) / k
    ys = np.convolve(y_net, kernel, mode="same")
    global_max = float(np.max(ys))
    if global_max <= 0:
        return []

    # margin: mean main-FWHM midpoint across the candidate set × the
    # proposal separation factor (the same "too close to a window to be a
    # separate feature" convention)
    margin = _preseed_window_margin(candidates)
    windows = _all_grammar_windows(candidates, canonical_windows)

    def in_any_window(be: float) -> bool:
        return any((lo - margin) <= be <= (hi + margin) for lo, hi in windows)

    found: list[PreseedSpec] = []
    edge = max(2, k // 2)     # smoothing edge — 'same' convolution damps ends
    for i in range(edge, len(ys) - edge):
        if not (ys[i] >= ys[i - 1] and ys[i] > ys[i + 1]
                and ys[i] >= ys[i - 2] and ys[i] > ys[i + 2]):
            continue
        center = float(x_asc[i])
        amp = float(ys[i])
        if in_any_window(center):
            continue
        if amp < PRESEED_MIN_FRACTION_OF_MAX * global_max:
            continue
        mask = (x_asc >= center - PROPOSAL_WINDOW_WIDTH) & \
               (x_asc <= center + PROPOSAL_WINDOW_WIDTH)
        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
            if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
        if amp < PRESEED_AMPLITUDE_SNR * local_sigma:
            continue
        # FWHM estimate: half-height walk on the smoothed net signal
        half = 0.5 * amp
        left = i
        while left > 0 and ys[left - 1] > half:
            left -= 1
        right = i
        while right < len(ys) - 1 and ys[right + 1] > half:
            right += 1
        fwhh = float(x_asc[right] - x_asc[left])
        fwhm_init = float(np.clip(fwhh if fwhh > 0 else PROPOSAL_FWHM_MIN,
                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
        found.append(PreseedSpec(
            role="", center_init=center, fwhm_init=fwhm_init,
            amplitude_net=amp, fraction_of_max=amp / global_max,
            local_snr=amp / max(local_sigma, 1e-12),
        ))

    # strongest first; enforce separation; cap; then stable role naming by BE
    found.sort(key=lambda s: s.amplitude_net, reverse=True)
    accepted: list[PreseedSpec] = []
    for s in found:
        if len(accepted) >= PRESEED_MAX:
            break
        if any(abs(s.center_init - a.center_init) < PRESEED_MIN_SEPARATION_BE
               for a in accepted):
            continue
        accepted.append(s)
    accepted.sort(key=lambda s: s.center_init)
    return [PreseedSpec(role=f"preseed_dominant_{i}", center_init=s.center_init,
                        fwhm_init=s.fwhm_init, amplitude_net=s.amplitude_net,
                        fraction_of_max=s.fraction_of_max, local_snr=s.local_snr)
            for i, s in enumerate(accepted)]


def _preseed_augmented(
    base: CandidateModel, specs: list[PreseedSpec]
) -> CandidateModel:
    """Every candidate gets the seeded slots — region/phase `unassigned`
    exactly like proposal slots (assignment is adjudication, not window
    inheritance; Codex Stage-2 finding #2 applies here identically).  The
    roles do not start with ``main_`` so the absent-slot machinery can
    classify a seed that carries no real signal absent, excluding it from
    the emitted peaks with the honest BIC* adjustment."""
    seeded = tuple(
        ComponentSlot(
            role=s.role,
            region="unassigned",
            phase_id="unassigned",
            be_window=(s.center_init - 0.75, s.center_init + 0.75),
            line_shape=PROPOSED_PEAK_SHAPE,
            fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
        )
        for s in specs
    )
    return CandidateModel(
        name=f"{base.name}+preseed",
        background=base.background,
        slots=base.slots + seeded,
        shared_fwhm_params=base.shared_fwhm_params,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Proposal pass (residual-guided peak augmentation)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ProposalSpec:
    role: str
    detection_windows: list[str]
    detection_energy: float
    detection_ratio: float
    center_init: float
    fwhm_init: float
    amplitude_init: float
    line_shape: LineShape


def _proposal_tiles(x: np.ndarray) -> list[tuple[str, tuple[float, float]]]:
    if len(x) < 2:
        return []
    lo, hi = float(np.min(x)), float(np.max(x))
    tiles = []
    start = lo
    while start + PROPOSAL_WINDOW_WIDTH <= hi + 1e-9:
        win = (start, start + PROPOSAL_WINDOW_WIDTH)
        tiles.append((f"proposal_{win[0]:.2f}-{win[1]:.2f}", win))
        start += PROPOSAL_WINDOW_STRIDE
    return tiles


def _main_slot_fwhm_midpoint(model: CandidateModel) -> float:
    mids = [0.5 * (s.fwhm_range[0] + s.fwhm_range[1])
            for s in model.slots if _is_main_role(s.role)]
    return float(np.mean(mids)) if mids else 1.0


def _proposal_blocked(
    center: float,
    base_model: CandidateModel,
    fitted_components: list["FittedComponent"],
) -> bool:
    """Stage-2 proposal-eligibility rule (2026-07-10; replaces the old
    window-membership test — Step-1 chokepoint 2): a residual cluster is
    blocked only by

    (i)  PROXIMITY to a fitted component — within
         ``PROPOSAL_GRAMMAR_SEPARATION_FACTOR × that component's own
         fitted width`` (transferable units: half its width, whatever the
         region's energy scale) the residual is that component's
         position/width business, never a new peak; or
    (ii) sitting inside a POPULATED slot's window — the slot owns its
         window's residuals, so a lineshape/width mismatch there surfaces
         as flags (χ²ᵣ, autocorrelation, residual_flags), NEVER as an
         invented tail-fixer peak.

    An UNPOPULATED window blocks nothing: the measured failure was real
    satellite intensity inside a canonical window that the winning family
    had no slot for — permanently unreachable under window-membership
    blocking.

    Deliberately NEVER uses the fit_full_window bound override (Codex-
    caught, round 2): a ``region == "unassigned"`` slot's window widens
    to the FULL ROI under that option, which would make rule (ii) block
    every later residual proposal anywhere in the ROI once the first one
    is accepted — defeating the iterative multi-proposal pass entirely.
    This rule's "populated slot's window" is about a slot's own intrinsic
    territory, not the fit's search bound; the two are different
    concepts and only the latter should ever widen."""
    populated_roles = {c.slot_role for c in fitted_components}
    for comp in fitted_components:
        if abs(center - comp.position) <= (
                PROPOSAL_GRAMMAR_SEPARATION_FACTOR * comp.fwhm):
            return True
    for slot in base_model.slots:
        if slot.role not in populated_roles:
            continue
        lo, hi = _effective_be_window(slot, fitted_components)
        if lo <= center <= hi:
            return True
    return False


def _detect_residual_proposals(
    x: np.ndarray,
    y: np.ndarray,
    y_fit: np.ndarray,
    noise_floor: float,
    base_model: CandidateModel,
    fitted_components: list["FittedComponent"],
) -> list[ProposalSpec]:
    if len(x) < 4:
        return []
    r = y - y_fit
    sigma = np.sqrt(np.maximum(y, noise_floor))
    r_std = r / sigma
    gmean = float(np.mean(r_std ** 2))
    if gmean <= 0:
        return []

    if x[0] > x[-1]:
        x_asc, r_asc, r_std_asc = x[::-1], r[::-1], r_std[::-1]
    else:
        x_asc, r_asc, r_std_asc = x, r, r_std

    flagged = []
    for label, (lo, hi) in _proposal_tiles(x_asc):
        mask = (x_asc >= lo) & (x_asc <= hi)
        if mask.sum() < 2:
            continue
        energy = float(np.mean(r_std_asc[mask] ** 2))
        if energy <= PROPOSAL_FLAG_RATIO * gmean:
            continue
        flagged.append({"label": label, "be_lo": lo, "be_hi": hi,
                        "be_center": 0.5 * (lo + hi), "energy": energy,
                        "ratio": energy / gmean})
    if not flagged:
        return []

    flagged.sort(key=lambda t: t["be_center"])
    clusters: list[list[dict]] = [[flagged[0]]]
    for t in flagged[1:]:
        if t["be_center"] - clusters[-1][-1]["be_center"] <= PROPOSAL_MERGE_BE:
            clusters[-1].append(t)
        else:
            clusters.append([t])

    specs: list[ProposalSpec] = []
    for idx, cluster in enumerate(clusters):
        lo = min(t["be_lo"] for t in cluster)
        hi = max(t["be_hi"] for t in cluster)
        mask = (x_asc >= lo) & (x_asc <= hi)
        if mask.sum() < 3:
            continue
        r_abs = np.abs(r_std_asc[mask])
        k = int(np.argmax(r_abs))
        span = x_asc[mask]
        center = float(span[k])
        r_at = float(r_asc[mask][k])
        if r_at <= 0:
            continue
        half = 0.5 * float(r_abs[k])
        above = r_abs > half
        left = k
        while left > 0 and above[left - 1]:
            left -= 1
        right = k
        while right < len(above) - 1 and above[right + 1]:
            right += 1
        fwhh = float(span[right] - span[left])
        fwhm_init = float(np.clip(fwhh if fwhh > 0 else PROPOSAL_FWHM_MIN,
                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
        if _proposal_blocked(center, base_model, fitted_components):
            continue
        specs.append(ProposalSpec(
            role=f"proposed_peak_{idx}",
            detection_windows=[t["label"] for t in cluster],
            detection_energy=float(sum(t["energy"] for t in cluster)),
            detection_ratio=float(max(t["ratio"] for t in cluster)),
            center_init=center, fwhm_init=fwhm_init,
            amplitude_init=max(r_at, 1.0),
            line_shape=PROPOSED_PEAK_SHAPE,
        ))
    specs.sort(key=lambda s: s.detection_energy, reverse=True)
    return specs


def _next_proposal_index(model: CandidateModel) -> int:
    """One past the highest existing ``proposed_peak_<n>`` suffix on ``model``
    (0 if none).  MUST be max-suffix+1, NOT a slot COUNT: within an F2 round
    the specs are numbered from a base and attempted in detection-energy
    order, so a rejected earlier spec followed by an accepted later one
    leaves e.g. ``proposed_peak_1`` present while ``proposed_peak_0`` never
    materialized — a count (1) would then re-issue ``proposed_peak_1`` next
    round, colliding the slot role and its lmfit param prefix (Codex
    c1s-fix review, both runs BLOCKER)."""
    mx = -1
    prefix = "proposed_peak_"
    for s in model.slots:
        if s.role.startswith(prefix):
            try:
                mx = max(mx, int(s.role[len(prefix):]))
            except ValueError:
                continue
    return mx + 1


def _augmented_candidate(base: CandidateModel, spec: ProposalSpec) -> CandidateModel:
    # Proposals spawn OUTSIDE every grammar window by construction (the
    # separation gate), so no region/phase can honestly be inherited —
    # assigning the base model's first slot's tags would leak a phase in
    # joint fits (Codex Stage-2 finding #2).  Region/phase assignment of a
    # proposed peak is a human adjudication step, not an inheritance.
    proposed = ComponentSlot(
        role=spec.role,
        region="unassigned",
        phase_id="unassigned",
        be_window=(spec.center_init - 0.75, spec.center_init + 0.75),
        line_shape=spec.line_shape,
        fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
    )
    return CandidateModel(
        name=f"{base.name}+prop",
        background=base.background,
        slots=base.slots + (proposed,),
        shared_fwhm_params=base.shared_fwhm_params,
    )


def _initial_params_for_augmented(
    aug_model: CandidateModel,
    base_fit: FitOutcome,
    spec: ProposalSpec,
    x: np.ndarray,
    y_net: np.ndarray,
    fit_full_window: bool = False,
) -> Parameters:
    params = _default_params_from_slots(aug_model, x=x, y_net=y_net,
                                        fit_full_window=fit_full_window)
    if base_fit.lmfit_result is not None:
        for pname, par in base_fit.lmfit_result.params.items():
            if pname not in params or not params[pname].vary:
                continue
            lo = params[pname].min if np.isfinite(params[pname].min) else -np.inf
            hi = params[pname].max if np.isfinite(params[pname].max) else np.inf
            params[pname].set(value=float(np.clip(par.value, lo, hi)))
    prefix = _slot_prefix(spec.role)
    pc = params[f"{prefix}center"]
    pc.set(value=float(np.clip(spec.center_init, pc.min, pc.max)))
    pa = params[f"{prefix}amplitude"]
    pa.set(value=float(np.clip(spec.amplitude_init, pa.min, pa.max)))
    pf = params.get(f"{prefix}fwhm")
    if pf is not None and pf.expr is None:
        pf.set(value=float(np.clip(spec.fwhm_init, pf.min, pf.max)))
    return params


def _attempt_proposal(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    base_report: ModelReport,
    spec: ProposalSpec,
    noise_floor: float,
    n_refits: int,
    rng_seed: int,
    absent_slot_area_fraction: float,
    absent_slot_persistence_threshold: float,
    diagnostic_windows: dict[str, tuple[float, float]],
    budget_remaining: float = float("inf"),
    fit_full_window: bool = False,
) -> tuple[Optional[ModelReport], ProposedPeakReport, str]:
    attempt_start = time.perf_counter()
    base_model = base_report.model
    base_fit = base_report.primary_fit
    aug_model = _augmented_candidate(base_model, spec)

    roi = (float(np.min(x)), float(np.max(x)))
    pr = ProposedPeakReport(
        role=spec.role, detection_windows=list(spec.detection_windows),
        detection_energy=spec.detection_energy, detection_ratio=spec.detection_ratio,
        proposed_center_init=spec.center_init, proposed_fwhm_init=spec.fwhm_init,
        proposed_amplitude_init=spec.amplitude_init, roi_bounds=roi,
    )

    def _fast(reason: str):
        pr.rejection_reason = reason
        return None, pr, "fast_rejected"

    # An augmented fit_candidate has no internal wall clock and runs
    # ~10-12 s worst-case; starting one with less than PROPOSAL_MIN_FIT_
    # BUDGET_SEC of sweep budget left would overrun TOTAL_ANALYSIS_TIMEOUT_SEC
    # and the gunicorn --timeout (Codex c1s-fix review, run B MAJOR).  The
    # caller passes budget_remaining = min(pass budget, sweep budget) left.
    if budget_remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
        return _fast(
            f"insufficient_budget: {budget_remaining:.1f}s left < "
            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s needed for one augmented fit")

    bg = _compute_background(x, y, aug_model.background)
    try:
        init = _initial_params_for_augmented(aug_model, base_fit, spec, x, y - bg,
                                             fit_full_window=fit_full_window)
    except Exception as exc:
        return _fast(f"init_params_error: {exc}")

    primary = fit_candidate(x, y, weights, aug_model, initial_params=init)
    if not primary.converged:
        return _fast("augmented_fit_did_not_converge")
    comp = next((c for c in primary.components if c.slot_role == spec.role), None)
    if comp is None:
        return _fast("proposed_slot_did_not_populate")

    pr.fitted_center = comp.position
    pr.fitted_fwhm = comp.fwhm
    pr.fitted_amplitude = comp.amplitude
    # A peg on the WIDTH cap alone (fwhm@max) is the ordinary physical FWHM
    # ceiling doing its job: the feature is broader than an ordinary
    # component with no known-broad justification.  KEEP such a proposal —
    # modelled at the physical limit — and let it flag the augmented report
    # (unphysical_widths + the fwhm@max boundary hit → CONDITIONAL) rather
    # than rejecting it and leaving the intensity unmodelled.  A SUBSTANTIVE
    # peg (center at a window edge, amplitude at a wall, or fwhm@MIN = an
    # implausibly narrow spike) is spurious → reject.  (Shape endpoints like
    # gl_ratio=0/1 are valid physics, excluded by the shared detector — see
    # _proposed_slot_pegs.)  NOTE this is re-evaluated AFTER the stability
    # best-outcome promotion below, since a deeper minimum can move a param
    # to a wall (Codex fwhm-cap review, run B BLOCKER).
    width_cap_hit = f"{spec.role}:fwhm@max"
    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
    if comp.amplitude <= noise_floor:
        return _fast(f"amplitude {comp.amplitude:.1f} ≤ noise_floor {noise_floor:.1f}")
    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
    if spurious_hits:
        return _fast(f"proposed slot boundary pegs: {spurious_hits}")

    mask = (x >= comp.position - PROPOSAL_WINDOW_WIDTH) & \
           (x <= comp.position + PROPOSAL_WINDOW_WIDTH)
    local_sigma = float(np.median(np.sqrt(np.maximum(y[mask], noise_floor)))) \
        if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
    if comp.amplitude < PROPOSAL_AMPLITUDE_SNR * local_sigma:
        return _fast(f"amplitude {comp.amplitude:.1f} < "
                     f"{PROPOSAL_AMPLITUDE_SNR:.1f} × local σ ({local_sigma:.2f})")

    aug_bic = compute_bic(primary)
    pr.delta_bic_vs_base = aug_bic - base_report.bic_adjusted
    if not (aug_bic + PROPOSAL_DELTABIC_THRESHOLD < base_report.bic_adjusted):
        return _fast(
            f"fast pre-check: augmented primary BIC {aug_bic:.2f} does not beat "
            f"base BIC* {base_report.bic_adjusted:.2f} by {PROPOSAL_DELTABIC_THRESHOLD:.1f}"
        )

    # budget_remaining was a snapshot BEFORE the augmented fit; that fit has
    # since consumed wall time, so the stability deadline must be computed
    # from what's ACTUALLY left, not the stale snapshot (Codex c1s-fix
    # review, run B MAJOR — otherwise the stability pass could run
    # min(stale_budget, 35) s past the fit and overrun the sweep budget).
    # The floor (not just <= 0) matters because run_stability_analysis
    # checks its deadline at the TOP of the loop and then runs an unbounded
    # fit_candidate — so starting stability with only a few seconds left
    # would still overrun by ~one worst-case fit (Codex c1s-fix RE-CHECK,
    # run B MAJOR: disposition 2 was not fully closed by the top guard).
    remaining = budget_remaining - (time.perf_counter() - attempt_start)
    if remaining < PROPOSAL_MIN_FIT_BUDGET_SEC:
        pr.rejection_reason = (
            f"insufficient_budget before stability: {remaining:.1f}s left < "
            f"{PROPOSAL_MIN_FIT_BUDGET_SEC:.0f}s (one refit could overrun)")
        return None, pr, "fast_rejected"

    stability = run_stability_analysis(
        x, y, weights, aug_model, primary,
        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
        deadline=time.perf_counter() + min(remaining,
                                           PROPOSAL_STABILITY_TIMEOUT_SEC),
        fit_full_window=fit_full_window,
    )
    if (stability.best_outcome is not None
            and stability.best_outcome.weighted_chi_sq < primary.weighted_chi_sq):
        primary = stability.best_outcome
        comp = next((c for c in primary.components if c.slot_role == spec.role), comp)
        if comp is not None:
            pr.fitted_center = comp.position
            pr.fitted_fwhm = comp.fwhm
            pr.fitted_amplitude = comp.amplitude
    # Re-evaluate the proposed-slot pegs against the FINAL (possibly
    # stability-promoted) outcome — a deeper minimum can move a param to a
    # wall the initial fit did not touch (Codex fwhm-cap review, run B
    # BLOCKER): a stability-promoted center@min must STILL reject, and a
    # stability-INTRODUCED fwhm@max must set width_capped so the payload
    # matches the emitted decomposition.
    pr.boundary_hits = _proposed_slot_pegs(primary, spec.role)
    spurious_hits = [h for h in pr.boundary_hits if h != width_cap_hit]
    if spurious_hits:
        pr.rejection_reason = (
            f"proposed slot boundary pegs (post-stability): {spurious_hits}")
        return None, pr, "stability_rejected"
    pr.width_capped = pr.boundary_hits == [width_cap_hit]
    sstab = stability.per_slot.get(spec.role)
    if sstab is None:
        pr.rejection_reason = "proposed slot missing from stability output"
        return None, pr, "stability_rejected"
    pr.persistence = sstab.persistence
    if sstab.persistence < PROPOSAL_PERSISTENCE_THRESHOLD:
        pr.rejection_reason = (f"persistence {sstab.persistence:.2f} < "
                               f"{PROPOSAL_PERSISTENCE_THRESHOLD:.2f}")
        return None, pr, "stability_rejected"

    y_fit_aug = (primary.lmfit_result.best_fit + primary.background
                 if primary.lmfit_result is not None else np.zeros_like(y))
    residuals = compute_residual_diagnostics(x, y, y_fit_aug, noise_floor, diagnostic_windows)
    slot_areas = compute_slot_areas(aug_model, primary, x)
    absent = _identify_absent_slots(
        aug_model, stability, slot_areas, primary,
        persistence_threshold=absent_slot_persistence_threshold,
        area_fraction_threshold=absent_slot_area_fraction,
    )
    aug_report = ModelReport(
        model=aug_model, primary_fit=primary, bic=compute_bic(primary),
        stability=stability, residuals=residuals,
        plausibility=PlausibilityFlags(
            boundary_hits=list(primary.boundary_hits),
            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
            orphan_peaks=stability.orphan_rate > 0.1,
        ),
        absent_slots=absent, augmented_from=base_model.name,
    )

    delta = aug_report.bic_adjusted - base_report.bic_adjusted
    pr.delta_bic_vs_base = delta
    if not (delta < -PROPOSAL_DELTABIC_THRESHOLD):
        pr.rejection_reason = (f"ΔBIC* = {delta:+.2f} does not beat "
                               f"-{PROPOSAL_DELTABIC_THRESHOLD:.1f} improvement threshold")
        return None, pr, "stability_rejected"

    lo, hi = roi
    pr.near_roi_endpoint = bool(
        abs(comp.position - lo) <= PROPOSAL_ENDPOINT_WARNING_BE
        or abs(comp.position - hi) <= PROPOSAL_ENDPOINT_WARNING_BE
    )
    pr.accepted = True
    aug_report.proposed_peaks = [pr]
    return aug_report, pr, "accepted"


def _cross_candidate_coincidences(
    attempts: list[tuple[str, ProposedPeakReport]],
) -> list[CoincidenceReport]:
    if not attempts:
        return []
    enriched = [{"base": b, "pr": pr,
                 "be": float(pr.fitted_center if pr.fitted_center is not None
                             else pr.proposed_center_init)}
                for b, pr in attempts]
    enriched.sort(key=lambda e: e["be"])
    clusters: list[list[dict]] = [[enriched[0]]]
    for e in enriched[1:]:
        if e["be"] - clusters[-1][-1]["be"] <= PROPOSAL_COINCIDENCE_BE:
            clusters[-1].append(e)
        else:
            clusters.append([e])
    out: list[CoincidenceReport] = []
    for c in clusters:
        bases = {e["base"] for e in c}
        if len(bases) < 2:
            continue
        per_base: dict[str, ProposedPeakReport] = {}
        for e in c:
            cur = per_base.get(e["base"])
            if cur is None or (e["pr"].accepted and not cur.accepted):
                per_base[e["base"]] = e["pr"]
        out.append(CoincidenceReport(
            center_be=float(np.median([e["be"] for e in c])),
            contributors=[(b, per_base[b].accepted) for b in sorted(per_base)],
        ))
    return out


# Bound the number of conditional candidates the override may refit — a
# runtime guard, not a statistical constant.
OVERRIDE_MAX_ATTEMPTS = 3


def _bound_fixed_refit(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    report: ModelReport,
    diagnostic_windows: dict[str, tuple[float, float]],
    noise_floor: float,
    n_refits: int,
    rng_seed: int,
    fit_full_window: bool = False,
) -> Optional[ModelReport]:
    """
    Refit a boundary-limited candidate with each pegged parameter FIXED at
    the bound it pegged to, so its BIC* uses an honest parameter count (a
    bound-pegged free parameter invalidates the interior-Laplace BIC
    approximation).

    Honesty requirements (Codex re-check blockers/major):
    - the refit must not itself peg any NEW bound — otherwise the
      interior-Laplace comparison is invalid again → return None;
    - a FRESH stability pass runs on the bound-fixed model (the constrained
      parameters stay fixed in every multi-start refit) — no inherited
      figures;
    - NO absent-slot adjustment is applied to the refit: its BIC* uses the
      full varying-parameter count (conservative — errs against promotion).
    """
    import dataclasses

    lm = report.primary_fit.lmfit_result
    if lm is None or not report.plausibility.boundary_hits:
        return None
    params = lm.params.copy()
    fixed: dict[str, float] = {}
    for hit in report.plausibility.boundary_hits:
        try:
            role_param, side = hit.rsplit("@", 1)
            role, pname = role_param.split(":", 1)
        except ValueError:
            continue
        full = _slot_prefix(role) + pname
        par = params.get(full)
        if par is None or not par.vary:
            continue
        val = par.min if side == "min" else par.max
        par.set(value=val, vary=False)
        fixed[full] = float(val)
    if not fixed:
        return None

    outcome = fit_candidate(x, y, weights, report.model, initial_params=params)
    if not outcome.converged:
        return None
    if outcome.boundary_hits:
        # fixing one wall pushed the fit onto another — still not an
        # interior optimum; no honest BIC* comparison is possible
        return None

    stability = run_stability_analysis(
        x, y, weights, report.model, outcome,
        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
        fixed_param_values=fixed,
        deadline=time.perf_counter() + CANDIDATE_TIMEOUT_SEC,
        fit_full_window=fit_full_window,
    )
    y_fit = (outcome.lmfit_result.best_fit + outcome.background
             if outcome.lmfit_result is not None else np.zeros_like(y))
    return ModelReport(
        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
        primary_fit=outcome,
        bic=compute_bic(outcome),
        stability=stability,
        residuals=compute_residual_diagnostics(
            x, y, y_fit, noise_floor, diagnostic_windows),
        plausibility=PlausibilityFlags(
            boundary_hits=[],
            # width pegs that were FIXED at the cap are still at the physical
            # ceiling — a fixed-at-2.0 ordinary component is no more physical
            # than a pegged one, so keep flagging it
            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
            orphan_peaks=stability.orphan_rate > 0.1,
        ),
        absent_slots=[],                      # conservative full-k BIC*
        boundary_fixed_params=sorted(fixed),
        # carry the proposal lineage forward so a width-capped proposal
        # promoted via decisive-override keeps its width_capped/proposed_peaks
        # record on the winner row (Codex fwhm-cap review, run A MINOR)
        proposed_peaks=list(report.proposed_peaks),
        augmented_from=report.augmented_from,
    )


def _apply_decisive_override(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    result: ComparisonResult,
    persistence_threshold: float,
    diagnostic_windows: dict[str, tuple[float, float]],
    noise_floor: float,
    n_refits: int,
    rng_seed: int,
    fit_full_window: bool = False,
) -> ComparisonResult:
    """Dominance rule — see CONDITIONAL_OVERRIDE_DELTA_BIC block comment."""
    if result.conditional or not result.survivors:
        return result
    clean_best = result.survivors[0]
    # (4) the clean best must itself show residual-structure evidence
    if not (clean_best.residuals.autocorr_flag
            or clean_best.residuals.flagged_windows):
        return result
    pool = [r for r, why in result.filtered_out
            if why.startswith("plausibility")
            and r.active_min_persistence >= persistence_threshold]
    pool.sort(key=lambda r: r.bic_adjusted)

    for candidate in pool[:OVERRIDE_MAX_ATTEMPTS]:
        refit = _bound_fixed_refit(x, y, weights, candidate,
                                   diagnostic_windows, noise_floor,
                                   n_refits=n_refits, rng_seed=rng_seed,
                                   fit_full_window=fit_full_window)
        if refit is None:
            continue
        # the bound-fixed model must be STABLE in its own right
        if refit.active_min_persistence < persistence_threshold:
            continue
        # (2) very-strong BIC* margin AND (3) strictly better χ²ᵣ
        if not (refit.bic_adjusted + CONDITIONAL_OVERRIDE_DELTA_BIC
                < clean_best.bic_adjusted
                and refit.reduced_chi_sq < clean_best.reduced_chi_sq):
            continue
        result.reports.append(refit)
        result.survivors = [refit] + result.survivors  # clean kept as alternatives
        result.conditional = True
        result.conditional_reason = "decisive_override"
        return result
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Top-level driver — region-agnostic
# ─────────────────────────────────────────────────────────────────────────────

def _report_progress(
    progress_cb: Optional[Callable[[dict], None]],
    phase: str, idx: int, total: int, name: str,
) -> None:
    """Fire ``progress_cb`` for one candidate transition; never let a
    broken sink (e.g. a full disk on the progress-file writer) break the
    analysis itself."""
    if progress_cb is None:
        return
    try:
        progress_cb({"phase": phase, "candidate_index": idx,
                     "candidate_total": total, "candidate_name": name})
    except Exception:
        log.debug("progress_cb raised — ignored", exc_info=True)


def compare_models(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,
    grammar: CandidateGrammar,
    noise_floor: float = 1.0,
    n_refits: int = 20,
    rng_seed: int = 0,
    absent_slot_area_fraction: float = ABSENT_SLOT_AREA_FRACTION,
    absent_slot_persistence_threshold: float = ABSENT_SLOT_PERSISTENCE_THRESHOLD,
    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY,
    enable_proposal_pass: bool = True,
    candidate_filter: Optional[list[str]] = None,
    enable_preseed: bool = True,
    progress_cb: Optional[Callable[[dict], None]] = None,
    fit_full_window: bool = False,
) -> ComparisonResult:
    """
    Full pipeline over ``grammar.candidates`` for one spectral window.

    ``fit_full_window`` (Find Peaks UI, 2026-07-13): OPTIONAL, default
    False — zero behavior change for every existing caller. When True,
    relaxes each candidate's primary-slot center bound per
    ``_full_window_bound_overrides`` (outer envelope only for curated
    multi-component models; full ROI for detection/structural-fallback
    slots) instead of the region module's fixed literature window.
    Threaded through every place a candidate's initial/refit parameters
    get built from scratch (screen fit, deep-phase primary fit, stability
    refits, the proposal pass, and the bound-fixed decisive-override
    refit) so the relaxed bound is consistent across a candidate's whole
    lifecycle.

    ``candidate_filter`` limits the run to the named candidates (useful for
    fast tests / method options); None = all.  ``enable_preseed`` gates the
    pre-fit out-of-grammar dominant seeding (unit F1) — detection-driven, so
    it is a no-op on spectra whose prominent features the grammar covers.

    ``progress_cb`` (Find Peaks UI, 2026-07-11): OPTIONAL, default None —
    zero behavior/perf change for every existing caller.  When given, it is
    invoked with ``{"phase": "screening"|"stabilizing", "candidate_index",
    "candidate_total", "candidate_name"}`` right before each candidate's
    fit — the REAL screen->stabilize sweep progress (unit F3), not a fake
    animation.  A raising callback is swallowed (never lets a progress sink
    break the analysis — the honesty/result contract outranks the nicety).
    """
    candidates = grammar.candidates
    if candidate_filter is not None:
        wanted = set(candidate_filter)
        candidates = [c for c in candidates if c.name in wanted]
    diagnostic_windows = dict(grammar.diagnostic_windows)

    preseed_specs: list[PreseedSpec] = []
    pool = None
    pool_error: Optional[str] = None
    detection_overflow: list[dict] = []
    if enable_preseed and (candidates or not grammar.candidates):
        # Detection-only background: today every candidate in a resolved
        # grammar shares one background family (C 1s/B 1s/Cl 2p/U 4f modules
        # are each homogeneous), so the first candidate's is representative.
        # A future mixed-background grammar only affects DETECTION here —
        # each candidate still fits with its own background.  Structural-
        # fallback regions (ZERO grammar candidates — the across-the-
        # periodic-table path) default to Shirley, the standard core-level
        # background (CLAUDE.md convention).
        det_bg_family = (candidates[0].background if candidates
                         else BackgroundType.SHIRLEY)
        det_bg = _compute_background(x, y, det_bg_family)
        preseed_specs = detect_out_of_grammar_dominants(
            x, y, det_bg, candidates, diagnostic_windows,
            noise_floor=noise_floor,
        )
        # Candidate-generation layer (autofit.candidates): overcomplete,
        # provenance-tagged pool.  The reviewed dominant channel above is
        # UNCHANGED; the pool's CWT curvature channel adds seeds the
        # local-max view structurally cannot produce — shoulders with no
        # local maximum, and resolved close pairs the dominant channel's
        # duplicate suppression discards (the measured ds7/ds8 loss
        # classes).  Seeding gates reuse the SAME reviewed constants;
        # detection proposes, selection judges.
        # Defense-in-depth: the layer is an ADD-ON — an unexpected failure
        # inside it degrades to dominant-channel-only seeding with the
        # error surfaced in the payload, never a dead analysis.
        try:
            pool = build_candidate_pool(
                x, y, det_bg,
                all_windows=_all_grammar_windows(candidates, diagnostic_windows),
                labeled_windows=dict(diagnostic_windows),
                dominant_seeds=[s.payload() for s in preseed_specs],
                noise_floor=noise_floor,
                min_fraction_of_max=CURVATURE_SEED_MIN_FRACTION,
                amplitude_snr=PRESEED_AMPLITUDE_SNR,
                coincidence_ev=PROPOSAL_COINCIDENCE_BE,
                max_total_seeds=SEED_MAX_TOTAL,
                smooth_points=PRESEED_SMOOTH_POINTS,
                fwhm_clip=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
                local_window_ev=PROPOSAL_WINDOW_WIDTH,
            )
        except Exception as exc:        # noqa: BLE001 — surfaced, not silent
            log.exception("candidate pool layer failed — degrading to "
                          "dominant-channel-only seeding")
            pool = None
            pool_error = f"{type(exc).__name__}: {exc}"
        if pool is not None:
            preseed_specs = preseed_specs + [
                PreseedSpec(
                    role=s.role, center_init=s.center_be,
                    fwhm_init=s.fwhm_init, amplitude_net=s.amplitude_net,
                    fraction_of_max=s.fraction_of_max, local_snr=s.local_snr,
                    provenance="curvature_shoulder", prom_z=s.prom_z,
                )
                for s in pool.curvature_seeds
            ]
        preseed_specs.sort(key=lambda s: s.center_init)
        if preseed_specs:
            log.info(
                "compare_models: %d out-of-grammar feature(s) pre-seeded "
                "at %s (%s; region-unassigned; human assignment required)",
                len(preseed_specs),
                [round(s.center_init, 2) for s in preseed_specs],
                [s.provenance for s in preseed_specs],
            )
            # Stage-2 (chokepoint 5, measured): augmenting EVERY grammar
            # family with the full seed set made all 29 screen fits blow
            # the nfev cap (0 converged → no survivor).  Grammar families
            # get a LIGHT augmentation — dominant seeds always, then the
            # strongest curvature seeds up to GRAMMAR_AUGMENT_MAX_SEEDS —
            # while the detection-driven family below carries the FULL
            # detected structure in one cheap, well-initialized model.
            dom_specs = [s for s in preseed_specs
                         if s.provenance == "local_max"]
            cwt_specs = sorted(
                (s for s in preseed_specs if s.provenance != "local_max"),
                key=lambda s: s.amplitude_net, reverse=True)
            augment_specs = (dom_specs + cwt_specs)[:GRAMMAR_AUGMENT_MAX_SEEDS]
            augment_specs.sort(key=lambda s: s.center_init)
            augment_roles = {s.role for s in augment_specs}
            if candidates:
                candidates = [_preseed_augmented(c, augment_specs)
                              for c in candidates]
            # The detection family: slots ARE the detected features (all
            # channels, window-containment-independent), region-unassigned,
            # absent-eligible.  Built ONLY when detection found structure
            # the grammar cannot express (preseed_specs non-empty), so
            # grammar-covered spectra keep a byte-identical candidate set.
            if pool is not None:
                det_model, det_dropped = build_detection_candidate(
                    pool, det_bg_family,
                    step_ev=float(np.median(np.abs(np.diff(x)))),
                )
                detection_overflow = det_dropped
                if det_dropped:
                    # LOUD overflow (Codex Stage-2, both runs MAJOR): the
                    # dropped features stay named in the log and in the
                    # pool payload (detection_model_overflow key).
                    log.warning(
                        "detection family overflow: %d feature(s) beyond "
                        "the slot cap dropped by amplitude: %s",
                        len(det_dropped),
                        [d["center_be"] for d in det_dropped])
                if det_model is not None:
                    # FIRST in sweep order: the detection family is the
                    # cheapest, best-initialized candidate, and the screen
                    # phase truncates under its wall budget on rich scans
                    # (measured: appended last, it was never screened at
                    # 21/30) — a budget truncation must never be able to
                    # drop the completeness carrier.
                    candidates = [det_model] + candidates
                    log.info(
                        "compare_models: detection family '%s' joins the "
                        "sweep with %d slot(s) at %s",
                        det_model.name, len(det_model.slots),
                        [round(0.5 * (s.be_window[0] + s.be_window[1]), 2)
                         for s in det_model.slots])
        else:
            augment_roles = set()
    else:
        augment_roles = set()

    reports: list[ModelReport] = []
    non_converged: list[tuple[CandidateModel, FitOutcome]] = []
    proposal_attempts: list[tuple[str, ProposedPeakReport]] = []
    timings: list[ProposalPassTiming] = []
    n_cand = len(candidates)
    sweep_start = time.perf_counter()
    n_evaluated = 0
    analysis_truncated = False

    # ── Unit F3: screen phase (only for candidate sets larger than the
    #    deep-evaluation budget — every existing gate/battery path is ≤
    #    SCREEN_TOP_K and unchanged) ─────────────────────────────────────
    screen_record: Optional[list[dict]] = None
    screen_fit: dict[str, FitOutcome] = {}
    if n_cand > SCREEN_TOP_K:
        screen_rows: list[dict] = []
        screened: list[tuple[CandidateModel, FitOutcome, float]] = []
        screen_deadline = sweep_start + SCREEN_BUDGET_FRACTION * TOTAL_ANALYSIS_TIMEOUT_SEC
        for idx, model in enumerate(candidates, 1):
            if time.perf_counter() > screen_deadline:
                analysis_truncated = True
                log.warning(
                    "compare_models: screen budget (%.0f%% of the sweep) "
                    "exhausted after %d/%d candidates — the deep phase runs "
                    "on what screened so far",
                    100 * SCREEN_BUDGET_FRACTION, idx - 1, n_cand)
                break
            log.info("[screen %2d/%d] %s", idx, n_cand, model.name)
            _report_progress(progress_cb, "screening", idx, n_cand, model.name)
            outcome = fit_candidate(x, y, weights, model,
                                    max_nfev=SCREEN_MAX_NFEV,
                                    fit_full_window=fit_full_window)
            if outcome.converged:
                bic = compute_bic(outcome)
                screened.append((model, outcome, bic))
                screen_rows.append({"name": model.name, "converged": True,
                                    "bic": float(bic), "selected": False})
            else:
                non_converged.append((model, outcome))
                screen_rows.append({"name": model.name, "converged": False,
                                    "bic": None, "selected": False})
        screened.sort(key=lambda t: t[2])
        selected_models = screened[:SCREEN_TOP_K]
        selected_names = {m.name for m, _, _ in selected_models}
        for row in screen_rows:
            row["selected"] = row["name"] in selected_names
        screen_record = screen_rows
        screen_fit = {m.name: o for m, o, _ in selected_models}
        candidates = [m for m, _, _ in selected_models]
        log.info(
            "compare_models: screen kept %d/%d candidates for deep "
            "evaluation: %s", len(candidates), n_cand,
            [m.name for m in candidates])

    for idx, model in enumerate(candidates, 1):
        # Pre-check with the candidate's own worst-case budget: a candidate
        # STARTED just under the wire used to overshoot the sweep budget by
        # its full stability + proposal cost (measured 310 s wall vs the
        # 240 s budget on real data — past the gunicorn --timeout 300, i.e.
        # the exact worker-kill this budget exists to prevent).  Truncating
        # BEFORE starting a candidate that cannot finish keeps the worst-case
        # wall ≈ TOTAL_ANALYSIS_TIMEOUT_SEC.
        elapsed = time.perf_counter() - sweep_start
        if elapsed > TOTAL_ANALYSIS_TIMEOUT_SEC - CANDIDATE_TIMEOUT_SEC:
            analysis_truncated = True
            log.warning(
                "compare_models: sweep budget cannot fit another candidate "
                "(%.0fs elapsed of %.0fs) after %d/%d — remaining candidates "
                "skipped, returning best-so-far",
                elapsed, TOTAL_ANALYSIS_TIMEOUT_SEC, n_evaluated, len(candidates),
            )
            break
        n_evaluated += 1
        log.info("[%2d/%d] %s: primary fit", idx, len(candidates), model.name)
        _report_progress(progress_cb, "stabilizing", idx, len(candidates),
                         model.name)
        # Shared wall-clock budget for this candidate's primary fit + all its
        # stability refits (CANDIDATE_TIMEOUT_SEC) — see run_stability_analysis.
        candidate_deadline = time.perf_counter() + CANDIDATE_TIMEOUT_SEC
        # reuse the screen fit as this candidate's primary (no repeated work)
        primary = screen_fit.get(model.name) or fit_candidate(
            x, y, weights, model, fit_full_window=fit_full_window)
        if not primary.converged:
            non_converged.append((model, primary))
            continue

        stability = run_stability_analysis(
            x, y, weights, model, primary,
            noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
            deadline=candidate_deadline,
            fit_full_window=fit_full_window,
        )
        # Promote a deeper minimum found by the multi-start pass (see
        # ModelStability.best_outcome).
        if (stability.best_outcome is not None
                and stability.best_outcome.weighted_chi_sq
                < primary.weighted_chi_sq):
            primary = stability.best_outcome
        y_fit = (primary.lmfit_result.best_fit +
                 (primary.background if primary.background is not None else 0.0)
                 if primary.lmfit_result is not None else np.zeros_like(y))
        residuals = compute_residual_diagnostics(x, y, y_fit, noise_floor, diagnostic_windows)
        slot_areas = compute_slot_areas(model, primary, x)
        absent = _identify_absent_slots(
            model, stability, slot_areas, primary,
            persistence_threshold=absent_slot_persistence_threshold,
            area_fraction_threshold=absent_slot_area_fraction,
        )
        base_report = ModelReport(
            model=model, primary_fit=primary, bic=compute_bic(primary),
            stability=stability, residuals=residuals,
            plausibility=PlausibilityFlags(
                boundary_hits=list(primary.boundary_hits),
                unphysical_widths=_unphysical_width_flags(primary.components, model),
                orphan_peaks=stability.orphan_rate > 0.1,
            ),
            absent_slots=absent,
        )

        final_report = base_report
        if enable_proposal_pass:
            # Unit F2: ITERATIVE rounds — each accepted proposal makes the
            # augmented report the new base, detection re-runs on ITS
            # residual, and the next round may accept another peak (up to
            # PROPOSAL_MAX_PER_CANDIDATE total), all under ONE shared
            # per-candidate wall budget.  Gates are unchanged per round.
            counts = dict(n_flagged=0, n_over_cap=0, n_attempted=0,
                          n_fast=0, n_stab=0, n_acc=0)
            timed_out = False
            pass_start = time.perf_counter()
            # the pass never spends beyond the sweep's remaining budget —
            # same worst-case-wall reasoning as the candidate pre-check
            pass_budget = min(
                PROPOSAL_CANDIDATE_TIMEOUT_SEC,
                TOTAL_ANALYSIS_TIMEOUT_SEC - (pass_start - sweep_start))
            rejected: list[ProposedPeakReport] = []
            current = base_report
            current_y_fit = y_fit
            while counts["n_acc"] < PROPOSAL_MAX_PER_CANDIDATE:
                if time.perf_counter() - pass_start > pass_budget:
                    timed_out = True
                    break
                specs = _detect_residual_proposals(
                    x, y, current_y_fit, noise_floor, current.model,
                    fitted_components=current.primary_fit.components,
                )
                # roles must stay unique across rounds — number this round's
                # specs from one past the HIGHEST existing suffix (never a
                # count: see _next_proposal_index for the collision this
                # avoids)
                base_idx = _next_proposal_index(current.model)
                for j, spec in enumerate(specs):
                    spec.role = f"proposed_peak_{base_idx + j}"
                attempts = specs[:PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE]
                counts["n_flagged"] += len(specs)
                counts["n_over_cap"] += max(len(specs) - len(attempts), 0)
                accepted_this_round = False
                for spec in attempts:
                    elapsed = time.perf_counter() - pass_start
                    if elapsed > pass_budget:
                        timed_out = True
                        break
                    counts["n_attempted"] += 1
                    aug_report, pr, outcome = _attempt_proposal(
                        x=x, y=y, weights=weights, base_report=current, spec=spec,
                        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
                        absent_slot_area_fraction=absent_slot_area_fraction,
                        absent_slot_persistence_threshold=absent_slot_persistence_threshold,
                        diagnostic_windows=diagnostic_windows,
                        budget_remaining=pass_budget - elapsed,
                        fit_full_window=fit_full_window,
                    )
                    proposal_attempts.append((model.name, pr))
                    if outcome == "accepted" and aug_report is not None:
                        counts["n_acc"] += 1
                        # carry earlier rounds' accepted-peak reports forward
                        # (base_report starts with [], so round 1 is a no-op)
                        aug_report.proposed_peaks = (
                            list(current.proposed_peaks) + aug_report.proposed_peaks)
                        current = aug_report
                        pf = current.primary_fit
                        current_y_fit = (
                            pf.lmfit_result.best_fit + pf.background
                            if pf.lmfit_result is not None else np.zeros_like(y))
                        accepted_this_round = True
                        break
                    rejected.append(pr)
                    counts["n_fast" if outcome == "fast_rejected" else "n_stab"] += 1
                if not accepted_this_round:
                    break
            final_report = current
            if rejected:
                # rejected attempts stay visible on whichever report we emit
                final_report.proposed_peaks = final_report.proposed_peaks + rejected
            timings.append(ProposalPassTiming(
                candidate_name=model.name, n_flagged=counts["n_flagged"],
                n_over_cap=counts["n_over_cap"],
                n_attempted=counts["n_attempted"], n_fast_rejected=counts["n_fast"],
                n_stability_rejected=counts["n_stab"], n_accepted=counts["n_acc"],
                wall_time_sec=time.perf_counter() - pass_start, timed_out=timed_out,
            ))

        reports.append(final_report)

    result = rank_and_filter(
        reports,
        persistence_threshold=persistence_threshold,
        bic_ambiguity_threshold=bic_ambiguity_threshold,
        allow_last_resort=bool(preseed_specs),
    )
    result = _apply_decisive_override(
        x, y, weights, result,
        persistence_threshold=persistence_threshold,
        diagnostic_windows=diagnostic_windows,
        noise_floor=noise_floor,
        n_refits=n_refits,
        rng_seed=rng_seed,
        fit_full_window=fit_full_window,
    )
    result.non_converged = non_converged
    result.cross_candidate_coincidences = _cross_candidate_coincidences(proposal_attempts)
    result.proposal_pass_timings = timings
    result.analysis_truncated = analysis_truncated
    result.n_candidates_evaluated = n_evaluated
    result.n_candidates_total = n_cand
    # honest augmentation bookkeeping: every detected seed is surfaced;
    # the flag says whether it augmented the grammar families or rides in
    # the detection family only (GRAMMAR_AUGMENT_MAX_SEEDS cap)
    result.preseeded_features = [
        {**s.payload(), "augmented_into_grammar": s.role in augment_roles}
        for s in preseed_specs]
    result.screen = screen_record
    if pool is not None:
        # honesty surface: the full pool payload, with the F2 residual-
        # proposal attempts merged in as the 'residual_gap' source (dedup
        # by the same coincidence tolerance the seeds use)
        pool_payload = pool.payload()
        merge_residual_attempts(
            pool_payload,
            [{"center_be": (pr.fitted_center
                            if pr.fitted_center is not None
                            else pr.proposed_center_init),
              "accepted": bool(pr.accepted)}
             for _, pr in proposal_attempts],
            coincidence_ev=PROPOSAL_COINCIDENCE_BE,
            proposal_pass_ran=enable_proposal_pass,
        )
        # loud detection-family truncation record (Codex Stage-2 MAJOR):
        # names every feature the slot cap dropped (empty = no overflow)
        pool_payload["detection_model_overflow"] = detection_overflow
        result.candidate_pool = pool_payload
    elif pool_error is not None:
        result.candidate_pool = {
            "error": pool_error,
            "note": "candidate-generation layer failed — analysis degraded "
                    "to dominant-channel-only seeding (see server log)",
        }

    # Result-level honesty flag (stress-suite finding 0 — burial measured
    # at ΔBIC* +74…+944): a FILTERED candidate whose BIC* decisively beats
    # the emitted winner must be visible at the RESULT level, not only in
    # the candidate table.  Purely additive: ranking, filtering, and the
    # promotion rules are unchanged — this only reports what they buried.
    if result.survivors:
        win_bic = result.survivors[0].bic_adjusted
        # promotion LINEAGE, not just names: a decisive-override winner is
        # renamed "X+bfix" while its free original "X" stays in
        # filtered_out — flagging the original as "buried" would name the
        # very candidate that was promoted (Codex analyze review blocker)
        survivor_names = set()
        for r in result.survivors:
            survivor_names.add(r.model.name)
            if r.model.name.endswith("+bfix"):
                survivor_names.add(r.model.name[:-len("+bfix")])
            if r.augmented_from:
                survivor_names.add(r.augmented_from)
        dominant = None
        for rep, why in result.filtered_out:
            if rep.model.name in survivor_names:
                continue        # promoted members / their free originals
            if win_bic - rep.bic_adjusted > CONDITIONAL_OVERRIDE_DELTA_BIC:
                if dominant is None or rep.bic_adjusted < dominant[0].bic_adjusted:
                    dominant = (rep, why)
        if dominant is not None:
            rep, why = dominant
            result.filtered_dominant_alternative = {
                "name": rep.model.name,
                "bic_star": float(rep.bic_adjusted),
                "delta_bic_vs_winner": float(win_bic - rep.bic_adjusted),
                "filter_reason": why,
            }
    result.weighted_ic_disagreement = _weighted_ic_disagreement(
        result.survivors)
    return result


def _weighted_ic_disagreement(survivors: "list[ModelReport]") -> Optional[dict]:
    """Result-level flag when the weighted-χ² BIC (consistent with the fit
    weights) tops a different survivor than the ranking's RSS-form BIC*."""
    if len(survivors) < 2:
        return None
    weighted_top = min(survivors, key=lambda r: r.bic_weighted)
    if weighted_top.model.name == survivors[0].model.name:
        return None
    return {
        "rss_bic_top": survivors[0].model.name,
        "weighted_bic_top": weighted_top.model.name,
        "note": "the weighted-χ² criterion (consistent with the fit "
                "weights) prefers a different survivor — model selection "
                "is noise-model-sensitive on this spectrum; treat the "
                "ranking as CONDITIONAL on the homoscedastic-RSS form",
    }
