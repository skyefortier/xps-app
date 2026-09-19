"""Differential Evolution must be runnable from the requests the page sends.

Confirmed bug (docs/findings/2026-09-fit-determinacy.md section 4, 2026-09-18):
the page sends ``amplitude_min: 0`` and never an ``amplitude_max``; a DS+G
peak's centre has no default bounds either. lmfit's ``differential_evolution``
refuses any varying parameter without finite bounds, so every ordinary fit
with that method returned HTTP 422 "Fit failed". ``run_fit`` now gives the
global search a finite box where the request left one open, and leaves every
other method's parameters exactly as they were.
"""

import io

import numpy as np
import pytest
from lmfit import Parameters

import fitting
from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _two_peak_spectrum(seed=3):
    rng = np.random.default_rng(seed)
    x = np.arange(280.0, 295.0, 0.1)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = rng.poisson(200.0 + g(284.8, 4000.0, 1.1) + g(288.6, 900.0, 1.4)).astype(float)
    return x, y


def _page_like_specs():
    # What peakToBackendSpec sends for two free GL peaks: a lower amplitude
    # bound of zero and NO upper bound.
    return [
        {"id": 1, "shape": "pseudo_voigt_gl", "center": 284.6, "amplitude": 3500.0,
         "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
        {"id": 2, "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0,
         "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
    ]


def test_api_fit_differential_evolution_runs_with_page_like_request(client):
    x, y = _two_peak_spectrum()
    csv = "\n".join(f"{a:.3f},{b:.1f}" for a, b in zip(x, y))
    up = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "c1s.csv")})
    assert up.status_code == 200, up.get_json()
    resp = client.post("/api/fit", json={
        "session_id": up.get_json()["session_id"],
        "background": {"method": "linear"},
        "peaks": _page_like_specs(),
        "fit_method": "differential_evolution",
        "n_perturb": 3,
    })
    assert resp.status_code == 200, resp.get_json()
    body = resp.get_json()
    assert body["success"] is True
    centres = sorted(p["params"]["center"]["value"] for p in body["individual_peaks"])
    assert centres[0] == pytest.approx(284.8, abs=0.05)
    assert centres[1] == pytest.approx(288.6, abs=0.1)


def test_differential_evolution_agrees_with_least_squares():
    x, y = _two_peak_spectrum()
    kw = dict(background_method="linear", n_perturb=0)
    de = fitting.run_fit(x, y, _page_like_specs(), fit_kws={"method": "differential_evolution"}, **kw)
    ls = fitting.run_fit(x, y, _page_like_specs(), fit_kws={"method": "least_squares"}, **kw)
    assert de["success"] and ls["success"]
    assert de["statistics"]["reduced_chi_square"] == pytest.approx(
        ls["statistics"]["reduced_chi_square"], rel=1e-3)


def test_differential_evolution_runs_with_unbounded_dsg_centre():
    # A free DS+G peak gets no default centre window, so its centre is
    # unbounded as well as its amplitude.
    x, y = _two_peak_spectrum()
    specs = [{"id": 1, "shape": "ds_g", "center": 284.7, "amplitude": 3500.0, "fwhm": 1.0,
              "alpha": 0.05, "beta": 0.3, "m_gauss": 0.8, "amplitude_min": 0},
             {"id": 2, "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0,
              "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert np.isfinite(res["statistics"]["reduced_chi_square"])
    centre = next(p for p in res["individual_peaks"] if p["id"] == 1)["params"]["center"]["value"]
    assert x.min() <= centre <= x.max()


def test_finite_search_box_only_touches_open_varying_bounds():
    p = Parameters()
    p.add("p1_amplitude", value=50.0, min=0.0)                     # open above
    p.add("p1_center", value=285.0)                                # open both sides
    p.add("p1_fwhm", value=1.0, min=0.1, max=15.0)                 # already boxed
    p.add("p2_amplitude", value=9.0e6, min=0.0, vary=False)        # fixed: untouched
    p.add("p3_amplitude", expr="p1_amplitude * 0.5")               # constrained: untouched
    x = np.linspace(280.0, 290.0, 101)
    y_sub = np.full_like(x, 100.0)
    fitting._finite_search_box(p, x, y_sub)
    assert p["p1_amplitude"].min == 0.0
    assert p["p1_amplitude"].max == pytest.approx(10 * 100.0)
    assert (p["p1_center"].min, p["p1_center"].max) == (280.0, 290.0)
    assert (p["p1_fwhm"].min, p["p1_fwhm"].max) == (0.1, 15.0)
    assert not np.isfinite(p["p2_amplitude"].max)
    assert not np.isfinite(p["p3_amplitude"].max)


def test_finite_search_box_keeps_a_start_above_the_data_inside_the_box():
    p = Parameters()
    p.add("p1_amplitude", value=5000.0, min=0.0)
    x = np.linspace(280.0, 290.0, 11)
    fitting._finite_search_box(p, x, np.full_like(x, 100.0))
    assert p["p1_amplitude"].max >= 2 * 5000.0
    assert p["p1_amplitude"].value == 5000.0


def test_other_methods_keep_an_open_amplitude_bound(monkeypatch):
    seen = {}
    real_fit = fitting.Model.fit

    def spy(self, data, params, **kw):
        seen["max"] = params["p1_amplitude"].max
        return real_fit(self, data, params, **kw)

    monkeypatch.setattr(fitting.Model, "fit", spy)
    x, y = _two_peak_spectrum()
    fitting.run_fit(x, y, _page_like_specs(), background_method="linear", n_perturb=0,
                    fit_kws={"method": "least_squares"})
    assert not np.isfinite(seen["max"])
