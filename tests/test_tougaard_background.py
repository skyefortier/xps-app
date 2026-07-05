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
    y = np.full_like(x, 1e-9)  # tiny pedestal keeps the amplitude anchor finite
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
    assert bg[-1] == 0.0, f"low-BE edge should carry zero loss background, got {bg[-1]}"
    assert np.all(np.isfinite(bg))
    assert np.all(bg >= 0.0)

    # Same anchor semantics for ascending input: the high-BE edge is x[-1]
    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
    assert np.isclose(bg_a[-1], y[0], rtol=1e-12)
    assert bg_a[0] == 0.0


def test_short_input_returns_zeros():
    """< 2 points: no background can be defined; must return zeros."""
    assert np.array_equal(
        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
    )
    assert tougaard_background(np.array([]), np.array([])).size == 0
