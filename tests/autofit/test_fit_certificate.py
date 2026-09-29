"""Unit A1 (2026-09-29): Find Peaks judges convergence by a CERTIFICATE, not the
optimiser's flag. A fit has reached a minimum when a fresh Trust-Region descent
from its end point improves chi2 by less than that descent's own stopping
tolerance (scipy least_squares' ftol); restarts repeat from each improved point
up to CERTIFY_MAX_RESTARTS; out of restarts = not converged. The flag was wrong
both ways: a warm restart from a stall "succeeded" in ~30 evaluations at
chi2r 37.6 where the minimum is 5.21 (8-JT C1s Scan_7), and a refit capped at
18 000 evaluations AT the minimum counted as failed (1-GTA C1s Scan_6)."""
import inspect
import os

import numpy as np
import pytest
import scipy.optimize

import autofit.engine as eng
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods.base import poisson_like_weights
from autofit.reference import load_reference_fits

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "docs", "autofit", "test_data")
G = resolve([Phase(id="graphite", material_class=MaterialClass.CONDUCTOR, regions=("C 1s",), material="graphite")], "C 1s")


def _scan(project, name):
    rf = next(r for r in load_reference_fits(os.path.join(DATA, project)) if r.name == name)
    x, y = np.asarray(rf.roi_be, float), np.asarray(rf.roi_intensity, float)
    return x, y, poisson_like_weights(y)


def _mg2():
    return next(c for c in G.candidates if c.name == "MG2_graphAsymGL_aliph_sat_CO_C=O")


def test_the_tolerance_is_the_optimisers_own():
    assert eng.CERTIFY_FTOL == inspect.signature(scipy.optimize.least_squares).parameters["ftol"].default
    assert isinstance(eng.CERTIFY_MAX_RESTARTS, int) and eng.CERTIFY_MAX_RESTARTS >= 1


def _kkt_violations(comp, params, x, y_net, w):
    """Parameters along which chi2 still descends: a free parameter with a
    non-negligible gradient, or one on a bound whose gradient points INTO the
    box. Empty = a (constrained) local minimum."""
    chi = lambda pp: float(np.sum(((y_net - comp.eval(pp, x=x)) * w) ** 2))
    c0, bad = chi(params), []
    for n, p in params.items():
        if not p.vary or p.expr is not None:
            continue
        span = (p.max - p.min) if np.isfinite(p.max) and np.isfinite(p.min) else (abs(p.value) or 1.0)
        h = 1e-6 * span
        q = params.copy()
        if p.value - p.min < 1e-9 * span:
            q[n].set(value=p.value + h)
            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
        elif p.max - p.value < 1e-9 * span:
            q[n].set(value=p.value - h)
            if chi(q) < c0 - 1e-9 * c0: bad.append(n)
        else:
            q[n].set(value=p.value + h); cp = chi(q); q[n].set(value=p.value - h); cm = chi(q)
            if abs(cp - cm) / (2 * h) * span > 1e-3 * c0: bad.append(n)
    return bad


def test_a_stall_now_ends_at_a_constrained_local_minimum():
    """Scan_7 MG2, stability refit 0's start. The removed warm restart
    reported success at the leastsq stall point (chi2 5220), which is NOT a
    minimum: a descent still lowers chi2. The certified point satisfies the
    KKT conditions (free gradients ~0, every parameter on a bound pushing out):
    a genuine local minimum, pinned on bounds (chi2r ~37 — a worse basin than
    the 5.21 least_squares finds from the same start by another path)."""
    x, y, w = _scan("8-JT Graphite.proj.zip", "C1s Scan_7")
    model = _mg2()
    primary = eng.fit_candidate(x, y, w, model)
    y_net = y - primary.background
    seed = int(np.random.default_rng(0).integers(0, 2**31 - 1))
    init = eng.perturb_initial_params(model, seed=seed, x=x, y_net=y_net)
    comp = eng._build_composite_model(model)
    stall = comp.fit(y_net, init.copy(), x=x, weights=w, method="leastsq", nan_policy="omit",
                     max_nfev=eng.FIT_CANDIDATE_MAX_NFEV)
    assert _kkt_violations(comp, stall.params, x, y_net, w), "the stall point is not a minimum"
    out = eng.fit_candidate(x, y, w, model, initial_params=init.copy())
    assert out.converged
    assert out.weighted_chi_sq < stall.chisqr
    assert _kkt_violations(comp, out.lmfit_result.params, x, y_net, w) == []


def _two_peak():
    x = np.arange(280.0, 292.0, 0.05)
    t = 500 + 8000 * np.exp(-4 * np.log(2) * ((x - 284.5) / 1.0) ** 2) + 1500 * np.exp(-4 * np.log(2) * ((x - 286.4) / 1.2) ** 2)
    y = t + np.sqrt(t) * np.random.default_rng(5).standard_normal(x.size)
    slot = lambda r, win: eng.ComponentSlot(role=r, region="C 1s", phase_id="p", be_window=win,
                                            line_shape=eng.LineShape.GAUSSIAN, fwhm_range=(0.5, 2.5))
    model = eng.CandidateModel(name="m", background=eng.BackgroundType.LINEAR,
                               slots=(slot("a", (284.0, 285.0)), slot("b", (286.0, 287.0))))
    return x, y, poisson_like_weights(y), model


def test_a_fit_capped_at_the_minimum_is_certified():
    """The Scan_6 case in general form: an optimiser that runs out of
    evaluations while sitting at the minimum reports failure; the certificate
    finds no descent and certifies it."""
    x, y, w, model = _two_peak()
    good = eng.fit_candidate(x, y, w, model)
    assert good.converged
    comp = eng._build_composite_model(model)
    y_sub = y - good.background
    capped = comp.fit(y_sub, good.lmfit_result.params.copy(), x=x, weights=w, method="leastsq",
                      nan_policy="omit", max_nfev=3)          # starts AT the minimum, capped at once
    assert not capped.success
    point, certified = eng._certify_minimum(comp, y_sub, capped, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert certified
    assert point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)


def test_out_of_restarts_is_not_converged(monkeypatch):
    """A start far from the minimum needs more than one restart to certify
    (the first descends a long way); with a single restart allowed it is
    'not converged' — whatever the optimiser says."""
    x, y, w, model = _two_peak()
    comp = eng._build_composite_model(model)
    good = eng.fit_candidate(x, y, w, model)
    y_sub = y - good.background
    far = good.lmfit_result.params.copy()
    far["s_a_center"].set(value=284.05); far["s_b_amplitude"].set(value=50.0); far["s_a_fwhm"].set(value=2.3)
    short = comp.fit(y_sub, far, x=x, weights=w, method="leastsq", nan_policy="omit", max_nfev=2)
    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 1)
    _, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert not certified
    monkeypatch.setattr(eng, "CERTIFY_MAX_RESTARTS", 5)
    point, certified = eng._certify_minimum(comp, y_sub, short, x, w, eng.FIT_CANDIDATE_MAX_NFEV)
    assert certified and point.chisqr == pytest.approx(good.weighted_chi_sq, rel=1e-6)


def test_the_warm_restart_is_gone():
    src = inspect.getsource(eng.fit_candidate)
    assert "retry" not in src and "WARM_RESTART" not in src
    assert "converged=bool(certified)" in src
