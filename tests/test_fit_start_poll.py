"""Unit 2 (2026-09-27): long fits via start-then-poll.

/api/fit/start validates exactly as /api/fit, runs the SAME run_fit in a
background thread on Find Peaks' job records, and the page polls
/api/fit/progress. Pinned here: a polled fit is the synchronous fit (same
body; byte-identical for Levenberg-Marquardt); every validation error is
immediate and word-for-word the same; a run_fit error becomes the same
message and status in the record; cancel (explicit, or no poll for
FIT_JOB_ABANDON_SEC) stops the fit within seconds; the heartbeat; every poll
is a short request.
"""

import io
import json
import time

import numpy as np
import pytest

import app as app_module
from app import create_app


def _gl(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


@pytest.fixture()
def client(tmp_path):
    a = create_app(upload_folder=str(tmp_path))
    a.config["TESTING"] = True
    with a.test_client() as c:
        yield c


def _upload(client, n=200, comps=((284.5, 5000, 0.9), (286.2, 1500, 1.1)), seed=3):
    rng = np.random.default_rng(seed)
    x = np.linspace(281.0, 292.0, n)
    y = rng.poisson(300 + sum(_gl(x, c, a, w) for c, a, w in comps)).astype(float)
    csv = "\n".join(f"{a:.4f},{b:.1f}" for a, b in zip(x, y))
    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["session_id"]


def _specs(comps):
    return [{"id": str(i + 1), "shape": "pseudo_voigt_gl", "center": c + 0.1, "fwhm": w * 1.1, "amplitude": a * 0.8,
             "gl_ratio": 0.3, "amplitude_min": 0} for i, (c, a, w) in enumerate(comps)]


def _body(sid, comps, method="leastsq", **extra):
    return {"session_id": sid, "background": {"method": "shirley"}, "peaks": _specs(comps),
            "fit_method": method, "n_perturb": 1, "n_starts": 0, **extra}


def _poll(client, job_id, limit=300.0):
    t0, longest = time.time(), 0.0
    while True:
        q0 = time.time()
        r = client.get(f"/api/fit/progress/{job_id}")
        longest = max(longest, time.time() - q0)
        assert r.status_code == 200
        rec = json.loads(r.get_data(as_text=True))
        if rec["status"] not in ("queued", "running"):
            return rec, longest
        assert time.time() - t0 < limit, "job did not finish"
        time.sleep(0.2)


COMPS = ((284.5, 5000, 0.9), (286.2, 1500, 1.1))


def test_a_polled_fit_is_the_synchronous_fit_byte_for_byte(client):
    sid = _upload(client)
    sync = client.post("/api/fit", json=_body(sid, COMPS))
    assert sync.status_code == 200
    start = client.post("/api/fit/start", json=_body(sid, COMPS))
    assert start.status_code == 202
    rec, longest = _poll(client, start.get_json()["job_id"])
    assert rec["status"] == "done"
    # Levenberg-Marquardt is byte-identical request to request (CLAUDE.md): same seed, same body
    assert json.dumps(rec["result"], sort_keys=True) == json.dumps(sync.get_json(), sort_keys=True)
    assert longest < 2.0, f"a poll took {longest:.2f} s"


@pytest.mark.parametrize("method", ["differential_evolution", "basinhopping", "least_squares"])
def test_the_stochastic_and_default_methods_give_the_synchronous_answer(client, method):
    sid = _upload(client)
    body = _body(sid, COMPS, method=method, n_perturb=0)
    sync = client.post("/api/fit", json=body).get_json()
    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
    res = rec["result"]
    assert res["random_seed"] == sync["random_seed"]
    assert res["success"] == sync["success"] is True
    # Trust-Region (also DE's and basinhopping's refinement) is not bit-reproducible
    # across calls (BLAS alignment, CLAUDE.md); the answer is the same fit
    assert res["statistics"]["reduced_chi_square"] == pytest.approx(sync["statistics"]["reduced_chi_square"], rel=1e-6)


@pytest.mark.parametrize("patch,status,fragment", [
    ({"n_perturb": 101}, 400, "n_perturb must be between"),
    ({"fit_method": "ampgo"}, 400, "Unknown fit_method"),
    ({"peaks": []}, 400, "'peaks' list is empty"),
    ({"session_id": "0" * 32}, 404, "not found"),
])
def test_a_bad_request_is_refused_immediately_and_identically(client, patch, status, fragment):
    sid = _upload(client)
    body = {**_body(sid, COMPS), **patch}
    a = client.post("/api/fit", json=body)
    b = client.post("/api/fit/start", json=body)
    assert a.status_code == b.status_code == status
    assert a.get_json() == b.get_json()
    assert fragment in b.get_json()["error"]


def test_a_run_fit_refusal_reaches_the_record_with_the_synchronous_message_and_status(client):
    sid = _upload(client, n=6)                                    # 8 free parameters, 6 points (unit F2)
    body = {**_body(sid, COMPS), "n_perturb": 0}
    sync = client.post("/api/fit", json=body)
    rec, _ = _poll(client, client.post("/api/fit/start", json=body).get_json()["job_id"])
    assert rec["status"] == "error"
    assert rec["http_status"] == sync.status_code == 400
    assert rec["error"] == sync.get_json()["error"]


SLOW = ((283.2, 2000, 0.8), (284.5, 5000, 0.9), (285.4, 1800, 1.0), (286.6, 1500, 1.1), (288.4, 900, 1.4))


def test_cancel_stops_a_running_fit_within_seconds(client):
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(1.0)
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] in ("queued", "running"), "the fixture must still be running when cancelled"
    t0 = time.time()
    assert client.post(f"/api/fit/cancel/{job}").status_code == 200
    rec, _ = _poll(client, job, limit=30)
    assert rec["status"] == "cancelled"
    assert time.time() - t0 < 10, f"cancel took {time.time() - t0:.1f} s"


def test_an_abandoned_job_stops_itself_when_polls_stop(client, monkeypatch):
    monkeypatch.setattr(app_module, "FIT_JOB_ABANDON_SEC", 1.5)
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(6.0)                                               # nobody polls
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] == "cancelled", rec["status"]


def test_the_heartbeat_moves_while_the_fit_runs(client):
    sid = _upload(client, n=300, comps=SLOW)
    job = client.post("/api/fit/start", json=_body(sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
    time.sleep(4.5)
    rec = json.loads(client.get(f"/api/fit/progress/{job}").get_data(as_text=True))
    assert rec["status"] in ("queued", "running")
    assert rec["heartbeat_age_sec"] is not None and rec["heartbeat_age_sec"] < 3.0
    assert rec["elapsed_sec"] >= 2.0
    client.post(f"/api/fit/cancel/{job}")
    _poll(client, job, limit=30)


def test_unknown_and_malformed_job_ids(client):
    assert client.get("/api/fit/progress/not-a-uuid").status_code == 400
    assert client.get("/api/fit/progress/00000000-0000-0000-0000-000000000000").status_code == 404
    assert client.post("/api/fit/cancel/not-a-uuid").status_code == 400


def test_a_non_finite_result_reaches_the_page_unsanitised(tmp_path):
    # the page's _readFitReply refuses NaN as a failed fit (unit F2): the job
    # record must carry it exactly as /api/fit would, never as null
    app_module._fit_job_write("11111111-1111-1111-1111-111111111111", str(tmp_path),
                              {"status": "done", "result": {"x": float("nan")}})
    text = (tmp_path / "11111111-1111-1111-1111-111111111111.job.json").read_text()
    assert "NaN" in text


def test_concurrency_is_bounded_one_fit_runs_per_process_the_rest_queue_and_admission_is_capped(client, monkeypatch):
    """Codex round 1: four sync workers used to bound concurrent fits at four;
    a thread per start would not. One fit runs per worker process; the rest
    wait "queued" (heartbeating, cancellable); beyond FIT_JOB_MAX_ADMITTED the
    start is refused at once with 503."""
    sid = _upload(client, n=300, comps=SLOW)
    body = _body(sid, SLOW, method="basinhopping", n_perturb=0)
    jobs = [client.post("/api/fit/start", json=body).get_json()["job_id"] for _ in range(3)]
    time.sleep(1.5)
    states = [json.loads(client.get(f"/api/fit/progress/{j}").get_data(as_text=True))["status"] for j in jobs]
    assert states.count("running") == 1 and states.count("queued") == 2, states
    monkeypatch.setattr(app_module, "FIT_JOB_MAX_ADMITTED", 3)
    busy = client.post("/api/fit/start", json=body)
    assert busy.status_code == 503 and "busy" in busy.get_json()["error"]
    for j in jobs:
        client.post(f"/api/fit/cancel/{j}")
    for j in jobs:
        rec, _ = _poll(client, j, limit=60)
        assert rec["status"] == "cancelled"
    # the slots are returned: a new start is admitted again
    ok = client.post("/api/fit/start", json=body)
    assert ok.status_code == 202
    client.post(f"/api/fit/cancel/{ok.get_json()['job_id']}")
    _poll(client, ok.get_json()["job_id"], limit=60)


@pytest.mark.parametrize("method", ["leastsq", "nelder", "differential_evolution"])
def test_a_cancel_observed_mid_fit_is_a_cancellation_never_a_solver_error(method):
    """Codex round 1: an aborted minimisation can surface as the solver's own
    error (AttributeError from Levenberg-Marquardt, RuntimeError from
    Nelder-Mead / DE); once cancellation was observed run_fit raises
    FitCancelled."""
    import fitting
    x = np.linspace(281.0, 292.0, 300)
    y = 300 + sum(_gl(x, c, a, w) for c, a, w in SLOW)
    cancel = lambda: True               # observed at the first check: the minimisation is aborted mid-fit
    with pytest.raises(fitting.FitCancelled):
        fitting.run_fit(x, y, _specs(SLOW), background_method="linear", n_perturb=0,
                        fit_kws={"method": method}, cancel=cancel)


@pytest.mark.parametrize("failing", ["fit-hb-", "fit-"])
def test_a_thread_that_fails_to_start_returns_its_admission_exactly_once(client, monkeypatch, failing):
    """Codex round 2: admission has exactly one owner — the route until the
    worker thread has started, the worker after."""
    real_start = app_module.threading.Thread.start

    def start(self):
        name = self.name or ""
        if name.startswith(failing) and not (failing == "fit-" and name.startswith("fit-hb-")):
            raise RuntimeError("cannot start thread")
        return real_start(self)

    import threading as _th
    # three run slots, so the faulted (fast) worker can RUN and finish while the
    # held jobs are still outstanding — the double release is then visible
    monkeypatch.setattr(app_module, "_FIT_JOB_RUN_SLOTS", _th.BoundedSemaphore(3))
    sid = _upload(client)
    # a job held OUTSTANDING (the counter is clamped at 0, so a double release
    # only shows while another admission is live)
    slow_sid = _upload(client, n=300, comps=SLOW)
    slow = [client.post("/api/fit/start", json=_body(slow_sid, SLOW, method="basinhopping", n_perturb=0)).get_json()["job_id"]
            for _ in range(2)]                     # TWO held: one running, one queued
    before = app_module._FIT_JOB_ADMITTED[0]
    assert before >= 2
    monkeypatch.setattr(app_module.threading.Thread, "start", start)
    with pytest.raises(RuntimeError):
        client.post("/api/fit/start", json=_body(sid, COMPS))
    monkeypatch.setattr(app_module.threading.Thread, "start", real_start)
    time.sleep(3.0)                                # long enough for a started (fast) worker to finish and release
    assert app_module._FIT_JOB_ADMITTED[0] == before, "released exactly once, by the route"
    for j in slow:
        client.post(f"/api/fit/cancel/{j}")
    for j in slow:
        _poll(client, j, limit=60)
    time.sleep(0.3)
    assert app_module._FIT_JOB_ADMITTED[0] == before - 2, "and the held jobs released their own, once each"
