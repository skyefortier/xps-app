"""
U 4f characterization battery — pins the MANUAL fit path's LACX + linked
spin-orbit doublet + Voigt satellite numerics against 29 expert reference
fits (structure mirrors test_c1s_parity_battery.py; shared logic in
battery_common.py).

Regenerate the fixture ONLY for reviewed numerics changes:
    venv/bin/python scripts/gen_u4f_battery_fixture.py

A03 (2026-09-22): the page now sends a Voigt with eta HELD at 0.5 (the mix
it has always drawn); the 29 expert U 4f fits were saved under the old
request (eta free from 0.3, ending at pure Gaussian or pure Lorentzian on
most satellites), so their saved parameters belong to another model and a
refit under today's request moves the LACX main line's width by up to 7.7 %
and its centre by up to 8 meV (the satellites' tails changed). The fixture
was regenerated for that reviewed change, and stationarity is measured
against a refit FROM the refit (battery_common, stationarity="refit"): the
fitter's own fixed point, not the pre-A03 save.
"""

import pytest

import battery_common as bc

REGION = "U 4f"
FIXTURE = "u4f_battery_expected.json"
MIN_BATTERY_SIZE = 20
MIN_PROJECTS = 3
# FIXTURE_RTOL (refit numerics): the worst LACX tab (UCl4_on_graphite U4f
# Scan_6, a flat alpha/beta/m valley) wobbles at 1.4e-4 relative across
# PROCESSES on one platform, but 1.9e-3 across PLATFORMS (first CI run on
# ubuntu/openBLAS vs the macOS/arm64 fixture, 2026-07-04 — fwhm 3.00971 vs
# frozen 3.00396 on that tab): that is OPTIMISED-parameter drift. 3e-3
# covers it with ~1.6x headroom while still catching any real numerics
# change (C 1s pins the shared machinery at 1e-6).
# EVAL_TOL (fixed-parameter evaluation, a different quantity): across the 29
# eligible fits, each Voigt evaluated with the mix the server recorded for
# the saved fit (A03 round 5), median 2.0e-7, max 7.9e-4 — the maximum on
# 4-GTA UCl4-BN / U4f Scan, whose LACX lines have m = 0, so it is not the
# convolution (the recomputed 'smart' background is the candidate; not
# attributed). The 6.0e-3 / 1.12e-2 measured before A03 and read as
# "bg-anchor drift" was the twin evaluating every Voigt at 0.3 against
# curves fitted with eta free. 3e-3 keeps ~4x headroom over the measured
# maximum.
EVAL_TOL = 3e-3
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
                                          fixture_rtol=FIXTURE_RTOL,
                                          stationarity="refit")
