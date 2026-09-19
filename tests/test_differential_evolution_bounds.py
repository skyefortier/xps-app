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


def test_without_a_converged_refinement_the_boxed_answer_is_not_a_success(monkeypatch):
    # The ceiling (10 x 625) binds; if the refinement that would settle it
    # does not converge, the capped answer must not be reported as a fit.
    real_fit = fitting.Model.fit

    def failing_polish(self, data, params, **kw):
        res = real_fit(self, data, params, **kw)
        if kw.get("method") == "least_squares":
            res.success = False
        return res

    monkeypatch.setattr(fitting.Model, "fit", failing_polish)
    x = np.linspace(286.0, 290.0, 81)
    y = 10000.0 * np.exp(-4 * np.log(2) * ((x - 285.0) / 1.0) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "amplitude": 1000.0, "fwhm": 1.0,
              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="none", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is False
    assert "generated limits" in res["message"] and "p1_amplitude" in res["message"]
    assert res["individual_peaks"][0]["params"]["amplitude"]["max"] is None


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


# ── Codex round 2 (both runs NO-GO) ─────────────────────────────────────────

def test_open_amplitude_floor_searches_negative_heights():
    # amplitude_min: null leaves the floor open; a generated floor of zero
    # excluded the true -100 and still reported success.
    x = np.linspace(280.0, 290.0, 101)
    y = 1000.0 - 100.0 * np.exp(-4 * np.log(2) * (x - 285.0) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "amplitude": 10.0, "fwhm": 1.0,
              "fix_center": True, "fix_fwhm": True, "amplitude_min": None}]
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[280.0, 1000.0], [290.0, 1000.0]], n_perturb=3,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True
    assert res["individual_peaks"][0]["params"]["amplitude"]["value"] == pytest.approx(-100.0, rel=1e-3)


@pytest.mark.parametrize("bound", [{"center_min": 0.0}, {"center_max": 1000.0}])
def test_exact_fit_beside_a_broad_one_sided_centre_bound_is_accepted(bound):
    # "Resting on the limit" is judged on the generated side's own scale: one
    # percent of [0, 285.4] is 2.9 eV and called an exact fit limited.
    x = np.linspace(284.6, 285.0, 81) if "center_min" in bound else np.linspace(285.0, 285.4, 81)
    y = fitting._SHAPE_FUNCS["ds_g"](x, amplitude=1000.0, center=285.0,
                                     alpha=0.05, beta=0.3, m_gauss=0.2)
    spec = {"id": 1, "shape": "ds_g", "center": 285.0, "amplitude": 1000.0, "fwhm": 1.0,
            "alpha": 0.05, "beta": 0.3, "m_gauss": 0.2, "fix_amplitude": True, "fix_fwhm": True,
            "fix_alpha": True, "fix_beta": True, "fix_m_gauss": True, **bound}
    res = fitting.run_fit(x, y, [spec], background_method="none", n_perturb=3,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True, res["message"]
    assert res["individual_peaks"][0]["params"]["center"]["value"] == pytest.approx(285.0, abs=0.02)


# ── Codex round 3 (both runs NO-GO): the widening loop is gone. A solution near
#    a generated side is refined FROM that solution with the request's own
#    bounds; nearness alone never refuses, and no candidate is discarded. ─────

def _two_dsg_at_the_roi_edge():
    x = np.linspace(280.0, 290.0, 501)
    dsg = fitting._SHAPE_FUNCS["ds_g"]
    y = (1000.0 + dsg(x, amplitude=100.0, center=280.0, alpha=0.0, beta=0.05, m_gauss=0.05)
         + dsg(x, amplitude=75.0, center=285.0, alpha=0.0, beta=0.05, m_gauss=0.05))
    spec = {"id": 1, "shape": "ds_g", "center": 285.0, "amplitude": 100.0, "fwhm": 1.0,
            "alpha": 0.0, "beta": 0.05, "m_gauss": 0.05, "fix_amplitude": True,
            "fix_alpha": True, "fix_beta": True, "fix_m_gauss": True}
    return x, y, [spec]


@pytest.mark.parametrize("seed,n_perturb", [(36, 1), (36, 2), (2, 0)])
def test_the_returned_fit_is_never_worse_than_a_candidate_it_saw(monkeypatch, seed, n_perturb):
    # Seeds from the review: a perturbed refit found the component at the ROI
    # edge (chi2r 0.0506) and the widened refit replaced it with 0.0589, still
    # reporting success.
    seen = []
    real_fit = fitting.Model.fit

    def spy(self, data, params, **kw):
        res = real_fit(self, data, params, **kw)
        if res.success:
            seen.append(res.chisqr)
        return res

    monkeypatch.setattr(fitting.Model, "fit", spy)
    np.random.seed(seed)
    x, y, specs = _two_dsg_at_the_roi_edge()
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[280.0, 1000.0], [290.0, 1000.0]], n_perturb=n_perturb,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True
    assert res["statistics"]["chi_square"] <= min(seen) * (1 + 1e-9)


def test_exact_amplitude_just_under_a_generated_ceiling_is_accepted():
    # True height 995 000 seen only through its tail (max 100 in the ROI): the
    # ceiling is 1 000. Nearness to a ceiling is a reason to refine, not to refuse.
    x = np.linspace(286.8221197003983, 287.8221197003983, 81)
    y = 1000.0 + 995000.0 * np.exp(-4 * np.log(2) * (x - 285.0) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "amplitude": 1.0, "fwhm": 1.0,
              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
    np.random.seed(4)
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[286.0, 1000.0], [288.0, 1000.0]], n_perturb=3,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True, res["message"]
    assert res["individual_peaks"][0]["params"]["amplitude"]["value"] == pytest.approx(995000.0, rel=1e-4)


def test_refinement_runs_only_for_differential_evolution(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("the search box is for differential evolution only")

    monkeypatch.setattr(fitting, "_search_then_refine", boom)
    x, y = _two_peak_spectrum()
    for method in ("leastsq", "least_squares", "nelder"):
        res = fitting.run_fit(x, y, _page_like_specs(), background_method="linear", n_perturb=1,
                              fit_kws={"method": method})
        assert res["success"] is True


# ── Codex round 4 (both runs NO-GO): nearness was a heuristic. Every
#    differential-evolution candidate is refined under the request's own
#    bounds before it is compared or returned. ────────────────────────────────

def test_box_limited_fit_far_from_the_ceiling_is_refined():
    # Ceiling 2 000 for a true height of 1e6 seen through its tail: DE
    # compensated with centre and width (amplitude 1 969, centre 286.08,
    # width 0.69) and sat 31 away from the ceiling, outside any "near" band.
    np.random.seed(3)
    x = np.linspace(287.0, 288.0, 81)
    y = 1000.0 + 1e6 * np.exp(-4 * np.log(2) * (x - 285.0) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "amplitude": 1000.0, "fwhm": 1.0,
              "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[280.0, 1000.0], [290.0, 1000.0]], n_perturb=3,
                          fit_kws={"method": "differential_evolution"})
    ls = fitting.run_fit(x, y, specs, background_method="manual",
                         manual_bg=[[280.0, 1000.0], [290.0, 1000.0]], n_perturb=0,
                         fit_kws={"method": "least_squares"})
    assert res["success"] is True, res["message"]
    assert res["statistics"]["chi_square"] <= ls["statistics"]["chi_square"] * (1 + 1e-6) + 1e-12
    got = res["individual_peaks"][0]["params"]
    assert got["amplitude"]["value"] == pytest.approx(1e6, rel=1e-3)
    assert got["center"]["value"] == pytest.approx(285.0, abs=1e-3)


@pytest.mark.parametrize("n_perturb", [0, 1, 3])
def test_a_boundary_candidate_is_refined_before_it_can_lose_the_comparison(n_perturb):
    # First search lands on the ceiling (chi2 ~1270); a perturbed search finds
    # an interior solution (~1250) that used to win and suppress the
    # refinement that takes the first candidate to ~1158.
    np.random.seed(0)
    x = np.linspace(286.8, 290.8, 81)
    y = (1000.0 + 1e7 * np.exp(-4 * np.log(2) * (x - 285.0) ** 2)
         + 310.0 * np.exp(-4 * np.log(2) * (x - 289.0) ** 2))
    specs = [{"id": 1, "shape": "gaussian", "center": 287.0, "center_min": 284.0, "center_max": 291.0,
              "amplitude": 1000.0, "amplitude_min": 0, "fwhm": 1.0, "fix_fwhm": True}]
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[286.0, 1000.0], [291.0, 1000.0]], n_perturb=n_perturb,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True, res["message"]
    assert res["statistics"]["chi_square"] == pytest.approx(1157.545422, rel=1e-3)


def test_solver_options_for_differential_evolution_do_not_reach_the_refinement():
    x = np.linspace(286.0, 290.0, 81)
    y = 10000.0 * np.exp(-4 * np.log(2) * ((x - 285.0) / 1.0) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "amplitude": 1000.0, "fwhm": 1.0,
              "fix_center": True, "fix_fwhm": True, "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="none", n_perturb=0,
                          fit_kws={"method": "differential_evolution", "fit_kws": {"seed": 4}})
    assert res["success"] is True
    assert res["individual_peaks"][0]["params"]["amplitude"]["value"] == pytest.approx(10000.0, rel=1e-3)


def test_a_perturbed_search_starts_from_the_requests_bounds_not_the_last_box():
    # An unverified candidate carries generated sides; the next search must
    # not mistake them for bounds the request set (and so skip refinement).
    from lmfit import Model
    model = Model(fitting._SHAPE_FUNCS["gaussian"], prefix="p1_")
    x = np.linspace(286.0, 290.0, 81)
    y = 10000.0 * np.exp(-4 * np.log(2) * ((x - 285.0) / 1.0) ** 2)
    params = model.make_params()
    params["p1_amplitude"].set(value=1000.0, min=0.0, max=6250.0)          # as left by an earlier box
    params["p1_center"].set(value=285.0, vary=False)
    params["p1_fwhm"].set(value=1.0, vary=False)
    requested = {"p1_amplitude": (0.0, np.inf), "p1_center": (-np.inf, np.inf), "p1_fwhm": (-np.inf, np.inf)}
    res = fitting._search_then_refine(model, params, requested, y, x, np.ones_like(y), y,
                                      {"method": "differential_evolution", "nan_policy": "omit"})
    assert res.box_unverified is False
    assert res.params["p1_amplitude"].value == pytest.approx(10000.0, rel=1e-3)


# ── Codex round 5 (both runs NO-GO) ─────────────────────────────────────────

@pytest.mark.parametrize("n_perturb", [0, 3])
def test_numerically_exact_refinement_is_accepted(n_perturb):
    # Noise-free data: DE reaches chi2 ~4e-28 on the requested centre bound,
    # least_squares steps 3e-8 eV inside it (chi2 ~1e-11). A relative-only
    # comparison rejected that and blamed the generated amplitude limit.
    np.random.seed(4)
    x = np.linspace(280.0, 290.0, 101)
    y = 1000.0 + 1000.0 * np.exp(-4 * np.log(2) * (x - 285.0) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "center_min": 285.0,
              "amplitude": 1000.0, "amplitude_min": 0, "fwhm": 1.0, "fix_fwhm": True}]
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[280.0, 1000.0], [290.0, 1000.0]], n_perturb=n_perturb,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True, res["message"]
    assert res["individual_peaks"][0]["params"]["amplitude"]["value"] == pytest.approx(1000.0, rel=1e-6)


def test_exact_fit_on_a_requested_width_floor_is_accepted():
    np.random.seed(0)
    x = np.linspace(284.0, 286.0, 81)
    y = 1000.0 + 100.0 * np.exp(-4 * np.log(2) * ((x - 285.0) / 0.1) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "fix_center": True,
              "amplitude": 10.0, "amplitude_min": 0, "fwhm": 0.2}]
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[280.0, 1000.0], [290.0, 1000.0]], n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True, res["message"]


def test_an_unverified_perturbed_candidate_does_not_displace_a_verified_fit(monkeypatch):
    # First candidate verified; every later refinement is made to fail, so the
    # perturbed candidates stay unverified. They must not replace the fit.
    real = fitting._search_then_refine
    calls = {"n": 0}

    def later_candidates_unverified(model, params, requested, y_sub, x, weights, raw, kws):
        calls["n"] += 1
        res = real(model, params, requested, y_sub, x, weights, raw, kws)
        if calls["n"] > 1:
            res.box_unverified, res.search_box = True, {"p1_amplitude": {"max": 1.0}}
            res.chisqr, res.redchi = res.chisqr * 0.5, res.redchi * 0.5     # and "better"
        return res

    monkeypatch.setattr(fitting, "_search_then_refine", later_candidates_unverified)
    x, y = _two_peak_spectrum()
    res = fitting.run_fit(x, y, _page_like_specs(), background_method="linear", n_perturb=3,
                          fit_kws={"method": "differential_evolution"})
    assert calls["n"] == 4
    assert res["success"] is True, res["message"]


def test_a_verified_candidate_displaces_an_unverified_one_even_at_higher_chi_square(monkeypatch):
    real = fitting._search_then_refine
    calls = {"n": 0}

    def first_candidate_unverified(model, params, requested, y_sub, x, weights, raw, kws):
        calls["n"] += 1
        res = real(model, params, requested, y_sub, x, weights, raw, kws)
        if calls["n"] == 1:
            res.box_unverified, res.search_box = True, {"p1_amplitude": {"max": 1.0}}
            res.chisqr, res.redchi = res.chisqr * 0.5, res.redchi * 0.5
        return res

    monkeypatch.setattr(fitting, "_search_then_refine", first_candidate_unverified)
    x, y = _two_peak_spectrum()
    res = fitting.run_fit(x, y, _page_like_specs(), background_method="linear", n_perturb=2,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True, res["message"]


# ── Codex round 6 (run A GO, run B NO-GO) ───────────────────────────────────

@pytest.mark.parametrize("scale", [1e-3, 1.0, 1e3, 1e6])
@pytest.mark.parametrize("n_perturb", [0, 3])
def test_exact_refinement_is_accepted_at_any_intensity_scale(scale, n_perturb):
    # 1e6 counts, noise-free, centre on a requested bound: the refinement
    # moves the centre 5e-8 eV and chi-square goes 1.6e-24 -> 1.5e-6, above a
    # fixed absolute allowance. The allowance now scales with the data.
    np.random.seed(4)
    x = np.linspace(999.0, 1001.0, 101)
    base = 1000.0 * min(scale, 1.0)
    y = base + scale * np.exp(-4 * np.log(2) * ((x - 1000.0) / 0.5) ** 2)
    specs = [{"id": 1, "shape": "gaussian", "center": 1000.0, "center_min": 1000.0,
              "amplitude": scale, "amplitude_min": 0, "fwhm": 0.5, "fix_fwhm": True}]
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[999.0, base], [1001.0, base]], n_perturb=n_perturb,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True, res["message"]
    assert res["individual_peaks"][0]["params"]["amplitude"]["value"] == pytest.approx(scale, rel=1e-5)


def test_a_materially_worse_refinement_is_still_rejected(monkeypatch):
    real_fit = fitting.Model.fit

    def worse_polish(self, data, params, **kw):
        res = real_fit(self, data, params, **kw)
        if kw.get("method") == "least_squares":
            res.chisqr = res.chisqr * 1.01          # one percent worse than it really is
        return res

    monkeypatch.setattr(fitting.Model, "fit", worse_polish)
    x, y = _two_peak_spectrum()
    res = fitting.run_fit(x, y, _page_like_specs(), background_method="linear", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is False
    assert "generated limits" in res["message"]


# ── Codex round 7 (both runs NO-GO): the allowance ──────────────────────────

@pytest.mark.parametrize("n_perturb", [0, 3])
def test_zero_signal_fit_is_accepted(n_perturb):
    # Flat 1000 counts on a 1000 background: DE puts the amplitude on its
    # requested floor (chi2 ~1e-248), the refinement nudges it to 1e-10
    # (chi2 ~2e-22). An allowance scaled by the background-SUBTRACTED power
    # is zero here and refused it.
    np.random.seed(4)
    x = np.linspace(999.0, 1001.0, 101)
    y = np.full_like(x, 1000.0)
    specs = [{"id": 1, "shape": "gaussian", "center": 1000.0, "fix_center": True, "fwhm": 0.5,
              "fix_fwhm": True, "amplitude": 1.0, "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="manual",
                          manual_bg=[[999.0, 1000.0], [1001.0, 1000.0]], n_perturb=n_perturb,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is True, res["message"]
    assert res["individual_peaks"][0]["params"]["amplitude"]["value"] == pytest.approx(0.0, abs=1e-6)


def _refinement_reported_worse_by(monkeypatch, factor):
    real_fit = fitting.Model.fit

    def worse(self, data, params, **kw):
        res = real_fit(self, data, params, **kw)
        if kw.get("method") == "least_squares":
            res.chisqr = res.chisqr * factor
        return res

    monkeypatch.setattr(fitting.Model, "fit", worse)


def test_one_percent_worse_is_refused_on_a_high_count_spectrum(monkeypatch):
    # 1e6-count Poisson spectrum, 1000 points: the old allowance (1e-8 of the
    # power) was ~10 in chi-square and let a 1 % worse refinement through.
    _refinement_reported_worse_by(monkeypatch, 1.01)
    rng = np.random.default_rng(0)
    x = np.linspace(999.0, 1001.0, 1000)
    y = rng.poisson(1e6 * np.exp(-4 * np.log(2) * ((x - 1000.0) / 15.0) ** 2)).astype(float)
    specs = [{"id": 1, "shape": "gaussian", "center": 1000.0, "fix_center": True, "fwhm": 15.0,
              "fix_fwhm": True, "amplitude": 9e5, "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="none", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is False


def test_one_percent_worse_is_refused_on_normalised_data(monkeypatch):
    _refinement_reported_worse_by(monkeypatch, 1.01)
    rng = np.random.default_rng(1)
    x = np.linspace(280.0, 290.0, 201)
    y = np.exp(-4 * np.log(2) * ((x - 285.0) / 1.2) ** 2) + rng.normal(0, 2e-3, x.size)
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "amplitude": 0.9, "fwhm": 1.0,
              "amplitude_min": 0}]
    res = fitting.run_fit(x, y, specs, background_method="none", n_perturb=0,
                          fit_kws={"method": "differential_evolution"})
    assert res["success"] is False


def test_a_channel_the_objective_omits_does_not_loosen_the_allowance(monkeypatch):
    # One channel with a NaN energy and a huge intensity is dropped from the
    # residual; counted in the allowance it let a 100-fold worse chi-square pass.
    _refinement_reported_worse_by(monkeypatch, 100.0)
    rng = np.random.default_rng(2)
    x = np.linspace(280.0, 290.0, 101)
    y = 1e-4 * np.exp(-4 * np.log(2) * ((x - 285.0) / 1.2) ** 2) + rng.normal(0, 1e-6, x.size)
    x[50], y[50] = np.nan, 1.0
    specs = [{"id": 1, "shape": "gaussian", "center": 285.0, "fix_center": True, "amplitude": 9e-5,
              "fwhm": 1.2, "fix_fwhm": True, "amplitude_min": 0}]
    try:
        res = fitting.run_fit(x, y, specs, background_method="none", n_perturb=0,
                              fit_kws={"method": "differential_evolution"})
    except (ValueError, RuntimeError):
        return                                  # refusing such input outright is also fine
    assert res["success"] is False
