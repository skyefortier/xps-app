"""Which committed saved fits does the page RESTORE, and how? (background math; owner rule 2026-10-03)

Runs the page's own `_restoredFitBgFailure` (with `_recordBackground`,
`_computeBackgroundForSource`, `_roiSelect` and the background section, extracted from
templates/index.html) over every spectrum tab with a saved fit in the committed
projects, and prints each tab's verdict: CURRENT (the background the fit used — its envelope less its
peaks — equals today's within BG_REL_TOL of its scale), STALE (it differs: reloaded with its
own background, statistics not reported; the size printed), or PEAKS-ONLY (uncheckable: the
reason). The
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
const constBlock = name => {
  const s = lines.findIndex(l => l.startsWith('const ' + name + ' ='));
  let e = s; while (!/;\s*$/.test(lines[e])) e++;
  return lines.slice(s, e + 1).join('\n');
};
const src = require(path.join(root, 'tests/js/_page_background_source.js'))({ manual: 'real' }) + '\n' +
  lines.find(l => l.startsWith('const LEGACY_ENDPOINT_AVG =')) + '\n' +
  lines.find(l => l.startsWith('const BG_RESTORE_REL =')) + '\n' + constBlock('_STARTS_MODEL_FIELDS') + '\n' +
  constBlock('_STARTS_UI_FIELDS') + '\n' +
  ['manualAnchorBackground', '_roiSelect', '_computeBackgroundForSource', '_recordBackground', '_restoredFitBgFailure',
   '_restoredFitGrid', '_restoredFitModel', 'evalAllPeaks', '_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt',
   'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array',
   'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'getPeak', '_migrateLineshapeAliases', '_restoredFitPeaks', '_asFitted', '_legacyVoigts', '_restoredStale',
   '_startsModelKey', '_startsRecordKey'].map(fn).join('\n') +
  '\nconst _getManualAnchors = () => { throw new Error("the active tab is not read"); };' +
  '\nreturn { _restoredFitBgFailure, _migrateLineshapeAliases };';
const { _restoredFitBgFailure, _migrateLineshapeAliases } = new Function(src)();
const out = tabs.map(t => {
  _migrateLineshapeAliases(t.rec.peaks);                 // as the project loader does first
  const reason = _restoredFitBgFailure(t.rec);
  return { project: t.project, tab: t.rec.name, bgType: t.rec.ui.bgType, endpointAvg: t.rec.ui.endpointAvg ?? null,
           kept: reason === null, reason,
           stalePct: reason === null && t.rec.fitResult.backgroundStale ? t.rec.fitResult.backgroundStale.pct : null,
           voigtStale: reason === null && t.rec.fitResult.voigtStale ? t.rec.fitResult.voigtStale : null,
           unconfirmed: !!(reason === null && t.rec.fitResult.backgroundStale && t.rec.fitResult.backgroundStale.unconfirmed) };
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
    cur = [r for r in res if r["kept"] and r["stalePct"] is None and not r["voigtStale"]]
    stale = sorted((r for r in res if r["kept"] and (r["stalePct"] is not None or r["voigtStale"])),
                   key=lambda r: -(r["stalePct"] or 0))
    print(f"{len(files)} projects, {len(res)} spectrum tabs with a saved fit: {len(cur)} current, "
          f"{len(stale)} stale (reloaded, statistics not reported), {len(res) - len(cur) - len(stale)} peaks-only")
    for r in cur:
        print(f"  CURRENT  {r['project']} / {r['tab']}  ({r['bgType']}, averaging {r['endpointAvg']})")
    pcts = sorted(r["stalePct"] for r in stale if r["stalePct"] is not None)
    nv = sum(1 for r in stale if r["voigtStale"])
    nu = sum(1 for r in stale if r["unconfirmed"])
    real = sorted(r["stalePct"] for r in stale if r["stalePct"] is not None and not r["unconfirmed"])
    print(f"  STALE x{len(stale)}: {len(real)} against another background (median {real[len(real) // 2]:.3g} %, max "
          f"{real[-1]:.3g} % of its scale), {nu} unconfirmed (charge correction changed after a keyless older fit), "
          f"{nv} with a Voigt fitted before A03 at another mix, "
          f"{sum(1 for r in stale if r['voigtStale'] and r['stalePct'] is None)} of them for that alone")
    for r in stale:
        bgp = f"{r['stalePct']:9.3g} %" if r["stalePct"] is not None else "   (same) "
        print(f"    {bgp}  {r['project']} / {r['tab']}  ({r['bgType']})" + ("  [pre-A03 Voigt]" if r["voigtStale"] else ""))
    reasons = {}
    for r in res:
        if not r["kept"]:
            key = r["reason"].split(" by ")[0]
            reasons[key] = reasons.get(key, 0) + 1
    for k, n in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"  PEAKS-ONLY x{n}: {k}")
    if a.json:
        with open(a.json, "w") as fh:
            json.dump(res, fh, indent=1)


if __name__ == "__main__":
    main()
