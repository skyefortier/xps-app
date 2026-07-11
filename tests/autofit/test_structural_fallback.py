"""Phase D unit 3 — structural fallback in resolve() + honesty surface.

Selecting ANY element/level region (Z=1..96) must return its DERIVED
STRUCTURE — doublet/singlet, ratio expectation, multiplet/conductor flags —
even when positions are UNVERIFIED, with the degradation reported honestly
('structure known, positions UNVERIFIED — supply a cited source') and the
UNVERIFIED/CONDITIONAL records rolling into the existing
uses_conditional_or_unverified_constants surface.

STRICTLY ADDITIVE: the flag defaults off (unknown regions still raise),
registered deep regions are untouched, /api/fit and the manual path are
untouched.
"""

from __future__ import annotations

import io
import json
import re

import numpy as np
import pytest

from autofit.cited_values import load_cited_values
from autofit.grammar import (
    MaterialClass,
    Phase,
    UnknownRegionError,
    resolve,
)


def _phase(regions, mc="conductor"):
    return Phase(id="sample", material_class=MaterialClass(mc),
                 regions=tuple(regions))


def _by_constant(records):
    out = {}
    for r in records:
        out.setdefault(r["constant"], r)
    return out


def test_fallback_off_by_default_unknown_region_still_raises():
    with pytest.raises(UnknownRegionError):
        resolve([_phase(["Fe 2p"])], "Fe 2p")


def test_structural_fallback_returns_structure_without_candidates():
    g = resolve([_phase(["Fe 2p"])], "Fe 2p", allow_structural_fallback=True)
    assert g.candidates == []
    assert g.structural_only == ("Fe 2p",)

    prov = _by_constant(g.provenance["Fe 2p"])
    # exact quantum bookkeeping → VERIFIED, rule-tagged
    st = prov["structure"]
    assert st["status"] == "VERIFIED"
    assert st["derived_rule"].startswith("derived:")
    assert [c["degeneracy"] for c in st["value"]["components"]] == [4, 2]
    assert st["value"]["structure"] == "doublet"
    # ratio EXPECTATION → CONDITIONAL (theory, not measurement)
    ratio = prov["statistical_area_ratio_expectation"]
    assert ratio["status"] == "CONDITIONAL"
    assert ratio["value"]["value"] == pytest.approx(0.5, abs=0)
    assert ratio["value"]["expectation_only"] is True
    # position → UNVERIFIED, value None, points at the cited-source loader
    be = prov["binding_energy_ev"]
    assert be["status"] == "UNVERIFIED" and be["value"] is None
    assert "cited source" in be["source"]
    # flags
    assert prov["multiplet_prone_flag"]["value"] is True        # Fe 3d6
    assert prov["conductor_class_default"]["value"] == "conductor"
    # the fit-physics DB exposure still rides along (entry or absence-record)
    assert any(c.startswith("fit_physics") for c in prov)
    # the honesty message is a first-class note
    assert any("positions UNVERIFIED" in n for n in g.notes)
    assert any("cited source" in n for n in g.notes)


def test_registered_deep_regions_unaffected_by_flag():
    g = resolve([_phase(["Cl 2p"], mc="insulator")], "Cl 2p",
                allow_structural_fallback=True)
    assert g.structural_only == ()
    assert [c.name for c in g.candidates] == [
        "Cl0_doublet", "Cl0r_doublet_relaxed",
        "Cl0w_doublet_freewidth", "Cl0rw_doublet_relaxed_freewidth"]


def test_unparseable_or_unoccupied_regions_still_raise():
    with pytest.raises(UnknownRegionError):
        resolve([_phase(["Xx 2p"])], "Xx 2p", allow_structural_fallback=True)
    with pytest.raises(UnknownRegionError, match="occupied"):
        resolve([_phase(["Fe 5f"])], "Fe 5f", allow_structural_fallback=True)
    with pytest.raises(UnknownRegionError):
        resolve([_phase(["Kryptonite 1s"])], "Kryptonite 1s",
                allow_structural_fallback=True)


def test_cited_values_ride_into_provenance(tmp_path):
    doc = {
        "schema_version": 1, "test_only": True,
        "rows": [
            {"element": "Fe", "level": "2p3/2", "oxidation_state": None,
             "value_type": "binding_energy_ev", "value_ev": 100.0,
             "uncertainty_ev": 0.5,
             "source_citation": "SYNTHETIC-TEST-ONLY demonstration value",
             "method": "synthetic", "convention": "synthetic frame"},
            {"element": "Cl", "level": "2p", "oxidation_state": None,
             "value_type": "spin_orbit_splitting_ev", "value_ev": 100.0,
             "uncertainty_ev": None,
             "source_citation": "SYNTHETIC-TEST-ONLY demonstration value",
             "method": "synthetic", "convention": "synthetic frame"},
        ],
    }
    p = tmp_path / "vals.json"
    p.write_text(json.dumps(doc))
    vals = load_cited_values(str(p))

    g = resolve([_phase(["Fe 2p"])], "Fe 2p", allow_structural_fallback=True,
                cited_values=vals)
    prov = _by_constant(g.provenance["Fe 2p"])
    cited = prov["cited:binding_energy_ev[2p3/2]"]
    assert cited["status"] == "UNVERIFIED"          # test_only file
    assert cited["value"]["value_ev"] == 100.0
    assert cited["value"]["test_only"] is True
    assert "SYNTHETIC-TEST-ONLY" in cited["source"]
    # the Cl row must NOT leak into the Fe 2p region
    assert not any("spin_orbit_splitting" in c for c in prov)
    # loading a position does NOT silently enable fitting
    assert g.candidates == []
    assert any("curated windows" in n for n in g.notes)


def test_singlet_region_has_no_ratio_expectation():
    g = resolve([_phase(["O 1s"], mc="insulator")], "O 1s",
                allow_structural_fallback=True)
    prov = _by_constant(g.provenance["O 1s"])
    assert prov["structure"]["value"]["structure"] == "singlet"
    assert "statistical_area_ratio_expectation" not in prov


def test_joint_deep_plus_structural_keeps_deep_candidates():
    g = resolve([_phase(["Cl 2p", "Fe 2p"], mc="insulator")],
                ["Cl 2p", "Fe 2p"], allow_structural_fallback=True)
    assert g.structural_only == ("Fe 2p",)
    # the deep region's candidates are NOT wiped by the empty structural set
    assert [c.name for c in g.candidates] == [
        "Cl0_doublet", "Cl0r_doublet_relaxed",
        "Cl0w_doublet_freewidth", "Cl0rw_doublet_relaxed_freewidth"]
    assert set(g.provenance) == {"Cl 2p", "Fe 2p"}
    assert any("excluded from candidate composition" in n for n in g.notes)


_EV_PROSE = re.compile(r"\d+\.\d+|\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b"
                       r"|\b\d+(?:\.\d+)?\s*[mk]?eV\b", re.I)


def _leaves(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _leaves(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _leaves(v)
    else:
        yield obj


def test_fallback_never_builds_from_db_values_and_derived_records_are_number_free():
    """Codex D3 review adjudication (run A BLOCKER, dispositioned as
    guard-the-boundary): the tiered fit-physics DB's SOURCED values
    (sha256-pinned NIST archive, exposure-only by design) legitimately
    ride into structural provenance under fit_physics:* constants — but
    they must NEVER become fit-enabling: no candidates, no slots, no
    windows, even for DB-covered regions. And every eV-bearing number in
    the structural provenance must live under a SOURCED record
    (fit_physics:* or cited:*) — the derived-structure records themselves
    stay number-free."""
    for region in ("Cu 2p", "Fe 2p"):   # both have machine-tier DB entries
        g = resolve([_phase([region])], region,
                    allow_structural_fallback=True)
        assert g.candidates == [], (
            f"{region}: DB exposure must never build candidates")
        assert g.diagnostic_windows == {}, (
            f"{region}: DB be_window_ev must never surface as a "
            f"diagnostic window (D3 recheck, both runs MINOR)")
        slug = region
        # Three sourced families may carry eV values: the fit-physics DB
        # exposure, user-cited loader records, and (unit R1) the data/xps
        # reference bridge. fit_physics/cited records are never VERIFIED;
        # bridge records may be VERIFIED ONLY for the curated tier (the
        # goal-prescribed mapping: curator-verified against cited sources).
        sourced_prefixes = ("fit_physics", "cited:", "reference:")
        for rec in g.provenance[slug]:
            const = str(rec.get("constant", ""))
            if const.startswith(sourced_prefixes):
                if rec.get("status") == "VERIFIED":
                    assert const.startswith("reference:curated:"), (
                        f"{region}: sourced record {const} is VERIFIED but "
                        "only curated-tier bridge records may be")
                continue
            # derived-structure record: NO eV-bearing numbers anywhere
            for leaf in _leaves(rec):
                if isinstance(leaf, str):
                    assert not _EV_PROSE.search(leaf), (
                        f"{region}:{rec['constant']}: prose smuggles a "
                        f"numeric value: {leaf!r}")
                if isinstance(leaf, float) and not isinstance(leaf, bool):
                    # the only legal float in derived records is the
                    # statistical ratio's exact value
                    assert rec["constant"] == \
                        "statistical_area_ratio_expectation", (
                        f"{region}:{rec['constant']}: unexpected float "
                        f"{leaf!r} in a derived record")
        # the exposure semantics are stated in a note
        assert any("not used to build candidates" in n.lower()
                   for n in g.notes), (
            f"{region}: DB-exposure semantics note missing")


def test_phase_ambiguity_checked_before_fallback():
    """A structural region contributed by two phases without a target must
    still raise PhaseAmbiguityError — disambiguation runs BEFORE the
    fallback (Codex D3 review, run B MINOR: regression pin)."""
    from autofit.grammar import PhaseAmbiguityError
    p1 = Phase(id="a", material_class=MaterialClass("conductor"),
               regions=("Fe 2p",))
    p2 = Phase(id="b", material_class=MaterialClass("conductor"),
               regions=("Fe 2p",))
    with pytest.raises(PhaseAmbiguityError):
        resolve([p1, p2], "Fe 2p", allow_structural_fallback=True)


def test_structural_records_roll_into_the_existing_rollup():
    g = resolve([_phase(["Fe 2p"])], "Fe 2p", allow_structural_fallback=True)
    # the exact expression the methods use (ic_model_comparison etc.)
    non_verified = sorted({
        f"{slug}:{e['constant']}"
        for slug, entries in g.provenance.items()
        for e in entries if e.get("status") != "VERIFIED"
    })
    assert "Fe 2p:binding_energy_ev" in non_verified
    assert "Fe 2p:statistical_area_ratio_expectation" in non_verified
    assert "Fe 2p:structure" not in non_verified     # exact QM — not flagged


# ── API degradation (POST /api/analyze) ─────────────────────────────────────

@pytest.fixture()
def client(tmp_path):
    from app import create_app
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload(client, peaked=True):
    x = np.arange(700.0, 730.0, 0.05)
    if peaked:
        y = 300.0 + 5000.0 * np.exp(-4 * np.log(2) * ((x - 710.0) / 2.0) ** 2)
    else:
        # featureless: flat baseline (detection must find nothing)
        y = np.full_like(x, 300.0)
    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    resp = client.post("/api/upload", data={
        "file": (io.BytesIO(csv.encode()), "fe.csv")})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["session_id"]


def test_api_analyze_degrades_to_structure_report(client):
    """Stage-2 UPDATE (2026-07-10): a structural-fallback region now RUNS
    the sweep (the detection family is the model space), so the honest
    structure-report stub is returned only when detection finds NOTHING
    fittable — pinned here with a featureless window."""
    sid = _upload(client, peaked=False)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "conductor",
        "regions": ["Fe 2p"], "method": "ic_model_comparison",
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["success"] is False
    assert body["structural_only"] == ["Fe 2p"]
    assert body["peaks"] == []
    assert "positions UNVERIFIED" in body["message"]
    assert "cited source" in body["message"]
    assert body["structure_report"]["Fe 2p"]
    assert "Fe 2p:binding_energy_ev" in \
        body["uses_conditional_or_unverified_constants"]
    # the review-gate honesty stub still rides on the degraded response
    assert body["review_gate"]["reviewed_by"] is None


def test_api_analyze_structural_region_fits_via_detection(client):
    """Stage-2 (across-the-periodic-table path): a structural-fallback
    region WITH real detectable structure fits through the detection
    family — peaks emitted region-unassigned, the derived-structure
    report still attached for the honesty surface."""
    sid = _upload(client, peaked=True)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "conductor",
        "regions": ["Fe 2p"], "method": "ic_model_comparison",
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["success"] is True
    assert body["structural_only"] == ["Fe 2p"]
    assert body["peaks"], "detection family must carry the fit"
    assert all(p["region"] == "unassigned" for p in body["peaks"])
    assert any(abs(p["center"] - 710.0) < 0.5 for p in body["peaks"])
    assert body["structure_report"]["Fe 2p"]
    assert body["diagnostics"]["winner"].startswith("D0_detected")
    assert body["review_gate"]["reviewed_by"] is None


def test_api_analyze_unparseable_region_still_400(client):
    sid = _upload(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "conductor",
        "regions": ["Kryptonite 9x"], "method": "ic_model_comparison",
    })
    assert resp.status_code == 400


def _upload_cl_doublet(client):
    rng = np.random.default_rng(7)
    x = np.arange(192.0, 205.0, 0.05)

    def pv(h, c, w, eta=0.3):
        g = np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
        lo = (w / 2) ** 2 / ((x - c) ** 2 + (w / 2) ** 2)
        return h * ((1 - eta) * g + eta * lo)

    y = rng.poisson(300.0 + pv(9000.0, 197.9, 1.65)
                    + pv(4950.0, 199.5, 1.65)).astype(float)
    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    resp = client.post("/api/upload", data={
        "file": (io.BytesIO(csv.encode()), "cl.csv")})
    assert resp.status_code == 200, resp.get_json()
    return resp.get_json()["session_id"]


def test_api_mixed_deep_plus_structural_runs_and_flags(client):
    """Mixed request: the deep region fits normally; the structural region
    is flagged in the payload (Codex D3 review, run B MINOR: API pin)."""
    sid = _upload_cl_doublet(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "insulator",
        "regions": ["Cl 2p", "Fe 2p"], "method": "ic_model_comparison",
        "roi": {"be_min": 192.0, "be_max": 205.0},
        "options": {"n_refits": 2, "enable_proposal_pass": False},
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["structural_only"] == ["Fe 2p"]
    assert body["success"] is True          # the Cl 2p fit ran
    assert len(body["peaks"]) == 2
    # the structural region's derived records ride in the analysis payload —
    # assert actual DERIVED content, not just the key (D3 recheck run B)
    fe_constants = {r["constant"]
                    for r in body["analysis"]["constants_provenance"]["Fe 2p"]}
    assert {"structure", "binding_energy_ev",
            "multiplet_prone_flag"} <= fe_constants


def test_api_least_squares_never_reaches_structural_degradation(client):
    """least_squares takes no grammar (grammar=None) — an unregistered
    region must not trigger the structure-report path (run B MINOR)."""
    sid = _upload_cl_doublet(client)
    resp = client.post("/api/analyze", json={
        "session_id": sid, "material_class": "conductor",
        "regions": ["Fe 2p"], "method": "least_squares",
        "peak_specs": [{"id": 1, "shape": "pseudo_voigt_gl",
                        "center": 197.9, "fwhm": 1.6, "amplitude": 9000.0,
                        "gl_mix": 30}],
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert "structure_report" not in body
    assert body["structural_only"] == []
