"""
Tiered fit-physics DB wiring (run-brief item 4) — EXPOSURE ONLY.

The DB's matching entries + mechanical cross-checks must appear in
grammar.provenance (and therefore in every fit's analysis payload), while
candidate construction stays byte-identical (parity preserved: the grammar
constants stand until the machine-tier human review).
"""

import pytest

from autofit.fit_physics import entries_for_region, provenance_entries
from autofit.grammar import MaterialClass, Phase, resolve

UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
             regions=("U 4f", "Cl 2p"))
B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
            regions=("B 1s", "C 1s"))


def _prov(region, phases):
    g = resolve(phases, region)
    slug = region
    return g, {p["constant"]: p for p in g.provenance[slug]}


def test_cl2p_db_entries_exposed():
    g, prov = _prov("Cl 2p", [UCL4])
    for key in ("fit_physics:Cl-2p3/2", "fit_physics:Cl-2p1/2"):
        assert key in prov
        assert prov[key]["status"] in ("CONDITIONAL", "UNVERIFIED")
        assert "fit-physics.json" in prov[key]["source"]
    # curated-tier entries map to CONDITIONAL
    assert prov["fit_physics:Cl-2p3/2"]["value"]["tier"] == "curated"
    assert prov["fit_physics:Cl-2p3/2"]["status"] == "CONDITIONAL"


def test_cl2p_cross_checks_agree():
    """DB Δso 1.6 / ratio 0.5 agree with the grammar's 1.60 / 0.5 — the
    cross-check records must say so, with no disagreement note."""
    g, prov = _prov("Cl 2p", [UCL4])
    checks = [p for c, p in prov.items()
              if c.startswith("fit_physics_cross_check:")]
    assert checks, "expected mechanical cross-check records"
    assert all(p["value"]["agrees"] for p in checks)
    assert not [n for n in g.notes if "DISAGREEMENT" in n]


def test_u4f_range_containment_agrees():
    """The U 4f grammar splitting is a RANGE [10.75, 10.95]; the DB's 10.8
    falls inside — containment is the honest comparison, so the
    cross-check must record agreement (no disagreement note)."""
    g, prov = _prov("U 4f", [UCL4])
    cc = prov["fit_physics_cross_check:U-4f7/2:splitting_ev"]
    assert cc["value"]["db"] == pytest.approx(10.8)
    assert cc["value"]["agrees"] is True
    assert not [n for n in g.notes if "DISAGREEMENT" in n]


def test_disagreement_path_surfaces():
    """Synthetic unit coverage of the disagreement machinery: a scalar
    module constant that contradicts the DB must produce agrees=False and
    a 'grammar value stands' note."""
    mod_prov = [{"constant": "spin_orbit_splitting_ev", "value": 1.75,
                 "status": "CONDITIONAL", "source": "synthetic"}]
    records, notes = provenance_entries("Cl 2p", mod_prov)
    cc = [r for r in records
          if r["constant"].endswith(":splitting_ev")]
    assert cc and all(r["value"]["agrees"] is False for r in cc)
    assert notes and "DISAGREEMENT" in notes[0]
    assert "grammar value stands" in notes[0]


def test_absent_db_region_exposed_honestly():
    """B 1s has no DB entry — exposed as an explicit marker record, not
    silence."""
    g, prov = _prov("B 1s", [B4C])
    assert "fit_physics_db" in prov
    assert "NO entries" in prov["fit_physics_db"]["source"]


def test_candidates_unchanged_by_wiring():
    """Parity guard: the wiring adds provenance/notes ONLY — candidate
    names, slot windows, and slot counts are the grammar's own."""
    g = resolve([UCL4], "Cl 2p")
    names = [c.name for c in g.candidates]
    assert names == ["Cl0_doublet", "Cl0r_doublet_relaxed",
                     "Cl0w_doublet_freewidth",
                     "Cl0rw_doublet_relaxed_freewidth"]
    for c in g.candidates:
        for s in c.slots:
            assert s.be_window[0] < s.be_window[1]


def test_entries_for_region_parsing():
    assert set(entries_for_region("Cl 2p")) == {"Cl-2p3/2", "Cl-2p1/2"}
    assert entries_for_region("N 1s") == {} or "N-1s" in entries_for_region("N 1s")
    assert entries_for_region("not a region") == {}


def test_provenance_entries_pure_function():
    """No mutation of the module provenance passed in."""
    mod_prov = [{"constant": "spin_orbit_splitting_ev", "value": 1.60,
                 "status": "CONDITIONAL", "source": "x"}]
    before = [dict(p) for p in mod_prov]
    provenance_entries("Cl 2p", mod_prov)
    assert mod_prov == before


def test_flows_into_analysis_payload():
    """The IC analysis payload must carry the DB records (runtime-visible
    provenance, not comments) and count them among the
    conditional/unverified constants."""
    import numpy as np
    from autofit.methods import get_method

    rng = np.random.default_rng(7)
    x = np.arange(192.0, 205.0, 0.05)

    def pv(h, c, w, eta=0.3):
        g = np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
        lo = (w / 2) ** 2 / ((x - c) ** 2 + (w / 2) ** 2)
        return h * ((1 - eta) * g + eta * lo)

    y = rng.poisson(300.0 + pv(9000.0, 197.9, 1.65)
                    + pv(4500.0, 199.5, 1.65)).astype(float)
    res = get_method("ic_model_comparison").run(
        x, y, grammar=resolve([UCL4], "Cl 2p"),
        options={"n_refits": 2, "rng_seed": 0, "noise_floor": 1.0,
                 "enable_proposal_pass": False})
    prov = res.analysis["constants_provenance"]["Cl 2p"]
    keys = {p["constant"] for p in prov}
    assert "fit_physics:Cl-2p3/2" in keys
    flagged = res.analysis["uses_conditional_or_unverified_constants"]
    assert any("fit_physics:Cl-2p3/2" in f for f in flagged)
