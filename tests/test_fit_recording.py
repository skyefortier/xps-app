"""Every fit response RECORDS what computed it (owner 2026-10-10; additive — no fitted number
changes, nothing here decides whether a fit is current): the method, the seed and where it came
from, the background's verdict against its defining statement, the whole certificate, and the
software (git commit, Python and the numerical libraries). The server accepts the seed over
HTTP, so a fit can be re-run with the same draws: re-running with the reported seed reproduces
it within rounding (tests/fit_equality.py)."""
import io
import platform

import lmfit
import numpy as np
import pytest
import scipy

import fitting
from app import create_app
from fit_equality import assert_same_fit
import test_scattered_starts as SS


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload(client, x, y):
    csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(x, y))   # full precision, as the page uploads
    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["session_id"]


@pytest.mark.parametrize("bg,check", [("shirley", "defining_statement"), ("smart", "defining_statement"),
                                      ("tougaard", "defining_statement"), ("linear", "explicit"), ("none", "explicit")])
def test_the_response_records_method_seed_background_certificate_and_software(bg, check):
    x, y, specs = SS._well_posed()
    r = fitting.run_fit(x, y, specs, background_method=bg, n_perturb=0, fit_kws={"method": "least_squares"})
    assert r["fit_method"] == "least_squares"
    assert r["seed_source"] == "request" and isinstance(r["random_seed"], int)
    bv = r["background_verdict"]
    assert bv["method"] == bg and bv["check"] == check and bv["converged"] is True and bv["reason"] == ""
    # the background by its EFFECT — the seed's own reading (fitting._background_effect)
    assert bv["effect"] == fitting._background_effect(bg, len(x), 0, len(x), 1, None)
    if check == "defining_statement":
        # exactly what the certificate reported on the fit's window (Tougaard's closed form is
        # certified by a rounding bound and reports no residual: null, faithfully)
        cert = {}
        fitting.compute_background(x, y, bg, n_avg=1, report=cert)
        assert bv["residual"] == (None if cert["residual"] is None else float(cert["residual"]))
        assert bg == "tougaard" or (isinstance(bv["residual"], float) and np.isfinite(bv["residual"]))
    else:
        assert bv["residual"] is None
    c = r["certificate"]
    assert set(c) == {"certified", "restarts", "moved", "optimiser_flag", "centre_moves", "largest_centre_move"}
    sw = r["software"]
    assert sw == {"git_commit": sw["git_commit"], "git_dirty": sw["git_dirty"], "python": platform.python_version(),
                  "numpy": np.__version__, "scipy": scipy.__version__, "lmfit": lmfit.__version__,
                  "seed_derivation": "xps-fit-seed-v2"}
    assert isinstance(sw["git_commit"], str) and len(sw["git_commit"]) == 40 and isinstance(sw["git_dirty"], bool)


def test_the_background_verdict_is_the_certificate_the_fit_was_made_on():
    # the recorded residual IS compute_background's certificate on the fit's window
    x, y, specs = SS._well_posed()
    r = fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=0, fit_kws={"method": "leastsq"})
    cert = {}
    fitting.compute_background(x, y, "shirley", n_avg=1, report=cert)
    assert r["background_verdict"]["residual"] == float(cert["residual"]) and cert["converged"] is True


def test_a_setting_the_background_ignores_is_not_recorded_as_acting():
    # (found by test_fit_reproducibility: endpoint_avg as SENT was recorded for "none")
    x, y, specs = SS._well_posed()
    a, b = (fitting.run_fit(x, y, specs, background_method="none", endpoint_avg=k, n_perturb=0,
                            fit_kws={"method": "leastsq"})["background_verdict"] for k in (1, 3))
    assert a == b == {"method": "none", "effect": {"method": "none"}, "check": "explicit", "converged": True,
                      "residual": None, "reason": ""}


def test_the_seed_derivation_tag_recorded_is_the_one_hashed():
    import inspect
    assert fitting.SEED_TAG == fitting.SOFTWARE["seed_derivation"] == "xps-fit-seed-v2"
    assert "SEED_TAG.encode()" in inspect.getsource(fitting._request_seed)


def test_global_methods_record_their_method_and_a_null_certificate():
    x, y, specs = SS._well_posed()
    r = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "differential_evolution"})
    assert r["fit_method"] == "differential_evolution" and r["certificate"] is None and r["background_verdict"]["converged"]


def test_a_caller_seed_is_recorded_as_such():
    x, y, specs = SS._well_posed()
    r = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=3, fit_kws={"method": "leastsq", "fit_kws": {"seed": 12345}})
    assert r["random_seed"] == 12345 and r["seed_source"] == "caller"


@pytest.mark.parametrize("bad", [True, -1, 2 ** 32, 1.5, "7", [1]])
@pytest.mark.parametrize("route", ["/api/fit", "/api/fit/start"])
def test_the_http_seed_is_validated(client, bad, route):
    x, y, specs = SS._well_posed()
    sid = _upload(client, x, y)
    r = client.post(route, json={"session_id": sid, "background": {"method": "linear"}, "peaks": specs,
                                 "fit_method": "leastsq", "n_perturb": 0, "seed": bad})
    assert r.status_code == 400 and r.get_json()["error"] == "seed must be an integer in [0, 2**32)"


@pytest.mark.parametrize("method", ["leastsq", "least_squares"])
def test_a_re_run_with_the_reported_seed_reproduces_the_fit_within_rounding(client, method):
    # the page's own request settings: perturbed restarts and scattered starts (both draw from the seed)
    x, y, specs = SS._well_posed()
    sid = _upload(client, x, y)
    body = {"session_id": sid, "background": {"method": "shirley"}, "peaks": specs, "fit_method": method,
            "n_perturb": 3, "n_starts": 3}
    a = client.post("/api/fit", json=body).get_json()
    assert a["success"] and a["seed_source"] == "request"
    b = client.post("/api/fit", json={**body, "seed": a["random_seed"]}).get_json()
    assert b["seed_source"] == "caller" and b["random_seed"] == a["random_seed"]
    assert_same_fit({**a, "seed_source": None}, {**b, "seed_source": None})
    # and the seed is really used: another one is reported back as given
    c = client.post("/api/fit", json={**body, "seed": (a["random_seed"] + 1) % 2 ** 32}).get_json()
    assert c["random_seed"] == (a["random_seed"] + 1) % 2 ** 32 and c["seed_source"] == "caller"


def test_the_job_route_records_the_same_fields(client):
    import time
    x, y, specs = SS._well_posed()
    sid = _upload(client, x, y)
    body = {"session_id": sid, "background": {"method": "shirley"}, "peaks": specs, "fit_method": "leastsq", "n_perturb": 0}
    sync = client.post("/api/fit", json=body).get_json()
    job = client.post("/api/fit/start", json=body).get_json()["job_id"]
    for _ in range(600):
        rec = client.get(f"/api/fit/progress/{job}").get_json()
        if rec["status"] in ("done", "error", "cancelled"):
            break
        time.sleep(0.1)
    assert rec["status"] == "done"
    for k in ("fit_method", "random_seed", "seed_source", "background_verdict", "certificate", "software"):
        assert rec["result"][k] == sync[k], k
