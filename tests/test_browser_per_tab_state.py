"""Real-browser guard for per-tab state ownership
(docs/superpowers/plans/2026-09-08-per-tab-state-ownership.md).

Undo/redo stacks and the Find Peaks result live on the tab record, so a
restore can never land on another tab: not after a switch, not after a
close, not after a project reload, and never on a stack tab.
Skips cleanly when Playwright/Chromium are absent.
"""
import glob
import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_chromium():
    base = os.path.expanduser("~/Library/Caches/ms-playwright")
    for pat in [
        base + "/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        base + "/chromium-*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
        base + "/chromium-*/chrome-linux/chrome",
        base + "/chromium_headless_shell-*/chrome-headless-shell-*/chrome-headless-shell",
    ]:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[-1]
    return None


def _free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close(); return port


@pytest.fixture(scope="module")
def server():
    gunicorn = os.path.join(os.path.dirname(sys.executable), "gunicorn")
    if not os.path.exists(gunicorn):
        pytest.skip("gunicorn not found next to the test interpreter")
    port = _free_port()
    proc = subprocess.Popen([gunicorn, "app:app", "-w", "1", "-b", f"127.0.0.1:{port}", "--timeout", "60"],
                            cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}"
    try:
        ok = False
        for _ in range(50):
            if proc.poll() is not None:
                pytest.skip("gunicorn exited during startup")
            try:
                with urllib.request.urlopen(base + "/api/health", timeout=1) as r:
                    if r.status == 200:
                        ok = True; break
            except Exception:
                time.sleep(0.2)
        if not ok:
            pytest.skip("gunicorn did not become healthy")
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


@pytest.fixture(scope="module")
def browser():
    exe = _find_chromium()
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(headless=True)
        except Exception:
            if not exe:
                pytest.skip("no usable Chromium build found")
            b = p.chromium.launch(headless=True, executable_path=exe)
        yield b
        b.close()


def _page(browser, server):
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.goto(server + "/", wait_until="load")
    return pg


GRID = """const be=[], inten=[];
    for (let i=0;i<120;i++){ const x=295-i*0.1; be.push(+x.toFixed(2)); inten.push(800+3000*Math.exp(-Math.pow(x-286.5,2)/0.5)); }"""

FP_RESULT = """{ body: { peaks: [ { role: 'C-C', center: 284.8, fwhm: 1.2, amplitude: 3000, shape: 'pseudo_voigt_gl', gl_ratio: 0.3 } ], diagnostics: {} },
                method: 'ic_model_comparison', regions: ['C1s'], fitFullWindow: false, endpointAvg: '3' }"""


def _snap(pg):
    return pg.evaluate("""() => ({ active: tabManager.activeId, nPeaks: state.peaks.length,
                                    undoDisabled: document.getElementById('btn-undo').disabled,
                                    redoDisabled: document.getElementById('btn-redo').disabled })""")


def test_undo_never_crosses_tabs_and_each_tab_keeps_its_own_history(browser, server):
    pg = _page(browser, server)
    try:
        ids = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('A', be, inten); const a = tabManager.activeId;
            addPeak(); addPeak();                         // A: two edits -> two undo entries
            tabManager.createTab('B', be, inten); const b = tabManager.activeId;
            addPeak();                                    // B: one edit
            return { a, b }; }""")
        pg.evaluate("() => undo()")                                   # on B: undoes B's edit only
        s = _snap(pg)
        assert s["active"] == ids["b"] and s["nPeaks"] == 0 and s["undoDisabled"], s
        pg.evaluate("() => undo()")                                   # nothing left on B: must NOT touch A's history
        assert _snap(pg)["nPeaks"] == 0
        pg.evaluate("(a) => tabManager.activateTab(a)", ids["a"])
        s = _snap(pg)
        assert s["nPeaks"] == 2 and not s["undoDisabled"], s        # A intact, A's history still there
        pg.evaluate("() => undo()")
        assert _snap(pg)["nPeaks"] == 1
        pg.evaluate("() => redo()")
        assert _snap(pg)["nPeaks"] == 2
    finally:
        pg.close()


def test_closing_a_tab_drops_its_history_and_reload_starts_empty(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('A', be, inten); const a = tabManager.activeId; addPeak();
            tabManager.createTab('B', be, inten); const b = tabManager.activeId; addPeak();
            const saved = []; window._downloadBlob = (blob) => { saved.push(blob.text()); };
            return _doSaveProject().then(async () => {
                const json = (await Promise.all(saved))[0];
                tabManager.closeTab(a);                                   // A gone with its stack
                const afterClose = { active: tabManager.activeId, undoDisabled: document.getElementById('btn-undo').disabled };
                _loadProjectJSON(JSON.parse(json), 'p.proj.json');       // reload: fresh records
                const reopened = tabManager._getTab(a); tabManager.activateTab(a);
                undo();                                                   // must be a no-op: no history survives a reload
                return { afterClose, serialisedHasStack: /undoStack|redoStack|findPeaks/.test(json),
                         reopenedPeaks: state.peaks.length, undoDisabled: document.getElementById('btn-undo').disabled };
            }); }""")
        assert out["afterClose"]["undoDisabled"] is False          # B still has its own entry
        assert out["serialisedHasStack"] is False, "runtime stacks must never be persisted"
        assert out["reopenedPeaks"] == 1 and out["undoDisabled"] is True, out
    finally:
        pg.close()


def test_find_peaks_result_belongs_to_the_tab_it_was_produced_on(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            window.confirm = () => true; window._showFindPeaksApplyConfirmModal = async () => true;
            tabManager.createTab('A', be, inten); const a = tabManager.activeId;
            _fpSetLast(""" + FP_RESULT + """);                       // result produced on A
            tabManager.createTab('B', be, inten); const b = tabManager.activeId;
            return applyFindPeaks().then(() => {
                const bPeaks = state.peaks.length;                        // B must be untouched
                tabManager.activateTab(a);
                return applyFindPeaks().then(() => ({ bPeaks, aPeaks: state.peaks.length }));
            }); }""")
        assert out == {"bPeaks": 0, "aPeaks": 1}, out
    finally:
        pg.close()


def test_stack_tab_active_makes_undo_redo_and_apply_inert(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            window.confirm = () => true; window._showFindPeaksApplyConfirmModal = async () => true;
            tabManager.createTab('A', be, inten); addPeak();
            _fpSetLast(""" + FP_RESULT + """);
            tabManager.createStackTab();
            const st = tabManager._getTab(tabManager.activeId);
            undo(); redo(); pushUndo();
            return applyFindPeaks().then(() => ({ isStack: !!st.isStack, peaks: state.peaks.length,
                     undoDisabled: document.getElementById('btn-undo').disabled, hasStack: 'undoStack' in st })); }""")
        assert out["isStack"] and out["peaks"] == 0 and out["undoDisabled"] and not out["hasStack"], out
    finally:
        pg.close()


# ── async ownership (Codex round 1, both runs): an operation is bound to the
# record it started on, before its first await ─────────────────────────────

def _deferred_confirm(pg):
    pg.evaluate("""() => { window.confirm = () => true;
        window._showFindPeaksApplyConfirmModal = () => new Promise(r => { window.__resolveConfirm = r; }); }""")


def test_apply_aborts_when_the_tab_changed_during_confirmation(browser, server):
    pg = _page(browser, server)
    try:
        _deferred_confirm(pg)
        pg.evaluate("() => { " + GRID + """
            tabManager.createTab('A', be, inten); window.__a = tabManager.activeId;
            _fpSetLast(""" + FP_RESULT + """);
            window.__apply = applyFindPeaks();                      // pending on the confirmation
            tabManager.createTab('B', be, inten); window.__b = tabManager.activeId; }""")
        out = pg.evaluate("""() => { window.__resolveConfirm(true); return window.__apply.then(() => ({
            bPeaks: state.peaks.length,                                 // B is active: read the LIVE peaks, not a stale record
            aPeaks: tabManager._getTab(window.__a).peaks.length,
            active: tabManager.activeId === window.__b })); }""")
        assert out == {"bPeaks": 0, "aPeaks": 0, "active": True}, out
    finally:
        pg.close()


def test_find_peaks_result_lands_on_the_tab_it_was_started_on(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('A', be, inten); window.__a = tabManager.activeId;
            return openFindPeaksModal().then(() => {
                document.getElementById('fp-method').value = 'ic_model_comparison'; _fpMethodChanged();
                _fpRegionsSelected.clear(); _fpRegionsSelected.add('C 1s');
                // fake the server: start returns a job, polling is held until the test releases it
                const realFetch = window.fetch;
                window.fetch = (u, o) => String(u).includes('/api/analyze/start')
                    ? Promise.resolve(new Response(JSON.stringify({ job_id: 'j1' }), { status: 200, headers: { 'Content-Type': 'application/json' } }))
                    : realFetch(u, o);
                window._fpPollJob = () => new Promise(r => { window.__resolvePoll = r; });
                window.__run = runFindPeaks();
                tabManager.createTab('B', be, inten); window.__b = tabManager.activeId;
                // runFindPeaks reaches the poll only after its upload + start awaits: wait for it
                const untilPolling = () => new Promise(res => { const t = setInterval(() => { if (window.__resolvePoll) { clearInterval(t); res(); } }, 25); });
                return untilPolling().then(() => {
                    window.__resolvePoll({ result: { peaks: [ { role: 'C-C', center: 284.8, fwhm: 1.2, amplitude: 3000, shape: 'pseudo_voigt_gl' } ], diagnostics: {} } });
                    return window.__run;
                }).then(() => ({
                    aHas: !!(tabManager._getTab(window.__a).findPeaks && tabManager._getTab(window.__a).findPeaks.last),
                    bHas: !!(tabManager._getTab(window.__b).findPeaks && tabManager._getTab(window.__b).findPeaks.last),
                    status: document.getElementById('fp-status').textContent }));
            }); }""")
        assert out["aHas"] and not out["bHas"], out
        assert "A" in out["status"] or "tab" in out["status"].lower(), out
    finally:
        pg.close()


def test_debounced_undo_belongs_to_the_edited_tab(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('B', be, inten); const b = tabManager.activeId;
            addPeak(); undo();                                        // B: one redo entry, no undo entries
            tabManager.createTab('A', be, inten); const a = tabManager.activeId;
            addPeak(); const pid = state.peaks[0].id;
            updatePeakParam(pid, 'center', 285.0);                    // debounced undo on A
            tabManager.activateTab(b);                                 // switch before the 500 ms timer fires
            return new Promise(r => setTimeout(r, 700)).then(() => ({
                bUndo: (tabManager._getTab(b).undoStack || []).length, bRedo: (tabManager._getTab(b).redoStack || []).length,
                aUndo: (tabManager._getTab(a).undoStack || []).length })); }""")
        assert out["bRedo"] == 1 and out["bUndo"] == 0, out          # B's history untouched by A's timer
        assert out["aUndo"] >= 2, out                                 # A got addPeak's entry and the debounced edit's entry
    finally:
        pg.close()


def test_auto_fit_rollback_is_bound_to_the_originating_record_object(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('A', be, inten); const a = tabManager.activeId; const aObj = tabManager._getTab(a);
            const snap = _autoFitSnapshot();                           // A with 0 peaks
            addPeak();                                                 // A now 1 peak (the 'provisional' state)
            tabManager.createTab('B', be, inten); const b = tabManager.activeId; addPeak();
            _autoFitRestore(snap, aObj);                               // owner live but not active -> A's RECORD restored
            const afterRecordRestore = { a: tabManager._getTab(a).peaks.length, b: state.peaks.length };
            const saved = []; window._downloadBlob = (blob) => saved.push(blob.text());
            return _doSaveProject().then(async () => {
                const json = (await Promise.all(saved))[0];
                tabManager.closeTab(a);
                _loadProjectJSON(JSON.parse(json), 'p.proj.json');   // reopened A: same id, NEW object
                const reopened = tabManager._getTab(a);
                reopened.peaks = [ { id: 1, name: 'x', center: 285, fwhm: 1, amplitude: 1, shape: 'GL' } ];
                _autoFitRestore(snap, aObj);                           // stale owner object: must be inert
                return { afterRecordRestore, reopenedPeaks: tabManager._getTab(a).peaks.length, sameId: reopened !== aObj };
            }); }""")
        assert out["afterRecordRestore"] == {"a": 0, "b": 1}, out
        assert out["reopenedPeaks"] == 1 and out["sameId"], out
    finally:
        pg.close()


def test_fit_file_load_aborts_when_the_tab_changed_while_reading(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('A', be, inten); const a = tabManager.activeId;
            const fit = JSON.stringify({ version: 1, peaks: [ { id: 1, name: 'imported', center: 285, fwhm: 1, amplitude: 1, shape: 'GL' } ],
                                         background: { type: 'shirley', start: '295', end: '283.1', shirleyIter: '5' } });
            const f = new File([fit], 'x.fit.json');
            f.text = () => new Promise(r => { window.__resolveText = () => r(fit); });
            window.__load = _loadSessionFile(f);
            tabManager.createTab('B', be, inten); const b = tabManager.activeId;
            window.__resolveText();
            return window.__load.then(() => ({ bPeaks: tabManager._getTab(b).peaks.length, aPeaks: tabManager._getTab(a).peaks.length })); }""")
        assert out == {"bPeaks": 0, "aPeaks": 0}, out
    finally:
        pg.close()


def test_v1_import_is_undoable_and_clears_a_stale_find_peaks_result(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('A', be, inten); addPeak(); state.peaks[0].center = 290.0;
            _fpSetLast(""" + FP_RESULT + """);
            tabManager.fromJSON({ version: 1, peaks: [ { id: 7, name: 'imported', center: 285, fwhm: 1, amplitude: 1, shape: 'GL' } ],
                                  background: { type: 'shirley', start: '295', end: '283.1', shirleyIter: '5' } });
            const afterImport = { n: state.peaks.length, name: state.peaks[0].name, fp: _fpGetLast() };
            undo();
            return { afterImport, afterUndo: { n: state.peaks.length, center: state.peaks[0].center } }; }""")
        assert out["afterImport"]["name"] == "imported" and out["afterImport"]["fp"] is None, out
        assert out["afterUndo"] == {"n": 1, "center": 290.0}, out
    finally:
        pg.close()


def test_shift_z_redoes(browser, server):
    pg = _page(browser, server)
    try:
        out = pg.evaluate("() => { " + GRID + """
            tabManager.createTab('A', be, inten); addPeak(); undo();
            document.body.focus();
            document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Z', shiftKey: true, ctrlKey: true, bubbles: true }));
            return state.peaks.length; }""")
        assert out == 1, out
    finally:
        pg.close()
