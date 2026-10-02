"""Unit A2 (2026-09-29): Run Fit's fits are judged by the minimum CERTIFICATE,
not by the optimiser's success flag — the RETURNED fit (after the fit and its
perturbed restarts have run exactly as before: owner decision, variant V3),
every scattered start and the required-component refit, for the local methods
(leastsq, least_squares, nelder). Restart Trust-Region from the
end point until a restart improves chi2 by less than Trust-Region's own ftol;
at most CERTIFY_MAX_RESTARTS restarts; out of restarts, a non-finite, raising
or evaluation-capped restart = not converged. The scope check
(docs/findings/fit-termination-scope/) found the flag wrong both ways."""
import inspect

import numpy as np
import pytest
import scipy.optimize

import fitting
from _legacy_line import legacy_line  # noqa: F401,E402  (autouse: the fixtures' background arithmetic)


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _problem():
    rng = np.random.default_rng(3)
    x = np.arange(280.0, 295.0, 0.1)
    y = rng.poisson(200.0 + _g(x, 284.8, 4000.0, 1.1) + _g(x, 288.6, 900.0, 1.4)).astype(float)
    specs = [{"id": 1, "shape": "pseudo_voigt_gl", "center": 284.6, "amplitude": 3500.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": 2, "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0}]
    return x, y, specs


def _far(specs):
    """A start from which a loose-tolerance fit stops well short."""
    return [{**specs[0], "center": 284.1, "fwhm": 2.4, "amplitude": 1500.0}, {**specs[1], "amplitude": 100.0, "fwhm": 2.6}]


KW = dict(background_method="linear", n_perturb=0)


def _values(res):
    return [{k: v["value"] for k, v in p["params"].items()} for p in res["individual_peaks"]]


def test_the_tolerance_is_the_optimisers_own():
    assert fitting.CERTIFY_FTOL == inspect.signature(scipy.optimize.least_squares).parameters["ftol"].default
    assert isinstance(fitting.CERTIFY_MAX_RESTARTS, int) and fitting.CERTIFY_MAX_RESTARTS >= 1
    assert set(fitting._CERTIFIED_METHODS) == {"leastsq", "least_squares", "nelder"}


def test_a_fit_flagged_successful_short_of_its_minimum_is_carried_to_it():
    """The scope finding: Levenberg-Marquardt reports success where a descent
    still lowers chi2 (a loose tolerance makes it certain here). The returned
    fit is the certified minimum — the same chi2 as a tight fit — and the
    response says the certificate moved it."""
    x, y, specs = _problem()
    tight = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **KW)
    loose_kws = {"method": "leastsq", "fit_kws": {"ftol": 0.1, "xtol": 0.1}}
    raw = fitting.run_fit.__wrapped__
    import unittest.mock as mock
    with mock.patch.object(fitting, "_CERTIFIED_METHODS", ()):
        flagged = raw(x, y, _far(specs), fit_kws=loose_kws, **KW)
    assert flagged["success"] is True                                    # the flag says converged ...
    assert flagged["statistics"]["chi_square"] > tight["statistics"]["chi_square"] * 1.01   # ... short of the minimum
    res = fitting.run_fit(x, y, _far(specs), fit_kws=loose_kws, **KW)
    assert res["success"] is True
    assert res["certificate"]["certified"] is True and res["certificate"]["moved"] is True
    assert res["certificate"]["optimiser_flag"] is True and res["certificate"]["restarts"] >= 2
    assert res["statistics"]["chi_square"] == pytest.approx(tight["statistics"]["chi_square"], rel=1e-6)
    assert "checked by restarting" in res["message"]


def test_a_fit_at_its_minimum_is_returned_exactly_as_its_method_returned_it():
    """A Levenberg-Marquardt fit that reached its minimum is certified by one
    restart and returned byte-identical — values, sigma, statistics, message."""
    x, y, specs = _problem()
    import unittest.mock as mock
    with mock.patch.object(fitting, "_CERTIFIED_METHODS", ()):
        plain = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **KW)
    res = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **KW)
    cert = res["certificate"]
    assert {k: cert[k] for k in ("certified", "restarts", "moved", "optimiser_flag")} == \
        {"certified": True, "restarts": 1, "moved": False, "optimiser_flag": True}
    assert all(m["ev"] == 0.0 for m in cert["centre_moves"])
    strip = lambda r: {k: v for k, v in r.items() if k != "certificate"}
    assert strip(res) == strip(plain)


def test_a_fit_capped_at_its_minimum_is_certified_not_failed():
    """The other way the flag is wrong: out of evaluations AT the minimum."""
    x, y, specs = _problem()
    tight = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **KW)
    at_min = [{**s, "center": p["params"]["center"]["value"], "amplitude": p["params"]["amplitude"]["value"],
               "fwhm": p["params"]["fwhm"]["value"], "gl_ratio": p["params"]["gl_ratio"]["value"]}
              for s, p in zip(specs, tight["individual_peaks"])]
    import unittest.mock as mock
    with mock.patch.object(fitting, "_CERTIFIED_METHODS", ()):
        capped = fitting.run_fit.__wrapped__(x, y, at_min, fit_kws={"method": "leastsq", "max_nfev": 2}, **KW)
    assert capped["success"] is False
    # the caller's max_nfev also limits each restart; one restart AT the minimum finishes inside it
    res = fitting.run_fit(x, y, at_min, fit_kws={"method": "leastsq", "max_nfev": 200}, **KW)
    assert res["success"] is True and res["certificate"]["certified"] is True


def test_out_of_restarts_is_not_converged(monkeypatch):
    x, y, specs = _problem()
    monkeypatch.setattr(fitting, "CERTIFY_MAX_RESTARTS", 1)
    res = fitting.run_fit(x, y, _far(specs), fit_kws={"method": "leastsq", "fit_kws": {"ftol": 0.1, "xtol": 0.1}}, **KW)
    assert res["success"] is False
    cert = res["certificate"]
    assert {k: cert[k] for k in ("certified", "restarts", "moved", "optimiser_flag")} == \
        {"certified": False, "restarts": 1, "moved": True, "optimiser_flag": True}
    assert res["message"].startswith("The fit did not reach a minimum: restarting from where it stopped still lowered")


def test_a_restart_cut_off_by_the_callers_evaluation_limit_never_certifies():
    x, y, specs = _problem()
    res = fitting.run_fit(x, y, _far(specs), fit_kws={"method": "leastsq", "max_nfev": 3}, **KW)
    assert res["success"] is False
    assert res["certificate"]["certified"] is False
    assert "evaluation limit" in res["message"] or "still lowered" in res["message"]


def test_a_restart_that_raises_is_not_converged(monkeypatch):
    x, y, specs = _problem()
    real = fitting.Model.fit

    def fit(self, *a, **k):
        if k.get("method") == "least_squares":
            raise RuntimeError("boom")
        return real(self, *a, **k)
    monkeypatch.setattr(fitting.Model, "fit", fit)
    res = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **KW)
    assert res["success"] is False and "a restart from the end point failed (RuntimeError)" in res["message"]


def test_the_returned_fit_and_every_scattered_start_are_certified(monkeypatch):
    """V3: the certificate runs on the winner of the search and on each
    scattered start — with the page's request (n_perturb 3, n_starts 3), 1 + 3."""
    x, y, specs = _problem()
    seen = []
    real = fitting._certified

    def spy(*a, **k):
        out = real(*a, **k); seen.append(out.certificate["certified"]); return out
    monkeypatch.setattr(fitting, "_certified", spy)
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=3, n_starts=3,
                          fit_kws={"method": "least_squares"})
    assert len(seen) == 1 + 3 and all(seen)
    assert res["starts"]["n_converged"] == 3


def test_the_search_before_the_certificate_is_unchanged(monkeypatch):
    """The fit and its perturbed restarts are made exactly as before the
    certificate: same starts, same results, in the same order (certifying them
    first changed the basins the restarts reached — A2 measurement, V1/V2)."""
    import test_fit_reproducibility as R
    x, y, specs = R._crowded_c1s()
    runs = []
    for methods in (fitting._CERTIFIED_METHODS, ()):
        monkeypatch.setattr(fitting, "_CERTIFIED_METHODS", methods)
        records = R._spy_on_fits(monkeypatch); records.append([])
        fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq"})
        runs.append([(sorted(r["start"].items()), sorted(r["end"].items())) for r in records[0] if r["method"] == "leastsq"])
        monkeypatch.undo()
    assert len(runs[0]) == 4 and runs[0] == runs[1]


def test_a_scattered_start_that_does_not_certify_is_not_counted_as_converged(monkeypatch):
    x, y, specs = _problem()
    real = fitting._certify_fit
    calls = {"n": 0}

    def fail_after_the_fit(*a, **k):
        calls["n"] += 1
        point, ok, n, why = real(*a, **k)
        return (point, ok, n, why) if calls["n"] == 1 else (point, False, n, "forced")
    monkeypatch.setattr(fitting, "_certify_fit", fail_after_the_fit)
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, n_starts=3,
                          fit_kws={"method": "leastsq"})
    assert res["success"] is True
    assert res["starts"]["ran"] is True and res["starts"]["n_converged"] == 0


@pytest.mark.parametrize("method", ["differential_evolution", "basinhopping"])
def test_the_global_methods_keep_their_own_verdict(method):
    x, y, specs = _problem()
    res = fitting.run_fit(x, y, specs, fit_kws={"method": method}, **KW)
    assert res["certificate"] is None


def test_the_response_reports_how_far_the_continued_fit_moved_each_centre():
    x, y, specs = _problem()
    import unittest.mock as mock
    loose = {"method": "leastsq", "fit_kws": {"ftol": 0.1, "xtol": 0.1}}
    with mock.patch.object(fitting, "_CERTIFIED_METHODS", ()):
        stopped = fitting.run_fit.__wrapped__(x, y, _far(specs), fit_kws=loose, **KW)
    res = fitting.run_fit(x, y, _far(specs), fit_kws=loose, **KW)
    moves = res["certificate"]["centre_moves"]
    assert [m["id"] for m in moves] == [s["id"] for s in specs]
    for m, before, after in zip(moves, stopped["individual_peaks"], res["individual_peaks"]):
        assert m["ev"] == pytest.approx(after["params"]["center"]["value"] - before["params"]["center"]["value"], abs=1e-9)
    big = res["certificate"]["largest_centre_move"]
    assert abs(big["ev"]) == max(abs(m["ev"]) for m in moves)


def test_a_continuation_that_relocates_a_component_by_more_than_1_ev_is_reported():
    """The scattered-starts two-basin model without perturbed restarts:
    Levenberg-Marquardt reports success at chi2r ~286, which is not a minimum;
    the certificate carries the fit to the real decomposition and moves a
    component by more than the red-band distance — the page shows that
    (_certificateMoveFrom), as a notice."""
    import test_scattered_starts as SS
    x, y, specs = SS._two_basin_problem()
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    cert = res["certificate"]
    assert cert["certified"] and cert["moved"] and cert["optimiser_flag"]
    assert abs(cert["largest_centre_move"]["ev"]) > 1.0
