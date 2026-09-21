"""An identical fit request must give an identical answer.

Measured 2026-09-19 (docs/findings/2026-09-fit-determinacy.md): the page sends
``n_perturb: 3`` and the server perturbed from an UNSEEDED generator, so five
presses of Run Fit on one committed C 1s scan gave reduced chi-square 70.6,
18.5, 70.6, 38.3, 18.5. A saved project could not regenerate its own figure.
Every random draw in ``run_fit`` is now derived from the request itself.

What that does and does not buy (measured while writing these tests):
Levenberg-Marquardt (MINPACK) and Nelder-Mead are then BYTE-identical from
press to press. Trust-Region (scipy ``least_squares``, the page's default) is
not and cannot be made so by seeding: OpenBLAS's dot product rounds
differently (one unit in the last place) depending on where its argument
sits in memory, and scipy's trust-region iteration amplifies that to ~1e-4
relative in component areas at its stopping tolerance of 1e-8. So for
Trust-Region these tests pin the seeds and draws exactly and the RESULT to a
stated tolerance.
"""

import io
import json

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


def _crowded_c1s(seed=11):
    """Five overlapping components: a model with several minima, where the
    perturbation decides which one is returned."""
    rng = np.random.default_rng(seed)
    x = np.arange(280.0, 296.0, 0.1)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = rng.poisson(400.0 + g(284.4, 9000, 0.7) + g(284.9, 2500, 1.6) + g(286.3, 900, 1.4)
                    + g(288.0, 500, 2.2) + g(291.0, 450, 3.0)).astype(float)
    specs = [
        {"id": 1, "shape": "asymmetric_gl", "center": 284.4, "amplitude": 8000.0, "fwhm": 0.8,
         "gl_ratio": 0.2, "asymmetry": 0.1, "asymmetry_min": 0.1, "asymmetry_max": 0.5, "amplitude_min": 0},
        {"id": 2, "shape": "pseudo_voigt_gl", "center": 284.8, "amplitude": 2000.0, "fwhm": 1.9, "gl_ratio": 0.0, "amplitude_min": 0},
        {"id": 3, "shape": "pseudo_voigt_gl", "center": 286.4, "amplitude": 700.0, "fwhm": 1.4, "gl_ratio": 0.0, "amplitude_min": 0},
        {"id": 4, "shape": "pseudo_voigt_gl", "center": 287.3, "amplitude": 600.0, "fwhm": 3.5, "gl_ratio": 0.0, "amplitude_min": 0},
        {"id": 5, "shape": "pseudo_voigt_gl", "center": 291.1, "amplitude": 500.0, "fwhm": 3.4, "gl_ratio": 0.5, "amplitude_min": 0},
    ]
    return x, y, specs


def _dump(result):
    return json.dumps(result, sort_keys=True)


def _spy_on_fits(monkeypatch):
    records = []
    real_fit = fitting.Model.fit

    def spy(self, data, params, **kw):
        records[-1].append({"start": {n: p.value for n, p in params.items()},
                            "method": kw.get("method"), "seed": (kw.get("fit_kws") or {}).get("seed")})
        return real_fit(self, data, params, **kw)

    monkeypatch.setattr(fitting.Model, "fit", spy)
    return records


def test_perturbed_starts_are_byte_identical_with_a_deterministic_method(monkeypatch):
    # Levenberg-Marquardt has no alignment-dependent arithmetic, so identical
    # draws show up as byte-identical perturbed starting points.
    records = _spy_on_fits(monkeypatch)
    x, y, specs = _crowded_c1s()
    for _ in range(3):
        records.append([])
        fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq"})
    starts = [[tuple(sorted(r["start"].items())) for r in run] for run in records]
    assert len(starts[0]) == 4                       # the first fit + three perturbed refits
    assert len(set(starts[0][1:])) == 3              # the three perturbations differ from each other
    assert starts[0] == starts[1] == starts[2]


def test_trust_region_perturbation_factors_are_identical(monkeypatch):
    # The first Trust-Region solution jitters at ~1e-5 (see the module
    # docstring), so compare the DRAWS: perturbed start / first solution.
    records = _spy_on_fits(monkeypatch)
    x, y, specs = _crowded_c1s()
    finals = []
    for _ in range(2):
        records.append([])
        finals.append(fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3,
                                      fit_kws={"method": "least_squares"}))
    for k in (1, 2, 3):
        a, b = records[0][k]["start"], records[1][k]["start"]
        for name in a:
            assert a[name] == pytest.approx(b[name], rel=1e-3, abs=1e-12), (k, name)
    fr = []
    for res in finals:
        areas = np.array([p["params"]["area"]["value"] for p in res["individual_peaks"]])
        fr.append(100 * areas / areas.sum())
    assert np.max(np.abs(fr[0] - fr[1])) < 0.05      # percentage points; unseeded this model moved by tens


@pytest.mark.parametrize("method", ["leastsq", "nelder"])
def test_repeated_fits_are_byte_identical(method):
    x, y, specs = _crowded_c1s()
    dumps = {_dump(fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3,
                                   fit_kws={"method": method})) for _ in range(3)}
    assert len(dumps) == 1


def _two_peaks():
    rng = np.random.default_rng(3)
    x = np.arange(280.0, 295.0, 0.1)

    def g(c, a, w):
        return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)

    y = rng.poisson(200.0 + g(284.8, 4000.0, 1.1) + g(288.6, 900.0, 1.4)).astype(float)
    specs = [{"id": 1, "shape": "pseudo_voigt_gl", "center": 284.6, "amplitude": 3500.0, "fwhm": 1.2,
              "gl_ratio": 0.3, "amplitude_min": 0},
             {"id": 2, "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0, "fwhm": 1.2,
              "gl_ratio": 0.3, "amplitude_min": 0}]
    return x, y, specs


@pytest.mark.parametrize("method,n_perturb", [("differential_evolution", 2), ("basinhopping", 1)])
def test_stochastic_methods_get_request_derived_seeds_not_the_global_generator(monkeypatch, method, n_perturb):
    # lmfit passes seed=None to both, i.e. numpy's GLOBAL generator: another
    # request in the same worker, or a restart, changed the answer.
    records = _spy_on_fits(monkeypatch)
    x, y, specs = _two_peaks()
    for global_seed in (0, 12345):
        np.random.seed(global_seed)
        records.append([])
        fitting.run_fit(x, y, specs, background_method="linear", n_perturb=n_perturb, fit_kws={"method": method})
    seeds = [[r["seed"] for r in run if r["method"] == method] for run in records]
    assert len(seeds[0]) == n_perturb + 1
    assert all(isinstance(s, int) for s in seeds[0])
    assert len(set(seeds[0])) == n_perturb + 1       # each minimisation its own population
    assert seeds[0] == seeds[1]                      # and the same ones on every press
    # the local refinement / local candidate never receives a solver seed
    assert all(r["seed"] is None for run in records for r in run if r["method"] != method)


@pytest.mark.parametrize("method", ["leastsq", "least_squares", "nelder"])
def test_deterministic_methods_receive_no_solver_seed(monkeypatch, method):
    records = _spy_on_fits(monkeypatch)
    records.append([])
    x, y, specs = _two_peaks()
    fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1, fit_kws={"method": method})
    assert [r["seed"] for r in records[0]] == [None, None]


def test_the_seed_is_a_pure_function_of_the_request():
    x, y, specs = _two_peaks()
    kw = dict(background_method="linear", bg_start_idx=None, bg_end_idx=None, endpoint_avg=1,
              manual_bg=None, fit_kws={"method": "least_squares"}, n_perturb=3)
    base = fitting._request_seed(x, y, specs, **kw)
    assert base == fitting._request_seed(x.copy(), y.copy(), json.loads(json.dumps(specs)), **kw)
    # key order and int-vs-float spelling of the same number do not matter (JSON from a browser)
    respelt = [dict(reversed(list({**s, "amplitude_min": 0.0}.items()))) for s in specs]
    assert base == fitting._request_seed(x, y, respelt, **kw)
    # anything that changes the request changes the seed
    y2 = y.copy(); y2[7] += 1
    moved = [{**specs[0], "center": 284.61}, specs[1]]
    assert len({base,
                fitting._request_seed(x, y2, specs, **kw),
                fitting._request_seed(x, y, moved, **kw),
                fitting._request_seed(x, y, specs, **{**kw, "n_perturb": 2}),
                fitting._request_seed(x, y, specs, **{**kw, "background_method": "shirley"}),
                fitting._request_seed(x, y, specs, **{**kw, "fit_kws": {"method": "leastsq"}})}) == 6


def test_the_seed_derivation_is_pinned():
    # Changing how the seed is derived silently changes the answer every saved
    # project regenerates. If this fails, that is a versioned, announced change.
    x = np.array([1.0, 2.0, 3.0])
    y = np.array([10.0, 20.0, 10.0])
    specs = [{"id": 1, "shape": "gaussian", "center": 2.0, "amplitude": 10.0, "fwhm": 1.0}]
    seed = fitting._request_seed(x, y, specs, background_method="none", bg_start_idx=None, bg_end_idx=None,
                                 endpoint_avg=1, manual_bg=None, fit_kws={"method": "least_squares"}, n_perturb=3)
    assert seed == PINNED_SEED


PINNED_SEED = 705102460  # xps-fit-seed-v1; recorded once from the implementation, never edited


def test_the_response_reports_its_seed():
    x, y, specs = _two_peaks()
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=3,
                          fit_kws={"method": "least_squares"})
    assert res["random_seed"] == fitting._request_seed(
        x, y, specs, background_method="linear", bg_start_idx=None, bg_end_idx=None, endpoint_avg=1,
        manual_bg=None, fit_kws={"method": "least_squares"}, n_perturb=3)


def test_a_caller_supplied_seed_wins_and_is_reported():
    x, y, specs = _two_peaks()
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1,
                        fit_kws={"method": "differential_evolution", "fit_kws": {"seed": 4}})
    b = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1,
                        fit_kws={"method": "differential_evolution", "fit_kws": {"seed": 4}})
    assert a["random_seed"] == b["random_seed"] == 4
    assert a["statistics"]["reduced_chi_square"] == pytest.approx(b["statistics"]["reduced_chi_square"], rel=1e-6)


@pytest.mark.parametrize("method,exact", [("leastsq", True), ("least_squares", False)])
def test_api_fit_from_separate_uploads_repeats(client, method, exact):
    # What "press Run Fit again" is: a new upload of the same points, then
    # the same request.
    x, y, specs = _crowded_c1s()
    csv = "\n".join(f"{a:.3f},{b:.2f}" for a, b in zip(x, y))
    bodies = []
    for _ in range(3):
        up = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "c1s.csv")})
        resp = client.post("/api/fit", json={
            "session_id": up.get_json()["session_id"], "background": {"method": "shirley"},
            "peaks": specs, "fit_method": method, "n_perturb": 3})
        assert resp.status_code == 200
        bodies.append(resp.get_data())
    if exact:
        assert bodies[0] == bodies[1] == bodies[2]
        return
    parsed = [json.loads(b) for b in bodies]
    assert len({p["random_seed"] for p in parsed}) == 1
    fr = []
    for p in parsed:
        areas = np.array([pk["params"]["area"]["value"] for pk in p["individual_peaks"]])
        fr.append(100 * areas / areas.sum())
    assert max(np.max(np.abs(f - fr[0])) for f in fr) < 0.05
