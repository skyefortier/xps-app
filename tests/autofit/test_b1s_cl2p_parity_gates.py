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
    # PROGRESS.md discrepancy #8; positions are what both sources agree on
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
    # doublet shares its lineshape
    assert p12["fwhm"] == pytest.approx(p32["fwhm"], rel=1e-9)
    assert p12["gl_ratio"] == pytest.approx(p32["gl_ratio"], rel=1e-9)

    # KNOWN ANCHOR RESULT, pinned directly (not winner-dependent): the data
    # rejects the 2:1 statistical ratio by very strong evidence, so the
    # decisive-override path must fire — winner is the bound-fixed refit of
    # the relaxed-ratio candidate, surfaced as conditional, with the fixed
    # ratio at the 0.55 bound and the fixed-vs-relaxed evidence recorded.
    assert res.diagnostics["winner"] == "Cl0r_doublet_relaxed+bfix"
    assert res.diagnostics["conditional"] is True
    assert res.diagnostics["conditional_reason"] == "decisive_override"
    assert any("ratio" in p for p in res.diagnostics["winner_boundary_fixed_params"])
    # the bound-fixed refit must be an INTERIOR optimum (no fresh pegs)
    assert res.diagnostics["winner_boundary_hits"] == []
    ratio = p12["amplitude"] / p32["amplitude"]
    assert ratio == pytest.approx(0.55, abs=1e-6)   # fixed at the bound

    names = {c["name"]: c for c in res.analysis["candidates"]}
    assert {"Cl0_doublet", "Cl0r_doublet_relaxed",
            "Cl0r_doublet_relaxed+bfix"} <= set(names)

    # Adjudication #7 (2026-07-03) — independent widths IMPLEMENTED and
    # measured 2026-07-04: the free-width candidates are enumerated but the
    # data REJECTS the Coster-Kronig hypothesis on both anchors — the width
    # excess pegs at its 0 bound (equal widths preferred) and the relaxed
    # ratio still pegs at 0.55 even WITH width freedom.  The ratio anomaly
    # is not a shared-FWHM artifact; Δso/ratio remain CONDITIONAL (the
    # adjudicated lift was contingent on the ratio returning to ~0.5).
    assert {"Cl0w_doublet_freewidth",
            "Cl0rw_doublet_relaxed_freewidth"} <= set(names)
    assert ("main_cl2p12:fwhm_excess@min"
            in names["Cl0w_doublet_freewidth"]["boundary_hits"])
    rw_hits = names["Cl0rw_doublet_relaxed_freewidth"]["boundary_hits"]
    assert "main_cl2p12:fwhm_excess@min" in rw_hits
    assert "main_cl2p12:ratio@max" in rw_hits
    # width freedom bought nothing at the fixed statistical ratio
    assert (names["Cl0w_doublet_freewidth"]["reduced_chi_sq"]
            <= names["Cl0_doublet"]["reduced_chi_sq"] * 1.02)
    # fixed-vs-relaxed evidence: the relaxed family is decisively better,
    # by the full dominance margin on BIC* and on χ²ᵣ
    assert names["Cl0r_doublet_relaxed+bfix"]["bic_star"] + 10 \
        < names["Cl0_doublet"]["bic_star"]
    assert names["Cl0r_doublet_relaxed+bfix"]["reduced_chi_sq"] \
        < names["Cl0_doublet"]["reduced_chi_sq"]
    # CONDITIONAL constants provenance is runtime-visible
    flagged = res.analysis["uses_conditional_or_unverified_constants"]
    assert any("spin_orbit_splitting_ev" in f for f in flagged)

    # engine must be at least on par with the (documented elevated-χ²ᵣ)
    # expert fits — measured: strictly better on both anchors
    winner = names[res.diagnostics["winner"]]
    assert winner["reduced_chi_sq"] <= rf.fit_result["chiReduced"]
