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
        with pytest.raises(fitting.BackgroundNotConverged, match="did not settle on a solution"):
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

def test_the_stop_and_the_certificate_use_one_predicate():
    # at the exact boundary diff == tol * span: the iteration stops, the certificate must accept
    for E, I in ((np.arange(4.0), np.array([0.0, 0.0, 7.326101243535137, 2.1978303730605416e-11])),
                 (np.array([0.0, 1.0, 3.0]), np.array([0.0, 31.620122043497105, 1.8972073226098264e-10]))):
        fitting.compute_background(E, I, "shirley")


def test_tougaard_is_the_stated_sum_on_a_near_uniform_grid():
    # the server used to evaluate a convolution with index separations on grids uniform to 1e-6
    # of the step; near cancellation that moved the background 16 % of the span and could turn the
    # high-edge sum into an exact zero. Now the stated sum, on every grid.
    import background_defining_statements as D
    for third in (0.008279338821039262, 0.007279338821039261):
        E, I = np.array([0.0, 1.0, 2.0000005, 3.0000005]), np.array([2.0, 3.0, third, 3.0])
        B = fitting.compute_background(E, I, "tougaard")          # both have a (badly conditioned) solution
        assert np.max(np.abs(B - D.tougaard_statement(E, I, 1, "levels"))) <= 1e-9 * np.max(np.abs(B))


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
