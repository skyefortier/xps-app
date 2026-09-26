import glob, json, os, sys
from playwright.sync_api import sync_playwright
S = "/private/tmp/claude-501/-Users-skyefortier-xps-app/02af00e1-adfc-44c5-aadc-a32951efe70c/scratchpad"
def chromium():
    base = os.path.expanduser("~/Library/Caches/ms-playwright")
    for pat in [base + "/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing", base + "/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium"]:
        h = sorted(glob.glob(pat))
        if h: return h[-1]
out = {}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, executable_path=chromium()); pg = b.new_page(); errors = []; pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto("http://127.0.0.1:5151/", wait_until="load"); pg.set_input_files("#fileInput", S + "/wide_scan.csv")
    pg.wait_for_function("() => state.rawBE && state.rawBE.length > 1000", timeout=30000)
    # the tab record holds a C 1s window (as if the student had set it and switched tabs once)
    pg.evaluate("() => { document.getElementById('roi-min').value = 280; document.getElementById('roi-max').value = 295; tabManager._syncActiveToRecord(); updatePlot(); }")
    out['record_roi'] = pg.evaluate("() => { const t = tabManager._getTab(tabManager.activeId); return [t.ui.roiMin, t.ui.roiMax]; }")
    # the student now types the U 4f window, no tab switch
    pg.evaluate("() => { const a = document.getElementById('roi-min'), c = document.getElementById('roi-max'); a.value = 370; c.value = 415; a.dispatchEvent(new Event('input')); c.dispatchEvent(new Event('input')); }"); pg.wait_for_timeout(200)
    out['menu_enabled'] = pg.evaluate("() => !document.getElementById('auto-fit-c1s-menu-item').disabled")
    out['isC1sTab_live'] = pg.evaluate("() => isC1sTab(tabManager._getTab(tabManager.activeId))")
    pg.evaluate("() => { window.__notes = []; const n = notify; window.notify = (m, k) => { window.__notes.push([k, String(m).slice(0, 220)]); return n(m, k); }; }")
    pg.evaluate("() => { window.__a = false; runAutoFitC1sGraphite().then(() => window.__a = true, () => window.__a = true); }"); pg.wait_for_timeout(600)
    if pg.evaluate("() => document.getElementById('auto-fit-c1s-confirm-overlay').classList.contains('open')"): pg.click("#auto-fit-c1s-confirm-proceed")
    pg.wait_for_function("() => window.__a === true", timeout=280000); pg.wait_for_timeout(500)
    out['after'] = pg.evaluate("() => ({ ccShift: state.ccShift, ccMethod: (document.getElementById('cc-method')||{}).value, ccObs: (document.getElementById('cc-obs')||{}).value, status: document.getElementById('sb-msg').textContent, peaks: state.peaks.map(p => [p.name, +p.center.toFixed(2)]) })")
    out['notices'] = pg.evaluate("() => window.__notes")
    out['toasts'] = pg.evaluate("() => Array.from(document.querySelectorAll('.notify, .toast, #notify-area *')).map(e => e.textContent.slice(0, 200)).filter(Boolean).slice(0, 6)")
    out['page_errors'] = errors
    b.close()
print(json.dumps(out, indent=1, ensure_ascii=False))
