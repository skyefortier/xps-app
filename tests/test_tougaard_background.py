"""Tougaard universal-cross-section background — correctness pins.

Pins the 2026-07-04 bug-fix (branch feature-autofit-stage2):

1. The universal-cross-section constant C was shipped SQUARED
   (``C = 1643.0**2`` ≈ 2.7e6 eV² instead of C = 1643 eV²), a
   transcription slip of "C = 1643 eV²".  The loss kernel
   K(T) = B·T/(C + T²)² peaks at T = sqrt(C/3): ≈ 23.4 eV with the
   correct constant, ≈ 948.6 eV with the squared one — so over any real
   ~20 eV XPS window the shipped "Tougaard" background was essentially
   flat/zero.  Reference: S. Tougaard, Surf. Interface Anal. 11, 453
   (1988) — two-parameter universal cross-section, B = 2866 eV²,
   C = 1643 eV².

2. The one-sided loss sum (j >= i) is only physical on a DESCENDING
   binding-energy grid; ascending input silently produced a background
   accumulating on the wrong side (same bug class as the np.interp
   descending-grid registration bug).  The function now normalizes to
   descending internally and flips the result back, mirroring
   shirley_background's ascending normalization.

3. The trailing-endpoint rescale was degenerate: K(0) = 0 makes the
   trailing background sample identically zero, so the zero-guard always
   fired and the "match the trailing endpoint" scale was in fact
   "multiply by the trailing raw counts".  The normalization now anchors
   the background to the measured intensity at the HIGH-BE edge of the
   window (the standard practical Tougaard criterion: B is effectively
   fitted so the background meets the spectrum above the peak).

No pre-existing test or fixture pinned the old (wrong) Tougaard output
(verified by grep over tests/, tests/autofit/, docs/autofit/inventory/,
scripts/ on 2026-07-04), so nothing needed regeneration.
"""

import numpy as np

from fitting import tougaard_background


def _synthetic_spectrum(descending: bool = True):
    """Realistic C 1s-like region: baseline + Gaussian peak + loss step."""
    x = np.linspace(295.0, 280.0, 151)  # descending BE, dx = 0.1 eV
    y = (
        100.0
        + 5000.0 * np.exp(-0.5 * ((x - 287.0) / 0.8) ** 2)
        + 400.0 / (1.0 + np.exp(-(287.0 - x)))  # step rising toward high BE
    )
    if not descending:
        return x[::-1].copy(), y[::-1].copy()
    return x, y


def test_kernel_peak_near_sqrt_c_over_3():
    """The loss-kernel response to a delta-like peak must peak ~23.4 eV
    above the peak (sqrt(C/3) with C = 1643 eV²), not ~949 eV.

    A spike at x0 on a descending grid produces bg(x) ∝ K(x − x0) on the
    high-BE side, so the argmax of the background directly locates the
    kernel maximum.
    """
    x = np.linspace(100.0, 0.0, 1001)  # descending, dx = 0.1 eV
    # A pedestal PLUS a high-BE step. The step matters: since the F1 offset
    # fix (2026-07-17) the fitted amplitude is proportional to the measured
    # rise across the window (data at the high-BE edge minus the low-BE
    # pre-loss level). A perfectly flat pedestal therefore has NO loss
    # intensity to model, so the honest background is flat and carries no
    # kernel shape to inspect. The step gives the anchor something to fit;
    # the background shape it scales is still the pure kernel response.
    y = np.full_like(x, 1e-9)
    y[0] = 2e-9  # high-BE edge: a measured rise -> nonzero fitted amplitude
    spike_idx = 800  # x = 20.0 eV
    y[spike_idx] = 1.0e6

    bg = tougaard_background(x, y)

    high_be_side = slice(0, spike_idx)  # x > 20 eV: traces K(x − 20)
    peak_x = x[high_be_side][np.argmax(bg[high_be_side])]
    expected = 20.0 + np.sqrt(1643.0 / 3.0)  # 20 + 23.402...
    assert abs(peak_x - expected) <= 0.25, (
        f"kernel response peaks at x = {peak_x:.2f} eV; expected "
        f"{expected:.2f} eV (spike at 20.0 + sqrt(C/3) ≈ 23.4 eV). "
        f"A peak near x = 100 means the squared constant (C = 1643²) is back."
    )


def test_ascending_and_descending_input_agree_exactly():
    """The same spectrum fed in ascending vs descending BE order must give
    the identical background (element-wise, after re-reversal)."""
    x_d, y_d = _synthetic_spectrum(descending=True)
    x_a, y_a = _synthetic_spectrum(descending=False)

    bg_d = tougaard_background(x_d, y_d)
    bg_a = tougaard_background(x_a, y_a)

    assert np.array_equal(bg_d, bg_a[::-1]), (
        f"order-dependent output: max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
    )


def test_ascending_descending_parity_on_nonuniform_grid():
    """Order-robustness must also hold on the non-uniform-grid code path
    (which uses the exact per-point separation loop, not the convolution)."""
    # Deterministic, mildly non-uniform descending grid
    steps = 0.08 + 0.04 * np.sin(np.arange(120))
    x_d = 295.0 - np.concatenate(([0.0], np.cumsum(steps)))
    y_d = 100.0 + 4000.0 * np.exp(-0.5 * ((x_d - 290.0) / 1.0) ** 2)

    bg_d = tougaard_background(x_d, y_d)
    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())

    assert np.array_equal(bg_d, bg_a[::-1]), (
        f"non-uniform grid is order-dependent: "
        f"max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
    )


def test_background_anchored_at_high_be_edge():
    """The background must equal the measured intensity at the high-BE edge
    of the window (practical Tougaard criterion: the universal cross-section
    amplitude is scaled so the background meets the data above the peak),
    and must vanish at the low-BE edge (no in-window emitters below it)."""
    x, y = _synthetic_spectrum(descending=True)
    bg = tougaard_background(x, y)

    # x[0] is the high-BE edge on this descending grid
    assert np.isclose(bg[0], y[0], rtol=1e-12), (
        f"high-BE-edge anchor broken: bg[0] = {bg[0]}, data = {y[0]}"
    )
    # Since the F1 offset fix (2026-07-17) the low-BE edge carries the
    # pre-loss constant C0 (the out-of-window baseline), NOT zero. K(0) = 0
    # still makes the LOSS integral vanish there, so the background equals C0
    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
    # Asserting 0.0 here was pinning the bug: it forced the background to dive
    # to zero at the low-BE edge regardless of the data, reporting the entire
    # baseline as net signal.
    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
        f"low-BE edge should sit on the pre-loss level C0 = {y[-1]}, got {bg[-1]}"
    )
    assert np.all(np.isfinite(bg))
    assert np.all(bg >= 0.0)

    # Same anchor semantics for ascending input: the high-BE edge is x[-1]
    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
    assert np.isclose(bg_a[-1], y[0], rtol=1e-12)
    # ...and the low-BE edge (index 0 when ascending) sits on C0, per above.
    assert np.isclose(bg_a[0], y[-1], rtol=1e-12)


def test_no_loss_signal_returns_flat_pre_loss_level():
    """Degenerate input: no net loss signal accumulates at the high-BE edge
    (bg[0] == 0 — counts are zero everywhere below the edge point).

    Supersedes the 2026-07-04 Codex pin ``..._returns_unanchored_zeros``.
    That pin asserted all-zeros, which was correct ONLY while the background
    carried no constant term: with the F1 offset fix (2026-07-17) the honest
    answer for a window containing no modellable loss signal is the flat
    pre-loss level C0, not zero. Returning zeros would report the entire
    baseline as net signal — the exact failure F1 fixes. The guard itself
    still exists (no force-matching to the edge intensity, no divide-by-zero);
    only its fallback VALUE changed from 0 to C0. Mirrored in the JS twin."""
    x = np.array([291.0, 290.0, 289.0, 288.0])  # descending
    y = np.array([100.0, 0.0, 0.0, 0.0])        # signal only at the edge itself
    bg = tougaard_background(x, y)
    assert np.array_equal(bg, np.zeros(4)), (
        f"C0 is 0.0 here (low-BE edge counts are zero), so the flat pre-loss "
        f"level IS zeros; got {bg}"
    )


def test_flat_window_yields_no_phantom_signal():
    """F1 regression pin (2026-07-17): a flat, featureless window must yield
    ~zero net counts everywhere.

    Before the offset fix, K(0) = 0 forced the background to zero at the
    low-BE edge regardless of the data, so a flat 500-count window produced a
    background ramping 0 -> 500 and reported up to 500 counts of phantom
    "signal" fabricated from a featureless baseline."""
    x = np.linspace(740.0, 700.0, 200)   # descending, flat data
    y = np.full_like(x, 500.0)
    bg = tougaard_background(x, y)
    net = y - bg
    assert np.max(np.abs(net)) < 1e-6, (
        f"flat window must leave ~zero net; net spans "
        f"{net.min():.3f}..{net.max():.3f}"
    )


def test_background_tracks_low_be_baseline_on_wide_region():
    """F1 regression pin (2026-07-17): on a wide 2p-like region sitting on a
    large out-of-window inelastic baseline, the background must track that
    baseline at the low-BE edge instead of diving to zero."""
    x = np.linspace(740.0, 700.0, 600)   # descending
    pk = (6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2)
          + 3000.0 * np.exp(-0.5 * ((x - 724.5) / 1.9) ** 2))
    baseline = 4000.0 + 3000.0 * np.cumsum(pk[::-1])[::-1] / np.sum(pk)
    y = pk + baseline
    bg = tougaard_background(x, y)
    # low-BE edge is index -1 on this descending grid
    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
        f"low-BE edge dove to {bg[-1]:.1f} instead of tracking the "
        f"{y[-1]:.1f}-count baseline"
    )
    assert np.isclose(bg[0], y[0], rtol=1e-12)


def test_nonuniform_grid_uses_local_quadrature_weights():
    """F2 regression pin (2026-07-17): the nonuniform-grid branch must weight
    each term by its local energy spacing.

    It previously used exact per-point separations but omitted the spacing
    weights, silently applying uniform-grid quadrature inside the branch
    written precisely BECAUSE the grid is not uniform (~24% error on a
    genuinely nonuniform grid). np.gradient returns dx exactly on a uniform
    grid, so the two branches must now agree to floating point -- the
    uniformity test is an optimization, not a semantic fork."""
    # Uniform grid, then the same grid perturbed below the uniformity
    # tolerance so the nonuniform branch runs on near-identical data.
    x = np.linspace(740.0, 700.0, 300)
    y = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))
    bg_uniform = tougaard_background(x, y)
    x_jitter = x.copy()
    x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
    bg_nonuniform = tougaard_background(x_jitter, y)
    assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
        "uniform and nonuniform branches disagree on near-identical grids"
    )

    # Genuinely nonuniform grid vs an explicit spacing-weighted reference.
    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
                         np.linspace(720.0, 700.0, 400)])
    ya = np.interp(xa[::-1], x[::-1], y[::-1])[::-1]
    got = tougaard_background(xa, ya)

    B_coef, C_coef = 2866.0, 1643.0
    c0 = float(ya[-1])
    net = ya - c0
    w = np.abs(np.gradient(xa))
    ref = np.zeros(len(xa))
    for i in range(len(xa)):
        T = np.abs(xa[i:] - xa[i])
        ref[i] = float(np.sum((B_coef * T) / (C_coef + T * T) ** 2 * net[i:] * w[i:]))
    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
    assert np.allclose(got, ref, rtol=1e-9), (
        "nonuniform branch does not match spacing-weighted quadrature"
    )


def test_short_input_returns_zeros():
    """< 2 points: no background can be defined; must return zeros."""
    assert np.array_equal(
        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
    )
    assert tougaard_background(np.array([]), np.array([])).size == 0
