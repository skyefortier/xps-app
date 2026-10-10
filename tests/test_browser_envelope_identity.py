"""Real browser, real server (owner 2026-10-10): the envelope the page DRAWS is the background
it draws plus the sum of the components it draws — after a server fit, after the student edits
a peak, and with components locked at their bounds; for every lineshape. On a common x-grid
always. After an EDIT the page draws everything with its own arithmetic: the identity holds
to rounding (tests/envelope_identity.py). After a FIT the drawn envelope and background are
the server's arrays — required EXACTLY — the server's own identity holds to rounding, and
each drawn component (the page's JavaScript evaluator) equals the server's component curve
within the page-server PARITY tolerance, 1e-6 of its amplitude
(tests/js/lineshape_roundtrip.test.js TIGHT_TOL): two implementations of a formula, not a
rounding bound (tests/envelope_identity.py says why).

The 2026-09-17 report (an envelope above the sum of its components on a UCl4 spectrum) was
this identity broken: the page drew asym-GL with a width that grew with distance from the
centre while the server fitted a bounded one (fixed in cf4938d, 2026-08-31). Each case below
is also run with a real defect put back into the page and must then FAIL. The bound:
tests/envelope_identity.py. Skips cleanly when Playwright / Chromium / gunicorn are absent."""
import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import _new_page, browser, server  # noqa: E402,F401
from envelope_identity import conv_term, envelope_gap  # noqa: E402

# a U 4f-like spectrum; the shape under test on both main lines, a GL satellite, a Gaussian
TAB = """(shape) => {
    const g = (x, c, a, w) => a * Math.exp(-4 * Math.LN2 * ((x - c) / w) ** 2);
    const raw = [], inten = [];
    let s = 17; const rnd = () => (s = (s * 1103515245 + 12345) % 2147483648) / 2147483648;
    for (let i = 0; i < 300; i++) {
      const x = 370 + 0.1 * i; raw.push(x);
      const lam = 500 + 60 / (1 + Math.exp(-(x - 386) * 2)) + g(x, 380.9, 9000, 1.6) + g(x, 391.8, 6800, 1.6) + g(x, 384.5, 900, 2.5) + g(x, 396, 700, 2);
      inten.push(Math.round(lam + Math.sqrt(lam) * (rnd() + rnd() + rnd() - 1.5)));
    }
    tabManager.createTab('envelope ' + shape, raw, inten);
    document.getElementById('roi-min').value = ''; document.getElementById('roi-max').value = '';
    document.getElementById('bg-type').value = 'shirley'; _onBgTypeChange();
    document.getElementById('show-envelope').checked = true;
    document.getElementById('show-individual').checked = true;
    state.peaks = [];
    const sp = { 'GL': { glMix: 30 }, 'asym-GL': { glMix: 30, asymmetry: 0.35 }, 'DS': { dsAlpha: 0.15, dsGamma: 0.2 },
                 'DSG_LA': { laAlpha: 0.12, laBeta: 0.4, laM: 0.8 }, 'LACX': { caAlpha: 1.4, caBeta: 0.8, caM: 20 } }[shape] || {};
    addPeak({ name: 'A', center: 381.0, fwhm: 1.5, amplitude: 8000, shape, ...sp });
    addPeak({ name: 'B', center: 391.7, fwhm: 1.5, amplitude: 6000, shape, ...sp });
    addPeak({ name: 'sat', center: 384.4, fwhm: 2.5, amplitude: 800, shape: 'GL', glMix: 30 });
    addPeak({ name: 'g', center: 396.1, fwhm: 2.0, amplitude: 600, shape: 'Gaussian' });
    updatePlot();
}"""

FIT = """async () => {
    window.__n = [];
    const o = notify; window.notify = (m, k) => { window.__n.push(String(m)); return o(m, k); };
    await runFit();
    return { engine: state.fitResult && state.fitResult.engine, n: window.__n, have: !!state.fitResult };
}"""

# what the chart draws: the envelope ('Fit…'), the background and each component (drawn on it),
# with their x-coordinates; and the server's own arrays for the fit on show
DRAWN = """() => {
    const ds = state.chart.data.datasets;
    const env = ds.find(d => /^Fit/.test(d.label || ''));
    const bg = ds.find(d => d.label === 'Background');
    const comps = ds.filter(d => d._peakId !== undefined);
    const xs = d => d.data.map(p => p.x), ys = d => d.data.map(p => p.y);
    const b = ys(bg);
    const br = state.fitResult && state.fitResult.backendResult;
    // as DRAWN means visible (Codex round 3: Chart.js hides a dataset by its `hidden` flag or its
    // metadata; isDatasetVisible reads both) — a hidden component is not on the chart
    const vis = d => state.chart.isDatasetVisible(ds.indexOf(d));
    return { visible: { env: vis(env), bg: vis(bg), comps: comps.map(vis) },
             envX: xs(env), bgX: xs(bg), compX: comps.map(xs),
             env: ys(env), bg: b, comps: comps.map(c => ys(c).map((v, i) => v - b[i])),
             ids: comps.map(c => String(c._peakId)), amps: comps.map(c => state.peaks.find(p => p.id === c._peakId).amplitude),
             server: br ? { fitted_y: br.fitted_y, background_y: br.background_y,
                            peaks: br.individual_peaks.map(p => ({ id: String(p.id), shape: p.shape, y: p.y, params: p.params })) } : null,
             stats: _statsLiveState() };
}"""

SHAPES = ["Gaussian", "Lorentzian", "Voigt", "GL", "asym-GL", "DS", "DSG_LA", "LACX"]


PARITY = 1e-6        # of a component's amplitude: tests/js/lineshape_roundtrip.test.js TIGHT_TOL


def _same_grid(d):
    # (every fixture here shows every component: a peak the student hides is a display choice,
    # outside this identity — so a hidden one here is a defect)
    v = d["visible"]
    assert v["env"] and v["bg"] and all(v["comps"]), f"not every curve is visible on the chart: {v}"
    assert d["bgX"] == d["envX"] and all(x == d["envX"] for x in d["compX"]), "the drawn curves are not on one x-grid"


def _edited_gap(d):
    """After an edit: all of it the page's own arithmetic — the summation bound."""
    _same_grid(d)
    return envelope_gap(d["env"], d["bg"], d["comps"])


def _check_fitted(d, label):
    """After a server fit: the drawn envelope and background ARE the server's; the server's own
    identity holds to rounding; each drawn component is the server's within parity."""
    _same_grid(d)
    sv = d["server"]
    assert sv is not None, "a server fit is on show"
    assert d["env"] == sv["fitted_y"], f"{label}: the drawn envelope is not the server's fitted_y"
    assert d["bg"] == sv["background_y"], f"{label}: the drawn background is not the server's background_y"
    extra = sum((conv_term(p["y"], p["params"]["m"]["value"]) for p in sv["peaks"] if p["shape"] == "la_casaxps"), 0.0)
    ratio, rel = envelope_gap(sv["fitted_y"], sv["background_y"], [p["y"] for p in sv["peaks"]], extra)
    assert ratio <= 1.0, f"{label}: the server's own envelope is not its background plus components ({ratio:.3g} x rounding)"
    # each drawn component (dataset − background, so recovering it rounds by up to
    # u (|b| + |c|): fl(fl(c + b) − b)) against the server's curve: parity of its amplitude plus
    # that recovery's rounding, point by point — a collapsed component (amplitude 5e-11 on a
    # 1000-count background) would otherwise read the background's ulps as a lineshape gap
    by_id = {p["id"]: p for p in sv["peaks"]}
    # every server component is drawn exactly once, on the same number of points (Codex round 2:
    # a missing or duplicated component dataset otherwise passed — the envelope 9 000 counts above)
    assert len(d["ids"]) == len(set(d["ids"])) and set(d["ids"]) == set(by_id), \
        f"{label}: drawn components {sorted(d['ids'])} are not the server's {sorted(by_id)}"
    assert all(len(c) == len(by_id[pid]["y"]) == len(d["env"]) for pid, c in zip(d["ids"], d["comps"])), f"{label}: lengths differ"
    U = 2.0 ** -53
    worst = 0.0
    for pid, c, amp in zip(d["ids"], d["comps"], d["amps"]):
        for ci, si, bi in zip(c, by_id[pid]["y"], d["bg"]):
            allowed = PARITY * abs(amp) + 2 * U * (abs(bi) + abs(si))
            worst = max(worst, abs(ci - si) / allowed)
            assert abs(ci - si) <= allowed, (f"{label}: component {pid} drawn {abs(ci - si):.3g} from the server's curve "
                                             f"(parity {PARITY:g} of its amplitude {amp:.3g} + the recovery's rounding)")
    return worst


def _fit(pg, shape):
    pg.evaluate(TAB, shape)
    r = pg.evaluate(FIT)
    assert r["have"] and r["engine"] != "local", f"{shape}: a server fit: {r}"
    return pg.evaluate(DRAWN)


@pytest.mark.parametrize("shape", SHAPES)
def test_after_a_server_fit_the_drawn_envelope_is_the_drawn_background_plus_components(browser, server, shape):
    pg = _new_page(browser, server)
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    try:
        d = _fit(pg, shape)
        assert d["stats"] == "current"
        _check_fitted(d, shape)
        # ...after the student edits a peak (the statistics go stale; the envelope is composed)
        pg.evaluate("() => { const p = state.peaks[0]; updatePeakParam(p.id, 'amplitude', p.amplitude * 1.3); updatePlot(); }")
        d = pg.evaluate(DRAWN)
        assert d["stats"] == "stale" and d["env"] != d["server"]["fitted_y"], "after an edit the envelope is composed"
        ratio, rel = _edited_gap(d)
        assert ratio <= 1.0, f"{shape} after an edit: {ratio:.3g} x rounding ({rel:.3g})"
        assert not errors, errors
    finally:
        pg.close()


# each lock at a bound the request builder once mis-sent (A03: `p.glMix || 50`, `p.dsAlpha || 0.1`)
# and the other ends of the boxes
LOCKS = [
    ("GL", {"glMix": 0, "fixGlMix": True}), ("GL", {"glMix": 100, "fixGlMix": True}),
    ("asym-GL", {"glMix": 0, "fixGlMix": True, "asymmetry": 1, "fixAsymmetry": True}),
    ("asym-GL", {"asymmetry": 0, "fixAsymmetry": True, "fixAmplitude": True}),
    ("DS", {"dsAlpha": 0, "fixDsAlpha": True}), ("DS", {"dsAlpha": 0.5, "fixDsAlpha": True, "dsGamma": 5, "fixDsGamma": True}),
    ("DS", {"dsGamma": 0, "fixDsGamma": True}), ("DSG_LA", {"laM": 4, "fixLaM": True}),
    ("DSG_LA", {"laAlpha": 0, "fixLaAlpha": True, "laM": 0.05, "fixLaM": True}),
    ("LACX", {"caM": 0, "fixCaM": True}), ("LACX", {"caM": 499, "fixCaM": True}),
    ("Gaussian", {"fixAmplitude": True, "fixCenter": True, "fixFwhm": True}),
    ("LACX", {"caAlpha": 5, "fixCaAlpha": True, "caBeta": 0.1, "fixCaBeta": True}),   # (α 0.1 with β 5 together does not certify)
]
# the page field a lock flag holds -> the server's parameter
BACKEND_NAME = {"glMix": "gl_ratio", "asymmetry": "asymmetry", "dsAlpha": "alpha", "dsGamma": "gamma_asym",
                "laAlpha": "alpha", "laBeta": "beta", "laM": "m_gauss", "caAlpha": "alpha", "caBeta": "beta", "caM": "m",
                "amplitude": "amplitude", "center": "center", "fwhm": "fwhm"}
# the values TAB starts the locked components with (a lock without a value holds these)
TAB_START = """(shape) => { const sp = { 'GL': { glMix: 30 }, 'asym-GL': { glMix: 30, asymmetry: 0.35 }, 'DS': { dsAlpha: 0.15, dsGamma: 0.2 },
    'DSG_LA': { laAlpha: 0.12, laBeta: 0.4, laM: 0.8 }, 'LACX': { caAlpha: 1.4, caBeta: 0.8, caM: 20 } }[shape] || {};
    return [{ amplitude: 8000, center: 381.0, fwhm: 1.5, ...sp }, { amplitude: 6000, center: 391.7, fwhm: 1.5, ...sp }]; }"""
LOCK_TAB = """([vals]) => { for (const p of state.peaks.slice(0, 2)) Object.assign(p, vals); updatePlot(); }"""


@pytest.mark.parametrize("shape,vals", LOCKS, ids=[f"{s}-{i}" for i, (s, _) in enumerate(LOCKS)])
def test_with_components_locked_at_bounds(browser, server, shape, vals):
    pg = _new_page(browser, server)
    try:
        pg.evaluate(TAB, shape)
        pg.evaluate(LOCK_TAB, [vals])
        r = pg.evaluate(FIT)
        assert r["have"] and r["engine"] != "local", r
        d = pg.evaluate(DRAWN)
        # the SERVER held every lock, on both locked components, at the requested value
        start = pg.evaluate(TAB_START, shape)
        for k, flag in [(k, v) for k, v in vals.items() if k.startswith("fix") and v]:
            page_key = k[3].lower() + k[4:]
            name = BACKEND_NAME[page_key]
            for comp, st in zip(d["server"]["peaks"][:2], start):
                par = comp["params"][name]
                want = vals.get(page_key, st[page_key])
                want = want / 100 if page_key == "glMix" else want
                assert par["vary"] is False and par["value"] == want, f"{shape}: {name} not held at {want}: {par}"
        _check_fitted(d, f"{shape} {vals}")
    finally:
        pg.close()


# ── each case FAILS with a real defect put back ───────────────────────────────

OLD_ASYMM_GL = """() => { window.asymmGL = function (x, center, fwhm, glMix, alpha) {
    // the page's asym-GL before cf4938d (2026-08-31): a width growing with distance from the centre
    const fwhmEff = x < center ? fwhm : fwhm * (1 + alpha * Math.abs(x - center) / fwhm);
    return pseudoVoigt(x, center, fwhmEff, glMix / 100);
}; }"""


def test_the_pre_cf4938d_asym_gl_breaks_it_after_a_fit(browser, server):
    # asymmetry held at 0.35 (this spectrum's lines are symmetric: a free asymmetry fits to ~0,
    # where the old and the new formula agree)
    pg = _new_page(browser, server)
    try:
        pg.evaluate(OLD_ASYMM_GL)
        pg.evaluate(TAB, "asym-GL")
        pg.evaluate(LOCK_TAB, [{"asymmetry": 0.35, "fixAsymmetry": True}])
        r = pg.evaluate(FIT)
        assert r["have"], r
        d = pg.evaluate(DRAWN)
        with pytest.raises(AssertionError, match="from the server's curve"):
            _check_fitted(d, "old asym-GL")
    finally:
        pg.close()


def test_an_envelope_composed_without_a_component_breaks_it_after_an_edit(browser, server):
    pg = _new_page(browser, server)
    try:
        _fit(pg, "GL")
        pg.evaluate("""() => { const real = evalAllPeaks;
            window.evalAllPeaks = (be, peaks) => real(be, peaks.slice(0, -1));   // the envelope drops one
            const p = state.peaks[0]; updatePeakParam(p.id, 'amplitude', p.amplitude * 1.3); updatePlot(); }""")
        d = pg.evaluate(DRAWN)
        assert d["stats"] == "stale"
        assert _edited_gap(d)[0] > 1.0
    finally:
        pg.close()


def test_a_locked_mix_of_zero_drawn_as_the_default_breaks_it(browser, server):
    # A03's builder defect, on the drawing side: a GL mix of exactly 0 read as `|| 50`
    pg = _new_page(browser, server)
    try:
        pg.evaluate(TAB, "GL")
        pg.evaluate(LOCK_TAB, [{"glMix": 0, "fixGlMix": True}])
        r = pg.evaluate(FIT)
        assert r["have"]
        pg.evaluate("""() => { const real = evalPeakArray;
            window.evalPeakArray = (be, p) => real(be, p.shape === 'GL' ? { ...p, glMix: p.glMix || 50 } : p); updatePlot(); }""")
        with pytest.raises(AssertionError, match="from the server's curve"):
            _check_fitted(pg.evaluate(DRAWN), "mix 0 as 50")
    finally:
        pg.close()


def test_a_component_drawn_on_shifted_energies_breaks_it(browser, server):
    # Codex round 1: the check compared y by index and ignored x
    pg = _new_page(browser, server)
    try:
        _fit(pg, "GL")
        d = pg.evaluate("""() => { const c = state.chart.data.datasets.find(d => d._peakId !== undefined);
            c.data = c.data.map(p => ({ x: p.x + 0.1, y: p.y })); }""")
        with pytest.raises(AssertionError, match="one x-grid"):
            _check_fitted(pg.evaluate(DRAWN), "shifted")
    finally:
        pg.close()


def test_a_ds_g_drawn_two_percent_too_wide_breaks_it(browser, server):
    # a DS+G-specific negative control: the page's FFT evaluator given a Gaussian width 2 % off
    pg = _new_page(browser, server)
    try:
        _fit(pg, "DSG_LA")
        pg.evaluate("""() => { const real = dsgConvolved_array;
            window.dsgConvolved_array = (be, c, a, b, m) => real(be, c, a, b, m * 1.02); updatePlot(); }""")
        with pytest.raises(AssertionError, match="from the server's curve"):
            _check_fitted(pg.evaluate(DRAWN), "DS+G too wide")
    finally:
        pg.close()


def test_a_component_not_drawn_after_a_fit_breaks_it(browser, server):
    # Codex round 2: the split check must see every server component — remove one drawn dataset
    pg = _new_page(browser, server)
    try:
        _fit(pg, "Gaussian")
        pg.evaluate("""() => { const ds = state.chart.data.datasets;
            ds.splice(ds.findIndex(d => d._peakId !== undefined), 1); }""")
        with pytest.raises(AssertionError, match="are not the server's"):
            _check_fitted(pg.evaluate(DRAWN), "a component not drawn")
    finally:
        pg.close()


def test_a_component_hidden_on_the_chart_after_a_fit_breaks_it(browser, server):
    # Codex round 3: a dataset hidden through Chart.js counted as drawn
    pg = _new_page(browser, server)
    try:
        _fit(pg, "Gaussian")
        pg.evaluate("""() => { const ds = state.chart.data.datasets;
            state.chart.setDatasetVisibility(ds.findIndex(d => d._peakId !== undefined), false); state.chart.update('none'); }""")
        with pytest.raises(AssertionError, match="not every curve is visible"):
            _check_fitted(pg.evaluate(DRAWN), "a hidden component")
    finally:
        pg.close()
