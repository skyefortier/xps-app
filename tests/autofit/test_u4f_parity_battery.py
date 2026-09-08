"""
U 4f migration battery for corrected LA convolution (2026-09-08).

The original fixture remains historical evidence, not a numerical oracle
for the repaired profile. Check independently evaluated curves, seed-objective
improvement and exact constraints, plus bounded migration from legacy fits.
See docs/repairs-2026-09-08/u4f-numerical-migration.json for characterization.
These compatibility bounds do not establish experimental accuracy.
"""

import numpy as np
import pytest
from scipy.ndimage import gaussian_filter1d
from scipy.integrate import trapezoid

from fitting import run_fit

import battery_common as bc

REGION = "U 4f"
FIXTURE = "u4f_battery_expected.json"
MIN_BATTERY_SIZE = 20
MIN_PROJECTS = 3
# Keep the existing saved-curve compatibility limit, which includes drift
# in saved background anchors. New model checks below use a tight oracle.
EVAL_TOL = 1.5e-2
# Explicit migration budgets: retain the existing 0.005 eV center guard;
# allow at most 1% change in widths/heights/areas and chi-square. These
# engineering budgets intentionally exceed observed changes (max 0.89%)
# and must not be interpreted as confidence intervals or science tolerances.
CENTER_MIGRATION_EV = 0.005
REL_MIGRATION = 0.01

_FITS = bc.battery_fits(REGION)
_IDS = [f"{rf.project}::{rf.name}" for rf in _FITS]
_EXPECTED = bc.load_fixture(FIXTURE)


def test_battery_roster():
    bc.assert_roster(_FITS, _EXPECTED, MIN_BATTERY_SIZE, MIN_PROJECTS,
                     "scripts/gen_u4f_battery_fixture.py")


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_eval_parity(rf):
    bc.assert_eval_parity(rf, tol=EVAL_TOL)


def _independent_profile(x, spec):
    """Closed GL formula / SciPy Gaussian-filter oracle; no fitting shapes."""
    amplitude, center, width = (spec[k] for k in ("amplitude", "center", "fwhm"))
    if spec["shape"] == "la_casaxps":
        def core(e):
            return (1 + (2 * e / width) ** 2) ** -np.where(
                e >= 0, spec["alpha"], spec["beta"])
        sigma = spec["m"] / 3
        if spec["m"] < .001:
            return amplitude * core(x - center)
        spacing = x[1] - x[0]
        radius = max(1, int(np.ceil(8 * sigma)))
        padded = x[0] + np.arange(-radius, len(x) + radius) * spacing
        # Analytic tails fill the padding. SciPy's boundary extension cannot
        # reach the retained samples, so it has no influence on the oracle.
        curve = gaussian_filter1d(core(padded - center), sigma, radius=radius)
        center_grid = np.arange(-radius, radius + 1) * spacing
        normalization = gaussian_filter1d(core(center_grid), sigma,
                                          radius=radius)[radius]
        return amplitude * curve[radius:-radius] / normalization
    assert spec["shape"] in ("pseudo_voigt_gl", "asymmetric_gl")
    if spec["shape"] == "asymmetric_gl":
        width = np.where(x > center, width * (1 + spec["asymmetry"]), width)
    scaled = (x - center) / width
    eta = spec["gl_ratio"]
    return amplitude * ((1 - eta) * np.exp(-4 * np.log(2) * scaled ** 2)
                        + eta / (1 + 4 * scaled ** 2))


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_refit_numerical_migration(rf):
    specs = rf.backend_peak_specs()
    x, y = rf.roi_be, rf.roi_intensity
    i0, i1 = rf.bg_indices()
    result = run_fit(x, y, specs, background_method=rf.bg_method,
                     bg_start_idx=i0, bg_end_idx=i1,
                     endpoint_avg=rf.endpoint_avg, n_perturb=0)
    assert result["success"], result["message"]
    bg = np.asarray(result["background_y"])
    seed_curve = sum((_independent_profile(x, p) for p in specs), np.zeros_like(x))
    seed_objective = np.sum((y - bg - seed_curve) ** 2 / np.maximum(y, 1))
    assert result["statistics"]["chi_square"] <= seed_objective * (1 + 1e-8)

    by_id = {p["id"]: p for p in result["individual_peaks"]}
    legacy = _EXPECTED[(rf.project, rf.name)]
    legacy_peaks = {str(p["id"]): p for p in legacy["peaks"]}
    independent_sum = np.zeros_like(x)
    for spec in specs:
        peak = by_id[spec["id"]]
        values = {k: v["value"] for k, v in peak["params"].items()}
        curve = _independent_profile(x, dict(spec, **values))
        np.testing.assert_allclose(peak["y"], curve, rtol=2e-10, atol=1e-8)
        independent_sum += curve
        area = abs(trapezoid(curve, x))
        assert np.isclose(values["area"], area, rtol=2e-10)
        frozen = legacy_peaks[spec["id"]]
        for reference in (spec, frozen):
            assert abs(values["center"] - reference["center"]) <= CENTER_MIGRATION_EV
            for key in ("fwhm", "amplitude"):
                assert np.isclose(values[key], reference[key], rtol=REL_MIGRATION)
        assert np.isclose(area, frozen["area"], rtol=REL_MIGRATION)
        if spec.get("constrain_to"):
            parent = by_id[spec["constrain_to"]]["params"]
            assert np.isclose(values["center"], parent["center"]["value"] + spec["splitting"],
                              rtol=0, atol=1e-10)
            assert np.isclose(values["amplitude"], parent["amplitude"]["value"] * spec["area_ratio"],
                              rtol=1e-12)
            for key in ("fwhm", "alpha", "beta", "m", "gl_ratio", "asymmetry"):
                if key in values:
                    assert values[key] == parent[key]["value"]
    np.testing.assert_allclose(result["fitted_y"], independent_sum + bg,
                               rtol=2e-10, atol=1e-8)
    assert np.isclose(result["statistics"]["reduced_chi_square"],
                      legacy["reduced_chi_square"], rtol=REL_MIGRATION)
