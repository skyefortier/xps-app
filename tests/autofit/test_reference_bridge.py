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
    """Global anti-invention sweep, FULL-FIELD (Codex R1 review, both
    runs): every position the bridge emits for every Z=1..96
    element/level must be FIELD-IDENTICAL to its committed record —
    nominal, expected_region_ev, spin_orbit (committed explicit null
    stays null; a field ABSENT in the source must be ABSENT in the
    emission, never synthesized as None) — and every bridged chemical
    state must match its committed record by id."""
    from autofit import coverage

    committed: dict[tuple, dict] = {}
    for fname, tier in (("elements-machine.json", "machine"),
                        ("elements-main.json", "curated"),
                        ("elements-actinides.json", "curated"),
                        ("elements-lanthanides.json", "curated")):
        for e in _load(fname)["elements"]:
            for fam in e["families"]:
                for t in fam["transitions"]:
                    committed[(e["symbol"], t["orbital"], tier)] = t
    for e in _load(os.path.join("legacy", "survey-lines.json"))["elements"]:
        for ln in e["lines"]:
            committed[(e["symbol"], ln["orbital"], "legacy")] = ln

    chem_by_id = {s["id"]: s
                  for g in _load(os.path.join(
                      "legacy", "chemical-states.json"))["groups"]
                  for s in g["states"]}

    emitted = 0
    for sym in coverage.PERIODIC_TABLE:
        st = coverage.element_structure(sym)
        for lv in st["levels"]:
            ref = rb.level_reference(sym, lv["level"])
            for pos in ref["positions"]:
                emitted += 1
                key = (sym, pos["orbital"], pos["tier"])
                assert key in committed, (
                    f"{key}: bridge emitted a position not present in "
                    "data/xps — INVENTION")
                src = committed[key]
                assert pos["nominal_be_ev"] == src.get(
                    "nominal_be_ev", src.get("be_ev"))
                for field in ("expected_region_ev", "spin_orbit"):
                    if field in src:
                        assert field in pos and pos[field] == src[field], (
                            f"{key}.{field}: emission differs from the "
                            "committed record")
                    else:
                        assert field not in pos, (
                            f"{key}.{field}: synthesized field — the "
                            "committed record has no such key")
            for s in ref["chemical_states"]:
                emitted += 1
                src = chem_by_id[s["id"]]
                assert s["be_ev"] == src["be_ev"] and s["ref"] == src["ref"]
    assert emitted > 0


def test_structural_provenance_relays_bridge_values_unmutated():
    """The coverage-layer emission must relay bridge values IDENTICALLY —
    a mutation between the bridge and the analysis namespace is the same
    class of invention (Codex R1 review, run A MAJOR 2)."""
    from autofit import coverage
    for region in ("Ti 2p", "Cu 2p", "Li 1s", "C 1s"):
        sym, sub = region.split()
        bridged = rb.level_reference(sym, sub)
        records, _ = coverage.structural_provenance(region)
        by_const = {}
        for r in records:
            by_const.setdefault(r["constant"], []).append(r)
        for pos in bridged["positions"]:
            recs = by_const[f"reference:{pos['tier']}:{pos['orbital']}"]
            # KEY-PRESENCE identity, not .get() equality: an absent field
            # and an explicit None must not be conflated (Codex R1
            # re-check MINOR — a relay regression synthesizing None for
            # legacy records would slip past .get() comparison)
            _MISSING = object()

            def _field(d, k):
                return d[k] if k in d else _MISSING
            assert any(
                r["value"]["nominal_be_ev"] == pos["nominal_be_ev"]
                and _field(r["value"], "expected_region_ev") ==
                    _field(pos, "expected_region_ev")
                and _field(r["value"], "spin_orbit") ==
                    _field(pos, "spin_orbit")
                and r["status"] == pos["status"]
                for r in recs), (
                f"{region} {pos['orbital']}: provenance record mutated "
                "relative to the bridge (or key-presence differs)")
        if bridged["chemical_states"]:
            agg = by_const["reference:legacy:chemical_states"][0]
            assert agg["value"] == bridged["chemical_states"]


def test_machine_sidecar_join_refusal_and_uniqueness():
    """(a) A machine transition with no sidecar record must REFUSE to
    bridge (never emit naked); (b) the join is by-id and value-unique —
    each Ti position's nominal equals ITS OWN sidecar record's nominal
    (Ti 2p3/2 and Ti 3p differ, so a wrong-key join cannot hide).
    Codex R1 review, run A MINOR."""
    from autofit.reference_bridge import _join_machine_sidecar
    with pytest.raises(ValueError, match="no provenance sidecar"):
        _join_machine_sidecar({"id": "Xx-9z"}, {})

    sidecar = {p["id"]: p for p in
               _load("elements-machine.provenance.json")["transitions"]}
    ref = rb.level_reference("Ti", "2p")
    machine_pos = [p for p in ref["positions"] if p["tier"] == "machine"]
    ref3p = rb.level_reference("Ti", "3p")
    machine_pos += [p for p in ref3p["positions"] if p["tier"] == "machine"]
    assert len({p["orbital"] for p in machine_pos}) >= 2
    for p in machine_pos:
        sc = sidecar[f"Ti-{p['orbital']}"]
        assert p["nominal_be_ev"] == sc["nominal_be_ev"], (
            f"Ti-{p['orbital']}: joined the wrong sidecar record")


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
