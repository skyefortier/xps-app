"""
B 1s and Cl 2p engine parity gates (region cookbook, spec §7).

Calibrated 2026-07-03:

- Cl 2p (both corrected anchors): with the decisive-override rule the
  RELAXED-ratio doublet wins as a CONDITIONAL result — it beats the
  fixed-ratio candidate by very strong evidence (χ²ᵣ 1.62 vs 2.40) while
  pegging its ratio bound at 0.55.  The engine is reporting honestly that
  the data rejects the 2:1 statistical ratio — consistent with the
  documented elevated χ²ᵣ / unmodeled structure in these spectra (PROGRESS
  discrepancy log).  2p3/2 Δ ≤ 0.05 eV and splitting 1.55–1.65 hold either
  way.
- B 1s (good anchor B1s Scan): the 3-component candidate wins CLEAN and
  beats the expert χ²ᵣ (1.26 vs 1.43); low Δ 51 meV, mid Δ 167 meV,
  oxide Δ 14 meV.  On the weaker Scan_7 the mid component drops (B2b wins)
  — expected weak-exemplar ambiguity (spec §3.3), not gated.

Fast (2–4 candidates per region) — runs in the normal suite.
"""

import os

import pytest

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")

OPTIONS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": False}

B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
            regions=("B 1s", "C 1s"))
UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
             regions=("U 4f", "Cl 2p"))


def _anchor(project, name):
    return next(r for r in load_reference_fits(os.path.join(DATA, project))
                if r.name == name)


def test_b1s_parity_gate():
    rf = _anchor("B4C-UCl4.proj.zip", "B1s Scan")
    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=resolve([B4C], "B 1s"),
        options=OPTIONS)
    assert res.success, res.message
    assert res.diagnostics["winner"] == "B3_low_mid_oxide"

    exp = {p["name"]: p["center"] for p in rf.peaks}
    by_role = {p["role"]: p for p in res.peaks}
    # position-neutral roles vs the expert's (conflicting) labels — see
    # PROGRESS.md discrepancy #7; positions are what both sources agree on
    assert abs(by_role["main_b_low"]["center"] - exp["B-C"]) <= 0.15
    assert abs(by_role["main_b_mid"]["center"] - exp["B-B"]) <= 0.30
    assert abs(by_role["main_b_oxide"]["center"] - exp["B-O"]) <= 0.10

    winner = next(c for c in res.analysis["candidates"]
                  if c["name"] == res.diagnostics["winner"])
    assert winner["reduced_chi_sq"] <= rf.fit_result["chiReduced"] * 1.2


@pytest.mark.parametrize("name", ["Cl2p Scan", "Cl2p Scan_0"])
def test_cl2p_parity_gate(name):
    rf = _anchor("Cl2p_projfit_test.proj.zip", name)
    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=resolve([UCL4], "Cl 2p"),
        options=OPTIONS)
    assert res.success, res.message

    exp32 = next(p for p in rf.peaks if "3/2" in p["name"])
    by_role = {p["role"]: p for p in res.peaks}
    p32, p12 = by_role["main_cl2p32"], by_role["main_cl2p12"]
    assert abs(p32["center"] - exp32["center"]) <= 0.05
    splitting = p12["center"] - p32["center"]
    assert 1.55 <= splitting <= 1.65
    ratio = p12["amplitude"] / p32["amplitude"]
    if res.diagnostics["winner"] == "Cl0_doublet":
        assert ratio == pytest.approx(0.5, rel=1e-6)
    else:
        # relaxed-ratio winner: decisively better fit with the ratio pegged
        # at its bound — MUST be surfaced as conditional with the violation
        assert res.diagnostics["winner"] == "Cl0r_doublet_relaxed"
        assert 0.45 <= ratio <= 0.55
        assert res.diagnostics["conditional"] is True
        assert any("ratio" in h for h in res.diagnostics["winner_boundary_hits"])
    # doublet shares its lineshape
    assert p12["fwhm"] == pytest.approx(p32["fwhm"], rel=1e-9)
    assert p12["gl_ratio"] == pytest.approx(p32["gl_ratio"], rel=1e-9)

    winner = next(c for c in res.analysis["candidates"]
                  if c["name"] == res.diagnostics["winner"])
    # engine must be at least on par with the (documented elevated-χ²ᵣ)
    # expert fits — measured: strictly better on both anchors
    assert winner["reduced_chi_sq"] <= rf.fit_result["chiReduced"]
