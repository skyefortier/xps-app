"""
Stage 9 Phase 1 parity gate: the legacy JSON docs must reconstruct the
original XPS_ELEMENTS and CHEMICAL_STATES constants EXACTLY (byte-faithful
values). This is the proof of "exact parity" — if transcription ever drifts
from the embedded constants, this fails.

The expected values are extracted directly from templates/index.html by
evaling the real JS literals (.stage9/legacy_raw.json, regenerated here if
missing), so the test compares JSON-against-source, not JSON-against-itself.
"""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / ".stage9" / "legacy_raw.json"


def _raw():
    # Post-cutover oracle: the XPS_ELEMENTS / CHEMICAL_STATES constants have
    # been REMOVED from the template, so the parity oracle is the immutable
    # fixture tests/fixtures/xps_legacy_snapshot.json — created once and
    # mechanically verified == the original constants (see test_cutover.py).
    # This proves legacy JSON == the frozen original values, which survives
    # constant deletion (Codex Checkpoint-B P0: the oracle must not vanish).
    fx = json.loads((REPO / "tests/fixtures/xps_legacy_snapshot.json").read_text())
    return {"XPS_ELEMENTS": fx["XPS_ELEMENTS"], "CHEMICAL_STATES": fx["CHEMICAL_STATES"]}


def _survey():
    return json.loads((REPO / "data/xps/legacy/survey-lines.json").read_text())


def _chem():
    return json.loads((REPO / "data/xps/legacy/chemical-states.json").read_text())


def test_survey_reconstructs_xps_elements_exactly():
    raw = _raw()["XPS_ELEMENTS"]
    rebuilt = {}
    for el in _survey()["elements"]:
        rebuilt[el["symbol"]] = {"lines": {ln["orbital"]: ln["be_ev"] for ln in el["lines"]}}
    assert rebuilt == raw


def test_chemical_states_reconstructs_exactly():
    raw = _raw()["CHEMICAL_STATES"]
    rebuilt = {}
    for g in _chem()["groups"]:
        rebuilt[g["orbital_key"]] = [
            {"state": s["state"], "be": s["be_ev"], "ref": s["ref"]} for s in g["states"]
        ]
    assert rebuilt == raw


def test_counts_match_known_totals():
    survey, chem = _survey(), _chem()
    assert len(survey["elements"]) == 53
    assert sum(len(e["lines"]) for e in survey["elements"]) == 62
    assert len(chem["groups"]) == 11
    assert sum(len(g["states"]) for g in chem["groups"]) == 52


def test_auger_lines_kept_as_legacy_be_not_converted():
    # O/Na/Mg KLL must remain at their verbatim legacy BE marker positions.
    raw = _raw()["XPS_ELEMENTS"]
    for el in _survey()["elements"]:
        for ln in el["lines"]:
            if ln["transition_type"] == "auger":
                assert ln["be_ev"] == raw[el["symbol"]]["lines"][ln["orbital"]]
                assert ln["be_basis"] == "legacy-marker-position"


def test_legacy_loads_through_reference_payload():
    from xps_reference import load_reference
    payload = load_reference(REPO / "data" / "xps")
    assert payload["legacy"] is not None
    assert len(payload["legacy"]["survey"]) == 53
    assert len(payload["legacy"]["chemical_states"]) == 11


def test_every_legacy_line_tagged_unverified():
    for el in _survey()["elements"]:
        for ln in el["lines"]:
            assert ln["tier"] == "legacy-unverified"
            assert ln["source"] == "legacy-embedded-dataset"
    for g in _chem()["groups"]:
        for s in g["states"]:
            assert s["tier"] == "legacy-unverified"
