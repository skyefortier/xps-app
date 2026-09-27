"""Unit F2 (2026-09-26), sweep H2: basinhopping's convergence.

lmfit 1.3 marks every basinhopping fit successful (it sets success before
minimising and never reads scipy's result). scipy's own flag is no verdict
either: on 23 of 24 sampled committed targets it reports BFGS "precision
loss" at a point equal to Trust-Region's minimum. Owner decision: the
differential-evolution pattern in full — the search, an unconditional
least_squares refinement from its point under the request's bounds (the
refinement's convergence is the verdict), then a competition with a
least_squares fit from the same start (verified beats unverified, then the
lower chi-square), so basinhopping is never worse than the default method.
"""

import numpy as np
import pytest

import fitting


def _gl(x, a, c, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


X = np.linspace(280.0, 292.0, 121)


def _two_peaks():
    y = np.round(200 + _gl(X, 5000, 284.8, 1.2) + _gl(X, 1800, 286.4, 1.3), 2)
    specs = [
        {"id": "1", "shape": "gaussian", "center": 284.6, "fwhm": 1.0, "amplitude": 4000.0, "amplitude_min": 0},
        {"id": "2", "shape": "gaussian", "center": 286.6, "fwhm": 1.0, "amplitude": 1500.0, "amplitude_min": 0},
    ]
    return y, specs


def _spy(monkeypatch, fail_methods=()):
    calls = []
    real = fitting.Model.fit

    def spy(self, data, params, **kw):
        res = real(self, data, params, **kw)
        calls.append(kw.get("method"))
        if kw.get("method") in fail_methods:
            res.success = False
        return res

    monkeypatch.setattr(fitting.Model, "fit", spy)
    return calls


def test_a_basinhopping_fit_is_the_refined_least_squares_result_and_never_worse_than_the_default():
    y, specs = _two_peaks()
    kw = dict(background_method="linear", n_perturb=0)
    bh = fitting.run_fit(X, y, specs, fit_kws={"method": "basinhopping"}, **kw)
    tr = fitting.run_fit(X, y, specs, fit_kws={"method": "least_squares"}, **kw)
    assert bh["success"] is True
    assert bh["statistics"]["reduced_chi_square"] <= tr["statistics"]["reduced_chi_square"] * (1 + 1e-12)
    # the returned result carries least_squares uncertainties (the refinement or the competitor)
    assert all(ip["params"]["center"]["stderr"] is not None for ip in bh["individual_peaks"])


def test_the_call_sequence_is_search_refine_compete(monkeypatch):
    calls = _spy(monkeypatch)
    y, specs = _two_peaks()
    fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
    assert calls == ["basinhopping", "least_squares", "least_squares"]


def test_an_unverifiable_search_does_not_converge_when_the_competitor_fails_too(monkeypatch):
    # every least_squares (the refinement AND the competitor) reports failure:
    # nothing verified the point, so it is not a converged fit — the old
    # behaviour returned lmfit's unconditional success here
    _spy(monkeypatch, fail_methods=("least_squares",))
    y, specs = _two_peaks()
    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
    assert res["success"] is False
    assert "not a verified fit" in res["message"]


def test_a_failed_refinement_is_rescued_by_a_converged_competitor(monkeypatch):
    real = fitting.Model.fit
    seen = []

    def spy(self, data, params, **kw):
        res = real(self, data, params, **kw)
        seen.append(kw.get("method"))
        if kw.get("method") == "least_squares" and seen.count("least_squares") == 1:
            res.success = False                  # the refinement from the search's point
        return res

    monkeypatch.setattr(fitting.Model, "fit", spy)
    y, specs = _two_peaks()
    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "basinhopping"})
    assert res["success"] is True, res["message"]


def test_the_required_refit_goes_through_the_same_verification(monkeypatch):
    calls = _spy(monkeypatch)
    y, specs = _two_peaks()
    res = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0, require_component="2",
                          fit_kws={"method": "basinhopping"})
    # the main fit and the required refit: two verified candidates
    assert calls.count("basinhopping") == 2
    assert calls.count("least_squares") == 4
    assert res["required"]["ran"] is True and res["required"]["refit_converged"] is True


def test_basinhopping_runs_no_perturbed_restarts(monkeypatch):
    # a global search already; with the page's n_perturb 3 the restarts took it
    # past the 300 s server timeout on 14 of 16 multi-component targets
    calls = _spy(monkeypatch)
    y, specs = _two_peaks()
    with_restarts_asked = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=3,
                                          fit_kws={"method": "basinhopping"})
    assert calls.count("basinhopping") == 1
    assert with_restarts_asked["success"] is True
    # the answer is the one the same request without restarts gets
    without = fitting.run_fit(X, y, specs, background_method="linear", n_perturb=0,
                              fit_kws={"method": "basinhopping"})
    assert with_restarts_asked["statistics"]["reduced_chi_square"] == pytest.approx(
        without["statistics"]["reduced_chi_square"], rel=1e-9)
    # differential evolution and the local methods still run the restarts they are asked for
    calls.clear()
    fitting.run_fit(X, y, specs, background_method="linear", n_perturb=2, fit_kws={"method": "leastsq"})
    assert calls.count("leastsq") == 3
