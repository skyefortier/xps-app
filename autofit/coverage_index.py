"""
autofit/coverage_index.py — the Find-Peaks region-selector coverage index
(2026-07-11, Find Peaks UI improvements, unit 3).

Enumerates every SELECTABLE region across the Phase D coverage framework
(Z=1..96 x occupied subshells) and classifies each into the FITTING-
COVERAGE tier the Find Peaks UI shows.  This is a DIFFERENT vocabulary
than data/xps's own curated/machine/legacy REFERENCE-DATA tier system
(exposed elsewhere via ``RefCore.tierColor``/``tierNote`` for the
Reference/Identify palette) — that system grades an ENERGY VALUE's
provenance; this one grades whether a REGION can be FIT with cited
grammar at all:

- ``curated``        a deep grammar module is registered
                     (``autofit/regions/*.py``) — cited fitting windows/
                     widths; Find Peaks uses a REAL grammar.  Today:
                     B 1s, C 1s, Cl 2p, N 1s, U 4f (unchanged).
- ``machine``        no deep module, but >=1 sourced position exists in
                     data/xps (via ``reference_bridge``) — CONDITIONAL,
                     structural-fallback fitting only (the detection-
                     driven candidate family, ``autofit.candidates.
                     build_detection_candidate``); never presented as
                     cited grammar.
- ``structure_only`` no deep module, no sourced position at all — pure
                     derived quantum bookkeeping (occupied subshells,
                     doublet/singlet structure); structural-fallback
                     fitting with no position to anchor a ROI on.

HONESTY RAIL (goal-mandated): ``curated`` here is reserved EXCLUSIVELY for
a registered deep grammar module — a region can be data/xps tier=
'curated' there and still show as 'machine' here, because THIS label
answers "does Find Peaks have cited fitting grammar for this region", not
"is the underlying energy value well-sourced". A structural-fallback
region must never be shown as if it had cited grammar.

Nothing here invents an energy — every non-None ROI/position value is
read straight from ``autofit.coverage``/``autofit.reference_bridge``,
which enforce the anti-confabulation contract already.
"""

from __future__ import annotations

import copy
from typing import Optional

from . import coverage, reference_bridge
from .regions import get_region_module, registered_regions

__all__ = ["region_coverage_index"]

# Practical, UI-only fallback margin around a bare nominal position when the
# source didn't record an explicit expected_region_ev (wide enough for a
# spin-orbit partner + a satellite) — NEVER presented as literature-cited.
_NOMINAL_ROI_MARGIN_EV = 12.0

# Same convention for a curated region's window union: the cookbook's own
# diagnostic windows are tight (e.g. C 1s ~284-292 eV); padding leaves room
# for out-of-grammar features the detection layer (Stage 2) can still find
# (CLAUDE.md's documented typical windows are similarly wider than the raw
# window union). UI-only, not a cited constant.
_CURATED_ROI_PADDING_EV = 6.0

_INDEX_CACHE: Optional[list[dict]] = None
_INDEX_CACHE_KEY: Optional[frozenset] = None


def _curated_roi(region: str) -> Optional[dict]:
    windows = get_region_module(region).diagnostic_windows()
    if not windows:
        return None
    lo = min(w[0] for w in windows.values()) - _CURATED_ROI_PADDING_EV
    hi = max(w[1] for w in windows.values()) + _CURATED_ROI_PADDING_EV
    return {"be_min": round(lo, 1), "be_max": round(hi, 1),
            "basis": "grammar diagnostic windows ± practical margin"}


def _sourced_roi(positions: list[dict]) -> Optional[dict]:
    """A practical starting BE window from the bridge's sourced
    positions — UI convenience only, never asserted as physics. Prefers a
    committed ``expected_region_ev`` (the source's own recorded span, e.g.
    a reduced-to-oxidized chemical-state range); falls back to a generic
    margin around the nominal position(s) otherwise."""
    if not positions:
        return None
    regions = [p["expected_region_ev"] for p in positions
              if p.get("expected_region_ev")]
    if regions:
        lo = min(r["min"] for r in regions)
        hi = max(r["max"] for r in regions)
        return {"be_min": round(lo, 1), "be_max": round(hi, 1),
                "basis": "expected_region_ev (source-recorded span)"}
    noms = [p["nominal_be_ev"] for p in positions
           if p.get("nominal_be_ev") is not None]
    if not noms:
        return None
    return {"be_min": round(min(noms) - _NOMINAL_ROI_MARGIN_EV, 1),
            "be_max": round(max(noms) + _NOMINAL_ROI_MARGIN_EV, 1),
            "basis": "nominal position ± practical margin (not "
                    "literature-cited)"}


def region_coverage_index() -> list[dict]:
    """Every selectable ``'<Element> <level>'`` region across Z=1..96,
    tiered.  Cached by the CURRENT set of registered grammar modules
    (pure/derived data — in production, region modules self-register at
    import time and never change again, so this is a one-time
    computation there; the keyed cache also makes the function correct
    if a caller ever registers a module after the first call — e.g. a
    test suite that registers a synthetic region module for an unrelated
    test — rather than silently freezing a stale snapshot).  Each entry:
    ``{region, symbol, z, name, level, tier, note, roi}`` — ``roi`` is
    ``None`` when nothing (cited or sourced) is available to anchor a
    starting window on (honest: ``structure_only`` always has ``roi:
    None``).
    """
    global _INDEX_CACHE, _INDEX_CACHE_KEY
    curated = frozenset(registered_regions())
    if _INDEX_CACHE is not None and _INDEX_CACHE_KEY == curated:
        return copy.deepcopy(_INDEX_CACHE)   # roi is a nested dict — deep copy per call
    out: list[dict] = []
    for sym in coverage.PERIODIC_TABLE:
        st = coverage.element_structure(sym)
        for lv in st["levels"]:
            region = f"{sym} {lv['level']}"
            if region in curated:
                out.append({
                    "region": region, "symbol": sym, "z": st["z"],
                    "name": st["name"], "level": lv["level"],
                    "tier": "curated",
                    "note": "Cited fitting grammar (lit-anchored "
                            "windows/widths).",
                    "roi": _curated_roi(region),
                })
                continue
            bridged = reference_bridge.level_reference(sym, lv["level"])
            positions = bridged["positions"]
            if positions:
                statuses = sorted({p["status"] for p in positions})
                out.append({
                    "region": region, "symbol": sym, "z": st["z"],
                    "name": st["name"], "level": lv["level"],
                    "tier": "machine",
                    "note": ("Sourced reference position(s), NOT a cited "
                             "fitting grammar — structural-fallback "
                             f"fitting (status: {', '.join(statuses)})."),
                    "roi": _sourced_roi(positions),
                })
            else:
                out.append({
                    "region": region, "symbol": sym, "z": st["z"],
                    "name": st["name"], "level": lv["level"],
                    "tier": "structure_only",
                    "note": "No cited or sourced position at all — "
                            "structure-only fallback; set the BE window "
                            "manually.",
                    "roi": None,
                })

    # Defensive completeness: a registered module OUTSIDE the classic
    # Z=1..96 element+level enumeration (e.g. a synthetic test region) is
    # never silently dropped — every entry in ``curated`` must appear
    # somewhere in the index (registered ⇒ 'curated', unconditionally).
    seen = {e["region"] for e in out}
    for region in sorted(curated - seen):
        parsed = coverage.parse_region(region)
        sym, level = parsed if parsed else (None, None)
        out.append({
            "region": region, "symbol": sym,
            "z": (coverage.PERIODIC_TABLE[sym][0] if sym in coverage.PERIODIC_TABLE
                 else None),
            "name": (coverage.PERIODIC_TABLE[sym][1] if sym in coverage.PERIODIC_TABLE
                    else None),
            "level": level, "tier": "curated",
            "note": "Cited fitting grammar (lit-anchored windows/widths).",
            "roi": _curated_roi(region),
        })

    out.sort(key=lambda r: (r["z"] if r["z"] is not None else 0, r["level"] or ""))
    _INDEX_CACHE = out
    _INDEX_CACHE_KEY = curated
    return copy.deepcopy(out)
