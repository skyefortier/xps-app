"""Real browser, real server (owner 2026-10-10): the envelope the page DRAWS is the background
it draws plus the sum of the components it draws, to rounding — after a server fit, after the
student edits a peak, and with components locked at their bounds; for every lineshape.

The 2026-09-17 report (an envelope above the sum of its components on a UCl4 spectrum) was
this identity broken: the page drew asym-GL with a width that grew with distance from the
centre while the server fitted a bounded one (fixed in cf4938d, 2026-08-31). Each case below
is also run with a real defect put back into the page and must then FAIL. The bound:
tests/envelope_identity.py. Skips cleanly when Playwright / Chromium / gunicorn are absent."""
import pytest

pytest.importorskip("playwright.sync_api")
from test_browser_find_peaks_full_window import _new_page, browser, server  # noqa: E402,F401
from envelope_identity import envelope_gap, fft_term  # noqa: E402

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

# what the chart draws: the envelope ('Fit…'), the background and each component (drawn on it)
DRAWN = """() => {
    const ds = state.chart.data.datasets;
    const env = ds.find(d => /^Fit/.test(d.label || ''));
    const bg = ds.find(d => d.label === 'Background');
    const comps = ds.filter(d => d._peakId !== undefined);
    const ys = d => d.data.map(p => p.y);
    const b = ys(bg);
    // each DS+G component's FFT norms, from a copy of the page's own evaluator at its fitted values
    const probe = new Function('return ' + dsgConvolved_array.toString().replace(
      'if (!(peakVal > 0)) return new Array(N).fill(0);',
      'let L = 1; while (L < 2 * nTot - 1) L <<= 1; let d1 = 0, d2 = 0, k1 = 0, k2 = 0;' +
      ' for (let t = 0; t < nTot; t++) { d1 += Math.abs(ds[t]); d2 += ds[t] * ds[t]; k1 += Math.abs(ks[t]); k2 += ks[t] * ks[t]; }' +
      ' window.__dsgNorm = { M: Math.max(Math.sqrt(d2) * k1, d1 * Math.sqrt(k2)), peakVal, L };' +
      ' if (!(peakVal > 0)) return new Array(N).fill(0);'))();
    const plotBE = state.fitResult && state.fitResult.be || env.data.map(p => p.x);
    const fft = state.peaks.filter(p => p.shape === 'DSG_LA').map(p => {
      window.__dsgNorm = null; probe(plotBE, p.center, p.laAlpha, p.laBeta, p.laM);
      return window.__dsgNorm && { amplitude: p.amplitude, ...window.__dsgNorm }; }).filter(Boolean);
    return { env: ys(env), bg: b, comps: comps.map(c => ys(c).map((v, i) => v - b[i])), fft,
             ids: comps.map(c => c._peakId), envFromServer: !!(state.fitResult && state.fitResult.fittedY && ys(env).every((v, i) => v === state.fitResult.fittedY[i])),
             stats: _statsLiveState() };
}"""

SHAPES = ["Gaussian", "Lorentzian", "Voigt", "GL", "asym-GL", "DS", "DSG_LA", "LACX"]


def _gap(d):
    # the components the chart draws are each "component + background", so each subtraction
    # adds a rounding of the background: n more terms, n + 1 more rounding units
    # DS+G components add their FFT rounding bound (tests/envelope_identity.py, fft_term)
    extra = sum(fft_term(f["amplitude"], f["M"], f["peakVal"], f["L"]) for f in d["fft"])
    return envelope_gap(d["env"], d["bg"], d["comps"], extra)


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
        assert d["envFromServer"] and d["stats"] == "current", "the envelope drawn is the server's fitted_y"
        ratio, rel = _gap(d)
        assert ratio <= 1.0, f"{shape}: drawn envelope - (background + components) = {ratio:.3g} x rounding ({rel:.3g} of its height)"
        # ...after the student edits a peak (the statistics go stale; the envelope is composed)
        pg.evaluate("() => { const p = state.peaks[0]; updatePeakParam(p.id, 'amplitude', p.amplitude * 1.3); updatePlot(); }")
        d = pg.evaluate(DRAWN)
        assert d["stats"] == "stale" and not d["envFromServer"]
        ratio, rel = _gap(d)
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
    ("DSG_LA", {"laAlpha": 0, "fixLaAlpha": True, "laM": 0.05, "fixLaM": True}),
    ("LACX", {"caM": 0, "fixCaM": True}), ("LACX", {"caM": 499, "fixCaM": True}),
    ("LACX", {"caAlpha": 5, "fixCaAlpha": True, "caBeta": 0.1, "fixCaBeta": True}),   # (α 0.1 with β 5 together does not certify)
]
LOCK_TAB = """([vals]) => { for (const p of state.peaks.slice(0, 2)) Object.assign(p, vals); updatePlot(); }"""


@pytest.mark.parametrize("shape,vals", LOCKS, ids=[f"{s}-{i}" for i, (s, _) in enumerate(LOCKS)])
def test_with_components_locked_at_bounds(browser, server, shape, vals):
    pg = _new_page(browser, server)
    try:
        pg.evaluate(TAB, shape)
        pg.evaluate(LOCK_TAB, [vals])
        r = pg.evaluate(FIT)
        assert r["have"] and r["engine"] != "local", r
        held = pg.evaluate("([keys]) => keys.map(k => state.peaks[0][k])", [[k for k in vals if not k.startswith("fix")]])
        assert held == [vals[k] for k in vals if not k.startswith("fix")], "the locks were held"
        d = pg.evaluate(DRAWN)
        assert d["envFromServer"]
        ratio, rel = _gap(d)
        assert ratio <= 1.0, f"{shape} {vals}: {ratio:.3g} x rounding ({rel:.3g})"
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
        ratio, rel = _gap(d)
        assert ratio > 1.0 and rel > 1e-3, f"the 2026-09-17 defect must be caught: {ratio:.3g} x rounding, {rel:.3g}"
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
        assert _gap(d)[0] > 1.0
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
        d = pg.evaluate(DRAWN)
        assert d["envFromServer"]
        assert _gap(d)[0] > 1.0
    finally:
        pg.close()
