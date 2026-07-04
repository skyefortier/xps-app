"""
Bayesian exchange-MC REAL-DATA gate (env-gated like the C 1s parity gate):
pins the cross-method agreement on the corrected Cl 2p anchor that the
full validation battery established (docs/autofit/bayesian-real-validation.md,
JSONL evidence in docs/autofit/inventory/bayesian_real_validation_runs.jsonl).

Battery evidence (2026-07-03): winner `Cl0r_doublet_relaxed` on every
default/seed/tunable variation (seeds 0/1; replicas 8/12/16; beta_min 1e-4/
1e-3; sweeps 1500/3000; exchange_every 1/5; burn 0.3/0.5), ΔF to the fixed-
ratio candidate 46–49, σ̂ 81.3–81.5 counts, min-ESS honesty warning firing
on the boundary-piled ratio chain.  The IC method's decisive-override winner
is the same model (mod +bfix).  Gate asserts those invariants with margin at
reduced sweeps.

    RUN_AUTOFIT_GATE=1 venv/bin/pytest tests/autofit/test_bayesian_real_gate.py
"""

import os

import pytest

if os.environ.get("RUN_AUTOFIT_GATE") != "1":
    pytest.skip(
        "SKIPPING Bayesian real-data gate (~1 min) — set RUN_AUTOFIT_GATE=1 "
        "to enforce; the synthetic battery in test_bayesian_method.py remains "
        "always-on.",
        allow_module_level=True,
    )

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")

UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
             regions=("U 4f", "Cl 2p"))


def test_cl2p_bayes_ic_cross_method_agreement():
    rf = next(r for r in load_reference_fits(
        os.path.join(DATA, "Cl2p_projfit_test.proj.zip")) if r.name == "Cl2p Scan")
    grammar = resolve([UCL4], "Cl 2p")

    bayes = get_method("bayesian_exchange_mc").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar,
        options={"n_sweeps": 800, "rng_seed": 0})
    assert bayes.success, bayes.message
    assert bayes.diagnostics["winner"] == "Cl0r_doublet_relaxed"

    cands = {c["name"]: c for c in bayes.analysis["candidates"]
             if "free_energy" in c}
    dF = cands["Cl0_doublet"]["free_energy"] - \
        cands["Cl0r_doublet_relaxed"]["free_energy"]
    assert dF > 10.0, f"relaxed-ratio evidence collapsed: ΔF={dF:.1f}"

    # σ̂ band measured 81.3–81.5 across the battery; generous margin
    assert 60.0 < bayes.diagnostics["sigma_hat"] < 110.0

    # honesty machinery: the ratio posterior piles at the 0.55 bound, so the
    # min-ESS warning MUST fire — its absence means the warning logic broke
    winner = cands["Cl0r_doublet_relaxed"]
    assert winner["ci_reliability_warning"], (
        "expected LOW-ESS warning on the boundary-piled ratio chain")

    ic = get_method("ic_model_comparison").run(
        rf.roi_be, rf.roi_intensity, grammar=grammar,
        options={"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
                 "enable_proposal_pass": False})
    assert ic.success
    assert ic.diagnostics["winner"].replace("+bfix", "") == \
        bayes.diagnostics["winner"], (
        "IC and Bayesian methods no longer agree on the Cl 2p anchor")
