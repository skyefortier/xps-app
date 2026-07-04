"""
PeakFitMethod registry (spec §5A) — the solver-selector seam.

Methods 1–4 implemented; the rest are registered stubs so the menu shape is
stable (ranked per the decision matrix):

  1. least_squares           — implemented (wraps existing run_fit)
  2. ic_model_comparison     — implemented (fitalg engine port)
  3. bayesian_exchange_mc    — implemented (the window flagship: replica
                               exchange + stepping-stone Bayes free energy)
  4. sparse_map              — implemented (L1 dictionary + debiased NNLS;
                               fast auto-pruning, few-separated-peaks regime)
  5. multivariate_mcr       — stub (multi-spectrum decomposition)
  6. max_entropy             — stub (resolution enhancement)
"""

from __future__ import annotations

from .base import MethodResult, NotImplementedMethod, PeakFitMethod
from .bayesian_exchange_mc import BayesianExchangeMCMethod
from .ic_model_comparison import ICModelComparisonMethod
from .least_squares import LeastSquaresMethod
from .sparse_map import SparseMAPMethod


class MultivariateMCRMethod(NotImplementedMethod):
    id = "multivariate_mcr"
    label = "Multivariate (PCA / MCR-ALS)"
    reason = "multi-spectrum decomposition — needs the repeat-scan data matrix plumbing"


class MaxEntropyMethod(NotImplementedMethod):
    id = "max_entropy"
    label = "Max-entropy (resolution enhancement)"
    reason = "needs an instrument broadening kernel model"


_METHODS: dict[str, PeakFitMethod] = {}
for _m in (
    LeastSquaresMethod(),
    ICModelComparisonMethod(),
    BayesianExchangeMCMethod(),
    SparseMAPMethod(),
    MultivariateMCRMethod(),
    MaxEntropyMethod(),
):
    _METHODS[_m.id] = _m


def get_method(method_id: str) -> PeakFitMethod:
    try:
        return _METHODS[method_id]
    except KeyError:
        raise KeyError(
            f"unknown PeakFitMethod {method_id!r} — available: {sorted(_METHODS)}"
        ) from None


def available_methods() -> list[dict]:
    """Menu payload: id, label, implemented — ranked (registration order)."""
    return [
        {"id": m.id, "label": m.label, "implemented": m.implemented,
         "requires_grammar": m.requires_grammar}
        for m in _METHODS.values()
    ]


__all__ = [
    "MethodResult", "PeakFitMethod", "get_method", "available_methods",
]
