"""
PeakFitMethod registry (spec §5A) — the solver-selector seam.

The FULL decision-matrix menu (methods 1–6) is implemented:

  1. least_squares           — wraps existing run_fit (the honest baseline)
  2. ic_model_comparison     — fitalg engine port (peak-count by IC panel)
  3. bayesian_exchange_mc    — the window flagship: replica exchange +
                               stepping-stone Bayes free energy
  4. sparse_map              — L1 dictionary + debiased NNLS (fast auto-
                               pruning, few-separated-peaks regime)
  5. multivariate_mcr        — PCA rank + MCR-ALS on a multi-spectrum
                               matrix (chemical states, not peaks)
  6. max_entropy             — resolution enhancement (USER-supplied
                               kernel; sharpening, not quantification)
"""

from __future__ import annotations

from .base import MethodResult, NotImplementedMethod, PeakFitMethod
from .bayesian_exchange_mc import BayesianExchangeMCMethod
from .ic_model_comparison import ICModelComparisonMethod
from .least_squares import LeastSquaresMethod
from .max_entropy import MaxEntropyMethod
from .multivariate_mcr import MultivariateMCRMethod
from .sparse_map import SparseMAPMethod


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
