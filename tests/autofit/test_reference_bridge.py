"""Unit R1 — the data/xps → autofit reference bridge.

Marries coverage.py's DERIVED STRUCTURE (levels, doublets, ratio
expectations, flags) with the committed data/xps tiers' SOURCED POSITIONS
(curated / machine / legacy survey + chemical states), loaded through the
same xps_reference loader that serves /api/xps-reference (so its
validation contract rides along) and joined with the machine tier's
provenance sidecar (NIST reference code, source URL, artifact sha256).

ANTI-INVENTION CONTRACT: the bridge emits NOTHING not present in
data/xps. These tests never hardcode a binding energy — every expected
value is read programmatically from the committed data files and compared
against the bridge output, so no number in this test source originates
from model memory.

Tier → status mapping (goal-prescribed; deviation from fit_physics.py's
older machine→UNVERIFIED exposure mapping is documented in PROGRESS.md
for review): curated → VERIFIED (curator-verified against cited sources,
still user-confirmable), machine → CONDITIONAL (sourced, sha-pinned,
NOT human-verified), legacy → UNVERIFIED.
"""

from __future__ import annotations

import json
import os

import pytest

from autofit import reference_bridge as rb
from autofit.grammar import MaterialClass, Phase, resolve

DATA = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), "data", "xps")


def _load(fname):
    with open(os.path.join(DATA, fname)) as f:
        return json.load(f)


def test_machine_tier_element_positions_conditional_with_provenance():
    """Goal-prescribed test: a machine-tier element (Ti) returns sourced
    positions + CONDITIONAL + the full provenance chain."""
    ref = rb.level_reference("Ti", "2p")
    assert ref["structure"]["structure"] == "doublet"     # from coverage.py
    assert ref["positions"], "Ti 2p must have machine-tier positions"

    machine = _load("elements-machine.json")
    ti = next(e for e in machine["elements"] if e["symbol"] == "Ti")
    file_by_orbital = {t["orbital"]: t for fam in ti["families"]
                       for t in fam["transitions"]}
    sidecar = {p["id"]: p for p in
               _load("elements-machine.provenance.json")["transitions"]}

    machine_pos = [p for p in ref["positions"] if p["tier"] == "machine"]
    assert machine_pos, "Ti 2p must include machine-tier positions"
    # Ti also carries a legacy survey marker — both tiers ride, each with
    # its own status; nothing is merged or preferred silently
    assert all(p["status"] == "UNVERIFIED" for p in ref["positions"]
               if p["tier"] == "legacy")
    for pos in machine_pos:
        assert pos["status"] == "CONDITIONAL"
        ft = file_by_orbital[pos["orbital"]]
        # the emitted value IS the committed file's value — nothing else
        assert pos["nominal_be_ev"] == ft["nominal_be_ev"]
        assert pos["expected_region_ev"]["min"] == ft["expected_region_ev"]["min"]
        assert pos["expected_region_ev"]["max"] == ft["expected_region_ev"]["max"]
        # provenance chain joined from the sidecar
        sc = sidecar[ft["id"]]
        assert pos["provenance"]["source_artifact_sha256"] == \
            sc["nominal_source"]["source_artifact_sha256"]
        assert pos["provenance"]["nist_reference_code"] == \
            sc["nominal_source"]["nist_reference_code"]
        assert pos["provenance"]["evaluated"] is True
        # the not-human-verified caveat must ride along
        assert "not human-verified" in pos["notes"].lower()


def test_curated_tier_element_verified_with_citation():
    """Curated positions (e.g. Nb) map to VERIFIED and their source id
    resolves to a citation in sources.json."""
    curated_syms = {e["symbol"] for e in _load("elements-main.json")["elements"]}
    sym = "Nb" if "Nb" in curated_syms else sorted(curated_syms)[0]
    st = None
    for fam in next(e for e in _load("elements-main.json")["elements"]
                    if e["symbol"] == sym)["families"]:
        st = fam["family"]
        break
    ref = rb.level_reference(sym, st)
    curated_pos = [p for p in ref["positions"] if p["tier"] == "curated"]
    assert curated_pos
    sources = _load("sources.json")["sources"]
    for pos in curated_pos:
        assert pos["status"] == "VERIFIED"
        assert pos["source_id"] in sources
        assert len(pos["citation"]) >= 8            # loader-validated shape


def test_legacy_survey_positions_unverified():
    """Legacy survey lines surface as UNVERIFIED positions with their
    legacy source marker (committed, loader-validated data — exposed,
    never upgraded)."""
    survey = _load(os.path.join("legacy", "survey-lines.json"))
    # pick a survey element with no curated/machine coverage of that line
    machine_syms = {e["symbol"] for e in _load("elements-machine.json")["elements"]}
    curated_syms = {e["symbol"] for e in _load("elements-main.json")["elements"]}
    el = next(e for e in survey["elements"]
              if e["symbol"] not in machine_syms | curated_syms)
    line = el["lines"][0]
    sub = line["orbital"][:2]
    ref = rb.level_reference(el["symbol"], sub)
    legacy_pos = [p for p in ref["positions"] if p["tier"] == "legacy"]
    assert legacy_pos, f"{el['symbol']} {sub}: expected legacy survey position"
    for p in legacy_pos:
        assert p["status"] == "UNVERIFIED"
        assert p["nominal_be_ev"] == line["be_ev"]
        assert p["source_id"] == "legacy-embedded-dataset"


def test_chemical_states_carry_ref_and_source():
    """Every bridged chemical state carries ref + source + UNVERIFIED —
    matching the committed legacy chem-states doc exactly."""
    chem = _load(os.path.join("legacy", "chemical-states.json"))
    for grp in chem["groups"]:
        sub = grp["orbital"][:2]
        ref = rb.level_reference(grp["element"], sub)
        states = ref["chemical_states"]
        assert len(states) == len(grp["states"])
        by_id = {s["id"]: s for s in grp["states"]}
        for s in states:
            src = by_id[s["id"]]
            assert s["be_ev"] == src["be_ev"]
            assert s["ref"] == src["ref"]           # citation required
            assert s["source"] == src["source"]
            assert s["status"] == "UNVERIFIED"


def test_uncovered_element_returns_no_positions():
    """An element with NO tier data anywhere returns structure + empty
    positions — the bridge never fills a gap."""
    ref = rb.level_reference("Tc", "3d")
    assert ref["structure"]["structure"] == "doublet"
    assert ref["positions"] == []
    assert ref["chemical_states"] == []


def test_bridge_emits_nothing_not_in_data_xps():
    """Global anti-invention sweep: EVERY position the bridge emits for
    EVERY Z=1..96 element/level must be value-identical to a record in the
    committed data files."""
    from autofit import coverage
    allowed = set()
    machine = _load("elements-machine.json")["elements"]
    for e in machine + _load("elements-main.json")["elements"] \
            + _load("elements-actinides.json")["elements"] \
            + _load("elements-lanthanides.json")["elements"]:
        for fam in e["families"]:
            for t in fam["transitions"]:
                allowed.add((e["symbol"], t["orbital"],
                             float(t["nominal_be_ev"])))
    for e in _load(os.path.join("legacy", "survey-lines.json"))["elements"]:
        for ln in e["lines"]:
            allowed.add((e["symbol"], ln["orbital"], float(ln["be_ev"])))

    emitted = 0
    for sym in coverage.PERIODIC_TABLE:
        st = coverage.element_structure(sym)
        for lv in st["levels"]:
            ref = rb.level_reference(sym, lv["level"])
            for pos in ref["positions"]:
                emitted += 1
                key = (sym, pos["orbital"], float(pos["nominal_be_ev"]))
                assert key in allowed, (
                    f"{key}: bridge emitted a position not present in "
                    "data/xps — INVENTION")
    assert emitted > 0


def test_structural_fallback_carries_bridge_records():
    """resolve() structural fallback for a machine-tier element now emits
    sourced reference records (status per tier) while still building ZERO
    candidates — and the degradation path for uncovered elements is
    unchanged."""
    phase = Phase(id="s", material_class=MaterialClass("conductor"),
                  regions=("Ti 2p",))
    g = resolve([phase], "Ti 2p", allow_structural_fallback=True)
    assert g.candidates == []
    recs = g.provenance["Ti 2p"]
    bridge_recs = [r for r in recs
                   if str(r["constant"]).startswith("reference:")]
    assert bridge_recs, "bridge records missing from structural provenance"
    assert any(r["status"] == "CONDITIONAL" for r in bridge_recs)
    # sha256 provenance reaches the analysis namespace
    assert any("sha256" in json.dumps(r.get("value", {}))
               for r in bridge_recs)
    # the naked position record still says UNVERIFIED (engine-level
    # honesty: sourced positions still need curation to build candidates)
    naked = next(r for r in recs if r["constant"] == "binding_energy_ev")
    assert naked["status"] == "UNVERIFIED" and naked["value"] is None

    # uncovered element: existing structure-only degradation, no bridge recs
    phase2 = Phase(id="s", material_class=MaterialClass("conductor"),
                   regions=("Tc 3d",))
    g2 = resolve([phase2], "Tc 3d", allow_structural_fallback=True)
    assert g2.candidates == []
    assert not [r for r in g2.provenance["Tc 3d"]
                if str(r["constant"]).startswith("reference:")]
    assert any("positions UNVERIFIED" in n for n in g2.notes)


def test_unknown_element_or_level_raises():
    with pytest.raises(KeyError):
        rb.level_reference("Zz", "2p")
    with pytest.raises(KeyError):
        rb.level_reference("Ti", "5f")   # not occupied
