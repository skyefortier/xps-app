"""Unit R3 — chemical-state tier: integrity pins + the sourced-or-skip
audit outcome.

Oxidation-state BEs are the highest confabulation risk, so the rail is
sourced-or-skip. The 2026-07-05 audit of every candidate source found NO
cleanly-sourceable extension:

1. The frontend's embedded CHEMICAL_STATES constant — the origin of the
   original 11-group/52-state tier — was FULLY transcribed (dual
   extraction, 4a/4b) and then REMOVED from the template. Source
   exhausted.
2. The archived NIST element pages (query_all_dat_el.asp) carry no
   chemical-state class — the standing gen_machine_tier
   "context-undeterminable" skip reason.
3. The archived NIST compound pages (elm_in_comp_res.asp) DO exist and
   were summarized during Stage 9 (.stage9/extract_chem_*/groups_4*.json)
   — but the summaries carry per-compound BEs with NO per-row reference
   codes, NO evaluated-star markers, and NO retained raw artifacts, so
   emitting from them would violate the tier's own per-state ref
   contract. A future pipeline (re-fetch, sha-pin, per-row ref recovery,
   plus Skye's editorial condensation rules for which compound rows
   constitute a "state") is the documented path — logged, not executed.

The tier therefore stays at 11 groups / 51 states (see the disclosed
deviation below — one state was intentionally removed from the original
52-state transcription). That is the correct outcome, not a failure.

DISCLOSED DEVIATION (2026-07-16, provenance audit): the U 4f7/2 group's
UCl₄/380.2 eV state (id legacy-cs-U-4f72-4) carried `"ref": "Fortier
2026"` — a literal self-citation, not an external literature source.
Removed entirely (Skye's call: delete rather than restructure). This is
the ONE intentional content deviation from the original transcribed
constant (52 states -> 51); see test_no_self_citation_in_any_ref_string
below and tests/test_legacy_parity.py.
"""

import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEM = os.path.join(REPO, "data", "xps", "legacy", "chemical-states.json")
STAGE9 = os.path.join(REPO, ".stage9")


def _load(path):
    with open(path) as f:
        return json.load(f)


def test_every_chem_state_carries_ref_source_tier():
    """The goal-prescribed pin: every emitted chemical state carries
    ref + source; none without provenance."""
    doc = _load(CHEM)
    assert doc["curation_status"] == "legacy-unverified"
    assert doc["source"] == "legacy-embedded-dataset"
    assert doc["content_sha256"]
    states = [s for g in doc["groups"] for s in g["states"]]
    assert len(doc["groups"]) == 11
    assert len(states) == 51
    for s in states:
        assert s["ref"] and isinstance(s["ref"], str), f"{s['id']}: no ref"
        assert s["source"] == "legacy-embedded-dataset"
        assert s["tier"] == "legacy-unverified"
        assert isinstance(s["be_ev"], (int, float)) and 0 < s["be_ev"] < 1500
    assert len({s["id"] for s in states}) == 51     # ids unique


def test_transcription_source_removed_from_frontend():
    """The tier's origin (the embedded frontend constant) was fully
    transcribed and REMOVED — pin the removal so a resurrected constant
    (a second, diverging copy of chem-state values) is caught."""
    html = open(os.path.join(REPO, "templates", "index.html")).read()
    assert "CHEMICAL_STATES constants have been REMOVED" in html
    # no live constant definition may reappear
    assert "CHEMICAL_STATES = {" not in html
    assert "CHEMICAL_STATES={" not in html


def test_compound_page_summaries_are_not_emittable():
    """The Stage-9 compound-page summaries (the only other sourced
    avenue) lack per-row refs — pin WHY they are skip-classified, so a
    future 'helpful' emission from them fails a test instead of shipping
    uncited values. Env-gated on the gitignored .stage9 data."""
    # BOTH extraction paths (4a claude + 4b codex — Codex R3 review, both
    # runs MINOR: watching only 4a would miss a 4b rerun gaining refs)
    checked_any = False
    for d, fname in (("extract_chem_claude", "groups_4a.json"),
                     ("extract_chem_codex", "groups_4b.json")):
        p = os.path.join(STAGE9, d, fname)
        if not os.path.exists(p):
            continue
        checked_any = True
        groups = _load(p)
        groups = groups.get("groups", groups)
        assert groups, f"{fname} present but empty"
        for g in groups:
            for row in g.get("compound_bes", []):
                assert "ref" not in row and "evaluated" not in row, (
                    f"{fname} {g['element']} {g['orbital']}: compound row "
                    "carries ref/evaluated fields — the not-emittable "
                    "classification may be stale; re-audit R3")
        # raw compound-page artifacts were NOT retained (no sha chain)
        arts = [f for f in os.listdir(os.path.join(STAGE9, d))
                if f.endswith(".html")]
        assert arts == [], (
            f"{d}: raw compound-page artifacts present — the "
            "future-pipeline preconditions may now hold; re-audit R3")
    if not checked_any:
        pytest.skip("gitignored .stage9 working data not present")


def test_chem_states_flow_through_bridge_with_provenance():
    """End-to-end: the tier reaches the autofit bridge with per-state
    ref/source intact and UNVERIFIED status (unit R1 integration)."""
    from autofit import reference_bridge as rb
    doc = _load(CHEM)
    for grp in doc["groups"]:
        sub = grp["orbital"][:2]
        ref = rb.level_reference(grp["element"], sub)
        assert len(ref["chemical_states"]) == len(grp["states"])
        for s in ref["chemical_states"]:
            assert s["ref"] and s["source"] and s["status"] == "UNVERIFIED"


def test_no_self_citation_in_any_ref_string():
    """Provenance audit (2026-07-16): 'ref' strings must cite an external
    literature source, never the lab itself. The legacy U 4f7/2 UCl4 entry
    (id legacy-cs-U-4f72-4) previously carried ``"ref": "Fortier 2026"`` —
    a literal self-citation dressed up as a source, indistinguishable from
    a real literature reference to anyone reading the tooltip. Removed
    entirely (Skye's explicit call: delete rather than restructure) — the
    tier is now 11 groups / 51 states. Pin the absence going forward so a
    future legacy-data edit can't silently reintroduce a self-citation.

    COMPLETE accounting of every remaining occurrence of the literal
    self-citation string "Fortier 2026" in tracked .json/.js/.py files as
    of this fix (verified via ``git grep -n "Fortier 2026" -- '*.json'
    '*.js' '*.py'`` — NOT the plain shell ``grep`` alias in this
    environment, which silently respects .gitignore and hides
    gitignored-but-tracked files). This does NOT cover every bare mention
    of the surname "Fortier" anywhere in the repo (e.g. ordinary "Fortier
    Lab" mentions in docs/superpowers/plans/*.md planning notes) — those
    are not citations and are out of scope for this audit:

    - .stage9/extract_targets_chem.json, .stage9/phase4chem_workflow.js,
      .stage9/manifest/manifest.json — the original Stage-9 dual-
      extraction transcription inputs/build-manifest, proving the
      transcription faithfully captured what was really in the old
      embedded JS constant at the time. None are loaded by any runtime
      code (app.py / xps_reference.py / autofit / fitting.py). Retaining
      them verbatim, self-citation included, is deliberate: they are
      historical evidence of what WAS transcribed, and editing them would
      rewrite that evidence — the opposite of honest. (manifest.json is
      additionally covered by .stage9/.gitignore for NEW writes, but was
      tracked before that rule existed.)
    - data/xps/elements-main.json and tests/fixtures/curated_records_
      snapshot.json — the C 1s notes field's "curator decision, S.
      Fortier 2026-06" is an editorial-decision ATTRIBUTION (who decided
      to prioritize 284.5 over 284.44), not a literature citation dressed
      up as one — a different provenance-audit unit's scope, tracked
      separately.
    """
    doc = _load(CHEM)
    for g in doc["groups"]:
        for s in g["states"]:
            assert "fortier" not in s["ref"].lower(), (
                f"{s['id']}: self-citation in ref field ({s['ref']!r})")
