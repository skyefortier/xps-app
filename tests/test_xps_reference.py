"""
Loader + endpoint tests for the data/xps reference dataset.

Covers the validation contract from the periodic-table feature plan:
schema validation with filename + JSON-path error reporting, semantic
checks (unique ids, source resolution, region ordering, spin-orbit
reciprocity, auger KE-not-BE), and the /api/xps-reference endpoint
(payload shape, structured errors, mtime cache invalidation).

Fixture values are SYNTHETIC — they exercise the validator, they are
not shipped reference data (curated values live in data/xps/*.json and
are validated by test_real_dataset_loads).
"""
import json
import os
import shutil
from pathlib import Path

import pytest

from xps_reference import XPSReferenceError, load_reference

REPO = Path(__file__).resolve().parents[1]


# ─────────────────────────────────────────────────────────────────────────────
# Fixture dataset builders
# ─────────────────────────────────────────────────────────────────────────────

def _nb_doublet():
    nb52 = {
        "id": "Nb-3d5/2", "element": "Nb", "z": 41, "orbital": "3d5/2",
        "transition_type": "photoelectron", "nominal_be_ev": 202.3,
        "spin_orbit": {"partner_id": "Nb-3d3/2", "splitting_ev": 2.72, "area_ratio": 1.5},
        "expected_region_ev": {"min": 201.0, "max": 211.0, "basis": "observed-reference-range"},
        "visibility": {"AlKa": "major"}, "source": "test-src",
    }
    nb32 = {
        "id": "Nb-3d3/2", "element": "Nb", "z": 41, "orbital": "3d3/2",
        "transition_type": "photoelectron", "nominal_be_ev": 205.0,
        "spin_orbit": {"partner_id": "Nb-3d5/2", "splitting_ev": 2.72, "area_ratio": 0.6667},
        "expected_region_ev": {"min": 203.5, "max": 214.0, "basis": "observed-reference-range"},
        "visibility": {"AlKa": "major"}, "source": "test-src",
    }
    return nb52, nb32


def _o_singlet():
    return {
        "id": "O-1s", "element": "O", "z": 8, "orbital": "1s",
        "transition_type": "photoelectron", "nominal_be_ev": 531.0,
        "spin_orbit": None,
        "expected_region_ev": {"min": 528.0, "max": 536.0, "basis": "observed-reference-range"},
        "visibility": {"AlKa": "major"}, "source": "test-src",
    }


def _cu_auger():
    return {
        "id": "Cu-L3M4,5M4,5", "element": "Cu", "z": 29, "orbital": "L3M4,5M4,5",
        "transition_type": "auger", "auger_ke_ev": 918.6,
        "expected_region_ev": {"min": 914.0, "max": 922.0, "basis": "observed-reference-range"},
        "visibility": {"AlKa": "major"}, "source": "test-src",
    }


def make_dataset(tmp_path):
    """Write a complete, minimal, VALID dataset; return its directory."""
    d = tmp_path / "xps"
    d.mkdir()
    shutil.copy(REPO / "data" / "xps" / "schema.json", d / "schema.json")
    _write(d, "sources.json", {
        "schema_version": 1,
        "sources": {"test-src": {"citation": "Synthetic Test Handbook of XPS, 1st ed., 1999.",
                                  "type": "handbook"}},
    })
    nb52, nb32 = _nb_doublet()
    _write(d, "elements-main.json", {
        "schema_version": 1, "file_id": "elements-main",
        "elements": [
            {"symbol": "Nb", "z": 41, "name": "Niobium", "curation_status": "curated",
             "families": [{"family": "3d", "transitions": [nb52, nb32]}]},
            {"symbol": "O", "z": 8, "name": "Oxygen", "curation_status": "curated",
             "families": [{"family": "1s", "transitions": [_o_singlet()]}]},
        ],
    })
    _write(d, "elements-lanthanides.json",
           {"schema_version": 1, "file_id": "elements-lanthanides", "elements": []})
    _write(d, "elements-actinides.json",
           {"schema_version": 1, "file_id": "elements-actinides", "elements": []})
    _write(d, "auger-lines.json", {
        "schema_version": 1, "file_id": "auger-lines",
        "elements": [{"symbol": "Cu", "z": 29, "name": "Copper", "curation_status": "partial",
                      "families": [{"family": "LMM", "transitions": [_cu_auger()]}]}],
    })
    return d


def _write(d, fname, data):
    (d / fname).write_text(json.dumps(data, indent=1))


def _edit(d, fname, mutate):
    """Load a dataset file, apply ``mutate(data)``, write it back."""
    data = json.loads((d / fname).read_text())
    mutate(data)
    _write(d, fname, data)


# ─────────────────────────────────────────────────────────────────────────────
# Loader: happy paths
# ─────────────────────────────────────────────────────────────────────────────

def test_real_dataset_loads():
    """The shipped data/xps dataset must always pass full validation."""
    payload = load_reference(REPO / "data" / "xps")
    assert payload["schema_version"] == 1
    assert "sources" in payload and "elements" in payload and "auger" in payload


def test_valid_minimal_dataset_payload_shape(tmp_path):
    d = make_dataset(tmp_path)
    payload = load_reference(d)
    symbols = [e["symbol"] for e in payload["elements"]]
    assert symbols == ["Nb", "O"]
    assert [e["symbol"] for e in payload["auger"]] == ["Cu"]
    assert payload["sources"]["test-src"]["type"] == "handbook"


def test_conventions_expose_displayed_defaults(tmp_path):
    """Photon energy / work function defaults must come from vgd_parser's
    convention (BE = hv - KE - wf), exposed for explicit UI display."""
    d = make_dataset(tmp_path)
    conv = load_reference(d)["conventions"]
    assert conv["photon_energy_ev"]["AlKa"] == 1486.6
    assert conv["photon_energy_ev"]["MgKa"] == 1253.6
    assert conv["work_function_ev"] == 4.5
    assert conv["default_source"] == "AlKa"


# ─────────────────────────────────────────────────────────────────────────────
# Loader: structural failures (filename + JSON path in the error)
# ─────────────────────────────────────────────────────────────────────────────

def test_malformed_json_reports_filename(tmp_path):
    d = make_dataset(tmp_path)
    (d / "elements-main.json").write_text('{"schema_version": 1,')
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert exc.value.filename == "elements-main.json"


def test_missing_file_reports_filename(tmp_path):
    d = make_dataset(tmp_path)
    (d / "auger-lines.json").unlink()
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert exc.value.filename == "auger-lines.json"


def test_schema_violation_reports_json_path(tmp_path):
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][0]["families"][0]
          ["transitions"][0].update({"nominal_be_ev": "not-a-number"}))
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert exc.value.filename == "elements-main.json"
    assert "elements[0]" in exc.value.json_path
    assert "transitions[0]" in exc.value.json_path


def test_auger_record_with_nominal_be_rejected(tmp_path):
    """Auger records store kinetic energy ONLY — nominal_be_ev is invalid."""
    d = make_dataset(tmp_path)

    def mutate(data):
        t = data["elements"][0]["families"][0]["transitions"][0]
        t["nominal_be_ev"] = 568.0
    _edit(d, "auger-lines.json", mutate)
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert exc.value.filename == "auger-lines.json"
    assert "transitions[0]" in exc.value.json_path


def test_photoelectron_record_with_auger_ke_rejected(tmp_path):
    d = make_dataset(tmp_path)

    def mutate(data):
        t = data["elements"][1]["families"][0]["transitions"][0]
        t["auger_ke_ev"] = 951.1
    _edit(d, "elements-main.json", mutate)
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert exc.value.filename == "elements-main.json"


# ─────────────────────────────────────────────────────────────────────────────
# Loader: semantic failures
# ─────────────────────────────────────────────────────────────────────────────

def test_duplicate_transition_ids_rejected(tmp_path):
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][0]["families"][0]
          ["transitions"][1].update({"id": "Nb-3d5/2"}))
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert "duplicate" in str(exc.value).lower()
    assert "Nb-3d5/2" in str(exc.value)


def test_unresolved_source_id_rejected(tmp_path):
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][1]["families"][0]
          ["transitions"][0].update({"source": "no-such-source"}))
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert "no-such-source" in str(exc.value)
    assert exc.value.filename == "elements-main.json"


def test_expected_region_min_above_max_rejected(tmp_path):
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][1]["families"][0]
          ["transitions"][0].update({"expected_region_ev":
              {"min": 536.0, "max": 528.0, "basis": "observed-reference-range"}}))
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert "min" in str(exc.value)


def test_nominal_energy_outside_expected_region_rejected(tmp_path):
    """Typo guard: the nominal energy must sit inside its orientation range."""
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][1]["families"][0]
          ["transitions"][0].update({"nominal_be_ev": 31.0}))
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert "expected_region" in str(exc.value)


def test_spin_orbit_partner_must_exist(tmp_path):
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][0]["families"][0]
          ["transitions"][0]["spin_orbit"].update({"partner_id": "Nb-3d1/2"}))
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert "Nb-3d1/2" in str(exc.value)


def test_spin_orbit_partner_must_be_reciprocal(tmp_path):
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][0]["families"][0]
          ["transitions"][1].update({"spin_orbit": None}))
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert "reciprocal" in str(exc.value).lower()


def test_element_symbol_duplicated_across_files_rejected(tmp_path):
    d = make_dataset(tmp_path)

    def mutate(data):
        main = json.loads((d / "elements-main.json").read_text())
        data["elements"].append(main["elements"][0])
    _edit(d, "elements-actinides.json", mutate)
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    # Duplicate ids are also a consequence; accept either message but the
    # offending file must be named.
    assert exc.value.filename in ("elements-actinides.json", "elements-main.json")


def test_transition_element_must_match_parent(tmp_path):
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][1]["families"][0]
          ["transitions"][0].update({"element": "N"}))
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert exc.value.filename == "elements-main.json"


def test_photoelectron_transition_in_auger_file_rejected(tmp_path):
    d = make_dataset(tmp_path)

    def mutate(data):
        o1s = _o_singlet()
        o1s["id"] = "O-1s-misplaced"
        data["elements"][0]["families"].append({"family": "1s", "transitions": [o1s]})
    _edit(d, "auger-lines.json", mutate)
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(d)
    assert exc.value.filename == "auger-lines.json"


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────────────────────────────────

def _make_app(tmp_path, data_dir):
    from app import create_app
    app = create_app(upload_folder=str(tmp_path / "uploads"), data_folder=str(data_dir))
    app.config["TESTING"] = True
    return app.test_client()


def test_endpoint_returns_validated_payload(tmp_path):
    client = _make_app(tmp_path, make_dataset(tmp_path))
    resp = client.get("/api/xps-reference")
    assert resp.status_code == 200
    body = resp.get_json()
    assert [e["symbol"] for e in body["elements"]] == ["Nb", "O"]
    assert body["conventions"]["work_function_ev"] == 4.5


def test_endpoint_structured_error_on_invalid_data(tmp_path):
    d = make_dataset(tmp_path)
    _edit(d, "elements-main.json", lambda data: data["elements"][0]["families"][0]
          ["transitions"][0].update({"visibility": {"AlKa": "blinding"}}))
    client = _make_app(tmp_path, d)
    resp = client.get("/api/xps-reference")
    assert resp.status_code == 500
    body = resp.get_json()
    assert body["file"] == "elements-main.json"
    assert "elements[0]" in body["path"]
    assert body["error"]


def test_endpoint_cache_invalidates_on_file_change(tmp_path):
    d = make_dataset(tmp_path)
    client = _make_app(tmp_path, d)
    assert len(client.get("/api/xps-reference").get_json()["elements"]) == 2

    # Remove the O entry, force a newer mtime (defeats coarse mtime ticks)
    _edit(d, "elements-main.json", lambda data: data["elements"].pop())
    stat = (d / "elements-main.json").stat()
    os.utime(d / "elements-main.json", ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))

    body = client.get("/api/xps-reference").get_json()
    assert [e["symbol"] for e in body["elements"]] == ["Nb"]
