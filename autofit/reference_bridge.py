"""
Unit R1 — the data/xps → autofit reference bridge.

Marries the two halves the Phase D framework kept deliberately separate:

- STRUCTURE from :mod:`autofit.coverage` — derivable quantum bookkeeping
  (levels, doublet/singlet, (2j+1) ratio expectations, flags); never a
  number from memory.
- POSITIONS from the committed ``data/xps`` tiers — every value loaded
  through :func:`xps_reference.load_reference` (the SAME loader that
  serves ``/api/xps-reference``, so its schema + semantic validation is
  inherited wholesale) and, for the machine tier, joined with the
  provenance sidecar (``elements-machine.provenance.json``: NIST
  reference code, archived source URL, artifact sha256, parse method,
  corroboration flags).

ANTI-INVENTION CONTRACT: the bridge emits NOTHING not present in
data/xps. No fallbacks, no interpolation, no memory. An element/level
with no tier data returns empty lists — the Phase D degradation story
(structure known, positions UNVERIFIED) stands unchanged.

Tier → status mapping (goal-prescribed, 2026-07-05):

- ``curated``  → **VERIFIED** — the schema defines curated as "all listed
  values verified against the cited sources" (curator-verified); still
  user-confirmable — the records remain fully visible in provenance.
- ``machine``  → **CONDITIONAL** — sourced and sha-pinned (NIST-evaluated
  starred records from archived SRD-20 snapshots) but NOT human-verified;
  the "not human-verified" caveat rides on every record.
- ``legacy``   → **UNVERIFIED** — verbatim legacy-embedded-dataset values
  (survey lines + chemical states), exposed, never upgraded.

DOCUMENTED DEVIATION: :mod:`autofit.fit_physics` (the older exposure-only
wiring) maps machine → UNVERIFIED and curated → CONDITIONAL. That mapping
predates this bridge and stays untouched (additive rail); both mappings
carry their tier labels so consumers can see which vocabulary applied.
Harmonization is a post-hand-check decision for Skye (PROGRESS.md).
"""

from __future__ import annotations

import copy
import os
import re
from typing import Optional

from . import coverage

__all__ = ["level_reference", "BRIDGE_TIER_STATUS"]

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "xps")

BRIDGE_TIER_STATUS = {
    "curated": "VERIFIED",
    "machine": "CONDITIONAL",
    "legacy": "UNVERIFIED",
}

_SUBSHELL_RE = re.compile(r"^([1-7][spdf])")

_CACHE: Optional[dict] = None


def _subshell(orbital: str) -> str:
    m = _SUBSHELL_RE.match(orbital)
    return m.group(1) if m else orbital


def _join_machine_sidecar(transition: dict, sidecar: dict) -> dict:
    """By-id join of a machine transition to its provenance record.
    A machine value with no sidecar record violates the tier's own
    contract — REFUSE it, never emit a machine position naked."""
    sc = sidecar.get(transition["id"])
    if sc is None:
        raise ValueError(
            f"machine transition {transition['id']} has no provenance "
            "sidecar record — refusing to bridge it")
    return sc


def _load_bridge() -> dict:
    """Build the (element, subshell) → positions/chem-states index once.

    Loads through xps_reference.load_reference — any schema or semantic
    violation in the data files fails HERE, loudly, exactly as it would
    for the served /api/xps-reference. No partial loads.
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    import xps_reference  # repo-root module (same pattern as fitting imports)

    ref = xps_reference.load_reference(_DATA_DIR)
    sources = ref["sources"]

    def _citation(source_id: str) -> str:
        src = sources.get(source_id)
        return src["citation"] if src else source_id

    positions: dict[tuple[str, str], list[dict]] = {}
    chem: dict[tuple[str, str], list[dict]] = {}

    def _add_position(sym: str, tier: str, t: dict, *,
                      notes: str, provenance: Optional[dict]) -> None:
        source_id = t.get("source")
        if isinstance(source_id, dict):          # defensive: {id: ...} shape
            source_id = source_id.get("id", str(source_id))
        rec = {
            "orbital": t["orbital"],
            "nominal_be_ev": t["nominal_be_ev"],
            "tier": tier,
            "status": BRIDGE_TIER_STATUS[tier],
            "source_id": source_id,
            "citation": _citation(source_id) if source_id else None,
            "notes": notes,
            "provenance": provenance,
        }
        # Fields ride ONLY when the committed record carries them (Codex R1
        # review, run A MAJOR: a legacy survey line has no
        # expected_region_ev/spin_orbit — synthesizing None would be a
        # default, not a pass-through). A committed EXPLICIT null (the
        # schema forces curated/machine spin_orbit to be present, null for
        # singlets/uncurated partners) passes through as null.
        for field in ("expected_region_ev", "spin_orbit"):
            if field in t:
                rec[field] = t[field]
        positions.setdefault((sym, _subshell(t["orbital"])), []).append(rec)

    # curated tier (elements-main + lanthanides + actinides, loader-merged)
    for el in ref["elements"]:
        for fam in el["families"]:
            for t in fam["transitions"]:
                _add_position(
                    el["symbol"], "curated", t,
                    notes=el.get("curation_notes", ""),
                    provenance=None)

    # machine tier + sha256 provenance sidecar join (by transition id)
    prov_doc = ref.get("machine_provenance")
    if prov_doc is None:
        import json
        with open(os.path.join(_DATA_DIR,
                               "elements-machine.provenance.json")) as f:
            prov_doc = json.load(f)
    sidecar = {p["id"]: p for p in prov_doc["transitions"]}
    for el in ref["machine"]:
        for fam in el["families"]:
            for t in fam["transitions"]:
                sc = _join_machine_sidecar(t, sidecar)
                ns = sc["nominal_source"]
                _add_position(
                    el["symbol"], "machine", t,
                    notes=el.get("curation_notes", ""),
                    provenance={
                        "nist_reference_code": ns["nist_reference_code"],
                        "evaluated": ns["evaluated"],
                        "source_url": ns["source_url"],
                        "source_artifact": ns["source_artifact"],
                        "source_artifact_sha256":
                            ns["source_artifact_sha256"],
                        "parse_method": sc["parse_method"],
                        "dual_extraction_corroborated":
                            sc.get("dual_extraction_corroborated"),
                        "agent_cross_checked": sc.get("agent_cross_checked"),
                    })

    # legacy survey tier (verbatim embedded-dataset marker positions)
    legacy = ref.get("legacy") or {}
    for el in legacy.get("survey") or []:
        for ln in el["lines"]:
            _add_position(
                el["symbol"], "legacy",
                {"orbital": ln["orbital"], "nominal_be_ev": ln["be_ev"],
                 "source": ln.get("source", "legacy-embedded-dataset")},
                notes="legacy survey marker position "
                      f"({ln.get('be_basis', 'legacy-marker-position')}) — "
                      "verbatim embedded dataset, unverified",
                provenance=None)

    # legacy chemical states (per-state be_ev + ref + source, verbatim)
    chem_doc = legacy.get("chemical_states")
    groups = (chem_doc.get("groups", []) if isinstance(chem_doc, dict)
              else chem_doc or [])
    for grp in groups:
        key = (grp["element"], _subshell(grp["orbital"]))
        for s in grp["states"]:
            chem.setdefault(key, []).append({
                "id": s["id"],
                "state": s["state"],
                "be_ev": s["be_ev"],
                "ref": s["ref"],
                "source": s["source"],
                "tier": "legacy",
                "status": "UNVERIFIED",
                "orbital": grp["orbital"],
            })

    _CACHE = {"positions": positions, "chem": chem}
    return _CACHE


def level_reference(element: str, subshell: str) -> dict:
    """Married record for one element/subshell: derived structure +
    every sourced position/chemical-state the committed tiers hold.

    Raises KeyError for unknown elements or unoccupied subshells (the
    coverage module's structure check runs FIRST — the bridge never
    returns positions for a level that does not structurally exist).
    """
    structure = coverage.level_structure(element, subshell)
    sym = element if isinstance(element, str) else structure["level"]
    b = _load_bridge()
    return {
        "element": sym,
        "subshell": subshell,
        "structure": structure,
        "positions": copy.deepcopy(b["positions"].get((sym, subshell), [])),
        "chemical_states": copy.deepcopy(b["chem"].get((sym, subshell), [])),
    }
