"""
U 4f UNRESOLVED-model-selection gate (env-gated; Codex Stage-5 re-check
blocker): the exact motivating real-data case — on the B4C-UCl4 U 4f anchor
the top-2 Bayesian candidates (U1b free-pair-separation vs U2 free
satellites) flip winner between seeds at every budget tried
(default 1500 sweeps: seed 0 U1b F=2803.2 < U2 2806.3, seed 1 U2 2800.1 <
U1b 2806.6; at 800 sweeps seed 0 even reports gap 12.3 with split-half
error 0.5 — a false 'resolved', proving the split-half proxy alone is a
lower bound that can miss it).

The honest mechanism is INDEPENDENT SEED REPLICATION (`seed_replicates`):
the across-replicate F spread feeds `free_energy_mc_error`, and with the
flip inside the replicates the UNRESOLVED warning fires deterministically.
This gate pins that contract on the real spectrum.

    RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_bayesian_u4f_unresolved_gate.py
"""

import os

import pytest

if os.environ.get("RUN_AUTOFIT_GATE") != "1":
    pytest.skip(
        "SKIPPING U 4f unresolved-selection gate (~8 min) — set "
        "RUN_AUTOFIT_GATE=1 to enforce.",
        allow_module_level=True,
    )

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")

UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
             regions=("U 4f", "Cl 2p"))


def test_u4f_replicated_selection_is_flagged_unresolved():
    rf = next(r for r in load_reference_fits(
        os.path.join(DATA, "B4C-UCl4.proj.zip")) if r.name == "U4f Scan")
    res = get_method("bayesian_exchange_mc").run(
        rf.roi_be, rf.roi_intensity, grammar=resolve([UCL4], "U 4f"),
        options={"n_sweeps": 800, "rng_seed": 0, "seed_replicates": 2,
                 "candidate_filter": ["U1b_mains_satpair_freesep",
                                      "U2_mains_satfree"]})
    assert res.success, res.message

    scored = [c for c in res.analysis["candidates"] if "free_energy" in c]
    assert len(scored) == 2
    for c in scored:
        assert c["free_energy_replicates"] and len(c["free_energy_replicates"]) == 2
        assert c["free_energy_replicate_spread"] is not None
        assert c["free_energy_mc_error"] >= c["free_energy_replicate_spread"] \
            or c["free_energy_mc_error"] >= (c["free_energy_split_half_error"] or 0)
        assert c["posterior_weight_reliable"] is False, c["name"]

    warning = res.analysis["model_selection_warning"]
    assert warning and "UNRESOLVED" in warning, (
        "the U1b/U2 comparison must be flagged unresolved under seed "
        f"replication — got {warning!r}")
