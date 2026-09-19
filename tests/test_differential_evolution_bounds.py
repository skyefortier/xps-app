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
    assert res["success"] is True
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
    generated = fitting._finite_search_box(p, x, y_sub)
    assert set(generated) == {"p1_amplitude", "p1_center"}
    assert set(generated["p1_amplitude"]) == {"max"} and set(generated["p1_center"]) == {"min", "max"}
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


# ── Codex round 1 (both runs NO-GO) ─────────────────────────────────────────

def test_generated_amplitude_limit_never_sets_the_answer():
    # A neighbouring peak's tail after narrowing the ROI: true height 10 000 at
    # 285 eV, ROI 286-290 eV where the data never exceed 625. The first search
    # box (10 x 625) would cap the amplitude at 6 250 and under-report the
    # area by 37 % while claiming success.
    x = np.linspace(286.0, 290.0, 81)
    y = 10000.0 * np.exp(-4 * np.log(2) * ((x - 285.0) / 1.0) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "amplitude": 1000.0, "fwhm": 1.0,
              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
    kw = dict(background_method="none", n_perturb=3)
    de = fitting.run_fit(x, y, specs, fit_kws={"method": "differential_evolution"}, **kw)
    ls = fitting.run_fit(x, y, specs, fit_kws={"method": "least_squares"}, **kw)
    assert de["success"] is True
    amp = de["individual_peaks"][0]["params"]["amplitude"]["value"]
    assert amp == pytest.approx(10000.0, rel=1e-3)
    assert de["individual_peaks"][0]["params"]["area"]["value"] == pytest.approx(
        ls["individual_peaks"][0]["params"]["area"]["value"], rel=1e-3)


def test_solution_still_on_the_search_limit_is_not_a_success(monkeypatch):
    monkeypatch.setattr(fitting, "_SEARCH_BOX_EXPANSIONS", 0)
    x = np.linspace(286.0, 290.0, 81)
    y = 10000.0 * np.exp(-4 * np.log(2) * ((x - 285.0) / 1.0) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "amplitude": 1000.0, "fwhm": 1.0,
              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="none", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is False
    assert "search box" in res["message"] and "p1_amplitude" in res["message"]


@pytest.mark.parametrize("bound", [{"center": 300.0, "center_min": 300.0},
                                   {"center": 270.0, "center_max": 270.0}])
def test_one_sided_centre_bound_outside_the_roi_keeps_a_real_interval(bound):
    p = Parameters()
    p.add("p1_center", value=bound["center"], min=bound.get("center_min", -np.inf),
          max=bound.get("center_max", np.inf))
    x = np.linspace(280.0, 290.0, 101)
    fitting._finite_search_box(p, x, np.full_like(x, 50.0))
    assert np.isfinite(p["p1_center"].min) and np.isfinite(p["p1_center"].max)
    assert p["p1_center"].max - p["p1_center"].min >= 10.0
    assert p["p1_center"].min <= bound["center"] <= p["p1_center"].max
    # and the request's own side is untouched
    if "center_min" in bound:
        assert p["p1_center"].min == 300.0
    else:
        assert p["p1_center"].max == 270.0


def test_one_sided_dsg_centre_bound_runs_end_to_end():
    x, y = _two_peak_spectrum()
    specs = [{"id": 1, "shape": "ds_g", "center": 284.7, "center_min": 284.7, "amplitude": 3500.0,
              "fwhm": 1.0, "alpha": 0.05, "beta": 0.3, "m_gauss": 0.8, "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert np.isfinite(res["statistics"]["reduced_chi_square"])


def test_generated_limits_are_not_reported_as_bounds():
    # The page stores returned bounds (_backendParams, saved with the fit) and
    # warns "at lower bound" within 1 % of [min, max]: a generated ceiling of
    # 10 x the main peak would flag every well-determined satellite below 10 %.
    x, y = _two_peak_spectrum()
    res = fitting.run_fit(x, y, _page_like_specs(), background_method="linear", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    for peak in res["individual_peaks"]:
        assert peak["params"]["amplitude"]["min"] == 0.0        # the request's own bound
        assert peak["params"]["amplitude"]["max"] is None       # ours is not echoed
        assert peak["params"]["center"]["min"] is not None      # the default +-2 eV window still is


def test_linked_doublet_runs_with_open_slave_bounds():
    rng = np.random.default_rng(5)
    x = np.arange(195.0, 206.0, 0.1)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = rng.poisson(150.0 + g(198.8, 3000.0, 1.2) + g(200.4, 1500.0, 1.2)).astype(float)
    specs = [{"id": 1, "shape": "pseudo_voigt_gl", "center": 198.6, "amplitude": 2500.0, "fwhm": 1.3,
              "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": 2, "shape": "pseudo_voigt_gl", "center": 200.2, "amplitude": 1250.0, "fwhm": 1.3,
              "gl_ratio": 0.3, "amplitude_min": 0, "constrain_to": 1, "splitting": 1.6, "area_ratio": 0.5}]
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True
    amps = {p["id"]: p["params"]["amplitude"]["value"] for p in res["individual_peaks"]}
    assert amps[2] == pytest.approx(0.5 * amps[1], rel=1e-6)


def test_nonfinite_data_is_a_validation_error_not_a_nan_bound():
    p = Parameters()
    p.add("p1_amplitude", value=10.0, min=0.0)
    x = np.linspace(280.0, 290.0, 11)
    with pytest.raises(ValueError, match="finite"):
        fitting._finite_search_box(p, x, np.full_like(x, np.nan))
    y = np.full_like(x, 100.0)
    y[3] = np.nan
    fitting._finite_search_box(p, x, y)
    assert p["p1_amplitude"].max == pytest.approx(1000.0)
