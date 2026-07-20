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
                                             "semiconductor", "mixed"}
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


def test_analyze_non_object_bodies_are_clean_400s(client):
    """Codex analyze review blocker: a JSON array/string/null body (or
    non-object roi/phase) must be a clean 400, never a 500."""
    sid = _upload_doublet(client)
    for body in (["not", "an", "object"], "string", 42):
        resp = client.post("/api/analyze", json=body)
        assert resp.status_code == 400, (body, resp.status_code)
        assert "JSON object" in resp.get_json()["error"]
    base = {"session_id": sid, "material_class": "insulator",
            "regions": ["Cl 2p"], "method": "ic_model_comparison"}
    # truthy AND falsy non-objects: `or {}` used to swallow [] / "" / false
    for bad in (["bad"], [], "", False):
        for field, frag in (("roi", "'roi'"), ("phase", "'phase'"),
                            ("options", "'options'")):
            resp = client.post("/api/analyze", json={**base, field: bad})
            assert resp.status_code == 400, (field, bad, resp.status_code)
            assert frag in resp.get_json()["error"]


def test_analyze_malformed_option_values_are_400s(client):
    """A well-formed options OBJECT with a malformed VALUE (TypeError from
    the method's numeric casts) must be a clean 400, never a 500."""
    sid = _upload_doublet(client)
    for bad_opts in ({"n_refits": []}, {"n_refits": {"a": 1}},
                     {"rng_seed": [1, 2]}):
        resp = client.post("/api/analyze", json={
            "session_id": sid, "material_class": "insulator",
            "regions": ["Cl 2p"], "method": "ic_model_comparison",
            "options": bad_opts})
        assert resp.status_code == 400, (bad_opts, resp.status_code)
        assert "invalid option" in resp.get_json()["error"].lower()


def test_analyze_material_class_mixed_accepted(client):
    """MaterialClass.MIXED (2026-07-20 unit) round-trips through the
    ordinary /api/analyze path exactly like any other material class --
    Cl 2p's region module doesn't special-case it, so this is a plain
    acceptance check, not a behavior check (that lives in
    tests/autofit/test_c1s_mixed_material_class.py, against C 1s)."""
    sid = _upload_doublet(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "mixed",
        "regions": ["Cl 2p"], "method": "ic_model_comparison",
        "roi": {"be_min": 192.0, "be_max": 205.0},
        "options": {"n_refits": 2, "enable_proposal_pass": False},
    })
    assert resp.status_code == 200, resp.get_json()
    assert resp.get_json()["success"] is True


def test_analyze_start_material_class_mixed_accepted(client):
    """Same acceptance check through the async /api/analyze/start path --
    shares _validate_analyze_request with the sync route. Success here is
    202 (job accepted), not 200 -- /api/analyze/start never returns the
    result body directly; that comes from polling /api/analyze/progress."""
    sid = _upload_doublet(client)
    resp = client.post("/api/analyze/start", json={
        "session_id": sid, "material_class": "mixed",
        "regions": ["Cl 2p"], "method": "ic_model_comparison",
        "roi": {"be_min": 192.0, "be_max": 205.0},
        "options": {"n_refits": 2, "enable_proposal_pass": False},
    })
    assert resp.status_code == 202, resp.get_json()
    assert "job_id" in resp.get_json()


def test_material_class_does_not_affect_charge_correction(client):
    """DECIDED (Skye, 2026-07-17): MIXED must not alter the charge-
    correction step in any way -- not suppressed, not adjusted, not
    conditionally applied. Verified at the mechanism, not just by reading
    the diff: _validate_analyze_request's corrected/ROI-masked (x, y)
    arrays -- the actual output of the cc_shift charge-correction step --
    must be byte-identical regardless of material_class. material_class
    only ever reaches Phase.material_class, consumed by grammar
    resolution/candidate building, which happens strictly AFTER x/y are
    already fixed."""
    from app import _validate_analyze_request

    sid = _upload_doublet(client)
    upload_folder = client.application.config["UPLOAD_FOLDER"]
    base = {
        "session_id": sid, "regions": ["Cl 2p"],
        "method": "ic_model_comparison", "cc_shift": 1.23,
        "roi": {"be_min": 192.0, "be_max": 205.0},
    }
    ctx_conductor = _validate_analyze_request(
        {**base, "material_class": "conductor"}, upload_folder)
    ctx_mixed = _validate_analyze_request(
        {**base, "material_class": "mixed"}, upload_folder)
    assert np.array_equal(ctx_conductor.x, ctx_mixed.x)
    assert np.array_equal(ctx_conductor.y, ctx_mixed.y)


def test_json_sanitize_non_finite():
    """inf/NaN (degenerate-fit BIC values) must become null, not invalid
    JSON tokens browsers refuse to parse."""
    from app import _json_sanitize
    out = _json_sanitize({"a": float("inf"), "b": float("nan"),
                          "c": [1.0, float("-inf")],
                          "d": np.float64("inf"), "e": 2.5})
    assert out == {"a": None, "b": None, "c": [1.0, None],
                   "d": None, "e": 2.5}
    json.dumps(out, allow_nan=False)
