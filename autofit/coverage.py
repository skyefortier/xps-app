"""
Phase D — derivable element structure for the whole periodic table (Z=1..96).

THE ANTI-CONFABULATION RAIL GOVERNS THIS MODULE: nothing here emits a
binding energy, a spin-orbit splitting magnitude, an RSF, a FWHM, or any
other empirical value — not from memory, not from a formula estimate.
Everything emitted is derivable from electron configuration + quantum
bookkeeping alone:

- which subshells are occupied (Madelung/Aufbau filling — an algorithm);
- spin-orbit doublet vs singlet structure (l > 0 → j = l ± 1/2);
- THEORETICAL (2j+1) area-ratio expectations for filled subshells —
  expectations only, never constraints (the Cl 2p adjudication measured a
  real doublet pegging past its ratio bound: Coster-Kronig and
  cross-section effects move measured ratios off the statistical value);
- an open-d/f multiplet-prone FLAG (a flag, never a splitting);
- a coarse conductor-class default from periodic position, always
  user-overridable.

Every derived field carries a ``derived:<rule>`` provenance tag. Every
value-bearing field (``binding_energy_ev``) exists but is ``None`` — the
cited-source loader (autofit.cited_values, unit D2) is the ONLY way an
empirical value enters this framework, and it demands a citation.
``tests/autofit/test_coverage_structure.py`` walks the full Z=1..96 output
and fails on any populated value-bearing field.

Element symbol/Z/name facts are DEFINITIONAL, not measured — but even
those are not re-transcribed from memory: the table below was GENERATED
(2026-07-05) from the committed single source of truth,
``scripts/gen_machine_tier.py::PERIODIC_TABLE`` (the same table the NIST
acquisition pipeline validates against committed data), restricted to the
goal's Z=1..96 span, and is cross-pinned to it by test.
"""

from __future__ import annotations

import copy
import re
from fractions import Fraction
from typing import Optional, Union

__all__ = [
    "PERIODIC_TABLE", "element_structure", "level_structure", "parse_region",
    "structural_provenance",
]

# Generated from scripts/gen_machine_tier.py PERIODIC_TABLE (Z <= 96);
# cross-pinned by test_periodic_table_cross_pinned_to_committed_source.
PERIODIC_TABLE: dict[str, tuple[int, str]] = {
    "H": (1, "Hydrogen"), "He": (2, "Helium"), "Li": (3, "Lithium"),
    "Be": (4, "Beryllium"), "B": (5, "Boron"), "C": (6, "Carbon"),
    "N": (7, "Nitrogen"), "O": (8, "Oxygen"), "F": (9, "Fluorine"),
    "Ne": (10, "Neon"), "Na": (11, "Sodium"), "Mg": (12, "Magnesium"),
    "Al": (13, "Aluminium"), "Si": (14, "Silicon"), "P": (15, "Phosphorus"),
    "S": (16, "Sulfur"), "Cl": (17, "Chlorine"), "Ar": (18, "Argon"),
    "K": (19, "Potassium"), "Ca": (20, "Calcium"), "Sc": (21, "Scandium"),
    "Ti": (22, "Titanium"), "V": (23, "Vanadium"), "Cr": (24, "Chromium"),
    "Mn": (25, "Manganese"), "Fe": (26, "Iron"), "Co": (27, "Cobalt"),
    "Ni": (28, "Nickel"), "Cu": (29, "Copper"), "Zn": (30, "Zinc"),
    "Ga": (31, "Gallium"), "Ge": (32, "Germanium"), "As": (33, "Arsenic"),
    "Se": (34, "Selenium"), "Br": (35, "Bromine"), "Kr": (36, "Krypton"),
    "Rb": (37, "Rubidium"), "Sr": (38, "Strontium"), "Y": (39, "Yttrium"),
    "Zr": (40, "Zirconium"), "Nb": (41, "Niobium"), "Mo": (42, "Molybdenum"),
    "Tc": (43, "Technetium"), "Ru": (44, "Ruthenium"), "Rh": (45, "Rhodium"),
    "Pd": (46, "Palladium"), "Ag": (47, "Silver"), "Cd": (48, "Cadmium"),
    "In": (49, "Indium"), "Sn": (50, "Tin"), "Sb": (51, "Antimony"),
    "Te": (52, "Tellurium"), "I": (53, "Iodine"), "Xe": (54, "Xenon"),
    "Cs": (55, "Caesium"), "Ba": (56, "Barium"), "La": (57, "Lanthanum"),
    "Ce": (58, "Cerium"), "Pr": (59, "Praseodymium"),
    "Nd": (60, "Neodymium"), "Pm": (61, "Promethium"),
    "Sm": (62, "Samarium"), "Eu": (63, "Europium"), "Gd": (64, "Gadolinium"),
    "Tb": (65, "Terbium"), "Dy": (66, "Dysprosium"), "Ho": (67, "Holmium"),
    "Er": (68, "Erbium"), "Tm": (69, "Thulium"), "Yb": (70, "Ytterbium"),
    "Lu": (71, "Lutetium"), "Hf": (72, "Hafnium"), "Ta": (73, "Tantalum"),
    "W": (74, "Tungsten"), "Re": (75, "Rhenium"), "Os": (76, "Osmium"),
    "Ir": (77, "Iridium"), "Pt": (78, "Platinum"), "Au": (79, "Gold"),
    "Hg": (80, "Mercury"), "Tl": (81, "Thallium"), "Pb": (82, "Lead"),
    "Bi": (83, "Bismuth"), "Po": (84, "Polonium"), "At": (85, "Astatine"),
    "Rn": (86, "Radon"), "Fr": (87, "Francium"), "Ra": (88, "Radium"),
    "Ac": (89, "Actinium"), "Th": (90, "Thorium"),
    "Pa": (91, "Protactinium"), "U": (92, "Uranium"),
    "Np": (93, "Neptunium"), "Pu": (94, "Plutonium"),
    "Am": (95, "Americium"), "Cm": (96, "Curium"),
}

_BY_Z: dict[int, str] = {z: sym for sym, (z, _) in PERIODIC_TABLE.items()}

_L_LETTER = "spdf"

_REGION_RE = re.compile(r"^([A-Z][a-z]?)\s+([1-7][spdf])$")

_CONFIGURATION_CAVEAT = (
    "Madelung (n+l, n) Aufbau filling — a derivation rule, not a lookup. A "
    "handful of true neutral-atom ground states deviate from it via "
    "near-degenerate s/d/f redistribution; those anomalies are NOT encoded "
    "(no-invention rail). Deviations can shift valence occupancy details "
    "(and so the multiplet flag's edge cases), never the deep core-level "
    "list XPS actually addresses."
)

_RATIO_CAVEAT = (
    "Theoretical (2j+1) statistical expectation for a FILLED subshell. "
    "Measured doublet ratios deviate from the statistical value "
    "(Coster-Kronig broadening, photoionization cross-section effects); "
    "this lab's Cl 2p adjudication is the documented example "
    "(docs/autofit/adjudication-decisions.md #7). Treat as a default "
    "EXPECTATION, never a hard constraint: allow a free/relaxed ratio and "
    "independent doublet widths when fitting."
)

_MULTIPLET_CAVEAT = (
    "Flag derived from the NEUTRAL-ATOM Madelung configuration. Oxidation "
    "states repopulate d/f in both directions (a d10 metal can be d9 as a "
    "2+ cation and vice versa), and some true ground states deviate from "
    "the Madelung rule — advisory only: never a constraint, never a "
    "splitting magnitude."
)

_CONDUCTOR_CAVEAT = (
    "Coarse ELEMENTAL-SOLID default from periodic position (the classic "
    "six-metalloid staircase convention: B, Si, Ge, As, Sb, Te). Allotrope- "
    "and compound-dependent — graphite conducts while diamond insulates, "
    "and most oxides insulate regardless of the element's class. Always "
    "user-overridable: the declared Phase.material_class wins."
)

# The six classical metalloids by (period, group) — a positional
# classification convention, not a measurement.
_STAIRCASE: frozenset[tuple[int, int]] = frozenset({
    (2, 13), (3, 14), (4, 14), (4, 15), (5, 15), (5, 16),
})


def _madelung_subshells() -> list[tuple[int, int]]:
    """(n, l) in Madelung filling order — sorted by (n+l, n). l <= 3 (s..f)
    covers every occupied subshell through Z = 96 (5g first fills far
    beyond)."""
    shells = [(n, l) for n in range(1, 9) for l in range(0, min(n, 4))]
    shells.sort(key=lambda nl: (nl[0] + nl[1], nl[0]))
    return shells


_MADELUNG_ORDER = _madelung_subshells()


def _configuration(z: int) -> list[dict]:
    """Madelung filling of ``z`` electrons → ordered occupied subshells."""
    remaining = z
    config: list[dict] = []
    for n, l in _MADELUNG_ORDER:
        if remaining <= 0:
            break
        capacity = 2 * (2 * l + 1)
        occ = min(capacity, remaining)
        remaining -= occ
        config.append({
            "subshell": f"{n}{_L_LETTER[l]}",
            "n": n, "l": l, "occupancy": occ,
        })
    return config


def _components(n: int, l: int) -> list[dict]:
    """Spin-orbit components, higher-j (parent) first — exact bookkeeping:
    j = l ± 1/2, degeneracy 2j + 1."""
    label = f"{n}{_L_LETTER[l]}"
    if l == 0:
        return [{"label": label, "j": "1/2", "degeneracy": 2}]
    return [
        {"label": f"{label}{2 * l + 1}/2", "j": f"{2 * l + 1}/2",
         "degeneracy": 2 * l + 2},
        {"label": f"{label}{2 * l - 1}/2", "j": f"{2 * l - 1}/2",
         "degeneracy": 2 * l},
    ]


def _statistical_ratio(l: int) -> dict:
    """Lower-j over higher-j degeneracy ratio, exact rational: 2l/(2l+2) =
    l/(l+1) → p 1:2, d 2:3, f 3:4. Matches the grammar's existing
    ``area_ratio`` convention (Cl 2p 1:2, U 4f 3:4 as child/parent)."""
    frac = Fraction(l, l + 1)
    return {
        "numerator": frac.numerator,
        "denominator": frac.denominator,
        "value": frac.numerator / frac.denominator,
        "convention": "lower_j_over_higher_j",
        "expectation_only": True,
        "derived_rule": "derived:statistical_2j_plus_1",
        "caveat": _RATIO_CAVEAT,
    }


def _level_record(c: dict) -> dict:
    n, l, occ = c["n"], c["l"], c["occupancy"]
    capacity = 2 * (2 * l + 1)
    partial = occ < capacity
    return {
        "level": c["subshell"],
        "n": n, "l": l,
        "occupancy": occ, "capacity": capacity,
        "partially_filled": partial,
        "structure": "singlet" if l == 0 else "doublet",
        "components": _components(n, l),
        # (2j+1) bookkeeping presumes a filled shell — a partially-filled
        # (valence-character) subshell gets NO ratio expectation.
        "statistical_area_ratio": None if (l == 0 or partial)
                                  else _statistical_ratio(l),
        # THE value-bearing field: always None here. Only the cited-source
        # loader (autofit.cited_values) may populate positions, and only
        # with a citation. UNVERIFIED until then.
        "binding_energy_ev": None,
        "derived_rule": "derived:aufbau_madelung+spin_orbit_j_coupling",
    }


def _period_group_block(config: list[dict]) -> tuple[int, Optional[int], str]:
    period = max(c["n"] for c in config)
    last = config[-1]           # the subshell that received the last electron
    block = _L_LETTER[last["l"]]
    occ = {c["subshell"]: c["occupancy"] for c in config}
    n = last["n"]
    if block == "s":
        group: Optional[int] = 18 if last["subshell"] == "1s" and occ["1s"] == 2 \
            else occ[f"{n}s"]
    elif block == "p":
        group = 12 + occ[f"{n}p"]
        period = n
    elif block == "d":
        group = occ[f"{n}d"] + occ.get(f"{n + 1}s", 0)
        period = n + 1
    else:                        # f-block: no group number
        group = None
        period = n + 2
    return period, group, block


def _conductor_class(z: int, period: int, group: Optional[int],
                     block: str) -> str:
    """Positional default (see _CONDUCTOR_CAVEAT). Rule:
    H/He → insulator (molecular/noble elemental solids, documented special
    case); f- and d-block and s-block (Z > 2) → conductor; p-block:
    the staircase (period, group) pairs → semiconductor, group >= 17 →
    insulator (halogens/nobles), groups left of the period's staircase →
    conductor, the rest → insulator."""
    if z in (1, 2):
        return "insulator"
    if block in ("d", "f", "s"):
        return "conductor"
    assert group is not None
    if (period, group) in _STAIRCASE:
        return "semiconductor"
    if group >= 17:
        return "insulator"
    stair_groups = [g for p, g in _STAIRCASE if p == period]
    if not stair_groups:         # period 6+: no staircase — p-metals
        return "conductor"
    if group < min(stair_groups):
        return "conductor"
    return "insulator"


_STRUCTURE_CACHE: dict[str, dict] = {}


def element_structure(element: Union[str, int]) -> dict:
    """Full derived structure for one element (symbol or Z), Z = 1..96.

    Contains ONLY derivable structure (see module docstring) — every
    value-bearing field is None, every derived field rule-tagged. Raises
    KeyError for unknown elements.
    """
    if isinstance(element, int):
        try:
            symbol = _BY_Z[element]
        except KeyError:
            raise KeyError(f"no element with Z={element} in the Z=1..96 span")
    else:
        symbol = element
    if symbol not in PERIODIC_TABLE:
        raise KeyError(f"unknown element symbol {symbol!r}")
    cached = _STRUCTURE_CACHE.get(symbol)
    if cached is not None:
        # deep copy: callers must not be able to mutate the cache
        return copy.deepcopy(cached)

    z, name = PERIODIC_TABLE[symbol]
    config = _configuration(z)
    period, group, block = _period_group_block(config)
    multiplet = any(c["l"] >= 2 and 0 < c["occupancy"] < 2 * (2 * c["l"] + 1)
                    for c in config)
    st: dict = {
        "symbol": symbol, "z": z, "name": name,
        "configuration": config,
        "configuration_rule": "derived:aufbau_madelung",
        "configuration_caveat": _CONFIGURATION_CAVEAT,
        "levels": [_level_record(c) for c in config],
        "multiplet_prone": multiplet,
        "multiplet_rule": "derived:open_shell_d_f_madelung",
        "multiplet_caveat": _MULTIPLET_CAVEAT,
        "conductor_class_default": _conductor_class(z, period, group, block),
        "conductor_class_rule": "derived:periodic_position_metalloid_staircase",
        "conductor_class_caveat": _CONDUCTOR_CAVEAT,
        "period": period, "group": group, "block": block,
    }
    _STRUCTURE_CACHE[symbol] = st
    return copy.deepcopy(st)


def level_structure(element: Union[str, int], level: str) -> dict:
    """One occupied level's derived record ('Cl', '2p'). KeyError when the
    subshell is not occupied for that element."""
    st = element_structure(element)
    for lv in st["levels"]:
        if lv["level"] == level:
            return lv
    raise KeyError(
        f"{st['symbol']}: subshell {level!r} is not occupied "
        f"(occupied: {[l['level'] for l in st['levels']]})"
    )


def parse_region(label: str) -> Optional[tuple[str, str]]:
    """'Cl 2p' → ('Cl', '2p'); None when the label is not an element+level
    region or the element is outside the Z=1..96 table."""
    m = _REGION_RE.match(label.strip())
    if not m:
        return None
    sym, level = m.group(1), m.group(2)
    if sym not in PERIODIC_TABLE:
        return None
    return sym, level


def structural_provenance(region: str, cited_values=None
                          ) -> tuple[list[dict], list[str]]:
    """Derived-structure provenance records + honesty notes for one
    element/level region ('Fe 2p') — the resolve() structural-fallback
    payload (Phase D unit 3).

    Status semantics (existing {VERIFIED, CONDITIONAL, UNVERIFIED}
    vocabulary, so the methods' uses_conditional_or_unverified_constants
    rollup works unchanged):

    - exact quantum bookkeeping (doublet/singlet, degeneracies) →
      VERIFIED (it is mathematics, not an empirical claim);
    - ratio EXPECTATIONS and advisory flags (multiplet, conductor class) →
      CONDITIONAL (theory/heuristics that real samples deviate from);
    - positions → UNVERIFIED with value None, until a cited source is
      loaded (autofit.cited_values), whose records then ride along with
      their own status (CONDITIONAL, or UNVERIFIED for test_only files).

    Raises KeyError when the region is not parseable as an element/level
    in the Z=1..96 table or the subshell is not occupied.
    """
    parsed = parse_region(region)
    if parsed is None:
        raise KeyError(
            f"region {region!r} is not an '<Element> <n><subshell>' label "
            "within the Z=1..96 table")
    sym, subshell = parsed
    lv = level_structure(sym, subshell)      # KeyError when not occupied
    st = element_structure(sym)

    records: list[dict] = [
        {"constant": "structure",
         "value": {"level": lv["level"], "structure": lv["structure"],
                   "components": lv["components"],
                   "occupancy": lv["occupancy"], "capacity": lv["capacity"],
                   "partially_filled": lv["partially_filled"]},
         "status": "VERIFIED",
         "derived_rule": lv["derived_rule"],
         "source": f"{lv['derived_rule']} — exact quantum bookkeeping "
                   "(j = l ± 1/2, degeneracy 2j+1), not an empirical claim"},
    ]
    ratio = lv["statistical_area_ratio"]
    if ratio is not None:
        records.append({
            "constant": "statistical_area_ratio_expectation",
            "value": ratio,
            "status": "CONDITIONAL",
            "derived_rule": ratio["derived_rule"],
            "source": f"{ratio['derived_rule']} — theoretical expectation "
                      "ONLY (see value.caveat); never a hard constraint: "
                      "allow a free/relaxed ratio and independent widths"})
    records.extend([
        {"constant": "binding_energy_ev",
         "value": None,
         "status": "UNVERIFIED",
         "source": "no VERIFIED position — supply a cited source via "
                   "autofit.cited_values (schema in that module's "
                   "docstring); the engine never invents a number"},
        {"constant": "multiplet_prone_flag",
         "value": st["multiplet_prone"],
         "status": "CONDITIONAL",
         "derived_rule": st["multiplet_rule"],
         "source": f"{st['multiplet_rule']} — advisory flag (oxidation "
                   "states repopulate d/f; see element caveat); never a "
                   "splitting"},
        {"constant": "conductor_class_default",
         "value": st["conductor_class_default"],
         "status": "CONDITIONAL",
         "derived_rule": st["conductor_class_rule"],
         "source": f"{st['conductor_class_rule']} — coarse positional "
                   "default, user-overridable (the declared "
                   "Phase.material_class wins)"},
    ])

    notes = [
        "structure known, positions UNVERIFIED — supply a cited source "
        "(autofit.cited_values) and curated windows/widths to enable "
        "fitting; no fit candidates built",
    ]
    matching = [v for v in (cited_values or [])
                if v.element == sym and v.level == subshell]
    for v in matching:
        records.append({
            "constant": f"cited:{v.value_type}[{v.component or v.level}]",
            "value": {"value_ev": v.value_ev,
                      "uncertainty_ev": v.uncertainty_ev,
                      "oxidation_state": v.oxidation_state,
                      "method": v.method, "convention": v.convention,
                      "test_only": v.test_only},
            "status": v.status,
            "source": v.source_citation})
    if matching:
        notes.append(
            f"{len(matching)} cited value(s) loaded for {region} — fitting "
            "still requires curated windows/widths (cited positions alone "
            "do not build candidates)")
    return records, notes
