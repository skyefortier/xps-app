"""Phase B conflict-resolution: 4 metal/elemental↔oxide/compound conflicts promoted
into the machine tier as reduced nominals with a reduced→oxidized band.

Hard invariants — the emitted numbers are reference data, so any failure blocks.
"""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data", "xps")
MACHINE_SNAPSHOT = os.path.join(REPO, "tests", "fixtures", "machine_records_snapshot.json")
CURATED_SNAPSHOT = os.path.join(REPO, "tests", "fixtures", "curated_records_snapshot.json")

# Curated photoelectron + auger files and the scientific element-level fields the
# old byte-diff guard protected. Additive display fields (short_caveat) and the
# families array are excluded — see tests/fixtures/curated_records_snapshot.json.
CURATED_FILES = ("elements-main.json", "elements-actinides.json",
                 "elements-lanthanides.json", "auger-lines.json")
ELEMENT_META_FIELDS = ("symbol", "z", "name", "curation_status", "curation_notes")
LEGACY_PAYLOADS = {"survey-lines.json": "elements",
                   "chemical-states.json": "groups",
                   "corrections.json": "crossrefs"}


def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def _assert_curated_and_legacy_match_snapshot():
    """Every curated transition, element-meta entry, and legacy payload in
    curated_records_snapshot.json is still present and structurally identical in
    the live data. Fixture is the SOLE oracle (no git/HEAD); additive display
    fields (short_caveat) are excluded, so they never trip it."""
    snap = json.load(open(CURATED_SNAPSHOT))
    records, meta = {}, {}
    for fn in CURATED_FILES:
        for el in _load(fn)["elements"]:
            meta[f"{fn}:{el['symbol']}"] = {k: el[k] for k in ELEMENT_META_FIELDS if k in el}
            for fam in el["families"]:
                for t in fam["transitions"]:
                    records[t["id"]] = t
    dropped = sorted(set(snap["records"]) - set(records))
    assert not dropped, f"protected curated transitions dropped from live data: {dropped}"
    for tid, rec in snap["records"].items():
        assert records[tid] == rec, f"curated transition {tid} changed vs snapshot"
    meta_dropped = sorted(set(snap["element_meta"]) - set(meta))
    assert not meta_dropped, f"protected element meta dropped from live data: {meta_dropped}"
    for key, m in snap["element_meta"].items():
        assert meta[key] == m, f"element meta {key} (curation_status/notes) changed vs snapshot"
    for fn, payload in snap["legacy_payloads"].items():
        with open(os.path.join(DATA, "legacy", fn)) as f:
            live = {k: json.load(f)[k] for k in payload}
        assert live == payload, f"legacy {fn} scientific payload changed vs snapshot"


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


def test_prior_machine_records_unchanged_vs_snapshot():
    """Durable replacement for the old `..._vs_head` guard.

    'Prior' is defined by the committed machine_records_snapshot.json fixture —
    NOT by the moving git HEAD (reading HEAD reintroduced the moving-target bug
    the count guard already hit). Every machine record in the snapshot, including
    the four conflict records, must still be present and byte-identical in the
    live machine file; coverage expansion is purely additive. Curated + legacy
    scientific content is likewise frozen vs curated_records_snapshot.json.
    Both fixtures are the sole oracle, so the guard is independent of git state
    and working-tree cleanliness, and additive display fields don't trip it.
    """
    # Prior machine records — the fixture is the oracle.
    snap = json.load(open(MACHINE_SNAPSHOT))["records"]
    assert snap, "machine snapshot empty — regenerate from elements-machine.json"
    live = {tid: t for tid, (t, el) in _machine_by_id().items()}
    # the four conflict records are part of the protected baseline
    assert set(EXPECTED) <= set(snap), \
        "conflict records (Ti/Cr/Fe/P-2p3/2) missing from the machine snapshot baseline"
    dropped = sorted(set(snap) - set(live))
    assert not dropped, f"protected machine records dropped from live file: {dropped}"
    for tid, rec in snap.items():
        assert live[tid] == rec, f"prior machine record {tid} changed vs snapshot"

    # Curated + legacy scientific content — frozen vs the curated fixture.
    _assert_curated_and_legacy_match_snapshot()
