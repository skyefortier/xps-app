"""
Region cookbook registry (spec §7).

A region module owns Layer B for one core-level region: candidate model
families, BE windows, FWHM priors, lineshape admissibility, satellites —
every constant lit-cited or flagged UNVERIFIED in the module source.

Modules self-register at import; ``get_region_module`` is the resolver's
lookup.
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from ..grammar import CandidateModel, Phase


@runtime_checkable
class RegionModule(Protocol):
    region: str

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        ...

    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        ...


_REGISTRY: dict[str, RegionModule] = {}


def register_region(module: RegionModule) -> None:
    key = module.region
    if key in _REGISTRY and _REGISTRY[key] is not module:
        raise ValueError(f"region {key!r} already registered")
    _REGISTRY[key] = module


def get_region_module(region: str) -> RegionModule:
    try:
        return _REGISTRY[region]
    except KeyError:
        from ..grammar import UnknownRegionError
        raise UnknownRegionError(
            f"no region module registered for {region!r} "
            f"(registered: {sorted(_REGISTRY)})"
        ) from None


def registered_regions() -> list[str]:
    return sorted(_REGISTRY)


# Import modules for self-registration (order = documentation order).
from . import c1s  # noqa: E402,F401
from . import n1s  # noqa: E402,F401
from . import u4f  # noqa: E402,F401
from . import b1s  # noqa: E402,F401
from . import cl2p  # noqa: E402,F401
