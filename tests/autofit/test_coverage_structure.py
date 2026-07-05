"""Phase D unit 1 — derivable element structure (autofit/coverage.py).

Everything this module emits must be derivable from electron configuration
+ quantum bookkeeping alone (anti-confabulation rail): NO binding energies,
NO splitting magnitudes, NO RSFs, NO FWHMs — those arrive only via the
cited-source loader (unit D2). The guard test at the bottom enforces this
structurally over the whole Z=1..96 span.

Element symbol/Z/name facts are DEFINITIONAL and must be cross-pinned to
the committed single source of truth (scripts/gen_machine_tier.py
PERIODIC_TABLE — the same table the NIST acquisition pipeline validates
against committed data), never re-transcribed from memory.
"""

from __future__ import annotations

import importlib.util
import os
import re

import pytest

from autofit import coverage


REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _committed_periodic_table() -> dict:
    spec = importlib.util.spec_from_file_location(
        "gen_machine_tier", os.path.join(REPO, "scripts", "gen_machine_tier.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PERIODIC_TABLE


def test_periodic_table_cross_pinned_to_committed_source():
    """coverage.PERIODIC_TABLE must equal the committed definitional table
    (restricted to the goal's Z=1..96 span) — symbol, Z, and name all exact.
    This is the no-retranscription guard."""
    committed = {sym: (z, name) for sym, (z, name) in
                 _committed_periodic_table().items() if z <= 96}
    assert coverage.PERIODIC_TABLE == committed
    zs = sorted(z for z, _ in coverage.PERIODIC_TABLE.values())
    assert zs == list(range(1, 97))


def test_madelung_configuration_is_the_documented_algorithm():
    """The configuration is the MADELUNG (n+l, n) filling — an algorithm,
    not a lookup. Known anomalous ground states (which the algorithm does
    not reproduce) must be documented as a caveat, not silently encoded."""
    def cfg(sym):
        return {c["subshell"]: c["occupancy"]
                for c in coverage.element_structure(sym)["configuration"]}

    assert cfg("H") == {"1s": 1}
    assert cfg("C") == {"1s": 2, "2s": 2, "2p": 2}
    assert cfg("Cl") == {"1s": 2, "2s": 2, "2p": 6, "3s": 2, "3p": 5}
    fe = cfg("Fe")
    assert fe["3d"] == 6 and fe["4s"] == 2          # [Ar] 4s2 3d6
    u = cfg("U")
    assert u["5f"] == 4 and u["7s"] == 2            # Madelung gives 5f4
    # total electron count == Z for every element
    for sym, (z, _) in coverage.PERIODIC_TABLE.items():
        assert sum(c["occupancy"]
                   for c in coverage.element_structure(sym)["configuration"]) == z
    # the anomaly caveat is a first-class field
    assert "Madelung" in coverage.element_structure("Cu")["configuration_caveat"]


def test_doublet_singlet_structure():
    """l = 0 → singlet; l > 0 → spin-orbit doublet with j = l ± 1/2 and
    degeneracies 2j + 1 (exact quantum bookkeeping)."""
    s1 = coverage.level_structure("C", "1s")
    assert s1["structure"] == "singlet"
    assert len(s1["components"]) == 1
    assert s1["components"][0]["label"] == "1s"

    p = coverage.level_structure("Cl", "2p")
    assert p["structure"] == "doublet"
    assert [(c["label"], c["j"], c["degeneracy"]) for c in p["components"]] == [
        ("2p3/2", "3/2", 4), ("2p1/2", "1/2", 2)]

    d = coverage.level_structure("Zr", "3d")
    assert [(c["label"], c["degeneracy"]) for c in d["components"]] == [
        ("3d5/2", 6), ("3d3/2", 4)]

    f = coverage.level_structure("U", "4f")
    assert [(c["label"], c["degeneracy"]) for c in f["components"]] == [
        ("4f7/2", 8), ("4f5/2", 6)]


def test_statistical_ratios_exact_for_p_d_f():
    """(2j+1) area-ratio EXPECTATIONS, exact rationals, child(lower-j) over
    parent(higher-j) — matching the grammar's existing area_ratio convention
    (Cl 2p 0.5, U 4f 0.75). Never a hard constraint (Cl 2p adjudication)."""
    cases = [("Cl", "2p", 1, 2), ("Zr", "3d", 2, 3), ("U", "4f", 3, 4)]
    for sym, level, num, den in cases:
        r = coverage.level_structure(sym, level)["statistical_area_ratio"]
        assert r["numerator"] == num and r["denominator"] == den
        assert r["value"] == pytest.approx(num / den, abs=0)
        assert r["convention"] == "lower_j_over_higher_j"
        assert r["expectation_only"] is True
        assert "Coster-Kronig" in r["caveat"]
        assert "free ratio" in r["caveat"] or "never a hard constraint" in r["caveat"]


def test_partially_filled_subshell_has_no_ratio_expectation():
    """A partially-filled subshell (valence character) gets NO statistical
    ratio — the (2j+1) bookkeeping presumes a filled shell."""
    fe3d = coverage.level_structure("Fe", "3d")
    assert fe3d["partially_filled"] is True
    assert fe3d["statistical_area_ratio"] is None
    cl3p = coverage.level_structure("Cl", "3p")   # 3p5
    assert cl3p["partially_filled"] is True
    assert cl3p["statistical_area_ratio"] is None
    cl2p = coverage.level_structure("Cl", "2p")   # filled
    assert cl2p["partially_filled"] is False
    assert cl2p["statistical_area_ratio"] is not None


def test_multiplet_prone_flag_open_d_f_only():
    """Open (partially-filled) d or f subshell in the Madelung neutral-atom
    configuration → multiplet-prone FLAG (a flag, never a splitting), with
    the oxidation-state / anomalous-configuration caveat attached."""
    assert coverage.element_structure("Fe")["multiplet_prone"] is True    # 3d6
    assert coverage.element_structure("Gd")["multiplet_prone"] is True    # 4f open
    assert coverage.element_structure("U")["multiplet_prone"] is True     # 5f open
    assert coverage.element_structure("Zn")["multiplet_prone"] is False   # 3d10
    assert coverage.element_structure("C")["multiplet_prone"] is False    # no d/f
    assert coverage.element_structure("K")["multiplet_prone"] is False
    st = coverage.element_structure("Fe")
    assert st["multiplet_rule"].startswith("derived:")
    assert "oxidation" in st["multiplet_caveat"].lower()


def test_conductor_class_positional_defaults():
    """Coarse elemental-solid default from periodic position (six-metalloid
    staircase convention), explicitly user-overridable, with the
    allotrope/compound caveat. Uses the grammar's MaterialClass vocabulary."""
    expect = {
        "Fe": "conductor", "Au": "conductor", "Al": "conductor",
        "Gd": "conductor", "U": "conductor", "K": "conductor",
        "Si": "semiconductor", "Ge": "semiconductor", "B": "semiconductor",
        "Te": "semiconductor",
        "Cl": "insulator", "O": "insulator", "Kr": "insulator",
        "H": "insulator", "C": "insulator",
    }
    for sym, cls in expect.items():
        st = coverage.element_structure(sym)
        assert st["conductor_class_default"] == cls, (
            f"{sym}: got {st['conductor_class_default']}, expected {cls}")
    st = coverage.element_structure("C")
    assert st["conductor_class_rule"].startswith("derived:")
    assert "overrid" in st["conductor_class_caveat"].lower()  # override/overridable
    # carbon's allotrope problem must be called out by name
    assert "graphite" in st["conductor_class_caveat"].lower()


def test_every_element_z1_to_z96_builds_with_provenance_tags():
    for sym, (z, _name) in sorted(coverage.PERIODIC_TABLE.items(),
                                  key=lambda kv: kv[1][0]):
        st = coverage.element_structure(sym)
        assert st["z"] == z
        assert st["levels"], f"{sym}: no levels"
        for lv in st["levels"]:
            assert lv["derived_rule"].startswith("derived:"), (
                f"{sym} {lv['level']}: missing derived-rule tag")
        assert st["multiplet_rule"].startswith("derived:")
        assert st["conductor_class_rule"].startswith("derived:")
    # by-Z access agrees with by-symbol access
    assert coverage.element_structure(26)["symbol"] == "Fe"


def test_region_label_parsing_and_unknowns():
    sym, level = coverage.parse_region("Cl 2p")
    assert (sym, level) == ("Cl", "2p")
    assert coverage.parse_region("nonsense") is None
    assert coverage.parse_region("Zz 9x") is None
    with pytest.raises(KeyError):
        coverage.element_structure("Zz")
    with pytest.raises(KeyError):
        coverage.level_structure("Cl", "5f")   # not occupied in Cl


_VALUE_BEARING_KEY = re.compile(
    r"(_ev$|_energy|energy_|^rsf|_rsf|fwhm|splitting|sensitivity)", re.I)

# generic "value" is NOT here — it is only allowed inside the
# statistical_area_ratio record (checked contextually below), so a wrapped
# empirical value like {"splitting_ev": {"value": 1.6}} cannot launder
# through a whitelisted leaf key (Codex D1 review, both runs).
_ALLOWED_NUMERIC_KEYS = frozenset({
    "z", "n", "l", "occupancy", "capacity", "degeneracy",
    "numerator", "denominator", "period", "group",
})

# decimal numbers, or integers glued to an eV unit, inside ANY string —
# catches value-laundering through caveat/source prose ("284.8", "1.6 eV").
# Derivable integer bookkeeping like "2j+1", "1:2", "3/2" stays legal.
_STRING_VALUE_PATTERN = re.compile(r"\d+\.\d+|\b\d+(\.\d+)?\s*eV\b", re.I)


def _walk(obj, path="", bearing=False):
    """Yield (path, leaf, under_value_bearing_key) for every leaf."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}",
                             bearing or bool(_VALUE_BEARING_KEY.search(k)))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]", bearing)
    else:
        yield path, obj, bearing


def test_anti_confabulation_no_energy_values_anywhere():
    """THE GOVERNING RAIL: across the whole Z=1..96 output there must be no
    populated value-bearing field (binding energies, splittings, RSFs,
    FWHMs) — including anything NESTED under a value-bearing key; every
    numeric leaf must belong to the whitelisted quantum bookkeeping (the
    ratio's 'value' only inside the statistical_area_ratio record); and no
    string leaf may smuggle a decimal number or an eV-suffixed quantity
    (caveat/source prose is scanned too)."""
    for sym in coverage.PERIODIC_TABLE:
        st = coverage.element_structure(sym)
        for path, leaf, bearing in _walk(st):
            key = path.rsplit(".", 1)[-1].split("[")[0]
            if bearing:
                assert leaf is None, (
                    f"{sym}{path}: populated content under a value-bearing "
                    f"key ({leaf!r}) — empirical values may only come from "
                    "the cited-source loader")
            if isinstance(leaf, (int, float)) and not isinstance(leaf, bool):
                if key == "value":
                    # EXACT direct child only — any-depth allowance would
                    # let {"statistical_area_ratio": {"empirical_bound":
                    # {"value": 0.55}}} launder structured empirical data
                    # (Codex D1 re-check, run B MAJOR)
                    assert path.endswith(".statistical_area_ratio.value"), (
                        f"{sym}{path}: numeric 'value' outside the "
                        f"statistical-ratio record's own value field "
                        f"({leaf!r})")
                else:
                    assert key in _ALLOWED_NUMERIC_KEYS, (
                        f"{sym}{path}: unexpected numeric leaf {leaf!r} "
                        f"under non-whitelisted key {key!r}")
            if isinstance(leaf, str):
                m = _STRING_VALUE_PATTERN.search(leaf)
                assert m is None, (
                    f"{sym}{path}: string leaf smuggles a numeric value "
                    f"({m.group(0)!r} in {leaf!r}) — prose must not carry "
                    "empirical numbers")
        # binding energy must exist as a field on every level and be None
        for lv in st["levels"]:
            assert "binding_energy_ev" in lv and lv["binding_energy_ev"] is None


def test_cache_isolation_first_call_and_cache_hit():
    """Mutating a returned structure must never corrupt later reads —
    on BOTH the first-call and cache-hit paths (Codex D1 review, MINOR)."""
    coverage._STRUCTURE_CACHE.clear()
    first = coverage.element_structure("Ni")          # first-call path
    first["levels"][0]["binding_energy_ev"] = 999.0
    first["multiplet_prone"] = "corrupted"
    second = coverage.element_structure("Ni")         # cache-hit path
    assert second["levels"][0]["binding_energy_ev"] is None
    assert isinstance(second["multiplet_prone"], bool)
    second["levels"][0]["binding_energy_ev"] = 888.0
    assert coverage.element_structure("Ni")["levels"][0]["binding_energy_ev"] is None
    lv = coverage.level_structure("Ni", "2p")
    lv["binding_energy_ev"] = 777.0
    assert coverage.level_structure("Ni", "2p")["binding_energy_ev"] is None


def test_madelung_anomaly_edge_cases_pinned():
    """Pins the ALGORITHM's outputs for elements whose TRUE ground states
    deviate from Madelung (real Cu is 3d10 4s1, Pd 4d10, La 5d1, Ce 4f1
    5d1). These pins make encoding the real configurations a REVIEWED
    decision that must consciously change this test — never a silent
    'helpful' patch (no-invention rail; the caveat documents the deviation
    instead). Codex D1 review, run B MINOR."""
    def occ(sym):
        return {c["subshell"]: c["occupancy"]
                for c in coverage.element_structure(sym)["configuration"]}
    assert occ("Cu")["3d"] == 9 and occ("Cu")["4s"] == 2      # Madelung, not real
    assert coverage.element_structure("Cu")["multiplet_prone"] is True
    assert occ("Pd")["4d"] == 8 and occ("Pd")["5s"] == 2      # Madelung, not real
    assert coverage.element_structure("Pd")["multiplet_prone"] is True
    assert occ("La")["4f"] == 1                                # Madelung, not real
    assert coverage.element_structure("La")["multiplet_prone"] is True
    assert occ("Ce")["4f"] == 2                                # Madelung, not real
    assert coverage.element_structure("Ce")["multiplet_prone"] is True
