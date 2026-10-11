"""Endpoint averaging outside the field's own 1-50 is REFUSED, never clamped (owner 2026-10-11).
The routes read max(1, int(x)): 0 or -5 fitted at 1, and 1e21 at the window's quarter while the
page's helpers read it as 1 (logged by the fit-recording unit, Codex round 3). One rule now,
fitting.check_endpoint_avg, for /api/fit, /api/fit/start, /api/background, run_fit,
compute_background_only and Find Peaks; a valid value computes exactly as before."""
import io

import numpy as np
import pytest

import fitting
from app import create_app
import test_scattered_starts as SS

BAD = [0, -1, -5, 51, 1000, 1e21, 2e21, 2.5, float("nan"), float("inf"), "3", "1e21", True, False, None, [3]]
GOOD = [(1, 1), (3, 3), (50, 50), (3.0, 3), (np.int64(7), 7), (np.float64(12.0), 12)]
WORDS = "endpoint_avg must be a whole number from 1 to 50"


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload(client, x, y):
    csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(x, y))
    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
    assert r.status_code == 200
    return r.get_json()["session_id"]


@pytest.mark.parametrize("bad", BAD, ids=repr)
def test_check_endpoint_avg_refuses_everything_outside_1_to_50(bad):
    with pytest.raises(ValueError, match=WORDS):
        fitting.check_endpoint_avg(bad)


@pytest.mark.parametrize("good,want", GOOD, ids=repr)
def test_check_endpoint_avg_accepts_whole_numbers_1_to_50(good, want):
    assert fitting.check_endpoint_avg(good) == want and type(fitting.check_endpoint_avg(good)) is int


def test_the_bound_is_the_page_fields_max_and_find_peaks_shares_the_rule():
    from autofit.methods.base import ENDPOINT_AVG_MAX, pop_endpoint_avg
    assert fitting.ENDPOINT_AVG_MAX == ENDPOINT_AVG_MAX == 50
    with pytest.raises(ValueError, match=WORDS):
        pop_endpoint_avg({"endpoint_avg": 0})


@pytest.mark.parametrize("bad", [0, -5, 51, 1e21, 2.5, "3", True, None], ids=repr)
@pytest.mark.parametrize("route", ["/api/fit", "/api/fit/start"])
def test_the_fit_routes_refuse_and_never_clamp(client, route, bad):
    x, y, specs = SS._well_posed()
    sid = _upload(client, x, y)
    r = client.post(route, json={"session_id": sid, "background": {"method": "shirley", "endpoint_avg": bad},
                                 "peaks": specs, "fit_method": "leastsq", "n_perturb": 0})
    assert r.status_code == 400 and WORDS in r.get_json()["error"], (r.status_code, r.get_json())


@pytest.mark.parametrize("bad", [0, -5, 51, 1e21, "3"], ids=repr)
def test_the_background_route_refuses_and_never_clamps(client, bad):
    x, y, _ = SS._well_posed()
    sid = _upload(client, x, y)
    r = client.post("/api/background", json={"session_id": sid, "method": "shirley", "endpoint_avg": bad})
    assert r.status_code == 400 and WORDS in r.get_json()["error"]


def test_run_fit_and_the_background_alone_refuse_too():
    x, y, specs = SS._well_posed()
    for bad in (0, 51, 1e21):
        with pytest.raises(ValueError, match=WORDS):
            fitting.run_fit(x, y, specs, background_method="shirley", endpoint_avg=bad, n_perturb=0)
        with pytest.raises(ValueError, match=WORDS):
            fitting.compute_background_only(x, y, method="shirley", endpoint_avg=bad)


def test_a_valid_or_absent_value_fits_exactly_as_before(client):
    # absent means 1, as it always did; 1 and 50 fit; the same request fits identically
    x, y, specs = SS._well_posed()
    sid = _upload(client, x, y)
    body = {"session_id": sid, "peaks": specs, "fit_method": "leastsq", "n_perturb": 0}
    absent = client.post("/api/fit", json={**body, "background": {"method": "shirley"}}).get_json()
    one = client.post("/api/fit", json={**body, "background": {"method": "shirley", "endpoint_avg": 1}}).get_json()
    assert absent["success"] and absent["background_y"] == one["background_y"] and absent["fitted_y"] == one["fitted_y"]
    for k in (3, 50, 3.0):
        r = client.post("/api/fit", json={**body, "background": {"method": "shirley", "endpoint_avg": k}})
        assert r.status_code == 200 and r.get_json()["success"], k
        bg = fitting.compute_background(np.asarray(x), np.asarray(y), "shirley", n_avg=int(k))
        assert np.array_equal(np.asarray(r.get_json()["background_y"]), bg), k


# ── Codex averaging round 1: every other reader refuses too ───────────────────────────────

@pytest.mark.parametrize("bad", [0, 51, 1e21], ids=repr)
def test_find_peaks_engine_and_parity_refuse(bad):
    import sys
    sys.path.insert(0, "tests/autofit")
    from test_endpoint_avg_wiring import GRAPHITE, _synthetic_c1s
    from autofit.engine import _compute_background, fit_candidate
    from autofit.grammar import resolve
    from autofit.methods.base import poisson_like_weights
    from autofit.grammar import BackgroundType
    from autofit.parity import background_like_run_fit
    x, y = _synthetic_c1s()
    with pytest.raises(ValueError, match=WORDS):
        fit_candidate(x, y, poisson_like_weights(y), resolve([GRAPHITE], "C 1s").candidates[0], endpoint_avg=bad)
    with pytest.raises(ValueError, match=WORDS):
        _compute_background(x, y, BackgroundType.SHIRLEY, endpoint_avg=bad)
    with pytest.raises(ValueError, match=WORDS):
        background_like_run_fit(x, y, "shirley", 0, len(x), endpoint_avg=bad)


def test_the_async_analyze_route_refuses_before_a_job_exists(client):
    x, y, _ = SS._well_posed()
    sid = _upload(client, x, y)
    for route in ("/api/analyze", "/api/analyze/start"):
        r = client.post(route, json={"session_id": sid, "material_class": "conductor", "method": "ic_model_comparison", "regions": ["C 1s"], "options": {"endpoint_avg": 51}})
        assert r.status_code == 400 and WORDS in r.get_json()["error"], (route, r.status_code, r.get_json())
        assert "job_id" not in (r.get_json() or {})


@pytest.mark.parametrize("saved,want", [("3", 3), ("3.0", 3), (" 7 ", 7), ("+3", 3), ("50", 50), (3, 3), (None, 1)])
def test_the_saved_project_twin_reads_a_valid_value_as_the_page_does(saved, want):
    from autofit.reference import ReferenceFit
    rf = ReferenceFit.__new__(ReferenceFit)
    rf.ui = {} if saved is None else {"endpointAvg": saved}
    assert rf.endpoint_avg == want


@pytest.mark.parametrize("saved", ["0", "-1", "51", "1e21", "1e1", "", "2.5", "abc"])
def test_the_saved_project_twin_refuses_what_the_page_refuses(saved):
    from autofit.reference import ReferenceFit
    rf = ReferenceFit.__new__(ReferenceFit)
    rf.ui = {"endpointAvg": saved}
    with pytest.raises(ValueError, match="endpoint averaging must be a whole number from 1 to 50"):
        rf.endpoint_avg
