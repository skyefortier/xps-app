"""POST /api/verify-fit (seal 1a′, V6.5 step 2, option (b)): the server recomputes a recorded
response O from its request R — never fits — and compares EXACTLY. A response it produced is
`consistent`; a change to anything it recomputes is a `mismatch` naming the check; a response
from other software is `unconfirmed`. Acceptance (success, certificate, starts, required, σ)
is the file's statement and is NOT recomputed: a forged `success` stays consistent — said, not
hidden (owner 2026-10-11: "converged" is shown as recorded, not proven)."""
import copy
import io
import json

import numpy as np
import pytest

import fitting
from app import create_app
import test_scattered_starts as SS
from test_seal_1a_server import SHAPES


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    app = create_app(upload_folder=str(tmp_path_factory.mktemp("up")))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _upload(client, x, y):
    csv = "\n".join(f"{float(a)!r},{float(b)!r}" for a, b in zip(x, y))
    r = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")})
    assert r.status_code == 200, r.get_json()
    return r.get_json()["session_id"]


def _seal(client, x, y, specs, **req):
    """(R, O) exactly as a page would hold them: the wire request, the uploaded arrays, the reply."""
    sid = _upload(client, x, y)
    body = {"session_id": sid, "peaks": specs, "background": {"method": "linear"}, "fit_method": "leastsq",
            "n_perturb": 0, **req}
    r = client.post("/api/fit", json=body)
    assert r.status_code == 200, r.get_json()
    return {"request": body, "energies": [float(v) for v in x], "counts": [float(v) for v in y]}, r.get_json()


def _verify(client, R, O):
    r = client.post("/api/verify-fit", json={"R": R, "O": O})
    assert r.status_code == 200, r.get_json()
    return r.get_json()


def _consistent(client, R, O):
    v = _verify(client, R, O)
    assert v["state"] == "consistent", v
    assert v["software"] == fitting.SOFTWARE


# ── a response the server produced is consistent ─────────────────────────────────────────────

@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_every_lineshape_verifies(client, shape):
    x, y, specs = SS._well_posed()
    specs = [{**s, "shape": shape, **SHAPES[shape]} for s in specs]
    _consistent(client, *_seal(client, x, y, specs, background={"method": "shirley"}))


@pytest.mark.parametrize("bg", [{"method": "shirley", "start_idx": 10, "end_idx": 120, "endpoint_avg": 3},
                                {"method": "smart"}, {"method": "smart_exp"}, {"method": "tougaard"},
                                {"method": "shirley_linear"}, {"method": "linear", "endpoint_avg": 5},
                                {"method": "none"}, {"method": "manual", "manual_bg": [[281.0, 210.0], [292.0, 190.0]]},
                                {"method": "manual"}])
def test_every_background_verifies(client, bg):
    x, y, specs = SS._well_posed()
    _consistent(client, *_seal(client, x, y, specs, background=bg))


@pytest.mark.parametrize("method", ["leastsq", "least_squares", "nelder"])
def test_the_local_methods_verify_with_restarts_starts_and_a_required_check(client, method):
    x, y, specs = SS._well_posed()
    _consistent(client, *_seal(client, x, y, specs, fit_method=method, n_perturb=3, n_starts=3, require_component=2))


@pytest.mark.parametrize("method", ["differential_evolution", "basinhopping"])
def test_the_global_methods_verify(client, method):
    x, y, specs = SS._well_posed()
    _consistent(client, *_seal(client, x, y, specs[:1], fit_method=method))


def test_links_held_values_and_a_callers_seed_verify(client):
    x, y, specs = SS._well_posed()
    specs[1] = {**specs[1], "constrain_to": 1, "splitting": 4.0, "area_ratio": 0.25, "fix_fwhm": True}
    specs[0] = {**specs[0], "fix_gl_ratio": True, "fwhm_min": 0.5, "fwhm_max": 3.0}
    R, O = _seal(client, x, y, specs, seed=12345, n_perturb=2)
    assert O["seed_source"] == "caller"
    _consistent(client, R, O)


def test_a_grandchild_listed_before_its_parent_verifies(client):
    x, y, specs = SS._well_posed()
    g = {**specs[1], "id": 3, "center": 291.0, "constrain_to": 2, "splitting": 2.0, "area_ratio": 0.5}
    child = {**specs[1], "constrain_to": 1, "splitting": 4.0, "area_ratio": 0.25}
    _consistent(client, *_seal(client, x, y, [g, specs[0], child]))


# ── what it does NOT recompute: acceptance is the file's (option (b)) ─────────────────────────

def test_acceptance_is_recorded_not_recomputed(client):
    x, y, specs = SS._well_posed()
    R, O = _seal(client, x, y, specs, fit_method="least_squares")
    forged = copy.deepcopy(O)
    forged["success"] = not O["success"]
    forged["message"] = "anything"
    forged["certificate"] = {"certified": True}
    forged["individual_peaks"][0]["params"]["center"]["stderr"] = 1e-9
    _consistent(client, R, forged)


# ── a change to anything it recomputes is a mismatch, named ──────────────────────────────────

def _set(path, value):
    def f(O):
        cur = O
        for k in path[:-1]:
            cur = cur[k]
        cur[path[-1]] = value(cur[path[-1]]) if callable(value) else value
    return f


def _bump(v):
    return np.nextafter(v, np.inf).item()


TAMPER = [
    ("energy", _set(["energy", 5], _bump), "data"),
    ("counts", _set(["counts", 5], _bump), "data"),
    ("fit_method", _set(["fit_method"], "least_squares"), "method"),
    ("charge_shift", _set(["charge_shift_applied"], 0.1), "shift"),
    ("seed", _set(["random_seed"], lambda s: (s + 1) % 2 ** 32), "seed"),
    ("seed_source", _set(["seed_source"], "caller"), "seed"),
    ("vary", _set(["individual_peaks", 0, "params", "fwhm", "vary"], False), "roles"),
    ("expr", _set(["individual_peaks", 0, "params", "fwhm", "expr"], "p2_fwhm"), "roles"),
    ("min", _set(["individual_peaks", 0, "params", "amplitude", "min"], 1.0), "roles"),
    ("held value", _set(["individual_peaks", 0, "params", "gl_ratio", "value"], 0.31), "held"),
    ("free value", _set(["individual_peaks", 0, "params", "center", "value"], _bump), "components"),
    ("background", _set(["background_y", 7], _bump), "background"),
    ("verdict", _set(["background_verdict", "method"], "smart"), "background"),
    ("curve", _set(["individual_peaks", 1, "y", 50], _bump), "components"),
    ("area", _set(["individual_peaks", 1, "params", "area", "value"], _bump), "components"),
    ("fitted_sub", _set(["fitted_sub", 50], _bump), "fitted_sub"),
    ("fitted_y", _set(["fitted_y", 50], _bump), "fitted_y"),
    ("residuals", _set(["residuals", 50], _bump), "residuals"),
    ("chi_square", _set(["statistics", "chi_square"], _bump), "statistics"),
    ("rmse", _set(["statistics", "rmse"], _bump), "statistics"),
    ("n_free", _set(["statistics", "n_free_params"], lambda n: n - 1), "statistics"),
    ("support", _set(["individual_peaks", 1, "support", "supported"], lambda s: not s), "support"),
    ("support f", _set(["individual_peaks", 1, "support", "delta_chi2"], _bump), "support"),
    ("shape", _set(["individual_peaks", 0, "shape"], "gaussian"), "schema"),
    ("id", _set(["individual_peaks", 0, "id"], 99), "schema"),
    ("short array", _set(["fitted_y"], lambda a: a[:-1]), "schema"),
    ("success type", _set(["success"], "yes"), "schema"),
    # JSON TYPES (Codex round 1): nothing is read through a coercion
    ("numeric strings", _set(["counts"], lambda a: [repr(v) for v in a]), "schema"),
    ("fitted_y strings", _set(["fitted_y"], lambda a: [repr(v) for v in a]), "schema"),
    ("shift as a flag", _set(["charge_shift_applied"], False), "schema"),
    ("supported as a number", _set(["individual_peaks", 1, "support", "supported"], lambda s: int(s)), "support"),
    ("area stderr text", _set(["individual_peaks", 1, "params", "area", "stderr"], "garbage"), "schema"),
    ("area stderr object", _set(["individual_peaks", 1, "params", "area", "stderr"], {"not": "a number"}), "schema"),
    ("stderr text", _set(["individual_peaks", 0, "params", "center", "stderr"], "0.1"), "schema"),
    ("vary as a number", _set(["individual_peaks", 0, "params", "center", "vary"], 1), "schema"),
    ("seed as a float", _set(["random_seed"], lambda s: float(s)), "schema"),
    ("verdict converged as a number", _set(["background_verdict", "converged"], 1), "background"),
    ("statistics n_data as a flag", _set(["statistics", "n_free_params"], True), "statistics"),
    # a free value outside its bounds, and a caller's seed that is not the caller's
    ("free value out of bounds", _set(["individual_peaks", 0, "params", "amplitude", "value"], -1.0), "roles"),
]


@pytest.fixture(scope="module")
def sealed(client):
    x, y, specs = SS._well_posed()
    specs[0] = {**specs[0], "fix_gl_ratio": True}
    return _seal(client, x, y, specs, background={"method": "shirley"})


@pytest.mark.parametrize("name,change,check", TAMPER, ids=[t[0] for t in TAMPER])
def test_a_changed_record_is_a_mismatch_naming_the_check(client, sealed, name, change, check):
    R, O = sealed
    _consistent(client, R, O)
    O2 = copy.deepcopy(O)
    change(O2)
    v = _verify(client, R, O2)
    assert v["state"] == "mismatch" and v["check"] == check, v


def test_an_extra_or_missing_field_is_a_mismatch(client, sealed):
    R, O = sealed
    for O2 in ({**O, "extra": 1}, {k: v for k, v in O.items() if k != "starts"}):
        v = _verify(client, R, O2)
        assert v["state"] == "mismatch" and v["check"] == "schema", v


def test_another_softwares_record_is_unconfirmed(client, sealed):
    R, O = sealed
    for change in ({"git_commit": "0" * 40}, {"numerics": "2026-10-09"}, {"env_sha256": "0" * 64}):
        O2 = {**O, "software": {**O["software"], **change}}
        v = _verify(client, R, O2)
        assert v["state"] == "unconfirmed" and v["check"] == "software", v


def test_a_record_paired_with_another_request_is_a_mismatch(client, sealed):
    R, O = sealed
    cases = [
        ({**R["request"], "background": {"method": "smart"}}, "background"),
        ({**R["request"], "peaks": [{**R["request"]["peaks"][0], "center": 284.7}, R["request"]["peaks"][1]]}, "seed"),
        ({**R["request"], "fit_method": "nelder"}, "method"),
        ({**R["request"], "n_perturb": 1}, "seed"),
        ({**R["request"], "fit_method": "ampgo"}, "request"),
        ({**R["request"], "peaks": []}, "request"),
    ]
    for req, check in cases:
        v = _verify(client, {**R, "request": req}, O)
        assert v["state"] == "mismatch" and v["check"] == check, (req, v)
    v = _verify(client, {**R, "counts": [c + 1 for c in R["counts"]]}, O)
    assert v["state"] == "mismatch" and v["check"] in ("data",), v


def test_a_malformed_body_is_a_400(client, sealed):
    R, O = sealed
    for body in ({}, {"R": R}, {"O": O}, {"R": {**R, "request": []}, "O": O},
                 {"R": {**R, "energies": R["energies"][:-1]}, "O": O},
                 {"R": {**R, "energies": ["a"] * len(R["energies"])}, "O": O}):
        assert client.post("/api/verify-fit", json=body).status_code == 400


def test_the_session_id_is_transport_only(client, sealed):
    R, O = sealed
    _consistent(client, {**R, "request": {**R["request"], "session_id": "expired-or-anything"}}, O)


def test_a_non_finite_number_is_unconfirmed_never_consistent(client, sealed):
    R, O = sealed
    for path in (["fitted_y", 3], ["individual_peaks", 0, "params", "center", "stderr"],
                 ["statistics", "rmse"], ["individual_peaks", 1, "support", "delta_chi2"]):
        for bad in (float("nan"), float("inf")):
            O2 = copy.deepcopy(O)
            _set(path, bad)(O2)
            v = _verify(client, R, O2)
            assert v["state"] == "unconfirmed" and v["check"] == "non_finite", (path, v)


def test_a_linked_value_that_is_not_its_expressions_is_a_mismatch(client):
    x, y, specs = SS._well_posed()
    specs[1] = {**specs[1], "constrain_to": 1, "splitting": 4.0, "area_ratio": 0.25}
    R, O = _seal(client, x, y, specs)
    _consistent(client, R, O)
    for name in ("center", "amplitude", "fwhm"):
        O2 = copy.deepcopy(O)
        _set(["individual_peaks", 1, "params", name, "value"], _bump)(O2)
        v = _verify(client, R, O2)
        assert v["state"] == "mismatch" and v["check"] == "expressions", (name, v)


def test_a_callers_seed_must_be_the_callers(client):
    x, y, specs = SS._well_posed()
    R, O = _seal(client, x, y, specs, seed=777)
    _consistent(client, R, O)
    for change in ({"random_seed": 778}, {"seed_source": "request"}):
        v = _verify(client, R, {**O, **change})
        assert v["state"] == "mismatch" and v["check"] == "seed", v


def test_overlapping_id_prefixes_each_own_only_their_parameters(client):
    # Codex round 1 BLOCKER: ids "1" and "1_x" give prefixes "p1_" and "p1_x_"; "p1_x_center" starts with
    # both, so component "1" echoed "x_center" too and a contradictory copy verified
    x, y, specs = SS._well_posed()
    specs = [{**specs[0], "id": "1", "shape": "gaussian"}, {**specs[1], "id": "1_x", "shape": "gaussian"}]
    R, O = _seal(client, x, y, specs)
    assert set(O["individual_peaks"][0]["params"]) == {"amplitude", "center", "fwhm", "area"}
    _consistent(client, R, O)
    O2 = copy.deepcopy(O)
    O2["individual_peaks"][0]["params"]["x_center"] = copy.deepcopy(O["individual_peaks"][1]["params"]["center"])
    assert _verify(client, R, O2)["check"] == "schema"
    O3 = copy.deepcopy(O)
    _set(["individual_peaks", 1, "params", "center", "value"], _bump)(O3)
    v = _verify(client, R, O3)
    assert v["state"] == "mismatch" and v["check"] == "components", v


def test_a_negative_zero_in_a_link_reads_as_zero(client):
    # Codex round 1: a splitting of -0.0 was written into the expression's text as "+ -0.0"; a JSON
    # writer spells -0 as 0, so the honest record re-sent read "mismatch / seed"
    x, y, specs = SS._well_posed()
    specs[1] = {**specs[1], "constrain_to": 1, "splitting": -0.0, "area_ratio": 0.25}
    R, O = _seal(client, x, y, specs)
    assert O["individual_peaks"][1]["params"]["center"]["expr"] == "p1_center + 0.0"
    _consistent(client, R, O)
    respelt = copy.deepcopy(R)
    respelt["request"]["peaks"][1]["splitting"] = 0
    _consistent(client, respelt, O)


def test_reversed_bounds_verify_as_the_fitter_holds_them(client):
    # Codex round 1: lmfit orders reversed bounds when Model.fit copies its start; the verifier compared
    # the uncopied ones and read an honest record "mismatch / roles"
    x, y, specs = SS._well_posed()
    specs[0] = {**specs[0], "center_min": 287.0, "center_max": 283.0, "fwhm_min": 3.0, "fwhm_max": 0.5}
    R, O = _seal(client, x, y, specs)
    assert O["individual_peaks"][0]["params"]["center"]["min"] == 283.0
    _consistent(client, R, O)


def test_a_lineshape_that_is_not_bit_stable_is_unconfirmed_not_mismatch(client):
    # owner Q7 / V6.5: LA(α,β,m)'s np.convolve is not bit-stable, so a curve-derived failure on a request
    # holding it cannot be told from arithmetic: UNCONFIRMED, never a tolerance, never a false STALE
    assert "la_casaxps" in fitting.NOT_BIT_STABLE_SHAPES
    x, y, specs = SS._well_posed()
    specs = [{**s, "shape": "la_casaxps", **SHAPES["la_casaxps"]} for s in specs]
    R, O = _seal(client, x, y, specs)
    _consistent(client, R, O)
    for path, check in ((["individual_peaks", 0, "y", 50], "components"), (["fitted_sub", 50], "fitted_sub"),
                        (["statistics", "chi_square"], "statistics")):
        O2 = copy.deepcopy(O)
        _set(path, _bump)(O2)
        v = _verify(client, R, O2)
        assert v["state"] == "unconfirmed" and v["check"] == check, (path, v)
    # what no evaluation decides stays a mismatch
    O2 = copy.deepcopy(O)
    _set(["random_seed"], lambda s: (s + 1) % 2 ** 32)(O2)
    assert _verify(client, R, O2)["state"] == "mismatch"


def test_an_undetermined_request_has_no_consistent_record(monkeypatch):
    # run_fit refuses n_free >= n_data; a record for such a request is not a response (built here by
    # switching the shared rule off for the fit only)
    x = np.array([280.0, 280.1, 280.2, 280.3, 280.4, 280.5])        # 6 points, 6 free parameters
    y = np.array([10.0, 30.0, 50.0, 30.0, 12.0, 9.0])
    specs = [{"id": 1, "shape": "gaussian", "center": 280.2, "amplitude": 40.0, "fwhm": 0.3},
             {"id": 2, "shape": "gaussian", "center": 280.3, "amplitude": 10.0, "fwhm": 0.3}]
    args = dict(energy=x, counts=y, peak_specs=specs, background_method="none", n_perturb=0,
                fit_kws={"method": "leastsq"})
    monkeypatch.setattr(fitting, "_determined", lambda n_free, n_data: True)
    O = json.loads(json.dumps(fitting.run_fit(**args)))
    assert fitting.verify_fit(O, **args)["state"] == "consistent"
    monkeypatch.undo()
    v = fitting.verify_fit(O, **args)
    assert v["state"] == "mismatch" and v["check"] == "determinacy", v
