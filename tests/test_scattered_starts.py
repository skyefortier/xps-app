"""Scattered-starts check (unit step (a), 2026-09-21).

Measured on the lab's 202 committed fit targets: the default method's result
is more than 5 pp of area fraction from the best known solution on 7.8 % of
not-yet-fitted starts, and a second METHOD from the same start shares the
minimum too often to expose it. Three more fits of the SAME method from
scattered starts do. Owner decisions pinned here: the student's fit is never
replaced; only LOWER-chi-square solutions are listed, with how far each
component moved from the student's start; solutions that are not better are
counted, not listed; nothing about the fit itself changes.
"""

import io
import json

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


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _two_basin_problem():
    """A main line with a shoulder 2.2 eV away and a weak satellite. Both
    leading components are started between the two features, so the student's
    Levenberg-Marquardt fit stops in a poor minimum (reduced chi-square ~30)
    while other starts find the real decomposition (~1.2) by moving a
    component more than 1 eV from where the student put it."""
    rng = np.random.default_rng(5)
    x = np.arange(280.0, 295.0, 0.05)
    for _ in range(3):                                   # keep the generator state of the probe that found it
        rng.poisson(300 + _g(x, 284.5, 8000, 0.8)).astype(float)
    y = rng.poisson(300 + _g(x, 284.5, 8000, 0.8) + _g(x, 286.7, 2500, 1.2) + _g(x, 288.5, 600, 1.8)).astype(float)
    specs = [{"id": 1, "name": "main", "shape": "gaussian", "center": 285.6, "amplitude": 3000.0, "amplitude_min": 0, "fwhm": 1.5},
             {"id": 2, "name": "shoulder", "shape": "pseudo_voigt_gl", "gl_ratio": 0.0, "fix_gl_ratio": True, "center": 285.7,
              "amplitude": 3000.0, "amplitude_min": 0, "fwhm": 1.5},
             {"id": 3, "name": "sat", "shape": "gaussian", "center": 288.0, "amplitude": 500.0, "amplitude_min": 0, "fwhm": 2.0}]
    return x, y, specs


def _well_posed():
    rng = np.random.default_rng(3)
    x = np.arange(280.0, 295.0, 0.1)
    y = rng.poisson(200.0 + _g(x, 284.8, 4000.0, 1.1) + _g(x, 288.6, 900.0, 1.4)).astype(float)
    specs = [{"id": 1, "shape": "pseudo_voigt_gl", "center": 284.6, "amplitude": 3500.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": 2, "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0}]
    return x, y, specs


KW = dict(background_method="linear", n_perturb=3)


def _strip(res):
    return json.dumps({k: v for k, v in res.items() if k != "starts"}, sort_keys=True)


def test_default_is_off_and_the_response_says_nothing():
    x, y, specs = _well_posed()
    assert fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **KW)["starts"] is None


def test_a_well_posed_fit_reports_that_every_start_reached_it():
    x, y, specs = _well_posed()
    st = fitting.run_fit(x, y, specs, n_starts=3, fit_kws={"method": "leastsq"}, **KW)["starts"]
    assert st["ran"] is True and st["n_run"] == 3
    assert st["n_converged"] == 3 and st["n_same_as_fit"] == 3
    assert st["alternatives"] == [] and st["n_not_better_elsewhere"] == 0
    assert [c["id"] for c in st["fit"]["components"]] == [1, 2]


def test_the_fit_is_byte_identical_with_and_without_the_check():
    # THE FIT is what the student asked for; the check only adds a report.
    # (Levenberg-Marquardt is bitwise repeatable; Trust-Region is not.)
    for make in (_well_posed, _two_basin_problem):
        x, y, specs = make()
        a = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **KW)
        b = fitting.run_fit(x, y, specs, n_starts=5, fit_kws={"method": "leastsq"}, **KW)
        assert _strip(a) == _strip(b)


def test_a_lower_chi_square_solution_is_reported_beside_the_fit_not_instead_of_it():
    x, y, specs = _two_basin_problem()
    res = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **KW)
    st = res["starts"]
    fit_chi = res["statistics"]["reduced_chi_square"]
    assert st["fit"]["chi2r"] == pytest.approx(fit_chi)
    assert st["alternatives"], "the scattered starts must find the two-line solution"
    alt = st["alternatives"][0]
    assert alt["chi2r"] < fit_chi * (1 - 1e-3)
    assert st["alternatives"] == sorted(st["alternatives"], key=lambda a: a["chi2r"])
    # it carries its own areas and what is needed to apply it ...
    assert [c["id"] for c in alt["components"]] == [1, 2, 3]
    assert sum(c["area_percent"] for c in alt["components"]) == pytest.approx(100.0)
    assert {"center", "amplitude", "fwhm"} <= set(alt["components"][0]["params"])
    # ... and how far each component moved from the STUDENT'S START (not from the fit)
    for c, spec in zip(alt["components"], specs):
        assert c["center_shift_from_start"] == pytest.approx(c["params"]["center"] - spec["center"])
    big = alt["largest_centre_shift_from_start"]
    assert abs(big["ev"]) == max(abs(c["center_shift_from_start"]) for c in alt["components"])
    assert abs(big["ev"]) > 1.0                       # a relocated component is visible at a glance
    assert alt["largest_fraction_difference_pp"] > 1.0
    # and the fit's own parameters are what the student's method returned
    centres = sorted(p["params"]["center"]["value"] for p in res["individual_peaks"])
    no_check = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **KW)
    assert centres == sorted(p["params"]["center"]["value"] for p in no_check["individual_peaks"])


def test_solutions_that_are_not_better_are_counted_not_listed(monkeypatch):
    # make every scattered start land somewhere worse than the fit
    real = fitting._scattered_start

    def bad_start(params, rng):
        out = real(params, rng)
        for name, par in out.items():
            if name.endswith("_center") and par.vary:
                par.set(value=par.max - 0.01)
            if name.endswith("_fwhm") and par.vary:
                par.set(value=par.max * 0.9)
        return out

    monkeypatch.setattr(fitting, "_scattered_start", bad_start)
    x, y, specs = _well_posed()
    specs = [{**s, "center_min": 281.0, "center_max": 294.5} for s in specs]
    res = fitting.run_fit(x, y, specs, n_starts=3, fit_kws={"method": "leastsq"}, **KW)
    st = res["starts"]
    assert st["alternatives"] == []
    assert st["n_same_as_fit"] + st["n_not_better_elsewhere"] == st["n_converged"]
    if st["n_not_better_elsewhere"]:
        assert all(c >= st["fit"]["chi2r"] * (1 - 1e-3) for c in st["not_better_chi2r"])
        assert "components" not in json.dumps(st["not_better_chi2r"])


def test_the_starts_are_a_pure_function_of_the_request():
    x, y, specs = _two_basin_problem()
    a = fitting.run_fit(x, y, specs, n_starts=4, fit_kws={"method": "leastsq"}, **KW)["starts"]
    np.random.seed(99)                                 # the global generator is irrelevant
    b = fitting.run_fit(x, y, specs, n_starts=4, fit_kws={"method": "leastsq"}, **KW)["starts"]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_the_third_stream_leaves_the_existing_draws_alone():
    seq = np.random.SeedSequence(12345)
    two = [np.random.default_rng(c).uniform(size=4).tolist() for c in seq.spawn(2)]
    three = [np.random.default_rng(c).uniform(size=4).tolist() for c in np.random.SeedSequence(12345).spawn(3)]
    assert three[:2] == two and three[2] not in two


def test_the_scatter_is_anchored_to_the_request_and_stays_inside_its_bounds():
    p = Parameters()
    p.add("p1_amplitude", value=1000.0, min=0.0)
    p.add("p1_center", value=285.0, min=283.0, max=287.0)
    p.add("p1_fwhm", value=1.0, min=0.1, max=15.0)
    p.add("p1_gl_ratio", value=0.0, min=0.0, max=1.0)            # sitting ON a bound at the start
    p.add("p1_m", value=50.0, min=0.0, max=499.0)                # integer kernel width: left alone
    p.add("p2_amplitude", value=400.0, min=0.0, vary=False)      # fixed: left alone
    p.add("p2_center", expr="p1_center + 1.6")                   # linked: left alone
    rng = np.random.default_rng(1)
    seen = [fitting._scattered_start(p, rng) for _ in range(200)]
    amp = np.array([q["p1_amplitude"].value for q in seen])
    cen = np.array([q["p1_center"].value for q in seen])
    wid = np.array([q["p1_fwhm"].value for q in seen])
    glr = np.array([q["p1_gl_ratio"].value for q in seen])
    assert 1000 / 3 - 1e-9 <= amp.min() and amp.max() <= 3000 + 1e-9 and amp.std() > 100
    assert 284.5 - 1e-9 <= cen.min() and cen.max() <= 285.5 + 1e-9
    assert 1 / 1.5 - 1e-9 <= wid.min() and wid.max() <= 1.5 + 1e-9
    assert 0.05 - 1e-9 <= glr.min() and glr.max() <= 0.95 + 1e-9     # moved OFF the bound it started on
    assert all(q["p1_m"].value == 50.0 and q["p2_amplitude"].value == 400.0 and q["p2_center"].expr for q in seen)
    assert p["p1_amplitude"].value == 1000.0 and p["p1_gl_ratio"].value == 0.0   # the request's start is not mutated
    # a start outside the centre window cannot be produced
    p["p1_center"].set(value=286.9)
    assert max(fitting._scattered_start(p, rng)["p1_center"].value for _ in range(100)) <= 287.0


@pytest.mark.parametrize("specs_mod,method,reason", [
    (lambda s: s[:1], "leastsq", "single_component"),
    (lambda s: [s[0], {**s[1], "constrain_to": 1, "splitting": 3.8, "area_ratio": 0.2}], "leastsq", "single_component"),
    (lambda s: s, "differential_evolution", "method"),
    (lambda s: s, "basinhopping", "method"),
])
def test_where_the_check_does_not_run_it_says_why(specs_mod, method, reason):
    x, y, specs = _well_posed()
    res = fitting.run_fit(x, y, specs_mod(specs), background_method="linear", n_perturb=0, n_starts=3,
                          fit_kws={"method": method})
    assert res["starts"] == {"ran": False, "reason": reason}


def test_a_failure_inside_the_check_never_costs_the_student_the_fit(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("clustering exploded")

    monkeypatch.setattr(fitting, "_solution_components", boom)
    x, y, specs = _well_posed()
    res = fitting.run_fit(x, y, specs, n_starts=3, fit_kws={"method": "leastsq"}, **KW)
    assert res["success"] is True
    assert res["starts"]["ran"] is False and res["starts"]["reason"] == "error"
    assert "clustering exploded" in res["starts"]["error"]


def test_a_start_that_raises_or_does_not_converge_is_not_counted(monkeypatch):
    x, y, specs = _well_posed()
    real = fitting._scattered_start
    calls = {"n": 0}

    def sometimes_broken(params, rng):
        calls["n"] += 1
        out = real(params, rng)
        if calls["n"] == 2:
            out["p1_fwhm"].set(value=float("nan"))
        return out

    monkeypatch.setattr(fitting, "_scattered_start", sometimes_broken)
    st = fitting.run_fit(x, y, specs, n_starts=3, fit_kws={"method": "leastsq"}, **KW)["starts"]
    assert st["n_run"] == 3 and st["n_converged"] <= 3
    assert st["n_same_as_fit"] + st["n_not_better_elsewhere"] + sum(a["n_starts"] for a in st["alternatives"]) == st["n_converged"]


@pytest.mark.parametrize("bad", [-1, 11, 2.5, "3", True])
def test_n_starts_is_validated(bad, client):
    x, y, specs = _well_posed()
    with pytest.raises(ValueError, match="n_starts"):
        fitting.run_fit(x, y, specs, n_starts=bad, fit_kws={"method": "leastsq"}, **KW)
    csv = "\n".join(f"{a:.3f},{b:.2f}" for a, b in zip(x, y))
    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
    resp = client.post("/api/fit", json={"session_id": sid, "background": {"method": "linear"}, "peaks": specs,
                                         "fit_method": "leastsq", "n_perturb": 3, "n_starts": bad})
    assert resp.status_code == 400 and "n_starts" in resp.get_json()["error"]


def test_the_api_passes_the_check_through(client):
    x, y, specs = _two_basin_problem()
    csv = "\n".join(f"{a:.3f},{b:.2f}" for a, b in zip(x, y))
    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
    body = {"session_id": sid, "background": {"method": "linear"}, "peaks": specs, "fit_method": "leastsq", "n_perturb": 3}
    assert client.post("/api/fit", json=body).get_json()["starts"] is None
    st = client.post("/api/fit", json={**body, "n_starts": 6}).get_json()["starts"]
    assert st["ran"] is True and st["alternatives"] and abs(st["alternatives"][0]["largest_centre_shift_from_start"]["ev"]) > 1.0


def test_n_starts_does_not_enter_the_seed():
    x, y, specs = _well_posed()
    seeds = {fitting.run_fit(x, y, specs, n_starts=k, fit_kws={"method": "leastsq"}, **KW)["random_seed"] for k in (0, 3, 7)}
    assert len(seeds) == 1


def test_two_interchangeable_components_that_swapped_labels_are_one_solution():
    comp = lambda i, shape, c, f: {"id": i, "shape": shape, "area_percent": f, "params": {"center": c}}  # noqa: E731
    a = [comp(1, "gaussian", 284.0, 60.0), comp(2, "gaussian", 291.5, 40.0)]
    swapped = [comp(1, "gaussian", 291.5, 40.0), comp(2, "gaussian", 284.0, 60.0)]
    assert fitting._same_solution(a, swapped)
    # ... but not when the lineshapes differ: "C-O" sitting on the main line is a different reading
    other = [comp(1, "gaussian", 291.5, 40.0), comp(2, "pseudo_voigt_gl", 284.0, 60.0)]
    assert not fitting._same_solution([comp(1, "gaussian", 284.0, 60.0), comp(2, "pseudo_voigt_gl", 291.5, 40.0)], other)
    assert not fitting._same_solution(a, [comp(1, "gaussian", 284.0, 58.5), comp(2, "gaussian", 291.5, 41.5)])
    assert not fitting._same_solution(a, [comp(1, "gaussian", 284.15, 60.0), comp(2, "gaussian", 291.5, 40.0)])
