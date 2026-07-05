"""Phase D unit 2 — cited-source empirical-value loader (autofit/cited_values.py).

The ONLY path by which an empirical value (binding energy, splitting) may
enter the Phase D coverage framework. Anti-confabulation contract:
- nothing loads without a non-empty, non-placeholder source citation;
- every row is validated against the derivable structure (element exists,
  subshell occupied, component label real);
- loaded values are at best CONDITIONAL (cited, not lab-verified);
  test-only files are forced UNVERIFIED and flagged;
- the loader itself contains no default values — an empty table loads to
  an empty list, never to invented numbers.
"""

from __future__ import annotations

import json
import os

import pytest

from autofit.cited_values import CitedValueError, load_cited_values

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures",
                       "example_cited_values.json")


def _write(tmp_path, rows, *, test_only=None, schema_version=1, fmt="json"):
    doc = {"schema_version": schema_version, "rows": rows}
    if test_only is not None:
        doc["test_only"] = test_only
    p = tmp_path / f"vals.{fmt}"
    if fmt == "json":
        p.write_text(json.dumps(doc))
    else:
        import csv
        cols = ["element", "level", "oxidation_state", "value_type",
                "value_ev", "uncertainty_ev", "source_citation", "method",
                "convention"]
        with open(p, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for r in rows:
                w.writerow({k: ("" if r.get(k) is None else r.get(k, ""))
                            for k in cols})
    return str(p)


def _row(**over):
    base = {
        "element": "Cl", "level": "2p3/2", "oxidation_state": None,
        "value_type": "binding_energy_ev", "value_ev": 100.0,
        "uncertainty_ev": 0.5,
        "source_citation": "SYNTHETIC-TEST-ONLY schema demonstration value",
        "method": "synthetic", "convention": "synthetic test frame",
    }
    base.update(over)
    return base


def test_example_fixture_loads_as_test_only_unverified():
    """The committed example file: obviously-synthetic values, file-level
    test_only, every record forced UNVERIFIED with the flag carried."""
    vals = load_cited_values(FIXTURE)
    assert len(vals) >= 2
    for v in vals:
        assert v.test_only is True
        assert v.status == "UNVERIFIED"
        assert v.source_citation.strip()
        assert "SYNTHETIC" in v.source_citation.upper()
    # the fixture's values are deliberately non-physical (100/200 eV
    # placements that exist nowhere near reality for these levels)
    assert all(v.value_ev in (100.0, 200.0) for v in vals)


def test_citation_required(tmp_path):
    for bad in ("", "   ", None, "unknown", "N/A", "todo", "TBD", "none",
                # Codex D2 review (both runs): laundering probes that loaded
                "n-a", "N-A", "false", "true", "0", "null", "nil",
                # Codex D2 re-check (run A MAJOR): punctuation/unicode/
                # whitespace placeholder variants
                "n–a", "None.", "n - a", "n\t-a", "...", "(none)"):
        rows = [_row(source_citation=bad)]
        with pytest.raises(CitedValueError, match="citation"):
            load_cited_values(_write(tmp_path, rows))


def test_non_string_citation_rejected(tmp_path):
    """JSON false/true/0/numbers must not be str()-coerced into 'citations'
    (Codex D2 review BLOCKER, both runs)."""
    for bad in (False, True, 0, 1, 100.0, [], {}):
        rows = [_row(source_citation=bad)]
        with pytest.raises(CitedValueError, match="citation"):
            load_cited_values(_write(tmp_path, rows))


def test_row_index_reported_on_rejection(tmp_path):
    rows = [_row(), _row(source_citation="")]
    with pytest.raises(CitedValueError, match=r"row 1"):
        load_cited_values(_write(tmp_path, rows))


def test_structure_cross_checks(tmp_path):
    with pytest.raises(CitedValueError, match="element"):
        load_cited_values(_write(tmp_path, [_row(element="Zz")]))
    # Cl has no occupied 5f
    with pytest.raises(CitedValueError, match="occupied"):
        load_cited_values(_write(tmp_path, [_row(level="5f7/2")]))
    # 2p has no 5/2 component
    with pytest.raises(CitedValueError, match="component"):
        load_cited_values(_write(tmp_path, [_row(level="2p5/2")]))


def test_value_validation(tmp_path):
    with pytest.raises(CitedValueError, match="value_type"):
        load_cited_values(_write(tmp_path, [_row(value_type="rsf")]))
    with pytest.raises(CitedValueError, match="finite"):
        load_cited_values(_write(tmp_path, [_row(value_ev=float("nan"))]))
    with pytest.raises(CitedValueError, match="positive"):
        load_cited_values(_write(tmp_path, [_row(value_ev=-5.0)]))
    with pytest.raises(CitedValueError, match="uncertainty"):
        load_cited_values(_write(tmp_path, [_row(uncertainty_ev=-0.1)]))
    # splitting: doublet subshells only, never on a specific component
    with pytest.raises(CitedValueError, match="doublet"):
        load_cited_values(_write(tmp_path, [_row(
            element="C", level="1s", value_type="spin_orbit_splitting_ev")]))
    with pytest.raises(CitedValueError, match="component"):
        load_cited_values(_write(tmp_path, [_row(
            level="2p3/2", value_type="spin_orbit_splitting_ev")]))
    # valid splitting row on the subshell passes
    vals = load_cited_values(_write(tmp_path, [_row(
        level="2p", value_type="spin_orbit_splitting_ev")]))
    assert vals[0].component is None and vals[0].level == "2p"


def test_unknown_keys_rejected_typo_guard(tmp_path):
    rows = [dict(_row(), source_citaton="typo carries no citation")]
    del rows[0]["source_citation"]
    with pytest.raises(CitedValueError):
        load_cited_values(_write(tmp_path, rows))
    rows = [dict(_row(), extra_field=1)]
    with pytest.raises(CitedValueError, match="unknown"):
        load_cited_values(_write(tmp_path, rows))


def test_real_cited_rows_are_conditional_never_verified(tmp_path):
    vals = load_cited_values(_write(tmp_path, [_row()], test_only=False))
    assert vals[0].status == "CONDITIONAL"
    assert vals[0].test_only is False
    vals = load_cited_values(_write(tmp_path, [_row()]))  # flag absent
    assert vals[0].status == "CONDITIONAL"


def test_component_parsing():
    vals = load_cited_values(FIXTURE)
    by_level = {(v.element, v.level, v.component) for v in vals}
    # the fixture exercises both a component-specific BE and a subshell row
    assert any(c is not None for _, _, c in by_level)


def test_csv_format_loads_identically(tmp_path):
    rows = [_row(), _row(element="U", level="4f7/2", value_ev=200.0)]
    j = load_cited_values(_write(tmp_path, rows, fmt="json"))
    c = load_cited_values(_write(tmp_path, rows, fmt="csv"))
    assert [(v.element, v.level, v.component, v.value_ev, v.status)
            for v in j] == \
           [(v.element, v.level, v.component, v.value_ev, v.status)
            for v in c]


def test_boolean_value_rejected(tmp_path):
    """bool is an int subclass: float(True) == 1.0 — a JSON true must not
    silently load as a 1.0 eV value."""
    with pytest.raises(CitedValueError, match="numeric"):
        load_cited_values(_write(tmp_path, [_row(value_ev=True)]))
    with pytest.raises(CitedValueError, match="numeric"):
        load_cited_values(_write(tmp_path, [_row(uncertainty_ev=False)]))


def test_json_infinity_rejected(tmp_path):
    """Python's json.loads accepts the nonstandard Infinity literal —
    it must be caught by the finiteness check, not loaded."""
    p = tmp_path / "inf.json"
    p.write_text('{"schema_version": 1, "rows": [{"element": "Cl", '
                 '"level": "2p3/2", "value_type": "binding_energy_ev", '
                 '"value_ev": Infinity, '
                 '"source_citation": "SYNTHETIC-TEST-ONLY demonstration"}]}')
    with pytest.raises(CitedValueError, match="finite"):
        load_cited_values(str(p))


def test_csv_overflow_cells_rejected(tmp_path):
    """A CSV row longer than its header must be rejected loudly — the
    overflow lands under DictReader's None key and silently dropping it
    would hide a shifted/malformed row."""
    p = tmp_path / "overflow.csv"
    p.write_text(
        "element,level,value_type,value_ev,source_citation\n"
        "Cl,2p3/2,binding_energy_ev,100.0,SYNTHETIC-TEST-ONLY demo,EXTRA\n")
    with pytest.raises(CitedValueError, match="malformed"):
        load_cited_values(str(p))


def test_csv_duplicate_headers_rejected(tmp_path):
    """DictReader silently collapses duplicate header names (last cell
    wins) — a blank source_citation can hide behind a duplicated column
    (Codex D2 review MAJOR, both runs)."""
    p = tmp_path / "dup.csv"
    p.write_text(
        "element,level,value_type,value_ev,source_citation,source_citation\n"
        "Cl,2p3/2,binding_energy_ev,100.0,,SYNTHETIC-TEST-ONLY demo\n")
    with pytest.raises(CitedValueError, match="duplicate"):
        load_cited_values(str(p))
    p2 = tmp_path / "dup2.csv"
    p2.write_text(
        "element,level,value_type,value_ev,value_ev,source_citation\n"
        "Cl,2p3/2,binding_energy_ev,BAD,100.0,SYNTHETIC-TEST-ONLY demo\n")
    with pytest.raises(CitedValueError, match="duplicate"):
        load_cited_values(str(p2))


def test_schema_version_gate(tmp_path):
    with pytest.raises(CitedValueError, match="schema_version"):
        load_cited_values(_write(tmp_path, [_row()], schema_version=2))
    # True == 1 in Python — a boolean must not satisfy the integer gate
    with pytest.raises(CitedValueError, match="schema_version"):
        load_cited_values(_write(tmp_path, [_row()], schema_version=True))
    # 1.0 == 1 too — the gate is a strict INTEGER 1
    with pytest.raises(CitedValueError, match="schema_version"):
        load_cited_values(_write(tmp_path, [_row()], schema_version=1.0))


def test_test_only_must_be_boolean(tmp_path):
    """A string 'false' must not be truthiness-coerced (bool('false') is
    True); the flag is part of the provenance contract."""
    for bad in ("false", "true", 1, 0, "yes"):
        with pytest.raises(CitedValueError, match="test_only"):
            load_cited_values(_write(tmp_path, [_row()], test_only=bad))
    # actual booleans pass
    assert load_cited_values(
        _write(tmp_path, [_row()], test_only=True))[0].test_only is True


def test_empty_table_loads_empty_never_invents(tmp_path):
    assert load_cited_values(_write(tmp_path, [])) == []
