"""Seal 1b: every spectrum tab with peaks in the committed projects, as `scripts/optimizer_disagreement_targets.js`
reads them (project, name, peaks, ui, ccShift, rawBE, rawIntensity) — so the fit targets are rebuilt with the
CURRENT page's request builder (Codex 1b round 1: the targets file in use had been built before A03 and lacked
`frontend_shape`). The tab's `ui` gets the defaults `_loadProjectJSON` applies.

Usage: python scripts/seal_1b_tabs.py OUT_tabs.json
       node scripts/optimizer_disagreement_targets.js OUT_tabs.json > targets.json
"""
import glob
import json
import os
import sys
import zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
UI_DEFAULTS = {"bgType": "shirley", "bgStart": "", "bgEnd": "", "shirleyIter": "5", "roiMin": "",
               "roiMax": "", "ccMethod": "none", "ccObs": "", "ccLit": ""}


def tabs_of(path):
    z = zipfile.ZipFile(path)
    manifest = json.loads(z.read("manifest.json"))
    for s in manifest.get("spectra", []):
        t = json.loads(z.read(s["filename"]))
        if t.get("isStack") or not t.get("peaks"):
            continue
        yield {"project": os.path.basename(path), "name": t.get("name"), "peaks": t["peaks"],
               "ui": {**UI_DEFAULTS, **(t.get("ui") or {})}, "ccShift": t.get("ccShift") or 0,
               "rawBE": t.get("rawBE") or [], "rawIntensity": t.get("rawIntensity") or []}


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip")))
    tabs = [t for f in files for t in tabs_of(f)]
    json.dump(tabs, open(sys.argv[1], "w"))
    shapes = sorted({p.get("shape") for t in tabs for p in t["peaks"]})
    print(f"{len(tabs)} tabs with peaks from {len(files)} projects; shapes {shapes}")
