"""F3 regression tests (2026-07-17 background audit): shirley_background and
smart_background must accept n_avg directly, matching the convention already
used by smart_experimental_background / shirley_linear_background, and
autofit/engine.py's _compute_background must forward an endpoint_avg knob to
every background type it dispatches.

The original sandboxed patch that introduced this wiring shipped with no
tests at all for it -- these are net-new coverage, not a port of anything
upstream.
"""
import numpy as np
import pytest

from fitting import (
    _apply_endpoint_averaging,
    compute_background_only,
    shirley_background,
    smart_background,
    smart_experimental_background,
    tougaard_background,
)


def _noisy_endpoint_fixture():
    """A spectrum whose single first/last SAMPLE is a noise outlier relative
    to its neighborhood, so endpoint averaging visibly changes the reported
    B_low/B_high and therefore the whole background curve."""
    rng = np.random.default_rng(0)
    x = np.linspace(700.0, 740.0, 200)
    y = 4000.0 + 3000.0 * np.exp(-0.5 * ((x - 720.0) / 4.0) ** 2)
    y = y.copy()
    y[0] += 500.0    # single-point low-BE outlier
    y[-1] -= 500.0   # single-point high-BE outlier
    return x, y


def test_shirley_background_default_n_avg_matches_pre_f3_output():
    """n_avg=1 (the default) must reproduce the pre-F3 raw-endpoint
    behaviour byte-for-byte -- this wiring must change no current output."""
    x, y = _noisy_endpoint_fixture()
    assert np.array_equal(shirley_background(x, y), shirley_background(x, y, n_avg=1))


def test_shirley_background_n_avg_changes_output_on_noisy_endpoints():
    """n_avg > 1 must actually average the endpoints internally and change
    the result relative to raw endpoints, on a fixture designed so that
    difference is visible."""
    x, y = _noisy_endpoint_fixture()
    raw = shirley_background(x, y, n_avg=1)
    averaged = shirley_background(x, y, n_avg=8)
    assert not np.allclose(raw, averaged), (
        "n_avg=8 produced the same background as n_avg=1 on a fixture with "
        "a deliberate single-point endpoint outlier"
    )


def test_shirley_background_n_avg_matches_external_pre_averaging():
    """Calling shirley_background(x, y, n_avg=N) must equal the OLD calling
    convention -- shirley_background(x, _apply_endpoint_averaging(y, N)) --
    so this is a pure convenience wrapper, not a new averaging algorithm."""
    x, y = _noisy_endpoint_fixture()
    for n_avg in (1, 4, 8):
        direct = shirley_background(x, y, n_avg=n_avg)
        pre_averaged = shirley_background(x, _apply_endpoint_averaging(y, n_avg))
        assert np.array_equal(direct, pre_averaged), f"mismatch at n_avg={n_avg}"


def test_smart_background_default_n_avg_matches_pre_f3_output():
    x, y = _noisy_endpoint_fixture()
    assert np.array_equal(smart_background(x, y), smart_background(x, y, n_avg=1))


def test_smart_background_forwards_n_avg_to_shirley():
    """smart_background(x, y, n_avg=N) must equal
    minimum(shirley_background(x, y, n_avg=N), y) -- the clamp applies
    against the RAW data, not an endpoint-averaged copy, so averaging only
    ever moves the background curve, never the reported net counts."""
    x, y = _noisy_endpoint_fixture()
    for n_avg in (1, 4, 8):
        got = smart_background(x, y, n_avg=n_avg)
        expected = np.minimum(shirley_background(x, y, n_avg=n_avg), y)
        assert np.array_equal(got, expected), f"mismatch at n_avg={n_avg}"


def test_smart_background_n_avg_changes_output_on_noisy_endpoints():
    x, y = _noisy_endpoint_fixture()
    raw = smart_background(x, y, n_avg=1)
    averaged = smart_background(x, y, n_avg=8)
    assert not np.allclose(raw, averaged)


def test_apply_endpoint_averaging_still_importable_and_unchanged():
    """F3 relocates _apply_endpoint_averaging above shirley_background in
    fitting.py's source order; its behaviour must not change."""
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    out = _apply_endpoint_averaging(y, 2)
    assert np.array_equal(out, np.array([1.5, 1.5, 3.0, 4.0, 5.0, 6.0, 7.5, 7.5]))


def test_compute_background_default_endpoint_avg_matches_pre_f3_output():
    """autofit/engine.py's _compute_background(x, y, bg) with no
    endpoint_avg argument must reproduce pre-F3 output exactly, for every
    background type it dispatches -- pure wiring, no behaviour change."""
    from autofit.engine import BackgroundType, _compute_background

    x, y = _noisy_endpoint_fixture()
    for bg_type in (BackgroundType.SHIRLEY, BackgroundType.SMART,
                    BackgroundType.SMART_EXP, BackgroundType.LINEAR,
                    BackgroundType.TOUGAARD):
        no_arg = _compute_background(x, y, bg_type)
        default_arg = _compute_background(x, y, bg_type, endpoint_avg=1)
        assert np.array_equal(no_arg, default_arg), f"mismatch for {bg_type}"


@pytest.mark.parametrize("bg_type_name,direct_fn", [
    ("SHIRLEY", shirley_background),
    ("SMART", smart_background),
    ("SMART_EXP", smart_experimental_background),
    ("TOUGAARD", tougaard_background),
])
def test_compute_background_forwards_endpoint_avg(bg_type_name, direct_fn):
    """_compute_background(x, y, bg, endpoint_avg=N) must match calling the
    underlying fitting.py function directly with n_avg=N -- Find Peaks and
    manual Run Fit must agree once both pass the same endpoint_avg."""
    from autofit.engine import BackgroundType, _compute_background

    x, y = _noisy_endpoint_fixture()
    bg_type = getattr(BackgroundType, bg_type_name)
    for n_avg in (1, 4, 8):
        via_engine = _compute_background(x, y, bg_type, endpoint_avg=n_avg)
        direct = direct_fn(x, y, n_avg=n_avg)
        assert np.array_equal(via_engine, direct), (
            f"{bg_type_name} mismatch at endpoint_avg={n_avg}"
        )


def test_compute_background_linear_ignores_endpoint_avg():
    """linear_background has no endpoint-averaging concept (it already
    reads only the two edge points); endpoint_avg must be accepted without
    error and have no effect."""
    from autofit.engine import BackgroundType, _compute_background

    x, y = _noisy_endpoint_fixture()
    no_avg = _compute_background(x, y, BackgroundType.LINEAR)
    with_avg = _compute_background(x, y, BackgroundType.LINEAR, endpoint_avg=8)
    assert np.array_equal(no_avg, with_avg)


@pytest.mark.parametrize("method", ["shirley", "smart", "tougaard"])
def test_compute_background_only_matches_direct_call_with_n_avg(method):
    """The manual /api/background and /api/fit dispatch (compute_background_only,
    mirrored by run_fit and autofit/parity.py) must produce IDENTICAL output to
    calling the underlying fitting.py function directly with the same n_avg --
    the whole point of F3 is that Find Peaks (via _compute_background) and
    manual Run Fit agree once both pass the same endpoint_avg.

    This is the parity gap Codex review caught in c5a24ac: smart_background
    has a post-hoc `np.minimum(shir, y)` clamp, so pre-averaging y externally
    (the old convention, still used by compute_background_only/run_fit/
    parity.py before this fix) clamps against the AVERAGED copy, while
    passing n_avg directly (the new engine.py convention) clamps against the
    TRUE raw data -- a real, non-trivial divergence for SMART specifically
    once endpoint_avg > 1 is used (shirley/tougaard have no such post-hoc
    step and were already equivalent either way)."""
    x, y = _noisy_endpoint_fixture()
    direct_fn = {"shirley": shirley_background, "smart": smart_background,
                 "tougaard": tougaard_background}[method]
    for n_avg in (1, 4, 8):
        result = compute_background_only(x, y, method=method, endpoint_avg=n_avg)
        via_dispatch = np.array(result["background"])
        direct = direct_fn(x, y, n_avg=n_avg)
        assert np.allclose(via_dispatch, direct, rtol=1e-9), (
            f"{method} dispatch diverges from direct n_avg={n_avg} call by "
            f"{np.max(np.abs(via_dispatch - direct)):.3f}"
        )
