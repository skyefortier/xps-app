"""Unit B: the reduced χ² of the committed fits under each candidate noise estimate — a report, not a conclusion.

collect: every committed project (docs/autofit/test_data/*.proj.zip) loaded into the page served at --url, Run Fit
         pressed on every spectrum tab with a model (the page's own request: Trust-Region, the saved model as the
         start), and each fit's record kept: the fitted window's energies and intensities, fitted_y, the reported
         statistics, and the tab's whole raw spectrum.
analyse: for each fit, the displayed χ²ᵣ (var = max(y, 1), fitting.py:3006) and the χ²ᵣ of the SAME residuals under
         each estimator's variance model, estimated once from the fit window and once from the whole spectrum.
         For a scaled-Poisson model (var = k·y) that is the displayed χ²ᵣ / k exactly.

    venv/bin/python scripts/noise_real_fits.py collect --url http://127.0.0.1:PORT --out FITS.json
    venv/bin/python scripts/noise_real_fits.py analyse FITS.json [--json OUT]
"""
import argparse
import base64
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import noise_estimators as ne  # noqa: E402

LOAD = """async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
  await _loadZipProject(new File([b], name)); }"""
RUN = """async () => {
  const out = [];
  for (const t of tabManager.tabs.filter(x => !x.isStack && x.peaks && x.peaks.length)) {
    tabManager.activateTab(t.id);
    let err = null;
    try { await runFit(); } catch (e) { err = String(e); }
    const fr = state.fitResult, O = fr && fr.seal ? fr.seal.O : null;
    out.push({ tab: t.name, err, engine: fr && fr.seal ? fr.seal.engine : null,
               shapes: t.peaks.map(p => p.shape),
               raw: Array.from(state.rawIntensity || []),
               O: O ? { energy: O.energy, counts: O.counts, fitted_y: O.fitted_y, statistics: O.statistics,
                        success: O.success } : null });
  }
  return out; }"""


def collect(url, out):
    from playwright.sync_api import sync_playwright
    rows = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for f in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip"))):
            pg = br.new_page()
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url + "/", wait_until="load")
            pg.evaluate(LOAD, [base64.b64encode(open(f, "rb").read()).decode(), os.path.basename(f)])
            pg.wait_for_timeout(500)
            for r in pg.evaluate(RUN):
                rows.append({"project": os.path.basename(f), **r, "page_errors": len(errors)})
            pg.close()
            print(os.path.basename(f), "done", flush=True)
        br.close()
    json.dump(rows, open(out, "w"))


EST = ("scaled_d2", "scaled_d4", "scaled_d2_lag3", "flat_ends", "varmean", "constant_d2", "constant_d4", "der_snr")


def analyse(path, out):
    rows = json.load(open(path))
    res = []
    for r in rows:
        O = r["O"]
        if not O or not O["success"] or r["engine"] != "server":
            continue
        y = np.asarray(O["counts"], float)
        resid = y - np.asarray(O["fitted_y"], float)
        st = O["statistics"]
        p = st["n_free_params"]
        shown = st["reduced_chi_square"]
        recomputed = ne.reduced_chi2(resid, np.maximum(y, 1.0), p)          # = the displayed value (a check)
        row = {"project": r["project"], "tab": r["tab"], "n": int(y.size), "p": p, "displayed": shown,
               "recomputed_k1": recomputed, "la": "LACX" in r["shapes"],
               "region": r["tab"].split(" ")[0] if "Survey" not in r["tab"] else "Survey"}
        raw = np.asarray(r["raw"], float)
        for est in EST:
            for where, data in (("window", y), ("spectrum", raw)):
                m = ne.ESTIMATORS[est](data)
                row[f"{est}@{where}"] = ne.reduced_chi2(resid, m.variance(y), p)
        res.append(row)
    print(f"{len(res)} converged server fits (of {len(rows)} tabs with a model)")
    print(f"displayed χ²ᵣ recomputed from the residuals: max relative difference "
          f"{max(abs(r['recomputed_k1'] / r['displayed'] - 1) for r in res):.1e}")
    q = lambda v: f"median {np.median(v):7.2f}  10-90 % [{np.percentile(v, 10):7.2f}, {np.percentile(v, 90):7.2f}]"
    print(f"{'displayed (var = max(y,1))':34s} {q([r['displayed'] for r in res])}")
    for est in EST:
        for where in ("window", "spectrum"):
            print(f"{est + ' @ ' + where:34s} {q([r[f'{est}@{where}'] for r in res])}")
    print("\nthe same estimator from the fit window and from the whole spectrum, PER FIT (ratio of the two χ²ᵣ):")
    for est in EST:
        rat = np.array([r[f"{est}@window"] / r[f"{est}@spectrum"] for r in res])
        worst = max(res, key=lambda r: abs(np.log(r[f"{est}@window"] / r[f"{est}@spectrum"])))
        print(f"  {est:16s} window/spectrum median {np.median(rat):5.2f}  10-90 % [{np.percentile(rat, 10):5.2f}, {np.percentile(rat, 90):5.2f}]"
              f"  extreme {worst[f'{est}@window']:.2f} vs {worst[f'{est}@spectrum']:.2f} ({worst['project'][:20]} / {worst['tab']})")
    by = {}
    for r in res:
        by.setdefault(r["region"], []).append(r)
    print("\nby region (median): displayed | scaled_d4@window | scaled_d2@window | varmean@window | flat_ends@window")
    for reg, rs in sorted(by.items()):
        md = lambda k: np.median([x[k] for x in rs])
        print(f"  {reg:8s} {len(rs):3d} fits  {md('displayed'):7.2f} | {md('scaled_d4@window'):7.2f} | "
              f"{md('scaled_d2@window'):7.2f} | {md('varmean@window'):7.2f} | {md('flat_ends@window'):7.2f}")
    if out:
        json.dump(res, open(out, "w"), indent=1)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="phase", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--url", required=True)
    c.add_argument("--out", required=True)
    a_ = sub.add_parser("analyse")
    a_.add_argument("fits")
    a_.add_argument("--json")
    a = ap.parse_args()
    if a.phase == "collect":
        collect(a.url, a.out)
    else:
        analyse(a.fits, a.json)


if __name__ == "__main__":
    main()
