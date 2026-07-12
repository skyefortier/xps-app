"""
Method 2 — grammar + information-criterion model comparison (fitalg engine).

Runs the full comparison pipeline over a resolved grammar and returns the
top survivor's decomposition, per-slot confidence vectors, and the complete
candidate/criteria record for the ``analysis`` namespace.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import numpy as np

from ..confidence import build_confidence_vector
from ..criteria import build_criteria_panel
from ..engine import ComparisonResult, ModelReport, compare_models, _slot_prefix
from ..grammar import BACKEND_SHAPE, CandidateGrammar
from .base import MethodResult, PeakFitMethod, poisson_like_weights

_ALLOWED_OPTIONS = {
    "noise_floor", "n_refits", "rng_seed", "candidate_filter",
    "enable_proposal_pass", "persistence_threshold", "bic_ambiguity_threshold",
    "absent_slot_area_fraction", "absent_slot_persistence_threshold",
    "enable_preseed",
}

ENGINE_VERSION = "autofit-stage2"


class ICModelComparisonMethod(PeakFitMethod):
    id = "ic_model_comparison"
    label = "Auto — model comparison (IC)"
    requires_grammar = True

    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> MethodResult:
        if grammar is None:
            raise ValueError("ic_model_comparison requires a resolved grammar")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown ic_model_comparison options: {sorted(unknown)}")

        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        w = np.asarray(weights, dtype=float) if weights is not None \
            else poisson_like_weights(y)
        noise_floor = float(opts.pop("noise_floor", 1.0))

        result = compare_models(
            x, y, w, grammar,
            noise_floor=noise_floor,
            n_refits=int(opts.pop("n_refits", 20)),
            rng_seed=int(opts.pop("rng_seed", 0)),
            candidate_filter=opts.pop("candidate_filter", None),
            enable_proposal_pass=bool(opts.pop("enable_proposal_pass", True)),
            enable_preseed=bool(opts.pop("enable_preseed", True)),
            persistence_threshold=float(opts.pop("persistence_threshold", 0.7)),
            bic_ambiguity_threshold=float(opts.pop("bic_ambiguity_threshold", 2.0)),
            absent_slot_area_fraction=float(opts.pop("absent_slot_area_fraction", 0.02)),
            absent_slot_persistence_threshold=float(
                opts.pop("absent_slot_persistence_threshold", 0.7)),
            progress_cb=progress_cb,
        )

        analysis = build_analysis_record(grammar, result)
        truncation_note = (
            f"analysis truncated — {result.n_candidates_evaluated} of "
            f"{result.n_candidates_total} candidates evaluated before the "
            "overall time budget was reached"
            if result.analysis_truncated else None
        )
        if not result.survivors:
            return MethodResult(
                method_id=self.id, success=False, peaks=[], analysis=analysis,
                confidence={}, diagnostics={
                    "n_reports": len(result.reports),
                    "analysis_truncated": result.analysis_truncated,
                    "n_candidates_evaluated": result.n_candidates_evaluated,
                    "n_candidates_total": result.n_candidates_total,
                },
                message=("no candidate survived filter-then-rank — see analysis "
                         "for filtered/non-converged detail (diagnostic, not "
                         "prescriptive: manual attention required)"
                         + (f"; {truncation_note}" if truncation_note else "")),
            )

        top = result.survivors[0]
        # Slots classified "correctly absent" won the BIC*-adjustment benefit
        # precisely because they carry no real signal — emitting them as
        # fitted peaks would contradict that classification (Codex finding
        # #4).  They remain visible in analysis.candidates[].absent_slots.
        absent_roles = {a.role for a in top.absent_slots}
        peaks = _peaks_from_report(top, exclude_roles=absent_roles)
        confidence = {
            slot.role: build_confidence_vector(top, slot.role, noise_floor)
            for slot in top.model.slots
            if slot.role not in absent_roles
        }
        message = ""
        winner_unassigned_roles = sorted(
            slot.role for slot in top.model.slots
            if slot.region == "unassigned"
            and slot.role not in absent_roles
        )
        if winner_unassigned_roles:
            centers = [
                f"{c.position:.2f}" for r in winner_unassigned_roles
                for c in top.primary_fit.components if c.slot_role == r
            ]
            message += (
                f"DATA-DRIVEN component(s) at {', '.join(centers)} eV "
                "(detected/seeded/proposed, region-unassigned): chemical "
                "assignment requires human review; positions are "
                "data-driven, not literature-anchored. "
            )
        if result.conditional:
            # the conditional banner leads, but must not CLOBBER the
            # data-driven/human-review note (Stage-2: a conditional
            # detection-family winner still needs its assignment caveat)
            if result.conditional_reason == "decisive_override":
                message = (
                    "CONDITIONAL result (decisive_override): clean candidates "
                    "exist but a bound-fixed refit of a constraint-limited "
                    f"candidate dominates them — winner {top.model.name} with "
                    f"parameters fixed at bounds: {top.boundary_fixed_params}; "
                    "clean alternatives retained in the ranking "
                    "(see analysis.candidates). "
                ) + message
            elif result.conditional_reason == "unstable_last_resort":
                message = (
                    "UNSTABLE result (last resort): NO candidate passed any "
                    "selection tier — component identities are NOT stable "
                    "across refits (min persistence "
                    f"{top.active_min_persistence:.2f}, orphan rate "
                    f"{top.stability.orphan_rate:.2f}).  Showing the best "
                    f"CONVERGED model ({top.model.name}, χ²ᵣ "
                    f"{top.reduced_chi_sq:.1f}) so you can see what the data "
                    "supports — treat EVERY component as a low-confidence "
                    "suggestion; the data may not distinguish one broad "
                    "feature from several overlapping ones here. "
                ) + message
            else:
                message = (
                    "CONDITIONAL result (no_clean_survivor): no candidate "
                    "passed plausibility cleanly; ranking the stable-but-"
                    f"boundary-limited tier — winner {top.model.name} has "
                    f"constraint violations {top.plausibility.boundary_hits} "
                    "(see analysis.candidates). "
                ) + message
        if top.plausibility.unphysical_widths:
            message += (
                " LOW CONFIDENCE — width(s) held at the ordinary physical "
                f"FWHM cap ({', '.join(top.plausibility.unphysical_widths)}): "
                "the data wants a broader component than an ordinary core line "
                "physically has, but no known-broad class (satellite / plasmon "
                "/ loss) is assigned here. The width is capped at the physical "
                "limit rather than silently widened; a human should identify "
                "the feature (or justify a wider width) before trusting it."
            )
        return MethodResult(
            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
            confidence=confidence,
            diagnostics={
                "winner": top.model.name,
                "conditional": bool(result.conditional),
                "conditional_reason": result.conditional_reason,
                "winner_boundary_hits": list(top.plausibility.boundary_hits),
                "winner_unphysical_widths": list(top.plausibility.unphysical_widths),
                "winner_boundary_fixed_params": list(top.boundary_fixed_params),
                # stress-suite finding 0: buried decisive evidence is a
                # RESULT-level flag, not candidate-table archaeology
                "filtered_dominant_alternative":
                    result.filtered_dominant_alternative,
                "weighted_ic_disagreement": result.weighted_ic_disagreement,
                "preseeded_features": result.preseeded_features,
                "n_survivors": len(result.survivors),
                "n_filtered": len(result.filtered_out),
                "n_non_converged": len(result.non_converged),
                "analysis_truncated": result.analysis_truncated,
                "n_candidates_evaluated": result.n_candidates_evaluated,
                "n_candidates_total": result.n_candidates_total,
            },
            message=(message + (
                f" WARNING: filtered candidate "
                f"{result.filtered_dominant_alternative['name']} beats this "
                f"winner by ΔBIC* "
                f"{result.filtered_dominant_alternative['delta_bic_vs_winner']:.1f} "
                "but did not survive filtering "
                f"({result.filtered_dominant_alternative['filter_reason']})"
                if result.filtered_dominant_alternative else "")
                + (f" {truncation_note}." if truncation_note else "")),
        )


def _peaks_from_report(
    report: ModelReport, exclude_roles: frozenset | set = frozenset()
) -> list[dict]:
    """Winning decomposition as backend-spec-shaped dicts."""
    peaks = []
    lm = report.primary_fit.lmfit_result
    for slot in report.model.slots:
        if slot.role in exclude_roles:
            continue
        comp = next((c for c in report.primary_fit.components
                     if c.slot_role == slot.role), None)
        if comp is None:
            continue
        rec = {
            "role": slot.role,
            "region": slot.region,
            "phase_id": slot.phase_id,
            "shape": BACKEND_SHAPE[slot.line_shape],
            "center": comp.position,
            "fwhm": comp.fwhm,
            "amplitude": comp.amplitude,
            **comp.shape_params,
        }
        if lm is not None:
            prefix = _slot_prefix(slot.role)
            stderr = {}
            for pname, par in lm.params.items():
                if pname.startswith(prefix) and par.stderr is not None:
                    stderr[pname[len(prefix):]] = float(par.stderr)
            if stderr:
                rec["stderr"] = stderr
        peaks.append(rec)
    return peaks


def build_analysis_record(
    grammar: CandidateGrammar, result: ComparisonResult
) -> dict:
    """
    The tab-level ``analysis`` payload — REGENERABLE ONLY (spec §1: older
    clients drop it on resave; no human decisions may live here).
    """
    filtered_reason = {r.model.name: why for r, why in result.filtered_out}
    survivor_rank = {r.model.name: i + 1 for i, r in enumerate(result.survivors)}

    candidates = []
    for r in result.reports:
        name = r.model.name
        candidates.append({
            "name": name,
            "n_components": int(r.model.n_components),
            "reduced_chi_sq": float(r.reduced_chi_sq),
            "bic_star": float(r.bic_adjusted),
            # the labeled-heuristic BIC*'s honest companions (BIC/IC math
            # review): full-k raw BIC, the weighted-χ² criterion the fits
            # are actually consistent with, and the effective sample size
            # under residual autocorrelation
            "bic_raw": float(r.bic_raw),
            "bic_weighted": float(r.bic_weighted),
            "n_eff_lag1": (float(r.n_eff_lag1)
                           if r.n_eff_lag1 is not None else None),
            "survived": name in survivor_rank,
            "rank": survivor_rank.get(name),
            "filter_reason": filtered_reason.get(name),
            "augmented_from": r.augmented_from,
            "boundary_fixed_params": list(r.boundary_fixed_params),
            "absent_slots": [
                {"role": a.role, "persistence": float(a.persistence),
                 "area_fraction": float(a.area_fraction)} for a in r.absent_slots
            ],
            "proposed_peaks": [
                {"role": p.role, "accepted": bool(p.accepted),
                 "fitted_center": p.fitted_center,
                 "fitted_fwhm": p.fitted_fwhm,
                 "width_capped": bool(p.width_capped),
                 "rejection_reason": p.rejection_reason,
                 "near_roi_endpoint": bool(p.near_roi_endpoint)}
                for p in r.proposed_peaks
            ],
            "residual_flags": r.residuals.flagged_windows,
            "unphysical_widths": list(r.plausibility.unphysical_widths),
            "autocorr_flag": bool(r.residuals.autocorr_flag),
            "min_active_persistence": float(r.active_min_persistence),
            "boundary_hits": r.plausibility.boundary_hits,
            # full plausibility surface (Codex Stage-2 re-review finding #3 —
            # the orphan flag was recorded but dropped from the payload)
            "unphysical_widths": r.plausibility.unphysical_widths,
            "orphan_peaks": bool(r.plausibility.orphan_peaks),
            # best-minimum honesty (re-review finding #4): how many of the
            # multi-start fits reproduced the reported minimum's χ² basin
            "best_minimum_basin_support": int(r.stability.best_basin_support),
        })

    import copy

    non_verified = sorted({
        f"{slug}:{e['constant']}"
        for slug, entries in grammar.provenance.items()
        for e in entries if e.get("status") != "VERIFIED"
    })
    return {
        "method": "ic_model_comparison",
        "engine_version": ENGINE_VERSION,
        "regions": list(grammar.regions),
        "phase_ids": list(grammar.phase_ids),
        "resolution_notes": grammar.notes,
        "conditional_tier": bool(result.conditional),
        "conditional_reason": result.conditional_reason,
        # Constants provenance — runtime-visible verification status of every
        # physical constant this fit was built on (never comments-only).
        # Deep-copied so payload consumers can't mutate the shared grammar.
        # SCOPE: region-wide (everything the resolved grammar consumes), not
        # per-candidate — a candidate that omits a slot still lists that
        # slot's constants; per-candidate provenance is logged future work.
        "constants_provenance": copy.deepcopy(grammar.provenance),
        "constants_provenance_scope": "region-wide",
        "uses_conditional_or_unverified_constants": non_verified,
        "candidates": candidates,
        "non_converged": [m.name for m, _ in result.non_converged],
        "ambiguous_pairs": [list(t) for t in result.ambiguous_pairs],
        # unit F1: out-of-grammar dominants every candidate was pre-seeded
        # with (empty = detection found nothing, candidate set unmodified)
        "preseeded_features": result.preseeded_features,
        # candidate-generation layer (2026-07-10): the OVERCOMPLETE,
        # provenance-tagged detection pool — every feature any source
        # (local_max / curvature_shoulder / residual_gap / grammar)
        # proposed, with per-feature gate outcomes and seeding decisions.
        # Features here are candidates the selection layer judged, NOT
        # confirmed peaks.  None when the layer did not run.
        "candidate_pool": result.candidate_pool,
        # unit F3: two-phase sweep record — every candidate's screen outcome
        # when the screen ran (None = classic single-phase path).  Screened-
        # out candidates are visible here, never silently dropped.
        "screen": result.screen,
        "filtered_dominant_alternative": result.filtered_dominant_alternative,
        "weighted_ic_disagreement": result.weighted_ic_disagreement,
        # BIC/IC math review: the ΔBIC thresholds (decisive 10 / ambiguity
        # 2, Kass & Raftery 1995) are CONVENTIONS assuming independent
        # residuals and a well-specified likelihood — n_eff_lag1 per
        # candidate shows how far independence is stretched; empirical
        # calibration (block bootstrap / CV) is logged future work.
        "bic_threshold_caveat": (
            "ΔBIC* thresholds are uncalibrated conventions under residual "
            "autocorrelation and background misspecification — see "
            "per-candidate n_eff_lag1 and the stress-test report"),
        "criteria_panel": build_criteria_panel(
            result.reports, result.survivors,
            # the SAME threshold the ranking used — panel and ranking can
            # never disagree (Codex Stage-2 re-review finding #1)
            bic_ambiguity_threshold=result.bic_ambiguity_threshold),
        "cross_candidate_coincidences": [
            {"center_be": c.center_be, "contributors": c.contributors}
            for c in result.cross_candidate_coincidences
        ],
    }
