"""
Tiered reference-DB accessor (``data/xps/fit-physics.json``) — run-brief
item 4: wire the DB into the engine.

EXPOSURE ONLY at this stage, by design: the region modules KEEP their own
lit-cited constants (migration is deferred until the human review of the
machine-tier values — Monday-handoff item 4; "no invention" rail), and
``grammar.resolve()`` attaches the DB's matching entries plus mechanical
cross-checks to ``grammar.provenance`` — which already flows into every
fit's ``analysis`` namespace.  Net effect: every result shows what the
tiered DB says NEXT TO what the grammar actually used, and any numeric
disagreement between them is a visible note, never a silent divergence.
Candidate construction is untouched (parity preserved by construction;
pinned in tests).

Status mapping into the provenance vocabulary {VERIFIED, CONDITIONAL,
UNVERIFIED}: machine-tier values are UNVERIFIED (pending the hand-
verification the handoff requires); curated-tier values are CONDITIONAL
(sourced conventions/derived values, not verified on this lab's samples).
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "xps",
                        "fit-physics.json")
_CACHE: Optional[dict] = None

_TIER_STATUS = {"machine": "UNVERIFIED", "curated": "CONDITIONAL"}

_REGION_RE = re.compile(r"^([A-Z][a-z]?)\s+(\d[spdf])$")


def load_entries() -> dict:
    global _CACHE
    if _CACHE is None:
        try:
            with open(_DB_PATH) as f:
                _CACHE = json.load(f).get("entries", {})
        except (OSError, ValueError):
            _CACHE = {}
    return _CACHE


def entries_for_region(region: str) -> dict[str, dict]:
    """Region label ('Cl 2p') → the DB's matching element+orbital entries
    (both spin-orbit lines where they exist).  Empty when the DB has none
    (e.g. B 1s / N 1s today) — absence is exposed, not papered over."""
    m = _REGION_RE.match(region.strip())
    if not m:
        return {}
    element, orbital = m.group(1), m.group(2)
    return {k: v for k, v in load_entries().items()
            if v.get("element") == element
            and k.split("-", 1)[-1].startswith(orbital)}


def _value_matches(module_value: Any, db_value: float,
                   tol: float = 1e-6) -> Optional[bool]:
    """Scalar module constant → exact-ish compare; [lo, hi] range →
    containment; anything else → None (not comparable)."""
    try:
        if isinstance(module_value, (int, float)):
            return abs(float(module_value) - db_value) <= max(
                tol, 1e-3 * abs(db_value))
        if (isinstance(module_value, (list, tuple))
                and len(module_value) == 2
                and all(isinstance(v, (int, float)) for v in module_value)):
            lo, hi = float(module_value[0]), float(module_value[1])
            return lo - tol <= db_value <= hi + tol
    except (TypeError, ValueError):
        pass
    return None


def provenance_entries(
    region: str, module_provenance: list[dict],
    slot_facts: Optional[dict] = None,
) -> tuple[list[dict], list[str]]:
    """
    (extra provenance records, resolution notes) for one region:

    - one record per DB entry (nominal BE, window, spin-orbit block) with
      the tier mapped into the provenance status vocabulary;
    - mechanical cross-checks of the DB's SPIN-ORBIT SPLITTING and
      STATISTICAL AREA RATIO ONLY (nominal-BE/window fields are exposed
      but not auto-compared — Codex analyze review: do not imply broader
      coverage), each against BOTH the module's provenance records AND —
      when ``slot_facts`` is supplied by resolve() — the RESOLVED
      candidate slots' actual constants (provenance strings can go stale
      relative to the slots that build candidates).  Agreement is recorded
      per record; DISAGREEMENT is additionally surfaced as a resolution
      note.
    """
    entries = entries_for_region(region)
    records: list[dict] = []
    notes: list[str] = []
    if not entries:
        records.append({
            "constant": "fit_physics_db",
            "value": None,
            "status": "UNVERIFIED",
            "source": f"data/xps/fit-physics.json has NO entries for "
                      f"{region!r} — grammar constants stand alone here",
        })
        return records, notes

    mod_by_name = {p.get("constant", ""): p for p in module_provenance}

    def _module_value(substr: str, exclude: str = "relaxation"):
        for name, p in mod_by_name.items():
            if substr in name and exclude not in name:
                return name, p.get("value")
        return None, None

    for key, e in sorted(entries.items()):
        tier = e.get("reference_tier", "machine")
        status = _TIER_STATUS.get(tier, "UNVERIFIED")
        w = e.get("be_window_ev") or {}
        records.append({
            "constant": f"fit_physics:{key}",
            "value": {
                "nominal_be_ev": (e.get("nominal_be_ev") or {}).get("value"),
                "be_window_ev": [w.get("min"), w.get("max")],
                "spin_orbit": e.get("spin_orbit"),
                "tier": tier,
            },
            "status": status,
            "source": f"data/xps/fit-physics.json [{tier} tier] — "
                      f"{(e.get('nominal_be_ev') or {}).get('source', '?')}"
                      + ("; machine-tier values pend hand-verification"
                         if tier == "machine" else ""),
        })

        so = e.get("spin_orbit") or {}
        for db_field, mod_substr in (("splitting_ev", "splitting"),
                                     ("area_ratio", "ratio")):
            db_val = so.get(db_field)
            if not isinstance(db_val, (int, float)):
                continue
            if db_field == "area_ratio" and db_val > 1.0:
                # DB stores each line's ratio-to-partner; compare the <1 one
                continue
            mod_name, mod_val = _module_value(mod_substr)
            if mod_name is None:
                continue
            ok = _value_matches(mod_val, float(db_val))
            if ok is None:
                continue
            records.append({
                "constant": f"fit_physics_cross_check:{key}:{db_field}",
                "value": {"db": db_val, "module": mod_val,
                          "module_constant": mod_name,
                          "agrees": bool(ok)},
                "status": "UNVERIFIED",
                "source": "mechanical DB-vs-grammar comparison "
                          "(exposure only; no behavior change)",
            })
            if not ok:
                notes.append(
                    f"fit-physics DISAGREEMENT {key}.{db_field}: DB "
                    f"{db_val} vs grammar {mod_name}={mod_val} — grammar "
                    "value stands (migration pends human review)")

            # RESOLVED-SLOT check: the constants actually building the
            # candidates, not just the provenance prose
            if slot_facts:
                if db_field == "splitting_ev":
                    facts = slot_facts.get("splitting") or []
                    ok_s = (any(lo - 1e-6 <= db_val <= hi + 1e-6
                                for lo, hi in facts) if facts else None)
                else:
                    facts = slot_facts.get("ratio") or []
                    ok_s = (any(abs(f - db_val) <= max(1e-6, 1e-3 * db_val)
                                for f in facts) if facts else None)
                if ok_s is not None:
                    records.append({
                        "constant": f"fit_physics_slot_check:{key}:{db_field}",
                        "value": {"db": db_val, "resolved_slots": facts,
                                  "agrees": bool(ok_s)},
                        "status": "UNVERIFIED",
                        "source": "mechanical DB-vs-RESOLVED-SLOT "
                                  "comparison (exposure only)",
                    })
                    if not ok_s:
                        notes.append(
                            f"fit-physics DISAGREEMENT (resolved slots) "
                            f"{key}.{db_field}: DB {db_val} vs slot "
                            f"constants {facts} — grammar value stands "
                            "(migration pends human review)")
    return records, notes
