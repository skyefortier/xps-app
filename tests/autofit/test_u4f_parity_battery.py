"""
U 4f characterization battery — pins the MANUAL fit path's LACX + linked
spin-orbit doublet + Voigt satellite numerics against 29 expert reference
fits (structure mirrors test_c1s_parity_battery.py; shared logic in
battery_common.py).

Regenerate the fixture ONLY for reviewed numerics changes:
    venv/bin/python scripts/gen_u4f_battery_fixture.py
"""

import pytest

import battery_common as bc

REGION = "U 4f"
FIXTURE = "u4f_battery_expected.json"
MIN_BATTERY_SIZE = 20
MIN_PROJECTS = 3
# Bounded by background-anchor drift / LACX FP wobble — measured and
# documented in battery_common.py.  The worst LACX tab (UCl4_on_graphite
# U4f Scan_6, a flat alpha/beta/m valley) wobbles at 1.4e-4 relative
# across PROCESSES on one platform, but 1.9e-3 across PLATFORMS (first CI
# run on ubuntu/openBLAS vs the macOS/arm64 fixture, 2026-07-04 — fwhm
# 3.00971 vs frozen 3.00396 on that tab).  3e-3 covers the measured
# cross-platform wobble with ~1.6x headroom while still catching any real
# numerics change (C 1s pins the shared machinery at 1e-6).
# Eval-parity across all 29 eligible fits: median 6.0e-3, max 1.12e-2
# (bg-anchor drift) — 1.5e-2 keeps ~34% headroom without masking a real
# 2%-level regression (Codex Stage-3 finding #4).
EVAL_TOL = 1.5e-2
FIXTURE_RTOL = 3e-3

_FITS = bc.battery_fits(REGION)
_IDS = [f"{rf.project}::{rf.name}" for rf in _FITS]
_EXPECTED = bc.load_fixture(FIXTURE)


def test_battery_roster():
    bc.assert_roster(_FITS, _EXPECTED, MIN_BATTERY_SIZE, MIN_PROJECTS,
                     "scripts/gen_u4f_battery_fixture.py")


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_eval_parity(rf):
    bc.assert_eval_parity(rf, tol=EVAL_TOL)


@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
def test_refit_stability_and_fixture(rf):
    bc.assert_refit_stability_and_fixture(rf, _EXPECTED,
                                          fixture_rtol=FIXTURE_RTOL)
