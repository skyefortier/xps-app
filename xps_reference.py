"""
Loader/validator for the version-controlled XPS reference dataset (data/xps/).

Validates every record against data/xps/schema.json plus semantic rules the
schema cannot express, then assembles the combined payload served by
GET /api/xps-reference. Validation NEVER silently skips a malformed record:
any failure raises :class:`XPSReferenceError` carrying the offending filename
and JSON path.

Energy conventions (must stay aligned with vgd_parser.py):
  - Photoelectron ``nominal_be_ev`` is source-invariant binding energy; it is
    drawn on the corrected-BE axis directly (never shifted by ccShift, never
    moved by the reference-source selector).
  - Auger lines store ``auger_ke_ev`` (source-invariant KINETIC energy). The
    apparent BE on a given source is computed at display time as
    ``photon_energy - auger_ke_ev - work_function`` — the same convention as
    vgd_parser's KE → BE conversion, NOT the simplified ``hv - KE``.
"""
import json
import math
from pathlib import Path

import jsonschema

from vgd_parser import DEFAULT_PHOTON_ENERGY, DEFAULT_WORK_FUNCTION

SCHEMA_FILE = "schema.json"
SOURCES_FILE = "sources.json"
ELEMENT_FILES = ("elements-main.json", "elements-lanthanides.json",
                 "elements-actinides.json")
AUGER_FILE = "auger-lines.json"
DATA_FILES = ELEMENT_FILES + (AUGER_FILE,)

# Legacy verbatim transcription (Stage 9). Loaded + validated when present;
# absent in the synthetic test datasets, so loading is optional.
LEGACY_DIR = "legacy"
LEGACY_SCHEMA_FILE = "schema.json"
LEGACY_SURVEY_FILE = "survey-lines.json"
LEGACY_CHEM_FILE = "chemical-states.json"

# Photon energies of the supported lab sources (eV). Al Kα reuses
# vgd_parser's constant so the two never drift; Mg Kα is the standard
# 1253.6 eV line (the "1254 eV" of Scofield 1976).
PHOTON_ENERGY_EV = {"AlKa": DEFAULT_PHOTON_ENERGY, "MgKa": 1253.6}


class XPSReferenceError(Exception):
    """Reference-data validation failure, pinpointing file + JSON path."""

    def __init__(self, filename: str, json_path: str, message: str):
        self.filename = filename
        self.json_path = json_path
        self.message = message
        super().__init__(f"{filename}: {json_path}: {message}")


# ─────────────────────────────────────────────────────────────────────────────
# Loading + schema validation
# ─────────────────────────────────────────────────────────────────────────────

def _read_json(data_dir: Path, fname: str):
    try:
        text = (data_dir / fname).read_text(encoding="utf-8")
    except FileNotFoundError:
        raise XPSReferenceError(fname, "$", "file not found") from None
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise XPSReferenceError(fname, "$", f"invalid JSON: {e}") from None


def _json_path(parts) -> str:
    return "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}"
                         for p in parts)


def _validate_schema(instance, def_name: str, schema: dict, fname: str) -> None:
    """Validate ``instance`` against ``#/$defs/<def_name>`` of schema.json."""
    validator = jsonschema.Draft202012Validator(
        {"$ref": f"#/$defs/{def_name}", "$defs": schema["$defs"]})
    error = jsonschema.exceptions.best_match(validator.iter_errors(instance))
    if error is not None:
        raise XPSReferenceError(fname, _json_path(error.absolute_path),
                                error.message)


# ─────────────────────────────────────────────────────────────────────────────
# Semantic validation (rules JSON Schema cannot express)
# ─────────────────────────────────────────────────────────────────────────────

def _validate_semantics(docs: dict, sources: dict) -> None:
    # Pass 1 — structural walk: file-role agreement, parent consistency,
    # cross-file element uniqueness, global id uniqueness.
    seen_symbols: dict[str, str] = {}            # symbol -> filename (element files)
    by_id: dict[str, tuple] = {}                 # id -> (fname, path, transition)
    walk: list[tuple] = []
    for fname, doc in docs.items():
        expected_type = "auger" if fname == AUGER_FILE else "photoelectron"
        for ei, el in enumerate(doc["elements"]):
            el_path = f"$.elements[{ei}]"
            if fname != AUGER_FILE:
                prev = seen_symbols.get(el["symbol"])
                if prev is not None:
                    raise XPSReferenceError(
                        fname, el_path,
                        f"element '{el['symbol']}' already defined in {prev}")
                seen_symbols[el["symbol"]] = fname
            for fi, fam in enumerate(el["families"]):
                for ti, t in enumerate(fam["transitions"]):
                    t_path = f"{el_path}.families[{fi}].transitions[{ti}]"
                    if t["transition_type"] != expected_type:
                        raise XPSReferenceError(
                            fname, t_path,
                            f"{fname} must contain only {expected_type} "
                            f"transitions, got '{t['transition_type']}' "
                            f"('{t['id']}')")
                    if t["element"] != el["symbol"] or t["z"] != el["z"]:
                        raise XPSReferenceError(
                            fname, t_path,
                            f"transition '{t['id']}' element/z "
                            f"({t['element']}, Z={t['z']}) does not match "
                            f"parent element ({el['symbol']}, Z={el['z']})")
                    if t["id"] in by_id:
                        prev_f, prev_p, _ = by_id[t["id"]]
                        raise XPSReferenceError(
                            fname, t_path,
                            f"duplicate transition id '{t['id']}' "
                            f"(first defined in {prev_f} at {prev_p})")
                    by_id[t["id"]] = (fname, t_path, t)
                    walk.append((fname, t_path, t))

    # Pass 2 — per-record checks needing the global id map.
    for fname, t_path, t in walk:
        if t["source"] not in sources:
            raise XPSReferenceError(
                fname, t_path,
                f"source id '{t['source']}' does not resolve in sources.json")
        for ci, cs in enumerate(t.get("chemical_states", ())):
            if cs["source"] not in sources:
                raise XPSReferenceError(
                    fname, f"{t_path}.chemical_states[{ci}]",
                    f"source id '{cs['source']}' does not resolve in "
                    f"sources.json")

        region = t["expected_region_ev"]
        if region["min"] > region["max"]:
            raise XPSReferenceError(
                fname, f"{t_path}.expected_region_ev",
                f"min ({region['min']}) exceeds max ({region['max']})")
        nominal = (t["nominal_be_ev"] if t["transition_type"] == "photoelectron"
                   else t["auger_ke_ev"])
        if not region["min"] <= nominal <= region["max"]:
            raise XPSReferenceError(
                fname, t_path,
                f"nominal energy {nominal} lies outside expected_region_ev "
                f"[{region['min']}, {region['max']}]")

        so = t.get("spin_orbit")
        if so is not None:
            so_path = f"{t_path}.spin_orbit"
            partner = by_id.get(so["partner_id"])
            if partner is None:
                raise XPSReferenceError(
                    fname, so_path,
                    f"partner_id '{so['partner_id']}' does not exist")
            partner_so = partner[2].get("spin_orbit")
            if partner_so is None or partner_so["partner_id"] != t["id"]:
                raise XPSReferenceError(
                    fname, so_path,
                    f"spin-orbit link to '{so['partner_id']}' is not "
                    f"reciprocal")
            if not math.isclose(partner_so["splitting_ev"], so["splitting_ev"],
                                rel_tol=1e-9):
                raise XPSReferenceError(
                    fname, so_path,
                    f"splitting_ev ({so['splitting_ev']}) disagrees with "
                    f"partner '{so['partner_id']}' ({partner_so['splitting_ev']})")
            if not math.isclose(so["area_ratio"] * partner_so["area_ratio"],
                                1.0, rel_tol=1e-3):
                raise XPSReferenceError(
                    fname, so_path,
                    f"area_ratio ({so['area_ratio']}) is not the reciprocal "
                    f"of partner's ({partner_so['area_ratio']})")


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def load_reference(data_dir) -> dict:
    """Load, validate, and assemble the full reference payload.

    Raises :class:`XPSReferenceError` on ANY structural or semantic problem —
    a malformed transition is never silently skipped.
    """
    data_dir = Path(data_dir)
    schema = _read_json(data_dir, SCHEMA_FILE)

    sources_doc = _read_json(data_dir, SOURCES_FILE)
    _validate_schema(sources_doc, "sourcesFile", schema, SOURCES_FILE)

    docs = {}
    for fname in DATA_FILES:
        doc = _read_json(data_dir, fname)
        _validate_schema(doc, "elementFile", schema, fname)
        docs[fname] = doc

    _validate_semantics(docs, sources_doc["sources"])

    legacy = _load_legacy(data_dir, sources_doc["sources"])

    return {
        "schema_version": 1,
        "sources": sources_doc["sources"],
        "elements": [el for f in ELEMENT_FILES for el in docs[f]["elements"]],
        "auger": docs[AUGER_FILE]["elements"],
        "legacy": legacy,
        "conventions": {
            # Exposed so the UI can DISPLAY (never silently assume) the
            # defaults used to place Auger markers on the BE axis.
            "default_source": "AlKa",
            "photon_energy_ev": PHOTON_ENERGY_EV,
            "work_function_ev": DEFAULT_WORK_FUNCTION,
            "auger_apparent_be": "photon_energy_ev - auger_ke_ev - work_function_ev",
        },
    }


def _load_legacy(data_dir: Path, sources: dict):
    """Load + validate the verbatim legacy docs (Stage 9), if present.

    Returns ``{"survey": [...elements], "chemical_states": [...groups]}`` or
    ``None`` when the legacy directory is absent. Validates against the legacy
    schema and enforces globally-unique ids + source resolution — a malformed
    legacy record fails loudly exactly like a curated one.
    """
    legacy_dir = data_dir / LEGACY_DIR
    if not legacy_dir.exists():
        return None
    schema = _read_json(legacy_dir, LEGACY_SCHEMA_FILE)
    rel = lambda f: f"{LEGACY_DIR}/{f}"

    survey = _read_json(legacy_dir, LEGACY_SURVEY_FILE)
    _validate_schema(survey, "legacySurveyFile", schema, rel(LEGACY_SURVEY_FILE))
    chem = _read_json(legacy_dir, LEGACY_CHEM_FILE)
    _validate_schema(chem, "legacyChemStatesFile", schema, rel(LEGACY_CHEM_FILE))

    seen: dict[str, str] = {}
    def check(rec_id, src, fname, path):
        if rec_id in seen:
            raise XPSReferenceError(fname, path,
                f"duplicate legacy id '{rec_id}' (first in {seen[rec_id]})")
        seen[rec_id] = fname
        if src not in sources:
            raise XPSReferenceError(fname, path,
                f"source id '{src}' does not resolve in sources.json")

    for ei, el in enumerate(survey["elements"]):
        for li, ln in enumerate(el["lines"]):
            check(ln["id"], ln["source"], rel(LEGACY_SURVEY_FILE),
                  f"$.elements[{ei}].lines[{li}]")
    for gi, g in enumerate(chem["groups"]):
        for si, s in enumerate(g["states"]):
            check(s["id"], s["source"], rel(LEGACY_CHEM_FILE),
                  f"$.groups[{gi}].states[{si}]")

    return {"survey": survey["elements"], "chemical_states": chem["groups"]}


# Per-process cache: data dir -> (mtime stamp, payload). Reference data is
# read-only at runtime, so this is safe under multi-worker gunicorn; the
# mtime stamp keeps dev edits live without a restart.
_cache: dict[str, tuple] = {}


def load_reference_cached(data_dir) -> dict:
    data_dir = Path(data_dir)
    try:
        stamp = [(f, (data_dir / f).stat().st_mtime_ns)
                 for f in (SCHEMA_FILE, SOURCES_FILE) + DATA_FILES]
        legacy_dir = data_dir / LEGACY_DIR
        if legacy_dir.exists():
            for f in (LEGACY_SCHEMA_FILE, LEGACY_SURVEY_FILE, LEGACY_CHEM_FILE):
                stamp.append((f"{LEGACY_DIR}/{f}", (legacy_dir / f).stat().st_mtime_ns))
        stamp = tuple(stamp)
    except FileNotFoundError as e:
        raise XPSReferenceError(Path(e.filename).name, "$",
                                "file not found") from None
    key = str(data_dir.resolve())
    hit = _cache.get(key)
    if hit is not None and hit[0] == stamp:
        return hit[1]
    payload = load_reference(data_dir)
    _cache[key] = (stamp, payload)
    return payload
