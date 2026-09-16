#!/usr/bin/env python3
"""Find saved XPS Fitting Studio files whose "fit" came from the in-page
local optimiser — including every Batch Fit result produced before
2026-09-15, which was the un-fitted starting model (unit A0; proof in
docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md).

Usage:
    python scripts/scan_batch_fit_signature.py FILE_OR_DIR [FILE_OR_DIR ...]
    python scripts/scan_batch_fit_signature.py ~/xps-projects --json report.json

Scans .proj.zip, .proj.json and .spec.json (recursively for directories),
prints one line per flagged tab and a summary, and exits 1 when anything
was flagged (0 when clean) so it can be used in scripts.

What it looks for — a saved tab or spectrum that has a fit result and:

  1. UNWEIGHTED statistics (the decisive signature). The local optimiser
     stores chiReduced = sum(r^2)/(n-k) and rmse = sqrt(sum(r^2)/n), so
     chiReduced / rmse^2 = n/(n-k), i.e. about 1. The server (lmfit) stores
     a counting-noise-WEIGHTED reduced chi-square, so the same ratio is
     about 1/<counts>: 1e-2 to 1e-6 on real spectra. A ratio above 0.1 is
     a local-optimiser result; between 0.01 and 0.1 it is reported as
     "possible" (very low-count data can blur the boundary).
  2. Corroboration: chiReduced far above any plausible weighted value
     (> 1000), and, in a project, another tab carrying the IDENTICAL
     centre/width set — a Batch Fit clone that was never fitted, with the
     tab it was cloned from named.

Batch Fit results made after the fix are still local-optimiser results and
will still be flagged by rule 1 (they are honest fits now, but carry no
uncertainties); use the "identical model" corroboration and the date of
the file to tell the two apart, or simply re-run Run Fit on flagged tabs.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

RATIO_FLAG = 0.1        # chiReduced / rmse^2 above this: unweighted (local) statistics
RATIO_POSSIBLE = 0.01   # between this and RATIO_FLAG: possible, check the file
CHI_HUGE = 1000.0       # weighted chi^2_r never gets here on real data
CENTER_TOL = 1e-9       # "identical" centre/width = bit-for-bit copy


def _load_tabs(path: Path) -> list[dict]:
    """Return [(tab_name, tab_dict)] for a .proj.zip / .proj.json / .spec.json."""
    name = path.name
    if name.endswith(".proj.zip"):
        with zipfile.ZipFile(path) as z:
            manifest = json.loads(z.read("manifest.json"))
            return [json.loads(z.read(e["filename"])) for e in manifest.get("spectra", [])]
    data = json.loads(path.read_text())
    if name.endswith(".spec.json"):
        # single spectrum: statistics block plays the role of fitResult
        tab = dict(data)
        tab["name"] = data.get("spectrumName") or path.stem
        tab["fitResult"] = data.get("statistics") or None
        return [tab]
    if isinstance(data.get("tabs"), list):
        return data["tabs"]
    raise ValueError(f"{name}: not a v3 project or spectrum file")


def _model_key(peaks: list[dict]):
    return tuple(sorted((round(float(p.get("center", 0.0)), 9), round(float(p.get("fwhm", 0.0)), 9))
                        for p in peaks if isinstance(p, dict)))


def _finite(v) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f and f not in (float("inf"), float("-inf")) else None


def scan_tabs(tabs: list[dict]) -> list[dict]:
    """Return one hit dict per flagged tab: {tab, level, ratio, chiReduced, reasons}."""
    keys = {}
    for t in tabs:
        if t.get("isStack") or not t.get("peaks"):
            continue
        keys.setdefault(_model_key(t["peaks"]), []).append(t.get("name", "?"))
    hits = []
    for t in tabs:
        if t.get("isStack"):
            continue
        fr = t.get("fitResult")
        peaks = t.get("peaks") or []
        if not fr or not peaks:
            continue
        chi_r = _finite(fr.get("chiReduced"))
        rmse = _finite(fr.get("rmse"))
        reasons, level = [], None
        ratio = None
        if chi_r is not None and rmse is not None and rmse > 0:
            ratio = chi_r / (rmse * rmse)
            if ratio >= RATIO_FLAG:
                level = "flagged"
                reasons.append(f"unweighted statistics: chiReduced/rmse^2 = {ratio:.3g} (local optimiser; a server fit gives ~1/<counts>)")
            elif ratio >= RATIO_POSSIBLE:
                level = "possible"
                reasons.append(f"chiReduced/rmse^2 = {ratio:.3g} is between the server and local ranges; inspect the file")
        if chi_r is not None and chi_r > CHI_HUGE:
            reasons.append(f"chiReduced = {chi_r:.4g} is far above any weighted value")
            level = level or "flagged"
        # Corroboration only: the tab a Batch Fit clone was copied FROM has
        # the same centre/width set but carries a genuine (weighted) result.
        if level:
            twins = [n for n in keys.get(_model_key(peaks), []) if n != t.get("name", "?")]
            if twins:
                reasons.append(f"identical centre/width set to tab(s) {', '.join(twins)} — a Batch Fit copy")
        if level:
            hits.append({"tab": t.get("name", "?"), "level": level, "ratio": ratio, "chiReduced": chi_r, "reasons": reasons})
    return hits


def scan_path(path: Path) -> list[dict]:
    hits = scan_tabs(_load_tabs(Path(path)))
    for h in hits:
        h["file"] = str(path)
    return hits


def iter_files(paths):
    for p in paths:
        p = Path(p)
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file() and (f.name.endswith(".proj.zip") or f.name.endswith(".proj.json") or f.name.endswith(".spec.json")):
                    yield f
        elif p.is_file():
            yield p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("paths", nargs="+", help="files or directories to scan")
    ap.add_argument("--json", help="also write the full report to this JSON file")
    args = ap.parse_args(argv)
    report, n_files, n_flagged, n_possible, n_errors = [], 0, 0, 0, 0
    for f in iter_files(args.paths):
        n_files += 1
        try:
            hits = scan_path(f)
        except Exception as exc:  # unreadable / not a project file
            n_errors += 1
            print(f"ERROR   {f}: {exc}")
            continue
        for h in hits:
            report.append(h)
            if h["level"] == "flagged":
                n_flagged += 1
            else:
                n_possible += 1
            print(f"{h['level'].upper():8s} {f} :: {h['tab']}")
            for r in h["reasons"]:
                print(f"           - {r}")
    print(f"\n{n_files} file(s) scanned: {n_flagged} flagged, {n_possible} possible, {n_errors} unreadable.")
    if n_flagged or n_possible:
        print("Flagged tabs hold a local-optimiser result. Before 2026-09-15 that result was the UN-FITTED "
              "starting model (Batch Fit or server-unreachable fallback): open the file and press Run Fit on each flagged tab.")
    if args.json:
        Path(args.json).write_text(json.dumps({"files": n_files, "flagged": n_flagged, "possible": n_possible, "hits": report}, indent=2))
    return 1 if (n_flagged or n_possible) else 0


if __name__ == "__main__":
    sys.exit(main())
