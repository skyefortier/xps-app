"""Seal 1c step 4 (plan docs/superpowers/plans/2026-10-14-seal-1c-page.md §2-§6, §9, §11): JUDGING a seal —
`sealedState` from the page's bindings, the live binding, the local engine's own exact check and the server's
verification, with the verification manager's ownership rules. Behind the switch (nothing reads it yet), so these
tests call it directly on real fits made by the real page and server.

Skips cleanly when Playwright / Chromium / gunicorn are absent.
"""
import json

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
        # a NEWER operation claims the tab while the producer-bound reply is in flight: discarded; a background
        # attempt recovers
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), seal = state.fitResult.seal;
            const op = _claimFitOp(owner);
            const p = _verifySeal(owner, seal, 'producer', op);
            const newer = _claimFitOp(owner);
            const r = await p;
            const out = [r, _fitOpCurrent(op), _fitOpCurrent(newer), sealedState(state.fitResult, owner).state, _sealVerdicts.has(seal)];
            await _ensureVerified(owner);
            return [...out, sealedState(state.fitResult, owner).state]; }""")
        assert got == [None, False, True, "pending", False, "current"], got
        # a TAB SWITCH while it is in flight (the operation still current): discarded, re-verified on return
        pg.evaluate("() => { const s = state.fitResult.seal; state.fitResult = { ...state.fitResult, seal: _makeSeal(structuredClone(s)) }; }")
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), seal = state.fitResult.seal;
            const op = _claimFitOp(owner);
            const p = _verifySeal(owner, seal, 'producer', op);
            tabManager.createTab('B', state.rawBE.slice(), state.rawIntensity.slice());
            const r = await p;
            const out = [r, _fitOpCurrent(op), sealedState(owner.fitResult, owner).state];
            tabManager.activateTab(owner.id);
            await _ensureVerified(owner);
            return [...out, sealedState(state.fitResult, owner).state]; }""")
        assert got == [None, True, "pending", "current"], got
    finally:
        pg.close()


def test_a_reply_for_a_replaced_seal_or_a_reused_tab_id_is_discarded(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), seal = state.fitResult.seal;
            const p = _verifySeal(owner, seal, 'background');
            const other = _makeSeal(structuredClone(seal));
            state.fitResult = { ...state.fitResult, seal: other };          // another seal installed meanwhile
            const r = await p;
            return [r, _sealVerdicts.has(seal), _sealVerdicts.has(other), sealedState(state.fitResult, owner).state]; }""")
        assert got == [None, False, False, "pending"], got
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), seal = state.fitResult.seal, id = owner.id;
            const raw = state.rawBE.slice(), inten = state.rawIntensity.slice(), peaks = structuredClone(state.peaks);
            const p = _verifySeal(owner, seal, 'background');
            tabManager.closeTab(id);
            const t2 = tabManager.createTab('again', raw, inten);
            t2.id = id; tabManager.activeId = id;                           // a NEW record under the SAME id
            state.peaks = peaks; state.fitResult = { seal };
            const r = await p;
            return [r, _sealVerdicts.has(seal), sealedState(state.fitResult, t2).state]; }""")
        assert got[:2] == [None, False] and got[2] != "current", got   # discarded (its controls are the new tab's own)
    finally:
        pg.close()


def test_a_background_check_never_claims_the_fit_operation(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), op = _claimFitOp(owner);
            await _verifySeal(owner, state.fitResult.seal, 'background');
            return [_fitOpCurrent(op), sealedState(state.fitResult, owner).state]; }""")
        assert got == [True, "current"], got
    finally:
        pg.close()


def test_check_again_always_starts_a_new_attempt(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        import json as _json
        pg.route("**/api/verify-fit", lambda route: route.fulfill(status=200, content_type="application/json",
                 body=_json.dumps({"state": "unconfirmed", "check": "numerics", "reason": "made under other numerics and the recomputation differs"})))
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == ["unconfirmed", "numerics"]
        pg.unroute("**/api/verify-fit")
        calls = []
        pg.on("request", lambda r: calls.append(r.url) if r.url.endswith("/api/verify-fit") else None)
        pg.evaluate(VERIFY)                                 # a background trigger: the answer is cached
        assert calls == [] and pg.evaluate(STATE) == ["unconfirmed", "numerics"]
        pg.evaluate("async () => { await _ensureVerified(_activeTab(), true); }")   # "check again"
        assert len(calls) == 1 and pg.evaluate(STATE) == ["current", None], calls
        # an unreachable server on "check again" leaves the cached answer in place
        pg.route("**/api/verify-fit", lambda route: route.abort())
        pg.evaluate("async () => { await _ensureVerified(_activeTab(), true); }")
        assert pg.evaluate(STATE) == ["current", None]
    finally:
        pg.close()


def test_a_negative_zero_sample_is_the_value_the_server_received(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    try:
        pg.goto(server + "/", wait_until="load")
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        # a spectrum whose energies cross zero exactly as -0 would need a shifted axis; a count of -0 is direct
        pg.evaluate("""() => { const i = state.rawIntensity.findIndex((v, k) => k > 2); state.rawIntensity[i] = -0;
                              const t = _activeTab(); if (t) t.rawIntensity = state.rawIntensity; }""")
        pg.evaluate("async () => { await runFit(); }")
        assert pg.evaluate("() => state.fitResult.seal.R.counts.some(v => Object.is(v, -0))")
        assert pg.evaluate("() => state.fitResult.seal.O.counts.every(v => !Object.is(v, -0))")
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == ["current", None]
        # a record stored and read back (JSON) is the same record
        pg.evaluate("() => { const s = JSON.parse(JSON.stringify(state.fitResult.seal)); state.fitResult = { ...state.fitResult, seal: _makeSeal(s) }; }")
        assert pg.evaluate("() => sealedState(state.fitResult, _activeTab()).state") == "pending"
    finally:
        pg.close()


def test_raw_data_edited_in_place_is_new_data(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == ["current", None]
        pg.evaluate("() => { const i = _sealView(state.fitResult.seal) && state.fitResult.seal.R.idx[3]; state.rawIntensity[i] += 1; }")
        assert pg.evaluate(STATE) == ["stale", "samples"]
    finally:
        pg.close()


INV = "const inv = (s) => { s.O.paramMap = _localInventory(structuredClone(s.R.pageModel)).paramMap; }; "


@pytest.mark.parametrize("src,checks", [
    ("s.O.energies[0] += 1e-9", ("samples",)),
    ("s.O.net[0] += 1e-9", ("samples",)),
    # each substitution made CONSISTENT everywhere but the values: the inventory is rebuilt from the substituted
    # start model, so only the projection (structure from R, free values from the engine) can catch it
    (INV + "s.R.pageModel[0].fixCenter = !s.R.pageModel[0].fixCenter; s.O.model[0].fixCenter = s.R.pageModel[0].fixCenter; inv(s)",
     ("model",)),                                                                 # a lock substituted
    (INV + "for (const m of [s.R.pageModel, s.O.model]) { m[1].shape = m[0].shape; m[1].linked = m[0].id; m[1].linkOffset = 1; m[1].linkRatio = 0.5; } inv(s)",
     ("model",)),                                                                 # a (valid) link substituted
    (INV + "s.R.pageModel[0].fixFwhm = true; s.O.model[0].fixFwhm = true; s.O.model[0].fwhm = s.R.pageModel[0].fwhm + 0.01; inv(s)",
     ("model",)),                                                                 # a held value moved
])
def test_a_local_record_that_does_not_hold_together_is_stale(browser, server, src, checks):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1500, "height": 950})
    try:
        pg.goto(server + "/", wait_until="load")
        _setup(pg, SCENARIOS["gauss_voigt_linear_avg3_window"])
        pg.route("**/api/upload", lambda route: route.abort())
        pg.evaluate("async () => { await runFit(); }")
        assert pg.evaluate("() => state.fitResult.seal.engine") == "local"
        st = pg.evaluate("(src) => { const s = structuredClone(state.fitResult.seal); (new Function('s', src))(s);"
                         " const r = sealedState({ seal: _makeSeal(s) }, _activeTab()); return [r.state, r.check]; }", src)
        assert st[0] == "stale" and st[1] in checks, (src, st)
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


def _autofitted(browser, server):  # noqa: F811
    pg = browser.new_page(viewport={"width": 1200, "height": 900})
    pg.goto(server + "/", wait_until="load")
    pg.set_input_files("#load-session-input", AUTOFIT_PROJECT)
    pg.wait_for_function("() => tabManager.tabs.some(t => t.name === 'C1s Scan')", timeout=60000)
    pg.evaluate("() => tabManager.activateTab(tabManager.tabs.find(t => t.name === 'C1s Scan').id)")
    pg.evaluate("() => { window._showAutoFitConfirmModal = () => Promise.resolve(true); }")
    pg.evaluate("async () => { await runAutoFitC1sGraphite(); }")
    assert pg.evaluate("() => state.fitResult.seal.producer") == "autoFit"
    return pg


@pytest.mark.parametrize("src,check", [
    # the final fit made WITHOUT the anchor check (the request consistent with it): not the anchor fit's settings
    ("s.R.context0.producer.require_component = null; s.R.request.require_component = null", "evidence"),
    # both fits asked about a component that is not the anchor
    ("for (const r of [s.E.R, s.R]) { r.context0.producer.require_component = 'nope'; r.request.require_component = 'nope'; }", "evidence"),
])
def test_auto_fit_evidence_must_be_the_same_producer_on_the_same_spectrum(browser, server, src, check):  # noqa: F811
    pg = _autofitted(browser, server)
    try:
        st = pg.evaluate("(src) => { const s = structuredClone(state.fitResult.seal); (new Function('s', src))(s);"
                         " const r = sealedState({ seal: _makeSeal(s) }, _activeTab()); return [r.state, r.check]; }", src)
        assert st == ["stale", check], (src, st)
    finally:
        pg.close()


def test_auto_fit_evidence_from_another_spectrum_is_stale(browser, server):  # noqa: F811
    pg = _autofitted(browser, server)
    try:
        # the anchor fit's R and O are coherent with each other but NOT with this spectrum: the raw data change
        # where only the anchor fit sampled (its window, before the charge shift moved it)
        got = pg.evaluate("""() => { const s = state.fitResult.seal, only = s.E.R.idx.filter(i => !s.R.idx.includes(i));
            if (!only.length) return null;
            state.rawIntensity[only[0]] += 1;
            const r = sealedState(state.fitResult, _activeTab()); return [r.state, r.check]; }""")
        assert got == ["stale", "evidence"], got
    finally:
        pg.close()


def _route_by_fit(pg, actions):
    """Route /api/verify-fit by WHICH fit is checked (the anchor fit E or the final fit R), via the reply's digest.
    actions: {'E': a, 'R': a}, a in 'continue' | 'abort' | 'hold' | dict (a reply body)."""
    import json as _json
    dig = pg.evaluate("() => ({ E: state.fitResult.seal.E.O.request_digest, R: state.fitResult.seal.O.request_digest })")
    held = []

    def handle(route):
        which = "E" if _json.loads(route.request.post_data)["O"]["request_digest"] == dig["E"] else "R"
        a = actions[which]
        if a == "continue":
            route.continue_()
        elif a == "abort":
            route.abort()
        elif a == "hold":
            held.append(route)
        else:
            route.fulfill(status=200, content_type="application/json", body=_json.dumps(a))
    pg.route("**/api/verify-fit", handle)
    return held


MISMATCH = {"state": "mismatch", "check": "components", "reason": "test mismatch"}
OTHER_NUMERICS = {"state": "unconfirmed", "check": "numerics", "reason": "made under other numerics and the recomputation differs"}


@pytest.mark.parametrize("actions,expect", [
    ({"E": MISMATCH, "R": "abort"}, ["stale", "components"]),         # a mismatch is never hidden by an unreachable check
    ({"E": "abort", "R": MISMATCH}, ["stale", "components"]),
    ({"E": "abort", "R": "continue"}, ["unconfirmed", "unreachable"]),
    ({"E": OTHER_NUMERICS, "R": "continue"}, ["unconfirmed", "numerics"]),
    ({"E": "continue", "R": "continue"}, ["current", None]),
])
def test_auto_fit_aggregates_its_two_checks_by_precedence(browser, server, actions, expect):  # noqa: F811
    pg = _autofitted(browser, server)
    try:
        _route_by_fit(pg, actions)
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == expect, actions
    finally:
        pg.close()


def test_auto_fit_with_one_check_outstanding_is_pending_unless_the_other_is_a_mismatch(browser, server):  # noqa: F811
    pg = _autofitted(browser, server)
    try:
        held = _route_by_fit(pg, {"E": "hold", "R": "continue"})
        pg.evaluate("() => { window.__p = _ensureVerified(_activeTab()); }")
        pg.wait_for_function("() => true")
        pg.wait_for_timeout(1500)
        assert pg.evaluate(STATE) == ["pending", None]
        held[0].continue_()
        pg.evaluate("async () => { await window.__p; }")
        assert pg.evaluate(STATE) == ["current", None]
    finally:
        pg.close()
    pg = _autofitted(browser, server)
    try:
        held = _route_by_fit(pg, {"E": "hold", "R": MISMATCH})
        pg.evaluate("async () => { await _ensureVerified(_activeTab()); }")   # resolves on the mismatch alone
        assert pg.evaluate(STATE) == ["stale", "components"]
        for r in held:
            r.abort()
    finally:
        pg.close()


def test_auto_fit_with_an_unreachable_check_waits_for_the_outstanding_one(browser, server):  # noqa: F811
    for partner, expect in ((MISMATCH, ["stale", "components"]), ("continue", ["unconfirmed", "unreachable"])):
        pg = _autofitted(browser, server)
        try:
            held = _route_by_fit(pg, {"E": "abort", "R": "hold"})
            pg.evaluate("() => { window.__p = _ensureVerified(_activeTab()); }")
            pg.wait_for_timeout(1500)
            assert pg.evaluate(STATE) == ["pending", None]                # never UNCONFIRMED before the other answers
            if partner == "continue":
                held[0].continue_()
            else:
                held[0].fulfill(status=200, content_type="application/json", body=json.dumps(partner))
            pg.evaluate("async () => { await window.__p; }")
            assert pg.evaluate(STATE) == expect, partner
        finally:
            pg.close()


def test_check_again_supersedes_an_attempt_in_flight(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        held = []
        pg.route("**/api/verify-fit", lambda route: held.append(route))
        pg.evaluate("() => { window.__p1 = _ensureVerified(_activeTab()); }")
        pg.wait_for_timeout(500)
        pg.evaluate("() => { window.__p0 = _ensureVerified(_activeTab()); }")   # a background trigger: no second attempt
        pg.wait_for_timeout(500)
        assert len(held) == 1
        pg.evaluate("() => { window.__p2 = _ensureVerified(_activeTab(), true); }")   # "check again"
        pg.wait_for_timeout(500)
        assert len(held) == 2
        held[1].continue_()
        pg.evaluate("async () => { await window.__p2; }")
        assert pg.evaluate(STATE) == ["current", None]
        held[0].fulfill(status=200, content_type="application/json", body=json.dumps(MISMATCH))   # the superseded reply
        assert pg.evaluate("async () => await window.__p1") is None
        assert pg.evaluate(STATE) == ["current", None]
    finally:
        pg.close()


def test_staged_checks_resolve_only_their_current_transaction(browser, server):  # noqa: F811
    pg = _autofitted(browser, server)
    try:
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), seal = state.fitResult.seal;
            // superseded at the FIRST check: a newer operation claims the tab
            let op = _claimFitOp(owner), txn = _beginStaged(owner, op);
            let p = _verifyStagedCheck(txn, seal.E.R, seal.E.O);
            _claimFitOp(owner);
            const a = await p;
            // superseded at the SECOND check: a newer transaction (another Auto-Fit) on the tab
            op = _claimFitOp(owner); txn = _beginStaged(owner, op);
            const b1 = await _verifyStagedCheck(txn, seal.E.R, seal.E.O);
            p = _verifyStagedCheck(txn, seal.R, seal.O);
            _beginStaged(owner, op);
            const b2 = await p;
            const committedStale = _commitStaged(txn, seal);
            // a current transaction checks the PRODUCER'S objects (not yet a seal); the seal built from them
            // (_makeSeal: its own deep copy) takes both answers at the commit, with no further request
            const parts = structuredClone(seal);                                   // what a producer holds before sealing
            op = _claimFitOp(owner); txn = _beginStaged(owner, op);
            const c1 = await _verifyStagedCheck(txn, parts.E.R, parts.E.O), c2 = await _verifyStagedCheck(txn, parts.R, parts.O);
            const fresh = _makeSeal(parts);
            state.fitResult = { ...state.fitResult, seal: fresh };
            const pendingBefore = sealedState(state.fitResult, owner).state;
            let posts = 0; const f0 = window.fetch; window.fetch = (...a) => { if (String(a[0]).includes('verify-fit')) posts++; return f0(...a); };
            const committed = _commitStaged(txn, fresh);
            window.fetch = f0;
            return [a, b1 && b1.state, b2, committedStale.committed, c1.state, c2.state, pendingBefore, committed.committed,
                    committed.verdict.state, posts, sealedState(state.fitResult, owner).state]; }""")
        assert got == [None, "consistent", None, False, "consistent", "consistent", "pending", True, "consistent", 0, "current"], got
        # an object changed while its check was in flight: the answer is about what was SENT, and a seal made from
        # the changed object does not receive it
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), parts = structuredClone(state.fitResult.seal);
            const op = _claimFitOp(owner), txn = _beginStaged(owner, op);
            const p1 = _verifyStagedCheck(txn, parts.E.R, parts.E.O), p2 = _verifyStagedCheck(txn, parts.R, parts.O);
            parts.R.counts[0] = 999;
            const v = [(await p1).state, (await p2).state];
            const changed = _makeSeal(parts);
            return [...v, _commitStaged(txn, changed).committed, _sealVerdicts.has(changed)]; }""")
        assert got == ["consistent", "consistent", False, False], got
        # a tab switch during a staged check: superseded
        got = pg.evaluate("""async () => {
            const owner = _activeTab(), seal = state.fitResult.seal, op = _claimFitOp(owner), txn = _beginStaged(owner, op);
            const p = _verifyStagedCheck(txn, seal.R, seal.O);
            tabManager.createTab('B', state.rawBE.slice(), state.rawIntensity.slice());
            return [await p, _commitStaged(txn, seal).committed]; }""")
        assert got == [None, False], got
    finally:
        pg.close()


# Owner 2026-10-15: a seal from another deployment is confirmed by recomputation — its commit, checkout state and
# environment are information only (the real server recomputes the record).
@pytest.mark.parametrize("src", [
    "s.O.software.git_commit = 'f'.repeat(40); s.O.software.git_dirty = true; s.O.software.env_sha256 = '0'.repeat(64)",
    "s.O.software.numerics = '2026-10-09'",                          # other numerics, recomputing exactly
])
def test_a_seal_from_another_deployment_is_current_when_it_recomputes(browser, server, src):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate(TAMPER, src)
        pg.evaluate(VERIFY)
        assert pg.evaluate(STATE) == ["current", None], src
    finally:
        pg.close()


def test_a_seal_from_other_numerics_that_recomputes_differently_is_unconfirmed(browser, server):  # noqa: F811
    pg = _fitted(browser, server)
    try:
        pg.evaluate(TAMPER, "s.O.software.numerics = '2026-10-09'; s.O.fitted_y[3] += 1e-6")
        pg.evaluate(VERIFY)
        st = pg.evaluate("() => { const s = sealedState(state.fitResult, _activeTab()); return [s.state, s.check, s.reason]; }")
        assert st[:2] == ["unconfirmed", "numerics"] and "2026-10-09" in st[2], st
    finally:
        pg.close()
