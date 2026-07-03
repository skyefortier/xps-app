"""
Stage-3 U 4f parity gate (spec §3.2): the resolver + IC engine reproduce the
expert U 4f fits — asymmetric LACX main doublet + explicitly modeled
satellites, one joint fit — and the U 4f + N 1s co-fit works with correct
per-phase tagging.

Calibrated 2026-07-03 (u4f diagnostics): single-region anchors give main Δ
2–14 meV, satellite Δ 0.01–0.02 eV, splitting 10.85, ratio 0.64–0.66, and
the engine's χ²ᵣ BEATS the expert fits (1.40 vs 1.71; 1.42 vs 2.00).  The
co-fit anchor (4-GTA, a known-rough reference) resolves the N 1s line at
398.28 (phase BN) with engine χ²ᵣ 7.1 vs the expert's 11.4; engine/expert
weight-split differences in the N-overlap zone are logged in PROGRESS.md,
not forced.

Unlike the C 1s gate this one is FAST (3 U-candidates; ~20 s total), so it
runs in the normal suite — no env gating.
"""

import os

import pytest

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")

UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
             regions=("U 4f", "Cl 2p"))
BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
           regions=("N 1s", "B 1s"))

MAIN_TOL_EV = 0.05
SAT_TOL_EV = 0.3
CHIR_FACTOR = 1.2          # engine χ²ᵣ must be ≤ expert × this (measured: better)
# The 4-GTA co-fit anchor is a KNOWN-ROUGH reference (expert χ²ᵣ 11.4) on a
# genuinely multi-modal problem (U satellite / N 1s overlap): the winner's
# U-main positions vary at the few-hundred-meV level with run-order FP
# wobble (documented in PROGRESS.md).  The co-fit gate therefore asserts
# STRUCTURE + phase correctness + fit quality; tight position parity is the
# single-region tests' job on the good anchors.
COFIT_MAIN_TOL_EV = 0.5
N1S_TOL_EV = 0.3

OPTIONS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
           "enable_proposal_pass": False}


def _anchor(project, name):
    return next(r for r in load_reference_fits(os.path.join(DATA, project))
                if r.name == name)


@pytest.mark.parametrize("project,name", [
    ("B4C-UCl4.proj.zip", "U4f Scan"),
    ("UCl4_on_graphite.proj.zip", "U4f Scan_5"),
], ids=["B4C-UCl4", "UCl4-graphite"])
def test_u4f_single_region_parity(project, name):
    rf = _anchor(project, name)
    grammar = resolve([UCL4], "U 4f")
    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar, options=OPTIONS)
    assert res.success, res.message

    exp_main = next(p for p in rf.peaks if p["name"].startswith("U 4f7"))
    exp_sat = min((p for p in rf.peaks if "at" in p["name"].lower()
                   and not p["name"].startswith("U 4f")),
                  key=lambda p: p["center"])
    by_role = {p["role"]: p for p in res.peaks}

    main = by_role["main_u4f72"]
    assert abs(main["center"] - exp_main["center"]) <= MAIN_TOL_EV, (
        f"main Δ {abs(main['center'] - exp_main['center'])*1000:.0f} meV"
    )
    m52 = by_role["main_u4f52"]
    splitting = m52["center"] - main["center"]
    assert 10.75 <= splitting <= 10.95, f"splitting {splitting:.3f}"
    ratio = m52["amplitude"] / main["amplitude"]
    assert 0.60 <= ratio <= 0.85, f"ratio {ratio:.3f}"
    # spin-orbit partner shares the LACX shape (spec: one manifold envelope)
    for pname in ("alpha", "beta", "m", "fwhm"):
        assert m52[pname] == pytest.approx(main[pname], rel=1e-9)

    sat = by_role.get("satellite_u4f72")
    assert sat is not None, "winner lacks the shake-up satellite"
    assert abs(sat["center"] - exp_sat["center"]) <= SAT_TOL_EV

    # fit quality at least on par with the expert fit
    winner = res.diagnostics["winner"]
    top = next(c for c in res.analysis["candidates"] if c["name"] == winner)
    expert_chir = rf.fit_result.get("chiReduced")
    assert top["reduced_chi_sq"] <= expert_chir * CHIR_FACTOR, (
        f"engine χ²ᵣ {top['reduced_chi_sq']:.2f} vs expert {expert_chir:.2f}"
    )


def test_u4f_n1s_cofit():
    """The U-in-BN joint window: U 4f grammar composed with N 1s (spec §2),
    fit jointly, per-phase slot tags preserved."""
    rf = _anchor("4-GTA UCl4-BN.proj.zip", "U4f Scan")
    grammar = resolve([UCL4, BN], ["U 4f", "N 1s"])
    assert grammar.phase_ids == ("UCl4", "BN")
    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar, options=OPTIONS)
    assert res.success, res.message

    by_role = {p["role"]: p for p in res.peaks}
    exp = {p["name"]: p for p in rf.peaks}

    n1s = by_role.get("N1s__main_n1s")
    assert n1s is not None, "co-fit winner lacks the N 1s line"
    assert n1s["phase_id"] == "BN" and n1s["region"] == "N 1s"
    assert abs(n1s["center"] - exp["N"]["center"]) <= N1S_TOL_EV

    main = by_role["U4f__main_u4f72"]
    assert main["phase_id"] == "UCl4" and main["region"] == "U 4f"
    assert abs(main["center"] - exp["U 4f7/2"]["center"]) <= COFIT_MAIN_TOL_EV
    m52 = by_role["U4f__main_u4f52"]
    assert abs(m52["center"] - exp["U 4f5/2"]["center"]) <= COFIT_MAIN_TOL_EV

    # no phase leakage anywhere in the winner
    for p in res.peaks:
        assert p["phase_id"] in ("UCl4", "BN"), p
        assert (p["phase_id"] == "BN") == (p["region"] == "N 1s"), p

    # engine fit quality at least on par with the (rough) expert reference
    winner = res.diagnostics["winner"]
    top = next(c for c in res.analysis["candidates"] if c["name"] == winner)
    assert top["reduced_chi_sq"] <= rf.fit_result.get("chiReduced")
