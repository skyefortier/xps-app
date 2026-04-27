import numpy as np
from lmfit import Model
from fitting import _la_casaxps_true


def test_la_covariance_with_free_m():
    # The bug: integer-rounding of m made the Jacobian column for
    # m identically zero, breaking covariance estimation.
    # This test ensures m can be free without poisoning covar.
    x = np.linspace(370, 405, 349)
    true = dict(amplitude=10000, center=380.4, fwhm=1.5,
                alpha=1.0, beta=1.0, m=50.0)
    y_true = _la_casaxps_true(x, **true)
    rng = np.random.default_rng(42)
    y = y_true + rng.normal(0, np.sqrt(np.maximum(y_true, 1.0)))

    model = Model(_la_casaxps_true)
    params = model.make_params(amplitude=8000, center=380.5,
                                fwhm=1.8, alpha=1.2, beta=0.8,
                                m=50.0)
    params['amplitude'].set(min=0)
    params['fwhm'].set(min=0.1, max=10)
    params['alpha'].set(min=0.1, max=5)
    params['beta'].set(min=0.1, max=5)
    params['m'].set(min=0, max=499, vary=True)
    result = model.fit(y, params, x=x,
                       weights=1/np.sqrt(np.maximum(y, 1)))
    assert result.success
    assert result.errorbars, (
        "covariance must be estimable with free m; was the "
        "integer-rounding regression reintroduced?"
    )
    assert result.covar is not None
    assert result.covar.shape == (6, 6)
    for name in ('amplitude', 'center', 'fwhm', 'alpha', 'beta', 'm'):
        assert result.params[name].stderr is not None, \
            f"{name} stderr must not be None"


def test_la_continuous_m_matches_integer_at_integers():
    # At integer m values, behavior should be near-identical to
    # the previous integer-rounded implementation, so existing
    # saved fits don't shift meaningfully.
    x = np.linspace(370, 405, 349)
    y_int = _la_casaxps_true(x, 1000, 380, 1.5, 1.0, 1.0, m=50.0)
    y_near = _la_casaxps_true(x, 1000, 380, 1.5, 1.0, 1.0, m=50.0001)
    # Should be effectively identical
    assert np.allclose(y_int, y_near, rtol=1e-4)
