"""
C 1s characterization battery — the Stage-2 parity / regression safety net.

Anchors (docs/autofit/phase1-grammar-architecture-spec-v2.md §3.1): the
expert C 1s fits in docs/autofit/test_data are the parity reference for the
autofit engine, and the seeded-refit records frozen in
fixtures/c1s_battery_expected.json pin today's ``fitting.run_fit`` numerics
so any unintentional change to the manual-fit path fails here first.

Three layers:

1. ``test_eval_parity_*`` — evaluating the saved peak params through
   fitting.py's lineshapes + run_fit's background reconstruction reproduces
   the saved ``fitResult.fittedY`` to ≤ 1e-5 relative (measured headroom:
   worst case 1.2e-7 across all 30 eligible fits).
2. ``test_refit_stability_*`` — a seeded, deterministic refit (leastsq,
   n_perturb=0) stays at the expert minimum: center drift ≤ 5 meV,
   FWHM/amplitude relative drift ≤ 0.5% (measured worst case: 2e-4).
3. ``test_battery_fixture_*`` — the same refit reproduces the frozen
   fixture records (χ²ᵣ, per-peak center/fwhm/amplitude/area) to tight
   tolerance.  Regenerate the fixture ONLY for reviewed, intentional
   numerics changes: ``venv/bin/python scripts/gen_c1s_battery_fixture.py``.

Tabs whose fit-time frame drifted from the saved ui state (charge correction
adjusted after fitting) and legacy saves without ``fitResult.be`` are
excluded by the same rules the generator applies, so fixture and battery
always agree on the roster.
"""

import glob
import json
import os

import numpy as np
import pytest

from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")
FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "c1s_battery_expected.json")

EVAL_PARITY_TOL = 1e-5          # measured worst case 1.2e-7
CENTER_DRIFT_TOL_EV = 0.005     # measured worst case 2e-4 eV
REL_DRIFT_TOL = 0.005           # FWHM / amplitude, measured worst case 1e-4
FIXTURE_CHI_RTOL = 1e-6
FIXTURE_PARAM_RTOL = 1e-6
MIN_BATTERY_SIZE = 25           # roster shrinking silently = data loss — fail


def _battery_fits():
    fits = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            if battery_eligible(rf, region="C 1s")[0]:
                fits.append(rf)
    return fits


_FITS = _battery_fits()
_IDS = [f"{rf.project}::{rf.name}" for rf in _FITS]


with open(FIXTURE) as _f:
    _EXPECTED = {(r["project"], r["name"]): r for r in json.load(_f)["records"]}


def test_battery_roster():
    assert len(_FITS) >= MIN_BATTERY_SIZE, (
        f"C 1s battery shrank to {len(_FITS)} fits (< {MIN_BATTERY_SIZE}) — "
        "reference data or eligibility rules changed"
    )
    projects = {rf.project for rf in _FITS}
    assert len(projects) >= 3, f"battery covers only {projects}"
    # fixture roster must match exactly
    assert {(rf.project, rf.name) for rf in _FITS} == set(_EXPECTED), (
        "battery roster no longer matches the frozen fixture — regenerate "
        "scripts/gen_c1s_battery_fixture.py only if this change is intentional"
    )


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_eval_parity(rf):
    relmax = eval_parity_relmax(rf)
    assert relmax < EVAL_PARITY_TOL, (
        f"{rf.project}/{rf.name}: python eval of saved params deviates from "
        f"saved fittedY by {relmax:.3e} (tol {EVAL_PARITY_TOL})"
    )


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_refit_stability_and_fixture(rf):
    rec = refit_record(rf)
    assert rec["success"], f"{rf.project}/{rf.name}: seeded refit did not converge"

    # (2) stays at the expert minimum
    by_id = {str(p["id"]): p for p in rf.peaks}
    for pk in rec["peaks"]:
        saved = by_id[str(pk["id"])]
        dc = abs(pk["center"] - saved["center"])
        dfw = abs(pk["fwhm"] - saved["fwhm"]) / max(saved["fwhm"], 1e-9)
        dam = abs(pk["amplitude"] - saved["amplitude"]) / max(abs(saved["amplitude"]), 1e-9)
        assert dc <= CENTER_DRIFT_TOL_EV, (
            f"{rf.name} peak {pk['id']}: center drifted {dc:.4f} eV from expert fit"
        )
        assert dfw <= REL_DRIFT_TOL, (
            f"{rf.name} peak {pk['id']}: fwhm drifted {dfw:.2%} from expert fit"
        )
        assert dam <= REL_DRIFT_TOL, (
            f"{rf.name} peak {pk['id']}: amplitude drifted {dam:.2%} from expert fit"
        )

    # (3) reproduces the frozen characterization record
    exp = _EXPECTED[(rf.project, rf.name)]
    assert np.isclose(
        rec["reduced_chi_square"], exp["reduced_chi_square"], rtol=FIXTURE_CHI_RTOL
    ), (
        f"{rf.name}: χ²ᵣ {rec['reduced_chi_square']} != frozen "
        f"{exp['reduced_chi_square']} — fitting.py numerics changed"
    )
    exp_peaks = {str(p["id"]): p for p in exp["peaks"]}
    for pk in rec["peaks"]:
        ep = exp_peaks[str(pk["id"])]
        for key in ("center", "fwhm", "amplitude", "area"):
            assert np.isclose(pk[key], ep[key], rtol=FIXTURE_PARAM_RTOL, atol=1e-9), (
                f"{rf.name} peak {pk['id']}: {key} {pk[key]} != frozen {ep[key]}"
            )
