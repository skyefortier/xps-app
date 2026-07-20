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
import re
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Optional

from .fit_physics import provenance_entries as _fit_physics_provenance

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
    SMART_EXP = "smart_exp"      # Avantage-style constrained Shirley
    LINEAR = "linear"
    TOUGAARD = "tougaard"


class MaterialClass(Enum):
    CONDUCTOR = "conductor"
    SEMICONDUCTOR = "semiconductor"
    INSULATOR = "insulator"
    # Analyte embedded in a different matrix (2026-07-20): differential
    # charging between analyte and matrix is possible, which voids the
    # single-species-homogeneity assumption behind some region modules'
    # width ceilings. MIXED only RELAXES existing constraints (region
    # modules opt in — see autofit.regions.c1s) — it asserts no new
    # position or width value, and it must never reach charge-correction
    # (that stays byte-identical to every other material class; see
    # tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction).
    # Appended LAST so the default dropdown/first-enum-member selection
    # (conductor) is unchanged.
    MIXED = "mixed"


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

    # Width-INEQUALITY linkage (spin-orbit doublets whose deeper j-hole is
    # Coster-Kronig broadened, e.g. Cl 2p1/2 — adjudication 2026-07-03,
    # docs/autofit/adjudication-decisions.md #7): this slot's width parameter
    # becomes parent_width + a FREE non-negative excess bounded by this
    # range, enforcing width(child) >= width(parent).  Requires
    # ``linked_to``; mutually exclusive with fixing/sharing/expression-
    # linking the width.  An excess pegged at 0 surfaces as a boundary hit,
    # correctly steering selection toward the nested shared-width candidate.
    fwhm_excess_range: Optional[tuple[float, float]] = None

    # Names of shape parameters tied to the PARENT slot's same-named
    # parameters via lmfit expressions (requires ``linked_to``).  The width
    # parameter name ('fwhm' / DS+G 'm_gauss') is allowed here too.  This is
    # how a spin-orbit partner shares its sibling's lineshape (e.g. LACX
    # alpha/beta/m across a U 4f doublet), mirroring the manual path's
    # linked-peak sync.
    share_parent_params: tuple[str, ...] = ()

    # Explicit semantic claim, independent of fwhm_range's magnitude
    # (2026-07-20 refactor): the region module VOUCHES that a component
    # this wide is legitimate physics for this slot specifically — e.g. the
    # C 1s π→π* shake-up satellite's intrinsic multi-electron-excitation
    # breadth, or U 4f's unresolved 5f² multiplet manifold. None means the
    # slot's width is ordinary — no known-broad justification exists, so
    # autofit.engine._unphysical_width_flags must not exempt it, REGARDLESS
    # of how wide fwhm_range happens to be. Before this field existed,
    # fwhm_range's upper bound alone served double duty as both the
    # optimizer's search bound AND this semantic claim (declared_hi >
    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
    # bound for an UNRELATED reason (numerical-stability headroom, a wider
    # calibration envelope) silently asserted "this is vouched-for physics"
    # as a side effect. A region module that just needs search headroom
    # without vouching for width MUST leave this None.
    broad_justification: Optional[str] = None

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
    # {region-slug: [{constant, value, status, source}, ...]} — every
    # physical constant the resolved grammar consumes, with its verification
    # status.  Travels into the analysis namespace (never comments-only).
    provenance: dict[str, list[dict]] = field(default_factory=dict)
    # Phase D structural fallback: regions resolved WITHOUT a registered
    # module — derived structure only (see autofit.coverage), zero fit
    # candidates contributed.  Empty for every pre-Phase-D caller.
    structural_only: tuple[str, ...] = ()


class PhaseAmbiguityError(ValueError):
    """Raised when a region is contributed by >1 phase and no target given."""


class UnknownRegionError(KeyError):
    """Raised when no registered region module or no phase covers a region."""


RegionRequest = "str | tuple[str, str]"  # region name, or (region, phase_id)


def _parse_region_requests(
    regions: "list[str | tuple[str, str]] | str | tuple[str, str]",
) -> list[tuple[str, Optional[str]]]:
    if isinstance(regions, str):
        return [(regions, None)]
    if isinstance(regions, tuple) and len(regions) == 2 \
            and all(isinstance(v, str) for v in regions):
        return [(regions[0], regions[1])]
    out: list[tuple[str, Optional[str]]] = []
    for r in regions:
        if isinstance(r, str):
            out.append((r, None))
        elif isinstance(r, tuple) and len(r) == 2:
            out.append((str(r[0]), str(r[1])))
        else:
            raise ValueError(
                f"region request must be 'Region' or ('Region', 'phase_id'), got {r!r}"
            )
    return out


def resolve(
    phases: list[Phase],
    regions: "list[str | tuple[str, str]] | str",
    oxidation_state: Optional[str] = None,
    target_phases: Optional[dict[str, str]] = None,
    allow_structural_fallback: bool = False,
    cited_values: Optional[list] = None,
) -> CandidateGrammar:
    """
    Compose the candidate grammar for ``regions`` over ``phases``.

    Parameters
    ----------
    phases          : the sample's phase list (length 1 = single-phase default)
    regions         : region requests for one (possibly joint) fit window.
                      Each request is either a region name (``"C 1s"``) or a
                      phase-qualified ``("B 1s", "BN")`` pair.  The SAME
                      region may appear once per phase — that is how a
                      BN/B4C sample co-fits both phases' B 1s contributions
                      in one window (spec §2: phase-scoped slot families).
    oxidation_state : Layer-C override, forwarded to region modules
    target_phases   : {region: phase_id} disambiguation for UNqualified
                      requests of a region contributed by more than one phase
    allow_structural_fallback : Phase D, OPT-IN (default False keeps every
                      existing caller byte-identical).  A region with no
                      registered module that parses as an element/level in
                      the Z=1..96 table resolves to DERIVED STRUCTURE only
                      (autofit.coverage): zero fit candidates, provenance
                      records for the doublet/singlet structure, ratio
                      expectation, multiplet/conductor flags, and an
                      UNVERIFIED value-None position — 'structure known,
                      positions UNVERIFIED, supply a cited source'.  Such
                      regions are listed in ``CandidateGrammar.
                      structural_only`` and excluded from joint candidate
                      composition.
    cited_values    : optional list of autofit.cited_values.CitedValue —
                      cited empirical values whose matching records ride
                      into the structural provenance (they do NOT build
                      candidates; windows/widths remain curation work).

    Raises
    ------
    PhaseAmbiguityError : unqualified region in multiple phases w/o a target
    UnknownRegionError  : region not registered, or not covered by any phase
                          (with fallback enabled: also not derivable —
                          unparseable label, unknown element, or an
                          unoccupied subshell)
    """
    from .regions import get_region_module  # local import: avoid cycle

    requests = _parse_region_requests(regions)
    if not phases:
        raise ValueError("phases must be a non-empty list (single-phase = length 1)")
    if not requests:
        raise ValueError("regions must be a non-empty list")
    target_phases = target_phases or {}

    ids = [p.id for p in phases]
    if len(set(ids)) != len(ids):
        raise ValueError(f"duplicate phase ids: {ids}")

    # Region names occurring in >1 request get phase-qualified slugs so the
    # composed slot roles stay unique across phases.
    region_counts: dict[str, int] = {}
    for region, _ in requests:
        region_counts[region] = region_counts.get(region, 0) + 1

    notes: list[str] = []
    per_request_candidates: list[list[CandidateModel]] = []
    slugs: list[str] = []            # module-backed requests (composition)
    all_slugs: list[str] = []        # module-backed + structural (collision)
    structural_regions: list[str] = []
    diagnostic_windows: dict[str, tuple[float, float]] = {}
    provenance: dict[str, list[dict]] = {}
    used_phase_ids: list[str] = []
    resolved_pairs: set[tuple[str, str]] = set()

    for region, explicit_phase in requests:
        contributors = [p for p in phases if region in p.regions]
        if not contributors:
            raise UnknownRegionError(
                f"region {region!r} is not contributed by any declared phase "
                f"(phases: {[p.id for p in phases]})"
            )
        if explicit_phase is not None:
            chosen = next((p for p in contributors if p.id == explicit_phase), None)
            if chosen is None:
                raise ValueError(
                    f"request ({region!r}, {explicit_phase!r}): phase does not "
                    f"contribute this region (contributors: "
                    f"{[p.id for p in contributors]})"
                )
        elif len(contributors) > 1:
            tid = target_phases.get(region)
            if tid is None:
                raise PhaseAmbiguityError(
                    f"region {region!r} appears in phases "
                    f"{[p.id for p in contributors]} — request it per-phase "
                    f"(({region!r}, <phase_id>)) or pass "
                    f"target_phases={{{region!r}: <phase_id>}} "
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

        pair = (region, chosen.id)
        if pair in resolved_pairs:
            raise ValueError(f"duplicate region request {pair}")
        resolved_pairs.add(pair)

        slug = region if region_counts[region] == 1 else f"{region}@{chosen.id}"
        try:
            module = get_region_module(region)
        except UnknownRegionError:
            # ── Phase D structural fallback (opt-in) ─────────────────────
            if not allow_structural_fallback:
                raise
            from . import coverage
            try:
                records, s_notes = coverage.structural_provenance(
                    region, cited_values=cited_values)
            except KeyError as exc:
                raise UnknownRegionError(
                    f"region {region!r}: no registered module and no "
                    f"derivable structure — {exc}"
                ) from None
            all_slugs.append(slug)
            structural_regions.append(region)
            used_phase_ids.append(chosen.id)
            provenance[slug] = records
            notes.append(
                f"{slug}: STRUCTURAL FALLBACK (phase {chosen.id!r}, "
                f"{chosen.material_class.value}) — derived structure only")
            notes.extend(f"{slug}: {n}" for n in s_notes)
            if oxidation_state is not None:
                notes.append(
                    f"{slug}: oxidation_state {oxidation_state!r} has no "
                    "effect on a structural-fallback region (Layer C needs "
                    "a region module)")
            # the tiered fit-physics DB exposure rides along here too —
            # the machine tier may already carry an (UNVERIFIED) entry
            db_prov, db_notes = _fit_physics_provenance(
                region, provenance[slug], slot_facts=None)
            provenance[slug].extend(db_prov)
            notes.extend(f"{slug}: {note}" for note in db_notes)
            if any(str(r.get("constant", "")).startswith("fit_physics:")
                   for r in db_prov):
                # exposure semantics, stated where a consumer will read
                # them: these are SOURCED tier values (sha256-pinned NIST
                # archive; tier-status UNVERIFIED/CONDITIONAL), relayed
                # for reference and curation — NOT used to build
                # candidates, windows, or any fit-enabling quantity here
                notes.append(
                    f"{slug}: fit-physics DB entries exposed for reference "
                    "only (sourced tier, hand-verification pending) — not "
                    "used to build candidates or windows; positions remain "
                    "UNVERIFIED until cited/curated")
            continue

        candidates = module.build_candidates(chosen, oxidation_state=oxidation_state)
        _guard_slot_tags(candidates, region, chosen.id)
        per_request_candidates.append(candidates)
        slugs.append(slug)
        all_slugs.append(slug)
        used_phase_ids.append(chosen.id)
        notes.append(
            f"{slug}: phase {chosen.id!r} ({chosen.material_class.value}"
            + (f", {chosen.material}" if chosen.material else "")
            + f"), {len(candidates)} candidates"
        )
        for label, win in module.diagnostic_windows().items():
            diagnostic_windows[f"{slug}:{label}"] = win
        prov_fn = getattr(module, "provenance", None)
        provenance[slug] = list(prov_fn()) if callable(prov_fn) else []
        # tiered fit-physics DB exposure (run-brief item 4): the DB's
        # matching entries + mechanical cross-checks ride along in the
        # provenance (→ analysis namespace); candidate construction is
        # untouched — grammar constants stand until the machine-tier
        # human review (see autofit/fit_physics.py)
        # slot FACTS (the constants actually building candidates) ride
        # along so the DB cross-check cannot be satisfied by stale
        # provenance prose alone (Codex analyze review)
        slot_facts = {"splitting": [], "ratio": []}
        for cand in candidates:
            for s in cand.slots:
                if s.linked_offset_range and s.area_ratio is not None:
                    slot_facts["splitting"].append(
                        (float(s.linked_offset_range[0]),
                         float(s.linked_offset_range[1])))
                    slot_facts["ratio"].append(float(s.area_ratio))
        db_prov, db_notes = _fit_physics_provenance(
            region, provenance[slug], slot_facts=slot_facts)
        provenance[slug].extend(db_prov)
        notes.extend(f"{slug}: {note}" for note in db_notes)

    # Role-prefix collision guard (Codex Stage-2 re-review finding #2): the
    # composition sanitizer strips non-alphanumerics from slugs, so distinct
    # phase ids like 'B-4C' and 'B4C' would collapse into one role prefix and
    # silently collide in the lmfit parameter namespace.  Fail loudly instead.
    sanitized = [re.sub(r"[^A-Za-z0-9_]", "", s.replace(" ", ""))
                 for s in all_slugs]
    if len(set(sanitized)) != len(sanitized):
        dupes = sorted({s for s in sanitized if sanitized.count(s) > 1})
        raise ValueError(
            f"phase-qualified role slugs collide after sanitization: {dupes} — "
            "phase ids must remain distinct once spaces/punctuation are removed"
        )

    # Composition runs over MODULE-BACKED requests only: a structural-
    # fallback region has no candidates, and letting its empty set into the
    # cartesian product would wipe the deep regions' candidates.
    if not per_request_candidates:
        composed: list[CandidateModel] = []
    elif len(per_request_candidates) == 1:
        composed = per_request_candidates[0]
    else:
        composed = _compose_joint_candidates(slugs, per_request_candidates)
        notes.append(
            f"joint co-fit of {slugs}: {len(composed)} composed candidates"
        )
    if structural_regions and len(requests) > 1:
        notes.append(
            f"structural-fallback region(s) {structural_regions} excluded "
            "from candidate composition (derived structure only — no "
            "windows or candidates to compose)")

    grammar = CandidateGrammar(
        regions=tuple(region for region, _ in requests),
        phase_ids=tuple(dict.fromkeys(used_phase_ids)),
        candidates=composed,
        diagnostic_windows=diagnostic_windows,
        notes=notes,
        provenance=provenance,
        structural_only=tuple(structural_regions),
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
    slugs: list[str],
    per_request: list[list[CandidateModel]],
) -> list[CandidateModel]:
    """
    Cartesian composition of per-request candidate sets into joint models for
    one shared spectral window.  Slot roles are prefixed with the request's
    slug (region name, phase-qualified when the same region appears for
    multiple phases) to stay unique; the shared window uses ONE background
    (co-fit means one physical loss continuum).
    """
    composed: list[CandidateModel] = []
    for combo in itertools.product(*per_request):
        backgrounds = {c.background for c in combo}
        if len(backgrounds) != 1:
            raise ValueError(
                f"joint candidates must share one background, got {backgrounds} "
                f"for {[c.name for c in combo]}"
            )
        slots: list[ComponentSlot] = []
        shared: list[tuple[str, float, float]] = []
        for slug, cand in zip(slugs, combo):
            slug = re.sub(r"[^A-Za-z0-9_]", "", slug.replace(" ", ""))
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
    """Rewrite role / linked_to / fwhm_linked_to under the region prefix.

    Uses dataclasses.replace (ComponentSlot is frozen) rather than
    reconstructing the slot field-by-field: replace() carries every field
    NOT explicitly overridden forward unchanged, including any field added
    to ComponentSlot after this function was written. The manual
    reconstruction this replaced was exactly how broad_justification got
    silently dropped for every multi-region composed candidate (Codex-caught
    regression, 2026-07-20): a new field simply wasn't in the list, so it
    defaulted back to None for every slot passing through here — see
    tests/autofit/test_broad_justification.py's
    test_retag_slot_preserves_all_fields_except_the_three_rewritten, which
    guards against this exact class of bug recurring for whatever field
    comes next.
    """
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
    return replace(
        s,
        role=rename[s.role],
        linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None,
        fwhm_linked_to=fwhm_link,
    )


def _slot_param_prefix(role: str) -> str:
    """Must match engine._slot_prefix — kept here to rewrite fwhm links."""
    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"
