#!/usr/bin/env python
"""
CWT ridge detector — SYNTHETIC calibration battery (committed generator).

Regenerates the evidence behind the `autofit.candidates` detector tunables
(CWT_PROM_Z_MIN and the scale-ladder constants) — see
docs/autofit/cwt-detector-calibration.md for the frozen numbers this
produced.  ANTI-OVERFIT RAIL: everything here is synthetic; the real
held-out scans are never touched by this script.

Sections:
1. H0 false-positive battery — 600 peakless negative spectra (flat /
   linear-drift / sigmoid-step backgrounds x counts 100..50000 x grid
   steps 0.05/0.1), per-spectrum MAX prominence-z distribution -> the
   z_min operating point and its measured per-spectrum FP rate.
2. Shoulder sensitivity map — (separation x ratio) grid at high/low
   counts, 5 noise draws each: detection rate at the frozen z_min, with
   the no-local-max class marked (the class local-max detectors cannot
   see by construction).
3. Close-doublet map — both-detected rate vs separation.
4. Broad-peak spurious-split check.

Usage:  venv/bin/python scripts/calibrate_cwt_detector.py
Output: JSONL rows to docs/autofit/inventory/cwt_calibration.jsonl
        (append-only, keyed, resumable) + a summary to stdout.
"""

from __future__ import annotations

import json
import sys
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from autofit.candidates import (  # noqa: E402
    CWT_FWHM_MAX_EV,
    CWT_FWHM_MIN_EV,
    CWT_PROM_Z_MIN,
    cwt_ridge_features,
)
from fitting import _SHAPE_FUNCS  # noqa: E402

_pv = _SHAPE_FUNCS["pseudo_voigt_gl"]
ETA = 0.30

OUT = Path(__file__).resolve().parents[1] / \
    "docs/autofit/inventory/cwt_calibration.jsonl"


def _load_done() -> set:
    done = set()
    if OUT.exists():
        with open(OUT) as fh:
            for line in fh:
                try:
                    done.add(json.loads(line)["key"])
                except Exception:
                    pass
    return done


def _emit(rec: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "a") as fh:
        fh.write(json.dumps(rec) + "\n")


def h0_battery(done: set) -> None:
    for step, npts in ((0.05, 300), (0.1, 191)):
        x = np.arange(0.0, npts * step, step)[:npts] + 190.0
        for level in (100.0, 500.0, 5000.0, 50000.0):
            for bg_kind in ("flat", "slope", "sigmoid"):
                for seed in range(25):
                    key = f"h0:{step}:{level:g}:{bg_kind}:{seed}"
                    if key in done:
                        continue
                    if bg_kind == "flat":
                        base = np.full(npts, level)
                    elif bg_kind == "slope":
                        base = level * (1.0 + 1.5 * np.arange(npts) / npts)
                    else:
                        base = level * (1.0 + 3.0 / (1.0 + np.exp(
                            -(np.arange(npts) - npts * 0.7) / (npts * 0.08))))
                    # STABLE seed derivation — Python's builtin hash() is
                    # salted per process (PYTHONHASHSEED), which would make
                    # the committed generator non-reproducible (Codex
                    # review, run B MAJOR); crc32 of the row key is exact.
                    rng = np.random.default_rng(zlib.crc32(key.encode()))
                    y = rng.poisson(base).astype(float)
                    feats = cwt_ridge_features(x, y, prom_z_min=0.0)
                    _emit({"key": key, "section": "h0", "step": step,
                           "level": level, "bg": bg_kind, "seed": seed,
                           # rounded: cross-process numpy SIMD dispatch
                           # wobbles the last ulp (the known LACX-battery
                           # effect) — 4 decimals keeps regeneration
                           # byte-identical without losing evidence
                           "max_prom_z": round(max((f.prom_z for f in feats),
                                                   default=0.0), 4),
                           "n_ge_gate": sum(1 for f in feats
                                            if f.prom_z >= CWT_PROM_Z_MIN)})


def shoulder_map(done: set) -> None:
    x = np.arange(190.0, 205.0, 0.05)
    for height in (40000.0, 2000.0):
        for sep in (0.5, 0.7, 0.9, 1.1, 1.3):
            for ratio in (0.10, 0.15, 0.20, 0.30, 0.50):
                for seed in range(5):
                    key = f"sh:{height:g}:{sep}:{ratio}:{seed}"
                    if key in done:
                        continue
                    c, f = 197.0, 1.2
                    sh = c + sep * f
                    sig = (_pv(x, height, c, f, ETA)
                           + _pv(x, ratio * height, sh, f, ETA))
                    d = np.diff(sig)
                    has_max = bool(np.any(
                        (d[:-1] > 0) & (d[1:] <= 0)
                        & (np.abs(x[1:-1] - sh) < 0.45)))
                    rng = np.random.default_rng(100 + seed)
                    y = rng.poisson(np.maximum(sig + 300.0, 0)).astype(float)
                    feats = cwt_ridge_features(x, y)
                    hit = [f2 for f2 in feats
                           if abs(f2.center_be - sh) < 0.35]
                    _emit({"key": key, "section": "shoulder",
                           "height": height, "sep_xfwhm": sep,
                           "ratio": ratio, "seed": seed,
                           "composite_has_local_max": has_max,
                           "detected": bool(hit),
                           "prom_z": (round(max(f2.prom_z for f2 in hit), 4)
                                      if hit else None)})


def doublet_map(done: set) -> None:
    x = np.arange(190.0, 205.0, 0.05)
    for sep in (0.5, 0.7, 0.9, 1.1):
        for seed in range(5):
            key = f"db:{sep}:{seed}"
            if key in done:
                continue
            c1, f = 197.0, 1.2
            c2 = c1 + sep * f
            sig = (_pv(x, 20000.0, c1, f, ETA)
                   + _pv(x, 16000.0, c2, f, ETA))
            rng = np.random.default_rng(600 + seed)
            y = rng.poisson(np.maximum(sig + 300.0, 0)).astype(float)
            feats = cwt_ridge_features(x, y)
            _emit({"key": key, "section": "doublet", "sep_xfwhm": sep,
                   "seed": seed,
                   "both": (any(abs(f2.center_be - c1) < 0.3 for f2 in feats)
                            and any(abs(f2.center_be - c2) < 0.3
                                    for f2 in feats))})


def broad_peak(done: set) -> None:
    x = np.arange(190.0, 205.0, 0.05)
    for seed in range(20):
        key = f"broad:{seed}"
        if key in done:
            continue
        sig = _pv(x, 30000.0, 197.5, 3.5, ETA)
        rng = np.random.default_rng(2000 + seed)
        y = rng.poisson(np.maximum(sig + 300.0, 0)).astype(float)
        feats = cwt_ridge_features(x, y)
        _emit({"key": key, "section": "broad", "seed": seed,
               "n_offcenter": sum(1 for f2 in feats
                                  if abs(f2.center_be - 197.5) > 0.5)})


def summarize() -> None:
    rows = [json.loads(line) for line in open(OUT)]
    h0 = np.array([r["max_prom_z"] for r in rows if r["section"] == "h0"])
    print(f"\nH0 battery ({len(h0)} spectra): per-spectrum max prom_z "
          f"q95 {np.quantile(h0, 0.95):.2f}  q99 {np.quantile(h0, 0.99):.2f}"
          f"  max {h0.max():.2f}")
    for z in (6.5, 7.0, 7.5, 8.0):
        print(f"  z_min={z}: per-spectrum FP rate "
              f"{100 * float(np.mean(h0 >= z)):.2f}%")
    print(f"  FROZEN operating point: CWT_PROM_Z_MIN = {CWT_PROM_Z_MIN} "
          f"(scale ladder FWHM {CWT_FWHM_MIN_EV}-{CWT_FWHM_MAX_EV} eV)")

    print("\nShoulder map (detected/draws at frozen gate; * = NO local max):")
    sh = [r for r in rows if r["section"] == "shoulder"]
    for height in (40000.0, 2000.0):
        print(f"  height {height:g}:")
        for sep in (0.5, 0.7, 0.9, 1.1, 1.3):
            cells = []
            for ratio in (0.10, 0.15, 0.20, 0.30, 0.50):
                sub = [r for r in sh if r["height"] == height
                       and r["sep_xfwhm"] == sep and r["ratio"] == ratio]
                n = sum(r["detected"] for r in sub)
                star = "*" if sub and not sub[0]["composite_has_local_max"] \
                    else " "
                cells.append(f"r{ratio:.2f}:{n}/{len(sub)}{star}")
            print(f"    sep {sep:.1f}xFWHM  {'  '.join(cells)}")

    db = [r for r in rows if r["section"] == "doublet"]
    for sep in (0.5, 0.7, 0.9, 1.1):
        sub = [r for r in db if r["sep_xfwhm"] == sep]
        print(f"  doublet sep {sep:.1f}xFWHM: both "
              f"{sum(r['both'] for r in sub)}/{len(sub)}")

    br = [r for r in rows if r["section"] == "broad"]
    print(f"  broad-peak spurious off-center features: "
          f"{sum(r['n_offcenter'] for r in br)} across {len(br)} draws")


if __name__ == "__main__":
    done = _load_done()
    h0_battery(done)
    shoulder_map(done)
    doublet_map(done)
    broad_peak(done)
    summarize()
