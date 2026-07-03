"""
Fit-physics DB no-invention invariants (mirrors the machine-tier test
discipline): every value in data/xps/fit-physics.json must be traceable —
copied from the sourced reference files, pure 2j+1 arithmetic, or a
DOI-cited seed.  Regeneration must be deterministic.
"""

import json
import os
import re
import subprocess
import sys

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DB = os.path.join(REPO, "data", "xps", "fit-physics.json")
GEN = os.path.join(REPO, "scripts", "gen_fit_physics.py")


def _load():
    with open(DB) as f:
        return json.load(f)


def _source_transitions():
    out = {}
    data_dir = os.path.join(REPO, "data", "xps")
    for fname in os.listdir(data_dir):
        if not (fname.startswith("elements-") and fname.endswith(".json")):
            continue
        if "provenance" in fname or "skipped" in fname:
            continue
        doc = json.load(open(os.path.join(data_dir, fname)))
        for el in doc.get("elements", []):
            for fam in el.get("families", []):
                for t in fam.get("transitions", []):
                    if t.get("kind") != "auger":
                        out[t["id"]] = t
    return out


def test_regeneration_is_deterministic_and_committed_current(tmp_path):
    """Committed DB == fresh regeneration (same guarantee style as the
    machine tier): nothing hand-edited, nothing stale."""
    committed = _load()
    env = dict(os.environ)
    out = tmp_path / "fit-physics.json"
    data_dir = os.path.abspath(os.path.join(REPO, "data", "xps"))
    src = open(GEN).read().replace(
        'OUT = os.path.join(DATA, "fit-physics.json")',
        f'OUT = {str(out)!r}').replace(
        'DATA = os.path.join(os.path.dirname(__file__), "..", "data", "xps")',
        f'DATA = {data_dir!r}')
    gen2 = tmp_path / "gen.py"
    gen2.write_text(src)
    subprocess.run([sys.executable, str(gen2)], check=True, cwd=REPO, env=env,
                   capture_output=True)
    regenerated = json.loads(out.read_text())
    assert regenerated == committed


def test_every_entry_traceable():
    db = _load()
    src = _source_transitions()
    for tid, e in db["entries"].items():
        t = src[tid]                       # entry must exist in source data
        assert e["status"] in ("UNVERIFIED-machine-derived",
                               "CONDITIONAL-derived", "SEEDED-lit-cited")
        assert e["derivation"]
        if "be_window_ev" in e:
            assert e["be_window_ev"]["min"] == t["expected_region_ev"]["min"]
            assert e["be_window_ev"]["max"] == t["expected_region_ev"]["max"]
        if "nominal_be_ev" in e:
            assert e["nominal_be_ev"]["value"] == t["nominal_be_ev"]
        if "spin_orbit" in e:
            so = t.get("spin_orbit") or {}
            assert e["spin_orbit"]["splitting_ev"] == so.get("splitting_ev")
            assert e["spin_orbit"]["area_ratio"] == so.get("area_ratio")


def test_statistical_ratios_are_arithmetic():
    db = _load()
    expected = {"p": 1 / 2, "d": 2 / 3, "f": 3 / 4}
    for tid, e in db["entries"].items():
        if "statistical_area_ratio" not in e:
            continue
        m = re.search(r"\d([spdf])", tid.split("-", 1)[1])
        assert m, tid
        assert e["statistical_area_ratio"]["value"] == expected[m.group(1)]
        assert "caveat" in e["statistical_area_ratio"]


def test_machine_tier_entries_flagged_and_never_gain_spin_orbit():
    db = _load()
    src = _source_transitions()
    n_machine = 0
    for tid, e in db["entries"].items():
        if src[tid].get("tier") == "machine":
            n_machine += 1
            assert e["status"] == "UNVERIFIED-machine-derived", tid
            # source has spin_orbit null for machine tier (no-invention);
            # the fit-physics DB must not invent one
            assert "spin_orbit" not in e, tid
    assert n_machine >= 40


def test_seeds_are_doi_cited():
    db = _load()
    for seed_key, seed in db["seeds"].items():
        blob = json.dumps(seed)
        assert "DOI 10." in blob, f"seed {seed_key} lacks a DOI citation"
    seeded = [tid for tid, e in db["entries"].items()
              if e["status"] == "SEEDED-lit-cited"]
    assert set(seeded) >= {"C-1s", "U-4f7/2", "U-4f5/2"}
