"""API wiring for the opt-in "fit the entire window" option (2026-07-13,
Find Peaks UI improvements round 3, unit 1). The engine-level behavior
(default clamps to the region's literature window; checked widens the
outer envelope for curated multi-component models / the full ROI for
detection slots) is proven directly against ``fit_candidate`` in
tests/autofit/test_fit_full_window_option.py — this file only confirms
the option round-trips end to end through the HTTP request path without
a validation error, and that the advertised default is False (today's
behavior unchanged unless a caller opts in).
"""

import io

import numpy as np
import pytest

from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload_c1s_like(client, seed=11):
    rng = np.random.default_rng(seed)
    x = np.arange(275.0, 300.0, 0.05)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = rng.poisson(300.0 + g(284.5, 5000.0, 0.8)
                    + g(291.0, 3000.0, 1.0)).astype(float)
    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    resp = client.post("/api/upload", data={
        "file": (io.BytesIO(csv.encode()), "c1s.csv")})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["session_id"]


def test_meta_advertises_fit_full_window_default_false(client):
    """The server default must be False — the checkbox is unchecked out
    of the box, so today's truncated-ROI behavior is exactly preserved
    for anyone not opting in."""
    meta = client.get("/api/analyze/meta").get_json()
    methods = {m["id"]: m for m in meta["methods"]}
    assert methods["ic_model_comparison"]["default_options"]["fit_full_window"] is False


def test_fit_full_window_option_round_trips_without_error(client):
    """A request with ``options.fit_full_window: true`` for a real
    curated region (C 1s) must be accepted and reach the engine — no
    "unknown option" validation error, confirming the option is plumbed
    through app.py's shared validate/run path to compare_models."""
    sid = _upload_c1s_like(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "insulator",
        "regions": ["C 1s"], "method": "ic_model_comparison",
        "roi": {"be_min": 275.0, "be_max": 300.0},
        "options": {"n_refits": 2, "enable_proposal_pass": False,
                    "fit_full_window": True},
    })
    assert resp.status_code == 200, resp.get_json()


def test_fit_full_window_false_still_the_default_via_the_api(client):
    """Omitting the option entirely must behave exactly as it always
    has — a request with no ``fit_full_window`` key is still accepted
    (the server-side default of False fills in silently)."""
    sid = _upload_c1s_like(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "insulator",
        "regions": ["C 1s"], "method": "ic_model_comparison",
        "roi": {"be_min": 275.0, "be_max": 300.0},
        "options": {"n_refits": 2, "enable_proposal_pass": False},
    })
    assert resp.status_code == 200, resp.get_json()
