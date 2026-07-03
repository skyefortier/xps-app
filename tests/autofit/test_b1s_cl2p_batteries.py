"""
B 1s and Cl 2p characterization batteries (manual fit path; shared logic in
battery_common.py).  Small rosters — the labeled sets are small (B 1s: 4
eligible incl. 3 known-rough 4-GTA tabs, still valid as numeric pins;
Cl 2p: 3, incl. the uncorrected Scan_1).

Regenerate fixtures ONLY for reviewed numerics changes:
    venv/bin/python scripts/gen_region_battery_fixture.py "B 1s" b1s_battery_expected.json
    venv/bin/python scripts/gen_region_battery_fixture.py "Cl 2p" cl2p_battery_expected.json
"""

import pytest

import battery_common as bc

_B1S = bc.battery_fits("B 1s")
_B1S_EXPECTED = bc.load_fixture("b1s_battery_expected.json")
_CL2P = bc.battery_fits("Cl 2p")
_CL2P_EXPECTED = bc.load_fixture("cl2p_battery_expected.json")

# Cl 2p eval parity is bounded by the same bg-anchor drift documented in
# battery_common.py (measured: 1.7e-2 on the uncorrected Scan_1 tab;
# ≤6.8e-7 on the corrected tabs).
CL2P_EVAL_TOL = 2.5e-2


def test_b1s_roster():
    bc.assert_roster(_B1S, _B1S_EXPECTED, min_size=3, min_projects=2,
                     gen_script="scripts/gen_region_battery_fixture.py 'B 1s'")


def test_cl2p_roster():
    bc.assert_roster(_CL2P, _CL2P_EXPECTED, min_size=2, min_projects=1,
                     gen_script="scripts/gen_region_battery_fixture.py 'Cl 2p'")


@pytest.mark.parametrize("rf", _B1S, ids=[f"{r.project}::{r.name}" for r in _B1S])
def test_b1s_eval_parity(rf):
    bc.assert_eval_parity(rf)


@pytest.mark.parametrize("rf", _B1S, ids=[f"{r.project}::{r.name}" for r in _B1S])
def test_b1s_refit_stability_and_fixture(rf):
    bc.assert_refit_stability_and_fixture(rf, _B1S_EXPECTED)


@pytest.mark.parametrize("rf", _CL2P, ids=[f"{r.project}::{r.name}" for r in _CL2P])
def test_cl2p_eval_parity(rf):
    bc.assert_eval_parity(rf, tol=CL2P_EVAL_TOL)


@pytest.mark.parametrize("rf", _CL2P, ids=[f"{r.project}::{r.name}" for r in _CL2P])
def test_cl2p_refit_stability_and_fixture(rf):
    bc.assert_refit_stability_and_fixture(rf, _CL2P_EXPECTED)
