"""'Is this component REQUIRED?' — the refit test (unit step (c), 2026-09-22).

`support` holds the other components at their fitted values, so redundancy
under overlap escapes it (Auto-Fit anchor unit, Codex round 6: a large
Graphite component the other components could absorb if refitted). The refit
without the component is the test for that. It costs one fit, so it runs
only when asked (`require_component`); Auto-Fit asks for its anchor.
"""

import io

import numpy as np
import pytest

import fitting
from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _gl(x, a, c, w, mix=0.3):
    return fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=mix)


def _agl(x, a, c, w):
    return fitting._SHAPE_FUNCS["asymmetric_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=0.3, asymmetry=0.25)


X = np.round(np.arange(280.0, 295.0001, 0.02), 4)


def _autofit_model(graphite_amp, others):
    specs = [{"id": "1", "name": "Graphite", "shape": "asymmetric_gl", "center": 284.5, "center_min": 284.2, "center_max": 284.8,
              "amplitude": graphite_amp, "fwhm": 0.7, "gl_ratio": 0.3, "asymmetry": 0.25, "asymmetry_min": 0.1, "asymmetry_max": 0.5,
              "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0}]
    for k, (a, c, w) in enumerate(others, start=2):
        specs.append({"id": str(k), "shape": "pseudo_voigt_gl", "center": c, "amplitude": a, "fwhm": w, "gl_ratio": 0.3,
                      "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0})
    return specs


KW = dict(background_method="manual", manual_bg=[[280.0, 1000.0], [295.0, 1000.0]], n_perturb=3,
          fit_kws={"method": "least_squares"})


def test_a_redundant_anchor_is_supported_but_not_required():
    # Codex, Auto-Fit anchor unit round 6 (run B): two symmetric GL lines at
    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. Auto-Fit's model puts an
    # asymmetric-GL Graphite at 284.5 with the ±0.3 eV window; the fit gives it
    # a large amplitude (F ~ 1e6 with the others HELD) — yet the other two
    # components fit the data to rounding precision without it.
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    assert res["success"] is True
    g = next(ip for ip in res["individual_peaks"] if ip["id"] == "1")
    assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
    req = res["required"]
    assert req["ran"] is True and req["refit_converged"] is True
    assert req["chi2_without_refit"] <= req["chi2_with"] * 1.001
    assert req["required"] is False


def test_a_real_graphite_anchor_is_required():
    rng = np.random.default_rng(0)
    y = rng.poisson(1000 + _agl(X, 86000, 284.5, 0.7) + _gl(X, 14000, 285.1, 1.9) + _gl(X, 2300, 286.4, 1.4)).astype(float)
    specs = _autofit_model(80000, [(14000, 285.1, 1.9), (2300, 286.4, 1.4)])
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    req = res["required"]
    assert req["ran"] and req["required"] is True and req["f"] > 1000
    assert req["chi2_without_refit"] > req["chi2_with"]


def test_the_fit_itself_is_unchanged_by_the_check():
    import json
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    kw = {**KW, "fit_kws": {"method": "leastsq"}}
    a = fitting.run_fit(X, y, specs, **kw)
    b = fitting.run_fit(X, y, specs, require_component="1", **kw)
    strip = lambda r: json.dumps({k: v for k, v in r.items() if k != "required"}, sort_keys=True)  # noqa: E731
    assert strip(a) == strip(b) and a["required"] is None and b["required"]["ran"] is True


def _linked(pid, master, offset):
    return {"id": pid, "shape": "pseudo_voigt_gl", "center": 284.5 + offset, "amplitude": 100.0, "fwhm": 0.7, "gl_ratio": 0.3,
            "amplitude_min": 0, "constrain_to": master, "splitting": offset, "area_ratio": 0.01}


def test_everything_linked_to_the_removed_component_goes_with_it_transitively():
    # Codex round 1: 1 -> 9 -> 10 raised NameError in the reduced model; and a
    # child ordered BEFORE its parent broke expression construction.
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs += [_linked("9", "1", 1.0), _linked("10", "9", 1.0)]
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    assert res["required"]["ran"] is True, res["required"]
    assert res["required"]["required"] is False
    # remove an UNRELATED component while a kept child precedes its kept parent in the request
    specs2 = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs2 = [specs2[0], _linked("4", "3", 0.8), specs2[1], specs2[2]]           # 4 -> 3, listed before 3
    res2 = fitting.run_fit(X, y, specs2, require_component="2", **KW)
    assert res2["required"]["ran"] is True, res2["required"]
    # Codex round 2: a retained CHAIN in reverse order (10 -> 9 -> 3, listed 10 before 9), removing 1
    specs3 = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)]) + [_linked("10", "9", 0.8), _linked("9", "3", 0.8)]
    res3 = fitting.run_fit(X, y, specs3, require_component="1", **KW)
    assert res3["required"]["ran"] is True, res3["required"]
    specs4 = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs4 = [specs4[0], specs4[1], _linked("4", "3", 0.8), specs4[2]]
    specs4[2]["constrain_to"] = "3"; specs4.append(_linked("5", "4", 0.8)); specs4 = [specs4[0], specs4[1], specs4[4], specs4[2], specs4[3]]
    res4 = fitting.run_fit(X, y, specs4, require_component="1", **KW)
    assert res4["required"]["ran"] is True, res4["required"]


def test_differential_evolution_goes_through_its_own_candidate_machinery():
    # Codex round 1: a direct model.fit under DE failed on the open amplitude bound -> ran:false
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    res = fitting.run_fit(X, y, specs, require_component="1", **{**KW, "n_perturb": 0, "fit_kws": {"method": "differential_evolution"}})
    assert res["success"] is True and res["required"]["ran"] is True, res["required"]
    assert res["required"]["required"] is False


def test_the_refit_of_a_stochastic_method_is_seeded(monkeypatch):
    seeds = []
    real_fit = fitting.Model.fit

    def spy(self, data, params, **kw):
        seeds.append((kw.get("method"), (kw.get("fit_kws") or {}).get("seed")))
        return real_fit(self, data, params, **kw)

    monkeypatch.setattr(fitting.Model, "fit", spy)
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4)])
    fitting.run_fit(X, y, specs, require_component="1", **{**KW, "n_perturb": 0, "fit_kws": {"method": "basinhopping"}})
    bh = [s for m, s in seeds if m == "basinhopping"]
    assert len(bh) == 2 and all(isinstance(s, int) for s in bh) and bh[0] != bh[1]


def test_known_limit_noise_free_exact_fit_reports_a_redundant_component_as_required():
    # Two identical half-amplitude components on noise-free data: removing one
    # is lossless, but the full fit is exact to machine precision (chi2 ~1e-28)
    # so F is meaningless and reads as huge. Every tolerance tried to handle
    # this masked a real anchor at high dynamic range (Codex rounds 2-3), so
    # none is applied: this is a documented limit, not a rule. Real data never
    # fit to machine precision.
    y = 1000 + _gl(X, 10000, 284.8, 1.4)                                     # unrounded: numerically exact
    specs = [{"id": "1", "name": "Graphite", "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 5000.0, "fwhm": 1.4, "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": "2", "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 5000.0, "fwhm": 1.4, "gl_ratio": 0.3, "amplitude_min": 0}]
    res = fitting.run_fit(X, y, specs, require_component="1", **{**KW, "fit_kws": {"method": "leastsq"}})
    assert res["required"]["ran"] is True
    assert res["required"]["chi2_with"] < 1e-12                                # the premise: an exact fit
    # documented: F is meaningless here and the verdict may read "required"; no rule papers over it
    # with Poisson noise the same construction is judged on its merits: lossless -> not required
    rng = np.random.default_rng(3)
    yn = rng.poisson(1000 + _gl(X, 10000, 284.8, 1.4)).astype(float)
    res_n = fitting.run_fit(X, yn, specs, require_component="1", **{**KW, "fit_kws": {"method": "leastsq"}})
    assert res_n["required"]["required"] is False, res_n["required"]


def test_a_resolved_anchor_at_extreme_dynamic_range_is_required():
    # Codex round 3: amplitude 1 beside 1e10 (F ~ 4e3) and 1 beside 3e9 (F ~ 9e2)
    for big in (1e10, 3e9):
        y = np.round(1000 + _agl(X, 1, 284.5, 0.7) + _gl(X, big, 285.1, 1.9) + _gl(X, 2300, 286.4, 1.4), 2)
        specs = _autofit_model(1, [(big, 285.1, 1.9), (2300, 286.4, 1.4)])
        res = fitting.run_fit(X, y, specs, require_component="1", **KW)
        assert res["required"]["ran"] and res["required"]["required"] is True, (big, res["required"])
