OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f721d-6a55-7210-b514-2668ac9774b9
--------
user
You are an adversarial reviewer for a scoped follow-up commit in this repo
(XPS peak-fitting web app), branch feature-autofit-stage2. This is a RECHECK
of a prior review round, not a fresh review — read the disposition below
before diffing anything.

CONTEXT: commit 3d9ff54 ("fix(fitting): Tougaard pre-loss constant (F1) +
non-uniform quadrature weights (F2)") was reviewed twice already. One run
returned GO with no findings. The other run returned NO-GO with one MAJOR
finding: `test_nonuniform_grid_uses_local_quadrature_weights`
(tests/test_tougaard_background.py) used a fixture where both window edges
sat at ~4000 counts (a symmetric Gaussian on a flat baseline), so the F1
amplitude anchor — which rescales the whole background by
`(ya[0]-c0)/bg[0]` — collapsed the signal toward zero on that fixture. The
reviewer proved (by reimplementing tougaard_background with the F2
weighting term removed and re-running the test's own comparison) that the
test would still pass even with F2 fully reverted from production: max
diff was 4.5e-13, far inside the test's rtol=1e-9.

THE FIX, now in commit 173f002 ("fix(tests): ..."): the fixture gained a
genuine high-BE endpoint rise (a linear ramp under the Gaussian, ~800-count
endpoint delta) so the anchor scale stays non-degenerate, plus an explicit
"guard the guard" assertion that the weighted and unweighted reference
implementations diverge by more than 10 counts before trusting the
allclose comparison between them. `git show 173f002` gives the full diff —
it touches ONLY tests/test_tougaard_background.py; fitting.py has zero
diff in this commit (the production F2 fix from 3d9ff54 is unchanged).

YOUR JOB — verify the fix actually closes the finding, and look for new
problems it might have introduced:

1. Does the new fixture (xa = concatenated dense/sparse nonuniform grid,
   ya = 4000 + 800*(xa-700)/40 + 6000*gaussian(xa, 710.9, 1.6)) actually
   produce a meaningful endpoint delta that survives the F1 anchor? Confirm
   by computation, not just reading the comment.
2. Does removing the F2 `w[i:]` weighting from a working copy of
   tougaard_background now make THIS test fail? (This is the load-bearing
   claim — reproduce the reviewer's own methodology from the prior round:
   reimplement the unweighted version, run it through the test's actual
   assertions, confirm failure.)
3. Does the "guard the guard" assertion (`max(abs(ref - ref_unweighted)) >
   10.0`) itself hold on this fixture, and is 10.0 counts a reasonable
   margin given the ~105-count divergence measured, or is it either so
   loose it could pass by accident or so tight it's fragile to unrelated
   changes?
4. Scope check: confirm fitting.py, templates/index.html,
   tests/js/tougaard_twin.test.js, autofit/engine.py, autofit/methods/*.py,
   and /api/fit have ZERO diff in commit 173f002 — this must be a pure
   test-only fix.
5. Re-run (or re-verify) the other 8 tests in
   tests/test_tougaard_background.py plus the 6 tests in
   tests/js/tougaard_twin.test.js still pass unmodified/unaffected.
6. Any OTHER regression pin in this test file (or the JS twin) that shares
   the same class of bug — an assertion that looks like it exercises a code
   path but is actually neutralized by a fixture choice (endpoint
   collapse, degenerate guard, etc.)? Do a fresh sweep, don't just take the
   "only one MAJOR finding" disposition on faith.

Also re-confirm the two items the FIRST round's GO run already checked
(cheap to re-verify, don't skip): (a) no saved-fit fixture or inventory
JSON anywhere in the repo pins Tougaard numeric output; (b) the negative-
scale anchoring behavior (baseline falls with BE -> negative scale factor,
passed through unclamped) is a deliberate, pre-existing project stance,
not a new bug introduced by this change.

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll treat this as a recheck review and verify the specific load-bearing behavior with computations. I’m going to inspect the commit diff and test file first, then run targeted simulations/tests where the read-only workspace allows it.
exec
/bin/zsh -lc "sed -n '1,260p' fitting.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
"""
fitting.py – XPS peak fitting engine using lmfit.

Supported lineshapes
--------------------
  gaussian        – pure Gaussian (amplitude at peak max, FWHM parameterised)
  lorentzian      – pure Lorentzian
  pseudo_voigt_gl – linear GL mix: (1‑η)·G + η·L  (η = Lorentzian fraction)
  asymmetric_gl   – GL mix with independent left/right FWHM
  doniach_sunjic  – metallic asymmetric lineshape
  ds_g            – DS+G: DS core × Gaussian convolution (formerly "la_casaxps")
  la_casaxps      – TRUE CasaXPS LA(α,β,m): asymmetric base Lorentzian + integer-kernel Gauss conv

Backgrounds
-----------
  shirley         – iterative Shirley (Proctor & Sherwood 1982)
  linear          – straight‑line between endpoints
  none            – flat zero

Spin‑orbit constraints are handled via lmfit parameter expressions.
"""

from __future__ import annotations

import logging
import warnings
from typing import Any

import numpy as np
from lmfit import Model, Parameters
from scipy.integrate import trapezoid

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Lineshape functions (all FWHM‑parameterised, amplitude = peak maximum)
# ─────────────────────────────────────────────────────────────────────────────

_LN2 = np.log(2.0)
_SQRT_PI_4LN2 = np.sqrt(np.pi / (4.0 * _LN2))  # ≈ 1.06447


def _gaussian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Gaussian; amplitude is the peak maximum value."""
    return amplitude * np.exp(-4.0 * _LN2 * ((x - center) / fwhm) ** 2)


def _lorentzian(x: np.ndarray, amplitude: float, center: float, fwhm: float) -> np.ndarray:
    """Lorentzian; amplitude is the peak maximum value."""
    hwhm = fwhm / 2.0
    return amplitude * hwhm ** 2 / ((x - center) ** 2 + hwhm ** 2)


def _pseudo_voigt_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    gl_ratio: float,
) -> np.ndarray:
    """
    Pseudo‑Voigt as a linear combination of Gaussian and Lorentzian.

    gl_ratio : Lorentzian fraction  (0 = pure Gaussian, 1 = pure Lorentzian)
    """
    eta = float(np.clip(gl_ratio, 0.0, 1.0))
    return (1.0 - eta) * _gaussian(x, amplitude, center, fwhm) + eta * _lorentzian(
        x, amplitude, center, fwhm
    )


def _asymmetric_gl(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    asymmetry: float,
    gl_ratio: float,
) -> np.ndarray:
    """
    Asymmetric GL pseudo‑Voigt with independent asymmetry parameter.

    fwhm      : base FWHM (used on the low‑BE side, i.e. x ≤ center)
    asymmetry : broadening factor for the high‑BE side;
                fwhm_right = fwhm × (1 + asymmetry).  0 = symmetric.
    gl_ratio  : common Lorentzian fraction for both sides.

    Both halves meet at x = center with value = amplitude.
    """
    asym = float(np.clip(asymmetry, 0.0, 1.0))
    fwhm_r = fwhm * (1.0 + asym)
    result = np.empty_like(x, dtype=float)
    left = x <= center
    result[left] = _pseudo_voigt_gl(x[left], amplitude, center, fwhm, gl_ratio)
    result[~left] = _pseudo_voigt_gl(x[~left], amplitude, center, fwhm_r, gl_ratio)
    return result


def _doniach_sunjic(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    alpha: float,
    gamma_asym: float = 0.0,
) -> np.ndarray:
    """
    Doniach‑Sunjic lineshape for metallic core‑level spectra.

      DS(x) = A · N · cos(πα/2 + (1‑α)·arctan((c‑x)/γ))
                    ─────────────────────────────────────────
                         ((c‑x)² + γ²)^((1‑α)/2)
              × exp(−gamma_asym · max(0, x−c))

    where γ = fwhm/2,  N = γ^(1‑α)/cos(πα/2)  so that DS(c) = A.
    dx = c − x so the power-law tail extends toward HIGHER BE (inelastic losses).
    gamma_asym > 0 adds an exponential envelope that limits how far the
    high-BE tail extends (0 = pure DS power-law tail, no limit).

    alpha     : asymmetry index  (0 = symmetric Lorentzian, typical 0–0.3)
    gamma_asym: exponential tail-decay rate (eV⁻¹).  0 = standard DS.
    """
    alpha      = float(np.clip(alpha, 0.0, 0.995))
    gamma_asym = max(float(gamma_asym), 0.0)
    gamma      = max(fwhm / 2.0, 1e-12)
    cos0 = np.cos(np.pi * alpha / 2.0)
    if abs(cos0) < 1e-12:
        cos0 = 1e-12
    norm = gamma ** (1.0 - alpha) / cos0
    # dx = center − x  →  positive on LOW-BE side, negative on HIGH-BE side.
    # The arctan and power-law terms produce a tail toward HIGH-BE (dx < 0).
    dx = center - x
    phase = np.pi * alpha / 2.0 + (1.0 - alpha) * np.arctan(dx / gamma)
    denom = (dx ** 2 + gamma ** 2) ** ((1.0 - alpha) / 2.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = amplitude * norm * np.cos(phase) / denom
    # Exponential envelope to gently limit the HIGH-BE tail extent.
    # dx = center - x: negative on the HIGH-BE side (x > center).
    # We want: decay = 1 at center, tapering toward zero far into the tail.
    # Use |dx| on the high-BE side only: exp(-gamma_asym * max(x - center, 0))
    if gamma_asym > 0.0:
        tail_decay = np.exp(-gamma_asym * np.maximum(x - center, 0.0))
        result = result * tail_decay
    result = np.where(np.isfinite(result), result, 0.0)
    return result


def _ds_g_dscore_gauss(
    x: np.ndarray,
    amplitude: float,
    center: float,
    alpha: float,    # CasaXPS: dimensionless asymmetry index, 0 ≤ α < 0.5
    beta: float,     # CasaXPS: Lorentzian half-width (eV)
    m_gauss: float,  # CasaXPS: Gaussian FWHM (eV) for convolution
) -> np.ndarray:
    """
    DS+G lineshape (formerly mislabeled "LA(α,β,m) [CasaXPS]") —
    Doniach-Šunjić asymmetric core convolved analytically with a Gaussian
    instrument-broadening kernel. NOT to be confused with the true CasaXPS
    LA shape (see _la_casaxps_true), which uses a piecewise-asymmetric
    Lorentzian with point-domain Gaussian convolution.

    The DS core with asymmetry index α and Lorentzian half-width β is convolved
    with a Gaussian of FWHM m for instrument broadening.

    Tail direction: eps = x − center > 0 → HIGHER binding energy (physically
    correct: low-energy electron-hole pair excitations produce intensity on the
    high-BE side only).

    Parameters
    ----------
    alpha   : dimensionless asymmetry index, 0 ≤ α < 0.5
              (0 = symmetric Lorentzian, ~0.1–0.3 for metallic systems)
    beta    : Lorentzian half-width at half-maximum (eV); controls core width
    m_gauss : Gaussian FWHM (eV) for instrument/phonon broadening (0 = none)

    Fixes (v2)
    ----------
    1. Convolution uses a padded grid (±10·m on each side) with cosine taper
       to eliminate cliff artifacts at array boundaries.
    2. Explicit FFT convolution with a properly normalised Gaussian kernel,
       so DS tail direction is preserved regardless of m value.
    """
    alpha   = float(np.clip(alpha, 0.0, 0.495))
    beta    = max(float(beta),    1e-6)
    m_gauss = max(float(m_gauss), 0.0)

    # ── DS core evaluator (independent of m_gauss) ───────────────────────────
    #
    # eps = x − center: positive on HIGH-BE side (where tail belongs)
    # DS formula:  cos(πα/2 − (1−α)·arctan2(ε, β)) / (ε² + β²)^((1−α)/2)
    #
    # Sign convention proof:
    #   At ε >> β (high BE):  arctan2(ε, β) → +π/2
    #     phase → πα/2 − (1−α)·π/2 → −π(1−2α)/2  (negative for α < 0.5)
    #     cos(phase) > 0, and denominator grows as |ε|^(1−α)
    #     → slow power-law decay toward HIGH BE  ✓
    #   At ε << −β (low BE): arctan2(ε, β) → −π/2
    #     phase → πα/2 + (1−α)·π/2 → π/2  (for small α)
    #     cos(phase) → 0, faster falloff
    #     → steeper decay toward LOW BE  ✓

    def _ds_core(xgrid):
        """Evaluate DS kernel on arbitrary grid. Independent of m_gauss."""
        eps = xgrid - center
        r2 = eps ** 2 + beta ** 2
        r2 = np.maximum(r2, 1e-30)
        rPow = r2 ** ((1.0 - alpha) / 2.0)
        phase = np.pi * alpha / 2.0 - (1.0 - alpha) * np.arctan2(eps, beta)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            core = np.cos(phase) / rPow
        core = np.where(np.isfinite(core), core, 0.0)
        return core

    # ── No Gaussian broadening — just return normalised DS core ──────────────
    if m_gauss < 0.001:
        ds_core = _ds_core(x)
        peak_val = float(np.interp(center, x if x[-1] > x[0] else x[::-1],
                                   ds_core if x[-1] > x[0] else ds_core[::-1]))
        if peak_val <= 0.0:
            peak_val = np.max(np.abs(ds_core))
        if peak_val <= 0.0:
            return np.zeros_like(x)
        return amplitude * ds_core / peak_val

    # ── Build padded grid for convolution ─────────────────────────────────────
    # Pad by ±10·m_gauss (≈ ±4.25σ) to avoid truncation artifacts.
    # The DS power-law tail decays as |ε|^(α−1), which is slow for small α,
    # so generous padding is essential.
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 0.05
    step = max(step, 1e-6)

    pad_ev = max(10.0 * m_gauss, 20.0 * beta)  # eV of padding on each side
    n_pad = int(np.ceil(pad_ev / step))
    n_pad = max(n_pad, 1)

    # Determine sort direction of input x
    ascending = (x[-1] > x[0]) if len(x) > 1 else True

    # Create padded energy grid extending beyond the data range
    if ascending:
        x_pad_lo = x[0] - n_pad * step
        x_pad_hi = x[-1] + n_pad * step
    else:
        x_pad_lo = x[-1] - n_pad * step
        x_pad_hi = x[0] + n_pad * step

    n_total = len(x) + 2 * n_pad
    x_padded = np.linspace(x_pad_lo, x_pad_hi, n_total)  # always ascending

    # Evaluate DS core on padded grid
    ds_padded = _ds_core(x_padded)

    # ── Cosine taper on pad regions ───────────────────────────────────────────
    # Smoothly ramp to zero at the array edges to kill any residual signal
    # that would cause Gibbs-like ringing in FFT convolution.
    taper = np.ones(n_total)
    if n_pad > 1:

exec
/bin/zsh -lc "sed -n '1,260p' tests/test_tougaard_background.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
    # A high-BE endpoint RISE (not just a symmetric peak on a flat baseline)
    # is required here: the F1 anchor rescales by (ya[0]-c0)/bg[0], so a
    # fixture whose two edges sit at nearly the same level collapses that
    # scale factor toward zero and the F2 weighting difference vanishes
    # into the noise floor *after* anchoring -- passing this assertion even
    # with the w[i:] weighting removed entirely (caught by Codex review,
    # 2026-07-17: the original flat-baseline fixture measured a 4.5e-13 max
    # diff between weighted and unweighted output, i.e. it did not actually
    # guard F2). The endpoint delta below (~800 counts) keeps the anchored
    # scale non-degenerate, so the ~105-count weighted-vs-unweighted
    # divergence survives anchoring and this pin is falsifiable again.
    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
                         np.linspace(720.0, 700.0, 400)])
    ya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(
        -0.5 * ((xa - 710.9) / 1.6) ** 2
    )
    got = tougaard_background(xa, ya)

    B_coef, C_coef = 2866.0, 1643.0
    c0 = float(ya[-1])
    net = ya - c0
    w = np.abs(np.gradient(xa))
    ref = np.zeros(len(xa))
    ref_unweighted = np.zeros(len(xa))
    for i in range(len(xa)):
        T = np.abs(xa[i:] - xa[i])
        kernel = (B_coef * T) / (C_coef + T * T) ** 2
        ref[i] = float(np.sum(kernel * net[i:] * w[i:]))
        ref_unweighted[i] = float(np.sum(kernel * net[i:]))
    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
    ref_unweighted = c0 + ref_unweighted * ((float(ya[0]) - c0) / ref_unweighted[0])


exec
/bin/zsh -lc 'git show --stat --oneline --decorate 173f002 && git show --name-only --format=fuller 173f002' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-g5oRCJtn' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UDOQj0GZ' (errno=Operation not permitted)
173f002 fix(tests): test_nonuniform_grid_uses_local_quadrature_weights didn't guard F2
 tests/test_tougaard_background.py | 28 ++++++++++++++++++++++++++--
 1 file changed, 26 insertions(+), 2 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YH3mNyU4' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-gFHhfZ06' (errno=Operation not permitted)
commit 173f0025cb843948111fa8e880b6bef053949ca5
Author:     Skye Fortier <skyefortier@gmail.com>
AuthorDate: Fri Jul 17 16:05:11 2026 -0600
Commit:     Skye Fortier <skyefortier@gmail.com>
CommitDate: Fri Jul 17 16:05:11 2026 -0600

    fix(tests): test_nonuniform_grid_uses_local_quadrature_weights didn't guard F2
    
    Codex review of 3d9ff54 (run B) caught a laundered regression pin: the
    fixture put a symmetric Gaussian on a flat baseline, so both window edges
    sat at ~4000 counts (endpoint delta ~5e-7). The F1 anchor scales the whole
    background by (ya[0]-c0)/bg[0], which collapsed to near-zero on that
    fixture — so the F2 weighted-vs-unweighted difference (measured ~105
    counts on a fixture with a real endpoint rise) vanished into the noise
    floor after anchoring. Independently verified: reverting the w[i:]
    weighting entirely from tougaard_background still passed this assertion
    (max diff 4.5e-13, well inside rtol=1e-9), i.e. the pin did not fail if F2
    regressed.
    
    Fix: give the fixture a genuine high-BE endpoint rise (linear ramp under
    the Gaussian) so the anchor scale stays non-degenerate, and add an
    explicit "guard the guard" assertion that the weighted/unweighted
    reference implementations actually diverge by a meaningful margin (>10
    counts) before trusting the allclose comparison between them.
    
    Verified red/green: reverting fitting.py's w[i:] weighting makes the
    rewritten test fail; restoring it passes. fitting.py itself is untouched
    by this commit — test-only fix. All 9 Python + 6 JS Tougaard tests pass.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

tests/test_tougaard_background.py

exec
/bin/zsh -lc 'git status --short && git rev-parse --abbrev-ref HEAD && git rev-parse HEAD' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-olmrxtTr' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RtPX8sli' (errno=Operation not permitted)
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HQviJvTW' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-hyRwdATh' (errno=Operation not permitted)
feature-autofit-stage2
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3pKuo8xY' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JDozrtpQ' (errno=Operation not permitted)
03b656aff4ec533bef308447051d4539cfb7af63

codex
The commit metadata matches the stated scope so far: `173f002` changes only `tests/test_tougaard_background.py`. I’m reading the exact assertions now and will compute the weighted/unweighted divergence against the current implementation rather than relying on commit text.
exec
/bin/zsh -lc "sed -n '260,560p' tests/test_tougaard_background.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:

    # The pin only means something if weighted and unweighted actually
    # disagree on this fixture -- guard the guard.
    assert np.max(np.abs(ref - ref_unweighted)) > 10.0, (
        "fixture does not separate weighted from unweighted quadrature -- "
        "endpoint delta too small to survive the F1 anchor, pin is dead"
    )
    assert np.allclose(got, ref, rtol=1e-9), (
        "nonuniform branch does not match spacing-weighted quadrature"
    )


def test_short_input_returns_zeros():
    """< 2 points: no background can be defined; must return zeros."""
    assert np.array_equal(
        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
    )
    assert tougaard_background(np.array([]), np.array([])).size == 0

exec
/bin/zsh -lc "rg -n \"Tougaard|tougaard|background\" tests tests/autofit docs/autofit/inventory scripts --glob '*.json' --glob '*.spec.json' --glob '*.yaml' --glob '*.yml' --glob '*.py' --glob '*.js' --glob '*.ts' 2>/dev/null" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/test_tougaard_background.py:1:"""Tougaard universal-cross-section background — correctness pins.
tests/test_tougaard_background.py:10:   ~20 eV XPS window the shipped "Tougaard" background was essentially
tests/test_tougaard_background.py:11:   flat/zero.  Reference: S. Tougaard, Surf. Interface Anal. 11, 453
tests/test_tougaard_background.py:16:   binding-energy grid; ascending input silently produced a background
tests/test_tougaard_background.py:20:   shirley_background's ascending normalization.
tests/test_tougaard_background.py:23:   trailing background sample identically zero, so the zero-guard always
tests/test_tougaard_background.py:26:   the background to the measured intensity at the HIGH-BE edge of the
tests/test_tougaard_background.py:27:   window (the standard practical Tougaard criterion: B is effectively
tests/test_tougaard_background.py:28:   fitted so the background meets the spectrum above the peak).
tests/test_tougaard_background.py:30:No pre-existing test or fixture pinned the old (wrong) Tougaard output
tests/test_tougaard_background.py:37:from fitting import tougaard_background
tests/test_tougaard_background.py:58:    high-BE side, so the argmax of the background directly locates the
tests/test_tougaard_background.py:66:    # intensity to model, so the honest background is flat and carries no
tests/test_tougaard_background.py:68:    # the background shape it scales is still the pure kernel response.
tests/test_tougaard_background.py:74:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:88:    the identical background (element-wise, after re-reversal)."""
tests/test_tougaard_background.py:92:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:93:    bg_a = tougaard_background(x_a, y_a)
tests/test_tougaard_background.py:108:    bg_d = tougaard_background(x_d, y_d)
tests/test_tougaard_background.py:109:    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
tests/test_tougaard_background.py:117:def test_background_anchored_at_high_be_edge():
tests/test_tougaard_background.py:118:    """The background must equal the measured intensity at the high-BE edge
tests/test_tougaard_background.py:119:    of the window (practical Tougaard criterion: the universal cross-section
tests/test_tougaard_background.py:120:    amplitude is scaled so the background meets the data above the peak),
tests/test_tougaard_background.py:123:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:131:    # still makes the LOSS integral vanish there, so the background equals C0
tests/test_tougaard_background.py:132:    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
tests/test_tougaard_background.py:133:    # Asserting 0.0 here was pinning the bug: it forced the background to dive
tests/test_tougaard_background.py:143:    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
tests/test_tougaard_background.py:154:    That pin asserted all-zeros, which was correct ONLY while the background
tests/test_tougaard_background.py:163:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:174:    Before the offset fix, K(0) = 0 forced the background to zero at the
tests/test_tougaard_background.py:176:    background ramping 0 -> 500 and reported up to 500 counts of phantom
tests/test_tougaard_background.py:180:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:188:def test_background_tracks_low_be_baseline_on_wide_region():
tests/test_tougaard_background.py:190:    large out-of-window inelastic baseline, the background must track that
tests/test_tougaard_background.py:197:    bg = tougaard_background(x, y)
tests/test_tougaard_background.py:220:    bg_uniform = tougaard_background(x, y)
tests/test_tougaard_background.py:223:    bg_nonuniform = tougaard_background(x_jitter, y)
tests/test_tougaard_background.py:245:    got = tougaard_background(xa, ya)
tests/test_tougaard_background.py:273:    """< 2 points: no background can be defined; must return zeros."""
tests/test_tougaard_background.py:275:        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
tests/test_tougaard_background.py:277:    assert tougaard_background(np.array([]), np.array([])).size == 0
tests/autofit/test_candidate_pool.py:153:    (Shirley) as in production — a zeros background makes the height
tests/autofit/test_candidate_pool.py:158:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool.py:342:    background) stay OUT of the pool payload — overcomplete does not mean
tests/autofit/test_candidate_pool.py:344:    background, which absorbs the flat baseline)."""
tests/autofit/test_candidate_pool.py:345:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_stage2_rereview_findings.py:41:    y_fit = fit.lmfit_result.best_fit + fit.background
tests/test_api_analyze_progress.py:14:(instant 400s, unchanged), then spawns a background THREAD (not a
scripts/run_bayesian_real_validation.py:23:  venv/bin/python scripts/run_bayesian_real_validation.py           # full battery (background-scale)
tests/autofit/test_stage2_completeness.py:53:    y_fit = rep.primary_fit.lmfit_result.best_fit + rep.primary_fit.background
tests/autofit/test_stage2_completeness.py:296:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:321:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:372:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:397:    dom = e2.detect_out_of_grammar_dominants(x, y, e2._compute_background(
scripts/run_stress_battery.py:127:    rec = _base(case, off, "least_squares", {"background_method":
tests/autofit/test_cl2p_freewidth.py:136:        name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:148:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:159:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:177:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:190:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:203:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_c1s_parity_gate.py:54:from fitting import shirley_background
tests/autofit/test_c1s_parity_gate.py:171:    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(
scripts/calibrate_cwt_detector.py:13:   linear-drift / sigmoid-step backgrounds x counts 100..50000 x grid
tests/autofit/test_stress_honesty.py:62:        options={"background_method": "linear"})
tests/test_api_analyze.py:104:        "options": {"background_method": "linear"},
tests/autofit/test_resolver.py:120:            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:122:            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
tests/autofit/test_criteria.py:31:                           background=BackgroundType.SHIRLEY,
tests/autofit/test_methods_seam.py:51:    res = m.run(x, y, peak_specs=specs, options={"background_method": "shirley"})
tests/autofit/test_c1s_parity_battery.py:13:   fitting.py's lineshapes + run_fit's background reconstruction reproduces
scripts/summarize_stress_battery.py:226:        "2. **Endpoint-anchored linear background + Lorentzian tails set a "
scripts/summarize_stress_battery.py:231:        "land below the truth-under-wrong-background score by bending "
scripts/summarize_stress_battery.py:234:        "absolute χ²-target criteria are miscalibrated whenever background "
scripts/summarize_stress_battery.py:236:        "the same integral background well (control case χ²ᵣ 1.24). Feeds "
scripts/summarize_stress_battery.py:299:        "tails, background curvature — those honesty cases surface via "
tests/autofit/test_max_entropy.py:69:    """Iterative deconvolution inherently amplifies background noise (~10×
tests/autofit/test_cwt_detector.py:112:    linear backgrounds cancel identically — drift must produce nothing."""
tests/autofit/test_u4f_parity_battery.py:19:# Bounded by background-anchor drift / LACX FP wobble — measured and
tests/autofit/stress_cases.py:10:expressible (linear) in every regime except the background-mismatch regime,
tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
tests/autofit/stress_cases.py:33:the true baseline at the ROI edges — and the engine's LINEAR background is
tests/autofit/stress_cases.py:35:the engine-background χ²ᵣ is therefore not 1: measured 0.96 with the true
tests/autofit/stress_cases.py:36:baseline vs 34 with the engine background at height 90000 (≈2 at 9000 —
tests/autofit/stress_cases.py:38:This is the REALISTIC background-subtraction problem, kept on purpose:
tests/autofit/stress_cases.py:80:    bg: str = "linear"                       # generator background family
tests/autofit/stress_cases.py:95:    """Integral (Shirley-shaped) background: proportional to the signal area
tests/autofit/stress_cases.py:114:    return CandidateModel(name=name, background=bg, slots=tuple(slots))
tests/autofit/stress_cases.py:323:# Regime 6 — background mismatch (Shirley-shaped truth, linear-only fits)
tests/autofit/stress_cases.py:364:    endpoint-anchored linear background.)
tests/autofit/stress_cases.py:418:        notes="integral background fit with a straight line — the mismatch "
tests/autofit/stress_cases.py:425:    The engine's iterative Shirley should absorb the integral background."""
tests/autofit/stress_cases.py:440:        notes="control: matched background family",
tests/autofit/stress_cases.py:488:        # background mismatch + control
tests/autofit/test_preseed_dominants.py:62:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:85:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:104:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:177:    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
tests/autofit/test_preseed_dominants.py:200:    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
tests/autofit/test_preseed_dominants.py:262:    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
tests/autofit/test_preseed_dominants.py:290:    y_fit = (base.primary_fit.lmfit_result.best_fit + base.primary_fit.background)
tests/autofit/test_preseed_dominants.py:298:    bg = eng._compute_background(x, y, aug_model.background)
tests/autofit/test_preseed_dominants.py:368:    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:382:    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:434:             + base_report.primary_fit.background)
tests/autofit/test_bayesian_method.py:35:    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:37:    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:40:    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:254:    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:257:    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
tests/autofit/battery_common.py:28:#   'smart' backgrounds that perturbs the recomputed background by
tests/autofit/battery_common.py:30:#   deviation profile exactly matching the background, not the shapes).
tests/autofit/test_candidate_pool_real_gate.py:101:    det_bg = eng._compute_background(x, y, cands[0].background)
tests/autofit/test_engine_doublet.py:36:    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
tests/autofit/test_engine_doublet.py:134:        name="joint", background=BackgroundType.SHIRLEY,
tests/autofit/test_fit_full_window_option.py:47:    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))
tests/test_browser_cc_overlay_repaint.py:108:# column reads as background (a handful). Returns {blue, white, sampled}.
tests/autofit/test_sparse_map.py:34:    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:160:    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:162:    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
tests/test_browser_identify_frame.py:220:        bg: getComputedStyle(document.getElementById('ref-identify-popover')).backgroundColor })""")
tests/test_browser_identify_frame.py:230:            bg: (()=>{const p=document.getElementById('ref-identify-popover');return p?getComputedStyle(p).backgroundColor:null;})() })""")
tests/test_browser_batch_roi.py:3:The bug: runPropagation() copied only the background fields into each target's
tests/test_browser_batch_roi.py:4:UI, omitting the ROI, so batch fit changed the background but left every target's
tests/test_mixed_ds_lacx_e2e.py:54:    background_method='none',
tests/js/tougaard_twin.test.js:1:// Tougaard background — JS twin of fitting.py's tougaard_background.
tests/js/tougaard_twin.test.js:6:// tests/test_tougaard_background.py):
tests/js/tougaard_twin.test.js:9://      S. Tougaard, Surf. Interface Anal. 11, 453 (1988).
tests/js/tougaard_twin.test.js:23:const match = html.match(/function tougaardBackground\([\s\S]*?\n\}/);
tests/js/tougaard_twin.test.js:24:assert.ok(match, 'tougaardBackground not found in templates/index.html');
tests/js/tougaard_twin.test.js:25:const tougaardBackground = eval('(' + match[0] + ')');
tests/js/tougaard_twin.test.js:56:  // pedestal has no loss intensity to model and yields a flat background with
tests/js/tougaard_twin.test.js:62:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:74:test('ascending and descending BE input give the identical background', () => {
tests/js/tougaard_twin.test.js:76:  const bgDesc = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:77:  const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
tests/js/tougaard_twin.test.js:85:test('background meets the data at BOTH edges (high-BE anchor, low-BE C0)', () => {
tests/js/tougaard_twin.test.js:87:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:93:  // background equals C0 exactly. Asserting 0 pinned the bug: it forced the
tests/js/tougaard_twin.test.js:94:  // background to dive to zero regardless of the data.
tests/js/tougaard_twin.test.js:104:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:115:  //   import numpy as np; from fitting import tougaard_background
tests/js/tougaard_twin.test.js:119:  //   bg = tougaard_background(x, y)
tests/js/tougaard_twin.test.js:134:  const bg = tougaardBackground(be, intensity);
tests/js/tougaard_twin.test.js:144:// caller computeBackgroundCore passed RAW intensity to tougaardBackground
tests/js/tougaard_twin.test.js:148:// (fitting.py run_fit / compute_background_only both do
tests/js/tougaard_twin.test.js:149:// tougaard_background(x, _apply_endpoint_averaging(y, n))).
tests/js/tougaard_twin.test.js:150:test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
tests/js/tougaard_twin.test.js:153:  // Stubs for background types this test never routes to; the eval'd
tests/js/tougaard_twin.test.js:172:  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
tests/js/tougaard_twin.test.js:176:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/js/tougaard_twin.test.js:181:    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
tests/js/batch_propagation.test.js:40:// --- no regression: background propagation behaves exactly as before ---
tests/js/batch_propagation.test.js:41:test('background fields still propagate from source (no regression)', () => {
tests/js/batch_propagation.test.js:42:  const src = ui({ bgType: 'tougaard', bgStart: '690', bgEnd: '750', shirleyIter: '9' });
tests/js/batch_propagation.test.js:45:  assert.strictEqual(out.bgType, 'tougaard');
tests/autofit/test_stress_honesty.py:62:        options={"background_method": "linear"})
tests/autofit/test_stage2_rereview_findings.py:41:    y_fit = fit.lmfit_result.best_fit + fit.background
tests/test_browser_find_peaks_full_window.py:12:background/fit-curve rendering to ``state.fitResult``'s own frozen
tests/test_browser_find_peaks_full_window.py:16:left the chart showing background/fit cropped to whatever OLD, possibly
tests/test_browser_find_peaks_full_window.py:209:def _background_span(pg):
tests/test_browser_find_peaks_full_window.py:211:        const bg = state.chart.data.datasets.find(d => /background/i.test(d.label || ''));
tests/test_browser_find_peaks_full_window.py:229:        before = _background_span(pg)
tests/test_browser_find_peaks_full_window.py:235:        after = _background_span(pg)
tests/test_browser_find_peaks_full_window.py:250:def test_checkbox_on_extends_fit_and_background_to_the_full_window(browser, server):
tests/test_browser_find_peaks_full_window.py:251:    """The actual fix: checked must make the background/fit-curve span
tests/test_browser_find_peaks_full_window.py:268:        before = _background_span(pg)
tests/test_browser_find_peaks_full_window.py:281:        after = _background_span(pg)
tests/test_browser_find_peaks_full_window.py:284:            f"checked must extend the background/fit to the full ROI: {after}")
tests/test_browser_find_peaks_full_window.py:314:    run on a tab) must also render peaks + background across the full
tests/test_browser_find_peaks_full_window.py:334:        after = _background_span(pg)
tests/autofit/stress_cases.py:10:expressible (linear) in every regime except the background-mismatch regime,
tests/autofit/stress_cases.py:23:                   charging replica, wrong background); the method must
tests/autofit/stress_cases.py:33:the true baseline at the ROI edges — and the engine's LINEAR background is
tests/autofit/stress_cases.py:35:the engine-background χ²ᵣ is therefore not 1: measured 0.96 with the true
tests/autofit/stress_cases.py:36:baseline vs 34 with the engine background at height 90000 (≈2 at 9000 —
tests/autofit/stress_cases.py:38:This is the REALISTIC background-subtraction problem, kept on purpose:
tests/autofit/stress_cases.py:80:    bg: str = "linear"                       # generator background family
tests/autofit/stress_cases.py:95:    """Integral (Shirley-shaped) background: proportional to the signal area
tests/autofit/stress_cases.py:114:    return CandidateModel(name=name, background=bg, slots=tuple(slots))
tests/autofit/stress_cases.py:323:# Regime 6 — background mismatch (Shirley-shaped truth, linear-only fits)
tests/autofit/stress_cases.py:364:    endpoint-anchored linear background.)
tests/autofit/stress_cases.py:418:        notes="integral background fit with a straight line — the mismatch "
tests/autofit/stress_cases.py:425:    The engine's iterative Shirley should absorb the integral background."""
tests/autofit/stress_cases.py:440:        notes="control: matched background family",
tests/autofit/stress_cases.py:488:        # background mismatch + control
tests/autofit/test_c1s_parity_battery.py:13:   fitting.py's lineshapes + run_fit's background reconstruction reproduces
tests/autofit/test_methods_seam.py:51:    res = m.run(x, y, peak_specs=specs, options={"background_method": "shirley"})
tests/autofit/test_cwt_detector.py:112:    linear backgrounds cancel identically — drift must produce nothing."""
tests/autofit/test_preseed_dominants.py:62:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:85:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:104:    bg = eng._compute_background(x, y, grammar.candidates[0].background)
tests/autofit/test_preseed_dominants.py:177:    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
tests/autofit/test_preseed_dominants.py:200:    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
tests/autofit/test_preseed_dominants.py:262:    model = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
tests/autofit/test_preseed_dominants.py:290:    y_fit = (base.primary_fit.lmfit_result.best_fit + base.primary_fit.background)
tests/autofit/test_preseed_dominants.py:298:    bg = eng._compute_background(x, y, aug_model.background)
tests/autofit/test_preseed_dominants.py:368:    m = CandidateModel(name="X", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:382:    m0 = CandidateModel(name="Y", background=eng.BackgroundType.LINEAR,
tests/autofit/test_preseed_dominants.py:434:             + base_report.primary_fit.background)
tests/autofit/battery_common.py:28:#   'smart' backgrounds that perturbs the recomputed background by
tests/autofit/battery_common.py:30:#   deviation profile exactly matching the background, not the shapes).
tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",
tests/autofit/test_engine_doublet.py:36:    return CandidateModel(name="doublet", background=BackgroundType.LINEAR,
tests/autofit/test_engine_doublet.py:134:        name="joint", background=BackgroundType.SHIRLEY,
tests/autofit/test_sparse_map.py:34:    model = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:160:    m1 = CandidateModel(name="A", background=BackgroundType.LINEAR,
tests/autofit/test_sparse_map.py:162:    m2 = CandidateModel(name="B", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:35:    one = CandidateModel(name="K1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:37:    two = CandidateModel(name="K2", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:40:    three = CandidateModel(name="K3", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:254:    twin_a = CandidateModel(name="T1", background=BackgroundType.LINEAR,
tests/autofit/test_bayesian_method.py:257:    twin_b = CandidateModel(name="T2", background=BackgroundType.LINEAR,
tests/autofit/test_c1s_parity_gate.py:54:from fitting import shirley_background
tests/autofit/test_c1s_parity_gate.py:171:    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(
tests/autofit/test_u4f_parity_battery.py:19:# Bounded by background-anchor drift / LACX FP wobble — measured and
tests/autofit/test_candidate_pool_real_gate.py:101:    det_bg = eng._compute_background(x, y, cands[0].background)
tests/autofit/test_criteria.py:31:                           background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:120:            CandidateModel(name="FK1", background=BackgroundType.SHIRLEY,
tests/autofit/test_resolver.py:122:            CandidateModel(name="FK2", background=BackgroundType.SHIRLEY,
tests/autofit/test_fit_full_window_option.py:47:    return CandidateModel(name="m", background=BackgroundType.LINEAR, slots=tuple(slots))
tests/autofit/test_max_entropy.py:69:    """Iterative deconvolution inherently amplifies background noise (~10×
tests/autofit/test_cl2p_freewidth.py:136:        name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:148:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:159:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:177:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:190:    cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cl2p_freewidth.py:203:        cand = CandidateModel(name="bad", background=BackgroundType.LINEAR,
tests/autofit/test_cited_values.py:105:        "Tougaard, Surf. Interface Anal. 11, 453 (1988)",
tests/autofit/test_candidate_pool.py:153:    (Shirley) as in production — a zeros background makes the height
tests/autofit/test_candidate_pool.py:158:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:174:        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_candidate_pool.py:342:    background) stay OUT of the pool payload — overcomplete does not mean
tests/autofit/test_candidate_pool.py:344:    background, which absorbs the flat baseline)."""
tests/autofit/test_candidate_pool.py:345:    from autofit.engine import _compute_background
tests/autofit/test_candidate_pool.py:350:    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
tests/autofit/test_stage2_completeness.py:53:    y_fit = rep.primary_fit.lmfit_result.best_fit + rep.primary_fit.background
tests/autofit/test_stage2_completeness.py:296:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:321:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:372:    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
tests/autofit/test_stage2_completeness.py:397:    dom = e2.detect_out_of_grammar_dominants(x, y, e2._compute_background(

exec
/bin/zsh -lc 'git diff --name-status 173f002''^ 173f002 -- fitting.py templates/index.html tests/js/tougaard_twin.test.js autofit/engine.py autofit/methods tests/test_tougaard_background.py && git diff --stat 173f002''^ 173f002 -- fitting.py templates/index.html tests/js/tougaard_twin.test.js autofit/engine.py autofit/methods . '"':(glob)**/*'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-8dZiSFL4' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vDHNv2f3' (errno=Operation not permitted)
M	tests/test_tougaard_background.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-kqliGHcu' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ezFmL0JY' (errno=Operation not permitted)
 tests/test_tougaard_background.py | 28 ++++++++++++++++++++++++++--
 1 file changed, 26 insertions(+), 2 deletions(-)

codex
The test file now has 9 Python tests, with the changed F2 pin ending in the explicit `> 10.0` guard. I also see untracked data fixtures in the worktree, but they are outside this commit; I’ll ignore them unless they affect the requested saved-fit inventory check.
exec
/bin/zsh -lc "sed -n '508,620p' fitting.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
def tougaard_background(
    x: np.ndarray,
    y: np.ndarray,
    n_avg: int = 1,
) -> np.ndarray:
    """Single-pass Tougaard universal-cross-section background, with the
    constant (pre-loss) term the window-limited integral cannot generate.

    Uses the two-parameter universal loss function
    K(T) = B·T / (C + T²)² with B = 2866 eV², C = 1643 eV²
    (S. Tougaard, Surf. Interface Anal. 11, 453 (1988): universal
    cross-section fitted to noble/transition-metal optical data; the
    kernel maximum sits at T = sqrt(C/3) ~= 23.4 eV energy loss).

    FORMULATION (2026-07-17 background audit, finding F1).  The idealized
    Tougaard integral B(E) = Σ_{E' < E} K(E-E')·J(E') assumes the analysis
    window BEGINS in a loss-free region, so that J at the low-BE edge is
    the zero-loss level.  Real windows never satisfy this: at (say) Fe 2p
    there is a large inelastic baseline produced by every lower-BE
    (higher-KE) transition OUTSIDE the window, which a window-limited
    integral structurally cannot reproduce.  Because K(0) = 0, the bare
    integral is identically zero at the low-BE edge REGARDLESS OF THE DATA
    — the background visibly dove to ~0 there, and a flat featureless
    window produced a full-amplitude phantom "signal".

    So the low-BE edge level is taken as a constant offset C0 (the
    out-of-window baseline the kernel cannot see), the kernel runs over the
    net (J - C0), and the amplitude is then anchored so the background
    meets the measured intensity at the HIGH-BE edge — the standard
    practical Tougaard criterion (B is effectively fitted, which is why the
    nominal B_coef cancels; C alone sets the kernel shape).  Equivalent to
    fitting B together with an offset rather than B alone.

    ``n_avg`` averages the first/last ``n_avg`` points before the endpoint
    levels are read, so neither C0 nor the high-BE anchor rests on a single
    noisy sample (see ``_apply_endpoint_averaging``).  n_avg=1 = raw
    endpoints = previous behaviour.

    The background at each binding energy accumulates loss contributions
    from electrons emitted at LOWER BE (higher kinetic energy), so the
    one-sided sum requires a descending-BE grid; input in either BE order
    is normalized internally.  Mirrors the frontend JS twin
    ``tougaardBackground``.
    """
    n = len(x)
    if n < 2:
        return np.zeros_like(y, dtype=float)

    # Universal cross-section constants, Tougaard (1988): B = 2866 eV²,
    # C = 1643 eV². A long-standing transcription slip shipped C = 1643²
    # (~2.7e6 eV²), which pushed the kernel maximum from ~23 eV to ~949 eV
    # of energy loss and flattened the background to ~zero over any real
    # XPS window. Fixed 2026-07-04 together with the JS twin.
    B_coef, C_coef = 2866.0, 1643.0

    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    if n_avg > 1:
        ya = _apply_endpoint_averaging(ya, n_avg)

    # The one-sided loss sum below (j >= i) is physical only when BE
    # DESCENDS along the array: the loss contributions at x[i] must come
    # from lower-BE (higher-KE) emitters, which sit at higher indices only
    # on a descending grid. Normalize to descending internally and flip
    # the result back — the mirror of shirley_background's ascending
    # normalization — so both BE orderings give identical output.
    flipped = bool(xa[0] < xa[-1])
    if flipped:
        xa, ya = xa[::-1].copy(), ya[::-1].copy()

    # C0: the low-BE edge level = index -1 on the descending working array.
    # This is the out-of-window (pre-loss) baseline; the kernel integral is
    # run on the net above it.
    c0 = float(ya[-1])
    net = ya - c0

    dx = float(abs(xa[1] - xa[0]))

    # bg[i] = Σ_{j>=i} K(|x[j]-x[i]|)·net[j]·w[j],  K(T) = B·T / (C + T²)²,
    # w[j] = the local quadrature weight (energy spacing) at point j.
    #
    # On a uniformly spaced grid |x[j]-x[i]| = (j-i)·dx and w[j] == dx, so the
    # kernel depends only on the index gap and this one-sided correlation
    # collapses to a convolution against a single precomputed kernel vector —
    # evaluated in C via np.convolve instead of an n-iteration Python loop
    # (audit F7). On a NONUNIFORM grid neither identity holds, so we keep the
    # exact per-point separation loop AND per-point weights (audit F2,
    # 2026-07-17: the loop previously used exact separations but omitted the
    # spacing weights, silently applying a uniform-grid quadrature inside the
    # branch written precisely because the grid is not uniform — up to ~24%
    # error on a genuinely nonuniform grid). np.gradient returns dx exactly
    # on a uniform grid, so both branches agree to floating point and the
    # uniformity test is a pure optimization, not a semantic fork.
    diffs = np.diff(xa)
    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)

    if uniform:
        m = np.arange(n, dtype=float)
        T = m * dx
        k = (B_coef * T) / (C_coef + T * T) ** 2          # k[m] = K(m·dx)
        # bg[i] = Σ_{m=0}^{n-1-i} k[m]·net[i+m]  =  conv(net, reverse(k))[n-1+i]
        bg = np.convolve(net, k[::-1])[n - 1:] * dx
    else:
        w = np.abs(np.gradient(xa))
        bg = np.zeros(n)
        for i in range(n):
            T = np.abs(xa[i:] - xa[i])
            kernel = (B_coef * T) / (C_coef + T * T) ** 2
            bg[i] = float(np.sum(kernel * net[i:] * w[i:]))

    # Amplitude anchor: scale the loss integral so the background equals the
    # measured intensity at the HIGH-BE edge (index 0 on the descending
    # working array), then sit it on the C0 pedestal. Guard semantics: if NO

exec
/bin/zsh -lc "sed -n '1,240p' tests/js/tougaard_twin.test.js" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "sed -n '4128,4215p' templates/index.html" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
}

// Single-pass Tougaard background — JS twin of fitting.py's
// tougaard_background (keep the two numerically in agreement; pinned by
// tests/js/tougaard_twin.test.js). Universal loss kernel
// K(T) = B·T/(C+T²)² with B = 2866 eV², C = 1643 eV² (S. Tougaard,
// Surf. Interface Anal. 11, 453 (1988); kernel max at sqrt(C/3) ≈ 23.4 eV).
// C was long shipped squared (1643*1643) — fixed 2026-07-04 with the backend.
function tougaardBackground(be, intensity, nAvg) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);
  const B = 2866, C = 1643;
  // The one-sided loss sum (j >= i) is physical only on a DESCENDING BE
  // grid (loss contributions come from lower-BE / higher-KE emitters).
  // Normalize to descending internally and flip back, like the backend.
  const flipped = be[0] < be[n - 1];
  const beW = flipped ? [...be].reverse() : be;
  let inW = flipped ? [...intensity].reverse() : intensity;
  if (nAvg > 1) inW = _applyEndpointAveraging(inW, nAvg);
  // C0 — the pre-loss constant (F1, 2026-07-17). The idealized Tougaard
  // integral assumes the window BEGINS loss-free, so J at the low-BE edge is
  // the zero-loss level. Real windows never satisfy that: the out-of-window
  // inelastic baseline from every lower-BE (higher-KE) transition cannot be
  // reproduced by a window-limited integral, and since K(0) = 0 the bare
  // integral is identically zero at the low-BE edge REGARDLESS of the data —
  // the background dove to ~0 there and a flat window produced phantom
  // signal. Take the low-BE level as a constant offset, run the kernel over
  // the net above it, then anchor the amplitude at the high-BE edge.
  const c0 = inW[n - 1];
  // Local quadrature weights (F2, 2026-07-17): weight each term by its own
  // energy spacing instead of a single dx lifted from the first two points,
  // which silently assumed a uniform grid.
  const w = new Array(n);
  for (let i = 0; i < n; i++) {
    if (i === 0) w[0] = Math.abs(beW[1] - beW[0]);
    else if (i === n - 1) w[n - 1] = Math.abs(beW[n - 1] - beW[n - 2]);
    else w[i] = Math.abs(beW[i + 1] - beW[i - 1]) / 2;
  }
  const bg = new Array(n).fill(0);
  for (let i = 0; i < n; i++) {
    let sum = 0;
    for (let j = i; j < n; j++) {
      const T = Math.abs(beW[j] - beW[i]);
      sum += (B * T) / Math.pow(C + T * T, 2) * (inW[j] - c0) * w[j];
    }
    bg[i] = sum;
  }
  // Amplitude anchor at the HIGH-BE edge (index 0 after normalization):
  // scale so the background meets the measured intensity above the peak —
  // the practical Tougaard criterion (B effectively fitted; C alone sets the
  // kernel shape). Guard: if no net loss signal accumulates at the high-BE
  // edge (bg[0] === 0 — e.g. a flat or empty window) the honest background is
  // the flat pre-loss level C0 itself, NOT zeros; zeros would report the
  // whole baseline as net signal (the pre-F1 behaviour). Negative counts
  // (physically invalid input) pass through signed; no clamping here.
  let out;
  if (bg[0] === 0) {
    out = new Array(n).fill(c0);
  } else {
    const scale = (inW[0] - c0) / bg[0];
    out = bg.map(v => c0 + v * scale);
  }
  return flipped ? out.reverse() : out;
}

// Apply endpoint averaging: replace first/last N points with their mean so
// existing Shirley/Smart functions pick up averaged endpoint intensities.
// Returns a new array — does not mutate the input.
function _applyEndpointAveraging(intensity, nAvg) {
  const n = intensity.length;
  if (nAvg <= 1 || n < 4) return intensity;
  const cap = Math.min(nAvg, Math.floor(n / 4));
  const out = [...intensity];
  let sumL = 0, sumR = 0;
  for (let i = 0; i < cap; i++) sumL += intensity[i];
  for (let i = n - cap; i < n; i++) sumR += intensity[i];
  const avgL = sumL / cap, avgR = sumR / cap;
  for (let i = 0; i < cap; i++) out[i] = avgL;
  for (let i = n - cap; i < n; i++) out[i] = avgR;
  return out;
}

// Shirley + Linear: a linear baseline plus a Shirley-like cumulative correction.
// Completely standalone — does not call shirleyBackground / smartBackground.
function shirleyLinearBackground(be, intensity, maxIter, nAvg) {
  const n = be.length;
  if (n < 2) return new Array(n).fill(0);


exec
/bin/zsh -lc 'git diff --name-only 173f002''^ 173f002 && git diff -- 173f002''^ 173f002 -- tests/test_tougaard_background.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6sZ1Rgg1' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uNPUh97s' (errno=Operation not permitted)
tests/test_tougaard_background.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Vrrqs5pq' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1aeKoiPw' (errno=Operation not permitted)

exec
/bin/zsh -lc "sed -n '620,685p' fitting.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    # working array), then sit it on the C0 pedestal. Guard semantics: if NO
    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
    # flat or empty window), the honest background is the flat pre-loss level
    # C0 itself, NOT zeros: a featureless window contains no loss signal to
    # model, and returning zeros would report the entire baseline as net
    # signal (the pre-F1 behaviour). Negative counts (physically invalid
    # input) pass through signed; no clamping policy is imposed here.
    if bg[0] == 0.0:
        out = np.full(n, c0)
    else:
        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])
    return out[::-1] if flipped else out


def _la_casaxps_true(
    x: np.ndarray,
    amplitude: float,
    center: float,
    fwhm: float,
    alpha: float,
    beta: float,
    m: float,
) -> np.ndarray:
    """
    True CasaXPS LA(α, β, m) lineshape.

    Built in two steps per the CasaXPS LA manual:

    1.  Asymmetric base Lorentzian. Start with a unit-amplitude Lorentzian
        of FWHM `fwhm` centered at `center`:
            L(x) = 1 / (1 + 4·((x − center)/fwhm)²)
        Apply piecewise exponents to introduce asymmetry. CasaXPS defines
        these on a kinetic-energy axis. We use a binding-energy axis, so
        the sides flip:
            LA_base(x) = L(x)^α   for x ≥ center  (high-BE side)
            LA_base(x) = L(x)^β   for x <  center  (low-BE side)
        Increasing α relative to β SUPPRESSES the high-BE tail; decreasing
        α extends it.

    2.  Gaussian convolution with an integer-point kernel of width `m`.
        m=0 means no convolution. For m>0, build a discrete Gaussian
        kernel of length 2m+1 with σ_pts = m/3 (so the 3σ tail just
        reaches the kernel edge). Convolve with mode='same' on the
        uniform x grid.

    With α=β=1 and m=0, this reduces exactly to amplitude × L(x) (a pure
    Lorentzian of peak height = amplitude, FWHM = `fwhm`).

    Parameters
    ----------
    fwhm  : Lorentzian FWHM in eV (must be > 0)
    alpha : high-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    beta  : low-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    m     : Gaussian convolution kernel width in DATA POINTS (not eV);
            integer 0–499. Stored as float in lmfit, rounded to int here.
    """
    fwhm = max(float(fwhm), 1e-9)
    alpha = max(float(alpha), 1e-3)
    beta = max(float(beta), 1e-3)
    # Continuous-σ kernel: m flows through to the kernel weights as a real
    # number, so the Jacobian column for m is well-defined under lmfit's
    # finite-difference perturbation. Previously m was rounded with
    # int(round(m)), making the function locally constant in m and
    # producing a singular Hessian whenever m varied — that poisoned
    # covariance estimation for every other free param too.
    # Defensive guard preserves the prior [0, 499] cap in case a saved

exec
/bin/zsh -lc "rg --files docs/autofit/inventory tests tests/autofit scripts 2>/dev/null | rg '\\.(json|fit\\.json|proj\\.json|spec\\.json)"'$|fixture|inventory'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
scripts/gen_c1s_battery_fixture.py
scripts/gen_region_battery_fixture.py
scripts/gen_u4f_battery_fixture.py
docs/autofit/inventory/sensitivity_sweeps.jsonl
docs/autofit/inventory/acquisition_exhaustion.json
docs/autofit/inventory/bayesian_u4f_tuned_run.jsonl
docs/autofit/inventory/stress_battery_runs.jsonl
docs/autofit/inventory/bayesian_real_validation_runs.jsonl
docs/autofit/inventory/cwt_calibration.jsonl
docs/autofit/inventory/replicate_noise_survey.json
docs/autofit/inventory/reference_fits_inventory.json
tests/fixtures/machine_records_snapshot.json
tests/fixtures/curated_records_snapshot.json
tests/fixtures/regen_curated_snapshot.py
tests/fixtures/xps_legacy_snapshot.json
tests/autofit/fixtures/c1s_battery_expected.json
tests/autofit/fixtures/u4f_battery_expected.json
tests/autofit/fixtures/b1s_battery_expected.json
tests/autofit/fixtures/example_cited_values.json
tests/autofit/fixtures/cl2p_battery_expected.json
tests/autofit/fixtures/c1s_battery_expected.json
tests/autofit/fixtures/u4f_battery_expected.json
tests/autofit/fixtures/b1s_battery_expected.json
tests/autofit/fixtures/example_cited_values.json
tests/autofit/fixtures/cl2p_battery_expected.json

exec
/bin/zsh -lc "find docs/autofit/inventory tests tests/autofit scripts -type f \\( -name '*.json' -o -name '*.fit.json' -o -name '*.proj.json' -o -name '*.spec.json' -o -name '*.js' -o -name '*.py' \\) -print 2>/dev/null | wc -l" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     160

exec
/bin/zsh -lc 'git show --numstat --format= 173f002 && git diff --name-status 173f002''^ 173f002 -- app.py fitting.py templates/index.html tests/js/tougaard_twin.test.js autofit/engine.py autofit/methods tests/test_tougaard_background.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ir4oRb08' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-vmDoVqGV' (errno=Operation not permitted)
26	2	tests/test_tougaard_background.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tqQiczrp' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-oP7HKoQR' (errno=Operation not permitted)
M	tests/test_tougaard_background.py

codex
The production anchor path is as expected: `scale = (ya[0] - c0) / bg[0]`, with negative scales deliberately passed through signed. Next I’m running a standalone numerical reproduction of the test’s exact fixture plus an unweighted local implementation to prove whether the assertion goes red.
codex
The read-only sandbox blocks shell here-docs because zsh tries to create a temp file. I’m switching to `python -c` so the computation can run without writing into the workspace.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python -c $'"'import numpy as np\\nfrom fitting import tougaard_background\\nB_coef, C_coef = 2866.0, 1643.0\\ndef tougaard_unweighted_nonuniform(x, y):\\n    n = len(x)\\n    if n < 2:\\n        return np.zeros_like(y, dtype=float)\\n    xa = np.asarray(x, dtype=float)\\n    ya = np.asarray(y, dtype=float)\\n    flipped = bool(xa[0] < xa[-1])\\n    if flipped:\\n        xa, ya = xa[::-1].copy(), ya[::-1].copy()\\n    c0 = float(ya[-1])\\n    net = ya - c0\\n    dx = float(abs(xa[1] - xa[0]))\\n    diffs = np.diff(xa)\\n    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)\\n    if uniform:\\n        m = np.arange(n, dtype=float)\\n        T = m * dx\\n        k = (B_coef * T) / (C_coef + T * T) ** 2\\n        bg = np.convolve(net, k[::-1])[n - 1:] * dx\\n    else:\\n        bg = np.zeros(n)\\n        for i in range(n):\\n            T = np.abs(xa[i:] - xa[i])\\n            kernel = (B_coef * T) / (C_coef + T * T) ** 2\\n            bg[i] = float(np.sum(kernel * net[i:]))\\n    if bg[0] == 0.0:\\n        out = np.full(n, c0)\\n    else:\\n        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])\\n    return out[::-1] if flipped else out\\nx = np.linspace(740.0, 700.0, 300)\\ny = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))\\nbg_uniform = tougaard_background(x, y)\\nx_jitter = x.copy()\\nx_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))\\nbg_nonuniform_good = tougaard_background(x_jitter, y)\\nbg_nonuniform_unweighted = tougaard_unweighted_nonuniform(x_jitter, y)\\nxa = np.concatenate([np.linspace(740.0, 720.1, 60), np.linspace(720.0, 700.0, 400)])\\nya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(-0.5 * ((xa - 710.9) / 1.6) ** 2)\\ngot = tougaard_background(xa, ya)\\ngot_unweighted = tougaard_unweighted_nonuniform(xa, ya)\\nc0 = float(ya[-1])\\nnet = ya - c0\\nw = np.abs(np.gradient(xa))\\nraw_weighted = np.zeros(len(xa))\\nraw_unweighted = np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T = np.abs(xa[i:] - xa[i])\\n    kernel = (B_coef * T) / (C_coef + T * T) ** 2\\n    raw_weighted[i] = float(np.sum(kernel * net[i:] * w[i:]))\\n    raw_unweighted[i] = float(np.sum(kernel * net[i:]))\\nref = c0 + raw_weighted * ((float(ya[0]) - c0) / raw_weighted[0])\\nref_unweighted = c0 + raw_unweighted * ((float(ya[0]) - c0) / raw_unweighted[0])\\ndef check_allclose(a, b, rtol=1e-9):\\n    d = np.abs(a-b)\\n    return bool(np.allclose(a, b, rtol=rtol)), float(np.max(d)), int(np.argmax(d))\\nprint(\"endpoint ya[0], ya[-1], delta:\", float(ya[0]), float(ya[-1]), float(ya[0]-ya[-1]))\\nprint(\"raw weighted bg[0], anchor scale:\", float(raw_weighted[0]), float((ya[0]-c0)/raw_weighted[0]))\\nprint(\"raw unweighted bg[0], anchor scale:\", float(raw_unweighted[0]), float((ya[0]-c0)/raw_unweighted[0]))\\nprint(\"weighted vs unweighted ref max diff:\", float(np.max(np.abs(ref-ref_unweighted))), \"idx\", int(np.argmax(np.abs(ref-ref_unweighted))))\\nprint(\"current got vs ref allclose/maxdiff/idx:\", check_allclose(got, ref))\\nprint(\"unweighted production vs ref allclose/maxdiff/idx:\", check_allclose(got_unweighted, ref))\\nprint(\"unweighted production vs ref_unweighted allclose/maxdiff/idx:\", check_allclose(got_unweighted, ref_unweighted))\\nprint(\"near-uniform good max diff:\", float(np.max(np.abs(bg_uniform-bg_nonuniform_good))))\\nprint(\"near-uniform unweighted max diff:\", float(np.max(np.abs(bg_uniform-bg_nonuniform_unweighted))))\\nprint(\"near-uniform good passes <0.1:\", bool(np.max(np.abs(bg_uniform-bg_nonuniform_good)) < 1e-1))\\nprint(\"near-uniform unweighted passes <0.1:\", bool(np.max(np.abs(bg_uniform-bg_nonuniform_unweighted)) < 1e-1))\\nprint(\"guard > 10:\", bool(np.max(np.abs(ref-ref_unweighted)) > 10.0))\\n'" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

codex
`python` is not on PATH here, so I’m retrying with `python3`.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import numpy as np\\nfrom fitting import tougaard_background\\nB_coef, C_coef = 2866.0, 1643.0\\ndef tougaard_unweighted_nonuniform(x, y):\\n    n = len(x)\\n    if n < 2:\\n        return np.zeros_like(y, dtype=float)\\n    xa = np.asarray(x, dtype=float)\\n    ya = np.asarray(y, dtype=float)\\n    flipped = bool(xa[0] < xa[-1])\\n    if flipped:\\n        xa, ya = xa[::-1].copy(), ya[::-1].copy()\\n    c0 = float(ya[-1])\\n    net = ya - c0\\n    dx = float(abs(xa[1] - xa[0]))\\n    diffs = np.diff(xa)\\n    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)\\n    if uniform:\\n        m = np.arange(n, dtype=float)\\n        T = m * dx\\n        k = (B_coef * T) / (C_coef + T * T) ** 2\\n        bg = np.convolve(net, k[::-1])[n - 1:] * dx\\n    else:\\n        bg = np.zeros(n)\\n        for i in range(n):\\n            T = np.abs(xa[i:] - xa[i])\\n            kernel = (B_coef * T) / (C_coef + T * T) ** 2\\n            bg[i] = float(np.sum(kernel * net[i:]))\\n    if bg[0] == 0.0:\\n        out = np.full(n, c0)\\n    else:\\n        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])\\n    return out[::-1] if flipped else out\\nx = np.linspace(740.0, 700.0, 300)\\ny = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))\\nbg_uniform = tougaard_background(x, y)\\nx_jitter = x.copy()\\nx_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))\\nbg_nonuniform_good = tougaard_background(x_jitter, y)\\nbg_nonuniform_unweighted = tougaard_unweighted_nonuniform(x_jitter, y)\\nxa = np.concatenate([np.linspace(740.0, 720.1, 60), np.linspace(720.0, 700.0, 400)])\\nya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(-0.5 * ((xa - 710.9) / 1.6) ** 2)\\ngot = tougaard_background(xa, ya)\\ngot_unweighted = tougaard_unweighted_nonuniform(xa, ya)\\nc0 = float(ya[-1])\\nnet = ya - c0\\nw = np.abs(np.gradient(xa))\\nraw_weighted = np.zeros(len(xa))\\nraw_unweighted = np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T = np.abs(xa[i:] - xa[i])\\n    kernel = (B_coef * T) / (C_coef + T * T) ** 2\\n    raw_weighted[i] = float(np.sum(kernel * net[i:] * w[i:]))\\n    raw_unweighted[i] = float(np.sum(kernel * net[i:]))\\nref = c0 + raw_weighted * ((float(ya[0]) - c0) / raw_weighted[0])\\nref_unweighted = c0 + raw_unweighted * ((float(ya[0]) - c0) / raw_unweighted[0])\\ndef check_allclose(a, b, rtol=1e-9):\\n    d = np.abs(a-b)\\n    return bool(np.allclose(a, b, rtol=rtol)), float(np.max(d)), int(np.argmax(d))\\nprint(\"endpoint ya[0], ya[-1], delta:\", float(ya[0]), float(ya[-1]), float(ya[0]-ya[-1]))\\nprint(\"raw weighted bg[0], anchor scale:\", float(raw_weighted[0]), float((ya[0]-c0)/raw_weighted[0]))\\nprint(\"raw unweighted bg[0], anchor scale:\", float(raw_unweighted[0]), float((ya[0]-c0)/raw_unweighted[0]))\\nprint(\"weighted vs unweighted ref max diff:\", float(np.max(np.abs(ref-ref_unweighted))), \"idx\", int(np.argmax(np.abs(ref-ref_unweighted))))\\nprint(\"current got vs ref allclose/maxdiff/idx:\", check_allclose(got, ref))\\nprint(\"unweighted production vs ref allclose/maxdiff/idx:\", check_allclose(got_unweighted, ref))\\nprint(\"unweighted production vs ref_unweighted allclose/maxdiff/idx:\", check_allclose(got_unweighted, ref_unweighted))\\nprint(\"near-uniform good max diff:\", float(np.max(np.abs(bg_uniform-bg_nonuniform_good))))\\nprint(\"near-uniform unweighted max diff:\", float(np.max(np.abs(bg_uniform-bg_nonuniform_unweighted))))\\nprint(\"near-uniform good passes <0.1:\", bool(np.max(np.abs(bg_uniform-bg_nonuniform_good)) < 1e-1))\\nprint(\"near-uniform unweighted passes <0.1:\", bool(np.max(np.abs(bg_uniform-bg_nonuniform_unweighted)) < 1e-1))\\nprint(\"guard > 10:\", bool(np.max(np.abs(ref-ref_unweighted)) > 10.0))\\n'" in /Users/skyefortier/xps-verify
 exited 1 in 120ms:
Traceback (most recent call last):
  File "<string>", line 2, in <module>
  File "/Users/skyefortier/xps-verify/fitting.py", line 30, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

codex
The system Python lacks `lmfit`, so importing `fitting.py` fails. I found the repo likely has a venv; I’ll use that interpreter for parity with the project tests.
exec
/bin/zsh -lc "rg --files -g 'python' -g 'python3' -g 'pytest' -g 'node' .venv venv env 2>/dev/null" in /Users/skyefortier/xps-verify
 exited 2 in 0ms:
exec
/bin/zsh -lc 'ls -la' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
total 560
drwxr-xr-x   29 skyefortier  staff    928 Jul 17 15:35 .
drwxr-xr-x+  74 skyefortier  staff   2368 Jul 17 16:00 ..
-rw-r--r--    1 skyefortier  staff     61 Jul 10 15:28 .git
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 .github
-rw-r--r--    1 skyefortier  staff    111 Jul 10 15:28 .gitignore
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 .impeccable
drwxr-xr-x    6 skyefortier  staff    192 Jul 10 19:53 .pytest_cache
drwxr-xr-x   27 skyefortier  staff    864 Jul 16 12:39 .stage9
-rw-r--r--    1 skyefortier  staff  20250 Jul 10 15:28 CLAUDE.md
-rw-r--r--    1 skyefortier  staff   2656 Jul 10 15:28 DEPLOY.md
-rw-r--r--    1 skyefortier  staff   8758 Jul 10 15:28 DESIGN.md
-rw-r--r--    1 skyefortier  staff   2735 Jul 10 15:28 PRODUCT.md
drwxr-xr-x    7 skyefortier  staff    224 Jul 17 16:04 __pycache__
-rw-r--r--    1 skyefortier  staff  52614 Jul 13 11:59 app.py
drwxr-xr-x   20 skyefortier  staff    640 Jul 17 15:33 autofit
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 data
drwxr-xr-x    6 skyefortier  staff    192 Jul 10 15:28 docs
-rw-r--r--    1 skyefortier  staff  55991 Jul 17 16:04 fitting.py
-rw-r--r--    1 skyefortier  staff  19994 Jul 10 15:28 parser.py
-rw-r--r--    1 skyefortier  staff    319 Jul 10 15:28 requirements-dev.txt
-rw-r--r--    1 skyefortier  staff    446 Jul 10 15:28 requirements.txt
drwxr-xr-x   22 skyefortier  staff    704 Jul 10 21:01 scripts
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 static
drwxr-xr-x    4 skyefortier  staff    128 Jul 17 15:30 templates
drwxr-xr-x   38 skyefortier  staff   1216 Jul 17 16:03 tests
drwxr-xr-x  159 skyefortier  staff   5088 Jul 17 15:49 uploads
-rw-r--r--    1 skyefortier  staff   6062 Jul 10 15:28 vgd_parser.py
-rw-r--r--    1 skyefortier  staff  68252 Jul 10 15:28 xps-fitting-tool.html
-rw-r--r--    1 skyefortier  staff  18124 Jul 10 15:28 xps_reference.py

exec
/bin/zsh -lc 'ls -la venv/bin .venv/bin 2>/dev/null' in /Users/skyefortier/xps-verify
 exited 1 in 0ms:
codex
There is no visible `venv` or `.venv` in this checkout. Since `tougaard_background` itself does not depend on `lmfit`, I’m going to stub the `lmfit` import for the numerical review and keep test execution separate.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types\\nlmfit = types.ModuleType(\"lmfit\")\\nlmfit.Model = object\\nlmfit.Parameters = object\\nsys.modules[\"lmfit\"] = lmfit\\nimport numpy as np\\nfrom fitting import tougaard_background\\nB_coef, C_coef = 2866.0, 1643.0\\ndef tougaard_unweighted_nonuniform(x, y):\\n    n = len(x)\\n    if n < 2:\\n        return np.zeros_like(y, dtype=float)\\n    xa = np.asarray(x, dtype=float)\\n    ya = np.asarray(y, dtype=float)\\n    flipped = bool(xa[0] < xa[-1])\\n    if flipped:\\n        xa, ya = xa[::-1].copy(), ya[::-1].copy()\\n    c0 = float(ya[-1])\\n    net = ya - c0\\n    dx = float(abs(xa[1] - xa[0]))\\n    diffs = np.diff(xa)\\n    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)\\n    if uniform:\\n        m = np.arange(n, dtype=float)\\n        T = m * dx\\n        k = (B_coef * T) / (C_coef + T * T) ** 2\\n        bg = np.convolve(net, k[::-1])[n - 1:] * dx\\n    else:\\n        bg = np.zeros(n)\\n        for i in range(n):\\n            T = np.abs(xa[i:] - xa[i])\\n            kernel = (B_coef * T) / (C_coef + T * T) ** 2\\n            bg[i] = float(np.sum(kernel * net[i:]))\\n    if bg[0] == 0.0:\\n        out = np.full(n, c0)\\n    else:\\n        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])\\n    return out[::-1] if flipped else out\\nx = np.linspace(740.0, 700.0, 300)\\ny = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))\\nbg_uniform = tougaard_background(x, y)\\nx_jitter = x.copy()\\nx_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))\\nbg_nonuniform_good = tougaard_background(x_jitter, y)\\nbg_nonuniform_unweighted = tougaard_unweighted_nonuniform(x_jitter, y)\\nxa = np.concatenate([np.linspace(740.0, 720.1, 60), np.linspace(720.0, 700.0, 400)])\\nya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(-0.5 * ((xa - 710.9) / 1.6) ** 2)\\ngot = tougaard_background(xa, ya)\\ngot_unweighted = tougaard_unweighted_nonuniform(xa, ya)\\nc0 = float(ya[-1])\\nnet = ya - c0\\nw = np.abs(np.gradient(xa))\\nraw_weighted = np.zeros(len(xa))\\nraw_unweighted = np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T = np.abs(xa[i:] - xa[i])\\n    kernel = (B_coef * T) / (C_coef + T * T) ** 2\\n    raw_weighted[i] = float(np.sum(kernel * net[i:] * w[i:]))\\n    raw_unweighted[i] = float(np.sum(kernel * net[i:]))\\nref = c0 + raw_weighted * ((float(ya[0]) - c0) / raw_weighted[0])\\nref_unweighted = c0 + raw_unweighted * ((float(ya[0]) - c0) / raw_unweighted[0])\\ndef check_allclose(a, b, rtol=1e-9):\\n    d = np.abs(a-b)\\n    return bool(np.allclose(a, b, rtol=rtol)), float(np.max(d)), int(np.argmax(d))\\nprint(\"endpoint ya[0], ya[-1], delta:\", float(ya[0]), float(ya[-1]), float(ya[0]-ya[-1]))\\nprint(\"raw weighted bg[0], anchor scale:\", float(raw_weighted[0]), float((ya[0]-c0)/raw_weighted[0]))\\nprint(\"raw unweighted bg[0], anchor scale:\", float(raw_unweighted[0]), float((ya[0]-c0)/raw_unweighted[0]))\\nprint(\"weighted vs unweighted ref max diff:\", float(np.max(np.abs(ref-ref_unweighted))), \"idx\", int(np.argmax(np.abs(ref-ref_unweighted))))\\nprint(\"current got vs ref allclose/maxdiff/idx:\", check_allclose(got, ref))\\nprint(\"unweighted production vs ref allclose/maxdiff/idx:\", check_allclose(got_unweighted, ref))\\nprint(\"unweighted production vs ref_unweighted allclose/maxdiff/idx:\", check_allclose(got_unweighted, ref_unweighted))\\nprint(\"near-uniform good max diff:\", float(np.max(np.abs(bg_uniform-bg_nonuniform_good))))\\nprint(\"near-uniform unweighted max diff:\", float(np.max(np.abs(bg_uniform-bg_nonuniform_unweighted))))\\nprint(\"near-uniform good passes <0.1:\", bool(np.max(np.abs(bg_uniform-bg_nonuniform_good)) < 1e-1))\\nprint(\"near-uniform unweighted passes <0.1:\", bool(np.max(np.abs(bg_uniform-bg_nonuniform_unweighted)) < 1e-1))\\nprint(\"guard > 10:\", bool(np.max(np.abs(ref-ref_unweighted)) > 10.0))\\n'" in /Users/skyefortier/xps-verify
 exited 1 in 101ms:
codex
`scipy` is also missing from the system interpreter. I’ll stub only the imported `scipy.integrate.trapezoid` symbol so the real `tougaard_background` function can be imported and exercised.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types\\nlmfit = types.ModuleType(\"lmfit\")\\nlmfit.Model = object\\nlmfit.Parameters = object\\nsys.modules[\"lmfit\"] = lmfit\\nscipy = types.ModuleType(\"scipy\")\\nintegrate = types.ModuleType(\"scipy.integrate\")\\ndef trapezoid(*args, **kwargs):\\n    raise RuntimeError(\"trapezoid stub should not be used by tougaard test\")\\nintegrate.trapezoid = trapezoid\\nscipy.integrate = integrate\\nsys.modules[\"scipy\"] = scipy\\nsys.modules[\"scipy.integrate\"] = integrate\\nimport numpy as np\\nfrom fitting import tougaard_background\\nB_coef, C_coef = 2866.0, 1643.0\\ndef tougaard_unweighted_nonuniform(x, y):\\n    n = len(x)\\n    if n < 2:\\n        return np.zeros_like(y, dtype=float)\\n    xa = np.asarray(x, dtype=float)\\n    ya = np.asarray(y, dtype=float)\\n    flipped = bool(xa[0] < xa[-1])\\n    if flipped:\\n        xa, ya = xa[::-1].copy(), ya[::-1].copy()\\n    c0 = float(ya[-1])\\n    net = ya - c0\\n    dx = float(abs(xa[1] - xa[0]))\\n    diffs = np.diff(xa)\\n    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)\\n    if uniform:\\n        m = np.arange(n, dtype=float)\\n        T = m * dx\\n        k = (B_coef * T) / (C_coef + T * T) ** 2\\n        bg = np.convolve(net, k[::-1])[n - 1:] * dx\\n    else:\\n        bg = np.zeros(n)\\n        for i in range(n):\\n            T = np.abs(xa[i:] - xa[i])\\n            kernel = (B_coef * T) / (C_coef + T * T) ** 2\\n            bg[i] = float(np.sum(kernel * net[i:]))\\n    if bg[0] == 0.0:\\n        out = np.full(n, c0)\\n    else:\\n        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])\\n    return out[::-1] if flipped else out\\nx = np.linspace(740.0, 700.0, 300)\\ny = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))\\nbg_uniform = tougaard_background(x, y)\\nx_jitter = x.copy()\\nx_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))\\nbg_nonuniform_good = tougaard_background(x_jitter, y)\\nbg_nonuniform_unweighted = tougaard_unweighted_nonuniform(x_jitter, y)\\nxa = np.concatenate([np.linspace(740.0, 720.1, 60), np.linspace(720.0, 700.0, 400)])\\nya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(-0.5 * ((xa - 710.9) / 1.6) ** 2)\\ngot = tougaard_background(xa, ya)\\ngot_unweighted = tougaard_unweighted_nonuniform(xa, ya)\\nc0 = float(ya[-1])\\nnet = ya - c0\\nw = np.abs(np.gradient(xa))\\nraw_weighted = np.zeros(len(xa))\\nraw_unweighted = np.zeros(len(xa))\\nfor i in range(len(xa)):\\n    T = np.abs(xa[i:] - xa[i])\\n    kernel = (B_coef * T) / (C_coef + T * T) ** 2\\n    raw_weighted[i] = float(np.sum(kernel * net[i:] * w[i:]))\\n    raw_unweighted[i] = float(np.sum(kernel * net[i:]))\\nref = c0 + raw_weighted * ((float(ya[0]) - c0) / raw_weighted[0])\\nref_unweighted = c0 + raw_unweighted * ((float(ya[0]) - c0) / raw_unweighted[0])\\ndef check_allclose(a, b, rtol=1e-9):\\n    d = np.abs(a-b)\\n    return bool(np.allclose(a, b, rtol=rtol)), float(np.max(d)), int(np.argmax(d))\\nprint(\"endpoint ya[0], ya[-1], delta:\", float(ya[0]), float(ya[-1]), float(ya[0]-ya[-1]))\\nprint(\"raw weighted bg[0], anchor scale:\", float(raw_weighted[0]), float((ya[0]-c0)/raw_weighted[0]))\\nprint(\"raw unweighted bg[0], anchor scale:\", float(raw_unweighted[0]), float((ya[0]-c0)/raw_unweighted[0]))\\nprint(\"weighted vs unweighted ref max diff:\", float(np.max(np.abs(ref-ref_unweighted))), \"idx\", int(np.argmax(np.abs(ref-ref_unweighted))))\\nprint(\"current got vs ref allclose/maxdiff/idx:\", check_allclose(got, ref))\\nprint(\"unweighted production vs ref allclose/maxdiff/idx:\", check_allclose(got_unweighted, ref))\\nprint(\"unweighted production vs ref_unweighted allclose/maxdiff/idx:\", check_allclose(got_unweighted, ref_unweighted))\\nprint(\"near-uniform good max diff:\", float(np.max(np.abs(bg_uniform-bg_nonuniform_good))))\\nprint(\"near-uniform unweighted max diff:\", float(np.max(np.abs(bg_uniform-bg_nonuniform_unweighted))))\\nprint(\"near-uniform good passes <0.1:\", bool(np.max(np.abs(bg_uniform-bg_nonuniform_good)) < 1e-1))\\nprint(\"near-uniform unweighted passes <0.1:\", bool(np.max(np.abs(bg_uniform-bg_nonuniform_unweighted)) < 1e-1))\\nprint(\"guard > 10:\", bool(np.max(np.abs(ref-ref_unweighted)) > 10.0))\\n'" in /Users/skyefortier/xps-verify
 succeeded in 135ms:
endpoint ya[0], ya[-1], delta: 4800.0 4000.0000005015495 799.9999994984505
raw weighted bg[0], anchor scale: 470.200100113026 1.7014032946954876
raw unweighted bg[0], anchor scale: 7803.418538117508 0.10251917100059098
weighted vs unweighted ref max diff: 104.82975035097024 idx 41
current got vs ref allclose/maxdiff/idx: (True, 0.0, 0)
unweighted production vs ref allclose/maxdiff/idx: (False, 104.82975035097024, 41)
unweighted production vs ref_unweighted allclose/maxdiff/idx: (True, 0.0, 0)
near-uniform good max diff: 3.637978807091713e-12
near-uniform unweighted max diff: 3.637978807091713e-12
near-uniform good passes <0.1: True
near-uniform unweighted passes <0.1: True
guard > 10: True

codex
The core calculation closes the prior hole: the fixture has an endpoint delta of about 800 counts, the anchored weighted/unweighted references differ by about 104.83 counts, and an unweighted production variant fails the test’s `allclose`. I’m checking executable test status now; missing Python deps may limit the Python side to this direct re-verification.
exec
/bin/zsh -lc 'node --test tests/js/tougaard_twin.test.js' in /Users/skyefortier/xps-verify
 succeeded in 153ms:
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 1 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 13.463772
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 2 - ascending and descending BE input give the identical background
  ---
  duration_ms: 0.662006
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 3 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.354742
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 4 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 2.595121
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 5 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 1.826818
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 6 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 0.886115
  type: 'test'
  ...
1..6
# tests 6
# suites 0
# pass 6
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 109.695547

codex
The JS twin’s 6 Node tests pass. Python `pytest` itself is not installed in this environment, so I’m going to execute the 9 `test_*` functions directly under a stubbed import; these tests are plain asserts and do not rely on pytest fixtures.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types, importlib\\nlmfit = types.ModuleType(\"lmfit\")\\nlmfit.Model = object\\nlmfit.Parameters = object\\nsys.modules[\"lmfit\"] = lmfit\\nscipy = types.ModuleType(\"scipy\")\\nintegrate = types.ModuleType(\"scipy.integrate\")\\ndef trapezoid(*args, **kwargs):\\n    raise RuntimeError(\"trapezoid stub should not be used by Tougaard tests\")\\nintegrate.trapezoid = trapezoid\\nscipy.integrate = integrate\\nsys.modules[\"scipy\"] = scipy\\nsys.modules[\"scipy.integrate\"] = integrate\\nmod = importlib.import_module(\"tests.test_tougaard_background\")\\nnames = sorted(n for n in dir(mod) if n.startswith(\"test_\"))\\nfor name in names:\\n    getattr(mod, name)()\\n    print(\"PASS\", name)\\nprint(\"TOTAL\", len(names))\\n'" in /Users/skyefortier/xps-verify
 succeeded in 136ms:
PASS test_ascending_and_descending_input_agree_exactly
PASS test_ascending_descending_parity_on_nonuniform_grid
PASS test_background_anchored_at_high_be_edge
PASS test_background_tracks_low_be_baseline_on_wide_region
PASS test_flat_window_yields_no_phantom_signal
PASS test_kernel_peak_near_sqrt_c_over_3
PASS test_no_loss_signal_returns_flat_pre_loss_level
PASS test_nonuniform_grid_uses_local_quadrature_weights
PASS test_short_input_returns_zeros
TOTAL 9

codex
All 9 Python Tougaard test functions pass when executed directly; the only reason `pytest` did not run normally is that this sandbox’s system Python has neither `pytest` nor the project dependencies installed. I’m doing the remaining artifact sweep for saved numeric Tougaard pins and degenerate assertions now.
exec
/bin/zsh -lc "nl -ba tests/test_tougaard_background.py | sed -n '45,285p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    45	        + 5000.0 * np.exp(-0.5 * ((x - 287.0) / 0.8) ** 2)
    46	        + 400.0 / (1.0 + np.exp(-(287.0 - x)))  # step rising toward high BE
    47	    )
    48	    if not descending:
    49	        return x[::-1].copy(), y[::-1].copy()
    50	    return x, y
    51	
    52	
    53	def test_kernel_peak_near_sqrt_c_over_3():
    54	    """The loss-kernel response to a delta-like peak must peak ~23.4 eV
    55	    above the peak (sqrt(C/3) with C = 1643 eV²), not ~949 eV.
    56	
    57	    A spike at x0 on a descending grid produces bg(x) ∝ K(x − x0) on the
    58	    high-BE side, so the argmax of the background directly locates the
    59	    kernel maximum.
    60	    """
    61	    x = np.linspace(100.0, 0.0, 1001)  # descending, dx = 0.1 eV
    62	    # A pedestal PLUS a high-BE step. The step matters: since the F1 offset
    63	    # fix (2026-07-17) the fitted amplitude is proportional to the measured
    64	    # rise across the window (data at the high-BE edge minus the low-BE
    65	    # pre-loss level). A perfectly flat pedestal therefore has NO loss
    66	    # intensity to model, so the honest background is flat and carries no
    67	    # kernel shape to inspect. The step gives the anchor something to fit;
    68	    # the background shape it scales is still the pure kernel response.
    69	    y = np.full_like(x, 1e-9)
    70	    y[0] = 2e-9  # high-BE edge: a measured rise -> nonzero fitted amplitude
    71	    spike_idx = 800  # x = 20.0 eV
    72	    y[spike_idx] = 1.0e6
    73	
    74	    bg = tougaard_background(x, y)
    75	
    76	    high_be_side = slice(0, spike_idx)  # x > 20 eV: traces K(x − 20)
    77	    peak_x = x[high_be_side][np.argmax(bg[high_be_side])]
    78	    expected = 20.0 + np.sqrt(1643.0 / 3.0)  # 20 + 23.402...
    79	    assert abs(peak_x - expected) <= 0.25, (
    80	        f"kernel response peaks at x = {peak_x:.2f} eV; expected "
    81	        f"{expected:.2f} eV (spike at 20.0 + sqrt(C/3) ≈ 23.4 eV). "
    82	        f"A peak near x = 100 means the squared constant (C = 1643²) is back."
    83	    )
    84	
    85	
    86	def test_ascending_and_descending_input_agree_exactly():
    87	    """The same spectrum fed in ascending vs descending BE order must give
    88	    the identical background (element-wise, after re-reversal)."""
    89	    x_d, y_d = _synthetic_spectrum(descending=True)
    90	    x_a, y_a = _synthetic_spectrum(descending=False)
    91	
    92	    bg_d = tougaard_background(x_d, y_d)
    93	    bg_a = tougaard_background(x_a, y_a)
    94	
    95	    assert np.array_equal(bg_d, bg_a[::-1]), (
    96	        f"order-dependent output: max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
    97	    )
    98	
    99	
   100	def test_ascending_descending_parity_on_nonuniform_grid():
   101	    """Order-robustness must also hold on the non-uniform-grid code path
   102	    (which uses the exact per-point separation loop, not the convolution)."""
   103	    # Deterministic, mildly non-uniform descending grid
   104	    steps = 0.08 + 0.04 * np.sin(np.arange(120))
   105	    x_d = 295.0 - np.concatenate(([0.0], np.cumsum(steps)))
   106	    y_d = 100.0 + 4000.0 * np.exp(-0.5 * ((x_d - 290.0) / 1.0) ** 2)
   107	
   108	    bg_d = tougaard_background(x_d, y_d)
   109	    bg_a = tougaard_background(x_d[::-1].copy(), y_d[::-1].copy())
   110	
   111	    assert np.array_equal(bg_d, bg_a[::-1]), (
   112	        f"non-uniform grid is order-dependent: "
   113	        f"max|Δ| = {np.max(np.abs(bg_d - bg_a[::-1]))}"
   114	    )
   115	
   116	
   117	def test_background_anchored_at_high_be_edge():
   118	    """The background must equal the measured intensity at the high-BE edge
   119	    of the window (practical Tougaard criterion: the universal cross-section
   120	    amplitude is scaled so the background meets the data above the peak),
   121	    and must vanish at the low-BE edge (no in-window emitters below it)."""
   122	    x, y = _synthetic_spectrum(descending=True)
   123	    bg = tougaard_background(x, y)
   124	
   125	    # x[0] is the high-BE edge on this descending grid
   126	    assert np.isclose(bg[0], y[0], rtol=1e-12), (
   127	        f"high-BE-edge anchor broken: bg[0] = {bg[0]}, data = {y[0]}"
   128	    )
   129	    # Since the F1 offset fix (2026-07-17) the low-BE edge carries the
   130	    # pre-loss constant C0 (the out-of-window baseline), NOT zero. K(0) = 0
   131	    # still makes the LOSS integral vanish there, so the background equals C0
   132	    # exactly -- i.e. Tougaard now meets the data at BOTH edges, like Shirley.
   133	    # Asserting 0.0 here was pinning the bug: it forced the background to dive
   134	    # to zero at the low-BE edge regardless of the data, reporting the entire
   135	    # baseline as net signal.
   136	    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
   137	        f"low-BE edge should sit on the pre-loss level C0 = {y[-1]}, got {bg[-1]}"
   138	    )
   139	    assert np.all(np.isfinite(bg))
   140	    assert np.all(bg >= 0.0)
   141	
   142	    # Same anchor semantics for ascending input: the high-BE edge is x[-1]
   143	    bg_a = tougaard_background(x[::-1].copy(), y[::-1].copy())
   144	    assert np.isclose(bg_a[-1], y[0], rtol=1e-12)
   145	    # ...and the low-BE edge (index 0 when ascending) sits on C0, per above.
   146	    assert np.isclose(bg_a[0], y[-1], rtol=1e-12)
   147	
   148	
   149	def test_no_loss_signal_returns_flat_pre_loss_level():
   150	    """Degenerate input: no net loss signal accumulates at the high-BE edge
   151	    (bg[0] == 0 — counts are zero everywhere below the edge point).
   152	
   153	    Supersedes the 2026-07-04 Codex pin ``..._returns_unanchored_zeros``.
   154	    That pin asserted all-zeros, which was correct ONLY while the background
   155	    carried no constant term: with the F1 offset fix (2026-07-17) the honest
   156	    answer for a window containing no modellable loss signal is the flat
   157	    pre-loss level C0, not zero. Returning zeros would report the entire
   158	    baseline as net signal — the exact failure F1 fixes. The guard itself
   159	    still exists (no force-matching to the edge intensity, no divide-by-zero);
   160	    only its fallback VALUE changed from 0 to C0. Mirrored in the JS twin."""
   161	    x = np.array([291.0, 290.0, 289.0, 288.0])  # descending
   162	    y = np.array([100.0, 0.0, 0.0, 0.0])        # signal only at the edge itself
   163	    bg = tougaard_background(x, y)
   164	    assert np.array_equal(bg, np.zeros(4)), (
   165	        f"C0 is 0.0 here (low-BE edge counts are zero), so the flat pre-loss "
   166	        f"level IS zeros; got {bg}"
   167	    )
   168	
   169	
   170	def test_flat_window_yields_no_phantom_signal():
   171	    """F1 regression pin (2026-07-17): a flat, featureless window must yield
   172	    ~zero net counts everywhere.
   173	
   174	    Before the offset fix, K(0) = 0 forced the background to zero at the
   175	    low-BE edge regardless of the data, so a flat 500-count window produced a
   176	    background ramping 0 -> 500 and reported up to 500 counts of phantom
   177	    "signal" fabricated from a featureless baseline."""
   178	    x = np.linspace(740.0, 700.0, 200)   # descending, flat data
   179	    y = np.full_like(x, 500.0)
   180	    bg = tougaard_background(x, y)
   181	    net = y - bg
   182	    assert np.max(np.abs(net)) < 1e-6, (
   183	        f"flat window must leave ~zero net; net spans "
   184	        f"{net.min():.3f}..{net.max():.3f}"
   185	    )
   186	
   187	
   188	def test_background_tracks_low_be_baseline_on_wide_region():
   189	    """F1 regression pin (2026-07-17): on a wide 2p-like region sitting on a
   190	    large out-of-window inelastic baseline, the background must track that
   191	    baseline at the low-BE edge instead of diving to zero."""
   192	    x = np.linspace(740.0, 700.0, 600)   # descending
   193	    pk = (6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2)
   194	          + 3000.0 * np.exp(-0.5 * ((x - 724.5) / 1.9) ** 2))
   195	    baseline = 4000.0 + 3000.0 * np.cumsum(pk[::-1])[::-1] / np.sum(pk)
   196	    y = pk + baseline
   197	    bg = tougaard_background(x, y)
   198	    # low-BE edge is index -1 on this descending grid
   199	    assert np.isclose(bg[-1], y[-1], rtol=1e-12), (
   200	        f"low-BE edge dove to {bg[-1]:.1f} instead of tracking the "
   201	        f"{y[-1]:.1f}-count baseline"
   202	    )
   203	    assert np.isclose(bg[0], y[0], rtol=1e-12)
   204	
   205	
   206	def test_nonuniform_grid_uses_local_quadrature_weights():
   207	    """F2 regression pin (2026-07-17): the nonuniform-grid branch must weight
   208	    each term by its local energy spacing.
   209	
   210	    It previously used exact per-point separations but omitted the spacing
   211	    weights, silently applying uniform-grid quadrature inside the branch
   212	    written precisely BECAUSE the grid is not uniform (~24% error on a
   213	    genuinely nonuniform grid). np.gradient returns dx exactly on a uniform
   214	    grid, so the two branches must now agree to floating point -- the
   215	    uniformity test is an optimization, not a semantic fork."""
   216	    # Uniform grid, then the same grid perturbed below the uniformity
   217	    # tolerance so the nonuniform branch runs on near-identical data.
   218	    x = np.linspace(740.0, 700.0, 300)
   219	    y = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))
   220	    bg_uniform = tougaard_background(x, y)
   221	    x_jitter = x.copy()
   222	    x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
   223	    bg_nonuniform = tougaard_background(x_jitter, y)
   224	    assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
   225	        "uniform and nonuniform branches disagree on near-identical grids"
   226	    )
   227	
   228	    # Genuinely nonuniform grid vs an explicit spacing-weighted reference.
   229	    # A high-BE endpoint RISE (not just a symmetric peak on a flat baseline)
   230	    # is required here: the F1 anchor rescales by (ya[0]-c0)/bg[0], so a
   231	    # fixture whose two edges sit at nearly the same level collapses that
   232	    # scale factor toward zero and the F2 weighting difference vanishes
   233	    # into the noise floor *after* anchoring -- passing this assertion even
   234	    # with the w[i:] weighting removed entirely (caught by Codex review,
   235	    # 2026-07-17: the original flat-baseline fixture measured a 4.5e-13 max
   236	    # diff between weighted and unweighted output, i.e. it did not actually
   237	    # guard F2). The endpoint delta below (~800 counts) keeps the anchored
   238	    # scale non-degenerate, so the ~105-count weighted-vs-unweighted
   239	    # divergence survives anchoring and this pin is falsifiable again.
   240	    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
   241	                         np.linspace(720.0, 700.0, 400)])
   242	    ya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(
   243	        -0.5 * ((xa - 710.9) / 1.6) ** 2
   244	    )
   245	    got = tougaard_background(xa, ya)
   246	
   247	    B_coef, C_coef = 2866.0, 1643.0
   248	    c0 = float(ya[-1])
   249	    net = ya - c0
   250	    w = np.abs(np.gradient(xa))
   251	    ref = np.zeros(len(xa))
   252	    ref_unweighted = np.zeros(len(xa))
   253	    for i in range(len(xa)):
   254	        T = np.abs(xa[i:] - xa[i])
   255	        kernel = (B_coef * T) / (C_coef + T * T) ** 2
   256	        ref[i] = float(np.sum(kernel * net[i:] * w[i:]))
   257	        ref_unweighted[i] = float(np.sum(kernel * net[i:]))
   258	    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
   259	    ref_unweighted = c0 + ref_unweighted * ((float(ya[0]) - c0) / ref_unweighted[0])
   260	
   261	    # The pin only means something if weighted and unweighted actually
   262	    # disagree on this fixture -- guard the guard.
   263	    assert np.max(np.abs(ref - ref_unweighted)) > 10.0, (
   264	        "fixture does not separate weighted from unweighted quadrature -- "
   265	        "endpoint delta too small to survive the F1 anchor, pin is dead"
   266	    )
   267	    assert np.allclose(got, ref, rtol=1e-9), (
   268	        "nonuniform branch does not match spacing-weighted quadrature"
   269	    )
   270	
   271	
   272	def test_short_input_returns_zeros():
   273	    """< 2 points: no background can be defined; must return zeros."""
   274	    assert np.array_equal(
   275	        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
   276	    )
   277	    assert tougaard_background(np.array([]), np.array([])).size == 0

exec
/bin/zsh -lc "nl -ba tests/js/tougaard_twin.test.js | sed -n '45,210p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    45	
    46	test('loss-kernel response peaks ~23.4 eV above a delta-like peak', () => {
    47	  const n = 1001;
    48	  const be = [], intensity = [];
    49	  for (let i = 0; i < n; i++) {
    50	    be.push(100.0 - 0.1 * i);      // descending 100 → 0 eV
    51	    intensity.push(1e-9);
    52	  }
    53	  // A high-BE step is required since the F1 offset fix (2026-07-17): the
    54	  // fitted amplitude is proportional to the measured rise across the window
    55	  // (high-BE edge minus the low-BE pre-loss level), so a perfectly flat
    56	  // pedestal has no loss intensity to model and yields a flat background with
    57	  // no kernel shape to inspect. Mirrors the Python twin test.
    58	  intensity[0] = 2e-9;
    59	  const spikeIdx = 800;            // be = 20.0 eV
    60	  intensity[spikeIdx] = 1e6;
    61	
    62	  const bg = tougaardBackground(be, intensity);
    63	
    64	  let maxV = -Infinity, maxX = NaN;
    65	  for (let i = 0; i < spikeIdx; i++) {   // high-BE side: traces K(be − 20)
    66	    if (bg[i] > maxV) { maxV = bg[i]; maxX = be[i]; }
    67	  }
    68	  const expected = 20.0 + Math.sqrt(1643.0 / 3.0);  // ≈ 43.4 eV
    69	  assert.ok(Math.abs(maxX - expected) <= 0.25,
    70	    `kernel response peaks at ${maxX.toFixed(2)} eV, expected ~${expected.toFixed(2)}; ` +
    71	    'a peak near 100 eV means the squared constant (1643*1643) is back');
    72	});
    73	
    74	test('ascending and descending BE input give the identical background', () => {
    75	  const { be, intensity } = syntheticSpectrum();
    76	  const bgDesc = tougaardBackground(be, intensity);
    77	  const bgAsc = tougaardBackground([...be].reverse(), [...intensity].reverse());
    78	  bgAsc.reverse();
    79	  for (let i = 0; i < be.length; i++) {
    80	    assert.strictEqual(bgDesc[i], bgAsc[i],
    81	      `order-dependent output at index ${i}: ${bgDesc[i]} vs ${bgAsc[i]}`);
    82	  }
    83	});
    84	
    85	test('background meets the data at BOTH edges (high-BE anchor, low-BE C0)', () => {
    86	  const { be, intensity } = syntheticSpectrum();
    87	  const bg = tougaardBackground(be, intensity);
    88	  const rel = Math.abs(bg[0] - intensity[0]) / intensity[0];
    89	  assert.ok(rel < 1e-12,
    90	    `high-BE-edge anchor broken: bg[0] = ${bg[0]}, data = ${intensity[0]}`);
    91	  // Since the F1 offset fix (2026-07-17) the low-BE edge carries the pre-loss
    92	  // constant C0, NOT zero. K(0)=0 still kills the LOSS integral there, so the
    93	  // background equals C0 exactly. Asserting 0 pinned the bug: it forced the
    94	  // background to dive to zero regardless of the data.
    95	  const last = bg.length - 1;
    96	  const relLow = Math.abs(bg[last] - intensity[last]) / intensity[last];
    97	  assert.ok(relLow < 1e-12,
    98	    `low-BE edge should sit on C0 = ${intensity[last]}, got ${bg[last]}`);
    99	});
   100	
   101	test('flat window yields no phantom signal (F1 regression pin)', () => {
   102	  const be = [], intensity = [];
   103	  for (let i = 0; i < 200; i++) { be.push(740.0 - 40.0 * i / 199); intensity.push(500.0); }
   104	  const bg = tougaardBackground(be, intensity);
   105	  for (let i = 0; i < bg.length; i++) {
   106	    assert.ok(Math.abs(intensity[i] - bg[i]) < 1e-6,
   107	      `flat window must leave ~zero net; net ${intensity[i] - bg[i]} at ${i}`);
   108	  }
   109	});
   110	
   111	test('agrees with the backend implementation (fitting.py) on the same spectrum', () => {
   112	  // Expected values regenerated against the backend on 2026-07-17 after the
   113	  // F1 (pre-loss constant C0) + F2 (local quadrature weights) fixes:
   114	  //   venv/bin/python - <<'EOF'
   115	  //   import numpy as np; from fitting import tougaard_background
   116	  //   x = np.linspace(295.0, 280.0, 151)
   117	  //   y = (100.0 + 5000.0*np.exp(-0.5*((x-287.0)/0.8)**2)
   118	  //        + 400.0/(1.0+np.exp(-(287.0-x))))
   119	  //   bg = tougaard_background(x, y)
   120	  //   print([float(bg[i]) for i in (0, 30, 75, 110, 149, 150)])
   121	  //   EOF
   122	  // Regenerate with that snippet if the backend numerics change for a
   123	  // reviewed reason. Tolerance 1e-9 relative: np.convolve vs the JS loop
   124	  // differ only by floating-point summation order.
   125	  const expected = {
   126	    0: 100.13414005218658,
   127	    30: 219.3991381848062,
   128	    75: 461.76541491579644,
   129	    110: 499.7312788702072,
   130	    149: 499.6355795222399,
   131	    150: 499.6355795222399,
   132	  };
   133	  const { be, intensity } = syntheticSpectrum();
   134	  const bg = tougaardBackground(be, intensity);
   135	  for (const [idx, want] of Object.entries(expected)) {
   136	    const got = bg[Number(idx)];
   137	    const tol = want === 0 ? 1e-15 : Math.abs(want) * 1e-9;
   138	    assert.ok(Math.abs(got - want) <= tol,
   139	      `backend/frontend disagree at index ${idx}: js ${got} vs python ${want}`);
   140	  }
   141	});
   142	
   143	// --- Codex review finding (2026-07-04, both runs, MAJOR): the shipped
   144	// caller computeBackgroundCore passed RAW intensity to tougaardBackground
   145	// while every backend caller applies endpoint averaging first. With the
   146	// high-BE-edge anchor, averaging directly sets the anchor amplitude, so
   147	// the caller contract — not just the function — must match the backend
   148	// (fitting.py run_fit / compute_background_only both do
   149	// tougaard_background(x, _apply_endpoint_averaging(y, n))).
   150	test('computeBackgroundCore applies endpoint averaging for tougaard (both branches)', () => {
   151	  const coreMatch = html.match(/function computeBackgroundCore\([\s\S]*?\n\}/);
   152	  assert.ok(coreMatch, 'computeBackgroundCore not found in templates/index.html');
   153	  // Stubs for background types this test never routes to; the eval'd
   154	  // function closes over this scope, so these names resolve at call time.
   155	  const manualAnchorBackground = () => { throw new Error('unexpected route: manual'); };
   156	  const shirleyBackground = () => { throw new Error('unexpected route: shirley'); };
   157	  const smartBackground = () => { throw new Error('unexpected route: smart'); };
   158	  const smartExperimentalBackground = () => { throw new Error('unexpected route: smart_exp'); };
   159	  const shirleyLinearBackground = () => { throw new Error('unexpected route: shirley_linear'); };
   160	  const linearBackground = () => { throw new Error('unexpected route: linear'); };
   161	  const computeBackgroundCore = eval('(' + coreMatch[0] + ')');
   162	
   163	  // Descending grid with an outlier at the high-BE edge: raw vs 3-point
   164	  // averaged anchors differ by construction (Codex's concrete scenario).
   165	  const n = 21;
   166	  const be = [], intensity = [];
   167	  for (let i = 0; i < n; i++) { be.push(292.0 - 0.5 * i); intensity.push(100); }
   168	  intensity[0] = 10000;   // high-BE outlier
   169	  intensity[10] = 4000;   // a peak so the correlation is non-trivial
   170	
   171	  const nAvg = 3;
   172	  const expected = tougaardBackground(be, _applyEndpointAveraging(intensity, nAvg));
   173	
   174	  // Branch 1: bg window covers the data (main sliced path)
   175	  const mainOut = computeBackgroundCore(be, intensity, {
   176	    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
   177	    bgStart: '292', bgEnd: '282',
   178	  });
   179	  // Branch 2: bg window misses the data entirely (fallback full-range path)
   180	  const fallbackOut = computeBackgroundCore(be, intensity, {
   181	    bgType: 'tougaard', shirleyIter: '5', endpointAvg: String(nAvg),
   182	    bgStart: '900', bgEnd: '905',
   183	  });
   184	
   185	  for (const [label, out] of [['main', mainOut], ['fallback', fallbackOut]]) {
   186	    for (let i = 0; i < n; i++) {
   187	      assert.strictEqual(out[i], expected[i],
   188	        `${label} branch: caller bypasses endpoint averaging at index ${i}: ` +
   189	        `${out[i]} vs averaged ${expected[i]}`);
   190	    }
   191	  }
   192	});

exec
/bin/zsh -lc "rg -n -i 'tougaard|bgIntensity|background|background_method|bgType|fitResult|fittedY' docs/autofit/inventory tests/fixtures tests/autofit/fixtures uploads --glob '*.json' --glob '*.jsonl' --glob '*.fit.json' --glob '*.proj.json' --glob '*.spec.json' 2>/dev/null" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
tests/autofit/fixtures/b1s_battery_expected.json:111:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:116:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:121:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:126:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:131:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:136:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:141:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:146:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:151:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:156:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/b1s_battery_expected.json:161:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1424:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1429:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1434:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1439:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1444:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1449:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1454:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1459:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1464:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1469:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1474:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1479:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1484:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1489:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/c1s_battery_expected.json:1494:   "reason": "internally inconsistent fitResult (fittedY 143 pts vs be 142 pts \u2014 stale fittedY from an earlier ROI)"
tests/autofit/fixtures/u4f_battery_expected.json:1137:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1142:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1147:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1152:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1157:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1162:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1167:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1172:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1177:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1182:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1187:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1192:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1197:   "reason": "legacy fitResult (no be/fittedY)"
tests/autofit/fixtures/u4f_battery_expected.json:1202:   "reason": "legacy fitResult (no be/fittedY)"
docs/autofit/inventory/stress_battery_runs.jsonl:1:{"case": "overlap_sep1_h9000", "chi_reduced": 2.1830979047606682, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 1.0\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0022, "d_fwhm_ev": 0.0144, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.0084, "d_fwhm_ev": 0.0093, "matched_role": "2", "true_center": 198.39999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:6:{"case": "overlap_sep0.7_h9000", "chi_reduced": 1.5809299088896689, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0184, "d_fwhm_ev": 0.0082, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.04, "d_fwhm_ev": 0.0615, "matched_role": "2", "true_center": 198.04}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:11:{"case": "overlap_sep0.4_h9000", "chi_reduced": 1.1991827295683668, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.04, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1939, "d_fwhm_ev": 0.1375, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.1966, "d_fwhm_ev": 2.5887, "matched_role": "2", "true_center": 197.67999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:16:{"case": "overlap_sep0.4_h900", "chi_reduced": 1.3658889942098313, "config": {"background_method": "linear"}, "expectation": "ambiguous", "method": "least_squares", "notes": "separation 0.4\u00d7FWHM, heights 900/630", "regime": "heavy_overlap", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1657, "d_fwhm_ev": 0.1563, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.2259, "d_fwhm_ev": 0.1642, "matched_role": "2", "true_center": 197.67999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:21:{"case": "weak_minor_0.03_h90000", "chi_reduced": 14.06952772490919, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.004, "d_fwhm_ev": 0.0114, "matched_role": "1", "true_center": 197.0}, {"d_center_ev": -0.0523, "d_fwhm_ev": 0.154, "matched_role": "2", "true_center": 198.8}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:26:{"case": "weak_minor_0.03_h2000", "chi_reduced": 2.3608518137434937, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 0.09, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0068, "d_fwhm_ev": 0.0266, "matched_role": "1", "true_center": 197.0}, {"d_center_ev": -0.1594, "d_fwhm_ev": -0.2592, "matched_role": "2", "true_center": 198.8}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:31:{"case": "overspecified_2true_5max", "chi_reduced": 2.6229747025005983, "config": {"background_method": "linear"}, "expectation": "prune", "method": "least_squares", "notes": "truth 2 well-separated peaks; menu offers up to 5", "regime": "overspecified", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0021, "d_fwhm_ev": 0.0273, "matched_role": "1", "true_center": 196.8}, {"d_center_ev": 0.0006, "d_fwhm_ev": 0.0343, "matched_role": "2", "true_center": 199.4}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:36:{"case": "overspecified_inroi_decoy", "chi_reduced": 1.0973184146182224, "config": {"background_method": "linear"}, "expectation": "prune", "method": "least_squares", "notes": "decoy 'shoulder' window between the true peaks (real tail intensity present) \u2014 must be pruned, not populated", "regime": "overspecified", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0008, "d_fwhm_ev": 0.0013, "matched_role": "1", "true_center": 196.8}, {"d_center_ev": -0.0, "d_fwhm_ev": 0.0108, "matched_role": "2", "true_center": 199.4}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:41:{"case": "charging_no_replica_candidate", "chi_reduced": 2.11933018079081, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0397, "d_fwhm_ev": 0.0591, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": -0.1661, "d_fwhm_ev": -0.1165, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:46:{"case": "charging_with_replica_candidate", "chi_reduced": 1.747290088264468, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0655, "d_fwhm_ev": -0.1281, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.4835, "d_fwhm_ev": 0.3695, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:51:{"case": "asym_truth_symmetric_only", "chi_reduced": 7.6455977637255454, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.02, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0099, "d_fwhm_ev": -0.0994, "matched_role": "1", "true_center": 197.8}], "truth_n": 1}
docs/autofit/inventory/stress_battery_runs.jsonl:56:{"case": "asym_truth_with_asym_candidate", "chi_reduced": 4.6396254134392585, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["asym_main"], "truth_match": [{"d_center_ev": -0.0032, "d_fwhm_ev": -0.0752, "matched_role": "1", "true_center": 197.8}], "truth_n": 1}
docs/autofit/inventory/stress_battery_runs.jsonl:61:{"case": "bg_shirley_truth_linear_fit", "chi_reduced": 1.3111668357842798, "config": {"background_method": "shirley"}, "expectation": "honesty", "method": "least_squares", "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0019, "d_fwhm_ev": 0.0058, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.0015, "d_fwhm_ev": 0.0102, "matched_role": "2", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:62:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4271.54858425193, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 468.6838552678528, "survived": false}, {"bic_star": 3801.4114042480733, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 308.7466180222082, "survived": true}, {"bic_star": 3648.466236534472, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 284.1218885924425, "survived": false}, {"bic_star": 3642.7622641369885, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 283.1387414386821, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 10.22, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0151, "d_fwhm_ev": -0.1716, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0174, "d_fwhm_ev": 0.2873, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 283.1387414386821, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:63:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4271.544614789273, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 468.68383163083354, "survived": false}, {"bic_star": 3801.406217540362, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 308.74661569462177, "survived": true}, {"bic_star": 3648.489127912308, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 284.1217320570383, "survived": false}, {"bic_star": 3642.785345422898, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 283.1386118748553, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 32.82, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0151, "d_fwhm_ev": -0.1716, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0172, "d_fwhm_ev": 0.2878, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 283.1386118748553, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:64:{"case": "bg_shirley_truth_linear_fit", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 16.71, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.8003, "d_fwhm_ev": 0.1674, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.95, "d_fwhm_ev": 1.3, "matched_role": "main_c", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:65:{"candidates": [{"free_energy": 1793.061086826171, "free_energy_mc_error": 0.9863760548835216, "free_energy_split_half_error": 0.9863760548835216, "min_effective_sample_size": 12.052467769853447, "name": "P1", "posterior_weight": 5.343170927789774e-25, "posterior_weight_reliable": false, "rank": 3}, {"free_energy": 1739.1943336883178, "free_energy_mc_error": 0.07941240036427644, "free_energy_split_half_error": 0.07941240036427644, "min_effective_sample_size": 11.81030231507597, "name": "P2", "posterior_weight": 0.13238315077870916, "posterior_weight_reliable": false, "rank": 2}, {"free_energy": 1737.314283864484, "free_energy_mc_error": 1.0489200045319649, "free_energy_split_half_error": 1.0489200045319649, "min_effective_sample_size": 6.0221753030026335, "name": "P3", "posterior_weight": 0.8676168492212908, "posterior_weight_reliable": false, "rank": 1}], "case": "bg_shirley_truth_linear_fit", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "honesty", "method": "bayesian_exchange_mc", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 10.46, "seed_offset": 0, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=1.9 is within 2\u00d7(MC errors 1.0+0.1; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0354, "d_fwhm_ev": -0.2686, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0884, "d_fwhm_ev": 0.6086, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3", "winner_is_true": false}
docs/autofit/inventory/stress_battery_runs.jsonl:66:{"case": "bg_shirley_truth_shirley_fit", "chi_reduced": 1.235588792953297, "config": {"background_method": "shirley"}, "expectation": "recover", "method": "least_squares", "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "2", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:67:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4146.61792120331, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 126.30873391628948, "survived": false}, {"bic_star": 2433.522542110988, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.2355887929329685, "survived": true}, {"bic_star": 2464.9017984747015, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.2209246366731366, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 1.17, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.2355887929329685, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:68:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4146.6177847728, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 126.30873391534688, "survived": false}, {"bic_star": 2433.5225504652817, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.2355887929327787, "survived": true}, {"bic_star": 2464.9017984747015, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.9166666666666666, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 1.2209246366731366, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 2.72, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0114, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0018, "d_fwhm_ev": 0.0065, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.2355887929327787, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:69:{"case": "bg_shirley_truth_shirley_fit", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 4, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 17.24, "seed_offset": 0, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.6582, "d_fwhm_ev": 0.0854, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.2376, "d_fwhm_ev": -0.4754, "matched_role": "main_c", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:70:{"candidates": [{"free_energy": 1599.110485813647, "free_energy_mc_error": 0.24260545262518463, "free_energy_split_half_error": 0.24260545262518463, "min_effective_sample_size": 7.137468682396516, "name": "P1", "posterior_weight": 2.7152041369339324e-286, "posterior_weight_reliable": false, "rank": 3}, {"free_energy": 941.5700903272918, "free_energy_mc_error": 2.1642208314430604, "free_energy_split_half_error": 2.1642208314430604, "min_effective_sample_size": 4.108234318776078, "name": "P2", "posterior_weight": 0.9999260319109442, "posterior_weight_reliable": false, "rank": 1}, {"free_energy": 951.0818931432085, "free_energy_mc_error": 7.596151277192121, "free_energy_split_half_error": 7.596151277192121, "min_effective_sample_size": 3.205537296135919, "name": "P3", "posterior_weight": 7.396808905581752e-05, "posterior_weight_reliable": false, "rank": 2}], "case": "bg_shirley_truth_shirley_fit", "config": {"n_replicas": 8, "n_sweeps": 600, "rng_seed": 0, "weights": "poisson_like"}, "expectation": "recover", "method": "bayesian_exchange_mc", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 11.19, "seed_offset": 0, "selection_warning": "UNRESOLVED model selection: top-2 \u0394F=9.5 is within 2\u00d7(MC errors 2.2+7.6; split-half (lower bound)) \u2014 increase n_sweeps/n_replicas or seed_replicates before trusting the winner", "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0032, "d_fwhm_ev": 0.0089, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 0.0003, "d_fwhm_ev": 0.0058, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_is_true": true}
docs/autofit/inventory/stress_battery_runs.jsonl:71:{"case": "overlap_sep1_h9000", "chi_reduced": 1.3479145468099627, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 1.0\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0003, "d_fwhm_ev": 0.0133, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.0066, "d_fwhm_ev": 0.0075, "matched_role": "2", "true_center": 198.39999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:75:{"case": "overlap_sep0.7_h9000", "chi_reduced": 1.2002472160352367, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0116, "d_fwhm_ev": -0.0012, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.0124, "d_fwhm_ev": 0.0279, "matched_role": "2", "true_center": 198.04}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:79:{"case": "overlap_sep0.4_h9000", "chi_reduced": 2.224779118759168, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.04, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1762, "d_fwhm_ev": 0.1318, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.471, "d_fwhm_ev": -0.03, "matched_role": "2", "true_center": 197.67999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:83:{"case": "overlap_sep0.4_h900", "chi_reduced": 1.096548700392471, "config": {"background_method": "linear"}, "expectation": "ambiguous", "method": "least_squares", "notes": "separation 0.4\u00d7FWHM, heights 900/630", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0132, "d_fwhm_ev": -0.0239, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.0207, "d_fwhm_ev": -0.008, "matched_role": "2", "true_center": 197.67999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:87:{"case": "weak_minor_0.03_h90000", "chi_reduced": 14.105716924378289, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 0.03, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0044, "d_fwhm_ev": 0.0122, "matched_role": "1", "true_center": 197.0}, {"d_center_ev": -0.0441, "d_fwhm_ev": 0.1289, "matched_role": "2", "true_center": 198.8}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:91:{"case": "weak_minor_0.03_h2000", "chi_reduced": 0.9864372885499808, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 0.02, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0005, "d_fwhm_ev": -0.007, "matched_role": "1", "true_center": 197.0}, {"d_center_ev": 0.0342, "d_fwhm_ev": 0.2912, "matched_role": "2", "true_center": 198.8}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:95:{"case": "overspecified_2true_5max", "chi_reduced": 1.7784581294460509, "config": {"background_method": "linear"}, "expectation": "prune", "method": "least_squares", "notes": "truth 2 well-separated peaks; menu offers up to 5", "regime": "overspecified", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0001, "d_fwhm_ev": 0.0147, "matched_role": "1", "true_center": 196.8}, {"d_center_ev": -0.0055, "d_fwhm_ev": 0.0299, "matched_role": "2", "true_center": 199.4}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:99:{"case": "overspecified_inroi_decoy", "chi_reduced": 2.225654105055817, "config": {"background_method": "linear"}, "expectation": "prune", "method": "least_squares", "notes": "decoy 'shoulder' window between the true peaks (real tail intensity present) \u2014 must be pruned, not populated", "regime": "overspecified", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0014, "d_fwhm_ev": 0.0238, "matched_role": "1", "true_center": 196.8}, {"d_center_ev": -0.005, "d_fwhm_ev": 0.0192, "matched_role": "2", "true_center": 199.4}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:103:{"case": "charging_no_replica_candidate", "chi_reduced": 3.2617136636412978, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.06, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0196, "d_fwhm_ev": -0.1273, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.5088, "d_fwhm_ev": 0.4886, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:107:{"case": "charging_with_replica_candidate", "chi_reduced": 1.8653919775457, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": -0.0239, "d_fwhm_ev": 0.0419, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": -0.0889, "d_fwhm_ev": -0.0014, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:111:{"case": "asym_truth_symmetric_only", "chi_reduced": 5.468264131068512, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0028, "d_fwhm_ev": -0.088, "matched_role": "1", "true_center": 197.8}], "truth_n": 1}
docs/autofit/inventory/stress_battery_runs.jsonl:115:{"case": "asym_truth_with_asym_candidate", "chi_reduced": 3.9705755151842212, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["asym_main"], "truth_match": [{"d_center_ev": -0.0118, "d_fwhm_ev": -0.0887, "matched_role": "1", "true_center": 197.8}], "truth_n": 1}
docs/autofit/inventory/stress_battery_runs.jsonl:119:{"case": "bg_shirley_truth_linear_fit", "chi_reduced": 1.4373087492015777, "config": {"background_method": "shirley"}, "expectation": "honesty", "method": "least_squares", "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0044, "d_fwhm_ev": 0.0073, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.0033, "d_fwhm_ev": 0.0082, "matched_role": "2", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:120:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4276.13751211553, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 485.82886930696975, "survived": false}, {"bic_star": 3798.867786537885, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 323.0957615487757, "survived": true}, {"bic_star": 3657.6171964795, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 300.2440732654479, "survived": false}, {"bic_star": 3651.9134139931, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 299.2051664358594, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 9.05, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.015, "d_fwhm_ev": -0.1739, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0129, "d_fwhm_ev": 0.2661, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 299.2051664358594, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:121:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4276.137336465737, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 485.8288419015945, "survived": false}, {"bic_star": 3798.867786537885, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 323.0957615487757, "survived": true}, {"bic_star": 3657.5852867891253, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 300.24406294190317, "survived": false}, {"bic_star": 3651.8815042352185, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 299.20515613836733, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 31.2, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0151, "d_fwhm_ev": -0.1737, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0127, "d_fwhm_ev": 0.2658, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 299.20515613836733, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:122:{"case": "bg_shirley_truth_linear_fit", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 16.13, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.8014, "d_fwhm_ev": 0.1565, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.9, "d_fwhm_ev": 1.3, "matched_role": "main_c", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:123:{"case": "bg_shirley_truth_shirley_fit", "chi_reduced": 1.6061790867360954, "config": {"background_method": "shirley"}, "expectation": "recover", "method": "least_squares", "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0031, "d_fwhm_ev": 0.0033, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.0, "d_fwhm_ev": 0.01, "matched_role": "2", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:124:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4149.40180690114, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 127.16094575159921, "survived": false}, {"bic_star": 2513.9500119745444, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.606179086709936, "survived": true}, {"bic_star": 2547.2588045334355, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.75, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.5585186839073915, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 1.38, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0031, "d_fwhm_ev": 0.0033, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0, "d_fwhm_ev": 0.01, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.606179086709936, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:125:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4149.401849051055, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 127.1609457367891, "survived": false}, {"bic_star": 2513.9499633731625, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 1.606179086709871, "survived": true}, {"bic_star": 2547.2588045334355, "boundary_hits": ["main_c:center@min"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min'], unphysical_widths=[], orphan_peaks=True)", "min_active_persistence": 0.6666666666666666, "name": "P3", "orphan_peaks": true, "reduced_chi_sq": 1.5585186839073915, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 2.41, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0031, "d_fwhm_ev": 0.0033, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0, "d_fwhm_ev": 0.01, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 1.606179086709871, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:126:{"case": "bg_shirley_truth_shirley_fit", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 15.73, "seed_offset": 1000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.6385, "d_fwhm_ev": 0.1072, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.35, "d_fwhm_ev": 1.3, "matched_role": "main_c", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:127:{"case": "overlap_sep1_h9000", "chi_reduced": 1.858992418320096, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 1.0\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0005, "d_fwhm_ev": 0.0151, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.0068, "d_fwhm_ev": 0.0052, "matched_role": "2", "true_center": 198.39999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:131:{"case": "overlap_sep0.7_h9000", "chi_reduced": 1.0584987881714802, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 0.7\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0012, "d_fwhm_ev": 0.0219, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.0064, "d_fwhm_ev": 0.0153, "matched_role": "2", "true_center": 198.04}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:135:{"case": "overlap_sep0.4_h9000", "chi_reduced": 1.1502058149153107, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "separation 0.4\u00d7FWHM, heights 9000/6300", "regime": "heavy_overlap", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0096, "d_fwhm_ev": 0.0229, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.0216, "d_fwhm_ev": 0.0267, "matched_role": "2", "true_center": 197.67999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:139:{"case": "overlap_sep0.4_h900", "chi_reduced": 1.4113981449770343, "config": {"background_method": "linear"}, "expectation": "ambiguous", "method": "least_squares", "notes": "separation 0.4\u00d7FWHM, heights 900/630", "regime": "heavy_overlap", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.1407, "d_fwhm_ev": 0.0856, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.3656, "d_fwhm_ev": -0.164, "matched_role": "2", "true_center": 197.67999999999998}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:143:{"case": "weak_minor_0.03_h90000", "chi_reduced": 12.68769982841999, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0028, "d_fwhm_ev": 0.0123, "matched_role": "1", "true_center": 197.0}, {"d_center_ev": -0.0369, "d_fwhm_ev": 0.1278, "matched_role": "2", "true_center": 198.8}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:147:{"case": "weak_minor_0.03_h2000", "chi_reduced": 1.1020599847729151, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "minor = 3% of main at +1.8 eV", "regime": "weak_minor", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0013, "d_fwhm_ev": 0.0097, "matched_role": "1", "true_center": 197.0}, {"d_center_ev": 0.0498, "d_fwhm_ev": -0.314, "matched_role": "2", "true_center": 198.8}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:151:{"case": "overspecified_2true_5max", "chi_reduced": 1.1873533059908317, "config": {"background_method": "linear"}, "expectation": "prune", "method": "least_squares", "notes": "truth 2 well-separated peaks; menu offers up to 5", "regime": "overspecified", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0, "d_fwhm_ev": 0.0103, "matched_role": "1", "true_center": 196.8}, {"d_center_ev": -0.0017, "d_fwhm_ev": 0.0075, "matched_role": "2", "true_center": 199.4}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:155:{"case": "overspecified_inroi_decoy", "chi_reduced": 1.7469968538502703, "config": {"background_method": "linear"}, "expectation": "prune", "method": "least_squares", "notes": "decoy 'shoulder' window between the true peaks (real tail intensity present) \u2014 must be pruned, not populated", "regime": "overspecified", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0027, "d_fwhm_ev": 0.0117, "matched_role": "1", "true_center": 196.8}, {"d_center_ev": -0.0037, "d_fwhm_ev": 0.0355, "matched_role": "2", "true_center": 199.4}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:159:{"case": "charging_no_replica_candidate", "chi_reduced": 1.7521780523190802, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0528, "d_fwhm_ev": -0.0962, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.4595, "d_fwhm_ev": 0.4025, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:163:{"case": "charging_with_replica_candidate", "chi_reduced": 1.0564952083796528, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "25% replica at \u22120.8 eV (differential charging shape)", "regime": "charging_tail", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": ["main_plus_replica"], "truth_match": [{"d_center_ev": 0.0319, "d_fwhm_ev": -0.0126, "matched_role": "1", "true_center": 197.8}, {"d_center_ev": 0.1501, "d_fwhm_ev": 0.1416, "matched_role": "2", "true_center": 197.0}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:167:{"case": "asym_truth_symmetric_only", "chi_reduced": 3.6429466885034265, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.02, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": -0.0093, "d_fwhm_ev": -0.0885, "matched_role": "1", "true_center": 197.8}], "truth_n": 1}
docs/autofit/inventory/stress_battery_runs.jsonl:171:{"case": "asym_truth_with_asym_candidate", "chi_reduced": 3.4942120036930677, "config": {"background_method": "linear"}, "expectation": "recover", "method": "least_squares", "notes": "DS truth \u03b1=0.18; high-BE tail", "regime": "asym_truth", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["asym_main"], "truth_match": [{"d_center_ev": -0.0025, "d_fwhm_ev": -0.0687, "matched_role": "1", "true_center": 197.8}], "truth_n": 1}
docs/autofit/inventory/stress_battery_runs.jsonl:175:{"case": "bg_shirley_truth_linear_fit", "chi_reduced": 1.0842650943028351, "config": {"background_method": "shirley"}, "expectation": "honesty", "method": "least_squares", "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0022, "d_fwhm_ev": -0.0004, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": 0.004, "d_fwhm_ev": -0.0044, "matched_role": "2", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:176:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4273.144118402068, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 461.7861240956535, "survived": false}, {"bic_star": 3784.0798938671683, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 299.7146067606419, "survived": true}, {"bic_star": 3632.9182123482246, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 276.66086742128124, "survived": false}, {"bic_star": 3627.2144296590523, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 275.70356335310606, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 4}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 12.24, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.022, "d_fwhm_ev": -0.1669, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0125, "d_fwhm_ev": 0.2415, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 275.70356335310606, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:177:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4273.143449195936, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 461.7860898312274, "survived": false}, {"bic_star": 3784.2145125764064, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 0.9166666666666666, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 299.71460190198326, "survived": true}, {"bic_star": 3632.976929866167, "boundary_hits": ["main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 276.6607492411966, "survived": false}, {"bic_star": 3627.273146187196, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 0.9166666666666666, "name": "P3+bfix", "orphan_peaks": false, "reduced_chi_sq": 275.7034454497869, "survived": true}], "case": "bg_shirley_truth_linear_fit", "conditional": true, "conditional_reason": "decisive_override", "config": {"n_refits": 12}, "expectation": "honesty", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 3, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 31.77, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.0218, "d_fwhm_ev": -0.1671, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0126, "d_fwhm_ev": 0.2423, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P3+bfix", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 275.7034454497869, "winner_is_true": false, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:178:{"case": "bg_shirley_truth_linear_fit", "config": {}, "expectation": "honesty", "flags": {}, "method": "sparse_map", "n_correct": true, "n_selected": 2, "notes": "integral background fit with a straight line \u2014 the mismatch must surface, not silently vanish", "regime": "bg_mismatch", "runtime_s": 15.78, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.7989, "d_fwhm_ev": 0.1534, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.85, "d_fwhm_ev": 1.3, "matched_role": "main_c", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:179:{"case": "bg_shirley_truth_shirley_fit", "chi_reduced": 2.588457868217619, "config": {"background_method": "shirley"}, "expectation": "recover", "method": "least_squares", "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0019, "d_fwhm_ev": 0.0101, "matched_role": "1", "true_center": 197.2}, {"d_center_ev": -0.0009, "d_fwhm_ev": 0.0126, "matched_role": "2", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:180:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4149.084639220466, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 127.55249026837087, "survived": false}, {"bic_star": 2624.164212560478, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 2.5884578681517856, "survived": true}, {"bic_star": 2639.635951866542, "boundary_hits": ["main_c:center@min", "main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min', 'main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 2.340160096106336, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 4}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 1.39, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0019, "d_fwhm_ev": 0.0101, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0009, "d_fwhm_ev": 0.0126, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.5884578681517856, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:181:{"accepted_proposals": [], "ambiguous_pairs": [], "candidates": [{"bic_star": 4149.084639220466, "boundary_hits": ["main_a:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_a:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 1.0, "name": "P1", "orphan_peaks": false, "reduced_chi_sq": 127.55249026837087, "survived": false}, {"bic_star": 2624.163913081583, "boundary_hits": [], "filter_reason": null, "min_active_persistence": 1.0, "name": "P2", "orphan_peaks": false, "reduced_chi_sq": 2.5884578681434554, "survived": true}, {"bic_star": 2639.635951866542, "boundary_hits": ["main_c:center@min", "main_c:fwhm@max"], "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_c:center@min', 'main_c:fwhm@max'], unphysical_widths=[], orphan_peaks=False)", "min_active_persistence": 0.9166666666666666, "name": "P3", "orphan_peaks": false, "reduced_chi_sq": 2.340160096106336, "survived": false}], "case": "bg_shirley_truth_shirley_fit", "conditional": false, "conditional_reason": null, "config": {"n_refits": 12}, "expectation": "recover", "filtered_dominant_alternative": null, "method": "ic_model_comparison", "n_emitted_components": 2, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 3.24, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": -0.0019, "d_fwhm_ev": 0.0101, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": -0.0009, "d_fwhm_ev": 0.0126, "matched_role": "main_b", "true_center": 198.9}], "truth_n": 2, "winner": "P2", "winner_absent_slots": [], "winner_autocorr_flag": true, "winner_boundary_hits": [], "winner_chi_reduced": 2.5884578681434554, "winner_is_true": true, "winner_residual_flags": []}
docs/autofit/inventory/stress_battery_runs.jsonl:182:{"case": "bg_shirley_truth_shirley_fit", "config": {}, "expectation": "recover", "flags": {}, "method": "sparse_map", "n_correct": false, "n_selected": 3, "notes": "control: matched background family", "regime": "bg_mismatch", "runtime_s": 16.15, "seed_offset": 2000, "success": true, "true_candidates": ["P2"], "truth_match": [{"d_center_ev": 0.6385, "d_fwhm_ev": 0.1123, "matched_role": "main_a", "true_center": 197.2}, {"d_center_ev": 2.5737, "d_fwhm_ev": 0.3664, "matched_role": "main_c", "true_center": 198.9}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:183:{"case": "isolated_missing_peak", "chi_reduced": 1.0666134387536021, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "isolated discrete unmodeled peak at +5 eV \u2014 the proposal pass must fire (accepted proposal = the honesty signal)", "regime": "proposal_pass", "runtime_s": 0.01, "seed_offset": 0, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.002, "d_fwhm_ev": 0.0039, "matched_role": "1", "true_center": 196.5}, {"d_center_ev": -0.0048, "d_fwhm_ev": -0.0107, "matched_role": "2", "true_center": 201.5}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:188:{"case": "isolated_missing_peak", "chi_reduced": 1.2748899162782585, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "isolated discrete unmodeled peak at +5 eV \u2014 the proposal pass must fire (accepted proposal = the honesty signal)", "regime": "proposal_pass", "runtime_s": 0.01, "seed_offset": 1000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0002, "d_fwhm_ev": 0.0115, "matched_role": "1", "true_center": 196.5}, {"d_center_ev": -0.0036, "d_fwhm_ev": 0.0136, "matched_role": "2", "true_center": 201.5}], "truth_n": 2}
docs/autofit/inventory/stress_battery_runs.jsonl:192:{"case": "isolated_missing_peak", "chi_reduced": 2.5338616877524722, "config": {"background_method": "linear"}, "expectation": "honesty", "method": "least_squares", "notes": "isolated discrete unmodeled peak at +5 eV \u2014 the proposal pass must fire (accepted proposal = the honesty signal)", "regime": "proposal_pass", "runtime_s": 0.01, "seed_offset": 2000, "success": true, "true_candidates": [], "truth_match": [{"d_center_ev": 0.0031, "d_fwhm_ev": 0.0137, "matched_role": "1", "true_center": 196.5}, {"d_center_ev": -0.0032, "d_fwhm_ev": 0.0088, "matched_role": "2", "true_center": 201.5}], "truth_n": 2}
uploads/a0499bc7-9313-4388-8408-d6e42386862c.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 22.5, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.5000049005795, "fwhm": 0.8000022727809339, "amplitude": 5999.985762735916, "gl_ratio": 8.555378627761456e-13, "stderr": {"center": 1.962102350870924e-06, "amplitude": 0.04162189670815025, "fwhm": 4.680060151954143e-06, "gl_ratio": 3.7802776622909907e-06}}], "confidence": {"main_aliphatic": {"sigma_stat": {"uncertainty_kind": "covariance", "values": {"center": 1.962102350870924e-06, "fwhm": 4.680060151954143e-06, "amplitude": 0.04162189670815025}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 2.7853275241795927e-12, "fwhm_mad": 4.9372728128105337e-11, "amplitude_mad": 2.594129000499379e-07}, "detectability": {"amplitude": 5999.985762735916, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:fwhm@min"], "max_cross_correlation": 0.6776994710374912}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "AG0_graphite_asymGL_satellite", "n_components": 2, "reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "bic_raw": -1732.2640251122796, "bic_weighted": 52.64466679288834, "n_eff_lag1": 366.3534125802044, "survived": true, "rank": 3, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['satellite_pi:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 3.186674785301061e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["satellite_pi:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_linked", "n_components": 3, "reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "bic_raw": -1721.6806443935482, "bic_weighted": 58.4939949414036, "n_eff_lag1": 363.28017154566334, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:fwhm@min', 'contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 5.19904519042311e-12}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.186864808391868e-11}], "proposed_peaks": [{"role": "proposed_peak_0", "accepted": false, "fitted_center": 284.0562, "fitted_fwhm": 0.5, "width_capped": false, "rejection_reason": "amplitude 1.0 \u2264 noise_floor 1.0", "near_roi_endpoint": false}], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_graphite_sym_CO_C=O", "n_components": 3, "reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "bic_raw": -1709.979884899033, "bic_weighted": 70.19264450130285, "n_eff_lag1": 363.28024523651777, "survived": true, "rank": 2, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_C=O:fwhm@max'], unphysical_widths=['contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.1271782252075944e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.382268211640556e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": ["contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)"], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["contamination_CO:center@max", "contamination_C=O:fwhm@max"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "bic_raw": -1708.8655954986962, "bic_weighted": 76.0419659126833, "n_eff_lag1": 366.35338688232457, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 7.909867801039288e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["main_aliphatic:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_linked", "n_components": 3, "reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "bic_raw": -1708.8655820330348, "bic_weighted": 76.04196591267502, "n_eff_lag1": 366.3533885732838, "survived": true, "rank": 5, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.4061902357893664e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 1.3408724708678914e-14}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "n_components": 3, "reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "bic_raw": -1708.8655817728024, "bic_weighted": 76.04196591267494, "n_eff_lag1": 366.3533923770929, "survived": true, "rank": 4, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.628908028198292e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.753864998110036e-16}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}], "non_converged": [], "ambiguous_pairs": [["B2_linked", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.12); structural difference: {'main_graphitic', 'main_aliphatic', 'contamination_CO', 'contamination_C=O', 'satellite_pi'}"], ["B2_graphite_sym_CO_C=O", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.11); structural difference: {'contamination_C=O', 'satellite_pi', 'contamination_CO'}"], ["AG0_graphite_asymGL_satellite", "AG1_graphite_asymGL_sat_plus_CO", "Indistinguishable on fit quality and BIC* (\u0394BIC*=0.00); structural difference: {'contamination_CO'}"]], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max", "residual_gap"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8, "residual_gap": {"n_attempts": 1, "n_accepted": 0}}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 2356.1031279564713, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 2379.5009607446636, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 2402.898356672834, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 2426.2955913250544, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 2379.5009606895596, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 2397.0489719191914, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 2414.5969365032793, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 2379.500437560467, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 2397.0484483372284, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 2414.596388869996, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": -1732.2628630458792, "selected": true}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": -1708.8655817728024, "selected": true}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": -1685.4717428556983, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": -1662.0718740907616, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": -1708.8655820330348, "selected": true}, {"name": "AG2_linked", "converged": true, "bic": -1691.3175603688178, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": -1673.7697813731577, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2379.5009857340206, "selected": false}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2402.8983010024053, "selected": false}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2426.29571673858, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2449.693448965505, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": -1708.8655888943526, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": -1685.4680086668614, "selected": false}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": -1662.0707790890274, "selected": false}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": -690.5033612735614, "selected": false}, {"name": "B2_linked", "converged": true, "bic": -1721.6789198318845, "selected": true}, {"name": "B3_linked", "converged": true, "bic": -1704.1305018737503, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": -1709.9798453429748, "selected": true}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": -1686.5824714043713, "selected": false}], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"AG0_graphite_asymGL_satellite": {"reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "aicc": -1766.373823502721, "n_params": 9, "n_params_adjusted": 5, "n_components": 2}, "B2_linked": {"reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "aicc": -1759.519130288255, "n_params": 10, "n_params_adjusted": 4, "n_components": 3}, "B2_graphite_sym_CO_C=O": {"reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "aicc": -1755.2376505218683, "n_params": 12, "n_params_adjusted": 4, "n_components": 3}, "MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "aicc": -1757.8137245449122, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "AG1_linked": {"reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "aicc": -1757.8137110792509, "n_params": 13, "n_params_adjusted": 6, "n_components": 3}, "AG1_graphite_asymGL_sat_plus_CO": {"reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "aicc": -1757.8137108190185, "n_params": 13, "n_params_adjusted": 5, "n_components": 3}}, "top_by_bic_star": "B2_linked", "top_by_aicc": "AG0_graphite_asymGL_satellite", "bic_ambiguous": true, "criteria_conflict": true, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "B2_linked", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "preseeded_features": [], "n_survivors": 5, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner B2_linked has constraint violations ['main_aliphatic:fwhm@min', 'contamination_CO:center@min'] (see analysis.candidates). ", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
uploads/58ef8f7c-8e65-4581-a1d5-b342298d1425.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 60.5, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_graphitic", "region": "C 1s", "phase_id": "sample", "shape": "ds_g", "center": 284.40862660161633, "fwhm": 0.6625927514639813, "amplitude": 3312.068644701938, "alpha": 4.6264159170306125e-12, "beta": 0.05, "m_gauss": 0.6625927514639813}, {"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.60000000001236, "fwhm": 0.8000000000185057, "amplitude": 2954.930348377461, "gl_ratio": 1.5421386390102043e-11}], "confidence": {"main_graphitic": {"sigma_stat": {"uncertainty_kind": "stability_mad", "values": {"center": 0.04460548852011925, "fwhm": 0.02629222009172294, "amplitude": 1333.794922536627}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 0.04460548852011925, "fwhm_mad": 0.02629222009172294, "amplitude_mad": 1333.794922536627}, "detectability": {"amplitude": 3312.068644701938, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": [], "max_cross_correlation": null}}, "main_aliphatic": {"sigma_stat": {"uncertainty_kind": "stability_mad", "values": {"center": 1.1368683772161603e-13, "fwhm": 0.0, "amplitude": 0.01636871560003783}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 0.75, "position_mad": 1.1368683772161603e-13, "fwhm_mad": 0.0, "amplitude_mad": 0.01636871560003783}, "detectability": {"amplitude": 2954.930348377461, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "max_cross_correlation": null}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866390594288e-06, "bic_star": -1732.2629233085559, "bic_raw": -1708.8656241887684, "bic_weighted": 76.04196591268362, "n_eff_lag1": 366.3533853562398, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.732479228417388e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 4}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "n_components": 4, "reduced_chi_sq": 2.2538587778357373e-06, "bic_star": -1732.262137328864, "bic_raw": -1685.467539089289, "bic_weighted": 99.4392650324933, "n_eff_lag1": 366.353460351388, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:offset@max', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.4702538358659414e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.515142706037034e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["contamination_CO:fwhm@min", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:offset@max", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 4}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "n_components": 5, "reduced_chi_sq": 2.2815134764749067e-06, "bic_star": -1732.262147660311, "bic_raw": -1662.0702503009486, "bic_weighted": 122.83656415227738, "n_eff_lag1": 366.3534720499048, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_C=O:center@max', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.5356066679308465e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.3563402013254895e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 6.937798106689261e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.25, "boundary_hits": ["contamination_C=O:center@max", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 3}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "n_components": 6, "reduced_chi_sq": 2.1990369814617878e-06, "bic_star": -1762.164200824285, "bic_raw": -1668.5750043451353, "bic_weighted": 146.2338275885795, "n_eff_lag1": 401.06051089289645, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 2.889000740966408e-10}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.084367297735124e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 3.3135447554575374e-11}, {"role": "contamination_OC=O", "persistence": 0.0, "area_fraction": 5.868305324176354e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.25, "boundary_hits": ["contamination_CO:center@max", "contamination_CO:fwhm@min", "contamination_C=O:fwhm@min", "contamination_OC=O:fwhm@min", "main_aliphatic:offset@min", "main_aliphatic:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 1}, {"name": "M0_graph_asym_aliph_sym_satellite", "n_components": 3, "reduced_chi_sq": 0.5445546916051832, "bic_star": 2199.204211199102, "bic_raw": 2222.6015103188893, "bic_weighted": 252.6177190470987, "n_eff_lag1": 4.371020551972791, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:center@min', 'main_aliphatic:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 1.1139261674936666e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": true, "min_active_persistence": 0.25, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 1}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "n_components": 4, "reduced_chi_sq": 0.5511354169322392, "bic_star": 2199.1834191338194, "bic_raw": 2245.9780173733943, "bic_weighted": 276.01501948372095, "n_eff_lag1": 4.3708990513348684, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:center@min', 'main_aliphatic:fwhm@min', 'contamination_CO:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.2370351534164325e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.487697359241712e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": true, "min_active_persistence": 0.75, "boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_CO:fwhm@min", "satellite_pi:fwhm@min"], "orphan_peaks": true, "best_minimum_basin_support": 2}], "non_converged": [], "ambiguous_pairs": [], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 3753.6915569887074, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 3777.0797675518816, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 3800.4736710871393, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 3823.878033686888, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 3777.0797675518816, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 3794.6107745192317, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 3812.179292646422, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 3777.07751804941, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 3794.603988962943, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 3812.1648087337817, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": 3203.092457785431, "selected": false}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": 3226.4895926311533, "selected": false}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": 3249.886864603099, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 3273.2841770393084, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": 3226.4896031446615, "selected": false}, {"name": "AG2_linked", "converged": true, "bic": 3244.0434203132595, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": 3261.5855136976834, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2263.1271879845717, "selected": true}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2286.5244671115156, "selected": true}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2309.921556825529, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2333.3190793743943, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": 1953.573584264419, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": 1976.9708924404435, "selected": true}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": 2000.3681945376777, "selected": true}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": 2023.7655196301753, "selected": true}, {"name": "B2_linked", "converged": true, "bic": 3807.15449535746, "selected": false}, {"name": "B3_linked", "converged": true, "bic": 3824.7024555091207, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": 3813.7161299169506, "selected": false}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": 3837.514037613595, "selected": false}], "filtered_dominant_alternative": {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "bic_star": -1762.164200824285, "delta_bic_vs_winner": 3961.3476199581046, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866390594288e-06, "bic_star": -1732.2629233085559, "aicc": -1757.8137532349845, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "MG1_graphAsymGL_aliph_sat_CO": {"reduced_chi_sq": 2.2538587778357373e-06, "bic_star": -1732.262137328864, "aicc": -1749.045877977565, "n_params": 17, "n_params_adjusted": 9, "n_components": 4}, "MG2_graphAsymGL_aliph_sat_CO_C=O": {"reduced_chi_sq": 2.2815134764749067e-06, "bic_star": -1732.262147660311, "aicc": -1740.0629937567558, "n_params": 21, "n_params_adjusted": 9, "n_components": 5}, "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O": {"reduced_chi_sq": 2.1990369814617878e-06, "bic_star": -1762.164200824285, "aicc": -1760.7582796070465, "n_params": 25, "n_params_adjusted": 9, "n_components": 6}, "M0_graph_asym_aliph_sym_satellite": {"reduced_chi_sq": 0.5445546916051832, "bic_star": 2199.204211199102, "aicc": 2177.343744696054, "n_params": 12, "n_params_adjusted": 8, "n_components": 3}, "M1_graph_asym_aliph_sym_sat_CO": {"reduced_chi_sq": 0.5511354169322392, "bic_star": 2199.1834191338194, "aicc": 2186.037305742729, "n_params": 16, "n_params_adjusted": 8, "n_components": 4}}, "top_by_bic_star": "M1_graph_asym_aliph_sym_sat_CO", "top_by_aicc": "M1_graph_asym_aliph_sym_sat_CO", "bic_ambiguous": false, "criteria_conflict": false, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "M1_graph_asym_aliph_sym_sat_CO", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:center@min", "main_aliphatic:fwhm@min", "contamination_CO:fwhm@min", "satellite_pi:fwhm@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "bic_star": -1762.164200824285, "delta_bic_vs_winner": 3961.3476199581046, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True)"}, "weighted_ic_disagreement": null, "preseeded_features": [], "n_survivors": 1, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner M1_graph_asym_aliph_sym_sat_CO has constraint violations ['main_aliphatic:center@min', 'main_aliphatic:fwhm@min', 'contamination_CO:fwhm@min', 'satellite_pi:fwhm@min'] (see analysis.candidates).  WARNING: filtered candidate MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O beats this winner by \u0394BIC* 3961.3 but did not survive filtering (plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_CO:fwhm@min', 'contamination_C=O:fwhm@min', 'contamination_OC=O:fwhm@min', 'main_aliphatic:offset@min', 'main_aliphatic:fwhm@min', 'satellite_pi:fwhm@min'], unphysical_widths=[], orphan_peaks=True))", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}
uploads/3ee1dcee-2f3a-4c83-a33e-ce349f9dd4e8.job.json:1:{"status": "done", "phase": "done", "elapsed_sec": 21.9, "message": "done", "result": {"method": "ic_model_comparison", "success": true, "structural_only": [], "peaks": [{"role": "main_aliphatic", "region": "C 1s", "phase_id": "sample", "shape": "pseudo_voigt_gl", "center": 284.5000049005795, "fwhm": 0.8000022727809339, "amplitude": 5999.985762735916, "gl_ratio": 8.555378627761456e-13, "stderr": {"center": 1.962102350870924e-06, "amplitude": 0.04162189670815025, "fwhm": 4.680060151954143e-06, "gl_ratio": 3.7802776622909907e-06}}], "confidence": {"main_aliphatic": {"sigma_stat": {"uncertainty_kind": "covariance", "values": {"center": 1.962102350870924e-06, "fwhm": 4.680060151954143e-06, "amplitude": 0.04162189670815025}}, "reference_sensitivity_range": {"kind": "unavailable_single_fit", "range_ev": null}, "stability": {"persistence": 1.0, "position_mad": 2.7853275241795927e-12, "fwhm_mad": 4.9372728128105337e-11, "amplitude_mad": 2.594129000499379e-07}, "detectability": {"amplitude": 5999.985762735916, "noise_floor": 1.0, "floor_multiple": 5.0, "floor_multiple_is_tunable": true, "status": "above_floor"}, "identifiability": {"boundary_hits": ["main_aliphatic:fwhm@min"], "max_cross_correlation": 0.6776994710374912}}}, "analysis": {"method": "ic_model_comparison", "engine_version": "autofit-stage2", "regions": ["C 1s"], "phase_ids": ["sample"], "resolution_notes": ["C 1s: phase 'sample' (conductor), 29 candidates"], "conditional_tier": true, "conditional_reason": "no_clean_survivor", "constants_provenance": {"C 1s": [{"constant": "graphite_reference_ev", "value": 284.4, "status": "VERIFIED", "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS 10.1116/1.1247695 (window anchor)"}, {"constant": "adventitious_reference_ev", "value": 284.8, "status": "CONDITIONAL", "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; Greczynski 10.1002/anie.201916000 \u2014 convention"}, {"constant": "dsg_core_hole_beta_ev", "value": 0.05, "status": "VERIFIED", "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 (\u0393_K(C) \u2248 0.10 eV FWHM \u2192 0.05 HWHM)"}, {"constant": "contamination_offsets_ev", "value": {"CO": [1.5, 0.3], "C=O": [3.0, 0.3], "OC=O": [4.0, 0.4]}, "status": "CONDITIONAL", "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"}, {"constant": "window_widths", "value": {"graphitic": [284.0, 284.8], "aliphatic": [284.6, 285.4], "CO": [285.8, 286.8], "C=O": [287.3, 288.3], "OC=O": [288.5, 289.6], "shake_up_pi": [290.0, 292.0]}, "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"}, {"constant": "fwhm_graphitic_ev", "value": [0.4, 1.2], "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"}, {"constant": "fwhm_contamination_floor_ev", "value": 0.8, "status": "CONDITIONAL", "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman (2020) \u2014 published lower bound for adventitious/aliphatic carbon FWHM"}, {"constant": "fwhm_contamination_ceiling_ev", "value": 2.0, "status": "UNVERIFIED", "source": "lab-adjudicated cap, not a literature value \u2014 expert adjudication 2026-07-03 (docs/autofit/adjudication-decisions.md #5); a literature-reasonable upper bound but a cap, not a target; replaces the prior split 1.6/3.5 caps"}, {"constant": "fwhm_satellite_ev", "value": [1.0, 5.5], "status": "UNVERIFIED", "source": "labeled-set calibration (44 fits, 1.9\u20135.0 eV)"}, {"constant": "dsg_alpha_cap", "value": [0.0, 0.3], "status": "UNVERIFIED", "source": "fitalg numeric guard"}, {"constant": "asymgl_family", "value": "empirical asymmetric envelope", "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"}, {"constant": "asymgl_asymmetry_range", "value": [0.0, 0.5], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical: chosen to bracket the expert reference fits (asymmetry \u2248 0.10, glMix \u2248 0.08\u20130.5) rather than derived from literature; treat as a calibration target, not physics"}, {"constant": "satellite_offset_range_ev", "value": [5.5, 7.0], "status": "UNVERIFIED", "source": "fitalg tunable \u2014 the \u03c0\u2192\u03c0* satellite offset window from the graphitic main"}, {"constant": "aromatic_polymer_fwhm_ev", "value": [0.8, 1.8], "status": "CONDITIONAL", "source": "Beamson & Briggs, High Resolution XPS of Organic Polymers \u2014 The Scienta ESCA300 Database, Wiley (1992): aromatic C 1s 0.9\u20131.5 eV; widened to 0.8\u20131.8 as the generous cross-instrument envelope (the widening beyond the cited range is editorial, not itself literature-derived)"}, {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6], "status": "UNVERIFIED", "source": "UNVERIFIED-empirical (labeled-set + convention): brackets both expert practice (+0.30: graphitic 284.5 vs aliphatic 284.8) and Biesinger's adventitious C-C/C-H convention (284.8 vs graphite 284.4, +0.4)"}, {"constant": "fit_physics:C-1s", "value": {"nominal_be_ev": 284.44, "be_window_ev": [282.0, 289.3], "spin_orbit": null, "tier": "curated"}, "status": "CONDITIONAL", "source": "data/xps/fit-physics.json [curated tier] \u2014 nist-srd-20"}]}, "constants_provenance_scope": "region-wide", "uses_conditional_or_unverified_constants": ["C 1s:adventitious_reference_ev", "C 1s:aliphatic_linked_offset_range_ev", "C 1s:aromatic_polymer_fwhm_ev", "C 1s:asymgl_asymmetry_range", "C 1s:asymgl_family", "C 1s:contamination_offsets_ev", "C 1s:dsg_alpha_cap", "C 1s:fit_physics:C-1s", "C 1s:fwhm_contamination_ceiling_ev", "C 1s:fwhm_contamination_floor_ev", "C 1s:fwhm_graphitic_ev", "C 1s:fwhm_satellite_ev", "C 1s:satellite_offset_range_ev", "C 1s:window_widths"], "candidates": [{"name": "AG0_graphite_asymGL_satellite", "n_components": 2, "reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "bic_raw": -1732.2640251122796, "bic_weighted": 52.64466679288834, "n_eff_lag1": 366.3534125802044, "survived": true, "rank": 3, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['satellite_pi:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 3.186674785301061e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["satellite_pi:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_linked", "n_components": 3, "reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "bic_raw": -1721.6806443935482, "bic_weighted": 58.4939949414036, "n_eff_lag1": 363.28017154566334, "survived": true, "rank": 1, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:fwhm@min', 'contamination_CO:center@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 5.19904519042311e-12}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.186864808391868e-11}], "proposed_peaks": [{"role": "proposed_peak_0", "accepted": false, "fitted_center": 284.0562, "fitted_fwhm": 0.5, "width_capped": false, "rejection_reason": "amplitude 1.0 \u2264 noise_floor 1.0", "near_roi_endpoint": false}], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "B2_graphite_sym_CO_C=O", "n_components": 3, "reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "bic_raw": -1709.979884899033, "bic_weighted": 70.19264450130285, "n_eff_lag1": 363.28024523651777, "survived": true, "rank": 2, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['contamination_CO:center@max', 'contamination_C=O:fwhm@max'], unphysical_widths=['contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)'], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "contamination_CO", "persistence": 0.0, "area_fraction": 3.1271782252075944e-11}, {"role": "contamination_C=O", "persistence": 0.0, "area_fraction": 9.382268211640556e-10}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": ["contamination_C=O:fwhm=2.00eV\u22652.0eV ordinary cap (no known-broad justification)"], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": ["contamination_CO:center@max", "contamination_C=O:fwhm@max"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "MG0_graphAsymGL_aliph_satellite", "n_components": 3, "reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "bic_raw": -1708.8655954986962, "bic_weighted": 76.0419659126833, "n_eff_lag1": 366.35338688232457, "survived": false, "rank": null, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=['main_aliphatic:offset@min'], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 7.909867801039288e-11}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 0.0, "boundary_hits": ["main_aliphatic:offset@min"], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_linked", "n_components": 3, "reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "bic_raw": -1708.8655820330348, "bic_weighted": 76.04196591267502, "n_eff_lag1": 366.3533885732838, "survived": true, "rank": 5, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 4.4061902357893664e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 1.3408724708678914e-14}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "n_components": 3, "reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "bic_raw": -1708.8655817728024, "bic_weighted": 76.04196591267494, "n_eff_lag1": 366.3533923770929, "survived": true, "rank": 4, "filter_reason": "plausibility: PlausibilityFlags(boundary_hits=[], unphysical_widths=[], orphan_peaks=True)", "augmented_from": null, "boundary_fixed_params": [], "absent_slots": [{"role": "satellite_pi", "persistence": 0.0, "area_fraction": 5.628908028198292e-11}, {"role": "contamination_CO", "persistence": 0.0, "area_fraction": 9.753864998110036e-16}], "proposed_peaks": [], "residual_flags": ["C 1s:graphitic", "C 1s:aliphatic"], "unphysical_widths": [], "autocorr_flag": false, "min_active_persistence": 1.0, "boundary_hits": [], "orphan_peaks": true, "best_minimum_basin_support": 5}], "non_converged": [], "ambiguous_pairs": [["B2_linked", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.12); structural difference: {'main_graphitic', 'main_aliphatic', 'contamination_CO', 'contamination_C=O', 'satellite_pi'}"], ["B2_graphite_sym_CO_C=O", "AG0_graphite_asymGL_satellite", "Indistinguishable on fit quality and BIC* (\u0394BIC*=1.11); structural difference: {'contamination_C=O', 'satellite_pi', 'contamination_CO'}"], ["AG0_graphite_asymGL_satellite", "AG1_graphite_asymGL_sat_plus_CO", "Indistinguishable on fit quality and BIC* (\u0394BIC*=0.00); structural difference: {'contamination_CO'}"]], "preseeded_features": [], "candidate_pool": {"sources_run": ["local_max", "curvature_shoulder", "grammar", "residual_gap"], "features": [{"center_be": 284.4, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.0, 284.8], "label": "C 1s:graphitic"}, {"center_be": 284.506, "provenance": ["curvature_shoulder", "local_max", "residual_gap"], "in_grammar_window": true, "seeded_role": null, "gate_fails": ["in_grammar_window"], "fwhm_est": 2.4, "amplitude_net": 5838.344, "fraction_of_max": 1.0, "local_snr": 82.082, "prom_z": 405.33, "ridge_length": 8, "residual_gap": {"n_attempts": 1, "n_accepted": 0}}, {"center_be": 285.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [284.6, 285.4], "label": "C 1s:aliphatic"}, {"center_be": 286.3, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [285.8, 286.8], "label": "C 1s:CO"}, {"center_be": 287.8, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [287.3, 288.3], "label": "C 1s:C=O"}, {"center_be": 289.05, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [288.5, 289.6], "label": "C 1s:OC=O"}, {"center_be": 291.0, "provenance": ["grammar"], "in_grammar_window": true, "seeded_role": null, "gate_fails": [], "fwhm_est": null, "amplitude_net": null, "fraction_of_max": null, "local_snr": null, "prom_z": null, "ridge_length": null, "window": [290.0, 292.0], "label": "C 1s:shake_up_pi"}], "curvature_seeds": [], "tunables": {"prom_z_min": 7.0, "min_fraction_of_max": 0.02, "amplitude_snr": 5.0, "coincidence_ev": 0.5, "max_total_seeds": 6, "pool_local_max_min_snr": 2.0, "cwt_fwhm_scale_range_ev": [0.3, 2.4], "note": "UNVERIFIED engine tunables (synthetic-calibrated; scripts/calibrate_cwt_detector.py)"}, "note": "OVERCOMPLETE detection pool \u2014 features are candidates to prune, not truth; selection (absent-slot / persistence / BIC*) judges.  All gate constants are UNVERIFIED engine tunables.", "detection_model_overflow": []}, "screen": [{"name": "A0_graphite_asym_satellite", "converged": true, "bic": 2356.1031279564713, "selected": false}, {"name": "A1_graphite_asym_sat_plus_CO", "converged": true, "bic": 2379.5009607446636, "selected": false}, {"name": "A2_graphite_asym_sat_plus_CO_C=O", "converged": true, "bic": 2402.898356672834, "selected": false}, {"name": "A3_graphite_asym_sat_plus_CO_C=O_OC=O", "converged": true, "bic": 2426.2955913250544, "selected": false}, {"name": "A1_linked", "converged": true, "bic": 2379.5009606895596, "selected": false}, {"name": "A2_linked", "converged": true, "bic": 2397.0489719191914, "selected": false}, {"name": "A3_linked", "converged": true, "bic": 2414.5969365032793, "selected": false}, {"name": "A1_linked_offset", "converged": true, "bic": 2379.500437560467, "selected": false}, {"name": "A2_linked_offset", "converged": true, "bic": 2397.0484483372284, "selected": false}, {"name": "A3_linked_offset", "converged": true, "bic": 2414.596388869996, "selected": false}, {"name": "AG0_graphite_asymGL_satellite", "converged": true, "bic": -1732.2628630458792, "selected": true}, {"name": "AG1_graphite_asymGL_sat_plus_CO", "converged": true, "bic": -1708.8655817728024, "selected": true}, {"name": "AG2_graphite_asymGL_sat_plus_CO_C=O", "converged": true, "bic": -1685.4717428556983, "selected": false}, {"name": "AG3_graphite_asymGL_sat_plus_CO_C=O_OC=O", "converged": true, "bic": -1662.0718740907616, "selected": false}, {"name": "AG1_linked", "converged": true, "bic": -1708.8655820330348, "selected": true}, {"name": "AG2_linked", "converged": true, "bic": -1691.3175603688178, "selected": false}, {"name": "AG3_linked", "converged": true, "bic": -1673.7697813731577, "selected": false}, {"name": "M0_graph_asym_aliph_sym_satellite", "converged": true, "bic": 2379.5009857340206, "selected": false}, {"name": "M1_graph_asym_aliph_sym_sat_CO", "converged": true, "bic": 2402.8983010024053, "selected": false}, {"name": "M2_graph_asym_aliph_sym_sat_CO_C=O", "converged": true, "bic": 2426.29571673858, "selected": false}, {"name": "M3_graph_asym_aliph_sym_sat_CO_C=O_OC=O", "converged": true, "bic": 2449.693448965505, "selected": false}, {"name": "MG0_graphAsymGL_aliph_satellite", "converged": true, "bic": -1708.8655888943526, "selected": true}, {"name": "MG1_graphAsymGL_aliph_sat_CO", "converged": true, "bic": -1685.4680086668614, "selected": false}, {"name": "MG2_graphAsymGL_aliph_sat_CO_C=O", "converged": true, "bic": -1662.0707790890274, "selected": false}, {"name": "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O", "converged": true, "bic": -690.5033612735614, "selected": false}, {"name": "B2_linked", "converged": true, "bic": -1721.6789198318845, "selected": true}, {"name": "B3_linked", "converged": true, "bic": -1704.1305018737503, "selected": false}, {"name": "B2_graphite_sym_CO_C=O", "converged": true, "bic": -1709.9798453429748, "selected": true}, {"name": "B3_graphite_sym_CO_C=O_OC=O", "converged": true, "bic": -1686.5824714043713, "selected": false}], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "bic_threshold_caveat": "\u0394BIC* thresholds are uncalibrated conventions under residual autocorrelation and background misspecification \u2014 see per-candidate n_eff_lag1 and the stress-test report", "criteria_panel": {"statement": "not independent tests \u2014 BIC*, AICc, \u03c7\u00b2\u1d63 and F share the Gaussian residual/noise assumption on processed data; treat as correlated views of one likelihood", "trust_order": "parity to expert fits \u2192 stability/persistence \u2192 residual structure \u2192 BIC* as a relative tie-breaker only", "per_candidate": {"AG0_graphite_asymGL_satellite": {"reduced_chi_sq": 2.200512918942303e-06, "bic_star": -1755.661324232067, "aicc": -1766.373823502721, "n_params": 9, "n_params_adjusted": 5, "n_components": 2}, "B2_linked": {"reduced_chi_sq": 2.217038382810293e-06, "bic_star": -1756.7765930732294, "aicc": -1759.519130288255, "n_params": 10, "n_params_adjusted": 4, "n_components": 3}, "B2_graphite_sym_CO_C=O": {"reduced_chi_sq": 2.2302744493428828e-06, "bic_star": -1756.7744831386078, "aicc": -1755.2376505218683, "n_params": 12, "n_params_adjusted": 4, "n_components": 3}, "MG0_graphAsymGL_aliph_satellite": {"reduced_chi_sq": 2.226866389581631e-06, "bic_star": -1732.2628946184836, "aicc": -1757.8137245449122, "n_params": 13, "n_params_adjusted": 9, "n_components": 3}, "AG1_linked": {"reduced_chi_sq": 2.2268663648144677e-06, "bic_star": -1749.8108554926628, "aicc": -1757.8137110792509, "n_params": 13, "n_params_adjusted": 6, "n_components": 3}, "AG1_graphite_asymGL_sat_plus_CO": {"reduced_chi_sq": 2.226866364596973e-06, "bic_star": -1755.6601800123774, "aicc": -1757.8137108190185, "n_params": 13, "n_params_adjusted": 5, "n_components": 3}}, "top_by_bic_star": "B2_linked", "top_by_aicc": "AG0_graphite_asymGL_satellite", "bic_ambiguous": true, "criteria_conflict": true, "bic_ambiguity_threshold": 2.0, "f_tests": []}, "cross_candidate_coincidences": []}, "diagnostics": {"winner": "B2_linked", "conditional": true, "conditional_reason": "no_clean_survivor", "winner_boundary_hits": ["main_aliphatic:fwhm@min", "contamination_CO:center@min"], "winner_unphysical_widths": [], "winner_boundary_fixed_params": [], "filtered_dominant_alternative": null, "weighted_ic_disagreement": {"rss_bic_top": "B2_linked", "weighted_bic_top": "AG0_graphite_asymGL_satellite", "note": "the weighted-\u03c7\u00b2 criterion (consistent with the fit weights) prefers a different survivor \u2014 model selection is noise-model-sensitive on this spectrum; treat the ranking as CONDITIONAL on the homoscedastic-RSS form"}, "preseeded_features": [], "n_survivors": 5, "n_filtered": 6, "n_non_converged": 0, "analysis_truncated": false, "n_candidates_evaluated": 6, "n_candidates_total": 29}, "message": "CONDITIONAL result (no_clean_survivor): no candidate passed plausibility cleanly; ranking the stable-but-boundary-limited tier \u2014 winner B2_linked has constraint violations ['main_aliphatic:fwhm@min', 'contamination_CO:center@min'] (see analysis.candidates). ", "review_gate": {"reviewed_by": null, "note": "results are candidates + confidence flags, not ground truth \u2014 a named human review is required before export (spec \u00a78)"}}}

exec
/bin/zsh -lc "rg -n -i 'tougaard' --glob '*.json' --glob '*.jsonl' --glob '*.fit.json' --glob '*.proj.json' --glob '*.spec.json' ." in /Users/skyefortier/xps-verify
 exited 1 in 0ms:
codex
The remaining sweep is not turning up another dead guard. One nuance: the near-uniform branch check still is not meant to catch the full F2 removal by itself; the new weighted-vs-unweighted guard is the discriminating part, and that one is now live.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import sys, types\\nlmfit = types.ModuleType(\"lmfit\")\\nlmfit.Model = object\\nlmfit.Parameters = object\\nsys.modules[\"lmfit\"] = lmfit\\nscipy = types.ModuleType(\"scipy\")\\nintegrate = types.ModuleType(\"scipy.integrate\")\\nintegrate.trapezoid = lambda *a, **k: (_ for _ in ()).throw(RuntimeError(\"unused\"))\\nscipy.integrate = integrate\\nsys.modules[\"scipy\"] = scipy\\nsys.modules[\"scipy.integrate\"] = integrate\\nimport numpy as np\\nfrom fitting import tougaard_background\\nB, C = 2866.0, 1643.0\\nx = np.linspace(740.0, 700.0, 600)\\ny = 4000.0 + 800.0 * (740.0 - x) / 40.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2)\\n# reproduce raw integral for scale sign\\nc0 = float(y[-1])\\nnet = y - c0\\ndx = abs(x[1]-x[0])\\nm = np.arange(len(x), dtype=float)\\nT = m * dx\\nk = (B*T)/(C+T*T)**2\\nraw = np.convolve(net, k[::-1])[len(x)-1:] * dx\\nscale = (float(y[0]) - c0) / raw[0]\\nbg = tougaard_background(x, y)\\nprint(\"ya0 c0 delta raw0 scale bg_min bg_max edges\", float(y[0]), c0, float(y[0]-c0), float(raw[0]), float(scale), float(bg.min()), float(bg.max()), float(bg[0]), float(bg[-1]))\\n'" in /Users/skyefortier/xps-verify
 succeeded in 130ms:
ya0 c0 delta raw0 scale bg_min bg_max edges 4000.0 4800.00000050155 -800.00000050155 175.98923765218063 -4.545732518500045 3649.8333683676474 4805.618091970655 4000.0 4800.00000050155

exec
/bin/zsh -lc 'git show 173f002''^:fitting.py | rg -n "Negative counts|no clamping|scale =|bg'"\\[0\\]\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yStqQZ5H' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PWirrNYw' (errno=Operation not permitted)
621:    # net loss signal accumulates at the high-BE edge (bg[0] == 0 — e.g. a
625:    # signal (the pre-F1 behaviour). Negative counts (physically invalid
626:    # input) pass through signed; no clamping policy is imposed here.
627:    if bg[0] == 0.0:
630:        out = c0 + bg * ((float(ya[0]) - c0) / bg[0])
1140:                    scale = 1.0 + rng.uniform(-0.15, 0.15)

exec
/bin/zsh -lc "git show 173f002:tests/test_tougaard_background.py | nl -ba | sed -n '206,268p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-D1yxEmgN' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-UnLLer1z' (errno=Operation not permitted)
   206	def test_nonuniform_grid_uses_local_quadrature_weights():
   207	    """F2 regression pin (2026-07-17): the nonuniform-grid branch must weight
   208	    each term by its local energy spacing.
   209	
   210	    It previously used exact per-point separations but omitted the spacing
   211	    weights, silently applying uniform-grid quadrature inside the branch
   212	    written precisely BECAUSE the grid is not uniform (~24% error on a
   213	    genuinely nonuniform grid). np.gradient returns dx exactly on a uniform
   214	    grid, so the two branches must now agree to floating point -- the
   215	    uniformity test is an optimization, not a semantic fork."""
   216	    # Uniform grid, then the same grid perturbed below the uniformity
   217	    # tolerance so the nonuniform branch runs on near-identical data.
   218	    x = np.linspace(740.0, 700.0, 300)
   219	    y = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))
   220	    bg_uniform = tougaard_background(x, y)
   221	    x_jitter = x.copy()
   222	    x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
   223	    bg_nonuniform = tougaard_background(x_jitter, y)
   224	    assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
   225	        "uniform and nonuniform branches disagree on near-identical grids"
   226	    )
   227	
   228	    # Genuinely nonuniform grid vs an explicit spacing-weighted reference.
   229	    # A high-BE endpoint RISE (not just a symmetric peak on a flat baseline)
   230	    # is required here: the F1 anchor rescales by (ya[0]-c0)/bg[0], so a
   231	    # fixture whose two edges sit at nearly the same level collapses that
   232	    # scale factor toward zero and the F2 weighting difference vanishes
   233	    # into the noise floor *after* anchoring -- passing this assertion even
   234	    # with the w[i:] weighting removed entirely (caught by Codex review,
   235	    # 2026-07-17: the original flat-baseline fixture measured a 4.5e-13 max
   236	    # diff between weighted and unweighted output, i.e. it did not actually
   237	    # guard F2). The endpoint delta below (~800 counts) keeps the anchored
   238	    # scale non-degenerate, so the ~105-count weighted-vs-unweighted
   239	    # divergence survives anchoring and this pin is falsifiable again.
   240	    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
   241	                         np.linspace(720.0, 700.0, 400)])
   242	    ya = 4000.0 + 800.0 * (xa - 700.0) / 40.0 + 6000.0 * np.exp(
   243	        -0.5 * ((xa - 710.9) / 1.6) ** 2
   244	    )
   245	    got = tougaard_background(xa, ya)
   246	
   247	    B_coef, C_coef = 2866.0, 1643.0
   248	    c0 = float(ya[-1])
   249	    net = ya - c0
   250	    w = np.abs(np.gradient(xa))
   251	    ref = np.zeros(len(xa))
   252	    ref_unweighted = np.zeros(len(xa))
   253	    for i in range(len(xa)):
   254	        T = np.abs(xa[i:] - xa[i])
   255	        kernel = (B_coef * T) / (C_coef + T * T) ** 2
   256	        ref[i] = float(np.sum(kernel * net[i:] * w[i:]))
   257	        ref_unweighted[i] = float(np.sum(kernel * net[i:]))
   258	    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
   259	    ref_unweighted = c0 + ref_unweighted * ((float(ya[0]) - c0) / ref_unweighted[0])
   260	
   261	    # The pin only means something if weighted and unweighted actually
   262	    # disagree on this fixture -- guard the guard.
   263	    assert np.max(np.abs(ref - ref_unweighted)) > 10.0, (
   264	        "fixture does not separate weighted from unweighted quadrature -- "
   265	        "endpoint delta too small to survive the F1 anchor, pin is dead"
   266	    )
   267	    assert np.allclose(got, ref, rtol=1e-9), (
   268	        "nonuniform branch does not match spacing-weighted quadrature"

exec
/bin/zsh -lc 'git show 173f002''^:tests/test_tougaard_background.py | nl -ba | sed -n '"'206,252p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-WfbxpcNX' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-95lRRWmP' (errno=Operation not permitted)
   206	def test_nonuniform_grid_uses_local_quadrature_weights():
   207	    """F2 regression pin (2026-07-17): the nonuniform-grid branch must weight
   208	    each term by its local energy spacing.
   209	
   210	    It previously used exact per-point separations but omitted the spacing
   211	    weights, silently applying uniform-grid quadrature inside the branch
   212	    written precisely BECAUSE the grid is not uniform (~24% error on a
   213	    genuinely nonuniform grid). np.gradient returns dx exactly on a uniform
   214	    grid, so the two branches must now agree to floating point -- the
   215	    uniformity test is an optimization, not a semantic fork."""
   216	    # Uniform grid, then the same grid perturbed below the uniformity
   217	    # tolerance so the nonuniform branch runs on near-identical data.
   218	    x = np.linspace(740.0, 700.0, 300)
   219	    y = (4000.0 + 6000.0 * np.exp(-0.5 * ((x - 710.9) / 1.6) ** 2))
   220	    bg_uniform = tougaard_background(x, y)
   221	    x_jitter = x.copy()
   222	    x_jitter[1:-1] += 1e-4 * np.sin(np.arange(len(x) - 2))
   223	    bg_nonuniform = tougaard_background(x_jitter, y)
   224	    assert np.max(np.abs(bg_uniform - bg_nonuniform)) < 1e-1, (
   225	        "uniform and nonuniform branches disagree on near-identical grids"
   226	    )
   227	
   228	    # Genuinely nonuniform grid vs an explicit spacing-weighted reference.
   229	    xa = np.concatenate([np.linspace(740.0, 720.1, 60),
   230	                         np.linspace(720.0, 700.0, 400)])
   231	    ya = np.interp(xa[::-1], x[::-1], y[::-1])[::-1]
   232	    got = tougaard_background(xa, ya)
   233	
   234	    B_coef, C_coef = 2866.0, 1643.0
   235	    c0 = float(ya[-1])
   236	    net = ya - c0
   237	    w = np.abs(np.gradient(xa))
   238	    ref = np.zeros(len(xa))
   239	    for i in range(len(xa)):
   240	        T = np.abs(xa[i:] - xa[i])
   241	        ref[i] = float(np.sum((B_coef * T) / (C_coef + T * T) ** 2 * net[i:] * w[i:]))
   242	    ref = c0 + ref * ((float(ya[0]) - c0) / ref[0])
   243	    assert np.allclose(got, ref, rtol=1e-9), (
   244	        "nonuniform branch does not match spacing-weighted quadrature"
   245	    )
   246	
   247	
   248	def test_short_input_returns_zeros():
   249	    """< 2 points: no background can be defined; must return zeros."""
   250	    assert np.array_equal(
   251	        tougaard_background(np.array([284.8]), np.array([123.0])), np.array([0.0])
   252	    )

codex
1. No findings.

Recheck evidence:
- New fixture endpoint delta is live: `ya[0]=4800.0`, `ya[-1]=4000.0000005015495`, delta `~800.0`.
- F1 anchor is non-degenerate: weighted raw `bg[0]=470.200100113026`, anchor scale `1.7014032946954876`.
- Weighted vs unweighted anchored references now diverge by `104.82975035097024` counts, so the `> 10.0` guard holds with about 10x margin. That is loose enough to avoid fragility and tight enough not to pass the old collapsed fixture.
- Simulated F2 removal fails this test: unweighted production vs weighted ref `allclose=False`, max diff `104.82975035097024`.
- Current production matches the weighted ref exactly in the reproduction: max diff `0.0`.

Scope confirmed: `git show 173f002` / `git diff 173f002^ 173f002` touch only `tests/test_tougaard_background.py`; no diff in `fitting.py`, `templates/index.html`, `tests/js/tougaard_twin.test.js`, `autofit/engine.py`, `autofit/methods/*.py`, or `app.py` `/api/fit`.

Tests:
- `node --test tests/js/tougaard_twin.test.js`: 6/6 pass.
- Python `pytest` could not run normally because this sandbox lacks `pytest`, `lmfit`, and `scipy`; I directly executed all 9 plain-assert Python Tougaard tests with only import stubs for unused deps, and all 9 passed.

Additional checks:
- `rg -i tougaard` across JSON/JSONL saved-fit and inventory fixtures found no Tougaard numeric output pins.
- Negative-scale anchoring is pre-existing and documented before `173f002`; computed a falling-endpoint case with scale `-4.5457`, passed through unclamped.
- Fresh sweep of Python/JS Tougaard pins found no other endpoint-collapse or dead-guard issue. The near-uniform branch check is not independently F2-discriminating, but the new explicit weighted/unweighted guard is.

VERDICT: GO
tokens used
100,552
1. No findings.

Recheck evidence:
- New fixture endpoint delta is live: `ya[0]=4800.0`, `ya[-1]=4000.0000005015495`, delta `~800.0`.
- F1 anchor is non-degenerate: weighted raw `bg[0]=470.200100113026`, anchor scale `1.7014032946954876`.
- Weighted vs unweighted anchored references now diverge by `104.82975035097024` counts, so the `> 10.0` guard holds with about 10x margin. That is loose enough to avoid fragility and tight enough not to pass the old collapsed fixture.
- Simulated F2 removal fails this test: unweighted production vs weighted ref `allclose=False`, max diff `104.82975035097024`.
- Current production matches the weighted ref exactly in the reproduction: max diff `0.0`.

Scope confirmed: `git show 173f002` / `git diff 173f002^ 173f002` touch only `tests/test_tougaard_background.py`; no diff in `fitting.py`, `templates/index.html`, `tests/js/tougaard_twin.test.js`, `autofit/engine.py`, `autofit/methods/*.py`, or `app.py` `/api/fit`.

Tests:
- `node --test tests/js/tougaard_twin.test.js`: 6/6 pass.
- Python `pytest` could not run normally because this sandbox lacks `pytest`, `lmfit`, and `scipy`; I directly executed all 9 plain-assert Python Tougaard tests with only import stubs for unused deps, and all 9 passed.

Additional checks:
- `rg -i tougaard` across JSON/JSONL saved-fit and inventory fixtures found no Tougaard numeric output pins.
- Negative-scale anchoring is pre-existing and documented before `173f002`; computed a falling-endpoint case with scale `-4.5457`, passed through unclamped.
- Fresh sweep of Python/JS Tougaard pins found no other endpoint-collapse or dead-guard issue. The near-uniform branch check is not independently F2-discriminating, but the new explicit weighted/unweighted guard is.

VERDICT: GO
