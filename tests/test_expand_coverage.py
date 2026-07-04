"""Coverage-expansion invariants (Sc/Ru/Pd/Hf/Ta/Re/Os/Ir/Hg/Tl machine records).

The CORE PRINCIPLE is a HARD test here: every emitted value must literally appear
as a NIST-evaluated (starred) record in its COMMITTED source artifact. Nothing
from memory. These tests read only committed data (the three machine JSON files +
the committed .stage9/expand_artifacts/*.html), so they run anywhere.
"""
import hashlib
import importlib.util
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data", "xps")
ART = os.path.join(REPO, ".stage9", "expand_artifacts")
SNAPSHOT = os.path.join(REPO, "tests", "fixtures", "machine_records_snapshot.json")

MACHINE = json.load(open(os.path.join(DATA, "elements-machine.json")))
PROV = {p["id"]: p for p in json.load(open(os.path.join(DATA, "elements-machine.provenance.json")))["transitions"]}
SKIPPED = json.load(open(os.path.join(DATA, "elements-machine.skipped.json")))

# The 18 emitted expansion values (also asserted to be literally present in artifacts).
EXPANSION = {
    "Sc-2p3/2": 398.53, "Ru-3d5/2": 280.08, "Ru-4p3/2": 43.37, "Pd-3d5/2": 335.12,
    "Hf-4d5/2": 211.5, "Hf-4f7/2": 14.31, "Ta-4d5/2": 226.4, "Ta-4f7/2": 21.83,
    "Re-4d5/2": 260.5, "Re-4f7/2": 40.34, "Os-4d5/2": 278.51, "Os-4f7/2": 50.69,
    "Ir-4d5/2": 296.31, "Ir-4f7/2": 60.84, "Hg-4d5/2": 359.32, "Hg-4f7/2": 99.85,
    "Tl-4d5/2": 385.02, "Tl-4f7/2": 117.73,
}
FAILED_ELEMENTS = {"Rb", "Cs"}   # artifact fetched but no NIST-evaluated value


def _machine_by_id():
    return {t["id"]: (t, el) for el in MACHINE["elements"]
            for f in el["families"] for t in f["transitions"]}


def _independent_starred(raw_bytes, orbital):
    """Independent raw-HTML extraction of starred energies for a spectral line —
    deliberately NOT gen_machine_tier.parse_nist_html (uses <tr>/<td> splitting,
    not the headers="t1..t4" regex), so a shared-parser bug cannot mask a value."""
    import re
    text = raw_bytes.decode("latin-1", "replace")
    out = []
    for row in re.split(r"(?i)<tr", text):
        cells = re.findall(r"(?is)<td[^>]*>(.*?)</td>", row)
        if len(cells) < 4:
            continue
        strip = lambda c: re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip()
        if strip(cells[1]) != orbital:
            continue
        if not re.search(r"(?i)<b>\s*\*\s*</b>", cells[3]):   # NIST-evaluated marker
            continue
        try:
            out.append(float(strip(cells[2])))
        except ValueError:
            pass
    return out


def test_expansion_records_emitted_at_machine_tier():
    by_id = _machine_by_id()
    for tid, nom in EXPANSION.items():
        assert tid in by_id, f"{tid} missing from machine tier"
        t, el = by_id[tid]
        assert t["tier"] == "machine" and t["transition_type"] == "photoelectron"
        assert t["nominal_be_ev"] == nom
        assert t["spin_orbit"] is None
        assert t["visibility"]["AlKa"] == "machine-unassessed"
        assert el["curation_status"] == "machine"
        r = t["expected_region_ev"]
        assert r["min"] <= t["nominal_be_ev"] <= r["max"]


def test_every_emitted_value_literally_in_committed_artifact():
    # The anti-confabulation invariant, verified WITHOUT the committed parser:
    #   (a) an independent raw-HTML parse finds the value as a starred record,
    #   (b) the independent second-agent cross-check agrees, and
    #   (c) the provenance sha256 matches the committed artifact bytes.
    agent = json.load(open(os.path.join(ART, "agent_crosscheck.json")))
    for tid, nom in EXPANSION.items():
        sym, orbital = tid.split("-", 1)
        art = os.path.join(ART, f"{sym}_nist.html")
        assert os.path.exists(art), f"committed artifact missing: {sym}_nist.html"
        raw = open(art, "rb").read()
        starred = _independent_starred(raw, orbital)            # (a) independent parser
        assert any(abs(v - nom) < 1e-9 for v in starred), \
            f"{tid}={nom} not a starred {orbital} record (independent raw-HTML parse)"
        assert tid in agent and abs(agent[tid] - nom) < 1e-9, \
            f"{tid} disagrees with independent agent cross-check"   # (b)
        assert PROV[tid]["nominal_source"]["source_artifact_sha256"] == hashlib.sha256(raw).hexdigest()  # (c)


def test_expansion_provenance_complete():
    for tid in EXPANSION:
        p = PROV[tid]
        ns = p["nominal_source"]
        assert ns["database"] == "nist-srd-20"
        assert ns["evaluated"] is True
        assert ns["nist_reference_code"]
        assert ns["source_url"].startswith("https://web.archive.org/")
        assert ns["archive_snapshot_timestamp"] and ns["fetch_utc"]
        assert len(ns["source_artifact_sha256"]) == 64
        assert p["parse_method"] == "nist-html-starred-record"
        assert p["acquisition"].startswith("coverage-expansion")
        assert p["dual_extraction_corroborated"] is False   # honest: single snapshot, not Stage-9 dual
        assert p["agent_cross_checked"] is True             # independent re-derivation confirmed it


def test_rb_cs_failed_not_emitted():
    by_id = _machine_by_id()
    for sym in FAILED_ELEMENTS:
        assert not any(tid.split("-")[0] == sym for tid in by_id), f"{sym} must not be emitted"
    skipped_failed = {t["element"] for t in SKIPPED["transitions"] if t["reason"] == "no-evaluated-value"}
    assert FAILED_ELEMENTS <= skipped_failed


def test_machine_count_is_78():
    # 27 tiers-driven + 51 coverage-expansion (18 original EXPANSION set +
    # 33 full-table sweep 2026-07-03, each agent-cross-checked)
    assert len(_machine_by_id()) == 78


def test_existing_machine_records_byte_unchanged_vs_snapshot():
    """Every machine record captured in the committed snapshot must still be
    present and structurally identical in the live machine file — a guard
    against silent mutation of already-shipped NIST reference energies.

    Durable across coverage expansions: this compares against a committed
    fixture (tests/fixtures/machine_records_snapshot.json), NOT a hard-coded
    record count and NOT the moving git HEAD (which made the old
    "prior 27" guard self-contradict once the expansion was merged). Records
    added by a later expansion are simply absent from the snapshot, so they
    neither break this guard nor are protected by it until the baseline is
    intentionally regenerated — see the fixture's "description" for the
    regeneration command and policy.
    """
    snap = json.load(open(SNAPSHOT))
    baseline = snap["records"]
    assert baseline, "snapshot has no records — regenerate it from the machine file"
    live = {tid: t for tid, (t, el) in _machine_by_id().items()}
    dropped = sorted(set(baseline) - set(live))
    assert not dropped, f"protected machine records dropped from the live file: {dropped}"
    for tid, rec in baseline.items():
        assert live[tid] == rec, f"machine record {tid} changed vs the protected snapshot"
