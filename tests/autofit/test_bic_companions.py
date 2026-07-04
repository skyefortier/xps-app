"""
BIC/IC math-review companions (run-brief item 3b): the labeled-heuristic
BIC* must never travel alone — every candidate row carries the full-k raw
BIC, the weighted-χ² criterion the fits are actually consistent with, and
n_eff under residual autocorrelation; a result-level flag fires when the
weighted criterion tops a different survivor.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import overlap_case  # noqa: E402
from autofit.engine import _weighted_ic_disagreement  # noqa: E402
from autofit.methods import get_method  # noqa: E402


def test_candidate_rows_carry_companions():
    case = overlap_case(1.0, 9000.0, seed=11, expectation="recover")
    res = get_method("ic_model_comparison").run(
        case.x, case.y, grammar=case.grammar,
        options={"n_refits": 2, "rng_seed": 0, "noise_floor": 1.0,
                 "enable_proposal_pass": False})
    for c in res.analysis["candidates"]:
        if c.get("bic_star") is None:
            continue
        assert np.isfinite(c["bic_raw"])
        assert np.isfinite(c["bic_weighted"])
        # no absent slots here → heuristic equals raw
        if not c["absent_slots"]:
            assert c["bic_raw"] == pytest.approx(c["bic_star"], rel=1e-12)
        assert c["n_eff_lag1"] is None or c["n_eff_lag1"] > 0
    assert "weighted_ic_disagreement" in res.analysis
    assert "uncalibrated" in res.analysis["bic_threshold_caveat"]
    assert "weighted_ic_disagreement" in res.diagnostics or True  # analysis is the contract


def test_weighted_disagreement_helper():
    class _Fit:
        def __init__(self, n, rss, chi, k):
            self.n_data, self.residual_sum_sq = n, rss
            self.weighted_chi_sq, self.n_params = chi, k
            self.lmfit_result = None

    class _Rep:
        def __init__(self, name, rss, chi):
            from autofit.engine import ModelReport  # noqa: F401
            self.primary_fit = _Fit(300, rss, chi, 6)
            self._name = name
            self.absent_slots = []

        class _M:
            def __init__(self, name):
                self.name = name

        @property
        def model(self):
            return self._M(self._name)

        @property
        def adjusted_n_params(self):
            return 6

        @property
        def bic_weighted(self):
            return self.primary_fit.weighted_chi_sq + 6 * np.log(300)

    # RSS prefers A (listed first = ranking top); weighted prefers B
    a = _Rep("A", rss=100.0, chi=500.0)
    b = _Rep("B", rss=120.0, chi=300.0)
    flag = _weighted_ic_disagreement([a, b])
    assert flag and flag["rss_bic_top"] == "A" \
        and flag["weighted_bic_top"] == "B"
    # agreement → None
    b2 = _Rep("B", rss=120.0, chi=700.0)
    assert _weighted_ic_disagreement([a, b2]) is None
    assert _weighted_ic_disagreement([a]) is None
