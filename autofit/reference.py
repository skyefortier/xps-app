"""
Reference-fit loading for the autofit engine.

Reads the v3 ``.proj.zip`` / ``.proj.json`` project format (the same format
``templates/index.html`` saves) into plain-Python records, and reconstructs
the exact fit inputs the frontend would send to ``/api/fit``:

- corrected BE axis  = rawBE + ccShift          (``getCorrectedBE``)
- ROI slice          = corrected BE within [ui.roiMin, ui.roiMax], inclusive
                       (``getROIData``, index.html:4494)
- background indices = nearest ROI-grid index to ui.bgStart / ui.bgEnd
                       (``runFit``, index.html:6575)
- peak specs         = mirror of ``peakToBackendSpec`` (index.html:5708)

This module is read-only with respect to the app: it imports nothing from
``app.py`` and never mutates project files.
"""

from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Project loading
# ─────────────────────────────────────────────────────────────────────────────

def load_project_tabs(path: str | Path) -> list[dict]:
    """
    Return the list of raw tab dicts from a ``.proj.zip`` or ``.proj.json``.

    Zip layout (saved by ``_doSaveProject`` for >= 5 tabs): ``manifest.json``
    with ``{version: 3, spectra: [{index, filename, ...}]}`` plus one
    ``spectrum_<i>_<name>.json`` per tab.  JSON layout (< 5 tabs): a single
    object with ``tabs: [...]``.
    """
    path = Path(path)
    if path.suffix == ".zip" or path.name.endswith(".proj.zip"):
        with zipfile.ZipFile(path) as z:
            manifest = json.loads(z.read("manifest.json"))
            if manifest.get("version") != 3:
                raise ValueError(
                    f"{path.name}: unsupported project version "
                    f"{manifest.get('version')!r} (expected 3)"
                )
            tabs = []
            for entry in manifest.get("spectra", []):
                tabs.append(json.loads(z.read(entry["filename"])))
            return tabs
    data = json.loads(path.read_text())
    if not isinstance(data.get("tabs"), list):
        raise ValueError(f"{path.name}: no 'tabs' array — not a v3 project JSON")
    return data["tabs"]


# ─────────────────────────────────────────────────────────────────────────────
# peakToBackendSpec mirror (index.html:5708)
# ─────────────────────────────────────────────────────────────────────────────

def _finite(v: Any) -> bool:
    """JS Number.isFinite: true only for finite numbers (not None/str/bool)."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and np.isfinite(v)


def peak_to_backend_spec(p: dict, all_peaks: list[dict]) -> dict:
    """
    Python mirror of the frontend's ``peakToBackendSpec``.

    ``all_peaks`` is needed for the linked-peak branch (JS resolves the
    parent via ``getPeak(p.linked)`` and silently drops the constraint when
    the parent is missing).
    """
    spec: dict[str, Any] = {
        "id": str(p["id"]),
        "name": p.get("name"),
        "center": p["center"],
        "amplitude": p["amplitude"],
        "fwhm": p["fwhm"],
        "amplitude_min": 0,
        "fix_center": bool(p.get("fixCenter")),
        "fix_fwhm": bool(p.get("fixFwhm")),
        "fix_amplitude": bool(p.get("fixAmplitude")),
        "fix_gl_ratio": bool(p.get("fixGlMix")),
    }
    shape = p.get("shape")
    if shape == "Gaussian":
        spec["shape"] = "gaussian"
    elif shape == "Lorentzian":
        spec["shape"] = "lorentzian"
    elif shape == "Voigt":
        spec["shape"] = "pseudo_voigt_gl"
        spec["gl_ratio"] = 0.3
    elif shape == "GL":
        spec["shape"] = "pseudo_voigt_gl"
        spec["gl_ratio"] = p["glMix"] / 100.0
    elif shape == "asym-GL":
        spec["shape"] = "asymmetric_gl"
        spec["gl_ratio"] = (p.get("glMix") or 50) / 100.0
        spec["asymmetry"] = p.get("asymmetry") or 0
        spec["fix_asymmetry"] = bool(p.get("fixAsymmetry"))
        if _finite(p.get("_afAsymMin")):
            spec["asymmetry_min"] = p["_afAsymMin"]
        if _finite(p.get("_afAsymMax")):
            spec["asymmetry_max"] = p["_afAsymMax"]
    elif shape == "DS":
        spec["shape"] = "doniach_sunjic"
        spec["alpha"] = p.get("dsAlpha") or 0.1
        spec["gamma_asym"] = p.get("dsGamma") or 0.0
        spec["fix_alpha"] = bool(p.get("fixDsAlpha"))
        spec["fix_gamma_asym"] = bool(p.get("fixDsGamma"))
    elif shape == "DSG_LA":
        spec["shape"] = "ds_g"
        spec["alpha"] = p["laAlpha"] if _finite(p.get("laAlpha")) else 0.10
        spec["beta"] = p["laBeta"] if _finite(p.get("laBeta")) else 0.3
        spec["m_gauss"] = p["laM"] if _finite(p.get("laM")) else 0.4
        spec["fix_alpha"] = bool(p.get("fixLaAlpha"))
        spec["fix_beta"] = bool(p.get("fixLaBeta"))
        spec["fix_m_gauss"] = bool(p.get("fixLaM"))
    elif shape == "LACX":
        spec["shape"] = "la_casaxps"
        spec["alpha"] = p["caAlpha"] if _finite(p.get("caAlpha")) else 1.0
        spec["beta"] = p["caBeta"] if _finite(p.get("caBeta")) else 1.0
        spec["m"] = p["caM"] if _finite(p.get("caM")) else 50.0
        spec["fix_alpha"] = bool(p.get("fixCaAlpha"))
        spec["fix_beta"] = bool(p.get("fixCaBeta"))
        spec["fix_m"] = bool(p.get("fixCaM"))
    else:
        spec["shape"] = "gaussian"

    if p.get("linked"):
        parent = next((q for q in all_peaks if q.get("id") == p["linked"]), None)
        if parent is not None:
            spec["constrain_to"] = str(p["linked"])
            spec["splitting"] = p.get("linkOffset")
            spec["area_ratio"] = p.get("linkRatio")
            spec["fix_fwhm"] = True
    return spec


# ─────────────────────────────────────────────────────────────────────────────
# ReferenceFit — one saved, fitted spectrum tab
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ReferenceFit:
    """A saved spectrum tab with a fit, plus reconstructed fit inputs."""

    project: str                 # source project filename
    tab_file: str                # spectrum_*.json name (or index for .proj.json)
    name: str
    raw_be: np.ndarray
    raw_intensity: np.ndarray
    cc_shift: float
    peaks: list[dict]
    fit_result: dict
    ui: dict = field(default_factory=dict)

    # ── frontend-semantics reconstructions ──────────────────────────────────

    @property
    def corrected_be(self) -> np.ndarray:
        # getCorrectedBE (index.html:4486): corrected = rawBE − ccShift
        # (ccShift = observed − literature, so the applied shift is −ccShift).
        return self.raw_be - self.cc_shift

    def _roi_bounds(self) -> tuple[float, float]:
        lo = _parse_float(self.ui.get("roiMin"), -np.inf)
        hi = _parse_float(self.ui.get("roiMax"), np.inf)
        return lo, hi

    @property
    def roi_mask(self) -> np.ndarray:
        lo, hi = self._roi_bounds()
        c = self.corrected_be
        return (c >= lo) & (c <= hi)

    @property
    def roi_be(self) -> np.ndarray:
        return self.corrected_be[self.roi_mask]

    @property
    def roi_intensity(self) -> np.ndarray:
        return self.raw_intensity[self.roi_mask]

    def bg_indices(self) -> tuple[int, int]:
        """Nearest ROI-grid indices to ui.bgStart / ui.bgEnd (index.html:6575)."""
        be = self.roi_be
        bg_start = _parse_float(self.ui.get("bgStart"), be[0] if len(be) else 0.0)
        bg_end = _parse_float(self.ui.get("bgEnd"), be[-1] if len(be) else 0.0)
        i_start = int(np.argmin(np.abs(be - bg_start)))
        i_end = int(np.argmin(np.abs(be - bg_end)))
        return i_start, i_end

    @property
    def bg_method(self) -> str:
        return self.ui.get("bgType") or "shirley"

    @property
    def endpoint_avg(self) -> int:
        try:
            return max(1, int(self.ui.get("endpointAvg", 1)))
        except (TypeError, ValueError):
            return 1

    def backend_peak_specs(self) -> list[dict]:
        return [peak_to_backend_spec(p, self.peaks) for p in self.peaks]

    @property
    def region_midpoint(self) -> Optional[float]:
        lo, hi = self._roi_bounds()
        if np.isfinite(lo) and np.isfinite(hi):
            return 0.5 * (lo + hi)
        be = self.corrected_be
        return 0.5 * (float(be.min()) + float(be.max())) if len(be) else None

    def region_guess(self) -> str:
        """Coarse region label from the ROI midpoint (mirrors isC1sTab logic)."""
        mid = self.region_midpoint
        if mid is None:
            return "unknown"
        for label, lo, hi in _REGION_WINDOWS:
            if lo <= mid <= hi:
                return label
        return "unknown"


# Coarse corrected-BE midpoint windows for region labeling of the reference
# data.  These are bookkeeping bins for test selection only — NOT physics
# constants (the engine's physical BE windows live in the region modules and
# are lit-cited there).
_REGION_WINDOWS = [
    ("C 1s", 270.0, 315.0),      # matches isC1sTab (index.html:6548)
    ("Cl 2p", 190.0, 210.0),
    ("B 1s", 178.0, 190.0),
    ("N 1s", 390.0, 410.0),      # overlaps U 4f — U 4f checked first below
    ("U 4f", 370.0, 415.0),
]


def _parse_float(v: Any, default: float) -> float:
    try:
        f = float(v)
        return f if np.isfinite(f) else default
    except (TypeError, ValueError):
        return default


def load_reference_fits(path: str | Path) -> list[ReferenceFit]:
    """All fitted spectrum tabs (>=1 peak, has rawBE + fitResult) in a project."""
    path = Path(path)
    out: list[ReferenceFit] = []
    for i, t in enumerate(load_project_tabs(path)):
        if t.get("isStack"):
            continue
        raw_be = t.get("rawBE") or []
        peaks = t.get("peaks") or []
        fr = t.get("fitResult")
        if not raw_be or not peaks or not fr:
            continue
        out.append(ReferenceFit(
            project=path.name,
            tab_file=f"tab_{i}" if not t.get("name") else t["name"],
            name=t.get("name", f"tab_{i}"),
            raw_be=np.asarray(raw_be, dtype=float),
            raw_intensity=np.asarray(t.get("rawIntensity"), dtype=float),
            cc_shift=float(t.get("ccShift") or 0.0),
            peaks=peaks,
            fit_result=fr,
            ui=t.get("ui") or {},
        ))
    return out
