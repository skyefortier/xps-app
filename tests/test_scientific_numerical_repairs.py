"""Independent oracles for the September scientific-audit repairs."""
import numpy as np
import pytest
from scipy.integrate import quad, trapezoid
from scipy.special import voigt_profile
from lmfit import Model, Parameters

from fitting import (
    _SHAPE_FUNCS, _ds_g_dscore_gauss, _la_casaxps_true,
    _make_peak_params, ds_g_fwhm, run_fit,
)


@pytest.mark.parametrize("n", [200, 201])
@pytest.mark.parametrize("beta,m", [(.3, .4), (.05, 2.), (1., .01), (.3, 0.)])
def test_dsg_matches_independent_voigt(n, beta, m):
    x = np.linspace(-5, 5, n)
    sigma = m / np.sqrt(8 * np.log(2))
    expected = voigt_profile(x - .023, sigma, beta) / voigt_profile(0, sigma, beta)
    actual = _ds_g_dscore_gauss(x, 1, .023, 0, beta, m)
    assert np.max(np.abs(actual - expected)) < 1e-7
    assert np.allclose(actual, _ds_g_dscore_gauss(x[::-1], 1, .023, 0, beta, m)[::-1])


def test_la_continuous_center_and_crop_independence():
    x = np.arange(-10, 10.01, .1)
    y = _la_casaxps_true(x, 1, .05 - 1e-8, 1, .5, 2, 30)
    other = _la_casaxps_true(x, 1, .05 + 1e-8, 1, .5, 2, 30)
    assert np.max(np.abs(y - other)) < 1e-6
    crop = (x > -2) & (x < 2)
    assert np.allclose(y[crop], _la_casaxps_true(x[crop], 1, .05 - 1e-8, 1, .5, 2, 30), atol=1e-12)


def test_asymmetric_dsg_matches_adaptive_integral():
    alpha, beta, width = .49, .05, 2.
    sigma = width / np.sqrt(8*np.log(2))
    def integral(energy):
        def integrand(z):
            u = energy - sigma*z
            return (np.cos(np.pi*alpha/2-(1-alpha)*np.arctan2(u,beta))
                    / (u*u+beta*beta)**((1-alpha)/2) * np.exp(-z*z/2))
        return quad(integrand, -8, 8, epsabs=1e-10, epsrel=1e-10, limit=200)[0]
    x = np.array([-2., -.13, .22, 3.])
    expected = np.array([integral(t)/integral(0) for t in x])
    assert np.allclose(_ds_g_dscore_gauss(x, 1, 0, alpha, beta, width), expected,
                       rtol=1e-8, atol=1e-9)


@pytest.mark.parametrize("shape", ["gaussian", "lorentzian", "pseudo_voigt_gl", "asymmetric_gl"])
def test_independent_width_links_enforce_full_component_area(shape):
    specs = [dict(id=1, shape=shape, amplitude=100, center=0, fwhm=1,
                  gl_ratio=.2, asymmetry=.1),
             dict(id=2, shape=shape, amplitude=50, center=5, fwhm=2,
                  gl_ratio=.8, asymmetry=.7, constrain_to=1, splitting=5,
                  area_ratio=.5, fix_fwhm=False)]
    params = Parameters()
    for spec in specs:
        prefix = f"p{spec['id']}_"
        params.update(_make_peak_params(Model(_SHAPE_FUNCS[shape], prefix=prefix), spec, prefix, specs))
    params.update_constraints()
    def analytic_area(pid):
        get = lambda key: params[f"p{pid}_{key}"].value
        eta = get("gl_ratio") if "gl" in shape else (1. if shape == "lorentzian" else 0.)
        value = get("amplitude") * get("fwhm") * ((1-eta)*np.sqrt(np.pi/(4*np.log(2))) + eta*np.pi/2)
        return value * (1 + get("asymmetry")/2) if shape == "asymmetric_gl" else value
    assert analytic_area(2) / analytic_area(1) == pytest.approx(.5)
    params["p2_fwhm"].value = 3.5
    params.update_constraints()
    assert analytic_area(2) / analytic_area(1) == pytest.approx(.5)


def test_unsupported_independent_asymmetric_link_refused():
    specs = [dict(id=1, shape="ds_g", center=0),
             dict(id=2, shape="ds_g", constrain_to=1, fix_fwhm=False)]
    with pytest.raises(ValueError, match="Independent-width"):
        _make_peak_params(Model(_SHAPE_FUNCS["ds_g"], prefix="p2_"), specs[1], "p2_", specs)


def test_fixed_width_area_and_linked_covariance():
    x = np.linspace(-5, 8, 401)
    g = lambda center: np.exp(-4*np.log(2)*(x-center)**2)
    y = np.random.default_rng(50).poisson(20+1000*g(0)+500*g(3)).astype(float)
    specs = [dict(id=1, shape="gaussian", amplitude=1000, center=0, fwhm=1,
                  fix_center=True, fix_fwhm=True),
             dict(id=2, shape="gaussian", constrain_to=1, splitting=3,
                  area_ratio=.5, fix_fwhm=True)]
    result = run_fit(x, y, specs, background_method="manual", manual_bg=[[-5,20],[8,20]])
    master, child = [peak["params"] for peak in result["individual_peaks"]]
    expected = master["amplitude"]["stderr"] * trapezoid(g(0), x)
    assert master["area"]["stderr"] == pytest.approx(expected, rel=1e-5)
    assert child["area"]["stderr"] == pytest.approx(.5*expected, rel=1e-5)


@pytest.mark.parametrize("weights", [[1], [1,np.nan,1], [1,0,1], [1,-1,1], [[1,1,1]]])
def test_invalid_supplied_weights_refused(weights):
    spec = dict(id=1, shape="gaussian", center=0, amplitude=10, fwhm=1)
    with pytest.raises(ValueError, match="weights"):
        run_fit(np.array([-1.,0.,1.]), np.array([2.,10.,2.]), [spec],
                background_method="none", weights=weights)


def test_dsg_width_is_measured_at_actual_asymmetric_half_maximum():
    width = ds_g_fwhm(.49, .3, .8)
    x = np.linspace(-10, 10, 10001)
    y = _ds_g_dscore_gauss(x, 1, 0, .49, .3, .8)
    i = np.argmax(y)
    observed = np.interp(y[i]/2, y[i:][::-1], x[i:][::-1]) - np.interp(y[i]/2, y[:i+1], x[:i+1])
    assert width == pytest.approx(observed, rel=1e-4)
    assert width > 2.9


@pytest.mark.parametrize("alpha,beta,width", [(0.,.05,4.),(.49,.05,2.),(.3,.1,1.2)])
def test_dsg_fft_fast_path_matches_independent_adaptive_integral(alpha,beta,width):
    from scipy.integrate import quad
    sigma = width / np.sqrt(8*np.log(2))
    def integral(t):
        def integrand(z):
            u = t - sigma*z
            return (np.cos(np.pi*alpha/2-(1-alpha)*np.arctan2(u,beta))
                    / (u*u+beta*beta)**((1-alpha)/2) * np.exp(-z*z/2))
        return quad(integrand,-8,8,epsabs=1e-10,epsrel=1e-10,limit=200)[0]
    probe = np.array([-2.,-.13,.22,3.])
    x = np.r_[probe,np.linspace(-5,5,30)]  # triggers padded FFT path
    curve = _ds_g_dscore_gauss(x,1,0,alpha,beta,width)
    expected = np.array([integral(t)/integral(0) for t in probe])
    np.testing.assert_allclose(curve[:4],expected,rtol=1e-8,atol=1e-9)
    np.testing.assert_allclose(curve[:4],_ds_g_dscore_gauss(probe,1,0,alpha,beta,width),
                               rtol=1e-8,atol=1e-9)
