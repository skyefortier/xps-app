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

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data", "xps")
STAGE9 = os.path.join(REPO, ".stage9")
CURATED_SNAPSHOT = os.path.join(REPO, "tests", "fixtures", "curated_records_snapshot.json")

# Curated photoelectron + auger files, and the scientific element-level fields
# the byte-diff guard used to protect. Additive display fields (short_caveat) and
# the families array are deliberately NOT here — see curated_records_snapshot.json.
CURATED_FILES = ("elements-main.json", "elements-actinides.json",
                 "elements-lanthanides.json", "auger-lines.json")
ELEMENT_META_FIELDS = ("symbol", "z", "name", "curation_status", "curation_notes")
LEGACY_PAYLOADS = {"survey-lines.json": "elements",
                   "chemical-states.json": "groups",
                   "corrections.json": "crossrefs"}


def _live_curated_records_and_meta():
    """Extract live curated transitions (whole, by id) + per-element scientific
    meta (allowlisted fields only, so short_caveat/families don't participate)."""
    records, meta = {}, {}
    for fn in CURATED_FILES:
        for el in _load(fn)["elements"]:
            meta[f"{fn}:{el['symbol']}"] = {k: el[k] for k in ELEMENT_META_FIELDS if k in el}
            for fam in el["families"]:
                for t in fam["transitions"]:
                    records[t["id"]] = t
    return records, meta


def _live_legacy_payloads():
    out = {}
    for fn, key in LEGACY_PAYLOADS.items():
        with open(os.path.join(DATA, "legacy", fn)) as f:
            out[fn] = {key: json.load(f)[key]}
    return out


def assert_curated_and_legacy_match_snapshot():
    """Shared durable check: every curated transition, element meta entry, and
    legacy payload in curated_records_snapshot.json is still present and
    structurally identical in the live data. The fixture is the SOLE oracle —
    no git/HEAD is consulted, so working-tree cleanliness is irrelevant; and
    additive display fields (short_caveat) are excluded, so they never trip it.
    A mutated value/region/tier/curation_notes/source IS caught."""
    snap = json.load(open(CURATED_SNAPSHOT))
    assert snap["records"], "snapshot has no curated records — regenerate from data"
    live_records, live_meta = _live_curated_records_and_meta()

    dropped = sorted(set(snap["records"]) - set(live_records))
    assert not dropped, f"protected curated transitions dropped from live data: {dropped}"
    for tid, rec in snap["records"].items():
        assert live_records[tid] == rec, f"curated transition {tid} changed vs snapshot"

    meta_dropped = sorted(set(snap["element_meta"]) - set(live_meta))
    assert not meta_dropped, f"protected element meta dropped from live data: {meta_dropped}"
    for key, m in snap["element_meta"].items():
        assert live_meta[key] == m, f"element meta {key} (curation_status/notes) changed vs snapshot"

    live_legacy = _live_legacy_payloads()
    for fn, payload in snap["legacy_payloads"].items():
        assert live_legacy[fn] == payload, f"legacy {fn} scientific payload changed vs snapshot"


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


def _subshell(orbital):
    import re
    m = re.match(r"^([1-7][spdf])", orbital)
    return m.group(1) if m else orbital


def test_no_curated_subshell_overlap():
    """Stronger additive-only invariant (broad-coverage expansion): a machine
    transition may not even share an (element, subshell) with the curated
    tiers — prevents a bare '2p' machine line shadowing a curated '2p3/2'."""
    curated_sub = set()
    for fn in ("elements-main.json", "elements-actinides.json",
               "elements-lanthanides.json", "auger-lines.json"):
        for el in _load(fn)["elements"]:
            for fam in el["families"]:
                for t in fam["transitions"]:
                    curated_sub.add((el["symbol"], _subshell(t["orbital"])))
    for t in _machine_transitions():
        assert (t["element"], _subshell(t["orbital"])) not in curated_sub, t["id"]


def test_machine_tier_no_internal_duplicates():
    """One machine record per (element, orbital) — the tiers path and the
    coverage-expansion path must never both emit the same line."""
    seen = set()
    for t in _machine_transitions():
        key = (t["element"], t["orbital"])
        assert key not in seen, f"duplicate machine emission {t['id']}"
        seen.add(key)


def test_machine_tier_no_internal_subshell_overlap():
    """Stronger machine-internal invariant (Codex Stage-6 blocker #2): the
    two emission paths must not even share an (element, subshell) — a bare
    '3p' expansion line must never coexist with a tiers-driven '3p3/2'."""
    seen = {}
    for t in _machine_transitions():
        key = (t["element"], _subshell(t["orbital"]))
        assert key not in seen, (
            f"machine-internal subshell overlap: {t['id']} vs {seen[key]}")
        seen[key] = t["id"]


def test_skip_reasons_enumerated():
    """Every skip reason used in the audit log is documented in the reasons
    legend (no unexplained skip categories)."""
    legend = set(SKIPPED["reasons"])
    used = {r["reason"] for r in SKIPPED["transitions"]}
    assert used <= legend, f"undocumented skip reasons: {sorted(used - legend)}"


def test_expansion_provenance_source_is_nist_archive():
    """Coverage-expansion values must be traceable to an Internet Archive
    snapshot of the retired NIST SRD-20 query page: strict archived-URL
    shape, snapshot timestamp consistent with the URL, artifact bytes
    matching the recorded sha256, the committed parse method (Codex
    Stage-6 MAJOR: substring checks were too loose and bytes unverified)."""
    import hashlib
    import re as _re
    url_re = _re.compile(
        r"^https?://web\.archive\.org/web/(\d{14})id_/"
        r"https?://srdata\.nist\.gov(:80)?/xps/query_all_dat_el\.aspx?"
        r"\?elm1=([A-Z][a-z]?)$")
    art_dir = os.path.join(STAGE9, "expand_artifacts")
    for p in PROV["transitions"]:
        if not p.get("acquisition"):
            continue
        ns = p["nominal_source"]
        m = url_re.match(ns["source_url"])
        assert m, f"{p['id']}: malformed archive URL {ns['source_url']}"
        assert m.group(1) == ns["archive_snapshot_timestamp"], (
            f"{p['id']}: URL timestamp {m.group(1)} != recorded "
            f"{ns['archive_snapshot_timestamp']}")
        assert m.group(3) == p["element"], (
            f"{p['id']}: archive URL queries {m.group(3)}, not {p['element']}")
        assert ns["fetch_utc"], p["id"]
        art = os.path.join(art_dir, ns["source_artifact"])
        assert os.path.exists(art), f"{p['id']}: tracked artifact missing"
        got = hashlib.sha256(open(art, "rb").read()).hexdigest()
        assert got == ns["source_artifact_sha256"], (
            f"{p['id']}: artifact bytes do not match recorded sha256")
        assert p["parse_method"] == "nist-html-starred-record", p["id"]


def test_expansion_values_agent_cross_checked():
    """Single-snapshot expansion values are only as strong as their
    independent re-derivation: every acquisition record must carry a
    confirmed agent cross-check."""
    for p in PROV["transitions"]:
        if p.get("acquisition"):
            assert p.get("agent_cross_checked") is True, p["id"]


def test_curated_and_legacy_content_unchanged_vs_snapshot():
    # The machine-tier generator writes only the three machine sidecars; curated
    # + legacy scientific content stays put. Durable replacement for the old
    # whole-file `git diff --quiet HEAD` guard, which went spuriously RED on any
    # uncommitted edit and false-failed the additive short_caveat work. The
    # committed fixture — not git/HEAD — is the oracle, and only scientific
    # fields are compared, so additive display fields don't trip it.
    assert_curated_and_legacy_match_snapshot()


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
    assert len(_machine_transitions()) == 78   # 23 corroborated + 4 conflict-resolved + 51 coverage-expansion (full-table sweep 2026-07-03)
