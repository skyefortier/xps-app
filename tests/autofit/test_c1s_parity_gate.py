"""
Stage-2 C 1s parity gate (spec §0/§3.1): the resolver + IC engine must
reproduce the expert C 1s reference fits within tolerance.

Parity is defined on what the grammar and the expert fits AGREE on
physically — not peak-by-peak equality, because the expert fits use freer
width conventions than the grammar caps (adventitious FWHM up to 2.66 eV
vs the ADJUDICATED uniform 2.0 eV cap — adjudication-decisions.md #5,
2026-07-03; the cap is the ruling, so exact width parity with the broadest
expert components is not expressible by construction).

Gate assertions per anchor spectrum:
1. the engine finds >= 1 surviving candidate (no forced answer, but the
   anchors are good-quality spectra — zero survivors means the grammar or
   pipeline regressed);
2. the winner's graphitic main lands within MAIN_CENTER_TOL of the expert
   graphite peak;
3. the winner includes the π→π* satellite within SATELLITE_TOL of the
   expert satellite;
4. envelope-level agreement: R-factor between the engine winner's envelope
   and the expert's saved fittedY below ENVELOPE_R_TOL.

Runtime: even reduced (3 candidates, 4 refits, proposal pass off) this takes
several minutes per anchor, so it is gated behind RUN_AUTOFIT_GATE=1 — run it
at stage checkpoints and after grammar/engine changes:

    RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_c1s_parity_gate.py

The always-on fast regression net is tests/autofit/test_c1s_parity_battery.py;
the FULL 25-candidate calibration is scripts/run_c1s_full_calibration.py.
"""

import os

import numpy as np
import pytest

if os.environ.get("RUN_AUTOFIT_GATE") != "1":
    # LOUD skip (Codex Stage-2 finding #8): this is a REQUIRED Stage-2 gate.
    # A default run does not enforce it — the always-on parity net is the
    # characterization battery.  Run this gate at every stage checkpoint and
    # after any grammar/engine change:  RUN_AUTOFIT_GATE=1 pytest <this file>
    pytest.skip(
        "SKIPPING REQUIRED STAGE GATE (C 1s parity) — slow; set "
        "RUN_AUTOFIT_GATE=1 to enforce. Do not treat a run without it as a "
        "full Stage-2 verification.",
        allow_module_level=True,
    )

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.parity import evaluate_model
from autofit.reference import load_reference_fits
from fitting import shirley_background

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")

ANCHORS = [
    ("UCl4_on_graphite.proj.zip", "C1s Scan_8"),
    ("8-JT Graphite.proj.zip", "C1s Scan_2"),
    ("1-GTA UCl4-graphite one set of U doublets.proj.zip", "C1s Scan_6"),
]

# Reduced representative candidate set: the MG expert-structure family, the
# AG lab-practice family, and a Biesinger-convention A competitor.
GATE_CANDIDATES = [
    "MG2_graphAsymGL_aliph_sat_CO_C=O",
    "MG3_graphAsymGL_aliph_sat_CO_C=O_OC=O",
    "AG2_linked",
    "A2_linked",
]

# Calibrated 2026-07-03; RE-calibrated 2026-07-04 under the adjudicated
# uniform 2.0 eV contamination cap (see PROGRESS.md parity-gate calibration
# log).  Measured mains: Scan_2 4 meV (clean MG2), Scan_6 12 meV (clean
# AG2), Scan_8 54 meV — the UCl4-composite anchor's expert adventitious
# widths (median 2.08 eV) exceed the cap, so its MG/AG candidates go
# boundary-limited/unstable and the winner drops to the conditional
# no_clean_survivor tier (A2_linked).  That anchor's degradation is the
# adjudicated convention meeting data that prefers wider components —
# expected, documented, not silently forced.
MAIN_CENTER_TOL_EV = 0.08
SATELLITE_TOL_EV = 0.5
# Measured domain envelope R 2026-07-04 under the adjudicated cap:
# Scan_2/Scan_6 unchanged (0.004–0.014); Scan_8 0.0407 (conditional-tier
# winner — same cap-vs-data cause as the main-center recalibration above).
ENVELOPE_R_TOL = 0.05     # Σ|engine−expert| / Σ|expert|, BE ≥ ENVELOPE_DOMAIN_MIN
# The expert fits model a low-BE 'Unknown' (~283.4 eV) that sits outside every
# grammar window (PROGRESS.md discrepancy #6 — proposal-pass territory, which
# the gate disables for runtime).  Envelope parity is asserted on the
# grammar's domain.
ENVELOPE_DOMAIN_MIN = 284.0

GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")


def _anchor(project, name):
    path = os.path.join(DATA, project)
    rf = next(r for r in load_reference_fits(path) if r.name == name)
    return rf


@pytest.fixture(scope="module")
def grammar():
    return resolve([GRAPHITE], "C 1s")


@pytest.mark.parametrize("project,name", ANCHORS,
                         ids=[f"{p}::{n}" for p, n in ANCHORS])
def test_c1s_parity_gate(grammar, project, name):
    rf = _anchor(project, name)
    expert_by_name = { (p.get("name") or "").lower(): p for p in rf.peaks }
    expert_graphite = next(v for k, v in expert_by_name.items() if "graphit" in k)
    expert_satellite = next((v for k, v in expert_by_name.items()
                             if "satellite" in k or "π" in k), None)

    res = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar,
        options={"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
                 "candidate_filter": GATE_CANDIDATES,
                 "enable_proposal_pass": False},
    )

    # (1) a survivor exists — clean tier preferred, conditional tier accepted
    # WITH its violations surfaced (two-tier semantics; on these composite
    # samples some lit-convention constraint typically binds somewhere)
    assert res.success, (
        f"{name}: no surviving candidate — {res.message}\n"
        + "\n".join(f"  {c['name']}: {c['filter_reason']}"
                    for c in res.analysis["candidates"])
    )
    if res.diagnostics["conditional"]:
        if res.diagnostics["conditional_reason"] == "decisive_override":
            # winner is a bound-fixed refit: constraint evidence lives in the
            # list of parameters fixed at their bounds
            assert res.diagnostics["winner_boundary_fixed_params"], (
                "override winner must record its bound-fixed parameters"
            )
        else:
            assert res.diagnostics["winner_boundary_hits"], (
                "conditional winner must carry its constraint violations"
            )

    # (2) graphitic main position parity
    main = next(p for p in res.peaks if p["role"] == "main_graphitic")
    dc = abs(main["center"] - expert_graphite["center"])
    assert dc <= MAIN_CENTER_TOL_EV, (
        f"{name}: engine graphitic main {main['center']:.3f} vs expert "
        f"{expert_graphite['center']:.3f} (Δ {dc*1000:.0f} meV)"
    )

    # (3) satellite present and positioned
    if expert_satellite is not None:
        sat = next((p for p in res.peaks if p["role"] == "satellite_pi"), None)
        assert sat is not None, f"{name}: winner has no π→π* satellite slot"
        ds = abs(sat["center"] - expert_satellite["center"])
        assert ds <= SATELLITE_TOL_EV, (
            f"{name}: satellite {sat['center']:.3f} vs expert "
            f"{expert_satellite['center']:.3f} (Δ {ds:.2f} eV)"
        )

    # (4) envelope-level parity vs the expert's saved envelope
    specs = []
    for p in res.peaks:
        spec = dict(p)
        spec.pop("role", None); spec.pop("region", None)
        spec.pop("phase_id", None); spec.pop("stderr", None)
        specs.append(spec)
    engine_env = evaluate_model(rf.roi_be, specs) + shirley_background(
        rf.roi_be, rf.roi_intensity)
    expert_env = np.asarray(rf.fit_result["fittedY"], dtype=float)
    dom = rf.roi_be >= ENVELOPE_DOMAIN_MIN
    r_factor = float(np.sum(np.abs(engine_env[dom] - expert_env[dom]))
                     / np.sum(np.abs(expert_env[dom])))
    assert r_factor <= ENVELOPE_R_TOL, (
        f"{name}: domain envelope R-factor {r_factor:.4f} > {ENVELOPE_R_TOL} "
        f"(winner {res.diagnostics['winner']})"
    )
