"""Async capacity is shared across application instances and worker processes."""
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import app as module
from app import create_app
from tests.test_api_analyze_progress import _BODY, _upload_doublet


def _request_setup(folder):
    app = create_app(upload_folder=str(folder))
    app.config["TESTING"] = True
    with app.test_client() as client:
        sid = _upload_doublet(client)
    return app, _BODY(sid)


def _assert_capacity_free(folder):
    leases = []
    try:
        for _ in range(2):
            lease = module._acquire_analyze_slot(str(folder))
            assert lease is not None
            leases.append(lease)
        assert module._acquire_analyze_slot(str(folder)) is None
    finally:
        for lease in leases:
            lease.close()


def test_concurrent_requests_share_two_slots_across_apps(tmp_path, monkeypatch):
    first, body = _request_setup(tmp_path)
    second = create_app(upload_folder=str(tmp_path))
    second.config["TESTING"] = True
    release = threading.Event()
    completed = threading.Event()
    mutex = threading.Lock()
    started = 0
    finished = 0
    def slow(ctx, progress_cb=None):
        nonlocal started, finished
        with mutex:
            started += 1
        try:
            assert release.wait(10)
            return object()
        finally:
            with mutex:
                finished += 1
                if finished == 2:
                    completed.set()
    monkeypatch.setattr(module, "_run_analyze_method", slow)
    monkeypatch.setattr(module, "_build_analyze_payload", lambda *args: {"success": True})
    barrier = threading.Barrier(6)
    def start(index):
        barrier.wait(timeout=5)
        with (first if index % 2 else second).test_client() as client:
            response = client.post("/api/analyze/start", json=body)
            return response.status_code, response.headers.get("Retry-After")
    try:
        with ThreadPoolExecutor(max_workers=6) as pool:
            responses = list(pool.map(start, range(6)))
        assert sorted(code for code, _ in responses) == [202, 202, 429, 429, 429, 429]
        assert all(retry == "5" for code, retry in responses if code == 429)
        assert started == 2
    finally:
        release.set()
        assert completed.wait(10)
    # Workers release after writing terminal progress; join them explicitly
    # by checking leases with a bounded retry, not an arbitrary sleep.
    _wait_capacity_free(tmp_path)


def _wait_capacity_free(folder):
    import time
    deadline = time.monotonic() + 5
    while True:
        try:
            _assert_capacity_free(folder)
            return
        except AssertionError:
            if time.monotonic() >= deadline:
                raise
            threading.Event().wait(.01)


def test_file_leases_are_process_shared_and_release_on_exit(tmp_path):
    # A fresh interpreter resembles a separate gunicorn worker. It must
    # observe our occupied slots, then have its own lease reclaimed by OS.
    leases = [module._acquire_analyze_slot(str(tmp_path)) for _ in range(2)]
    script = "from app import _acquire_analyze_slot; import sys; " \
             "lease=_acquire_analyze_slot(sys.argv[1]); print(lease is None)"
    try:
        out = subprocess.run([sys.executable, "-c", script, str(tmp_path)],
                             cwd=str(Path(module.__file__).parent),
                             text=True, capture_output=True, check=True, timeout=15)
        assert out.stdout.strip() == "True"
    finally:
        for lease in leases:
            lease.close()
    out = subprocess.run([sys.executable, "-c", script, str(tmp_path)],
                         cwd=str(Path(module.__file__).parent),
                         text=True, capture_output=True, check=True, timeout=15)
    assert out.stdout.strip() == "False"
    _assert_capacity_free(tmp_path)


@pytest.mark.parametrize("failure", ["method", "progress", "payload", "terminal_progress"])
def test_worker_failure_releases_slot(tmp_path, monkeypatch, failure):
    application, body = _request_setup(tmp_path)
    real_thread = threading.Thread
    workers = []
    def tracked_thread(*args, **kwargs):
        worker = real_thread(*args, **kwargs)
        workers.append(worker)
        return worker
    monkeypatch.setattr(module.threading, "Thread", tracked_thread)
    original_write = module._write_job_progress
    def write(job, folder, payload, **kwargs):
        if ((failure == "progress" and payload.get("phase") == "screening")
                or (failure == "terminal_progress" and payload.get("status") == "done")):
            raise OSError("simulated full progress disk")
        return original_write(job, folder, payload, **kwargs)
    def run(ctx, progress_cb=None):
        if failure == "method":
            raise module._AnalyzeError("simulated method failure", 400)
        progress_cb({"phase": "screening", "candidate_index": 1, "candidate_total": 1})
        return object()
    def build(*args):
        if failure == "payload":
            raise RuntimeError("simulated serialization failure")
        return {"success": True}
    monkeypatch.setattr(module, "_write_job_progress", write)
    monkeypatch.setattr(module, "_run_analyze_method", run)
    monkeypatch.setattr(module, "_build_analyze_payload", build)
    with application.test_client() as client:
        response = client.post("/api/analyze/start", json=body)
        assert response.status_code == 202
        for worker in workers:
            worker.join(5)
            assert not worker.is_alive()
        result = client.get("/api/analyze/progress/" + response.json["job_id"]).json
    assert result["status"] == "error"
    _assert_capacity_free(tmp_path)


@pytest.mark.parametrize("failure", ["initial_progress", "thread_start"])
def test_startup_failure_releases_slot(tmp_path, monkeypatch, failure):
    application, body = _request_setup(tmp_path)
    if failure == "initial_progress":
        monkeypatch.setattr(module.os, "replace", lambda *args: (_ for _ in ()).throw(OSError("disk full")))
    else:
        class BrokenThread:
            def __init__(self, **kwargs):
                pass
            def start(self):
                raise RuntimeError("no threads available")
        monkeypatch.setattr(module.threading, "Thread", BrokenThread)
    with application.test_client() as client:
        response = client.post("/api/analyze/start", json=body)
    assert response.status_code == 503
    _assert_capacity_free(tmp_path)


@pytest.mark.parametrize("value", [0, -1, 101, 1.5, True, [], {}])
@pytest.mark.parametrize("route", ["/api/analyze", "/api/analyze/start"])
def test_refit_cost_limits_reject_before_job_start(tmp_path, value, route):
    application, body = _request_setup(tmp_path)
    body["options"]["n_refits"] = value
    with application.test_client() as client:
        response = client.post(route, json=body)
    assert response.status_code == 400
    assert "n_refits" in response.json["error"]
    assert not list(tmp_path.glob("*.job.json"))
    _assert_capacity_free(tmp_path)


@pytest.mark.parametrize("method,option,value", [
    ("least_squares", "n_perturb", 101),
    ("sparse_map", "n_widths", 17),
    ("sparse_map", "n_lambdas", 101),
    ("sparse_map", "cd_max_iter", 5001),
])
def test_other_iteration_cost_limits(tmp_path, method, option, value):
    application, body = _request_setup(tmp_path)
    body["method"] = method
    body["options"] = {option: value}
    with application.test_client() as client:
        response = client.post("/api/analyze/start", json=body)
    assert response.status_code == 400
    assert option in response.json["error"]
    assert not list(tmp_path.glob("*.job.json"))
