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
from fit_equality import assert_same_fit


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _two_basin_problem():
    """Two minima, each well inside its own basin (the two-basin unit, owner 2026-10-04/09).

    A main line at 284.5 eV, a weak shoulder at 285.25, a line at 286.7 and a broad
    satellite at 288.8. The student starts "shoulder" at 285.2 (on the weak shoulder) and
    "sat" at 288.5: Levenberg-Marquardt reaches a genuine, certified minimum (reduced
    chi-square ~47) in which "sat" covers the 286.7 line and the satellite is left
    unfitted. Four of six scattered starts reach the better decomposition (~13.7) by moving
    "shoulder" 1.5 eV onto the 286.7 line; one reaches another, not-better minimum.

    Unlike the fixture it replaces (which sat ON a basin boundary: one rounding step of the
    linear background at 3 of 300 points decided its basin), every outcome here is
    unchanged by rounding-level changes of its input — the floating-point line instead of
    the exact one, ulps of the counts or the start values
    (test_the_two_basin_fixture_is_inside_its_basins) — so no arithmetic is pinned. It runs
    without perturbed restarts (TWO_BASIN_KW): ±15 % redraws of every parameter of a
    multi-minimum model land restarts near basin boundaries, which is the multiple-minima
    property itself (CLAUDE.md, "Determinacy"), not what these tests are about."""
    rng = np.random.default_rng(2)
    x = np.arange(280.0, 295.0, 0.05)
    lam = 300 + _g(x, 284.5, 8000, 0.8) + _g(x, 285.25, 1400, 0.7) + _g(x, 286.7, 3000, 1.0) + _g(x, 288.8, 600, 1.8)
    y = rng.poisson(lam).astype(float)
    specs = [{"id": 1, "name": "main", "shape": "gaussian", "center": 284.6, "amplitude": 6000.0, "amplitude_min": 0, "fwhm": 1.0},
             {"id": 2, "name": "shoulder", "shape": "gaussian", "center": 285.2, "amplitude": 2000.0, "amplitude_min": 0, "fwhm": 1.0},
             {"id": 3, "name": "sat", "shape": "gaussian", "center": 288.5, "amplitude": 500.0, "amplitude_min": 0, "fwhm": 2.0}]
    return x, y, specs


def _well_posed():
    rng = np.random.default_rng(3)
    x = np.arange(280.0, 295.0, 0.1)
    y = rng.poisson(200.0 + _g(x, 284.8, 4000.0, 1.1) + _g(x, 288.6, 900.0, 1.4)).astype(float)
    specs = [{"id": 1, "shape": "pseudo_voigt_gl", "center": 284.6, "amplitude": 3500.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": 2, "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0}]
    return x, y, specs


KW = dict(background_method="linear", n_perturb=3)
TWO_BASIN_KW = dict(background_method="linear", n_perturb=0)     # _two_basin_problem's request (no perturbed restarts)


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


def test_the_fit_is_the_same_with_and_without_the_check():
    # THE FIT is what the student asked for; the check only adds a report.
    # Equal within rounding (unit A2: a fit the minimum certificate moves
    # carries Trust-Region's arithmetic; tests/fit_equality.py).
    for make, kw in ((_well_posed, KW), (_two_basin_problem, TWO_BASIN_KW)):
        x, y, specs = make()
        a = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **kw)
        b = fitting.run_fit(x, y, specs, n_starts=5, fit_kws={"method": "leastsq"}, **kw)
        assert_same_fit(json.loads(_strip(a)), json.loads(_strip(b)))


def test_a_lower_chi_square_solution_is_reported_beside_the_fit_not_instead_of_it():
    x, y, specs = _two_basin_problem()
    res = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **TWO_BASIN_KW)
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
    no_check = fitting.run_fit(x, y, specs, fit_kws={"method": "leastsq"}, **TWO_BASIN_KW)
    assert_same_fit(json.loads(_strip(res)), json.loads(_strip(no_check)))


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


def test_the_starts_are_a_pure_function_of_the_request(monkeypatch):
    # Identical requests give the same seed, the same scattered starting points — whatever
    # the global generator holds — and the same response (within rounding: the certificate
    # carries Trust-Region's arithmetic, tests/fit_equality.py). Restored on the two-basin
    # fixture now that it lies inside its basins (owner 2026-10-04: narrowed to the draws
    # while the old fixture sat on a boundary).
    x, y, specs = _two_basin_problem()
    drawn, real = [], fitting._scattered_start

    def record(params, rng):
        out = real(params, rng)
        drawn[-1].append({k: (p.value, p.min, p.max, p.vary, p.expr) for k, p in out.items()})
        return out
    monkeypatch.setattr(fitting, "_scattered_start", record)
    drawn.append([])
    a = fitting.run_fit(x, y, specs, n_starts=4, fit_kws={"method": "leastsq"}, **TWO_BASIN_KW)
    np.random.seed(99)                                 # the global generator is irrelevant
    drawn.append([])
    b = fitting.run_fit(x, y, specs, n_starts=4, fit_kws={"method": "leastsq"}, **TWO_BASIN_KW)
    assert a["starts"]["ran"] and a["random_seed"] == b["random_seed"]
    assert len(drawn[0]) == 4 and drawn[0] == drawn[1]  # the same four starting points, bit for bit
    assert a["starts"]["alternatives"], "the comparison covers an alternative"
    assert_same_fit(a, b)                              # and the same response, starts included


def _float_line_through(x, x0, y0, x1, y1, span=None):
    """The linear background as y0 + slope (x − x0) in floating point — what fitting.py did
    before it evaluated the line exactly (background math, round 11): up to an ulp away."""
    y0, y1 = float(y0), float(y1)
    slope = (y1 - y0) / (x1 - x0) if x1 != x0 else 0.0
    return fitting._explicit_background(y0 + slope * (np.asarray(x, dtype=float) - x0), "Linear")


def test_the_two_basin_fixture_is_inside_its_basins(monkeypatch):
    # What the fixture promises: rounding-level changes of its input change nothing — the
    # fit, its certificate, every scattered start's solution (the request seed held fixed:
    # the counts enter the seed). The fixture it replaces moved basins on an ulp of 3 of its
    # 300 background points.
    x, y, specs = _two_basin_problem()
    run = lambda yy, sp, seed=None: fitting.run_fit(                              # noqa: E731
        x, yy, sp, n_starts=6, fit_kws={"method": "leastsq", **({"fit_kws": {"seed": seed}} if seed else {})}, **TWO_BASIN_KW)
    base = run(y, specs)
    st = base["starts"]
    assert base["certificate"]["certified"] and not base["certificate"]["moved"], "the student's fit is itself a minimum"
    assert st["alternatives"] and st["n_not_better_elsewhere"] >= 1 and st["n_same_as_fit"] >= 1
    seed = base["random_seed"]
    rng = np.random.default_rng(7)
    variants = []
    for k in range(3):
        yy = y.copy(); idx = rng.choice(len(y), 5, replace=False)
        yy[idx] = np.nextafter(yy[idx], np.inf if k % 2 == 0 else -np.inf)
        variants.append((f"ulps of the counts ({k})", yy, specs))
    for f in (1 + 4 * 2.0 ** -53, 1 - 4 * 2.0 ** -53):
        sp = [{**s, **{q: s[q] * f for q in ("center", "amplitude", "fwhm")}} for s in specs]
        variants.append((f"start values x {f!r}", y, sp))
    for label, yy, sp in variants:
        r = run(yy, sp, seed)
        assert_same_fit({**base, "random_seed": None}, {**r, "random_seed": None}), label
    monkeypatch.setattr(fitting, "_line_through", _float_line_through)
    assert_same_fit(base, run(y, specs))               # the floating-point line: the same fit, the same seed


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
    assert 0.05 - 1e-9 <= glr.min() and glr.max() <= 0.95 + 1e-9     # a SHAPE parameter is redrawn, off the bound it started on
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
    csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(x, y))    # full precision, as the page uploads since 2026-10-03
    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
    body = {"session_id": sid, "background": {"method": "linear"}, "peaks": specs, "fit_method": "leastsq", "n_perturb": 0}
    assert client.post("/api/fit", json=body).get_json()["starts"] is None
    st = client.post("/api/fit", json={**body, "n_starts": 6}).get_json()["starts"]
    assert st["ran"] is True and st["alternatives"] and abs(st["alternatives"][0]["largest_centre_shift_from_start"]["ev"]) > 1.0


def test_n_starts_does_not_enter_the_seed():
    x, y, specs = _well_posed()
    seeds = {fitting.run_fit(x, y, specs, n_starts=k, fit_kws={"method": "leastsq"}, **KW)["random_seed"] for k in (0, 3, 7)}
    assert len(seeds) == 1


def test_solutions_are_compared_by_component_identity_never_by_permutation():
    # Codex round 1: "C-O" at 286.4 eV / 60 % and "C=O" at 288.0 eV / 40 %, both GL. A start that
    # reverses them is a DIFFERENT chemical reading; a lineshape-based permutation rule merged them,
    # which can inflate "reached this solution" or hide a lower-chi-square swapped solution.
    comp = lambda i, c, f: {"id": i, "area_percent": f, "params": {"center": c}}  # noqa: E731
    a = [comp(1, 286.4, 60.0), comp(2, 288.0, 40.0)]
    assert fitting._same_solution(a, [comp(1, 286.45, 60.6), comp(2, 288.05, 39.4)])
    assert not fitting._same_solution(a, [comp(1, 288.0, 40.0), comp(2, 286.4, 60.0)])
    assert not fitting._same_solution(a, [comp(1, 286.4, 58.5), comp(2, 288.0, 41.5)])
    assert not fitting._same_solution(a, [comp(1, 286.55, 60.0), comp(2, 288.0, 40.0)])


def test_the_scatter_keeps_the_documented_ranges_beside_a_wall_and_the_sign_of_an_amplitude():
    # Codex round 1: a 5 %-of-range margin turned fwhm 0.1 in [0.1, 15] into exactly 0.845 and a
    # centre of 1 in [0, 100] into exactly 5; a negative amplitude came back positive.
    p = Parameters()
    p.add("p1_amplitude", value=-100.0)                       # open both sides
    p.add("p1_fwhm", value=0.1, min=0.1, max=15.0)            # ON its lower wall
    p.add("p1_center", value=1.0, min=0.0, max=100.0)
    rng = np.random.default_rng(2)
    seen = [fitting._scattered_start(p, rng) for _ in range(300)]
    amp = np.array([q["p1_amplitude"].value for q in seen]); wid = np.array([q["p1_fwhm"].value for q in seen])
    cen = np.array([q["p1_center"].value for q in seen])
    assert amp.max() < 0 and -300 - 1e-9 <= amp.min() and amp.max() <= -100 / 3 + 1e-9
    assert 0.1 < wid.min() and wid.max() <= 0.15 + 1e-9 and len(set(np.round(wid, 6))) > 50
    assert 0.5 - 1e-9 <= cen.min() and cen.max() <= 1.5 + 1e-9 and len(set(np.round(cen, 6))) > 50


def test_starts_and_solutions_are_counted_separately():
    x, y, specs = _two_basin_problem()
    st = fitting.run_fit(x, y, specs, n_starts=6, fit_kws={"method": "leastsq"}, **TWO_BASIN_KW)["starts"]
    assert st["n_in_alternatives"] == sum(a["n_starts"] for a in st["alternatives"]) >= 1
    assert st["n_same_as_fit"] + st["n_not_better_elsewhere"] + st["n_in_alternatives"] == st["n_converged"]
