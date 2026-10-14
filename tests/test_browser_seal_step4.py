"""Seal 1c step 4 (plan docs/superpowers/plans/2026-10-14-seal-1c-page.md §2-§6, §9, §11): JUDGING a seal —
`sealedState` from the page's bindings, the live binding, the local engine's own exact check and the server's
verification, with the verification manager's ownership rules. Behind the switch (nothing reads it yet), so these
tests call it directly on real fits made by the real page and server.

Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import pytest

pytest.importorskip("playwright.sync_api")

from test_browser_bg_window_request import browser, server  # noqa: F401,E402
from test_browser_seal_requests import SCENARIOS, _setup, AUTOFIT_PROJECT  # noqa: E402

STATE = "() => { const s = sealedState(state.fitResult, _activeTab()); return [s.state, s.check]; }"
VERIFY = "async (retry) => { await _ensureVerified(_activeTab(), !!retry); }"
# install a modified copy of the current seal (structuredClone unfreezes; _makeSeal freezes again)
TAMPER = """(src) => { const s = structuredClone(state.fitResult.seal); (new Function('s', src))(s);
  state.fitResult = { ...state.fitResult, seal: _makeSeal(s) }; }"""


def _fitted(browser, server, scenario="asymgl_linked_smart"):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)))
    pg.goto(server + "/", wait_until="load")
    _setup(pg, SCENARIOS[scenario])
    pg.evaluate("async () => { await runFit(); }")
    return pg


def test_a_fresh_server_fit_is_pending_then_current_and_a_presentation_edit_changes_nothing(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        assert pg.evaluate(STATE) == ["pending", None]
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == ["current", None]
        pg.evaluate("() => { state.peaks[0].name = 'renamed'; state.peaks[0].color = '#123456'; state.peaks[1].visible = false; }")
        assert pg.evaluate(STATE) == ["current", None]
        assert pg.errors == [], pg.errors
    finally:
        pg.close()


@pytest.mark.parametrize("edit,undo", [
    ("state.peaks[0].center += 0.01", "state.peaks[0].center -= 0.01"),
    ("state.peaks[1].fixCenter = !state.peaks[1].fixCenter", "state.peaks[1].fixCenter = !state.peaks[1].fixCenter"),
    ("document.getElementById('fit-method').value = 'leastsq'", "document.getElementById('fit-method').value = 'least_squares'"),
    ("document.getElementById('bg-type').value = 'linear'", "document.getElementById('bg-type').value = 'smart'"),
    ("document.getElementById('cc-method').value = 'custom'; document.getElementById('cc-obs').value = '284.8'; document.getElementById('cc-lit').value = '284.8'",
     "document.getElementById('cc-method').value = 'none'; document.getElementById('cc-obs').value = ''; document.getElementById('cc-lit').value = ''"),
    ("document.getElementById('bg-endpoint-avg').value = '1e0'", "document.getElementById('bg-endpoint-avg').value = '3'"),
])
def test_an_edit_of_the_model_or_its_context_is_stale_and_its_reversal_current_again(browser, server, edit, undo):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate(VERIFY)
        before = pg.evaluate("() => _sealLiveKey(_activeTab())")
        pg.evaluate("() => { " + edit + "; }")
        assert pg.evaluate(STATE) == ["stale", "edited"], edit
        pg.evaluate("() => { " + undo + "; }")
        assert pg.evaluate("() => _sealLiveKey(_activeTab())") == before
        assert pg.evaluate(STATE) == ["current", None], undo
    finally:
        pg.close()


def test_unreachable_is_unconfirmed_until_check_again(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.route("**/api/verify-fit", lambda route: route.abort())
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == ["unconfirmed", "unreachable"]
        pg.unroute("**/api/verify-fit")
        pg.evaluate(VERIFY)                       # a background trigger does not retry by itself
        assert pg.evaluate(STATE) == ["unconfirmed", "unreachable"]
        pg.evaluate("async () => { await _ensureVerified(_activeTab(), true); }")   # "check again"
        assert pg.evaluate(STATE) == ["current", None]
    finally:
        pg.close()


@pytest.mark.parametrize("src,state,check", [
    ("s.O.statistics.chi_square *= 1.000001", "stale", "statistics"),               # the server's check fails
    ("s.O.individual_peaks[0].y[3] += 1e-6", "stale", "components"),
    ("s.R.request.fit_method = 'nelder'", "stale", "request"),                       # step 0 (the page)
    ("s.R.idx = s.R.idx.slice(1); s.R.energies = s.R.energies.slice(1); s.R.counts = s.R.counts.slice(1)", "stale", "samples"),
    ("s.O.background_y[2] += 1e-9", "stale", "background"),
    ("s.R.context0.live.ccShift = NaN", "stale", "context"),
    ("s.v = 'something else'", "peaks-only", "schema"),
])
def test_a_record_that_does_not_hold_together_is_never_current(browser, server, src, state, check):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate(TAMPER, src)
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == [state, check], src
    finally:
        pg.close()


def test_a_seal_installed_on_another_spectrum_is_stale(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate("""() => { const seal = state.fitResult.seal;
            const raw = state.rawBE.slice(), inten = state.rawIntensity.map(v => v * 1.01);
            tabManager.createTab('other spectrum', raw, inten);
            state.peaks = structuredClone(seal.R.pageModel); state.fitResult = { seal }; }""")
        assert pg.evaluate(STATE) == ["stale", "samples"]
    finally:
        pg.close()


def test_the_local_engine_is_its_own_exact_check(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    pg.goto(server + "/", wait_until="load")
    try:
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        pg.route("**/api/upload", lambda route: route.abort())
        pg.evaluate("async () => { await runFit(); }")
        assert pg.evaluate("() => state.fitResult.seal.engine") == "local"
        assert pg.evaluate(STATE) == ["current", None]
        for src, check in (("s.O.model[0].shape = 'Lorentzian'", "model"), ("s.O.chi2 *= 1.0000001", "statistics"),
                           ("s.O.weights[4] *= 1.0000001", "weights"), ("s.O.paramMap.pop()", "inventory"),
                           ("s.O.curves[0][10] += 1e-9", "components"), ("s.O.support = {}", "support")):
            st = pg.evaluate("(src) => { const s = structuredClone(state.fitResult.seal); (new Function('s', src))(s);"
                             " const r = sealedState({ seal: _makeSeal(s) }, _activeTab()); return [r.state, r.check]; }", src)
            assert st == ["stale", check], (src, st)
    finally:
        pg.close()


def test_auto_fit_is_current_only_with_both_checks_and_its_evidence(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1200, "height": 900})
    try:
        pg.goto(server + "/", wait_until="load")
        pg.set_input_files("#load-session-input", AUTOFIT_PROJECT)
        pg.wait_for_function("() => tabManager.tabs.some(t => t.name === 'C1s Scan')", timeout=60000)
        pg.evaluate("() => tabManager.activateTab(tabManager.tabs.find(t => t.name === 'C1s Scan').id)")
        pg.evaluate("() => { window._showAutoFitConfirmModal = () => Promise.resolve(true); }")
        pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
        calls = []
        pg.on("request", lambda r: calls.append(r.url) if r.url.endswith("/api/verify-fit") else None)
        assert pg.evaluate(STATE) == ["pending", None]
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == ["current", None]
        assert len(calls) == 2, calls                       # the anchor fit and the final fit
        for src, check in (("s.E.O.success = false", "evidence"), ("s.O.success = false", "acceptance"),
                           ("s.E.R.context0.live.bgType = 'linear'", "evidence"),   # what the anchor request was built from
                           ("s.E.R.pageModel[0].fixFwhm = !s.E.R.pageModel[0].fixFwhm", "evidence")):
            st = pg.evaluate("(src) => { const s = structuredClone(state.fitResult.seal); (new Function('s', src))(s);"
                             " const r = sealedState({ seal: _makeSeal(s) }, _activeTab()); return [r.state, r.check]; }", src)
            assert st == ["stale", check], (src, st)
    finally:
        pg.close()


def test_a_producer_bound_reply_is_attached_only_under_its_operation_and_active_tab(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        # an operation that is no longer current: its reply is discarded, and a background trigger recovers
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), seal = state.fitResult.seal;
            const op = _newFitOp(owner); _installFitOp(owner, _newFitOp(owner));   // a newer operation on the tab
            await _verifySeal(owner, seal, 'producer', op);
            const after = sealedState(state.fitResult, owner).state;
            await _ensureVerified(owner);
            return [after, sealedState(state.fitResult, owner).state]; }""")
        assert got == ["pending", "current"], got
    finally:
        pg.close()


def test_a_reply_for_a_closed_tab_is_discarded_and_an_inactive_tab_is_judged_by_its_own_context(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        # judged by its own record: switch to another tab whose controls differ
        got = pg.evaluate("""async () => {
            const a = _activeTab(); await _ensureVerified(a);
            tabManager.createTab('B', state.rawBE.slice(), state.rawIntensity.slice());
            document.getElementById('fit-method').value = 'nelder';
            document.getElementById('bg-type').value = 'linear';
            return [sealedState(a.fitResult, a).state, a.ui.fitMethod, a.ui.bgType]; }""")
        assert got == ["current", "least_squares", "smart"], got
        # per-tab method: back on A, its own method is restored
        assert pg.evaluate("() => { tabManager.activateTab(tabManager.tabs[0].id); return document.getElementById('fit-method').value; }") == "least_squares"
        # a closed tab's reply is discarded without error
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), seal = state.fitResult.seal;
            const p = _verifySeal(owner, seal, 'background');
            tabManager.closeTab(owner.id);
            return await p; }""")
        assert got is None
    finally:
        pg.close()
