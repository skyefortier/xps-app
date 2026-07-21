"""Find Peaks math-first architecture, Step 1 (i)+(ii) (2026-07-21):
decouple the CWT ridge detector's own scale ceiling, and the curvature-
channel seed's ``fwhm_init`` clip in ``build_candidate_pool``, from the
chemistry constant ``FWHM_MAX_ORDINARY_EV`` -- drive both from ROI width
and grid step instead. See
docs/autofit/find-peaks-math-first-architecture.md.

Scope discipline (Skye, 2026-07-21): ``FWHM_MAX_ORDINARY_EV`` played three
distinct roles in the detection path, split by MEANING, not by "it's the
same constant":
  (i)   the detector's own scale ceiling (``CWT_FWHM_MAX_EV``)
        -- how well we CHARACTERIZE what's present.
  (ii)  the seed ``fwhm_init`` clip inside ``build_candidate_pool``
        -- also characterization (the starting estimate handed to the
        optimizer).
  (iii) the fit's free-parameter bound on ``preseed_curvature_*`` slots
        -- a different question, what a component may BECOME (degeneracy
        control). Left untouched here; that is step 6 of the migration
        outline ("treat ceiling-pegged widths as evidence for k+1").

This file covers (i) and (ii) only.

Real-spectrum verification (the actual reported bug): the file
"docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, 10spot.DATA/
N1s Scan_2.VGD" (raw, uncorrected) has a genuine broad hump near
400.6-400.9 eV. Measured BEFORE this change (2026-07-21): a ridge IS
detected there (`center_be=400.02, fwhm_est=2.40, prom_z=34.02,
ridge_length=8/8`) -- this corrected the architecture doc's original
"invisible" framing: the detector is not blind to the shoulder, it is
WIDTH-BLIND (fwhm_est pegged exactly at the old fixed ceiling). AFTER:
the estimate must reflect the true, wider hump.
"""
from __future__ import annotations

import numpy as np
import pytest

from autofit.candidates import (
    CWT_FWHM_MIN_EV,
    CWT_PROM_Z_MIN,
    CWT_SIGMA_MIN_PTS,
    _FWHM_PER_SIGMA,
    build_candidate_pool,
    cwt_ridge_features,
    cwt_scale_range_ev,
)


def _pv(x, height, center, fwhm, eta):
    g = np.exp(-4 * np.log(2) * ((x - center) / fwhm) ** 2)
    lo = (fwhm / 2) ** 2 / ((x - center) ** 2 + (fwhm / 2) ** 2)
    return height * ((1 - eta) * g + eta * lo)


ETA = 0.30


# ── (i) detector scale ceiling: derived, not fixed ─────────────────────────

def test_cwt_scale_range_floor_is_unchanged_instrument_resolution():
    """CWT_FWHM_MIN_EV (0.3 eV) is instrument-resolution physics -- nothing
    narrower is real XPS signal -- and stays FIXED regardless of ROI,
    unlike the ceiling."""
    x_narrow = np.arange(0.0, 8.0, 0.05)
    x_wide = np.arange(0.0, 35.0, 0.1)
    lo_narrow, _ = cwt_scale_range_ev(x_narrow)
    lo_wide, _ = cwt_scale_range_ev(x_wide)
    assert lo_narrow == CWT_FWHM_MIN_EV == 0.3
    assert lo_wide == CWT_FWHM_MIN_EV == 0.3


def test_cwt_scale_range_ceiling_scales_with_roi_width_not_fixed():
    """The ceiling must be DERIVED from ROI width and grid step -- not the
    old fixed CWT_FWHM_MAX_EV = 2.4 ("just above FWHM_MAX_ORDINARY_EV =
    2.0"). A wider ROI must yield a wider ceiling; narrower, narrower;
    and the ceiling should scale roughly linearly with ROI width (the
    structural kernel-fits-in-window bound is a fixed fraction of ROI
    width for a fixed grid step)."""
    x_narrow = np.arange(0.0, 8.0, 0.05)     # narrow C1s-like window
    x_medium = np.arange(0.0, 18.1, 0.1)     # matches the real N1s file
    x_wide = np.arange(0.0, 35.1, 0.1)       # matches the real joint U4f+N1s file
    _, hi_narrow = cwt_scale_range_ev(x_narrow)
    _, hi_medium = cwt_scale_range_ev(x_medium)
    _, hi_wide = cwt_scale_range_ev(x_wide)
    assert hi_narrow < hi_medium < hi_wide, (
        "ceiling must scale with ROI width", hi_narrow, hi_medium, hi_wide)
    assert hi_medium / 18.1 == pytest.approx(hi_wide / 35.1, rel=0.05), (
        "same grid step -> ceiling should be a near-constant fraction of "
        "ROI width (structural kernel-fits-in-window bound)"
    )


def test_cwt_scale_range_traces_to_existing_kernel_truncation_not_a_new_number():
    """The derivation must be traceable to the EXISTING kernel-truncation
    convention (radius = ceil(4.0*sigma), already used elsewhere in this
    module's per-scale window-fit filter) -- not a fresh, unrelated
    coefficient. Recompute the expected ceiling directly from that
    formula and confirm the helper matches exactly."""
    x = np.arange(0.0, 18.1, 0.1)
    n = len(x)
    step = 0.1
    # radius = ceil(4.0*sigma); fit-in-window: 2*radius+1 <= n
    # => sigma <= (n-1)/8 (using the SAME "4.0" truncation already used
    # by cwt_ridge_features' own per-scale filter and kernel construction)
    expected_max_sigma = max((n - 1) / 8.0, CWT_SIGMA_MIN_PTS)
    expected_hi = expected_max_sigma * _FWHM_PER_SIGMA * step
    _, hi = cwt_scale_range_ev(x)
    assert hi == pytest.approx(expected_hi, rel=1e-9)


def test_cwt_scale_range_degrades_gracefully_for_tiny_windows():
    """A very short window must not crash or produce a nonsensical
    (negative/zero) ceiling -- floors at CWT_SIGMA_MIN_PTS same as the
    lower bound."""
    x = np.arange(0.0, 1.6, 0.1)   # 16 points, the module's own minimum
    lo, hi = cwt_scale_range_ev(x)
    assert hi >= lo > 0.0


# ── real-spectrum red/green: the actual reported bug ────────────────────────

_N1S_FILE = ("docs/autofit/test_data/4 UCl4-BN 4%, Cu, 1eV, 180 mA, 200 um, "
             "10spot.DATA/N1s Scan_2.VGD")


def test_real_ucl4_bn_n1s_shoulder_no_longer_pegged_at_old_ceiling():
    """Red-green on the actual reported bug spectrum. BEFORE (measured
    2026-07-21, prior to this fix): the shoulder near 400.6-400.9 eV
    produces a ridge with fwhm_est PEGGED exactly at the old fixed
    ceiling (2.40 eV) -- width-blind, not invisible (this measurement
    corrected the architecture doc's original wrong diagnosis).

    AFTER: the honest correction is NOT "the estimate must get bigger" --
    a direct per-scale scan (done before writing this assertion) shows
    this feature's prominence-z genuinely PEAKS around 2.1-2.3 eV FWHM
    and falls off on both sides; the old 2.40 eV value was coincidentally
    close, but was reported ONLY because the ladder ran out of rungs
    there, not because the algorithm found it to be the best match. The
    correct invariant is that the new estimate is a genuine INTERIOR
    local maximum of the (now finer, wider) ladder -- strictly between
    its own floor and ceiling, never pinned to either boundary -- rather
    than a value forced out by truncation. Whether that interior optimum
    lands above, at, or below the old fixed number is incidental; what
    matters is that it is no longer a boundary artifact of a ladder that
    stopped too soon."""
    from vgd_parser import parse_vgd

    from autofit.candidates import cwt_scale_range_ev

    be, cts = parse_vgd(_N1S_FILE)
    x = np.asarray(be, dtype=float)
    y = np.asarray(cts, dtype=float)

    feats = cwt_ridge_features(x, y)
    shoulder = [f for f in feats if 399.0 <= f.center_be <= 401.5]
    assert shoulder, "fixture assumption: the shoulder ridge must still be found"
    f = max(shoulder, key=lambda f: f.prom_z)
    assert f.prom_z >= 30.0, (
        "fixture assumption: this is the same high-significance ridge "
        "measured before this fix (prom_z=34.02)"
    )
    lo, hi = cwt_scale_range_ev(x)
    assert lo < f.fwhm_est_ev < hi, (
        "the shoulder's width estimate must be a genuine interior local "
        f"maximum of the derived ladder ({lo:.2f}-{hi:.2f} eV), not "
        f"pinned to either boundary -- got {f.fwhm_est_ev:.2f}"
    )
    assert f.fwhm_est_ev != 2.40, (
        "must no longer equal the OLD fixed ceiling by construction "
        f"(a coincidental match to 2.40 would need independent scrutiny) "
        f"-- got {f.fwhm_est_ev:.2f}"
    )


def test_real_ucl4_bn_n1s_main_peak_still_found_and_still_sharp():
    """Non-regression: the dominant, extremely sharp N 1s/U-related main
    peak at ~392.2-392.4 eV (prom_z in the thousands) must still be found
    and read as highly significant.

    Corrected 2026-07-21 (Codex step-1 review, Run A -- confirmed real):
    this test previously claimed the peak's width characterization was
    "essentially unchanged" but never actually asserted a width bound, so
    a regression where this feature's fwhm_est started chasing the ROI's
    derived ceiling (the documented monotonic-prom_z-vs-scale behavior
    some sharp/strong peaks show -- see test_cwt_detector.py's
    test_feature_fields_populated) would have passed silently. Measured:
    this specific real feature's fwhm_est is 2.14 eV, a genuine interior
    rung of this file's ROI (derived range 0.3-5.30 eV) -- NOT
    ceiling-pegged, unlike the synthetic isolated-peak case. Asserting
    that explicitly now."""
    from vgd_parser import parse_vgd

    be, cts = parse_vgd(_N1S_FILE)
    x = np.asarray(be, dtype=float)
    y = np.asarray(cts, dtype=float)

    feats = cwt_ridge_features(x, y)
    main = [f for f in feats if 391.5 <= f.center_be <= 393.0]
    assert main, "fixture assumption: the dominant main peak must be found"
    f = max(main, key=lambda f: f.prom_z)
    assert f.prom_z > 500.0
    ceiling = cwt_scale_range_ev(x)[1]
    assert 0.3 < f.fwhm_est_ev < 0.9 * ceiling, (
        f"main peak's fwhm_est ({f.fwhm_est_ev:.3f} eV) is chasing this "
        f"ROI's derived ceiling ({ceiling:.3f} eV) rather than reading as "
        "a genuine, bounded characterization of a sharp real peak"
    )


# ── negative control: no new spurious detections on featureless data ──────

def test_negative_control_flat_slope_sigmoid_no_meaningful_fp_rate_increase():
    """The risk to attack directly (Skye, 2026-07-21): does a wider
    ceiling let the detector latch onto broad background curvature on a
    flat/sloped/sigmoid, effectively-featureless region -- the
    "sloped/poorly-subtracted background" case Skye actually named, NOT
    a hard step discontinuity (a separate, far more pathological input;
    measured pre-existing at n>=40 under the OLD fixed ladder too --
    tracked as a known detector limitation, not this test's job).

    Widened 2026-07-21 (Codex step-1 review, both runs independently):
    the original version of this test covered only ONE ROI size (181
    pts) with a loose 15% tolerance -- loose enough that a real
    regression from ~2% to 14% would still pass. Fixed on both axes:
    5 ROI sizes spanning the small-to-large range this detector
    actually sees in production (30/60/100/181/300 pts, the last two
    being real Find-Peaks-scale windows), and an aggregate tolerance
    grounded in a real measurement rather than picked to be lenient --
    60 draws/condition/size (900 trials total) measured 6/900 = 0.67%
    aggregate, with individual cells up to 5% (n=300 flat) from ordinary
    multiple-comparisons noise across a denser scale ladder at larger n.
    8% aggregate gives >10x headroom above the measured baseline while
    still catching an order-of-magnitude jump."""
    n_draws = 40
    sizes = (30, 60, 100, 181, 300)
    kinds = ("flat", "slope", "sigmoid")
    n_fp = 0
    n_total = 0
    for n in sizes:
        x = np.arange(0.0, n * 0.1, 0.1)[:n] + 380.0
        for seed in range(n_draws):
            for level, kind in ((6000.0, "flat"), (6000.0, "slope"), (6000.0, "sigmoid")):
                rng = np.random.default_rng(
                    900_000 + n * 10_000 + seed * 3
                    + {"flat": 0, "slope": 1, "sigmoid": 2}[kind])
                if kind == "flat":
                    base = np.full(n, level)
                elif kind == "slope":
                    base = level * (1.0 + 1.5 * np.arange(n) / n)
                else:
                    base = level * (1.0 + 3.0 / (1.0 + np.exp(
                        -(np.arange(n) - n * 0.7) / (n * 0.08))))
                y = rng.poisson(base).astype(float)
                feats = cwt_ridge_features(x, y)
                n_total += 1
                if any(f.prom_z >= CWT_PROM_Z_MIN for f in feats):
                    n_fp += 1
    fp_rate = n_fp / n_total
    assert fp_rate <= 0.08, (
        f"false-positive rate at the frozen gate jumped to {fp_rate:.2%} "
        f"across {len(sizes)} ROI sizes on featureless/sloped data -- the "
        "wider ceiling is letting the detector latch onto background "
        "curvature (measured baseline ~0.67% aggregate, up to ~5% in the "
        "noisiest single cell; this bound gives >10x headroom above that, "
        "not zero-tolerance, since some baseline false-positive rate is "
        "expected and already tolerated by design)"
    )


# ── (ii) seed fwhm_init clip: characterization, not the fit bound ─────────

def _dominant_seed(center, fwhm=1.2, amp=40000.0, frac=1.0, snr=200.0):
    return {"role": "preseed_dominant_0", "center_be": center,
            "fwhm_init": fwhm, "amplitude_net": amp,
            "fraction_of_max": frac, "local_snr": snr}


def test_seed_fwhm_init_not_clipped_to_ordinary_ceiling_when_clip_hi_is_none():
    """(ii): when build_candidate_pool is called the way engine.py calls
    it after this fix (fwhm_clip upper bound = None, signaling
    "derive it"), a curvature seed whose ridge-measured width genuinely
    exceeds the old FWHM_MAX_ORDINARY_EV/PROPOSAL_FWHM_MAX (2.0 eV) must
    NOT be silently clipped down to that chemistry-derived ceiling --
    the same "characterization must not be capped by chemistry"
    principle as (i), one layer downstream."""
    x = np.arange(180.0, 220.0, 0.05)   # wide ROI: 800 pts, ceiling >> 2.0
    dom_c, dom_f = 191.0, 1.2
    sh_c, sh_f = dom_c - 6.0, 4.5        # genuinely broad, well-separated shoulder
    sig = (_pv(x, 40000.0, dom_c, dom_f, ETA)
           + _pv(x, 9000.0, sh_c, sh_f, ETA))
    rng = np.random.default_rng(7)
    y = rng.poisson(np.maximum(sig + 300.0, 0.0)).astype(float)

    pool = build_candidate_pool(
        x, y, np.zeros_like(x),
        all_windows=[], labeled_windows={},
        dominant_seeds=[_dominant_seed(dom_c, fwhm=dom_f)],
        noise_floor=1.0, min_fraction_of_max=0.05, amplitude_snr=5.0,
        coincidence_ev=0.5, max_total_seeds=2, smooth_points=5,
        fwhm_clip=(0.5, None),
    )
    assert pool.curvature_seeds, "fixture assumption: the shoulder must be seeded"
    seed = pool.curvature_seeds[0]
    assert seed.fwhm_init > 2.0, (
        "a genuinely broad ridge's fwhm_init must not be clipped down to "
        f"the old 2.0 eV ordinary ceiling -- got {seed.fwhm_init:.2f}"
    )


def test_seed_fwhm_init_explicit_clip_still_honored_backward_compat():
    """Existing synthetic tests (and any future caller) that explicitly
    pass a fixed fwhm_clip upper bound must see UNCHANGED behavior --
    only the DEFAULT/None-signaled path derives from the ROI."""
    x = np.arange(180.0, 220.0, 0.05)
    dom_c, dom_f = 191.0, 1.2
    sh_c, sh_f = dom_c - 6.0, 4.5
    sig = (_pv(x, 40000.0, dom_c, dom_f, ETA)
           + _pv(x, 9000.0, sh_c, sh_f, ETA))
    rng = np.random.default_rng(7)
    y = rng.poisson(np.maximum(sig + 300.0, 0.0)).astype(float)

    pool = build_candidate_pool(
        x, y, np.zeros_like(x),
        all_windows=[], labeled_windows={},
        dominant_seeds=[_dominant_seed(dom_c, fwhm=dom_f)],
        noise_floor=1.0, min_fraction_of_max=0.05, amplitude_snr=5.0,
        coincidence_ev=0.5, max_total_seeds=2, smooth_points=5,
        fwhm_clip=(0.5, 2.0),
    )
    assert pool.curvature_seeds, "fixture assumption: the shoulder must be seeded"
    seed = pool.curvature_seeds[0]
    assert seed.fwhm_init <= 2.0, (
        "an EXPLICIT fwhm_clip upper bound must still be honored exactly "
        "as before -- backward compatibility for existing callers"
    )
