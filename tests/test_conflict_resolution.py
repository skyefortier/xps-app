"""Phase B conflict-resolution: 4 metal/elemental↔oxide/compound conflicts promoted
into the machine tier as reduced nominals with a reduced→oxidized band.

Hard invariants — the emitted numbers are reference data, so any failure blocks.
"""
import json
import os
import subprocess

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data", "xps")


def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


MACHINE = _load("elements-machine.json")
PROV = _load("elements-machine.provenance.json")
SKIPPED = _load("elements-machine.skipped.json")

# id -> (expected reduced nominal, legacy oxidized value, reduced_state, oxidized_state)
EXPECTED = {
    "Ti-2p3/2": (453.98, 459, "metal", "oxide"),
    "Cr-2p3/2": (574.35, 577, "metal", "oxide"),
    "Fe-2p3/2": (706.86, 711, "metal", "oxide"),
    "P-2p3/2":  (130.01, 133, "elemental", "phosphate"),
}


def _machine_by_id():
    out = {}
    for el in MACHINE["elements"]:
        for fam in el["families"]:
            for t in fam["transitions"]:
                out[t["id"]] = (t, el)
    return out


def test_four_conflicts_promoted_as_reduced_to_oxidized():
    by_id = _machine_by_id()
    for tid, (nom, oxid, red_state, ox_state) in EXPECTED.items():
        assert tid in by_id, f"{tid} not in machine tier"
        t, el = by_id[tid]
        assert t["tier"] == "machine"
        assert t["nominal_be_ev"] == nom                         # reduced NIST-evaluated value
        r = t["expected_region_ev"]
        assert r["basis"] == "reduced-to-oxidized-chemical-state-span"
        assert r["max"] == oxid                                  # band top = legacy oxidized value
        assert r["min"] <= t["nominal_be_ev"] < r["max"]         # reduced nominal inside, below oxidized
        assert t["spin_orbit"] is None
        assert t["visibility"]["AlKa"] == "machine-unassessed"
        # nothing on these records reads "curated"
        assert el["curation_status"] == "machine"
        assert t["tier"] != "curated"


def test_p_reads_elemental_phosphate_not_metal_oxide():
    prov = {p["id"]: p for p in PROV["transitions"]}
    cr = prov["P-2p3/2"]["conflict_resolution"]
    assert cr["reduced_state"] == "elemental" and cr["oxidized_state"] == "phosphate"
    notes = _machine_by_id()["P-2p3/2"][0]["notes"]
    assert "elemental" in notes and "phosphate" in notes
    assert "metal" not in notes and "oxide" not in notes


def test_provenance_has_conflict_resolution_and_sha256():
    prov = {p["id"]: p for p in PROV["transitions"]}
    for tid, (nom, oxid, red_state, ox_state) in EXPECTED.items():
        assert tid in prov, f"{tid} missing from provenance"
        p = prov[tid]
        assert p["nominal_be_ev"] == nom
        assert len(p["nominal_source"]["source_artifact_sha256"]) == 64
        cr = p["conflict_resolution"]
        assert set(cr) == {"rule", "reduced_state", "oxidized_state",
                           "superseded_legacy_value", "region_basis"}
        assert cr["reduced_state"] == red_state
        assert cr["oxidized_state"] == ox_state
        assert cr["superseded_legacy_value"] == oxid
        assert cr["region_basis"] == "reduced-to-oxidized-chemical-state-span"


def test_v_and_augers_still_skipped_and_four_gone_from_conflict():
    conflict = [(t["element"], t.get("orbital")) for t in SKIPPED["transitions"]
                if t["reason"] == "conflict"]
    # The 4 are gone from the conflict bucket.
    for el, orb in [("Ti", "2p3/2"), ("Cr", "2p3/2"), ("Fe", "2p3/2"), ("P", "2p3/2")]:
        assert (el, orb) not in conflict
    # V + both Auger KLL remain in the conflict bucket.
    assert ("V", "2p3/2") in conflict
    assert ("Na", "KL23L23(1D)") in conflict
    assert ("Mg", "KL23L23(1D)") in conflict
    # V's skip is annotated with BOTH reasons.
    v = [t for t in SKIPPED["transitions"] if (t["element"], t.get("orbital")) == ("V", "2p3/2")][0]
    assert "no NIST-evaluated" in v["detail"] and "conflict" in v["detail"].lower()
    # V is NOT in the machine tier.
    assert "V-2p3/2" not in _machine_by_id()


def test_conflict_records_present():
    # The 4 conflict-resolution records remain in the machine tier (they are part
    # of HEAD/main now; the coverage-expansion work must not drop them).
    assert set(EXPECTED) <= set(_machine_by_id())


def test_prior_machine_records_unchanged_vs_head():
    # Curated + legacy byte-unchanged, and EVERY machine record present at HEAD
    # (the 27, including the 4 conflict records) is byte-identical in the working
    # tree — later work (coverage expansion) is purely additive.
    paths = ["data/xps/elements-main.json", "data/xps/elements-actinides.json",
             "data/xps/elements-lanthanides.json", "data/xps/auger-lines.json",
             "data/xps/legacy"]
    r = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "HEAD", "--"] + paths)
    if r.returncode not in (0, 1):
        pytest.skip("git unavailable / no HEAD")
    assert r.returncode == 0, "curated/legacy files changed — must stay byte-unchanged"

    head = subprocess.run(["git", "-C", REPO, "show", "HEAD:data/xps/elements-machine.json"],
                          capture_output=True, text=True)
    if head.returncode != 0:
        pytest.skip("HEAD elements-machine.json unavailable")
    head_doc = json.loads(head.stdout)
    head_by_id = {t["id"]: t for el in head_doc["elements"] for fam in el["families"] for t in fam["transitions"]}
    new_by_id = {tid: t for tid, (t, el) in _machine_by_id().items()}
    for tid, t in head_by_id.items():
        assert new_by_id.get(tid) == t, f"prior machine record {tid} changed"
