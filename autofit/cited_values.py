"""
Phase D — cited-source empirical-value loader.

THE ONLY PATH by which an empirical value (a binding-energy position or a
spin-orbit splitting magnitude) may enter the Phase D coverage framework
(autofit.coverage emits structure only; every one of its value-bearing
fields is None). Extends the existing tiered-provenance system
(data/xps fit-physics tiers: machine → UNVERIFIED, curated → CONDITIONAL)
with a ``user_cited`` tier:

- NOTHING loads without a non-empty, non-placeholder ``source_citation``;
- every row is cross-checked against the derivable structure (element in
  the Z=1..96 table, subshell occupied, component label real);
- loaded rows are at best **CONDITIONAL** (cited, not verified on this
  lab's samples) — a load can NEVER mint VERIFIED status;
- a file marked ``test_only`` is forced **UNVERIFIED** and every record
  carries the flag (the committed example fixture is such a file, with
  deliberately non-physical values);
- the loader holds no defaults: an empty table loads to an empty list.

Formats: JSON (``{"schema_version": 1, "test_only": bool?, "rows": [...]}``)
or CSV (header = the row fields; treated as schema v1, not test-only).
Row fields: element, level (subshell ``2p`` or component ``2p3/2``),
oxidation_state?, value_type (``binding_energy_ev`` |
``spin_orbit_splitting_ev``), value_ev, uncertainty_ev?,
source_citation, method?, convention?.
"""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from typing import Optional

from . import coverage

__all__ = ["CitedValue", "CitedValueError", "load_cited_values"]


class CitedValueError(ValueError):
    """A cited-values table failed validation (message carries the row)."""


_VALUE_TYPES = ("binding_energy_ev", "spin_orbit_splitting_ev")

_REQUIRED = frozenset({"element", "level", "value_type", "value_ev",
                       "source_citation"})
_OPTIONAL = frozenset({"oxidation_state", "uncertainty_ev", "method",
                       "convention"})

# Rejected even when non-empty: citation laundering via placeholder text
# (extended after the Codex D2 review — both runs probed "n-a"/"false"/"0"
# through the original set).
_PLACEHOLDER_CITATIONS = frozenset({
    "none", "unknown", "n/a", "n-a", "na", "todo", "tbd", "?", "-", "--",
    "false", "true", "0", "null", "nil", "no",
})

_LEVEL_RE = re.compile(r"^([1-7][spdf])(\d/2)?$")


@dataclass(frozen=True)
class CitedValue:
    element: str
    level: str                       # subshell, e.g. "2p"
    component: Optional[str]         # full component label, e.g. "2p3/2"
    oxidation_state: Optional[str]
    value_type: str
    value_ev: float
    uncertainty_ev: Optional[float]
    source_citation: str
    method: Optional[str]
    convention: Optional[str]
    test_only: bool
    status: str                      # CONDITIONAL (cited) | UNVERIFIED (test)


def _reject(i: int, reason: str) -> "CitedValueError":
    return CitedValueError(f"row {i}: {reason}")


def _validate_row(i: int, row: dict, test_only: bool) -> CitedValue:
    if not isinstance(row, dict):
        raise _reject(i, f"row must be an object, got {type(row).__name__}")

    unknown = set(row) - _REQUIRED - _OPTIONAL
    if unknown:
        raise _reject(i, f"unknown field(s) {sorted(unknown)} — "
                         "typo guard: unknown keys are never ignored")
    missing = {k for k in _REQUIRED if row.get(k) is None
               or (isinstance(row.get(k), str) and not row[k].strip())}
    if "source_citation" in missing:
        raise _reject(i, "source_citation is REQUIRED — nothing loads "
                         "without a citation")
    if missing:
        raise _reject(i, f"missing required field(s) {sorted(missing)}")

    # a citation is TEXT — JSON false/true/0/numbers must not be
    # str()-coerced into "citations" (Codex D2 review, both runs)
    if not isinstance(row["source_citation"], str):
        raise _reject(i, f"source_citation must be a string, got "
                         f"{row['source_citation']!r} — a non-text value "
                         "is not a citation")
    citation = row["source_citation"].strip()
    # placeholder detection runs on a CANONICAL form (D2 re-check, run A
    # MAJOR: "n–a", "None.", "n - a" loaded): unicode dashes → hyphen,
    # internal whitespace removed, edge punctuation stripped, lowercased.
    # The stored citation stays verbatim; only the check normalizes.
    canonical = re.sub(r"[‐-―−]", "-", citation.lower())
    canonical = re.sub(r"\s+", "", canonical).strip(".,;:!?()[]{}'\"")
    if not canonical or canonical in _PLACEHOLDER_CITATIONS:
        raise _reject(i, f"placeholder citation {citation!r} rejected — "
                         "a real source citation is required")

    element = str(row["element"]).strip()
    if element not in coverage.PERIODIC_TABLE:
        raise _reject(i, f"unknown element {element!r} (Z=1..96 table)")

    m = _LEVEL_RE.match(str(row["level"]).strip())
    if not m:
        raise _reject(i, f"level {row['level']!r} is not a subshell "
                         "('2p') or component ('2p3/2') label")
    subshell, j_suffix = m.group(1), m.group(2)
    try:
        level = coverage.level_structure(element, subshell)
    except KeyError:
        raise _reject(i, f"subshell {subshell!r} is not occupied for "
                         f"{element} (structure cross-check)")
    component: Optional[str] = None
    if j_suffix:
        component = f"{subshell}{j_suffix}"
        labels = [c["label"] for c in level["components"]]
        if component not in labels:
            raise _reject(i, f"component {component!r} does not exist for "
                             f"{element} {subshell} (components: {labels})")

    value_type = str(row["value_type"]).strip()
    if value_type not in _VALUE_TYPES:
        raise _reject(i, f"value_type {value_type!r} not in {_VALUE_TYPES} "
                         "— RSFs/FWHMs/etc. are not loadable quantities here")
    if value_type == "spin_orbit_splitting_ev":
        if level["structure"] != "doublet":
            raise _reject(i, f"{element} {subshell} is not a doublet — "
                             "no spin-orbit splitting exists for it")
        if component is not None:
            raise _reject(i, "a splitting belongs to the subshell, not a "
                             "component — drop the j suffix")

    # bool is an int subclass (float(True) == 1.0) — a JSON true must not
    # silently load as a 1.0 eV value
    if isinstance(row["value_ev"], bool):
        raise _reject(i, f"value_ev {row['value_ev']!r} is not numeric")
    try:
        value_ev = float(row["value_ev"])
    except (TypeError, ValueError):
        raise _reject(i, f"value_ev {row['value_ev']!r} is not numeric")
    if not math.isfinite(value_ev):
        raise _reject(i, "value_ev must be finite")
    if value_ev <= 0.0:
        raise _reject(i, "value_ev must be positive (XPS binding-energy "
                         "scale; splittings are magnitudes)")

    uncertainty: Optional[float] = None
    if row.get("uncertainty_ev") is not None:
        if isinstance(row["uncertainty_ev"], bool):
            raise _reject(i, f"uncertainty_ev {row['uncertainty_ev']!r} "
                             "is not numeric")
        try:
            uncertainty = float(row["uncertainty_ev"])
        except (TypeError, ValueError):
            raise _reject(i, f"uncertainty_ev {row['uncertainty_ev']!r} "
                             "is not numeric")
        if not math.isfinite(uncertainty) or uncertainty < 0.0:
            raise _reject(i, "uncertainty_ev must be finite and >= 0")

    def _opt(key: str) -> Optional[str]:
        v = row.get(key)
        if v is None:
            return None
        v = str(v).strip()
        return v or None

    return CitedValue(
        element=element,
        level=subshell,
        component=component,
        oxidation_state=_opt("oxidation_state"),
        value_type=value_type,
        value_ev=value_ev,
        uncertainty_ev=uncertainty,
        source_citation=citation,
        method=_opt("method"),
        convention=_opt("convention"),
        test_only=test_only,
        # A load can never mint VERIFIED: cited-but-not-lab-verified is
        # CONDITIONAL (mirrors the curated tier); test files are UNVERIFIED.
        status="UNVERIFIED" if test_only else "CONDITIONAL",
    )


def _rows_from_json(path: str) -> tuple[list[dict], bool]:
    try:
        with open(path) as f:
            doc = json.load(f)
    except ValueError as e:
        raise CitedValueError(f"{path}: not valid JSON ({e})")
    if not isinstance(doc, dict):
        raise CitedValueError(f"{path}: top level must be an object")
    sv = doc.get("schema_version")
    # bool is an int subclass (True == 1) and 1.0 == 1 — the gate is a
    # strict INTEGER 1, no cross-type equality
    if isinstance(sv, bool) or not isinstance(sv, int) or sv != 1:
        raise CitedValueError(
            f"{path}: unsupported schema_version {sv!r} (expected 1)")
    rows = doc.get("rows")
    if not isinstance(rows, list):
        raise CitedValueError(f"{path}: 'rows' must be a list")
    test_only = doc.get("test_only", False)
    # part of the provenance contract — no truthiness coercion
    # (bool("false") is True; 1 is not a declaration)
    if not isinstance(test_only, bool):
        raise CitedValueError(
            f"{path}: test_only must be a JSON boolean, got {test_only!r}")
    return rows, test_only


def _rows_from_csv(path: str) -> tuple[list[dict], bool]:
    rows: list[dict] = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return [], False
        # DictReader silently collapses duplicate header names (last cell
        # wins) — a blank source_citation could hide behind a duplicated
        # column (Codex D2 review, both runs). Validate the header first.
        dupes = sorted({h for h in header if header.count(h) > 1})
        if dupes:
            raise CitedValueError(
                f"{path}: duplicate CSV header column(s) {dupes} — "
                "malformed table rejected")
        if any(not h.strip() for h in header):
            raise CitedValueError(f"{path}: empty CSV header column name")
        for n, cells in enumerate(reader):
            if len(cells) > len(header):
                raise CitedValueError(
                    f"row {n}: malformed CSV row — more cells than header "
                    f"columns (overflow: {cells[len(header):]!r})")
            # blank CSV cells are absent optionals, not empty strings
            rows.append({k: (v if v != "" else None)
                         for k, v in zip(header, cells)})
    return rows, False


def load_cited_values(path: str) -> list[CitedValue]:
    """Load + validate a cited-values table (JSON or CSV by extension).

    Raises :class:`CitedValueError` on the FIRST invalid row (index in the
    message) — a provenance table is all-or-nothing, no partial loads.
    """
    if path.lower().endswith(".csv"):
        rows, test_only = _rows_from_csv(path)
    else:
        rows, test_only = _rows_from_json(path)
    return [_validate_row(i, row, test_only) for i, row in enumerate(rows)]
