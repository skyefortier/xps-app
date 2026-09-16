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

This is a TRIAGE tool: it reports SUSPECTED local-optimiser results with
the evidence for each, it cannot prove that a flagged result was
un-fitted, and a file it reports as clean is not proven unaffected.

Levels reported per tab:

  SUSPECTED   UNWEIGHTED statistics, the local optimiser's signature. It
              stores chiReduced = sum(r^2)/(n-k) and rmse = sqrt(sum(r^2)/n),
              so chiReduced / rmse^2 = n/(n-k), about 1. The server (lmfit)
              stores a counting-noise-WEIGHTED reduced chi-square, so the
              same ratio is about 1/<counts>. The two coincide when counts
              are ~1 per channel; as a rough guard the ratio is used only
              when rmse > 10 counts (rmse is a proxy for count level, not a
              measurement of it, so very-low-count server fits can still be
              listed). Corroborating evidence is listed: a huge chiReduced,
              and another tab in the same project carrying the IDENTICAL
              centre/width set (consistent with a Batch Fit copy, or with a
              deliberately locked model).
  POSSIBLE    the ratio sits between the two ranges, or the counts are too
              low for the ratio to discriminate — inspect the file.
  INSUFFICIENT no rmse stored (older files): cannot classify; listed when
              chiReduced is huge or an identical-model twin exists.
  POST-FIX    the file itself says engine "local" (written by the fixed
              app on/after 2026-09-15): an honest but unweighted local fit,
              with no uncertainties. Not part of the incident; re-run Run
              Fit before quantifying.

Exit code: 1 when anything is SUSPECTED/POSSIBLE/INSUFFICIENT, 2 when a
file could not be read (never reported as clean), 0 otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

RATIO_FLAG = 0.1        # chiReduced / rmse^2 above this: unweighted (local) statistics
RATIO_POSSIBLE = 0.01   # between this and RATIO_FLAG: possible, check the file
RMSE_MIN = 10.0         # below ~10 counts rms the weighted and unweighted ratios can coincide
CHI_HUGE = 1000.0       # corroboration only: a weighted chi^2_r this large is implausible but not impossible
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
    """Return one hit dict per reported tab: {tab, level, ratio, chiReduced, reasons}."""
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
        twins = [n for n in keys.get(_model_key(peaks), []) if n != t.get("name", "?")]
        reasons, level, ratio = [], None, None
        if fr.get("engine") == "local" or fr.get("objective") == "unweighted_residual_variance":
            level = "post-fix"
            reasons.append("file records engine 'local': a converged but unweighted local fit written by the fixed app; no uncertainties")
        elif chi_r is not None and rmse is not None and rmse > 0:
            ratio = chi_r / (rmse * rmse)
            if rmse < RMSE_MIN and ratio >= RATIO_POSSIBLE:
                level = "possible"
                reasons.append(f"chiReduced/rmse^2 = {ratio:.3g} but rmse = {rmse:.3g} counts is too low for the ratio to separate weighted from unweighted statistics")
            elif ratio >= RATIO_FLAG:
                level = "suspected"
                reasons.append(f"unweighted statistics: chiReduced/rmse^2 = {ratio:.3g} (local optimiser; a server fit stores ~1/<counts>)")
            elif ratio >= RATIO_POSSIBLE:
                level = "possible"
                reasons.append(f"chiReduced/rmse^2 = {ratio:.3g} is between the server and local ranges; inspect the file")
        elif chi_r is not None and (chi_r > CHI_HUGE or twins):
            level = "insufficient"
            reasons.append("no rmse stored: the unweighted-statistics test cannot be applied")
        if level and level != "post-fix":
            if chi_r is not None and chi_r > CHI_HUGE:
                reasons.append(f"corroboration: chiReduced = {chi_r:.4g} is far above any plausible weighted value")
            if twins:
                reasons.append(f"corroboration: identical centre/width set to tab(s) {', '.join(twins)} — consistent with a Batch Fit copy (or a locked model)")
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
    report, counts, n_files, n_errors = [], {"suspected": 0, "possible": 0, "insufficient": 0, "post-fix": 0}, 0, 0
    for p in args.paths:
        if not Path(p).exists():
            n_errors += 1
            print(f"UNREADABLE {p}: no such file or directory")
    for f in iter_files(args.paths):
        n_files += 1
        try:
            hits = scan_path(f)
        except Exception as exc:  # unreadable / not a project file: NOT clean
            n_errors += 1
            print(f"UNREADABLE {f}: {exc}")
            continue
        for h in hits:
            report.append(h)
            counts[h["level"]] += 1
            print(f"{h['level'].upper():12s} {f} :: {h['tab']}")
            for r in h["reasons"]:
                print(f"             - {r}")
    print(f"\n{n_files} file(s) scanned: {counts['suspected']} suspected, {counts['possible']} possible, "
          f"{counts['insufficient']} insufficient evidence, {counts['post-fix']} post-fix local, {n_errors} unreadable.")
    if counts["suspected"] or counts["possible"] or counts["insufficient"]:
        print("Suspected tabs carry the local optimiser's statistics signature. Before 2026-09-15 a local-optimiser "
              "result was the UN-FITTED starting model (Batch Fit, or Run Fit after a server error/outage): open the file "
              "and press Run Fit on each such tab.")
    print("This is a triage heuristic: a file with no hits is not proven unaffected (results whose rmse is missing or "
          "was recomputed cannot be classified, and very-low-count fits blur the signature). If you know a tab came from "
          "Batch Fit, re-fit it regardless.")
    if args.json:
        Path(args.json).write_text(json.dumps({"files": n_files, "unreadable": n_errors, **counts, "hits": report}, indent=2))
    if n_errors:
        return 2
    return 1 if (counts["suspected"] or counts["possible"] or counts["insufficient"]) else 0


if __name__ == "__main__":
    sys.exit(main())
