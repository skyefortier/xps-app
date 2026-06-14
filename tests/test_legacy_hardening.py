"""
Stage 9 Checkpoint-A hardening regression tests (Codex adversarial findings).

Covers:
  #2  load-time content-checksum verification (tamper-evidence)
  #3  loader rejects duplicate element symbol / orbital_key (accessor overwrite)
  #4  the REAL JS accessor functions deep-equal the constants (rendered page)
  #7  the survey-marker axis convention is locked at be (not be+ccShift)
"""
import copy
import json
import re
import subprocess
from pathlib import Path

import pytest

from xps_reference import (XPSReferenceError, _canon_survey, _verify_legacy_checksum,
                           load_reference)

REPO = Path(__file__).resolve().parents[1]
LEGACY = REPO / "data/xps/legacy"


def _survey():
    return json.loads((LEGACY / "survey-lines.json").read_text())


def _write_temp_dataset(tmp_path, mutate_survey=None, mutate_chem=None):
    """Copy the real data/xps into tmp, optionally mutate a legacy doc."""
    import shutil
    dst = tmp_path / "xps"
    shutil.copytree(REPO / "data/xps", dst)
    if mutate_survey:
        doc = json.loads((dst / "legacy/survey-lines.json").read_text())
        mutate_survey(doc)
        (dst / "legacy/survey-lines.json").write_text(json.dumps(doc, indent=2))
    if mutate_chem:
        doc = json.loads((dst / "legacy/chemical-states.json").read_text())
        mutate_chem(doc)
        (dst / "legacy/chemical-states.json").write_text(json.dumps(doc, indent=2))
    return dst


# ── #2: checksum tamper-evidence ────────────────────────────────────────────

def test_shipped_legacy_checksum_verifies():
    # The real dataset must load (checksum matches) — guards against a stale
    # stamp shipping.
    assert load_reference(REPO / "data/xps")["legacy"] is not None


def test_edited_be_value_without_restamp_is_rejected(tmp_path):
    # Drift a single be_ev (schema accepts any in-range number) WITHOUT
    # updating the checksum → load must fail loudly (Codex #2).
    def mutate(doc):
        doc["elements"][0]["lines"][0]["be_ev"] += 0.7
    dst = _write_temp_dataset(tmp_path, mutate_survey=mutate)
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(dst)
    assert "checksum mismatch" in str(exc.value)
    assert exc.value.filename == "legacy/survey-lines.json"


def test_checksum_helper_matches_transcriber_canonicalization():
    # The loader's canonical form must equal the stored stamp for the real data.
    doc = _survey()
    _verify_legacy_checksum(doc, _canon_survey(doc["elements"]),
                            "legacy/survey-lines.json")  # must not raise


# ── #3: duplicate symbol / orbital_key rejection ────────────────────────────

def test_duplicate_element_symbol_rejected(tmp_path):
    def mutate(doc):
        dup = copy.deepcopy(doc["elements"][0])
        dup["lines"][0]["id"] = dup["lines"][0]["id"] + "x"  # unique id, same symbol
        doc["elements"].append(dup)
    dst = _write_temp_dataset(tmp_path, mutate_survey=mutate)
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(dst)
    assert "duplicate element symbol" in str(exc.value)


def test_duplicate_orbital_within_element_rejected(tmp_path):
    def mutate(doc):
        el = doc["elements"][0]
        dup = copy.deepcopy(el["lines"][0])
        dup["id"] = dup["id"] + "x"
        el["lines"].append(dup)  # same orbital, unique id
    dst = _write_temp_dataset(tmp_path, mutate_survey=mutate)
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(dst)
    assert "duplicate orbital" in str(exc.value)


def test_duplicate_orbital_key_rejected(tmp_path):
    def mutate(doc):
        dup = copy.deepcopy(doc["groups"][0])
        for i, s in enumerate(dup["states"]):
            s["id"] = s["id"] + "x"
        doc["groups"].append(dup)  # same orbital_key, unique ids
    dst = _write_temp_dataset(tmp_path, mutate_chem=mutate)
    with pytest.raises(XPSReferenceError) as exc:
        load_reference(dst)
    assert "duplicate orbital_key" in str(exc.value)


# ── #4: real JS accessor deep-equals the constants ──────────────────────────

def test_js_accessor_functions_deep_equal_constants(tmp_path):
    """Render the page and run the ACTUAL _accSurveyElements/_accChemicalStates
    JS against the injected LEGACY_REFERENCE, asserting deep parity with the
    retained constants — not a Python reimplementation."""
    from app import create_app
    app = create_app(upload_folder=str(tmp_path / "up"),
                     data_folder=str(REPO / "data/xps"))
    app.config["TESTING"] = True
    html = app.test_client().get("/").get_data(as_text=True)
    rendered = tmp_path / "rendered.html"
    rendered.write_text(html)
    proc = subprocess.run(
        ["node", ".stage9/accessor_parity_check.mjs", str(rendered)],
        cwd=REPO, capture_output=True, text=True)
    assert proc.returncode == 0, f"accessor parity failed: {proc.stdout}\n{proc.stderr}"
    assert "ACCESSOR_PARITY_OK" in proc.stdout


# ── #7: axis-convention lock (survey markers draw at be, not be+ccShift) ─────

def test_survey_marker_axis_convention_locked():
    """The survey label plugin must place reference markers at the reference
    BE directly on the corrected-BE axis — never be+ccShift (the legacy bug).
    Locks the convention against regression."""
    html = (REPO / "templates/index.html").read_text()
    # The survey-marker draw call inside the markers.forEach over el.lines.
    m = re.search(r"Object\.entries\(el\.lines\)\.forEach\(\(\[line, be\]\) => \{(.*?)\}\);",
                  html, re.S)
    assert m, "survey-marker draw block not found — refactor may have moved it"
    block = m.group(1)
    assert "getPixelForValue(be)" in block, "survey marker must draw at be"
    assert "getPixelForValue(be + shift)" not in block, \
        "REGRESSION: survey marker reverted to be+ccShift (the documented bug)"
    # And the corrected-BE axis itself: getCorrectedBE subtracts ccShift.
    cb = re.search(r"function getCorrectedBE\(\) \{(.*?)\}", html, re.S)
    assert cb and "ccShift" in cb.group(1) and "- shift" in cb.group(1), \
        "getCorrectedBE must produce the corrected (ccShift-subtracted) axis"
