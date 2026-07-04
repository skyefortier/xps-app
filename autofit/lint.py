"""
Quantification lint (spec §8) — FLAG-ONLY checks on saved-project peak
metadata consumed for quantification.  The lint NEVER alters source data.

Adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #1/#2):
the labeled set carries confirmed-erroneous region-mismatched ``_rsfKey``
tags — ``Zr 3d`` on the B4C-UCl4 B 1s B-B/B-C peaks and ``K 2p`` on every
C 1s π→π* satellite (no Zr or K in any sample; atomic-% computed from
those tabs used the wrong RSF).  This lint detects the PATTERN.  Re-tagging
is a human action; the engine only flags (ruling: "Do NOT alter the source
data files").

Rule, per peak whose ``_rsfKey`` names a region other than the tab's:

- POSITIONALLY JUSTIFIED → ``info`` note, NOT a flag.  Justification means
  the peak center (corrected frame — saved peak centers are corrected-frame
  values) lies inside the named region's territory, established from either
  (a) the named region's engine module diagnostic windows (lit-cited /
  flagged constants — e.g. the ``N 1s`` tag on the ~397 eV U 4f satellite
  sits inside the N 1s window: LEAVE per adjudication), or
  (b) a machine-tier ``data/xps/fit-physics.json`` BE window for that
  element+orbital, widened by ``FIT_PHYSICS_TOL_EV`` (chemical-shift
  allowance — an UNVERIFIED bookkeeping tolerance for flagging only, not
  physics).
- Otherwise → ``flag`` (level ``region_mismatch``), with all evidence
  gathered: tab region, peak BE, nearest known territory and distance
  where one exists, or the fact that no territory is known to the engine.

Conservatism: if the TAB region itself cannot be labeled (coarse ROI-
midpoint bins in ``reference._REGION_WINDOWS``), a foreign key is flagged
only when the key HAS a known territory that clearly excludes the peak —
an unknown tab plus an unknown key is skipped, not guessed at.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

from .reference import ReferenceFit
from .regions import get_region_module, registered_regions

# Chemical-shift allowance around machine-tier fit-physics windows
# (observed-reference-range, typically narrow).  UNVERIFIED bookkeeping
# tolerance: sets only how far outside a known territory a tag must sit
# before it is flagged — never used as a physics constant.
FIT_PHYSICS_TOL_EV = 3.0

_FIT_PHYSICS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "xps", "fit-physics.json")

_KEY_RE = re.compile(r"^([A-Z][a-z]?)\s*[- ]\s*(\d[spdf])")


def _parse_rsf_key(key: str) -> Optional[tuple[str, str]]:
    """'K 2p' / 'Zr 3d' / 'N 1s' → (element, orbital); None if unparseable."""
    m = _KEY_RE.match(key.strip())
    return (m.group(1), m.group(2)) if m else None


def _region_module_windows(region: str) -> list[tuple[float, float]]:
    if region not in registered_regions():
        return []
    return list(get_region_module(region).diagnostic_windows().values())


def _fit_physics_windows(element: str, orbital: str) -> list[tuple[float, float]]:
    """Machine-tier BE windows for an element+orbital family (e.g. Zr 3d →
    every Zr-3d* entry's be_window_ev).  Empty when the DB has none."""
    db = _load_fit_physics()
    out = []
    for key, entry in db.items():
        if entry.get("element") != element:
            continue
        suffix = key.split("-", 1)[-1] if "-" in key else ""
        if not suffix.startswith(orbital):
            continue
        w = entry.get("be_window_ev") or {}
        if "min" in w and "max" in w:
            out.append((float(w["min"]), float(w["max"])))
    return out


_FIT_PHYSICS_CACHE: Optional[dict] = None


def _load_fit_physics() -> dict:
    global _FIT_PHYSICS_CACHE
    if _FIT_PHYSICS_CACHE is None:
        try:
            with open(_FIT_PHYSICS_PATH) as f:
                _FIT_PHYSICS_CACHE = json.load(f).get("entries", {})
        except (OSError, ValueError):
            _FIT_PHYSICS_CACHE = {}
    return _FIT_PHYSICS_CACHE


def _territory_evidence(rsf_region: str, element: str, orbital: str,
                        center: float) -> dict[str, Any]:
    """Gather every known territory for the key + the peak's relation to it."""
    module_windows = _region_module_windows(rsf_region)
    db_windows = _fit_physics_windows(element, orbital)
    inside_module = any(lo <= center <= hi for lo, hi in module_windows)
    inside_db = any(lo - FIT_PHYSICS_TOL_EV <= center <= hi + FIT_PHYSICS_TOL_EV
                    for lo, hi in db_windows)
    dist = None
    all_windows = module_windows + db_windows
    if all_windows:
        dist = min(max(lo - center, center - hi, 0.0) for lo, hi in all_windows)
    return {
        "module_windows": module_windows,
        "fit_physics_windows": db_windows,
        "inside_module_window": inside_module,
        "inside_fit_physics_window_with_tol": inside_db,
        "distance_to_nearest_territory_ev": dist,
        "territory_known": bool(all_windows),
    }


def lint_rsf_tags(rf: ReferenceFit) -> list[dict[str, Any]]:
    """
    Lint one saved tab's peaks for region-mismatched ``_rsfKey`` tags.

    Returns findings ``[{level, peak_name, rsf_key, tab_region, center_ev,
    reason, evidence}]`` with ``level`` ∈ {"flag", "info"}.  Flag-only:
    the input is never modified.
    """
    tab_region = rf.region_guess()
    findings: list[dict[str, Any]] = []
    for p in rf.peaks:
        key = p.get("_rsfKey")
        if not key or not isinstance(key, str):
            continue
        rsf_region = key.strip()
        if rsf_region == tab_region:
            continue
        parsed = _parse_rsf_key(rsf_region)
        center = p.get("center")
        if parsed is None or not isinstance(center, (int, float)):
            continue
        element, orbital = parsed
        ev = _territory_evidence(rsf_region, element, orbital, float(center))

        base = {
            "peak_name": p.get("name"),
            "rsf_key": rsf_region,
            "tab_region": tab_region,
            "center_ev": float(center),
            "evidence": ev,
        }
        if ev["inside_module_window"] or ev["inside_fit_physics_window_with_tol"]:
            findings.append({
                **base, "level": "info",
                "reason": (f"_rsfKey {rsf_region!r} differs from the tab "
                           f"region {tab_region!r} but the peak sits inside "
                           f"{rsf_region!r} territory — positionally "
                           "justified (possibly deliberate cross-region "
                           "tag); not flagged"),
            })
            continue
        if tab_region == "unknown" and not ev["territory_known"]:
            # unknown tab + unknown key territory: nothing to judge against
            continue
        if ev["territory_known"]:
            reason = (f"region-mismatched _rsfKey: {rsf_region!r} on a "
                      f"{tab_region!r} tab, peak at {center:.2f} eV is "
                      f"{ev['distance_to_nearest_territory_ev']:.2f} eV "
                      f"outside every known {rsf_region!r} territory "
                      f"(±{FIT_PHYSICS_TOL_EV} eV allowance on DB windows)")
        else:
            reason = (f"region-mismatched _rsfKey: {rsf_region!r} on a "
                      f"{tab_region!r} tab, peak at {center:.2f} eV; no "
                      f"{rsf_region!r} territory known to the engine "
                      "(no region module, no fit-physics entry) — no "
                      "positional justification found")
        findings.append({**base, "level": "flag",
                         "category": "region_mismatch", "reason": reason})
    return findings


def lint_project(reference_fits: list[ReferenceFit]) -> list[dict[str, Any]]:
    """Lint a whole project's tabs; findings carry tab identity."""
    out: list[dict[str, Any]] = []
    for rf in reference_fits:
        for f in lint_rsf_tags(rf):
            out.append({**f, "project": rf.project, "tab": rf.name})
    return out
