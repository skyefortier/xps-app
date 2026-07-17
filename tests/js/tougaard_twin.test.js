// Tougaard background — JS twin of fitting.py's tougaard_background.
//
// The function lives inline in templates/index.html; extract its source and
// evaluate it so these tests exercise the exact shipped code. Pins the
// 2026-07-04 fix (mirrored from the backend, see
// tests/test_tougaard_background.py):
//   1. Universal cross-section constant C = 1643 eV² (was shipped squared:
//      1643*1643). Kernel K(T) = B·T/(C+T²)² peaks at sqrt(C/3) ≈ 23.4 eV.
//      S. Tougaard, Surf. Interface Anal. 11, 453 (1988).
//   2. Order-robustness: the one-sided loss sum needs a descending-BE grid;
//      ascending input is normalized internally and flipped back.
//   3. Amplitude anchored to the measured intensity at the HIGH-BE edge
//      (the old "trailing endpoint" rescale was degenerate: K(0)=0 forced
//      the zero-guard, multiplying by raw trailing counts instead).

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(
  path.join(__dirname, '../../templates/index.html'), 'utf8');
const match = html.match(/function tougaardBackground\([\s\S]*?\n\}/);
assert.ok(match, 'tougaardBackground not found in templates/index.html');
const tougaardBackground = eval('(' + match[0] + ')');

const avgMatch = html.match(/function _applyEndpointAveraging\([\s\S]*?\n\}/);
assert.ok(avgMatch, '_applyEndpointAveraging not found in templates/index.html');
const _applyEndpointAveraging = eval('(' + avgMatch[0] + ')');

function syntheticSpectrum() {
  // Same C 1s-like region as the Python tests: descending BE, dx = 0.1 eV.
  const be = [], intensity = [];
  for (let i = 0; i <= 150; i++) {
    const x = 295.0 - 0.1 * i;
    be.push(x);
    intensity.push(
      100.0
      + 5000.0 * Math.exp(-0.5 * Math.pow((x - 287.0) / 0.8, 2))
      + 400.0 / (1.0 + Math.exp(-(287.0 - x)))
    );
  }
  return { be, intensity };
}

test('loss-kernel response peaks ~23.4 eV above a delta-like peak', () => {
  const n = 1001;
  const be = [], intensity = [];
  for (let i = 0; i < n; i++) {
    be.push(100.0 - 0.1 * i);      // descending 100 → 0 eV
    intensity.push(1e-9);
  }
  // A high-BE step is required since the F1 offset fix (2026-07-17): the
  // fitted amplitude is proportional to the measured rise across the window
  // (high-BE edge minus the low-BE pre-loss level), so a perfectly flat
  // pedestal has no loss intensity to model and yields a flat background with
  // no kernel shape to inspect. Mirrors the Python twin test.
  intensity[0] = 2e-9;
  const spikeIdx = 800;            // be = 20.0 eV
  intensity[spikeIdx] = 1e6;

  const bg = tougaardBackground(be, intensity);

  let maxV = -Infinity, maxX = NaN;
  for (let i = 0; i < spikeIdx; i++) {   // high-BE side: traces K(be − 20)
    if (bg[i] > maxV) { maxV = bg[i]; maxX = be[i]; }
  }
  const expected = 20.0 + Math.sqrt(1643.0 / 3.0);  // ≈ 43.4 eV
  assert.ok(Math.abs(maxX - expected) <= 0.25,
    `kernel response peaks at ${maxX.toFixed(2)} eV, expected ~${expected.toFixed(2)}; ` +
    'a peak near 100 eV means the squared constant (1643*1643) is back');
});

test('ascending and descending BE input give the identical background', () => {
  const { be, intensity } = syntheticSpectrum();
  const bgDesc = tougaardBackground(be, intensity);
  const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
  bgAsc.reverse();
  for (let i = 0; i < be.length; i++) {
    assert.strictEqual(bgDesc[i], bgAsc[i],
      `order-dependent output at index ${i}: ${bgDesc[i]} vs ${bgAsc[i]}`);
  }
});

test('background meets the data at BOTH edges (high-BE anchor, low-BE C0)', () => {
  const { be, intensity } = syntheticSpectrum();
  const bg = tougaardBackground(be, intensity);
  const rel = Math.abs(bg[0] - intensity[0]) / intensity[0];
  assert.ok(rel < 1e-12,
    `high-BE-edge anchor broken: bg[0] = ${bg[0]}, data = ${intensity[0]}`);
  // Since the F1 offset fix (2026-07-17) the low-BE edge carries the pre-loss
  // constant C0, NOT zero. K(0)=0 still kills the LOSS integral there, so the
  // background equals C0 exactly. Asserting 0 pinned the bug: it forced the
  // background to dive to zero regardless of the data.
  const last = bg.length - 1;
  const relLow = Math.abs(bg[last] - intensity[last]) / intensity[last];
  assert.ok(relLow < 1e-12,
    `low-BE edge should sit on C0 = ${intensity[last]}, got ${bg[last]}`);
});

test('flat window yields no phantom signal (F1 regression pin)', () => {
  const be = [], intensity = [];
  for (let i = 0; i < 200; i++) { be.push(740.0 - 40.0 * i / 199); intensity.push(500.0); }
  const bg = tougaardBackground(be, intensity);
  for (let i = 0; i < bg.length; i++) {
    assert.ok(Math.abs(intensity[i] - bg[i]) < 1e-6,
      `flat window must leave ~zero net; net ${intensity[i] - bg[i]} at ${i}`);
  }
});

test('agrees with the backend implementation (fitting.py) on the same spectrum', () => {
  // Expected values regenerated against the backend on 2026-07-17 after the
  // F1 (pre-loss constant C0) + F2 (local quadrature weights) fixes:
  //   venv/bin/python - <<'EOF'
  //   import numpy as np; from fitting import tougaard_background
  //   x = np.linspace(295.0, 280.0, 151)
  //   y = (100.0 + 5000.0*np.exp(-0.5*((x-287.0)/0.8)**2)
  //        + 400.0/(1.0+np.exp(-(287.0-x))))
  //   bg = tougaard_background(x, y)
  //   print([float(bg[i]) for i in (0, 30, 75, 110, 149, 150)])
  //   EOF
  // Regenerate with that snippet if the backend numerics change for a
  // reviewed reason. Tolerance 1e-9 relative: np.convolve vs the JS loop
  // differ only by floating-point summation order.
  const expected = {
    0: 100.13414005218658,
    30: 219.3991381848062,
    75: 461.76541491579644,
    110: 499.7312788702072,
    149: 499.6355795222399,
    150: 499.6355795222399,
  };
  const { be, intensity } = syntheticSpectrum();
  const bg = tougaardBackground(be, intensity);
  for (const [idx, want] of Object.entries(expected)) {
    const got = bg[Number(idx)];
    const tol = want === 0 ? 1e-15 : Math.abs(want) * 1e-9;
    assert.ok(Math.abs(got - want) <= tol,
      `backend/frontend disagree at index ${idx}: js ${got} vs python ${want}`);
  }
});

// --- Codex review finding (2026-07-04, both runs, MAJOR): the shipped
// caller computeBackgroundCore passed RAW intensity to tougaardBackground
// while every backend caller applies endpoint averaging first. With the
// high-BE-edge anchor, averaging directly sets the anchor amplitude, so
// the caller contract — not just the function — must match the backend
// (fitting.py run_fit / compute_background_only both do
// tougaard_background(x, _apply_endpoint_averaging(y, n))).
test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
  const coreMatch = html.match(/function computeBackgroundCore\([\s\S]*?\n\}/);
  assert.ok(coreMatch, 'computeBackgroundCore not found in templates/index.html');
  // Stubs for background types this test never routes to; the eval'd
  // function closes over this scope, so these names resolve at call time.
  const manualAnchorBackground = () => { throw new Error('unexpected route: manual'); };
  const shirleyBackground = () => { throw new Error('unexpected route: shirley'); };
  const smartBackground = () => { throw new Error('unexpected route: smart'); };
  const smartExperimentalBackground = () => { throw new Error('unexpected route: smart_exp'); };
  const shirleyLinearBackground = () => { throw new Error('unexpected route: shirley_linear'); };
  const linearBackground = () => { throw new Error('unexpected route: linear'); };
  const computeBackgroundCore = eval('(' + coreMatch[0] + ')');

  // Descending grid with an outlier at the high-BE edge: raw vs 3-point
  // averaged anchors differ by construction (Codex's concrete scenario).
  const n = 21;
  const be = [], intensity = [];
  for (let i = 0; i < n; i++) { be.push(292.0 - 0.5 * i); intensity.push(100); }
  intensity[0] = 10000;   // high-BE outlier
  intensity[10] = 4000;   // a peak so the correlation is non-trivial

  const nAvg = 3;
  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));

  // Branch 1: bg window covers the data (main sliced path)
  const mainOut = computeBackgroundCore(be, intensity, {
    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
    bgStart: '292', bgEnd: '282',
  });
  // Branch 2: bg window misses the data entirely (fallback full-range path)
  const fallbackOut = computeBackgroundCore(be, intensity, {
    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
    bgStart: '900', bgEnd: '905',
  });

  for (const [label, out] of [['main', mainOut], ['fallback', fallbackOut]]) {
    for (let i = 0; i < n; i++) {
      assert.strictEqual(out[i], expected[i],
        `${label} branch: caller bypasses endpoint averaging at index ${i}: ` +
        `${out[i]} vs averaged ${expected[i]}`);
    }
  }
});
