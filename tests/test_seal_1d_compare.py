"""Seal 1d (docs/superpowers/plans/2026-10-15-seal-1d-rerun.md): "Re-run this fit" is judged by ONE comparator —
same_fit, the tests' own (tests/fit_equality.py re-exports it) — behind POST /api/compare-fits. The fit is compared
without its scattered starts (their own line, owner 2026-10-15), its software record (information; the numerics on
their own line, the 2026-10-15 rule) and its seed SOURCE (a re-run passes the recorded seed explicitly)."""
import copy

import pytest

import fit_equality
import fitting
import same_fit
import test_scattered_starts as SS
from test_seal_1a_verify import _seal, _upload, client  # noqa: F401


def _compare(client, a, b, status=200):  # noqa: F811
    r = client.post("/api/compare-fits", json={"a": a, "b": b})
    assert r.status_code == status, r.get_json()
    return r.get_json()


def _rerun(client, R, O):  # noqa: F811
    """What the page's re-run sends: the record's samples, its request, its own seed."""
    sid = _upload(client, R["energies"], R["counts"])
    r = client.post("/api/fit", json={**R["request"], "session_id": sid, "seed": O["random_seed"]})
    assert r.status_code == 200, r.get_json()
    return r.get_json()


def test_the_tests_comparator_is_the_app_module():
    assert fit_equality.assert_same_fit is same_fit.assert_same_fit
    assert fit_equality.fit_differences is same_fit.fit_differences
    assert (fit_equality.SAME_MINIMUM_REL, fit_equality.OBJECTIVE_REL) == (same_fit.SAME_MINIMUM_REL, same_fit.OBJECTIVE_REL)


@pytest.mark.parametrize("req", [
    {"fit_method": "leastsq", "n_perturb": 0},
    {"fit_method": "least_squares", "n_perturb": 3, "n_starts": 3},      # what Run Fit sends
])
def test_a_rerun_with_the_records_seed_is_the_same_fit_and_the_same_starts(client, req):  # noqa: F811
    x, y, specs = SS._well_posed()
    R, O = _seal(client, x, y, specs, background={"method": "shirley"}, **req)
    O2 = _rerun(client, R, O)
    assert O2["seed_source"] == "caller" and O2["random_seed"] == O["random_seed"]
    got = _compare(client, O, O2)
    assert got["same"] and got["problems"] == [] and got["starts"]["same"], got
    assert got["numerics"] == {"same": True, "differing": []} and got["software"] == fitting.SOFTWARE


def _record(client):  # noqa: F811
    x, y, specs = SS._well_posed()
    return _seal(client, x, y, specs, background={"method": "shirley"}, fit_method="least_squares", n_perturb=0, n_starts=3)[1]


def test_a_different_solution_is_named(client):  # noqa: F811
    a = _record(client)
    b = copy.deepcopy(a)
    ip = b["individual_peaks"][0]
    ip["params"]["center"]["value"] += 0.05 * ip["params"]["fwhm"]["value"]     # 50 x the same-minimum resolution
    got = _compare(client, a, b)
    assert not got["same"] and any("center" in p for p in got["problems"]), got
    assert got["starts"]["same"], got                                            # the starts are their own line


def test_the_scattered_starts_are_judged_on_their_own_line(client):  # noqa: F811
    a = _record(client)
    assert a["starts"] and a["starts"]["ran"], a["starts"]
    b = copy.deepcopy(a)
    b["starts"]["n_same_as_fit"] = (b["starts"]["n_same_as_fit"] + 1) % 4
    got = _compare(client, a, b)
    assert got["same"] and not got["starts"]["same"] and got["starts"]["problems"], got
    b = copy.deepcopy(a)
    b["starts"] = {"ran": False, "reason": "not requested"}                     # ran in one only
    got = _compare(client, a, b)
    assert got["same"] and not got["starts"]["same"], got


def test_software_is_information_and_numerics_their_own_line(client):  # noqa: F811
    a = _record(client)
    b = copy.deepcopy(a)
    b["seed_source"] = "caller"
    got = _compare(client, a, b)
    assert got["same"] and got["numerics"]["same"], got
    a2 = copy.deepcopy(a)
    a2["software"] = {**a2["software"], "git_commit": "0" * 40, "git_dirty": True, "env_sha256": "f" * 64}
    got = _compare(client, a2, b)
    assert got["same"] and got["numerics"]["same"], got                          # another commit: information only
    a3 = copy.deepcopy(a)
    a3["software"] = {**a3["software"], "numpy": "1.0.0"}
    got = _compare(client, a3, b)
    assert got["same"] and not got["numerics"]["same"] and any("numpy" in d for d in got["numerics"]["differing"]), got


@pytest.mark.parametrize("mutate", [
    lambda o: o.pop("energy"),
    lambda o: o.pop("statistics"),
    lambda o: o.__setitem__("fitted_y", o["fitted_y"][:-1]),
    lambda o: o.__setitem__("individual_peaks", "x"),
])
def test_a_side_that_is_not_a_fit_response_is_refused_never_compared(client, mutate):  # noqa: F811
    a = _record(client)
    for side in ("a", "b"):
        b = copy.deepcopy(a)
        mutate(b)
        pair = (b, a) if side == "a" else (a, b)
        got = _compare(client, *pair, status=400)
        assert side + " is not a fit response" in got["error"], got
    r = client.post("/api/compare-fits", json={"a": a})
    assert r.status_code == 400


# ── Codex 1d round 1 ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("mutate", [
    lambda o: o["energy"].__setitem__(0, 10 ** 400),
    lambda o: o["individual_peaks"][0]["params"]["center"].__setitem__("max", 10 ** 400),
])
def test_a_number_no_float_represents_is_refused_never_compared(client, mutate):  # noqa: F811
    a = _record(client)
    for side in ("a", "b"):
        b = copy.deepcopy(a)
        mutate(b)
        got = _compare(client, *((b, a) if side == "a" else (a, b)), status=400)
        assert got["error"] == side + " is not a fit response: it holds a number no float represents", got


def test_the_numerics_are_the_records_against_the_reruns_own(client):  # noqa: F811
    """Never against the worker answering the comparison: under a rolling deployment the re-run's worker may differ."""
    a = _record(client)
    b = copy.deepcopy(a)
    b["software"] = {**b["software"], "numpy": "9.9.9"}               # the re-run made elsewhere; the record matches here
    got = _compare(client, a, b)
    assert got["same"] and got["numerics"]["same"] is False, got
    assert got["numerics"]["differing"] == [f"numpy {a['software']['numpy']} (re-run 9.9.9)"], got
    got = _compare(client, b, b)                                       # both made under numerics this worker lacks
    assert got["numerics"] == {"same": True, "differing": []}, got


# ── Codex 1d rounds 2-3: hostile inputs are refused (4xx) on EITHER side, before any comparison ───────────────────
def _with_span(o, lo, hi):
    p = o["individual_peaks"][0]["params"]["fwhm"]
    p["min"], p["max"] = lo, hi


def _with_chain(o, n=1100):
    ip = o["individual_peaks"][0]
    tmpl = ip["params"]["center"]
    for i in range(n):                                                  # p<id>_l0 -> p<id>_l1 -> ... (bounds null)
        nxt = f"p{ip['id']}_l{i + 1}" if i < n - 1 else f"p{ip['id']}_center"   # each names one parameter that exists
        ip["params"][f"l{i}"] = {**tmpl, "min": None, "max": None, "vary": False, "expr": nxt}


def _with_signal(o):
    o["counts"][0], o["background_y"][0] = 1e308, -1e308                  # each finite; their difference is not


def _with_wide_grid(o):
    o["energy"][0], o["energy"][-1] = -1e306, 1e306                       # a finite span; x n points it is not


def _with_link(o, expr):
    ip = o["individual_peaks"][0]
    ip["params"]["extra"] = {**ip["params"]["center"], "min": None, "max": None, "vary": False, "expr": expr}


@pytest.mark.parametrize("hostile,words", [
    (_with_wide_grid, "energy span"),                                       # every half-maximum width is bounded by n x span
    (lambda o: _with_link(o, f"p{o['individual_peaks'][0]['id']}_center + p{o['individual_peaks'][0]['id']}_fwhm"), "not one a fit writes"),
    (lambda o: _with_link(o, "nothing_here * 2"), "not one a fit writes"),
    (lambda o: _with_span(o, -(10 ** 308), 10 ** 308), "bound span"),       # integers
    (lambda o: _with_span(o, -1e308, 1e308), "bound span"),                 # floats: their difference is inf, no exception
    (_with_chain, "chain of parameter links"),
    (_with_signal, "signal overflows"),
])
@pytest.mark.parametrize("side", ["a", "b", "both"])
def test_a_hostile_side_is_refused_before_any_comparison(client, hostile, words, side):  # noqa: F811
    a = _record(client)
    h = copy.deepcopy(a)
    hostile(h)
    pair = {"a": (h, a), "b": (a, h), "both": (h, copy.deepcopy(h))}[side]
    got = _compare(client, *pair, status=400)
    assert words in got["error"] and got["error"].startswith(("a is not a fit response", "b is not a fit response")), got
    if side == "b":
        b_value = copy.deepcopy(h)
        b_value["individual_peaks"][0]["params"]["fwhm"]["value"] = 1e307
        _compare(client, a, b_value, status=400)


def test_no_real_record_is_refused():
    """The 202 + 126 records of seal 1b's run v2, when present: every one passes the scale checks (open bounds are
    null, links one level deep)."""
    import json
    import os
    path = os.environ.get("SEAL_1B_RECORDS")
    if not path or not os.path.exists(path):
        pytest.skip("SEAL_1B_RECORDS not set (the verbatim records are not committed)")
    from app import create_app
    app = create_app()
    with app.test_client() as c:
        for line in open(path):
            O = json.loads(line)["O"]
            r = c.post("/api/compare-fits", json={"a": O, "b": O})
            assert r.status_code == 200 and r.get_json()["same"], r.get_json()


# ── Codex 1d round 5 ─────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("offset", [0.00001, -2.5e-7, 1e5, 10.9])
def test_a_link_with_an_exponent_the_page_can_send_is_compared_not_refused(client, offset):  # noqa: F811
    """A real fit's link: the page's linked offset 0.00001 is written `p1_center + 1e-05` — one parameter named."""
    x, y, specs = SS._well_posed()
    specs = [dict(s) for s in specs]
    specs[1].update(constrain_to=specs[0]["id"], splitting=offset, area_ratio=0.5, fix_fwhm=True)   # as peakToBackendSpec sends
    R, O = _seal(client, x, y, specs, background={"method": "shirley"})
    exprs = [v["expr"] for ip in O["individual_peaks"] for v in ip["params"].values() if isinstance(v, dict) and v.get("expr")]
    assert any(e.endswith(" + " + repr(float(offset))) for e in exprs), exprs   # the offset written as Python spells it
    got = _compare(client, O, copy.deepcopy(O))
    assert got["same"], (exprs, got)


def test_duplicate_component_ids_are_refused(client):  # noqa: F811
    a = _record(client)
    h = copy.deepcopy(a)
    dup = copy.deepcopy(h["individual_peaks"][0])
    h["individual_peaks"][0]["params"]["fwhm"]["expr"] = "nothing_here * 2"   # hidden behind the duplicate's own expr
    dup["params"]["fwhm"]["expr"] = f"p{dup['id']}_center"
    h["individual_peaks"].append(dup)
    for pair in ((h, a), (a, h), (h, copy.deepcopy(h))):
        got = _compare(client, *pair, status=400)
        assert "share an id" in got["error"], got


def _resized(o, m):
    """o with every per-sample array (and each component's curve) stretched to m samples on a unit grid."""
    n = len(o["energy"])
    out = copy.deepcopy(o)
    for k, v in o.items():
        if isinstance(v, list) and len(v) == n and all(isinstance(e, (int, float)) for e in v):
            out[k] = [v[i % n] for i in range(m)]
    out["energy"] = [i / m for i in range(m)]
    for ip in out["individual_peaks"]:
        ip["y"] = [ip["y"][i % n] for i in range(m)]
    return out


def test_b_curves_on_as_grid_are_bounded_by_the_longer_side(client):  # noqa: F811
    """Each side passes its own n x span bound; the comparison measures b's longer curves on a's wide grid."""
    a = _record(client)
    n = len(a["energy"])
    span = 1.7e308 / (2 * n)                                              # a: n x span = 8.5e307, finite
    a["energy"] = [i * span / (n - 1) for i in range(n)]
    b = _resized(a, 10 * n)                                               # b: its own grid is the unit interval
    assert _compare(client, a, a)["same"] is True                         # a alone is comparable
    got = _compare(client, a, b, status=400)                              # 10 n x a's span overflows
    assert "on a's grid" in got["error"], got
