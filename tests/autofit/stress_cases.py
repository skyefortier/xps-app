"""
Synthetic hard-case library for the method stress suite (run-brief item:
"validate EVERY method against KNOWN ground truth in the regimes the real
anchors lack").

Every case is generated from a KNOWN parameter-level ground truth with
counting noise (Poisson, seeded — so the canonical 1/sqrt(counts) weights
are CORRECT by construction here; the noise-model unit stresses the
mis-specified-weights question separately).  Backgrounds are kept EXACTLY
expressible (linear) in every regime except the background-mismatch regime,
so failures isolate each regime's intended difficulty.

Expectation classes (the KEY CRITERION of the run brief):
- ``recover``    — the data distinguishes the models; the method must
                   recover the true structure/parameters.
- ``ambiguous``  — the data does NOT distinguish the models; the method
                   must REPORT ambiguity (ambiguous_pairs / conditional /
                   selection warnings / wide posteriors), never confidently
                   pick one.
- ``prune``      — the candidate set is over-specified; extra components
                   must be pruned/absent-classified, not invented.
- ``honesty``    — the truth is OUTSIDE the model space (asymmetric truth,
                   charging replica, wrong background); the method must
                   surface the mismatch (elevated χ²ᵣ, residual flags,
                   proposals), not silently absorb it.

Fictional region label "SYN 2x" keeps synthetic candidates clearly apart
from the lit-cited region cookbook; windows/bounds here are test scaffolds,
not physics constants.

MEASURED χ²ᵣ FLOOR (2026-07-04, deliberate design property): the truth
peaks carry a 30% Lorentzian mix, so their tails are ~150-220 counts above
the true baseline at the ROI edges — and the engine's LINEAR background is
anchored on those (noisy, tail-loaded) endpoints.  At the TRUE parameters
the engine-background χ²ᵣ is therefore not 1: measured 0.96 with the true
baseline vs 34 with the engine background at height 90000 (≈2 at 9000 —
the systematic bias scales with height while noise scales with √height).
This is the REALISTIC background-subtraction problem, kept on purpose:
model-SELECTION conclusions share the bias across candidates, but absolute
χ²ᵣ-target criteria are miscalibrated under it — quantified evidence for
the noise-model work item (see stress-test-report.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from autofit.grammar import (
    BackgroundType,
    CandidateGrammar,
    CandidateModel,
    ComponentSlot,
    LineShape,
)
from fitting import _SHAPE_FUNCS

_pv = _SHAPE_FUNCS["pseudo_voigt_gl"]
_ds = _SHAPE_FUNCS["doniach_sunjic"]

REGION = "SYN 2x"
PHASE = "syn"
STEP = 0.05
ETA = 0.30                     # generator GL mix (matches engine PV default)


@dataclass
class StressCase:
    name: str
    regime: str
    expectation: str                     # recover | ambiguous | prune | honesty
    x: np.ndarray
    y: np.ndarray
    truth: list[dict]                    # [{center, fwhm, height}] generator params
    grammar: CandidateGrammar
    truth_n: int
    ls_specs: Optional[list[dict]] = None    # true-structure manual model
    bg: str = "linear"                       # generator background family
    notes: str = ""
    # names of grammar candidates with the TRUE component count
    true_candidates: tuple[str, ...] = ()


def _grid(lo=190.0, hi=205.0):
    return np.arange(lo, hi, STEP)


def _linear_bg(x, b0=300.0, slope=0.0):
    return b0 + slope * (x - x[0])


def _shirley_like_bg(x, signal, k=0.15, b0=300.0):
    """Integral (Shirley-shaped) background: proportional to the signal area
    at higher BE — deliberately NOT a straight line."""
    # BE axis ascends; Shirley steps up on the high-BE side of peaks
    csum = np.cumsum(signal[::-1])[::-1] * STEP
    return b0 + k * (csum.max() - csum)


def _noisy(y_true, seed):
    rng = np.random.default_rng(seed)
    return rng.poisson(np.maximum(y_true, 0.0)).astype(float)


def _slot(role, window, fwhm=(0.6, 2.5), shape=LineShape.PSEUDO_VOIGT, **kw):
    return ComponentSlot(role=role, region=REGION, phase_id=PHASE,
                         be_window=window, line_shape=shape,
                         fwhm_range=fwhm, **kw)


def _cand(name, slots, bg=BackgroundType.LINEAR):
    return CandidateModel(name=name, background=bg, slots=tuple(slots))


def _grammar(candidates, windows=None):
    return CandidateGrammar(
        regions=(REGION,), phase_ids=(PHASE,), candidates=list(candidates),
        diagnostic_windows=windows or {}, notes=["synthetic stress grammar"],
        provenance={},
    )


def _ls_specs(truth, shape="pseudo_voigt_gl"):
    return [{"id": str(i + 1), "shape": shape, "center": t["center"],
             "amplitude": t["height"], "fwhm": t["fwhm"], "glMix": ETA * 100}
            for i, t in enumerate(truth)]


def _n_peak_ladder(c1, c2, n_max=4, fwhm=(0.6, 2.5), half=2.0,
                   bg=BackgroundType.LINEAR):
    """1..n_max-component candidates with DISTINCT slot windows — the
    engine's slot-role identity contract: cross-refit matching identifies
    components BY WINDOW, so identical windows label-switch across refits
    and zero out persistence (measured: minpers=0.00, orphan_peaks=True).
    Real region grammars always give each species its own window; the
    ladder mirrors that.

    P1: one window over the doublet span.  P2: split at the true-centers
    midpoint.  P3+: flanking windows where NO truth exists — absent-slot /
    pruning territory."""
    mid = 0.5 * (c1 + c2)
    lo, hi = c1 - half, c2 + half
    windows = {
        1: [(lo, hi)],
        2: [(lo, mid), (mid, hi)],
        3: [(lo, mid), (mid, hi), (hi, hi + 2.5)],
        4: [(lo - 2.5, lo), (lo, mid), (mid, hi), (hi, hi + 2.5)],
        5: [(lo - 2.5, lo), (lo, mid), (mid, hi), (hi, hi + 2.5),
            (hi + 2.5, hi + 5.0)],
    }
    out = []
    for n in range(1, n_max + 1):
        slots = [_slot(f"main_{chr(97 + i)}", w, fwhm)
                 for i, w in enumerate(windows[n])]
        out.append(_cand(f"P{n}", slots, bg=bg))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Regime 1 — heavy overlap: two equal-width peaks at k×FWHM separation
# ─────────────────────────────────────────────────────────────────────────────

def overlap_case(sep_frac: float, height: float, seed: int,
                 expectation: str) -> StressCase:
    x = _grid()
    fwhm = 1.2
    c1 = 197.2
    c2 = c1 + sep_frac * fwhm
    truth = [{"center": c1, "fwhm": fwhm, "height": height},
             {"center": c2, "fwhm": fwhm, "height": 0.7 * height}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    return StressCase(
        name=f"overlap_sep{sep_frac:g}_h{height:g}",
        regime="heavy_overlap", expectation=expectation,
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(_n_peak_ladder(c1, c2, n_max=3)),
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
        notes=f"separation {sep_frac}×FWHM, heights {height:g}/{0.7*height:g}",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Regime 2 — low-S/N minor component
# ─────────────────────────────────────────────────────────────────────────────

def weak_minor_case(minor_frac: float, height: float, seed: int,
                    expectation: str) -> StressCase:
    x = _grid()
    truth = [{"center": 197.0, "fwhm": 1.2, "height": height},
             {"center": 198.8, "fwhm": 1.2, "height": minor_frac * height}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    return StressCase(
        name=f"weak_minor_{minor_frac:g}_h{height:g}",
        regime="weak_minor", expectation=expectation,
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(_n_peak_ladder(197.0, 198.8, n_max=3)),
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
        notes=f"minor = {minor_frac:.0%} of main at +1.8 eV",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Regime 3 — over-specified candidate set (must prune, not invent)
# ─────────────────────────────────────────────────────────────────────────────

def overspecified_case(seed: int) -> StressCase:
    x = _grid()
    truth = [{"center": 196.8, "fwhm": 1.1, "height": 8000.0},
             {"center": 199.4, "fwhm": 1.3, "height": 5000.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    return StressCase(
        name="overspecified_2true_5max",
        regime="overspecified", expectation="prune",
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(_n_peak_ladder(196.8, 199.4, n_max=5)),
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
        notes="truth 2 well-separated peaks; menu offers up to 5",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Regime 4 — differential-charging replica (truth outside the model space)
# ─────────────────────────────────────────────────────────────────────────────

def charging_tail_case(seed: int, with_replica_candidate: bool) -> StressCase:
    x = _grid()
    main = {"center": 197.8, "fwhm": 1.2, "height": 9000.0}
    replica = {"center": 197.0, "fwhm": 1.2, "height": 0.25 * 9000.0}
    truth = [main, replica]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _linear_bg(x), seed)
    one = _cand("single_main", [_slot("main_a", (196.5, 199.0))])
    cands = [one]
    if with_replica_candidate:
        cands.append(_cand("main_plus_replica", [
            _slot("main_a", (197.4, 199.4)),
            _slot("replica", (195.4, 197.4)),
        ]))
    return StressCase(
        name=("charging_with_replica_candidate" if with_replica_candidate
              else "charging_no_replica_candidate"),
        regime="charging_tail",
        expectation="recover" if with_replica_candidate else "honesty",
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(cands),
        ls_specs=_ls_specs(truth),
        true_candidates=("main_plus_replica",) if with_replica_candidate else (),
        notes="25% replica at −0.8 eV (differential charging shape)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Regime 5 — asymmetric (DS) truth vs symmetric-only candidates
# ─────────────────────────────────────────────────────────────────────────────

def asym_truth_case(seed: int, with_asym_candidate: bool) -> StressCase:
    x = _grid()
    height, center, fwhm, alpha = 9000.0, 197.8, 1.2, 0.18
    sig = _ds(x, height, center, fwhm, alpha, 0.4)
    y = _noisy(sig + _linear_bg(x), seed)
    sym = _cand("sym_main", [_slot("main_a", (196.5, 199.5))])
    cands = [sym]
    if with_asym_candidate:
        cands.append(_cand("asym_main", [
            _slot("main_a", (196.5, 199.5), shape=LineShape.DS)]))
    return StressCase(
        name=("asym_truth_with_asym_candidate" if with_asym_candidate
              else "asym_truth_symmetric_only"),
        regime="asym_truth",
        expectation="recover" if with_asym_candidate else "honesty",
        x=x, y=y,
        truth=[{"center": center, "fwhm": fwhm, "height": height,
                "ds_alpha": alpha}],
        truth_n=1,
        grammar=_grammar(cands),
        ls_specs=[{"id": "1", "shape": "doniach_sunjic", "center": center,
                   "amplitude": height, "fwhm": fwhm, "dsAlpha": alpha,
                   "dsGamma": 0.4}],
        true_candidates=("asym_main",) if with_asym_candidate else (),
        notes=f"DS truth α={alpha}; high-BE tail",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Regime 6 — background mismatch (Shirley-shaped truth, linear-only fits)
# ─────────────────────────────────────────────────────────────────────────────

def bg_mismatch_case(seed: int) -> StressCase:
    x = _grid()
    truth = [{"center": 197.2, "fwhm": 1.2, "height": 9000.0},
             {"center": 198.9, "fwhm": 1.2, "height": 6300.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
    return StressCase(
        name="bg_shirley_truth_linear_fit",
        regime="bg_mismatch", expectation="honesty",
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(_n_peak_ladder(197.2, 198.9, n_max=3)),  # LINEAR bg
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
        bg="shirley_like",
        notes="integral background fit with a straight line — the mismatch "
              "must surface, not silently vanish",
    )


def bg_matched_control_case(seed: int) -> StressCase:
    """Control for the mismatch case: same truth, Shirley-candidate fits.
    The engine's iterative Shirley should absorb the integral background."""
    x = _grid()
    truth = [{"center": 197.2, "fwhm": 1.2, "height": 9000.0},
             {"center": 198.9, "fwhm": 1.2, "height": 6300.0}]
    sig = sum(_pv(x, t["height"], t["center"], t["fwhm"], ETA) for t in truth)
    y = _noisy(sig + _shirley_like_bg(x, sig), seed)
    cands = _n_peak_ladder(197.2, 198.9, n_max=3, bg=BackgroundType.SHIRLEY)
    return StressCase(
        name="bg_shirley_truth_shirley_fit",
        regime="bg_mismatch", expectation="recover",
        x=x, y=y, truth=truth, truth_n=2,
        grammar=_grammar(cands),
        ls_specs=_ls_specs(truth),
        true_candidates=("P2",),
        bg="shirley_like",
        notes="control: matched background family",
    )


# ─────────────────────────────────────────────────────────────────────────────
# The roster
# ─────────────────────────────────────────────────────────────────────────────

def build_all_cases(seed_offset: int = 0) -> list[StressCase]:
    """The full battery roster (seeds fixed; deterministic).  A nonzero
    ``seed_offset`` regenerates the SAME truths under fresh noise draws —
    conclusion-stability replicates for the battery."""
    o = seed_offset
    return [
        # heavy overlap — resolvable at wide separation/high counts,
        # honestly ambiguous at 0.4×FWHM with low counts
        overlap_case(1.0, 9000.0, seed=11 + o, expectation="recover"),
        overlap_case(0.7, 9000.0, seed=12 + o, expectation="recover"),
        # 0.4×FWHM at high counts: a-priori labeled ambiguous, but the
        # 2026-07-04 battery measured the EVIDENCE decisively favoring P2
        # on every noise draw (ΔBIC* 74-97, P2 stable at persistence
        # 0.92-1.0) — the data distinguishes; the current filter pipeline
        # buries the dominant candidate (orphan matching) → relabeled
        # recover; its FAILs are a measured engine deficiency (see
        # stress-test-report.md finding on evidence burial), not noise.
        overlap_case(0.4, 9000.0, seed=13 + o, expectation="recover"),
        # at low counts the parsimony choice genuinely wins the evidence
        # (P1 ΔBIC* 5-12 below P2 on every draw) — truly ambiguous
        overlap_case(0.4, 900.0, seed=14 + o, expectation="ambiguous"),
        # weak minor — detectable at high counts; the low-count case was
        # a-priori labeled "ambiguous" but MEASURED recoverable (2026-07-04
        # battery: IC picks P2 on every noise draw, Bayes picks P2 with an
        # honest budget warning) → relabeled recover; the battery JSONL
        # rows generated under the old label carry the
        # confident_true(RELABEL?) classification documenting exactly this.
        # The minor's fitted center wobbles ±0.16 eV at these counts.
        weak_minor_case(0.03, 90000.0, seed=21 + o, expectation="recover"),
        weak_minor_case(0.03, 2000.0, seed=22 + o, expectation="recover"),
        # over-specification
        overspecified_case(seed=31 + o),
        # charging replica
        charging_tail_case(seed=41 + o, with_replica_candidate=False),
        charging_tail_case(seed=42 + o, with_replica_candidate=True),
        # asymmetric truth
        asym_truth_case(seed=51 + o, with_asym_candidate=False),
        asym_truth_case(seed=52 + o, with_asym_candidate=True),
        # background mismatch + control
        bg_mismatch_case(seed=61 + o),
        bg_matched_control_case(seed=62 + o),
    ]
