"""
PeakFitMethod — the solver selector seam (spec §5A).

The user picks the *rules* (material class + region(s) → grammar) and a
*method* (how the plausible peak set is found).  Methods share one result
shape so the (later-gate) API/UI can treat them uniformly.  The full menu +
when-each-wins live in docs/autofit/peak-fit-methods-decision-matrix.md.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from ..grammar import CandidateGrammar


@dataclass
class MethodResult:
    """Uniform output of every PeakFitMethod."""
    method_id: str
    success: bool
    # Winning decomposition: one dict per component with backend-spec-shaped
    # fitted parameters ({role, shape, center, fwhm, amplitude, ...}).
    peaks: list[dict] = field(default_factory=list)
    # Payload for the tab-level `analysis` namespace (REGENERABLE only).
    analysis: dict = field(default_factory=dict)
    # Per-component `_confidence` payloads keyed by role — these ride the
    # durable peak-spread channel when written into a project.
    confidence: dict[str, dict] = field(default_factory=dict)
    diagnostics: dict = field(default_factory=dict)
    message: str = ""


class PeakFitMethod(ABC):
    """One mathematical treatment for decomposing a spectrum."""

    id: str = ""
    label: str = ""
    implemented: bool = True
    requires_grammar: bool = True

    @abstractmethod
    def run(
        self,
        x: np.ndarray,
        y: np.ndarray,
        weights: Optional[np.ndarray] = None,
        grammar: Optional[CandidateGrammar] = None,
        peak_specs: Optional[list[dict]] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> MethodResult:
        """
        Fit spectrum (x, y).  Grammar-driven methods consume ``grammar``;
        the manual baseline consumes explicit ``peak_specs`` instead.
        ``options`` carries method-specific parameters (documented per
        method); unknown keys are rejected.
        """


class NotImplementedMethod(PeakFitMethod):
    """Registered-but-stubbed menu entry (visible, not yet runnable)."""

    implemented = False
    reason: str = ""

    def run(self, *args, **kwargs) -> MethodResult:  # noqa: D102
        raise NotImplementedError(
            f"PeakFitMethod {self.id!r} ({self.label}) is a registered stub: "
            f"{self.reason} — see docs/autofit/peak-fit-methods-decision-matrix.md"
        )


def poisson_like_weights(y: np.ndarray) -> np.ndarray:
    """
    1/√max(y,1) weights — matching the existing manual-fit path.  Valid for
    RAW COUNTS only; for processed spectra prefer an empirical repeat-sweep
    noise estimate (fitalg LIMITATIONS §8; spec §9) when replicates exist.
    """
    return 1.0 / np.sqrt(np.maximum(np.asarray(y, dtype=float), 1.0))
