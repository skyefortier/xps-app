"""The server's envelope is its background plus the sum of its components, to rounding:
fitted_y = background_y + Σ individual_peaks[].y — free and locked, every lineshape.
The bound and why: tests/envelope_identity.py. Owner 2026-10-10."""
import copy

import lmfit
import numpy as np
import pytest

import fitting
from envelope_identity import U, assert_response_identity, envelope_gap


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


X = np.arange(370.0, 400.0, 0.1)
Y = np.random.default_rng(17).poisson(
    500 + _g(X, 380.9, 9000, 1.6) + _g(X, 391.8, 6800, 1.6) + _g(X, 384.5, 900, 2.5) + _g(X, 396.0, 700, 2.0)).astype(float)

# one component of every lineshape the server registers, each with its shape parameters
SHAPES = {
    "gaussian":        {},
    "lorentzian":      {},
    "pseudo_voigt_gl": {"gl_ratio": 0.3},
    "asymmetric_gl":   {"gl_ratio": 0.3, "asymmetry": 0.35},
    "doniach_sunjic":  {"alpha": 0.15, "gamma_asym": 0.2},
    "ds_g":            {"alpha": 0.12, "beta": 0.4, "m_gauss": 0.8},
    "la_casaxps":      {"alpha": 1.4, "beta": 0.8, "m": 20.0},
}


def _model(shape, extra=None, locks=None):
    """A U 4f-like model: the shape under test on both main lines, a GL satellite and a
    Gaussian, so every response has four components to sum."""
    sp = {**SHAPES[shape], **(extra or {})}
    specs = [{"id": 1, "shape": shape, "center": 381.0, "amplitude": 8000.0, "fwhm": 1.5, "amplitude_min": 0, **sp},
             {"id": 2, "shape": shape, "center": 391.7, "amplitude": 6000.0, "fwhm": 1.5, "amplitude_min": 0, **sp},
             {"id": 3, "shape": "pseudo_voigt_gl", "center": 384.4, "amplitude": 800.0, "fwhm": 2.5, "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": 4, "shape": "gaussian", "center": 396.1, "amplitude": 600.0, "fwhm": 2.0, "amplitude_min": 0}]
    for s in specs[:2]:
        s.update(locks or {})
    return specs


def _fit(specs, **kw):
    return fitting.run_fit(X, Y, specs, background_method=kw.pop("background_method", "shirley"),
                           n_perturb=kw.pop("n_perturb", 0), fit_kws={"method": kw.pop("method", "leastsq")}, **kw)


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_every_lineshape_free(shape):
    assert_response_identity(_fit(_model(shape)), shape)


# shape parameters locked at bounds (the cases below — not every bound of every parameter:
# fitting._make_peak_params), and amplitudes, centres and widths locked
LOCKS = [
    ("pseudo_voigt_gl", {"gl_ratio": 0.0, "fix_gl_ratio": True}),
    ("pseudo_voigt_gl", {"gl_ratio": 1.0, "fix_gl_ratio": True}),
    ("asymmetric_gl", {"asymmetry": 0.0, "fix_asymmetry": True}),
    ("asymmetric_gl", {"asymmetry": 1.0, "fix_asymmetry": True}),
    ("asymmetric_gl", {"gl_ratio": 0.0, "fix_gl_ratio": True, "asymmetry": 1.0, "fix_asymmetry": True}),
    ("doniach_sunjic", {"alpha": 0.0, "fix_alpha": True}),
    ("doniach_sunjic", {"alpha": 0.5, "fix_alpha": True, "gamma_asym": 5.0, "fix_gamma_asym": True}),
    ("doniach_sunjic", {"gamma_asym": 0.0, "fix_gamma_asym": True}),
    ("ds_g", {"m_gauss": 4.0, "fix_m_gauss": True}),
    ("ds_g", {"alpha": 0.0, "fix_alpha": True, "m_gauss": 0.05, "fix_m_gauss": True}),
    ("ds_g", {"alpha": 0.49, "fix_alpha": True, "beta": 0.05, "fix_beta": True}),   # (β at 2.0 took > 6 min to certify)
    ("la_casaxps", {"m": 0.0}),                                  # m is held by default
    ("la_casaxps", {"alpha": 0.1, "fix_alpha": True, "beta": 5.0, "fix_beta": True, "m": 499.0}),
    ("asymmetric_gl", {"fix_amplitude": True}),
    ("gaussian", {"fix_amplitude": True, "fix_center": True, "fix_fwhm": True}),
]


@pytest.mark.parametrize("shape,locks", LOCKS, ids=[f"{s}-{'-'.join(sorted(k for k in l if k.startswith('fix_')) or ['m'])}-{i}" for i, (s, l) in enumerate(LOCKS)])
def test_components_locked_at_bounds(shape, locks):
    specs = _model(shape, locks=locks)
    res = _fit(specs)
    # every lock was HELD by the server, on both locked components: not varied, at the requested
    # value (a flag the server ignored would otherwise pass — Codex round 1)
    held = [k[len("fix_"):] for k, v in locks.items() if k.startswith("fix_") and v]
    if shape == "la_casaxps" and "fix_m" not in locks:
        held.append("m")                                          # m is held by default
    held = ["gl_ratio" if h == "gl_ratio" else h for h in held]
    assert held, "the case locks something"
    for spec, ip in zip(specs[:2], res["individual_peaks"][:2]):
        for name in held:
            par = ip["params"][name]
            assert par["vary"] is False and par["expr"] is None, f"{shape}: {name} varied"
            assert par["value"] == spec[name], f"{shape}: {name} {par['value']} != requested {spec[name]}"
    assert_response_identity(res, f"{shape} {locks}")


@pytest.mark.parametrize("method", ["leastsq", "least_squares", "nelder"])
def test_every_local_method_with_perturbed_restarts_and_scattered_starts(method):
    res = _fit(_model("asymmetric_gl"), method=method, n_perturb=3, n_starts=3)
    assert_response_identity(res, method)


@pytest.mark.parametrize("bg", ["shirley", "smart", "linear", "tougaard", "none"])
def test_every_background(bg):
    assert_response_identity(_fit(_model("asymmetric_gl"), background_method=bg), bg)


def _capped_moving_fit(monkeypatch):
    """The certificate MOVES this fit (Levenberg-Marquardt cut off after 6 evaluations, 2 eV
    from its line; tests/test_runfit_certificate.py): the returned point is not the optimiser's."""
    x = np.arange(280.0, 292.0, 0.05)
    y = np.random.default_rng(11).poisson(300 + _g(x, 284.5, 6000, 1.0)).astype(float)
    specs = [{"id": 1, "shape": "gaussian", "center": 286.5, "amplitude": 6000.0, "amplitude_min": 0, "fwhm": 2.0},
             {"id": 2, "shape": "gaussian", "center": 289.0, "amplitude": 50.0, "amplitude_min": 0, "fwhm": 1.0}]
    real_fit = lmfit.Model.fit

    def cut_off(self, *args, **kw):
        if kw.get("method", "leastsq") == "leastsq":
            kw = {**kw, "max_nfev": 6}
        return real_fit(self, *args, **kw)
    monkeypatch.setattr(lmfit.Model, "fit", cut_off)
    return x, y, specs


def test_a_fit_the_certificate_moved(monkeypatch):
    x, y, specs = _capped_moving_fit(monkeypatch)
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    assert res["certificate"]["moved"]
    assert_response_identity(res, "certificate-moved")


# ── the checks FAIL when the identity is broken ──────────────────────────────

def test_the_check_rejects_a_component_off_by_more_than_rounding():
    res = _fit(_model("asymmetric_gl"))
    ratio, _ = envelope_gap(res["fitted_y"], res["background_y"], [p["y"] for p in res["individual_peaks"]])
    assert ratio <= 1.0
    bad = copy.deepcopy(res)
    i = int(np.argmax(bad["individual_peaks"][0]["y"]))
    bad["individual_peaks"][0]["y"][i] *= 1 + 1e-12            # far below anything visible, above rounding
    with pytest.raises(AssertionError, match="not the background plus its components"):
        assert_response_identity(bad)
    bad = copy.deepcopy(res)
    bad["background_y"][i] += 1e-9 * abs(bad["fitted_y"][i])
    with pytest.raises(AssertionError, match="not the background plus its components"):
        assert_response_identity(bad)
    bad = copy.deepcopy(res)
    bad["individual_peaks"] = bad["individual_peaks"][:-1]        # a component left out of the sum
    with pytest.raises(AssertionError):
        assert_response_identity(bad)


def test_the_check_rejects_an_envelope_from_another_point_than_its_components(monkeypatch):
    # a plausible defect: the certificate moves the parameters but the envelope keeps the
    # optimiser's curve (best_fit of the point it stopped at)
    x, y, specs = _capped_moving_fit(monkeypatch)
    real = fitting._certified

    def stale_best_fit(model, result, *a, **k):
        before = np.array(result.best_fit, copy=True)
        point = real(model, result, *a, **k)
        point.best_fit = before
        return point
    monkeypatch.setattr(fitting, "_certified", stale_best_fit)
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "leastsq"})
    assert res["certificate"]["moved"]
    with pytest.raises(AssertionError, match="not the background plus its components"):
        assert_response_identity(res)


def test_the_bound_is_the_stated_one():
    # 4 (n + 2) u of |b| + Σ |c|, point by point (tests/envelope_identity.py): with b = 1 and one
    # zero component the bound is 12 u = 6 ulps of 1 exactly, so 5 ulps pass and 7 fail
    b, c = np.array([1.0]), [np.array([0.0])]
    ulp = np.spacing(1.0)
    assert 4 * 3 * U == 6 * ulp
    assert envelope_gap(b + 5 * ulp, b, c)[0] <= 1.0
    assert envelope_gap(b + 6 * ulp, b, c)[0] <= 1.0
    assert envelope_gap(b + 7 * ulp, b, c)[0] > 1.0
