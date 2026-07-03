"""
PeakFitMethod registry (spec §5A) — the solver-selector seam.

Stage 2 ships methods 1–2 implemented; the rest are registered stubs so the
menu shape is stable (ranked per the decision matrix):

  1. least_squares           — implemented (wraps existing run_fit)
  2. ic_model_comparison     — implemented (fitalg engine port)
  3. bayesian_exchange_mc    — stub; the window flagship (new math)
  4. sparse_map              — stub
  5. multivariate_mcr        — stub (multi-spectrum decomposition)
  6. max_entropy             — stub (resolution enhancement)
"""

from __future__ import annotations

from .base import MethodResult, NotImplementedMethod, PeakFitMethod
from .ic_model_comparison import ICModelComparisonMethod
from .least_squares import LeastSquaresMethod


class BayesianExchangeMCMethod(NotImplementedMethod):
    id = "bayesian_exchange_mc"
    label = "Bayesian (exchange Monte Carlo)"
    reason = ("planned window flagship: replica-exchange MC + Bayes free "
              "energy (Nagata/Sugita/Okada 2012, 10.1016/j.neunet.2011.12.001; "
              "Tokuda/Nagata/Okada 2017, 10.7566/JPSJ.86.024001)")


class SparseMAPMethod(NotImplementedMethod):
    id = "sparse_map"
    label = "Sparse / MAP (fast auto)"
    reason = "needs an XPS lineshape dictionary (STAM:Methods 2024, 10.1080/27660400.2024.2373046)"


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
