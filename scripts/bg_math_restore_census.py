"""Which committed saved fits does the page RESTORE? (background math, Codex impl round 3)

Runs the page's own `_restoredFitBgFailure` (with `_recordBackground`,
`_computeBackgroundForSource`, `_roiSelect` and the background section, extracted from
templates/index.html) over every spectrum tab with a saved fit in the committed
projects, and prints each tab's verdict: kept, or the reason it is dropped. The
tab record is the one `_loadProjectJSON` builds (its `ui` defaults applied).

    venv/bin/python scripts/bg_math_restore_census.py [--json OUT]
"""
import argparse
import glob
import json
import os
import subprocess
import tempfile
import zipfile

ROOT = os.path.join(os.path.dirname(__file__), "..")
UI_DEFAULTS = {"bgType": "shirley", "bgStart": "", "bgEnd": "", "shirleyIter": "5", "roiMin": "",
               "roiMax": "", "ccMethod": "none", "ccObs": "", "ccLit": ""}

NODE = r"""
const fs = require('fs'), path = require('path');
const root = process.argv[1], tabs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const lines = fs.readFileSync(path.join(root, 'templates/index.html'), 'utf8').split('\n');
const fn = name => {
  const s = lines.findIndex(l => l.startsWith('function ' + name + '('));
  let d = 0, seen = false;
  for (let i = s; i < lines.length; i++) {
    for (const c of lines[i]) { if (c === '{') { d++; seen = true; } else if (c === '}') d--; }
    if (seen && d === 0) return lines.slice(s, i + 1).join('\n');
  }
  throw new Error(name);
};
const src = require(path.join(root, 'tests/js/_page_background_source.js'))({ manual: 'real' }) + '\n' +
  lines.find(l => l.startsWith('const LEGACY_ENDPOINT_AVG =')) + '\n' +
  ['manualAnchorBackground', '_roiSelect', '_computeBackgroundForSource', '_recordBackground', '_restoredFitBgFailure'].map(fn).join('\n') +
  '\nconst _getManualAnchors = () => { throw new Error("the active tab is not read"); };' +
  '\nreturn { _restoredFitBgFailure };';
const { _restoredFitBgFailure } = new Function(src)();
const out = tabs.map(t => {
  const reason = _restoredFitBgFailure(t.rec);
  return { project: t.project, tab: t.rec.name, bgType: t.rec.ui.bgType, endpointAvg: t.rec.ui.endpointAvg ?? null,
           kept: reason === null, reason };
});
console.log(JSON.stringify(out));
"""


def tabs_of(path):
    z = zipfile.ZipFile(path)
    manifest = json.loads(z.read("manifest.json"))
    for s in manifest.get("spectra", []):
        t = json.loads(z.read(s["filename"]))
        if t.get("isStack") or not t.get("fitResult"):
            continue
        yield {"name": t.get("name"), "rawBE": t.get("rawBE") or [], "rawIntensity": t.get("rawIntensity") or [],
               "ccShift": t.get("ccShift") or 0, "manualAnchors": t.get("manualAnchors") or [],
               "fitResult": t["fitResult"], "peaks": t.get("peaks") or [], "ui": {**UI_DEFAULTS, **(t.get("ui") or {})}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip")))
    tabs = [{"project": os.path.basename(f), "rec": r} for f in files for r in tabs_of(f)]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(tabs, fh)
        tmp = fh.name
    try:
        res = json.loads(subprocess.run(["node", "-e", NODE, ROOT, tmp], capture_output=True, text=True, check=True).stdout)
    finally:
        os.unlink(tmp)
    kept = [r for r in res if r["kept"]]
    print(f"{len(files)} projects, {len(res)} spectrum tabs with a saved fit: {len(kept)} restored, {len(res) - len(kept)} dropped")
    for r in kept:
        print(f"  RESTORED  {r['project']} / {r['tab']}  ({r['bgType']}, averaging {r['endpointAvg']})")
    reasons = {}
    for r in res:
        if not r["kept"]:
            key = r["reason"].split(" (it differs")[0]
            reasons[key] = reasons.get(key, 0) + 1
    for k, n in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"  dropped x{n}: {k}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
