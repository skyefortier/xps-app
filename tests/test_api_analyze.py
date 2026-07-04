"""
POST /api/analyze + GET /api/analyze/meta — the opt-in Find Peaks backend
(spec §5A/§8).  STRICTLY ADDITIVE: /api/fit and the manual path are
untouched (their own tests stand).

End-to-end through the Flask client: upload a synthetic Cl 2p-like doublet
session, run the IC method against the registered grammar, and pin the
contract — candidate peaks + per-peak confidence + the analysis namespace
(ambiguity flags, ranked alternatives, constants provenance incl. the
fit-physics exposure) + the named-review gate stub.  Validation paths pin
clean 400s (never 500s) for malformed input, with the METHOD's own option
whitelist doing option validation.
"""

import io
import json

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
    """Synthetic Cl 2p-like doublet (corrected frame, cc_shift=0)."""
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


def test_meta_menu(client):
    meta = client.get("/api/analyze/meta").get_json()
    assert set(meta["material_classes"]) == {"conductor", "insulator",
                                             "semiconductor"}
    assert {"C 1s", "Cl 2p", "U 4f", "B 1s", "N 1s"} <= set(meta["regions"])
    methods = {m["id"]: m for m in meta["methods"]}
    assert set(methods) == {"least_squares", "ic_model_comparison",
                            "bayesian_exchange_mc", "sparse_map"}
    assert methods["ic_model_comparison"]["default_options"]["n_refits"] == 4


def test_analyze_ic_end_to_end(client):
    sid = _upload_doublet(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "insulator",
        "regions": ["Cl 2p"], "method": "ic_model_comparison",
        "roi": {"be_min": 192.0, "be_max": 205.0},
        "options": {"n_refits": 2, "enable_proposal_pass": False},
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["success"] is True
    assert body["diagnostics"]["winner"]
    assert len(body["peaks"]) == 2
    roles = {p["role"] for p in body["peaks"]}
    assert roles == {"main_cl2p32", "main_cl2p12"}
    # per-peak confidence vector present
    assert set(body["confidence"]) == roles
    # ambiguity/alternatives surface: ranked candidate table + flags
    names = [c["name"] for c in body["analysis"]["candidates"]]
    assert "Cl0_doublet" in names
    assert "conditional_tier" in body["analysis"]
    # constants provenance flows through, incl. the fit-physics exposure
    prov_keys = {p["constant"]
                 for p in body["analysis"]["constants_provenance"]["Cl 2p"]}
    assert "fit_physics:Cl-2p3/2" in prov_keys
    # the named-review gate (spec §8): nothing is pre-approved
    assert body["review_gate"]["reviewed_by"] is None
    # payload is pure JSON (no numpy leakage)
    json.dumps(body)


def test_analyze_least_squares_baseline(client):
    sid = _upload_doublet(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "insulator",
        "regions": ["Cl 2p"], "method": "least_squares",
        "peak_specs": [
            {"id": "1", "shape": "pseudo_voigt_gl", "center": 197.9,
             "amplitude": 9000, "fwhm": 1.6, "glMix": 30},
            {"id": "2", "shape": "pseudo_voigt_gl", "center": 199.5,
             "amplitude": 5000, "fwhm": 1.6, "glMix": 30},
        ],
        "options": {"background_method": "linear"},
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["success"] is True
    centers = sorted(p["center"] for p in body["peaks"])
    assert centers[0] == pytest.approx(197.9, abs=0.1)
    assert centers[1] == pytest.approx(199.5, abs=0.1)


@pytest.mark.parametrize("payload,fragment", [
    ({"method": "nonexistent"}, "Unknown analyze method"),
    ({"material_class": "plasma"}, "material_class"),
    ({"regions": []}, "regions"),
    ({"regions": ["Xx 9z"]}, "region"),
    ({"method": "least_squares"}, "peak_specs"),
    ({"options": {"bogus_option": 1}}, "unknown"),
    ({"roi": {"be_min": 197.0, "be_max": 197.2}}, "20 points"),
    ({"cc_shift": "lots"}, "cc_shift"),
])
def test_analyze_validation_400s(client, payload, fragment):
    sid = _upload_doublet(client)
    base = {"session_id": sid, "material_class": "insulator",
            "regions": ["Cl 2p"], "method": "ic_model_comparison",
            "options": {"n_refits": 2, "enable_proposal_pass": False}}
    base.update(payload)
    resp = client.post("/api/analyze", json=base)
    assert resp.status_code == 400, resp.get_json()
    assert fragment.lower() in resp.get_json()["error"].lower()


def test_analyze_unknown_session_404(client):
    resp = client.post("/api/analyze", json={
        "session_id": "0" * 32, "material_class": "insulator",
        "regions": ["Cl 2p"]})
    assert resp.status_code == 404
