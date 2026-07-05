"""Unit R2 — element-coverage exhaustion certification.

The full-table NIST SRD-20 acquisition is COMPLETE: all 103 definitional
elements probed, 52 archivally recoverable (all recovered into the tiers),
51 structurally unrecoverable (no archive snapshot of either page format,
re-confirmed by a fresh re-probe on 2026-07-05; or an archived page with
no NIST-evaluated starred line). These pins certify the committed state
and keep the counts from drifting silently.

Always-on pins run against COMMITTED files only; the manifest-consistency
pin self-skips when the gitignored .stage9 working data is absent (CI),
following the established test_machine_tier pattern.
"""

import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data", "xps")
SUMMARY = os.path.join(REPO, "docs", "autofit", "inventory",
                       "acquisition_exhaustion.json")
MANIFEST = os.path.join(REPO, ".stage9", "expand_artifacts",
                        "acquire_manifest.json")


def _load(path):
    with open(path) as f:
        return json.load(f)


def test_committed_exhaustion_summary_counts():
    s = _load(SUMMARY)
    assert s["probed_element_count"] == 103        # full definitional table
    assert s["ok_count"] == 52
    assert s["failed_count"] == 51
    assert s["ok_count"] + s["failed_count"] == s["probed_element_count"]
    reasons = set(s["failed_by_reason"])
    # ONLY the two structural reasons — anything else means an unhandled
    # failure class snuck in (e.g. a transient error mistaken for absence)
    assert reasons <= {"no-archive-snapshot", "artifact-has-no-starred-value"}
    assert len(s["failed_by_reason"]["no-archive-snapshot"]) == 24
    assert len(s["failed_by_reason"]["artifact-has-no-starred-value"]) == 27


def test_machine_tier_counts_and_provenance_coverage():
    """51 elements / 78 transitions in the machine tier; every transition
    has exactly one provenance record carrying the full chain."""
    machine = _load(os.path.join(DATA, "elements-machine.json"))["elements"]
    assert len(machine) == 51
    tids = [t["id"] for e in machine for f in e["families"]
            for t in f["transitions"]]
    assert len(tids) == 78 and len(set(tids)) == 78
    prov = _load(os.path.join(DATA, "elements-machine.provenance.json"))
    recs = {p["id"]: p for p in prov["transitions"]}
    assert set(recs) == set(tids)
    for tid in tids:
        ns = recs[tid]["nominal_source"]
        assert ns["evaluated"] is True
        assert len(ns["source_artifact_sha256"]) == 64
        assert ns["source_url"].startswith("http")
        assert ns["nist_reference_code"]


def test_every_machine_element_is_manifest_ok():
    """Manifest ↔ committed-tier consistency (env-gated: needs the
    gitignored .stage9 manifest)."""
    if not os.path.exists(MANIFEST):
        pytest.skip("gitignored .stage9 acquisition manifest not present")
    man = {m["symbol"]: m for m in _load(MANIFEST)["elements"]}
    s = _load(SUMMARY)
    # committed summary is exactly the deterministic regeneration
    import subprocess
    import sys
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "summarize_acquisition",
        os.path.join(REPO, "scripts", "summarize_acquisition.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    regen = mod.build()
    assert regen == s, "committed summary != deterministic regeneration"
    # EVERY committed machine element must have a manifest row AND be OK —
    # a missing row must fail, not silently pass (Codex R2 review, run A
    # MAJOR: a hand-edited element with plausible provenance but no
    # manifest row previously slipped this certification)
    machine = _load(os.path.join(DATA, "elements-machine.json"))["elements"]
    for e in machine:
        m = man.get(e["symbol"])
        assert m is not None, (
            f"{e['symbol']}: committed machine element has NO manifest "
            "row — where did it come from?")
        assert m["status"] == "OK", (
            f"{e['symbol']}: committed machine element but manifest "
            f"status {m['status']}")


def test_no_snapshot_elements_absent_from_machine_tier():
    """The 24 archive-dark elements must have NO machine-tier positions —
    that tier is DEFINED as archive-derived, so a dark element appearing
    there means an invented value. (Curated tiers are deliberately NOT
    pinned here: they draw on independent cited sources, so Skye can
    legitimately hand-curate a dark element from a handbook later.)"""
    s = _load(SUMMARY)
    dark = {r["symbol"] for r in s["failed_by_reason"]["no-archive-snapshot"]}
    machine = {e["symbol"] for e in
               _load(os.path.join(DATA, "elements-machine.json"))["elements"]}
    overlap = dark & machine
    assert not overlap, (
        f"elements-machine.json: {overlap} committed despite no archived "
        "source — where did those values come from?")
