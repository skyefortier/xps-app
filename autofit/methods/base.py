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
from typing import Any, Callable, Optional

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
        progress_cb: Optional[Callable[[dict], None]] = None,
    ) -> MethodResult:
        """
        Fit spectrum (x, y).  Grammar-driven methods consume ``grammar``;
        the manual baseline consumes explicit ``peak_specs`` instead.
        ``options`` carries method-specific parameters (documented per
        method); unknown keys are rejected.

        ``progress_cb`` (Find Peaks UI, 2026-07-11): OPTIONAL, default
        None — every method accepts it for interface uniformity; only
        ``ic_model_comparison`` threads it through to a real signal
        (``autofit.engine.compare_models``'s screen->stabilize sweep).
        Methods that ignore it are unaffected.
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


# Shared upper bound for endpoint averaging: the Background panel's
# #bg-endpoint-avg input carries max="50" and the frontend defines the same
# ENDPOINT_AVG_MAX, so every value the engine accepts is representable by the
# panel (Codex 2026-09-08 round 2: 1e21 passed both validators while the
# preview's parseInt read it as 1).
ENDPOINT_AVG_MAX = 50


def pop_endpoint_avg(opts: dict, default: int = 1) -> int:
    """Pop and validate the ``endpoint_avg`` option shared by every method that
    fits a background (Find Peaks honours the Background panel, 2026-09-08).
    Must be an integer >= 1; the frontend sends the panel value, so a bad value
    is a request error (ValueError -> 400), never a silent fallback to 1."""
    import math
    raw = opts.pop("endpoint_avg", default)
    # Strict by type, not by coercion: int("1_0") == 10 and int(True) == 1
    # would let a malformed Advanced-JSON value fit at one averaging while the
    # frontend records another (Codex 2026-09-08, both runs). Only a JSON
    # integer (or an integral finite float such as 3.0) is accepted.
    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        raise ValueError(f"endpoint_avg must be an integer >= 1, got {raw!r}")
    if isinstance(raw, float):
        if not math.isfinite(raw) or not raw.is_integer():
            raise ValueError(f"endpoint_avg must be an integer >= 1, got {raw!r}")
    n = int(raw)
    if n < 1 or n > ENDPOINT_AVG_MAX:
        raise ValueError(f"endpoint_avg must be an integer between 1 and {ENDPOINT_AVG_MAX}, got {raw!r}")
    return n
