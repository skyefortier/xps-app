"""Every background satisfies its defining statement or reports failure
(owner, 2026-10-01; background math F10, F11, F12): fitting.background_certificate
checks a result against its statement, compute_background raises
BackgroundNotConverged on a failure, run_fit fits against no such background, and
/api/fit, /api/fit/start and /api/background answer 422 with the plain message.
Endpoint averaging sets the edge levels only and every iteration stops on
BG_REL_TOL of the span (F1, F5) — pinned in test_background_defining_statements.py."""
import io
import json
import os
import sys
import time

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import fitting  # noqa: E402
from app import create_app  # noqa: E402
from test_background_defining_statements import SPECTRA, _K  # noqa: E402

ITERATIVE = ("shirley", "smart", "smart_exp", "shirley_linear")
ALL = ITERATIVE + ("tougaard",)


def test_every_committed_spectrum_is_certified_under_every_method():
    for name, x, y, ep in SPECTRA:
        for m in ALL:
            fitting.compute_background(x, y, m, n_avg=ep)          # raises on a failure


@pytest.mark.parametrize("I,methods", [
    ([2.0, 3.0, 10.0, 13.0], ("shirley", "smart", "smart_exp")),
    ([11.0, 14.0, 1.0, 33.0, 40.0], ("shirley", "smart", "smart_exp")),
    ([20.0, 44.0, 34.0, 41.0, 47.0], ("shirley_linear",)),
])
def test_a_cycling_iteration_is_not_converged(I, methods):
    # findings F12: the iteration alternates between two curves and returns a non-solution
    E = np.arange(float(len(I)))
    for m in methods:
        with pytest.raises(fitting.BackgroundNotConverged, match="misses the .* relation by"):
            fitting.compute_background(E, np.array(I), m)


def test_no_net_signal_is_not_converged():
    # findings F10: the data lie below the line between the edge levels — no net signal, the
    # Shirley relation is undefined; the line (shirley) or the data (smart methods) solve nothing
    E, I = np.array([0.0, 1, 2, 3, 4]), np.array([10.0, 5, 5, 17, 20])
    for m in ("shirley", "smart", "smart_exp"):
        with pytest.raises(fitting.BackgroundNotConverged, match="no net signal"):
            fitting.compute_background(E, I, m)


def test_tougaard_undetermined_and_unsolvable_are_not_converged():
    # findings F11
    r = 2 * (1644 / 1647) ** 2
    with pytest.raises(fitting.BackgroundNotConverged, match="does not fix the background's amplitude"):
        fitting.compute_background(np.arange(4.0), np.array([10.0, 11.0, 10.0 - r, 10.0]), "tougaard")
    with pytest.raises(fitting.BackgroundNotConverged, match="no amplitude can meet"):
        fitting.compute_background(np.array([0.0, 1.0]), np.array([10.0, 20.0]), "tougaard")
    # equal levels and an all-zero loss vector: the flat C0 IS the answer
    assert np.array_equal(fitting.compute_background(np.array([0.0, 1.0]), np.array([10.0, 10.0]), "tougaard"), [10.0, 10.0])


def test_shirley_linear_equal_edge_levels_are_not_converged():
    # the implementation returns L unclamped where the equation gives min(L, I)
    with pytest.raises(fitting.BackgroundNotConverged):
        fitting.compute_background(np.arange(5.0), np.array([10.0, 15.0, 5.0, 15.0, 10.0]), "shirley_linear")


def test_the_certificate_checks_the_statement_not_the_iteration():
    # an arbitrary curve is judged against the statement: the line is no Shirley solution here
    _, x, y, ep = SPECTRA[0]
    line = np.linspace(y[0], y[-1], len(y))
    c = fitting.background_certificate(x, y, line, "shirley", ep)
    assert c["converged"] is False and c["residual"] > fitting.BG_REL_TOL
    good = fitting.shirley_background(x, y, n_avg=ep)
    c = fitting.background_certificate(x, y, good, "shirley", ep)
    assert c["converged"] is True and c["residual"] <= fitting.BG_REL_TOL
    # explicit methods carry nothing to converge
    assert fitting.background_certificate(x, y, fitting.linear_background(x, y), "linear")["converged"] is True
    assert fitting.background_certificate(x, y, np.full(len(y), np.nan), "shirley")["converged"] is False


# ── run_fit and the routes ───────────────────────────────────────────────────

def _u_shape(n=120):
    x = np.linspace(280.0, 292.0, n)
    # convex, so every interior point lies below the line between the (unequal) edge levels;
    # a symmetric U would have equal levels, a zero step, and the flat line as its solution
    return x, 1000.0 + 40.0 * (x - 285.0) ** 2


PEAK = [{"id": "1", "shape": "pseudo_voigt_gl", "center": 286.0, "fwhm": 1.0, "amplitude": 100.0,
         "gl_ratio": 0.3, "amplitude_min": 0}]


def test_run_fit_fits_against_no_unconverged_background():
    x, y = _u_shape()
    with pytest.raises(fitting.BackgroundNotConverged, match="Shirley background not converged"):
        fitting.run_fit(x, y, PEAK, background_method="shirley")
    fitting.run_fit(x, y, PEAK, background_method="linear")         # an explicit background still fits


@pytest.fixture()
def client(tmp_path):
    a = create_app(upload_folder=str(tmp_path))
    a.config["TESTING"] = True
    with a.test_client() as c:
        yield c


def _upload(client):
    x, y = _u_shape()
    csv = "\n".join(f"{a:.4f},{b:.1f}" for a, b in zip(x, y))
    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "u.csv")})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["session_id"]


def test_the_routes_answer_422_with_the_plain_message(client):
    sid = _upload(client)
    body = {"session_id": sid, "background": {"method": "smart", "endpoint_avg": 3}, "peaks": PEAK,
            "fit_method": "leastsq", "n_perturb": 0, "n_starts": 0}
    r = client.post("/api/fit", json=body)
    assert r.status_code == 422 and "Smart (constrained Shirley) background not converged" in r.get_json()["error"]
    job = client.post("/api/fit/start", json=body)
    assert job.status_code == 202
    jid = job.get_json()["job_id"]
    for _ in range(300):
        rec = json.loads(client.get(f"/api/fit/progress/{jid}").get_data(as_text=True))
        if rec["status"] not in ("queued", "running"):
            break
        time.sleep(0.1)
    assert rec["status"] == "error" and rec["http_status"] == 422 and "not converged" in rec["error"]
    r = client.post("/api/background", json={"session_id": sid, "method": "shirley"})
    assert r.status_code == 422 and "no net signal" in r.get_json()["error"]


# ── Codex implementation round 1 ─────────────────────────────────────────────

def test_the_verdict_is_the_exact_statement_at_the_float_stops_boundary():
    # Codex impl round 1 built these at the FLOAT boundary diff == tol * span (the iteration
    # stops there). Since round 13 the certificate checks the returned curve EXACTLY, and the
    # exact residual here is a hair over the predicate: the verdict is the statement's, so they
    # are refused — the stop is the iteration's (float), the verdict governs
    for E, I in ((np.arange(4.0), np.array([0.0, 0.0, 7.326101243535137, 2.1978303730605416e-11])),
                 (np.array([0.0, 1.0, 3.0]), np.array([0.0, 31.620122043497105, 1.8972073226098264e-10]))):
        with pytest.raises(fitting.BackgroundNotConverged, match="misses the Shirley relation by 1e-10 %"):
            fitting.compute_background(E, I, "shirley")


def test_tougaard_is_the_stated_sum_on_a_near_uniform_grid():
    # the server used to evaluate a convolution with index separations on grids uniform to 1e-6
    # of the step; near cancellation that moved the background 16 % of the span and could turn the
    # high-edge sum into an exact zero. Now the stated sum, on every grid.
    import background_defining_statements as D
    for third in (0.008279338821039262, 0.007279338821039261):
        E, I = np.array([0.0, 1.0, 2.0000005, 3.0000005]), np.array([2.0, 3.0, third, 3.0])
        B = fitting.tougaard_background(E, I)                     # both have a (badly conditioned) solution
        assert np.max(np.abs(B - D.tougaard_statement(E, I, 1, "levels"))) <= 1e-9 * np.max(np.abs(B))
        # ... which the certificate refuses since round 13: so near cancellation the rounding
        # bound exceeds the predicate
        with pytest.raises(fitting.BackgroundNotConverged, match="nearly cancels"):
            fitting.compute_background(E, I, "tougaard")


def test_a_non_finite_evaluation_is_not_converged():
    E, I = np.arange(4.0), np.array([1.0, 1e308, 1e308, 3.0])
    with pytest.raises(fitting.BackgroundNotConverged):
        fitting.compute_background(E, I, "shirley")


# ── Codex implementation round 4 ─────────────────────────────────────────────

def test_a_linear_window_whose_ends_share_an_energy_but_not_an_intensity_is_not_converged():
    # no line passes through (1, 10) and (1, 30): the flat 10 used to be fitted against
    E = np.array([3.0, 2.0, 1.0, 1.0, 0.0])
    I = np.array([20.0, 25.0, 10.0, 30.0, 5.0])
    with pytest.raises(fitting.BackgroundNotConverged, match="no line passes through both"):
        fitting.run_fit(E, I, [{"id": "1", "shape": "gaussian", "center": 2.0, "fwhm": 1.0, "amplitude": 10.0,
                                 "amplitude_min": 0}], background_method="linear", bg_start_idx=2, bg_end_idx=4)
    with pytest.raises(fitting.BackgroundNotConverged, match="no line passes through both"):
        fitting.compute_background_only(np.array([1.0, 1.0]), np.array([10.0, 30.0]), method="linear")
    # equal intensities: the flat line exists
    assert np.array_equal(fitting.linear_background(np.array([1.0, 1.0]), np.array([10.0, 10.0])), [10.0, 10.0])
    # an ordinary window is unchanged, bit for bit
    x, y = np.array([3.0, 2.0, 1.0, 0.0]), np.array([20.0, 25.0, 10.0, 5.0])
    assert np.array_equal(fitting.linear_background(x, y), y[0] + ((y[-1] - y[0]) / (x[-1] - x[0])) * (x - x[0]))


# ── Codex implementation round 5 ─────────────────────────────────────────────

LINE_WORDS = ("Linear background not converged: its two end points are at the same energy with "
              "different intensities, so no line passes through both.")
ANCHOR_WORDS = ("Manual background not converged: two anchors are at the same energy with different "
                "intensities, so no curve passes through both.")
FINITE_WORDS = ("Linear background not converged: it is not a finite number at every point "
                "(the arithmetic overflowed or an input is not finite).")
GPEAK = [{"id": "1", "shape": "gaussian", "center": 2.0, "fwhm": 1.0, "amplitude": 10.0, "amplitude_min": 0}]


def test_an_explicit_background_must_exist_server():
    # the page's words are pinned to these in tests/js/background_not_converged.test.js
    with pytest.raises(fitting.BackgroundNotConverged) as e:
        fitting.linear_background(np.array([1.0, 1.0]), np.array([10.0, 30.0]))
    assert str(e.value) == LINE_WORDS
    # conflicting manual anchors: no curve through both
    E, I = np.array([0.0, 1, 2, 3, 4, 5]), np.array([10.0, 12, 40, 30, 22, 20])
    with pytest.raises(fitting.BackgroundNotConverged) as e:
        fitting.run_fit(E, I, GPEAK, background_method="manual", manual_bg=[[0, 0], [2, 1], [2, 20], [5, 0]])
    assert str(e.value) == ANCHOR_WORDS
    fitting.run_fit(E, I, GPEAK, background_method="manual", manual_bg=[[0, 0], [2, 1], [2, 1], [5, 0]])  # agreeing duplicates exist
    # finite inputs that used to overflow are evaluated exactly since round 11 (their true line);
    # only an EXTRAPOLATION past the largest double (a narrow window's line across the ROI) is not finite
    assert np.array_equal(fitting.compute_background_only(np.array([0.0, 1e-309]), np.array([0.0, 1.0]), method="linear")["background"], [0.0, 1.0])
    assert np.array_equal(fitting.compute_background_only(np.array([0.0, 1, 2]), np.array([1e308, 1, -1e308]), method="linear")["background"], [1e308, 0.0, -1e308])
    with pytest.raises(fitting.BackgroundNotConverged) as e:
        fitting.run_fit(np.array([0.0, 1, 2, 3]), np.array([-1.7e308, 1.7e308, 0, 0]), GPEAK, background_method="linear",
                        bg_start_idx=0, bg_end_idx=2)
    assert str(e.value) == FINITE_WORDS


def test_the_parity_reference_follows_run_fits_linear_rule():
    from autofit.parity import background_like_run_fit
    E, I = np.array([3.0, 2.0, 1.0, 1.0, 0.0]), np.array([20.0, 25.0, 10.0, 30.0, 5.0])
    with pytest.raises(fitting.BackgroundNotConverged, match="no line passes through both"):
        background_like_run_fit(E, I, "linear", 2, 4)


def test_an_anchor_that_is_not_a_pair_of_finite_numbers_is_not_converged():
    E, I = np.array([0.0, 1, 2, 3, 4, 5]), np.array([10.0, 12, 40, 30, 22, 20])
    for bad in ([[0, 0], [float("nan"), 1], [5, 0]], [[0, 0], [2, float("inf")], [5, 0]],
                [[0, 0], ["2", 1], [5, 0]], [[0, 0], [2, None], [5, 0]], [[0, 0], [True, 1], [5, 0]], [[0, 0], [2], [5, 0]]):
        with pytest.raises(fitting.BackgroundNotConverged) as e:
            fitting.run_fit(E, I, GPEAK, background_method="manual", manual_bg=bad)
        assert str(e.value) == "Manual background not converged: an anchor is not a pair of finite numbers."


# ── Codex implementation round 6 ─────────────────────────────────────────────

def test_an_unsorted_window_is_not_converged_for_the_integral_methods():
    # the integral relations run along the energy axis: an unsorted window integrated the
    # array order, and its own certificate agreed (Shirley [10, 30, 20, 20] above both levels)
    for E, I in (([0.0, 2, 1, 3], [10.0, 40, 12, 20]), ([3.0, 1, 2, 0], [20.0, 12, 40, 10])):
        for m in ("shirley", "smart", "smart_exp", "shirley_linear", "tougaard"):
            with pytest.raises(fitting.BackgroundNotConverged, match="energies in the window are not in order"):
                fitting.compute_background(np.array(E), np.array(I), m)
        with pytest.raises(fitting.BackgroundNotConverged, match="not in order"):
            fitting.run_fit(np.array(E), np.array(I), GPEAK, background_method="shirley")
    # repeated energies in order are fine
    fitting.compute_background(np.array([0.0, 1, 1, 2, 3, 4, 5]), np.array([10.0, 12, 14, 40, 30, 22, 20]), "shirley")


def test_an_overflowing_certificate_does_not_certify():
    E, I = np.arange(5.0), np.array([1e308, -1e308, 1e308, -1e308, 1e308])
    with pytest.raises(fitting.BackgroundNotConverged, match="not converged"):     # exactly, since round 13
        fitting.compute_background(E, I, "shirley_linear")


def test_manual_without_anchors_is_the_line_and_every_anchor_is_checked():
    E, I = np.array([0.0, 1, 2, 3, 4, 5]), np.array([10.0, 12, 40, 30, 22, 20])
    line = fitting.linear_background(E, I)
    for absent in (None, []):
        r = fitting.run_fit(E, I, GPEAK, background_method="manual", manual_bg=absent, n_perturb=0)
        assert np.array_equal(np.asarray(r["background_y"]), line)
    assert np.array_equal(fitting.compute_background_only(E, I, method="manual")["background"], line)
    for lone in ([[float("nan"), 1]], [[2, None]], [[True, 1]], [None, [5, 0]], ["ab", [5, 0]]):
        with pytest.raises(fitting.BackgroundNotConverged, match="an anchor is not a pair of finite numbers"):
            fitting.run_fit(E, I, GPEAK, background_method="manual", manual_bg=lone)


# ── Codex implementation round 7 ─────────────────────────────────────────────

def test_an_integral_background_on_an_unsorted_region_is_not_converged():
    # a sorted window inside an unsorted region: the flat hold beyond the window is by array
    # position, so the high-BE side took the low-edge level
    from autofit.parity import background_like_run_fit
    E, I = np.array([5.0, 0, 1, 2, 3, -1]), np.array([20.0, 10, 10, 40, 20, 10])
    for m in ("shirley", "smart", "smart_exp", "shirley_linear", "tougaard"):
        with pytest.raises(fitting.BackgroundNotConverged, match="energies in the fitted region are not in order"):
            fitting.run_fit(E, I, GPEAK, background_method=m, bg_start_idx=2, bg_end_idx=5)
        with pytest.raises(fitting.BackgroundNotConverged, match="fitted region are not in order"):
            background_like_run_fit(E, I, m, 2, 5)
    fitting.run_fit(E, I, GPEAK, background_method="linear", bg_start_idx=2, bg_end_idx=5, n_perturb=0)  # affine in energy


def test_the_residual_is_rounded_half_up_on_the_exact_value():
    # one definition the page computes exactly (toExponential); Python's %.3g rounds ties to even
    assert [fitting._fmt3(v) for v in (12.25, 1.125, 0.125, 1.234e-5, 999.6, 1234.0, 0.0001, 100.0)] == \
        ["12.3", "1.13", "0.125", "1.23e-05", "1e+03", "1.23e+03", "0.0001", "100"]


def test_an_empty_linear_or_manual_window_is_an_empty_curve_not_a_500(client):
    sid = _upload(client)
    for m in ("linear", "manual"):
        r = client.post("/api/background", json={"session_id": sid, "method": m, "start_idx": 1, "end_idx": 1})
        assert r.status_code == 200 and r.get_json()["background"] == [], (m, r.status_code, r.get_json())


# ── Codex implementation round 9 ─────────────────────────────────────────────

def test_manual_is_the_exact_piecewise_affine_curve_for_far_anchors():
    # rounds 9-10: np.interp overflowed (a 2e308 gap: slope 0, a finite, wrong 0) and
    # cancelled (-1e20 eV anchors against 280 eV data: 0 where the line is 80); the curve is
    # now evaluated exactly and rounded once, and fits against the line the anchors define
    E = np.arange(280.0, 291.0)
    I = np.array([50.0, 50, 60, 100, 500, 100, 60, 50, 50, 50, 50])
    for anchors, want in (([[-1e308, 0], [1e308, 100]], np.full(11, 50.0)),
                          ([[-1e20, -1e20], [300, 100]], 80.0 + np.arange(11)),
                          ([[-1e20, 1e20], [300, 1]], 21.0 - np.arange(11))):
        assert np.array_equal(fitting.manual_anchor_background(E, anchors), want), anchors
    r = fitting.run_fit(E, I, GPEAK, background_method="manual", manual_bg=[[-1e308, 0], [1e308, 100]], n_perturb=0)
    assert np.array_equal(np.asarray(r["background_y"]), np.full(11, 50.0))
    # ordinary anchors: within an ulp of np.interp (correctly rounded, where np.interp is not always)
    x = np.linspace(280, 296, 40)
    A = [[281.3, 120.0], [285.0, 400.5], [293.2, 210.25]]
    ref = np.interp(x, [a[0] for a in A], [a[1] for a in A])
    assert np.all(np.abs(fitting.manual_anchor_background(x, A) - ref) <= 2 * np.spacing(np.abs(ref)))


def test_the_parity_reference_reads_manual_without_anchors_as_run_fit_does():
    from autofit.parity import background_like_run_fit
    E, I = np.array([0.0, 1, 2, 3, 4, 5]), np.array([10.0, 12, 40, 30, 22, 20])
    assert np.array_equal(background_like_run_fit(E, I, "manual", 0, 6), fitting.linear_background(E, I))



# ── Codex implementation round 11 ────────────────────────────────────────────

def test_linear_is_the_exact_line_beside_a_huge_end_point():
    # y0 + slope (x - x0) cancelled to a finite, wrong 0 beside a 1e20 end point
    E = np.array([1e20, 290, 289, 288, 287, 286, 285, 284, 283, 282, 281, 280.0])
    I = np.array([1e20, 70, 70, 80, 120, 500, 120, 80, 70, 70, 60, 50.0])
    assert np.array_equal(fitting.linear_background(E, I), [1e20, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50])
    E = np.array([-1e20] + list(range(280, 291)) + [300.0])
    I = np.array([1e20, 50, 50, 60, 100, 500, 100, 60, 50, 50, 50, 50, 1.0])
    r = fitting.run_fit(E, I, GPEAK, background_method="manual", manual_bg=[], n_perturb=0)
    assert np.array_equal(np.asarray(r["background_y"]), [1e20] + list(range(21, 10, -1)) + [1.0])
    # ordinary windows: within an ulp of the floating-point formula
    x = np.linspace(280, 296, 50)
    y = 100 + 30 * np.sin(x)
    ref = y[0] + ((y[-1] - y[0]) / (x[-1] - x[0])) * (x - x[0])
    assert np.all(np.abs(fitting.linear_background(x, y) - ref) <= 4 * np.spacing(np.abs(ref)))


# ── Codex implementation round 12 ────────────────────────────────────────────

def _tougaard_exact(E, I):
    """The stated Tougaard relation in exact rationals (descending working grid,
    np.gradient's weights, averaging 1): c0 + (a_high - c0) L(i) / L(0)."""
    from fractions import Fraction as F
    x, y = list(map(F, E)), list(map(F, I))
    flipped = x[0] < x[-1]
    if flipped:
        x, y = x[::-1], y[::-1]
    n = len(x)
    w = [abs(x[1] - x[0])] + [abs(x[i + 1] - x[i - 1]) / 2 for i in range(1, n - 1)] + [abs(x[-1] - x[-2])]
    c0, a_high = y[-1], y[0]
    K = lambda T: F(2866) * T / (F(1643) + T * T) ** 2  # noqa: E731
    L = [sum(K(abs(x[j] - x[i])) * (y[j] - c0) * w[j] for j in range(i, n)) for i in range(n)]
    out = [c0 + (a_high - c0) * L[i] / L[0] for i in range(n)]
    return out[::-1] if flipped else out


def test_tougaard_whose_kernel_arithmetic_overflows_is_refused_and_large_data_meet_the_predicate():
    # energies near 1e80: u*u overflows and real terms became silent zeros (99.99999 % of the span)
    with pytest.raises(fitting.BackgroundNotConverged, match="not finite"):
        fitting.compute_background(np.array([0, 1, 9.999999999999999e79, 1e80]), np.array([0, 1e200, 1e145, 1e200]), "tougaard")
    # intensities near 1e20: the anchoring rounds at the data's own scale — the curve meets the
    # stated relation within the certificate's predicate (BG_REL_TOL of the span), as every
    # certified background does; computed exactly it would be 50 at the high edge, it is 16384
    for E, I in (([280.0, 285, 290], [1e20, 2e20, 50]), ([290.0, 285, 280], [50, 2e20, 1e20])):
        bg = fitting.compute_background(np.array(E), np.array(I), "tougaard")
        exact = _tougaard_exact(E, I)
        span = max(I) - min(I)
        assert max(abs(float(b - e)) for b, e in zip(map(float, bg), exact)) <= fitting.BG_REL_TOL * span


# ── Codex implementation round 13 ────────────────────────────────────────────

def test_the_certificate_claims_only_what_it_verified():
    # Tougaard: a high-edge sum that nearly cancels amplified rounding 280 000-fold past the
    # predicate on four ordinary points — refused by the rigorous rounding bound, both orders
    for E, I in (([280.0, 281, 282, 283], [200, 300, 0.73, 300]), ([283.0, 282, 281, 280], [300, 0.73, 300, 200])):
        with pytest.raises(fitting.BackgroundNotConverged, match="nearly cancels"):
            fitting.compute_background(np.array(E), np.array(I), "tougaard")
    # Shirley family on 1e12 +- 8 counts: the float check rounded a residual of 6.6e-7 to 0 against
    # a predicate of 8e-12 — the exact check refuses, both orders, every Shirley-family method
    I = [1e12, 1e12 + 4, 1e12 + 8, 1e12 + 2]
    for E, Iv in ((np.arange(4.0), I), (np.arange(4.0)[::-1], I[::-1])):
        for m in ("shirley", "smart", "smart_exp", "shirley_linear"):
            with pytest.raises(fitting.BackgroundNotConverged, match="misses the .* relation by"):
                fitting.compute_background(np.array(E), np.array(Iv), m)
    # run B2's cases, the same two classes: another near-cancelling Tougaard (0.6 % of the span
    # off), and a Shirley-family window at 1e-200 whose arithmetic underflowed (25 % off) while
    # the float check repeated it — both refused, both orders, every method
    for E, I in (([280.0, 281, 282, 283], [2, 3, 0.0072794, 3]),):
        for o in (1, -1):
            with pytest.raises(fitting.BackgroundNotConverged, match="nearly cancels"):
                fitting.compute_background(np.array(E[::o]), np.array(I[::o]), "tougaard")
    tiny = [1e-200, 5e-200, 4e-200, 2e-200]
    for o in (1, -1):
        for m in ("shirley", "smart", "smart_exp", "shirley_linear"):
            with pytest.raises(fitting.BackgroundNotConverged, match="misses the .* relation by"):
                fitting.compute_background(np.arange(280.0, 284.0)[::o], np.array(tiny[::o]), m)
    # the committed data keep every verdict (scripts/bg_math_exact_certificate_margin.py: exact
    # residual <= 0.993 of the predicate on all 1 212 cases); the rounding bound is far inside it
    x = np.linspace(280, 295, 301)
    y = 300 + 6000 * np.exp(-((x - 284.5) / 0.6) ** 2) + 400 / (1 + np.exp(-(x - 284.5) / 0.3))
    assert fitting._tougaard_rounding_bound(x, y) < 0.05 * fitting.BG_REL_TOL * (y.max() - y.min())


# ── Codex implementation round 14 ────────────────────────────────────────────

def test_the_tougaard_bound_holds_at_any_scale_and_the_zero_loss_branch_is_exact():
    # (A, B) the bound's own products underflowed on 1e-110-count data and dropped the error it
    # bounds: Tougaard now computes, and the bound evaluates, in a power-of-two-normalised frame
    for E, I in (([280.0, 281, 282, 283], [2e-118, 3e-118, 1.15e-120, 3e-118]),
                 ([280.0, 281, 282, 283], [2e-110, 3e-110, 1.3e-112, 3e-110])):
        for o in (1, -1):
            with pytest.raises(fitting.BackgroundNotConverged, match="nearly cancels"):
                fitting.compute_background(np.array(E[::o]), np.array(I[::o]), "tougaard")
    # ... and on ordinary data the normalisation is exact: the same bits as unnormalised
    x = np.linspace(280, 295, 301)
    y = 300 + 6000 * np.exp(-((x - 284.5) / 0.6) ** 2) + 400 / (1 + np.exp(-(x - 284.5) / 0.3))
    bg, a_high, c0, flipped = fitting._tougaard_loss(x, y, 3)
    out = c0 + bg * ((a_high - c0) / bg[0])
    assert np.array_equal(fitting.tougaard_background(x, y, n_avg=3), out[::-1] if flipped else out)
    # (A, B) every loss sum zero and float edge means equal, the EXACT means unequal: no
    # amplitude meets the anchor — refused (it certified the flat C0)
    for E, I, n_avg in (([281.0, 280, 280, 280, 280, 280, 280, 280],
                         [1e12 + 2 ** -13, 1e12, 1e12 + 4, 1e12 + 8, 1e12 + 4, 1e12 + 8, 1e12, 1e12], 2),
                        (list(np.arange(280.0, 288.0)), [1, 1, 1, 1, 1, 1, 1, 1.0000000000000002], 2)):
        for o in (1, -1):
            with pytest.raises(fitting.BackgroundNotConverged, match="no amplitude can meet"):
                fitting.compute_background(np.array(E[::o]), np.array(I[::o]), "tougaard", n_avg=n_avg)
    # the bound is the bound of the computation actually performed (in the normalised frame):
    # at 1.5e-307 counts the result is certified — and it IS within the predicate of the exact
    # relation — where a bound evaluated at the data's own scale would have refused (1.1 x)
    I = [3e-307, 4.5e-307, 2.7e-307, 4.5e-307]
    bg = fitting.compute_background(np.array([280.0, 281, 282, 283]), np.array(I), "tougaard")
    exact = _tougaard_exact([280.0, 281, 282, 283], I)
    assert max(abs(float(b - e)) for b, e in zip(map(float, bg), exact)) <= fitting.BG_REL_TOL * (max(I) - min(I))
    # the flat window with exactly equal levels is still its own flat background
    assert np.array_equal(fitting.compute_background(np.arange(4.0), np.full(4, 7.0), "tougaard"), np.full(4, 7.0))



# ── Codex implementation round 15 ────────────────────────────────────────────

def test_the_tougaard_bound_is_rigorous_when_the_computed_edge_difference_is_zero():
    # (A, B) computed D = 0 while the exact edge difference is 2^-45 / 3 (A) or 2^-50 (B) and the
    # high-edge sum's uncertainty exceeds its magnitude: the first-order bound vanished
    # (7e11 / 2e13 x the predicate, certified). The bound is now rigorous (an interval for the
    # exact ratio, the exact D's own uncertainty, no truncation) and refuses
    for E, I, n_avg in (([333.0, 280.0 + 2 ** -44, 280.0] + [245.21875] * 9, [146.21875000000003, 162.78125, 75.0] + [128.0] * 9, 3),
                        ([55.4022790912908, 55.4022790912908, 32, 32, 31.999999999999996, 31.999999999999996, 24, 24],
                         [12, 12.000000000000002, 15.999999999999998, 12, 12, 0.2988604543545996, 12, 12], 2)):
        for o in (1, -1):
            with pytest.raises(fitting.BackgroundNotConverged, match="nearly cancels"):
                fitting.compute_background(np.array(E[::o], float), np.array(I[::o], float), "tougaard", n_avg=n_avg)
    # the exact D's own uncertainty is part of the bound: here the high-edge sum is well determined,
    # the computed D is 0 and the exact one 2^-53, and a far peak makes the ratio ~1e13 — the
    # returned flat curve misses the exact relation by 8.7 x the predicate; without dD the bound
    # would have been 3e-4 of it (certified)
    E = [1e6, 1e6 - 1e-3, 1e6 - 2e-3, 30, 25, 20, 15, 1, 0]
    I = [1.0, 1.0, 1.0, 400.0, 1000.0, 400.0, 1.0, 1.0, 1.0 + 2 ** -52]
    for o in (1, -1):
        with pytest.raises(fitting.BackgroundNotConverged, match="nearly cancels"):
            fitting.compute_background(np.array(E[::o]), np.array(I[::o]), "tougaard", n_avg=2)
    # (B) scaling back rounded the whole curve to zero (exempt from the subnormal guard): the
    # rescale must round-trip, so a value that lost bits even to zero is refused
    eta = 2.0 ** -1074
    I = [eta * v for v in (1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0)]
    for o in (1, -1):
        with pytest.raises(fitting.BackgroundNotConverged, match="not finite"):
            fitting.compute_background(np.arange(11.0, -1.0, -1.0)[::o], np.array(I[::o]), "tougaard", n_avg=3)
