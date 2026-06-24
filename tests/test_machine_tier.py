"""Phase B machine-tier invariants — the no-invention rules are HARD tests.

Two layers, per the deploy constraint:
  * committed-only invariants always run (they verify elements-machine.json
    against its committed provenance sidecar + the curated/legacy files);
  * .stage9-gated invariants (reproducibility, agreed-set membership) skip
    cleanly when the gitignored working data is absent (e.g. a fresh clone).
"""
import importlib.util
import json
import os
import subprocess

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data", "xps")
STAGE9 = os.path.join(REPO, ".stage9")


def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


MACHINE = _load("elements-machine.json")
PROV = _load("elements-machine.provenance.json")
SKIPPED = _load("elements-machine.skipped.json")


def _machine_transitions():
    return [t for el in MACHINE["elements"] for fam in el["families"] for t in fam["transitions"]]


PROV_BY_ID = {p["id"]: p for p in PROV["transitions"]}


def _is_expansion(tid):
    # Coverage-expansion records carry an "acquisition" provenance key and are
    # corroborated by artifact-literal + agent cross-check, not the Stage-9
    # dual-extraction agreed-set; the tiers-backed invariants don't apply to them.
    return bool(PROV_BY_ID.get(tid, {}).get("acquisition"))


# ── committed-only invariants ────────────────────────────────────────────────

def test_no_spin_orbit_emitted():
    for t in _machine_transitions():
        assert t["spin_orbit"] is None, t["id"]


VALID_BASES = {"observed-reference-range", "reduced-to-oxidized-chemical-state-span"}


def test_region_basis_order_and_nominal_within():
    for t in _machine_transitions():
        r = t["expected_region_ev"]
        assert r["basis"] in VALID_BASES, t["id"]
        assert r["min"] <= r["max"], t["id"]
        assert r["min"] <= t["nominal_be_ev"] <= r["max"], t["id"]   # nominal is a sourced value


def test_every_transition_is_machine_tier():
    for t in _machine_transitions():
        assert t["tier"] == "machine"
        assert t["transition_type"] == "photoelectron"
        assert t["source"] == "nist-srd-20"
        assert t["visibility"]["AlKa"] == "machine-unassessed"
    for el in MACHINE["elements"]:
        assert el["curation_status"] == "machine"


def test_nominal_matches_committed_provenance():
    # Reproducibility layer 2: every emitted value is verifiable from the
    # committed provenance manifest (independent of the gitignored .stage9).
    prov = PROV_BY_ID
    emitted_ids = set()
    for t in _machine_transitions():
        emitted_ids.add(t["id"])
        p = prov[t["id"]]
        assert p["nominal_be_ev"] == t["nominal_be_ev"], t["id"]
        assert p["nominal_source"]["evaluated"] is True            # NIST-evaluated (starred)
        assert p["tier"] == "machine"
        assert p["nominal_source"]["nist_reference_code"]
        assert len(p["nominal_source"]["source_artifact_sha256"]) == 64
        assert p["parse_method"] == "nist-html-starred-record"
        assert p["expected_region_ev"]["min"] == t["expected_region_ev"]["min"]
        assert p["expected_region_ev"]["max"] == t["expected_region_ev"]["max"]
        if _is_expansion(t["id"]):
            # coverage-expansion: single-snapshot, NOT Stage-9 dual extraction
            assert p["dual_extraction_corroborated"] is False
            assert p["nominal_source"]["archive_snapshot_timestamp"]
        else:
            assert p["dual_extraction_corroborated"] is True       # Stage-9 dual-extraction
    assert emitted_ids == set(prov)                  # provenance covers exactly the emitted set


def test_html_only_recoveries_flagged():
    html_only = {p["id"] for p in PROV["transitions"] if p.get("html_only_recovery")}
    assert html_only == {"Ag-3d5/2", "Pt-4f7/2"}     # the digest-truncated evaluated records


def test_additive_only_no_curated_overlap():
    curated = set()
    for fn in ("elements-main.json", "elements-actinides.json",
               "elements-lanthanides.json", "auger-lines.json"):
        for el in _load(fn)["elements"]:
            for fam in el["families"]:
                for t in fam["transitions"]:
                    curated.add((el["symbol"], t["orbital"]))
    for t in _machine_transitions():
        assert (t["element"], t["orbital"]) not in curated, t["id"]


def test_curated_and_legacy_byte_unchanged():
    # The generator writes only the three machine sidecars; curated + legacy
    # files are untouched (verified against git HEAD).
    paths = ["data/xps/elements-main.json", "data/xps/elements-actinides.json",
             "data/xps/elements-lanthanides.json", "data/xps/auger-lines.json",
             "data/xps/legacy"]
    r = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "HEAD", "--"] + paths)
    if r.returncode not in (0, 1):
        pytest.skip("git unavailable / no HEAD")
    assert r.returncode == 0, "curated/legacy files differ from HEAD — must stay byte-unchanged"


# ── .stage9-gated invariants ─────────────────────────────────────────────────

_HAVE_STAGE9 = os.path.exists(os.path.join(STAGE9, "manifest", "tiers_survey.json"))
stage9 = pytest.mark.skipif(not _HAVE_STAGE9, reason=".stage9 working data absent")


def _gen_module():
    spec = importlib.util.spec_from_file_location(
        "gen_machine_tier", os.path.join(REPO, "scripts", "gen_machine_tier.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tiers_by_el_line():
    tiers = json.load(open(os.path.join(STAGE9, "manifest", "tiers_survey.json")))
    obs = {o["field_id"]: o for o in
           json.load(open(os.path.join(STAGE9, "extract_claude", "observations_4a.json")))["observations"]}
    return {(r["element"], obs.get(r["field_id"], {}).get("nist_line")): r for r in tiers}


@stage9
def test_deterministic_reproducible_from_stage9():
    mod = _gen_module()
    m, p, s = mod.build()
    assert mod.serialize(m) == open(os.path.join(DATA, "elements-machine.json")).read()
    assert mod.serialize(p) == open(os.path.join(DATA, "elements-machine.provenance.json")).read()
    assert mod.serialize(s) == open(os.path.join(DATA, "elements-machine.skipped.json")).read()


@stage9
def test_every_nominal_present_in_agreed_set():
    tl = _tiers_by_el_line()
    for t in _machine_transitions():
        if _is_expansion(t["id"]):
            continue                       # expansion records are artifact-backed, not tiers-backed
        r = tl[(t["element"], t["orbital"])]
        assert any(abs(t["nominal_be_ev"] - a) < 1e-6 for a in r["agreed_values"]), t["id"]


@stage9
def test_region_endpoints_are_agreed_minmax():
    tl = _tiers_by_el_line()
    for t in _machine_transitions():
        if _is_expansion(t["id"]):
            continue                       # expansion region is from the artifact, not the agreed-set
        agreed = tl[(t["element"], t["orbital"])]["agreed_values"]
        r = t["expected_region_ev"]
        # observed-reference-range: min..max of the agreed-set. Conflict-resolution
        # (reduced-to-oxidized) records keep min == reduced-cluster min but extend
        # max up to the (non-agreed) legacy oxidized value, so only min is bounded
        # by the agreed-set there.
        assert r["min"] == min(agreed), t["id"]
        if r["basis"] == "observed-reference-range":
            assert r["max"] == max(agreed), t["id"]
        else:
            assert r["max"] > max(agreed), t["id"]   # extends past the reduced cluster


@stage9
def test_only_corroborated_or_allowlisted_conflict_emitted():
    # Insufficient-evidence is NEVER emitted; conflict is emitted ONLY for the
    # explicit conflict-resolution allowlist.
    allow = set(_gen_module().CONFLICT_RESOLUTIONS)
    tl = _tiers_by_el_line()
    for t in _machine_transitions():
        if _is_expansion(t["id"]):
            continue                       # expansion records aren't in the Stage-9 tiers manifest
        key = (t["element"], t["orbital"])
        tier = tl[key]["tier"]
        if tier == "conflict":
            assert key in allow, f"{t['id']} is a conflict but not in the allowlist"
        else:
            assert tier == "transcription-corroborated", t["id"]


@stage9
def test_emitted_count_matches_eligible_sanity():
    assert len(_machine_transitions()) == 45   # 23 corroborated + 4 conflict-resolved + 18 coverage-expansion
