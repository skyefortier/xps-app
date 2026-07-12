"""
Method 1 — classical constrained least-squares (the manual-model baseline).

Thin wrapper over the EXISTING ``fitting.run_fit`` (unchanged, same code the
manual UI uses) so the method seam has an honest baseline entry.  Consumes
explicit ``peak_specs``; no grammar required.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

import numpy as np

from fitting import run_fit

from ..grammar import CandidateGrammar
from .base import MethodResult, PeakFitMethod

_ALLOWED_OPTIONS = {
    "background_method", "bg_start_idx", "bg_end_idx", "endpoint_avg",
    "fit_method", "n_perturb", "manual_bg",
}


class LeastSquaresMethod(PeakFitMethod):
    id = "least_squares"
    label = "Least-squares (manual model)"
    requires_grammar = False

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
        if not peak_specs:
            raise ValueError("least_squares requires explicit peak_specs (manual model)")
        opts = dict(options or {})
        unknown = set(opts) - _ALLOWED_OPTIONS
        if unknown:
            raise ValueError(f"unknown least_squares options: {sorted(unknown)}")
        fit_method = opts.pop("fit_method", None)
        fit_kws = {"method": fit_method} if fit_method else None

        res = run_fit(
            np.asarray(x, dtype=float),
            np.asarray(y, dtype=float),
            peak_specs,
            background_method=opts.pop("background_method", "shirley"),
            bg_start_idx=opts.pop("bg_start_idx", None),
            bg_end_idx=opts.pop("bg_end_idx", None),
            endpoint_avg=opts.pop("endpoint_avg", 1),
            n_perturb=opts.pop("n_perturb", 0),
            manual_bg=opts.pop("manual_bg", None),
            fit_kws=fit_kws,
        )

        peaks = []
        confidence: dict[str, dict] = {}
        for ip in res["individual_peaks"]:
            par = ip["params"]
            rec = {"id": ip["id"]}
            for name, info in par.items():
                rec[name] = info["value"]
            peaks.append(rec)
            stderr = {name: info.get("stderr") for name, info in par.items()}
            has_cov = any(v is not None for v in stderr.values())
            confidence[str(ip["id"])] = {
                "sigma_stat": {
                    "uncertainty_kind": "covariance" if has_cov else "unavailable",
                    "values": stderr if has_cov else None,
                },
                "reference_sensitivity_range": {
                    "kind": "unavailable_single_fit", "range_ev": None,
                },
            }

        stats = res["statistics"]
        return MethodResult(
            method_id=self.id,
            success=bool(res["success"]),
            peaks=peaks,
            analysis={
                "method": self.id,
                "statistics": stats,
                "note": "manual-model baseline; no candidate enumeration",
            },
            confidence=confidence,
            diagnostics={"lmfit_message": res.get("message")},
            message=res.get("message") or "",
        )
