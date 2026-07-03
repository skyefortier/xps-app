"""
Composable grammar for the autofit engine (spec v2.1 §2).

``resolve(phases, regions, ...)`` → :class:`CandidateGrammar`.

Three layers:

- **Layer A** — material class (per phase): lineshape family admissibility,
  charge strategy, reference.
- **Layer B** — region/element module (``autofit.regions``): doublet
  Δso/ratio, BE windows, allowed lineshapes, satellites, core-hole width.
- **Layer C** — oxidation-state override (multiplet fingerprint, BE shift).
  Seam only in Stage 2 — region modules may accept it, none require it.

Multi-phase model (v2 B1 fix): a ``phases`` list, never a pairwise
``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
``phase_id``; when the same region is contributed by more than one phase the
caller MUST disambiguate with ``target_phases`` (Codex precondition 2 — a
region is not a unique key).

Multi-region co-fit ([Skye]): ``regions`` is multi-valued; the grammars of
all requested regions are composed into joint candidates fit together in the
shared window (e.g. U 4f + N 1s overlap).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

__all__ = [
    "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
    "CandidateModel", "CandidateGrammar", "PhaseAmbiguityError",
    "UnknownRegionError", "resolve", "BACKEND_SHAPE",
]


class LineShape(Enum):
    GAUSSIAN = "gaussian"
    LORENTZIAN = "lorentzian"
    PSEUDO_VOIGT = "pseudo_voigt"    # backend pseudo_voigt_gl
    ASYM_GL = "asym_gl"              # backend asymmetric_gl
    DS = "doniach_sunjic"
    DS_G = "ds_g"                    # DS core ⊗ Gaussian (fitalg's "LA_ASYMMETRIC")
    LACX = "la_casaxps"              # true CasaXPS LA(α, β, m)


# LineShape → fitting.py _SHAPE_FUNCS key
BACKEND_SHAPE: dict[LineShape, str] = {
    LineShape.GAUSSIAN: "gaussian",
    LineShape.LORENTZIAN: "lorentzian",
    LineShape.PSEUDO_VOIGT: "pseudo_voigt_gl",
    LineShape.ASYM_GL: "asymmetric_gl",
    LineShape.DS: "doniach_sunjic",
    LineShape.DS_G: "ds_g",
    LineShape.LACX: "la_casaxps",
}

# Shapes whose asymmetric tail encodes physics (metallic screening or an
# unresolvable multiplet envelope) — admissible only where Layer A allows.
ASYMMETRIC_SHAPES = frozenset({LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX})


class BackgroundType(Enum):
    SHIRLEY = "shirley"
    SMART = "smart"
    LINEAR = "linear"
    TOUGAARD = "tougaard"


class MaterialClass(Enum):
    CONDUCTOR = "conductor"
    SEMICONDUCTOR = "semiconductor"
    INSULATOR = "insulator"


@dataclass(frozen=True)
class Phase:
    """
    One physical phase of the sample (spec §2).  ``regions`` declares which
    core-level regions this phase's material contributes signal to — the
    resolver uses it to detect region↔phase ambiguity.
    """
    id: str
    material_class: MaterialClass
    regions: tuple[str, ...]
    role: str = "analyte"                    # analyte | matrix | phase
    material: Optional[str] = None           # e.g. "graphite" — region-module hint
    # Per-phase charge reference (Layer A default when None):
    #   conductor → internal (graphite C 1s 284.4 eV / Fermi edge)
    #   insulator → adventitious C 1s 284.8 eV (CONDITIONAL, Biesinger 2022)
    #   semiconductor → internal-if-present else adventitious
    charge_reference: Optional[dict] = None
    shift_model: str = "rigid"               # per-phase rigid shift (Stage 2)


@dataclass(frozen=True)
class ComponentSlot:
    """
    A component defined by grammar role — the stable identity used for
    cross-refit matching (never optimizer index).  Ported from fitalg with
    two generalizations: ``phase_id``/``region`` tagging, and generic
    per-parameter fixes/bounds instead of LA-specific fields.
    """
    role: str
    region: str
    phase_id: str
    be_window: tuple[float, float]
    line_shape: LineShape
    fwhm_range: tuple[float, float]

    # Offset-linkage (satellites, chemically-shifted contaminants):
    linked_to: Optional[str] = None
    linked_offset_range: Optional[tuple[float, float]] = None

    # Amplitude-linkage (spin-orbit doublets):  amplitude = parent × ratio.
    # `area_ratio_range` bounds a *relaxed* ratio parameter around the
    # theoretical default (e.g. U 4f 0.75 with bounded relaxation, spec §3.2).
    area_ratio: Optional[float] = None
    area_ratio_range: Optional[tuple[float, float]] = None

    # Generic per-shape-parameter constraints, e.g. (("beta", 0.05),) to fix
    # the DS+G Lorentzian HWHM at the C 1s core-hole lifetime.
    fixed_params: tuple[tuple[str, float], ...] = ()
    param_ranges: tuple[tuple[str, tuple[float, float]], ...] = ()

    # Width-linkage: this slot's fwhm becomes an lmfit expression referencing
    # another parameter name (Biesinger-style shared contamination width).
    fwhm_linked_to: Optional[str] = None

    def contains(self, be: float, fwhm: float, amplitude: float,
                 noise_floor: float) -> bool:
        return (
            self.be_window[0] <= be <= self.be_window[1]
            and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
            and amplitude > noise_floor
        )


@dataclass(frozen=True)
class CandidateModel:
    """A candidate model M = (background, slots) with admissibility built in."""
    name: str
    background: BackgroundType
    slots: tuple[ComponentSlot, ...]
    # (name, min, max) free params referenced by fwhm_linked_to expressions
    shared_fwhm_params: tuple[tuple[str, float, float], ...] = ()

    @property
    def n_components(self) -> int:
        return len(self.slots)

    def slot_by_role(self, role: str) -> Optional[ComponentSlot]:
        for s in self.slots:
            if s.role == role:
                return s
        return None


@dataclass
class CandidateGrammar:
    """resolve() output: the composed, admissible candidate set."""
    regions: tuple[str, ...]
    phase_ids: tuple[str, ...]
    candidates: list[CandidateModel]
    diagnostic_windows: dict[str, tuple[float, float]]
    # Human-readable resolution trace (which phase supplied which region,
    # Layer-A decisions, oxidation-state overrides applied).
    notes: list[str] = field(default_factory=list)


class PhaseAmbiguityError(ValueError):
    """Raised when a region is contributed by >1 phase and no target given."""


class UnknownRegionError(KeyError):
    """Raised when no registered region module or no phase covers a region."""


def resolve(
    phases: list[Phase],
    regions: list[str] | str,
    oxidation_state: Optional[str] = None,
    target_phases: Optional[dict[str, str]] = None,
) -> CandidateGrammar:
    """
    Compose the candidate grammar for ``regions`` over ``phases``.

    Parameters
    ----------
    phases          : the sample's phase list (length 1 = single-phase default)
    regions         : one region id or a list for a joint co-fit window
    oxidation_state : Layer-C override, forwarded to region modules
    target_phases   : {region: phase_id} disambiguation — REQUIRED for any
                      region contributed by more than one phase

    Raises
    ------
    PhaseAmbiguityError : region in multiple phases without a target
    UnknownRegionError  : region not registered, or not covered by any phase
    """
    from .regions import get_region_module  # local import: avoid cycle

    if isinstance(regions, str):
        regions = [regions]
    if not phases:
        raise ValueError("phases must be a non-empty list (single-phase = length 1)")
    if not regions:
        raise ValueError("regions must be a non-empty list")
    target_phases = target_phases or {}

    ids = [p.id for p in phases]
    if len(set(ids)) != len(ids):
        raise ValueError(f"duplicate phase ids: {ids}")

    notes: list[str] = []
    per_region_candidates: list[list[CandidateModel]] = []
    diagnostic_windows: dict[str, tuple[float, float]] = {}
    used_phase_ids: list[str] = []

    for region in regions:
        contributors = [p for p in phases if region in p.regions]
        if not contributors:
            raise UnknownRegionError(
                f"region {region!r} is not contributed by any declared phase "
                f"(phases: {[p.id for p in phases]})"
            )
        if len(contributors) > 1:
            tid = target_phases.get(region)
            if tid is None:
                raise PhaseAmbiguityError(
                    f"region {region!r} appears in phases "
                    f"{[p.id for p in contributors]} — pass "
                    f"target_phases={{{region!r}: <phase_id>}} to disambiguate "
                    "(spec v2.1 §2: region is not a unique key)"
                )
            chosen = next((p for p in contributors if p.id == tid), None)
            if chosen is None:
                raise PhaseAmbiguityError(
                    f"target phase {tid!r} for region {region!r} is not among "
                    f"its contributors {[p.id for p in contributors]}"
                )
        else:
            chosen = contributors[0]

        module = get_region_module(region)
        candidates = module.build_candidates(chosen, oxidation_state=oxidation_state)
        _guard_slot_tags(candidates, region, chosen.id)
        per_region_candidates.append(candidates)
        used_phase_ids.append(chosen.id)
        notes.append(
            f"{region}: phase {chosen.id!r} ({chosen.material_class.value}"
            + (f", {chosen.material}" if chosen.material else "")
            + f"), {len(candidates)} candidates"
        )
        for label, win in module.diagnostic_windows().items():
            diagnostic_windows[f"{region}:{label}"] = win

    if len(regions) == 1:
        composed = per_region_candidates[0]
    else:
        composed = _compose_joint_candidates(regions, per_region_candidates)
        notes.append(
            f"joint co-fit of {regions}: {len(composed)} composed candidates"
        )

    grammar = CandidateGrammar(
        regions=tuple(regions),
        phase_ids=tuple(dict.fromkeys(used_phase_ids)),
        candidates=composed,
        diagnostic_windows=diagnostic_windows,
        notes=notes,
    )
    _guard_phase_leakage(grammar, phases)
    return grammar


def _guard_slot_tags(candidates: list[CandidateModel], region: str, phase_id: str) -> None:
    """Region modules must tag every slot with the region + resolved phase."""
    for cand in candidates:
        for slot in cand.slots:
            if slot.region != region:
                raise ValueError(
                    f"candidate {cand.name!r}: slot {slot.role!r} tagged region "
                    f"{slot.region!r}, expected {region!r}"
                )
            if slot.phase_id != phase_id:
                raise ValueError(
                    f"candidate {cand.name!r}: slot {slot.role!r} tagged phase "
                    f"{slot.phase_id!r}, expected {phase_id!r} (phase-id leakage)"
                )


def _guard_phase_leakage(grammar: CandidateGrammar, phases: list[Phase]) -> None:
    """Every slot's phase must be declared AND contribute the slot's region."""
    by_id = {p.id: p for p in phases}
    for cand in grammar.candidates:
        roles = [s.role for s in cand.slots]
        if len(set(roles)) != len(roles):
            raise ValueError(f"candidate {cand.name!r}: duplicate slot roles {roles}")
        for slot in cand.slots:
            phase = by_id.get(slot.phase_id)
            if phase is None:
                raise ValueError(
                    f"candidate {cand.name!r}: slot {slot.role!r} references "
                    f"undeclared phase {slot.phase_id!r}"
                )
            if slot.region not in phase.regions:
                raise ValueError(
                    f"candidate {cand.name!r}: slot {slot.role!r} region "
                    f"{slot.region!r} is not contributed by phase {phase.id!r}"
                )


def _compose_joint_candidates(
    regions: list[str],
    per_region: list[list[CandidateModel]],
) -> list[CandidateModel]:
    """
    Cartesian composition of per-region candidate sets into joint models for
    one shared spectral window.  Slot roles are prefixed with a region slug
    to stay unique; the shared window uses ONE background (the regions'
    backgrounds must agree — co-fit means one physical loss continuum).
    """
    composed: list[CandidateModel] = []
    for combo in itertools.product(*per_region):
        backgrounds = {c.background for c in combo}
        if len(backgrounds) != 1:
            raise ValueError(
                f"joint candidates must share one background, got {backgrounds} "
                f"for {[c.name for c in combo]}"
            )
        slots: list[ComponentSlot] = []
        shared: list[tuple[str, float, float]] = []
        for region, cand in zip(regions, combo):
            slug = region.replace(" ", "")
            rename = {s.role: f"{slug}__{s.role}" for s in cand.slots}
            shared_rename = {name: f"{slug}__{name}" for name, _, _ in cand.shared_fwhm_params}
            for s in cand.slots:
                slots.append(_retag_slot(s, rename, shared_rename))
            for name, lo, hi in cand.shared_fwhm_params:
                shared.append((shared_rename[name], lo, hi))
        composed.append(CandidateModel(
            name="+".join(c.name for c in combo),
            background=combo[0].background,
            slots=tuple(slots),
            shared_fwhm_params=tuple(shared),
        ))
    return composed


def _retag_slot(
    s: ComponentSlot,
    rename: dict[str, str],
    shared_rename: dict[str, str],
) -> ComponentSlot:
    """Rewrite role / linked_to / fwhm_linked_to under the region prefix."""
    fwhm_link = s.fwhm_linked_to
    if fwhm_link is not None:
        # fwhm_linked_to may reference either a shared param or another
        # slot's parameter name (prefix-based); rewrite whichever matches.
        if fwhm_link in shared_rename:
            fwhm_link = shared_rename[fwhm_link]
        else:
            for old, new in rename.items():
                old_prefix = _slot_param_prefix(old)
                if fwhm_link.startswith(old_prefix):
                    fwhm_link = _slot_param_prefix(new) + fwhm_link[len(old_prefix):]
                    break
    return ComponentSlot(
        role=rename[s.role],
        region=s.region,
        phase_id=s.phase_id,
        be_window=s.be_window,
        line_shape=s.line_shape,
        fwhm_range=s.fwhm_range,
        linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None,
        linked_offset_range=s.linked_offset_range,
        area_ratio=s.area_ratio,
        area_ratio_range=s.area_ratio_range,
        fixed_params=s.fixed_params,
        param_ranges=s.param_ranges,
        fwhm_linked_to=fwhm_link,
    )


def _slot_param_prefix(role: str) -> str:
    """Must match engine._slot_prefix — kept here to rewrite fwhm links."""
    import re
    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"
