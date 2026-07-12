"""
POST /api/analyze/start + GET /api/analyze/progress/<job_id> — the
async job path behind the Find Peaks progress indicator (2026-07-11,
unit 1).  STRICTLY ADDITIVE: /api/analyze itself is a thin wrapper over
the SAME shared validation + method-execution helpers now, so its
existing contract (tests/test_api_analyze.py) stays provably unchanged.

Design (documented here, mirrors PROGRESS.md): gunicorn runs with the
default SYNC worker class (see ~/Library/LaunchAgents' plist: `--workers
4`, no `-k gthread/gevent`), so an SSE connection held open for the
whole analysis would tie up an entire worker for 60-240s — exactly what
the existing synchronous /api/analyze already risks, doubled. Instead:
POST /start does the SAME fast synchronous validation /api/analyze does
(instant 400s, unchanged), then spawns a background THREAD (not a
worker-blocking connection) that runs the method and writes progress to
a small JSON file under the upload folder (per-worker in-memory state
would be invisible to a poll landing on a different gunicorn worker
process — the file is the cross-process-safe channel, same pattern as
session .npz files). GET /progress/<job_id> is a cheap poll of that
file. The indicator clears via the SAME poll on both "done" and "error"
statuses — never spins forever.
"""

import io
import time

import numpy as np
import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload_doublet(client, seed=7):
    rng = np.random.default_rng(seed)
    x = np.arange(192.0, 205.0, 0.05)

    def pv(h, c, w, eta=0.3):
        g = np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
        lo = (w / 2) ** 2 / ((x - c) ** 2 + (w / 2) ** 2)
        return h * ((1 - eta) * g + eta * lo)

    y = rng.poisson(300.0 + pv(9000.0, 197.9, 1.65)
                    + pv(4950.0, 199.5, 1.65)).astype(float)
    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    resp = client.post("/api/upload", data={
        "file": (io.BytesIO(csv.encode()), "doublet.csv")})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["session_id"]


_BODY = lambda sid: {                                          # noqa: E731
    "session_id": sid, "material_class": "insulator",
    "regions": ["Cl 2p"], "method": "ic_model_comparison",
    "roi": {"be_min": 192.0, "be_max": 205.0},
    "options": {"n_refits": 2, "enable_proposal_pass": False},
}


def _poll_until_terminal(client, job_id, timeout_sec=30.0):
    deadline = time.time() + timeout_sec
    last = None
    while time.time() < deadline:
        resp = client.get(f"/api/analyze/progress/{job_id}")
        assert resp.status_code == 200, resp.get_json()
        last = resp.get_json()
        if last["status"] in ("done", "error"):
            return last
        time.sleep(0.05)
    raise AssertionError(f"job {job_id} never reached a terminal state: {last}")


def test_start_returns_job_id_and_202(client):
    sid = _upload_doublet(client)
    resp = client.post("/api/analyze/start", json=_BODY(sid))
    assert resp.status_code == 202, resp.get_json()
    body = resp.get_json()
    assert "job_id" in body
    import uuid
    uuid.UUID(body["job_id"])  # must parse as a real UUID


def test_progress_reaches_done_with_the_same_result_as_sync(client):
    """The async path must produce the EXACT SAME result payload the
    synchronous /api/analyze produces for the identical (seeded,
    deterministic) request — proving the refactor changed nothing about
    the analysis itself."""
    sid = _upload_doublet(client)
    sync_resp = client.post("/api/analyze", json=_BODY(sid))
    assert sync_resp.status_code == 200
    sync_body = sync_resp.get_json()

    start_resp = client.post("/api/analyze/start", json=_BODY(sid))
    assert start_resp.status_code == 202
    job_id = start_resp.get_json()["job_id"]
    final = _poll_until_terminal(client, job_id)
    assert final["status"] == "done"
    assert final["result"] == sync_body


def test_progress_clears_on_success_never_spins_forever(client):
    sid = _upload_doublet(client)
    start_resp = client.post("/api/analyze/start", json=_BODY(sid))
    job_id = start_resp.get_json()["job_id"]
    final = _poll_until_terminal(client, job_id)
    assert final["status"] == "done"
    assert final["phase"] == "done"
    assert isinstance(final["elapsed_sec"], (int, float))
    assert final["elapsed_sec"] >= 0


def test_progress_shows_real_candidate_fields_while_running(client, monkeypatch):
    """Force the two-phase screen->stabilize path so the sweep takes long
    enough to observe a RUNNING poll with real phase/candidate fields —
    never a fake animation."""
    import autofit.engine as eng
    monkeypatch.setattr(eng, "SCREEN_TOP_K", 1)

    sid = _upload_doublet(client)
    start_resp = client.post("/api/analyze/start", json=_BODY(sid))
    job_id = start_resp.get_json()["job_id"]

    saw_running_with_fields = False
    deadline = time.time() + 30.0
    while time.time() < deadline:
        poll = client.get(f"/api/analyze/progress/{job_id}").get_json()
        if poll["status"] == "running" and poll.get("candidate_name"):
            assert poll["phase"] in ("starting", "screening", "stabilizing")
            if poll["phase"] in ("screening", "stabilizing"):
                assert poll["candidate_index"] >= 1
                assert poll["candidate_total"] >= poll["candidate_index"]
                saw_running_with_fields = True
        if poll["status"] in ("done", "error"):
            break
        time.sleep(0.02)
    assert saw_running_with_fields, "never observed a real in-flight progress event"


def test_progress_clears_on_error_never_spins_forever(client):
    """A malformed OPTION VALUE (discovered inside the method's run(),
    same class of error test_analyze_malformed_option_values_are_400s
    pins synchronously) must surface as a terminal 'error' status via
    the SAME poll channel — the indicator must clear, not spin."""
    sid = _upload_doublet(client)
    body = _BODY(sid)
    body["options"] = {"n_refits": []}     # TypeError inside run()
    start_resp = client.post("/api/analyze/start", json=body)
    assert start_resp.status_code == 202     # validation passed; run() will fail
    job_id = start_resp.get_json()["job_id"]
    final = _poll_until_terminal(client, job_id)
    assert final["status"] == "error"
    assert final["phase"] == "done"
    assert "invalid option" in final["error"].lower()


def test_start_validation_errors_are_still_synchronous_400s(client):
    """Cheap, request-shape validation (session/region/roi/material_class)
    stays SYNCHRONOUS on /start too — identical to /api/analyze — so a
    malformed request never even reaches the spinner."""
    resp = client.post("/api/analyze/start", json={
        "session_id": "not-a-uuid", "material_class": "insulator",
        "regions": ["Cl 2p"], "method": "ic_model_comparison"})
    assert resp.status_code == 400
    assert "job_id" not in (resp.get_json() or {})


def test_progress_unknown_job_id_404(client):
    import uuid
    resp = client.get(f"/api/analyze/progress/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_progress_invalid_job_id_format_400(client):
    """Path-traversal guard, same convention as _validate_session_id."""
    resp = client.get("/api/analyze/progress/../../etc/passwd")
    assert resp.status_code in (400, 404)  # Flask routing may itself 404
    resp2 = client.get("/api/analyze/progress/not-a-uuid-at-all")
    assert resp2.status_code == 400

