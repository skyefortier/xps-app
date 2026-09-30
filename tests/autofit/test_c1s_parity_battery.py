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
from fit_equality import SAME_MINIMUM_REL

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")
FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "c1s_battery_expected.json")

EVAL_PARITY_TOL = 1e-5          # measured worst case 1.2e-7
CENTER_DRIFT_TOL_EV = 0.005     # measured worst case 2e-4 eV
REL_DRIFT_TOL = 0.005           # FWHM / amplitude, measured worst case 1e-4
# Unit A2 (2026-09-29): the refit is certified by Trust-Region restarts, so a
# refit the certificate moves carries Trust-Region's rounding (measured press
# to press <= 1.4e-6 relative): the fixture is compared WITHIN ROUNDING, on the
# scale of tests/fit_equality.py (10 x sqrt(ftol) = 1e-3; a centre to that
# fraction of the fitted energy span) — owner decision 2026-09-29.
FIXTURE_CHI_RTOL = SAME_MINIMUM_REL
FIXTURE_PARAM_RTOL = SAME_MINIMUM_REL
# The certificate showed four saved expert fits are NOT minima (unit A2,
# docs/findings/runfit-certificate/README.md). The old rule — the seeded
# refit stays within 5 meV / 0.5 % of the saved fit — held only because the
# optimiser's flag stopped the refit there. chi2r below is the saved fit's
# (main's refit, which did not move it); the certified refit must be LOWER.
# 8-JT C1s Scan_6 is not certified within CERTIFY_MAX_RESTARTS: a flat valley
# (106 restarts, chi2 -3.1 %, a zero-amplitude component resurrected as a
# 0.2 eV needle); the page's Run Fit (3 perturbed restarts) certifies its own
# model in 32 (Trust-Region) / 1 (Levenberg-Marquardt) restarts.
BEYOND_THE_EXPERT_FIT = {
    ("8-JT Graphite.proj.zip", "C1s Scan_2"): 5.49378,
    ("8-JT Graphite.proj.zip", "C1s Scan_3"): 5.99467,
    ("8-JT Graphite.proj.zip", "C1s Scan_5"): 6.94134,
    ("8-JT Graphite.proj.zip", "C1s Scan_6"): 8.95275,
}
NOT_CERTIFIED = {("8-JT Graphite.proj.zip", "C1s Scan_6")}
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
    key = (rf.project, rf.name)
    if key in NOT_CERTIFIED:
        assert not rec["success"], f"{rf.project}/{rf.name}: now certified — update NOT_CERTIFIED"
    else:
        assert rec["success"], f"{rf.project}/{rf.name}: seeded refit did not converge"

    # (2) stays at the expert minimum — or, where the certificate showed the
    # saved fit is not one, descends below it
    by_id = {str(p["id"]): p for p in rf.peaks}
    if key in BEYOND_THE_EXPERT_FIT:
        assert rec["reduced_chi_square"] < BEYOND_THE_EXPERT_FIT[key], (
            f"{rf.name}: the certified refit did not descend below the saved fit")
    for pk in rec["peaks"] if key not in BEYOND_THE_EXPERT_FIT else []:
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
    assert rec["success"] == exp["success"], f"{rf.name}: the verdict changed"
    exp_peaks = {str(p["id"]): p for p in exp["peaks"]}
    span = float(np.ptp(np.asarray(rf.roi_be, float)))
    for pk in rec["peaks"]:
        ep = exp_peaks[str(pk["id"])]
        for field in ("center", "fwhm", "amplitude", "area"):
            if field == "center":
                close = abs(pk[field] - ep[field]) <= FIXTURE_PARAM_RTOL * span
            else:
                close = np.isclose(pk[field], ep[field], rtol=FIXTURE_PARAM_RTOL, atol=1e-9)
            assert close, f"{rf.name} peak {pk['id']}: {field} {pk[field]} != frozen {ep[field]}"
