"""
Method 2 — grammar + information-criterion model comparison (fitalg engine).

Runs the full comparison pipeline over a resolved grammar and returns the
top survivor's decomposition, per-slot confidence vectors, and the complete
candidate/criteria record for the ``analysis`` namespace.
"""

from __future__ import annotations

from typing import Any, Optional

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
            persistence_threshold=float(opts.pop("persistence_threshold", 0.7)),
            bic_ambiguity_threshold=float(opts.pop("bic_ambiguity_threshold", 2.0)),
            absent_slot_area_fraction=float(opts.pop("absent_slot_area_fraction", 0.02)),
            absent_slot_persistence_threshold=float(
                opts.pop("absent_slot_persistence_threshold", 0.7)),
        )

        analysis = build_analysis_record(grammar, result)
        if not result.survivors:
            return MethodResult(
                method_id=self.id, success=False, peaks=[], analysis=analysis,
                confidence={}, diagnostics={"n_reports": len(result.reports)},
                message="no candidate survived filter-then-rank — see analysis "
                        "for filtered/non-converged detail (diagnostic, not "
                        "prescriptive: manual attention required)",
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
        if result.conditional:
            message = (
                "CONDITIONAL result: no candidate passed plausibility cleanly; "
                "ranking the stable-but-boundary-limited tier — winner "
                f"{top.model.name} has constraint violations "
                f"{top.plausibility.boundary_hits} (see analysis.candidates)"
            )
        return MethodResult(
            method_id=self.id, success=True, peaks=peaks, analysis=analysis,
            confidence=confidence,
            diagnostics={
                "winner": top.model.name,
                "conditional": bool(result.conditional),
                "winner_boundary_hits": list(top.plausibility.boundary_hits),
                "n_survivors": len(result.survivors),
                "n_filtered": len(result.filtered_out),
                "n_non_converged": len(result.non_converged),
            },
            message=message,
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
            "survived": name in survivor_rank,
            "rank": survivor_rank.get(name),
            "filter_reason": filtered_reason.get(name),
            "augmented_from": r.augmented_from,
            "absent_slots": [
                {"role": a.role, "persistence": float(a.persistence),
                 "area_fraction": float(a.area_fraction)} for a in r.absent_slots
            ],
            "proposed_peaks": [
                {"role": p.role, "accepted": bool(p.accepted),
                 "fitted_center": p.fitted_center,
                 "rejection_reason": p.rejection_reason,
                 "near_roi_endpoint": bool(p.near_roi_endpoint)}
                for p in r.proposed_peaks
            ],
            "residual_flags": r.residuals.flagged_windows,
            "autocorr_flag": bool(r.residuals.autocorr_flag),
            "min_active_persistence": float(r.active_min_persistence),
            "boundary_hits": r.plausibility.boundary_hits,
        })

    return {
        "method": "ic_model_comparison",
        "engine_version": ENGINE_VERSION,
        "regions": list(grammar.regions),
        "phase_ids": list(grammar.phase_ids),
        "resolution_notes": grammar.notes,
        "conditional_tier": bool(result.conditional),
        "candidates": candidates,
        "non_converged": [m.name for m, _ in result.non_converged],
        "ambiguous_pairs": [list(t) for t in result.ambiguous_pairs],
        "criteria_panel": build_criteria_panel(result.reports, result.survivors),
        "cross_candidate_coincidences": [
            {"center_be": c.center_be, "contributors": c.contributors}
            for c in result.cross_candidate_coincidences
        ],
    }
