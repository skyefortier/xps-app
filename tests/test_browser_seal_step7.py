"""Seal 1c step 7 (plan docs/superpowers/plans/2026-10-14-seal-1c-page.md §6.3, §9, §11, §12 step 7): every
producer installs its SEAL and nothing else; a fresh server fit checks itself (Run Fit / "Use this solution" by a
producer-bound check, Auto-Fit by its two staged checks BEFORE anything is published — only a fit both checks
confirm is installed); a STALE sealed fit's spectrum file writes the current model's curves, as a save with no fit
does; and the legacy census — every committed saved fit loads LEGACY (no seal is ever manufactured) and re-saves
without one.

Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import glob
import io
import json
import os
import zipfile

import pytest

pytest.importorskip("playwright.sync_api")

from test_browser_bg_window_request import browser, server  # noqa: F401,E402
from test_browser_seal_requests import SCENARIOS, _setup, AUTOFIT_PROJECT  # noqa: E402

ROOT = os.path.join(os.path.dirname(__file__), "..")
STATE = "() => { const s = sealedState(state.fitResult, _activeTab()); return [s.state, s.check]; }"
SETTLE = """async () => { for (let k = 0; k < 600 && tabManager.tabs.some(t => _sealAttempts.has(t)); k++)
  await new Promise(r => setTimeout(r, 50)); }"""
# the installed result is the seal alone, frozen, and the tab record holds the same object
ONLY_SEAL = """(name) => { const t = name ? tabManager.tabs.find(x => x.name === name) : _activeTab();
  const fr = t === _activeTab() ? state.fitResult : t.fitResult;
  return { keys: Object.keys(fr), frozen: Object.isFrozen(fr) && Object.isFrozen(fr.seal), producer: fr.seal.producer,
           engine: fr.seal.engine, record: t === _activeTab() ? (tabManager._syncActiveToRecord(), t.fitResult === fr) : true }; }"""


def _page(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    return pg


def _verify_calls(pg):
    calls = []
    pg.on("request", lambda r: calls.append(r.url) if r.url.endswith("/api/verify-fit") else None)
    return calls


def test_a_server_run_fit_installs_only_its_seal_and_checks_itself(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        calls = _verify_calls(pg)
        pg.evaluate("async () => { await runFit(); }")
        got = pg.evaluate(ONLY_SEAL, None)
        assert got == {"keys": ["seal"], "frozen": True, "producer": "runFit", "engine": "server", "record": True}, got
        pg.evaluate(SETTLE)                                  # nothing else asked: the fit's own check answers
        assert pg.evaluate(STATE) == ["current", None]
        assert len(calls) == 1, calls
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


def test_a_local_fit_installs_only_its_seal_and_is_its_own_check(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        pg.route("**/api/upload", lambda route: route.abort())
        calls = _verify_calls(pg)
        pg.evaluate("async () => { await runFit(); }")
        got = pg.evaluate(ONLY_SEAL, None)
        assert got == {"keys": ["seal"], "frozen": True, "producer": "local", "engine": "local", "record": True}, got
        assert pg.evaluate(STATE) == ["current", None]
        pg.evaluate(SETTLE)
        assert calls == [], calls                            # the local engine is its own exact check
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_use_this_solution_installs_only_its_seal_and_checks_itself(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        pg.evaluate("async () => { await runFit(); }")
        pg.evaluate(SETTLE)
        # an alternative in the recorded starts (the server's check reads their form, not their values)
        pg.evaluate("""() => { const s = structuredClone(state.fitResult.seal), st = s.O.starts, ips = s.O.individual_peaks;
            st.alternatives = [{ chi2r: st.fit.chi2r * 0.9, n_starts: 1,
              components: st.fit.components.map(c => { const ip = ips.find(q => q.id === c.id);
                return { ...c, area: ip.params.area.value,
                         params: Object.fromEntries(Object.entries(ip.params).filter(([k]) => k !== 'area')
                                   .map(([k, v]) => [k, k === 'center' ? v.value + 0.05 : v.value])) }; }),
              largest_centre_shift_from_start: st.fit.largest_centre_shift_from_start, largest_fraction_difference_pp: 2.0 }];
            st.n_in_alternatives = 1;
            state.fitResult = Object.freeze({ seal: _makeSeal(s) }); }""")
        pg.evaluate("async () => { await _ensureVerified(_activeTab(), true); }")
        assert pg.evaluate(STATE) == ["current", None]
        calls = _verify_calls(pg)
        pg.evaluate("async () => { await useAlternative(0); }")
        got = pg.evaluate(ONLY_SEAL, None)
        assert got == {"keys": ["seal"], "frozen": True, "producer": "useSolution", "engine": "server", "record": True}, got
        pg.evaluate(SETTLE)
        assert pg.evaluate(STATE) == ["current", None] and len(calls) == 1, calls
    finally:
        pg.close()


def test_batch_fit_installs_only_a_seal_on_each_target(browser, server):  # noqa: F811
    pg = _page(browser, server)
    try:
        ids = pg.evaluate("""() => {
            const mk = (amp, off) => { const be = [], inten = [];
                for (let i = 0; i < 80; i++) { const x = 520 + i * 0.25; be.push(x);
                    inten.push(1000 + off + amp * Math.exp(-Math.pow(x - 530, 2) / (2 * 0.9 * 0.9)) + 37 * Math.sin(i)); }
                return { be, inten }; };
            const s = mk(8000, 0); tabManager.createTab('SRC', s.be, s.inten); const srcId = tabManager.activeId;
            document.getElementById('bg-type').value = 'linear';
            addPeak({ center: 530, fwhm: 2, amplitude: 8000 });
            const t = mk(5000, 200); tabManager.createTab('TGT', t.be, t.inten); const tgtId = tabManager.activeId;
            tabManager.activateTab(srcId); return { srcId, tgtId }; }""")
        pg.evaluate("() => showPropagateModal()")
        pg.evaluate("(id) => { const c = document.querySelector('.prop-chk[data-id=\"' + id + '\"]'); if (c) c.checked = true; }", ids["tgtId"])
        pg.evaluate("async () => { await runPropagation(); }")
        got = pg.evaluate(ONLY_SEAL, "TGT")
        assert got == {"keys": ["seal"], "frozen": True, "producer": "batch", "engine": "local", "record": True}, got
    finally:
        pg.close()


def _autofit_page(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1200, "height": 900})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    pg.set_input_files("#load-session-input", AUTOFIT_PROJECT)
    pg.wait_for_function("() => tabManager.tabs.some(t => t.name === 'C1s Scan')", timeout=60000)
    pg.evaluate("() => tabManager.activateTab(tabManager.tabs.find(t => t.name === 'C1s Scan').id)")
    pg.evaluate("() => { window._showAutoFitConfirmModal = () => Promise.resolve(true); }")
    pg.evaluate("() => { window.__n = []; const o = notify; window.notify = (m, k) => { window.__n.push(String(m)); return o(m, k); }; }")
    return pg


BEFORE = """() => ({ peaks: JSON.stringify(state.peaks), fit: state.fitResult === null ? null : JSON.stringify(state.fitResult),
                     cc: [document.getElementById('cc-method').value, document.getElementById('cc-obs').value, document.getElementById('cc-lit').value] })"""


def test_auto_fit_installs_only_a_fit_both_checks_confirmed(browser, server):  # noqa: F811
    pg = _autofit_page(browser, server)
    try:
        calls = _verify_calls(pg)
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        got = pg.evaluate(ONLY_SEAL, None)
        assert got == {"keys": ["seal"], "frozen": True, "producer": "autoFit", "engine": "server", "record": True}, got
        # CURRENT the moment it is installed: both checks answered before the commit, nothing asked since
        assert pg.evaluate(STATE) == ["current", None]
        assert len(calls) == 2, calls                        # the anchor fit and the final fit
        pg.evaluate(SETTLE)
        assert len(calls) == 2, calls
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


@pytest.mark.parametrize("answer,words", [
    ("abort", "could not be reached"),
    ("mismatch", "the server's check of its fits failed"),
])
def test_auto_fit_that_cannot_be_confirmed_changes_nothing(browser, server, answer, words):  # noqa: F811
    pg = _autofit_page(browser, server)
    try:
        before = pg.evaluate(BEFORE)
        if answer == "abort":
            pg.route("**/api/verify-fit", lambda route: route.abort())
        else:
            body = json.dumps({"state": "mismatch", "check": "statistics", "reason": "the recomputed statistics differ",
                               "software": pg.evaluate("() => _pageIdentity().software")})
            pg.route("**/api/verify-fit", lambda route: route.fulfill(status=200, content_type="application/json", body=body))
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        assert pg.evaluate(BEFORE) == before                 # the model, the result and the charge correction as they were
        assert any(words in m for m in pg.evaluate("() => window.__n")), pg.evaluate("() => window.__n")
        assert pg.errors == [], pg.errors
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_a_stale_sealed_spectrum_file_writes_the_current_models_curves(browser, server):  # noqa: F811
    """Q5 / F1 (plan §5: STALE is a live recompute): the convenience arrays of a stale sealed fit's spectrum file are
    exactly what a save of the same workspace with no fit writes — the areas Results shows, the fitted curve matching
    its residuals — while the seal (the record) travels unchanged beside them."""
    pg = _page(browser, server)
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        pg.evaluate("async () => { await runFit(); }")
        pg.evaluate(SETTLE)
        pg.evaluate("() => { state.peaks[0].amplitude *= 1.3; updatePlot(); }")
        assert pg.evaluate(STATE) == ["stale", "edited"]
        cap = """async () => { let out = null; const o = window._downloadBlob;
            window._downloadBlob = async (blob, name) => { out = JSON.parse(await blob.text()); };
            document.getElementById('save-fname').value = 's'; await _doSaveSpectrum();
            for (let k = 0; k < 400 && out === null; k++) await new Promise(r => setTimeout(r, 25)); window._downloadBlob = o; return out; }"""
        sealed = pg.evaluate(cap)
        seal = pg.evaluate("() => JSON.parse(JSON.stringify(state.fitResult.seal))")
        pg.evaluate("() => { state.fitResult = null; tabManager._syncActiveToRecord(); updatePlot(); }")
        nofit = pg.evaluate(cap)
    finally:
        pg.close()
    for k in ("roiBE", "fitCounts", "background", "backgroundFailure", "fittedY", "residuals", "peakCurves"):
        assert sealed[k] == nofit[k], k
    assert sealed["seal"] == seal
    st = sealed["statistics"]
    assert st["statisticsState"] == "stale" and "chiReduced" not in st and "chi" not in st, st


def test_every_page_call_of_the_local_engine_seals_its_result():
    """runFitLocal installs a legacy result only when called without `options.seal` — the JS harnesses do; the page
    never does (Run Fit's fallback and Batch Fit pass their samples and context)."""
    import re
    src = open(os.path.join(ROOT, "templates/index.html"), encoding="utf-8").read()
    calls = [m.start() for m in re.finditer(r"(?<!function )runFitLocal\(", src)]
    assert len(calls) == 2, len(calls)
    for at in calls:
        body = src[at:src.index(");", at)]
        assert re.search(r"\bseal: \{ producer: '(local|batch)'", body), body[:200]


# ── the legacy census (plan §11): every committed saved fit is LEGACY ──────────────────────────────────────────────

def _committed_projects():
    return sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip")))


def test_every_committed_saved_fit_loads_legacy_and_re_saves_without_a_seal(browser, server):  # noqa: F811
    """The 121 spectrum tabs with a saved fit in the committed projects: none carries a seal, each loads through the
    legacy adapter (a restored fit reads LEGACY; one dropped to peaks only keeps its record as provenance where it is
    well formed), and a re-save writes no seal anywhere. scripts/seal_legacy_census.py compares the re-save with
    main's, field by field."""
    files = _committed_projects()
    n_fit = 0
    for f in files:
        with zipfile.ZipFile(f) as z:
            manifest = json.loads(z.read("manifest.json"))
            tabs = [json.loads(z.read(s["filename"])) for s in manifest.get("spectra", [])]
        assert not any("seal" in (t.get("fitResult") or {}) for t in tabs), f
        fitted = {t.get("name") for t in tabs if not t.get("isStack") and t.get("fitResult")}
        n_fit += len(fitted)
        pg = _page(browser, server)
        try:
            with open(f, "rb") as fh:
                b64 = __import__("base64").b64encode(fh.read()).decode()
            pg.evaluate("""async ([b64, name]) => { const s = atob(b64), b = new Uint8Array(s.length);
                for (let i = 0; i < s.length; i++) b[i] = s.charCodeAt(i);
                await _loadZipProject(new File([b], name)); }""", [b64, os.path.basename(f)])
            got = pg.evaluate("""(names) => tabManager.tabs.filter(t => !t.isStack && names.includes(t.name)).map(t => {
                const fr = t === _activeTab() ? state.fitResult : t.fitResult;
                return { name: t.name, fit: !!fr, sealed: !!(fr && Object.hasOwn(fr, 'seal')),
                         state: fr ? sealedState(fr, t).state : null }; })""", sorted(fitted))
            assert len(got) == len(fitted), (f, got)
            for g in got:
                assert not g["sealed"] and (g["state"] == "legacy" or not g["fit"]), (f, g)
            saved = pg.evaluate("""async () => { let out = null; const o = window._downloadBlob;
                window._downloadBlob = async (blob, name) => { out = { name, b: Array.from(new Uint8Array(await blob.arrayBuffer())) }; };
                document.getElementById('save-fname').value = 'p'; await _doSaveProject();
                for (let k = 0; k < 400 && out === null; k++) await new Promise(r => setTimeout(r, 25)); window._downloadBlob = o; return out; }""")
            raw = bytes(saved["b"])
            if saved["name"].endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    texts = [z.read(n).decode() for n in z.namelist()]
            else:
                texts = [raw.decode()]
            assert not any('"seal"' in t for t in texts), f
            assert pg.errors == [], (f, pg.errors)
        finally:
            pg.close()
    assert n_fit == 121, n_fit


# ── Codex step 7 round 1: the lifecycle ───────────────────────────────────────────────────────────────────────────

def _hold(pg, pattern):
    """Requests to `pattern` are HELD while hold[0] (released with release()); otherwise they go through."""
    held, hold = [], [True]

    def handler(route):
        if hold[0]:
            held.append(route)
        else:
            route.continue_()
    pg.route(pattern, handler)

    def release():
        hold[0] = False
        for r in held:
            try:
                r.continue_()
            except Exception:
                pass
    return held, release


def _until(pg, cond, timeout_ms=60000):
    for _ in range(timeout_ms // 100):
        if cond():
            return True
        pg.wait_for_timeout(100)
    return cond()


def test_a_fit_whose_check_is_discarded_by_a_failed_newer_fit_is_still_confirmed(browser, server):  # noqa: F811
    """Run Fit A installs its seal with its check in flight; Run Fit B claims the tab and fails on the server (A's
    result stays). A's producer-bound reply is not B's operation's to attach — a background check takes over, so A
    reaches CURRENT with nothing else asked of the page."""
    pg = _page(browser, server)
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        held, release = _hold(pg, "**/api/verify-fit")
        pg.evaluate("async () => { await runFit(); window.__a = state.fitResult.seal; }")
        assert _until(pg, lambda: len(held) == 1), held
        pg.route("**/api/fit/start", lambda route: route.fulfill(status=500, content_type="application/json", body='{"error": "boom"}'))
        pg.evaluate("async () => { await runFit(); }")
        assert pg.evaluate("() => state.fitResult.seal === window.__a")          # B failed: A's result kept
        pg.unroute("**/api/fit/start")
        release()
        pg.wait_for_function("() => sealedState(state.fitResult, _activeTab()).state === 'current'", timeout=30000)
        assert pg.errors == [], pg.errors
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_cancel_during_auto_fits_confirmation_restores_at_once(browser, server):  # noqa: F811
    pg = _autofit_page(browser, server)
    try:
        before = pg.evaluate(BEFORE)
        held, release = _hold(pg, "**/api/verify-fit")
        pg.evaluate("() => { window.__af = runAutoFitC1sGraphite(); }")
        assert _until(pg, lambda: len(held) == 2, 120000), len(held)              # both staged checks in flight
        pg.evaluate("() => { window.__afDone = false; window.__af.then(() => { window.__afDone = true; }); }")
        pg.evaluate("() => document.getElementById('autofit-busy-cancel').click()")
        pg.wait_for_function("() => window.__afDone", timeout=15000)              # ends at once, without any reply
        got = pg.evaluate("""() => ({ overlay: document.getElementById('autofit-busy-overlay').style.display,
                                      txn: _stagedTxns.has(_activeTab()), n: window.__n })""")
        assert pg.evaluate(BEFORE) == before
        assert got["overlay"] == "none" and not got["txn"], got
        assert any("Auto-fit cancelled" in m for m in got["n"]), got["n"]
        release()
        pg.wait_for_timeout(500)
        assert pg.evaluate(BEFORE) == before                                     # a late reply changes nothing
        assert pg.errors == [], pg.errors
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_auto_fit_whose_final_check_alone_mismatches_publishes_nothing_and_ends_its_transaction(browser, server):  # noqa: F811
    pg = _autofit_page(browser, server)
    try:
        before = pg.evaluate(BEFORE)
        body = json.dumps({"state": "mismatch", "check": "statistics", "reason": "the recomputed statistics differ",
                           "software": pg.evaluate("() => _pageIdentity().software")})
        n = [0]

        def handler(route):
            n[0] += 1
            if n[0] == 2:                                   # the anchor fit's check goes first (sent while the final fit runs)
                route.fulfill(status=200, content_type="application/json", body=body)
            else:
                route.continue_()
        pg.route("**/api/verify-fit", handler)
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        assert n[0] == 2, n
        assert pg.evaluate(BEFORE) == before
        assert pg.evaluate("() => _stagedTxns.has(_activeTab())") is False
        assert any("the server's check of its fits failed" in m for m in pg.evaluate("() => window.__n"))
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()


def test_an_auto_fit_rolled_back_on_an_inactive_tab_re_verifies_the_seal_it_reinstalls(browser, server):  # noqa: F811
    pg = _autofit_page(browser, server)
    try:
        # the tab's own sealed fit, not yet checked (a reloaded fit's case)
        pg.evaluate("async () => { await runFit(); }")
        pg.evaluate(SETTLE)
        pg.evaluate("""() => { const s = state.fitResult.seal; _sealVerdicts.delete(s); _sealUnreachable.delete(s);
            window.__tab = _activeTab(); window.__seal = s; }""")
        held, release = _hold(pg, "**/api/verify-fit")
        pg.evaluate("() => { window.__af = runAutoFitC1sGraphite(); }")
        assert _until(pg, lambda: len(held) == 2, 120000), len(held)
        pg.evaluate("() => { tabManager.createTab('OTHER', state.rawBE.slice(), state.rawIntensity.slice()); }")
        release()
        pg.evaluate("async () => { await window.__af; }")
        assert pg.evaluate("() => window.__tab.fitResult.seal === window.__seal")       # rolled back into the record
        pg.wait_for_function("() => sealedState(window.__tab.fitResult, window.__tab).state === 'current'", timeout=30000)
        assert pg.evaluate("() => _activeTab() !== window.__tab")                       # with no activation
    finally:
        pg.unroute_all(behavior="ignoreErrors")
        pg.close()
