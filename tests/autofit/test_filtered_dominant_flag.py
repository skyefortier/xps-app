"""
Result-level `filtered_dominant_alternative` flag (stress-suite finding 0:
the filter-then-rank pipeline buried candidates that beat the winner by
ΔBIC* +74…+944 with no result-level trace).

The flag is purely additive — ranking/filtering/promotion unchanged — and
must fire on the measured burial case (sub-FWHM doublet at high counts:
stable P2 orphan-filtered, clean P1 emitted) and stay None on clean wins.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import overlap_case, overspecified_case  # noqa: E402
from autofit.methods import get_method  # noqa: E402

OPTS = {"n_refits": 4, "rng_seed": 0, "noise_floor": 1.0,
        "enable_proposal_pass": False}


def _ic(case):
    return get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar, options=dict(OPTS))


def test_burial_case_fires_result_level_flag():
    case = overlap_case(0.4, 9000.0, seed=13, expectation="recover")
    res = _ic(case)
    assert res.diagnostics["winner"] == "P1"
    flag = res.diagnostics["filtered_dominant_alternative"]
    assert flag is not None
    assert flag["name"] == "P2"
    assert flag["delta_bic_vs_winner"] > 10.0
    assert flag["filter_reason"]
    # mirrored in the analysis namespace and the human-facing message
    assert res.analysis["filtered_dominant_alternative"]["name"] == "P2"
    assert "beats this winner" in res.message


def test_clean_win_has_no_flag():
    case = overspecified_case(seed=31)
    res = _ic(case)
    assert res.diagnostics["winner"] == "P2"
    assert res.diagnostics["filtered_dominant_alternative"] is None
    assert "beats this winner" not in res.message
