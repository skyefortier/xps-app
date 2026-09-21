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
relative in component areas at its stopping tolerance of 1e-8. Worse, the
perturbed restarts start from that jittering solution, and on a model with
several minima a 1e-5 difference in a start can send a restart into another
basin: on the five-component model below two presses of the SEEDED request
differed by 29 percentage points (on the lab's 202 committed targets that
happened once, by 0.30). So for Trust-Region these tests pin what is exactly
true — the seed and the draws — and deliberately assert nothing about the
result; for Levenberg-Marquardt and Nelder-Mead they assert byte identity.
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
        rec = {"start": {n: p.value for n, p in params.items()},
               "bounds": {n: (p.min, p.max) for n, p in params.items()},
               "method": kw.get("method"), "seed": (kw.get("fit_kws") or {}).get("seed")}
        records[-1].append(rec)
        res = real_fit(self, data, params, **kw)
        rec["end"] = {n: p.value for n, p in res.params.items()}
        rec["vary"] = {n: bool(p.vary) and p.expr is None for n, p in res.params.items()}
        return res

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


def test_trust_region_perturbation_draws_are_exactly_identical(monkeypatch):
    # The first Trust-Region solution jitters at ~1e-5 from press to press
    # (see the module docstring), so the perturbed STARTS differ by that much.
    # The DRAWS must not: draw = perturbed start / the solution it perturbed,
    # both taken from the same press, for every parameter the clip left alone.
    records = _spy_on_fits(monkeypatch)
    x, y, specs = _crowded_c1s()
    for _ in range(2):
        records.append([])
        fitting.run_fit(x, y, specs, background_method="shirley", n_perturb=3, fit_kws={"method": "least_squares"})

    def draws(run):
        best, out = run[0]["end"], []
        for k in (1, 2, 3):
            row = {}
            for name, start in run[k]["start"].items():
                lo, hi = run[k]["bounds"][name]
                if run[0]["vary"][name] and best[name] != 0 and lo < start < hi:
                    row[name] = start / best[name]
            out.append(row)
            if run[k].get("end") and fitting_would_adopt(run, k):
                best = run[k]["end"]
        return out

    def fitting_would_adopt(run, k):            # the loop perturbs the FIRST result every time
        return False

    d0, d1 = draws(records[0]), draws(records[1])
    compared = 0
    for a, b in zip(d0, d1):
        for name in set(a) & set(b):
            assert a[name] == pytest.approx(b[name], rel=1e-12), name
            assert 0.85 <= a[name] <= 1.15
            compared += 1
    assert compared >= 20


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
    # nothing COSMETIC or merely spelt differently changes it (Codex round 1: renaming
    # "C-C" to "Graphite" moved a component's area fraction from 19 % to 5 %)
    cosmetic = [{**s, "name": "Graphite", "color": "#ff0000", "visible": False, "_rsf": 0.3} for s in specs]
    assert base == fitting._request_seed(x, y, cosmetic, **kw)
    assert base == fitting._request_seed(x, y, [{**s, "id": str(s["id"]), "constrain_to": None} for s in specs], **kw)
    assert base == fitting._request_seed(x, y, [{**s, "amplitude_min": -0.0} for s in specs], **kw)
    assert base == fitting._request_seed(x, y, specs, **{**kw, "fit_kws": {"method": "Least_Squares"}})
    anchors = [[280.0, 200.0], [287.0, 210.0], [294.9, 205.0]]
    manual = {**kw, "background_method": "manual"}
    assert (fitting._request_seed(x, y, specs, **{**manual, "manual_bg": anchors})
            == fitting._request_seed(x, y, specs, **{**manual, "manual_bg": anchors[::-1]}))
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


PINNED_SEED = 8582179  # xps-fit-seed-v1; recorded once from the implementation, never edited


def test_the_response_reports_its_seed():
    x, y, specs = _two_peaks()
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=3,
                          fit_kws={"method": "least_squares"})
    assert res["random_seed"] == fitting._request_seed(
        x, y, specs, background_method="linear", bg_start_idx=None, bg_end_idx=None, endpoint_avg=1,
        manual_bg=None, fit_kws={"method": "least_squares"}, n_perturb=3)


def test_a_caller_supplied_seed_wins_and_is_reported():
    x, y, specs = _two_peaks()
    kw = {"method": "differential_evolution", "fit_kws": {"seed": 4}}
    a = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1, fit_kws=kw)
    b = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1, fit_kws=kw)
    assert kw == {"method": "differential_evolution", "fit_kws": {"seed": 4}}     # the caller's dict is not mutated
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
    # Trust-Region: the seed is the same on every press; the result is not
    # asserted (module docstring).
    assert len({json.loads(b)["random_seed"] for b in bodies}) == 1


# ── Codex round 1 (both runs NO-GO) ─────────────────────────────────────────

def test_a_cosmetic_rename_does_not_change_the_fit():
    x, y, specs = _crowded_c1s()
    named = [{**s, "name": n} for s, n in zip(specs, ["C-C", "b", "c", "d", "e"])]
    renamed = [{**s, "name": n} for s, n in zip(specs, ["Graphite", "b", "c", "d", "e"])]
    a = fitting.run_fit(x, y, named, background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq"})
    b = fitting.run_fit(x, y, renamed, background_method="shirley", n_perturb=3, fit_kws={"method": "leastsq"})
    assert _dump(a) == _dump(b)


def test_the_seed_hashes_every_spec_key_the_fit_reads():
    import re
    from pathlib import Path
    src = Path(fitting.__file__).read_text()
    body = src[src.index("def _make_peak_params("):src.index("def _finite_search_box(")]
    read = set(re.findall(r'spec(?:\.get\(|\[)"([a-z_A-Z]+)"', body))
    assert read, "parser found nothing: the source moved"
    assert read <= set(fitting._SEED_SPEC_KEYS), sorted(read - set(fitting._SEED_SPEC_KEYS))


@pytest.mark.parametrize("method", ["ampgo", "dual_annealing", "shgo", "powell", "emcee"])
def test_methods_outside_the_supported_five_are_refused_centrally(method):
    # /api/analyze forwards options.fit_method straight to run_fit; lmfit knows
    # these and the stochastic ones would draw from numpy's global generator.
    x, y, specs = _two_peaks()
    with pytest.raises(ValueError, match="Unknown fit method"):
        fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": method})


def test_a_differently_cased_method_name_is_the_same_seeded_method(monkeypatch):
    records = _spy_on_fits(monkeypatch)
    records.append([])
    x, y, specs = _two_peaks()
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0, fit_kws={"method": "BasinHopping"})
    assert [r["method"] for r in records[0]] == ["basinhopping"]
    assert isinstance(records[0][0]["seed"], int)
    assert res["random_seed"] == fitting.run_fit(x, y, specs, background_method="linear", n_perturb=0,
                                                 fit_kws={"method": "basinhopping"})["random_seed"]


def test_the_analyze_wrapper_cannot_reach_an_unseeded_method():
    from autofit.methods.least_squares import LeastSquaresMethod
    x, y, specs = _two_peaks()
    with pytest.raises(ValueError, match="Unknown fit method"):
        LeastSquaresMethod().run(x, y, peak_specs=specs, options={"fit_method": "ampgo", "background_method": "linear"})


@pytest.mark.parametrize("method", ["leastsq", "least_squares", "nelder"])
def test_a_caller_seed_works_with_the_deterministic_methods(method):
    # it selects the draws and must not be forwarded to a solver that rejects it
    x, y, specs = _two_peaks()
    res = fitting.run_fit(x, y, specs, background_method="linear", n_perturb=2,
                          fit_kws={"method": method, "fit_kws": {"seed": 7}})
    assert res["success"] is True and res["random_seed"] == 7


@pytest.mark.parametrize("seed", [-1, True, 1.5, "4", 2 ** 32])
def test_an_unusable_caller_seed_is_a_validation_error_not_a_silent_fallback(seed):
    x, y, specs = _two_peaks()
    with pytest.raises(ValueError, match="seed must be an integer"):
        fitting.run_fit(x, y, specs, background_method="linear", n_perturb=1,
                        fit_kws={"method": "least_squares", "fit_kws": {"seed": seed}})


def test_the_perturbation_draws_are_pinned():
    # numpy does not promise the same stream from default_rng across versions.
    # If this fails after an upgrade, saved projects regenerate differently:
    # that is a release note, not a silent change.
    rng = np.random.default_rng(np.random.SeedSequence(705102460).spawn(2)[0])
    assert [round(float(v), 12) for v in rng.uniform(-0.15, 0.15, 3)] == PINNED_DRAWS


PINNED_DRAWS = [-0.090153485234, -0.101472558174, -0.146139265021]   # numpy 2.4.4
