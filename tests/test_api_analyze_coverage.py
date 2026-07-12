"""
GET /api/analyze/meta's additive `coverage` key + the routing half of the
expanded element/region selector (2026-07-11, Find Peaks UI improvements
unit 3).  See autofit/coverage_index.py for the tier vocabulary and
tests/autofit/test_coverage_index.py for the index's own unit tests.
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


def test_meta_exposes_the_full_coverage_index(client):
    """Unit 3: /api/analyze/meta gains a 'coverage' key (additive; the
    existing 'regions' key — used by tests/test_api_analyze.py — is
    UNCHANGED) enumerating the full Z=1..96 coverage-tier index for the
    expanded region selector."""
    meta = client.get("/api/analyze/meta").get_json()
    assert {"C 1s", "Cl 2p", "U 4f", "B 1s", "N 1s"} <= set(meta["regions"])
    assert "coverage" in meta
    cov = meta["coverage"]
    assert len(cov) > 100                              # far beyond the 5 basis elements
    by_region = {e["region"]: e for e in cov}
    assert by_region["C 1s"]["tier"] == "curated"
    assert by_region["Fe 2p"]["tier"] in ("machine", "structure_only")
    tiers = {e["tier"] for e in cov}
    assert tiers <= {"curated", "machine", "structure_only"}
    # every curated region in the coverage index matches meta['regions']
    curated_in_cov = {e["region"] for e in cov if e["tier"] == "curated"}
    assert curated_in_cov == set(meta["regions"])


def test_fe2p_runs_via_the_existing_analyze_route_structural_fallback(client):
    """The routing half of unit 3's bar: selecting a coverage-only
    element (Fe 2p) and running Find Peaks must route through the
    EXISTING structural-fallback path — no backend change needed beyond
    the read-only coverage index, confirming /api/analyze already
    handles any Z=1..96 region."""
    rng = np.random.default_rng(3)
    x = np.arange(700.0, 730.0, 0.1)
    y = rng.poisson(300.0 + 5000.0 * np.exp(
        -4 * np.log(2) * ((x - 710.0) / 3.0) ** 2)).astype(float)
    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    resp = client.post("/api/upload", data={
        "file": (io.BytesIO(csv.encode()), "fe2p.csv")})
    sid = resp.get_json()["session_id"]

    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "conductor",
        "regions": ["Fe 2p"], "method": "ic_model_comparison",
        "roi": {"be_min": 700.0, "be_max": 730.0},
        "options": {"n_refits": 2, "enable_proposal_pass": False},
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["structural_only"] == ["Fe 2p"]
    # detection-driven family carries the fit (Stage-2); every emitted
    # peak stays region-unassigned (never dressed up as cited grammar)
    if body["success"]:
        assert all(p["region"] == "unassigned" for p in body["peaks"])
    assert body["structure_report"]


def test_curated_element_still_uses_its_grammar(client):
    """Regression: a curated region (C 1s, unchanged from before unit 3)
    still resolves to a real grammar with candidates, never structural
    fallback."""
    sid = _upload_doublet(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "insulator",
        "regions": ["Cl 2p"], "method": "ic_model_comparison",
        "roi": {"be_min": 192.0, "be_max": 205.0},
        "options": {"n_refits": 2, "enable_proposal_pass": False},
    })
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["structural_only"] == []
    assert body["success"] is True
    assert all(p["region"] == "Cl 2p" for p in body["peaks"])
