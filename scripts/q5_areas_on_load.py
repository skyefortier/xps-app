#!/usr/bin/env python3
"""Q5 unit (owner 2026-10-12), through the page's own loading path (Codex Q5 round 1: a census of the
raw records skipped the restore, which drops fits it cannot reconstruct, and integrated on a saved
fit grid that older saves hold in the UNCORRECTED frame): every committed project is loaded into the
page in a real browser and each tab activated; for every component it records the area every reader
now shows (_peakArea on _areaGrid: the server's trapezoid) beside the rectangle sum the page showed
until now on the same grid, the area % under both, Auto-Fit's 40 % graphite warning under both, and
whether Results shows the "centred outside the window" note. Usage:
venv/bin/python scripts/outside_window_note_on_load.py BASE_URL. Writes docs/findings/q5-area/on_load.json."""
import glob, json, os, sys, time
from playwright.sync_api import sync_playwright

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5151"
OUT = os.path.join(REPO, "docs/findings/q5-area/on_load.json")
READ = """() => { const n = document.querySelector('#results-area .outside-window-note');
  const ids = n ? n.getAttribute('data-peak-ids').split(',') : [];
  const g = _areaGrid();
  // the page's area until this unit: the rectangle sum x the first step, on the same grid
  const rect = p => g.length > 1 ? evalPeakArray(g, p).reduce((s, y) => s + y, 0) * Math.abs(g[1] - g[0]) : 0;
  const comps = state.peaks.map(p => ({ name: p.name, id: p.id, rect: rect(p), now: g.length > 1 ? _peakArea(p, g) : 0 }));
  const tr = comps.reduce((s, c) => s + c.rect, 0), tn = comps.reduce((s, c) => s + c.now, 0);
  comps.forEach(c => { c.pct_rect = tr > 0 ? 100 * c.rect / tr : null; c.pct_now = tn > 0 ? 100 * c.now / tn : null; });
  const gr = state.peaks.find(p => p.name === 'Graphite');
  const warn = gr ? { rect: !!_autoFitDecideAreaWarning(comps.map(c => ({ id: c.id, area: c.rect })), gr.id),
                      now: !!_autoFitDecideAreaWarning(comps.map(c => ({ id: c.id, area: c.now })), gr.id),
                      pct: comps.find(c => c.id === gr.id).pct_now } : null;
  return { fit: !!state.fitResult, stats: _statsLiveState(), components: state.peaks.length, comps, warn,
           noted: state.peaks.filter(p => ids.includes(String(p.id))).map(p => ({ name: p.name, center: p.center })),
           window: g.length ? [_arrMin(g), _arrMax(g)] : null }; }"""

rows = []
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for f in sorted(glob.glob(os.path.join(REPO, "docs/autofit/test_data/**/*.proj.*"), recursive=True)):
        pg = b.new_page(viewport={"width": 1200, "height": 900})
        pg.goto(BASE + "/", wait_until="load")
        pg.set_input_files("#load-session-input", f)
        pg.wait_for_function("() => tabManager && tabManager.tabs && tabManager.tabs.length > 0", timeout=120000)
        time.sleep(2)
        for t in pg.evaluate("() => tabManager.tabs.filter(t => !t.isStack).map(t => ({ id: t.id, name: t.name }))"):
            pg.evaluate("(id) => tabManager.activateTab(id)", t["id"])
            r = pg.evaluate(READ)
            if r["components"]:
                rows.append({"file": os.path.basename(f), "tab": t["name"], **r})
        pg.close()
    b.close()
rel = sorted(abs(c["now"] - c["rect"]) / c["rect"] for r in rows for c in r["comps"] if c["rect"] > 0)
dpp = sorted(max(abs(c["pct_now"] - c["pct_rect"]) for c in r["comps"] if c["pct_now"] is not None) for r in rows if any(c["pct_now"] is not None for c in r["comps"]))
q = lambda xs, f: xs[min(len(xs) - 1, int(f * len(xs)))] if xs else None
gr = [r for r in rows if r["warn"]]
out = {"tabs_with_peaks": len(rows), "components": sum(r["components"] for r in rows),
       "area_rel_change": {"median": q(rel, .5), "p90": q(rel, .9), "max": rel[-1] if rel else None,
                           "over_0_1_pct": sum(v > 1e-3 for v in rel), "over_1_pct": sum(v > 1e-2 for v in rel)},
       "area_pct_change_pp_per_tab_max": {"median": q(dpp, .5), "max": dpp[-1] if dpp else None,
                                          "tabs_over_0_1_pp": sum(v > .1 for v in dpp)},
       "graphite_warning": {"tabs": len(gr), "warn_before": sum(r["warn"]["rect"] for r in gr), "warn_now": sum(r["warn"]["now"] for r in gr),
                            "flips": [r["file"] + " / " + r["tab"] for r in gr if r["warn"]["rect"] != r["warn"]["now"]],
                            "nearest_to_40": sorted((round(r["warn"]["pct"], 2) for r in gr), key=lambda v: abs(v - 40))[:3]},
       "tabs_with_a_restored_fit": sum(r["fit"] for r in rows),
       "noted": sum(len(r["noted"]) for r in rows), "tabs_with_a_note": sum(1 for r in rows if r["noted"]),
       "noted_with_a_fit": sum(len(r["noted"]) for r in rows if r["fit"]), "rows": rows}
json.dump(out, open(OUT, "w"), indent=1)
print({k: v for k, v in out.items() if k != "rows"})
for r in rows:
    if r["noted"]:
        print(" ", r["file"], "/", r["tab"], "fit" if r["fit"] else "no fit", r["stats"], [n["name"] for n in r["noted"]], r["window"])
