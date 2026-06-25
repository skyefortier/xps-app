"""Curated-card short_caveat invariants.

Prompt 2 of the reference-card copy work: each curated (reviewed) element
record gains an OPTIONAL one-line ``short_caveat`` shown above the "more…"
expander, while the full ``curation_notes`` stays byte-identical behind it.

These tests assert (a) the schema admits short_caveat and still admits its
absence, (b) the seven target records carry the exact expected strings, (c)
short_caveat is served through the loader untouched, and (d) this change did
NOT alter any curation_notes string (compared per-record vs the branch point,
main) — i.e. only short_caveat was added.
"""
import json
import os
import subprocess
from pathlib import Path

import jsonschema
import pytest

from xps_reference import load_reference

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "xps"

# The seven curated records and their verbatim caveats (exact unicode).
EXPECTED = {
    ("elements-main.json", "C"):
        "Reference is for elemental/adventitious carbon. Oxidized states "
        "(carbonates, C–F groups) sit at higher binding energy and may fall "
        "above the shaded band.",
    ("elements-main.json", "O"):
        "The reference band reflects compound and adsorbed oxygen. "
        "Lattice/metal-oxide oxygen sits lower and may fall below the band.",
    ("elements-main.json", "Cl"):
        "The 2p reference is a single chloride-type value of unidentified "
        "specimen — use it as an approximate guide for the chloride region.",
    ("elements-main.json", "Cu"):
        "Reference is for copper metal. Cu(II) species show strong shake-up "
        "satellites near 940–945 eV that aren't included here but are "
        "diagnostic of oxidation state.",
    ("elements-main.json", "Nb"):
        "Reference is for niobium metal. Oxides (Nb₂O₅, NbO₂) sit at higher "
        "binding energy; the band's upper extent for those states is "
        "approximate.",
    ("elements-actinides.json", "U"):
        "Reference positions are for the metal. Real samples are usually "
        "oxidized and sit several eV higher, so the shaded bands are widened "
        "upward to cover the common oxidation states.",
    ("auger-lines.json", "Cu"):
        "The principal Cu LMM Auger line. Oxide-specific kinetic energies — "
        "used in Auger-parameter (Wagner) analysis to tell Cu oxidation states "
        "apart — aren't included.",
}

CURATED_FILES = ("elements-main.json", "elements-actinides.json", "auger-lines.json")


def _schema():
    return json.loads((DATA / "schema.json").read_text(encoding="utf-8"))


def _element_validator():
    schema = _schema()
    return jsonschema.Draft202012Validator(
        {"$ref": "#/$defs/element", "$defs": schema["$defs"]})


def _doc(fname):
    return json.loads((DATA / fname).read_text(encoding="utf-8"))


def _by_symbol(fname):
    return {el["symbol"]: el for el in _doc(fname)["elements"]}


# (a) schema admits short_caveat AND still admits its absence ──────────────────

def test_schema_admits_short_caveat():
    v = _element_validator()
    base = {
        "symbol": "Xe", "z": 54, "name": "Xenon", "curation_status": "curated",
        "curation_notes": "demo", "families": [],
    }
    with_caveat = dict(base, short_caveat="a one-line caveat")
    assert list(v.iter_errors(with_caveat)) == [], "short_caveat must validate"


def test_schema_still_admits_absent_short_caveat():
    v = _element_validator()
    without = {
        "symbol": "Xe", "z": 54, "name": "Xenon", "curation_status": "machine",
        "families": [],
    }
    assert list(v.iter_errors(without)) == [], "absence must remain valid"


def test_schema_rejects_non_string_short_caveat():
    v = _element_validator()
    bad = {
        "symbol": "Xe", "z": 54, "name": "Xenon", "curation_status": "curated",
        "families": [], "short_caveat": 123,
    }
    assert list(v.iter_errors(bad)), "non-string short_caveat must be rejected"


# (b) the seven target records carry the exact expected strings ────────────────

@pytest.mark.parametrize("key", sorted(EXPECTED), ids=lambda k: f"{k[0]}:{k[1]}")
def test_curated_record_has_exact_short_caveat(key):
    fname, sym = key
    el = _by_symbol(fname).get(sym)
    assert el is not None, f"{sym} not found in {fname}"
    assert el.get("short_caveat") == EXPECTED[key]


def test_exactly_seven_short_caveats_across_curated_files():
    found = {(f, el["symbol"]) for f in CURATED_FILES
             for el in _doc(f)["elements"] if "short_caveat" in el}
    assert found == set(EXPECTED)


def test_machine_records_have_no_short_caveat():
    payload = load_reference(DATA)
    leaked = [el["symbol"] for el in payload["machine"] if "short_caveat" in el]
    assert leaked == [], f"machine tier must not carry short_caveat: {leaked}"


# (c) loader serves short_caveat through untouched ─────────────────────────────

def test_loader_serves_every_short_caveat():
    payload = load_reference(DATA)
    served = {}
    for el in payload["elements"]:
        if "short_caveat" in el:
            served[el["symbol"]] = el["short_caveat"]
    for el in payload["auger"]:
        if "short_caveat" in el:
            served[("auger", el["symbol"])] = el["short_caveat"]
    # every photoelectron target is served verbatim
    for (fname, sym), text in EXPECTED.items():
        if fname == "auger-lines.json":
            assert served.get(("auger", sym)) == text
        else:
            assert served.get(sym) == text


# (d) curation_notes strings byte-unchanged vs the branch point (main) ─────────

def _git_show(ref_path):
    r = subprocess.run(["git", "-C", str(REPO), "show", ref_path],
                       capture_output=True, text=True)
    return r


def test_curation_notes_strings_unchanged_vs_main():
    """Per-record curation_notes equality (NOT whole-object bytes — this change
    intentionally adds short_caveat to the same objects). Every element's
    curation_notes must match its value at main; only short_caveat is new."""
    probe = _git_show("main:data/xps/elements-main.json")
    if probe.returncode != 0:
        pytest.skip("git/main unavailable")
    changed = []
    added_caveats = []
    for fname in CURATED_FILES:
        base = json.loads(_git_show(f"main:data/xps/{fname}").stdout)
        base_notes = {el["symbol"]: el.get("curation_notes") for el in base["elements"]}
        base_has_caveat = {el["symbol"] for el in base["elements"] if "short_caveat" in el}
        for el in _doc(fname)["elements"]:
            sym = el["symbol"]
            if el.get("curation_notes") != base_notes.get(sym):
                changed.append(f"{fname}:{sym}")
            if "short_caveat" in el and sym not in base_has_caveat:
                added_caveats.append(f"{fname}:{sym}")
    assert changed == [], f"curation_notes changed (must be byte-identical): {changed}"
    # sanity: main carried no short_caveat; this branch adds exactly the seven
    assert len(added_caveats) == 7, added_caveats
