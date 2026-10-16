"""Seal 1d (docs/superpowers/plans/2026-10-15-seal-1d-rerun.md): "Re-run this fit" is judged by ONE comparator —
same_fit, the tests' own (tests/fit_equality.py re-exports it) — behind POST /api/compare-fits. The fit is compared
without its scattered starts (their own line, owner 2026-10-15), its software record (information; the numerics on
their own line, the 2026-10-15 rule) and its seed SOURCE (a re-run passes the recorded seed explicitly)."""
import copy
import json

import pytest

import fit_equality
import fitting
import same_fit
import test_scattered_starts as SS
from test_seal_1a_server import SHAPES
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
        assert got["error"].startswith(side + " is not a fit response: it holds a number no float represents"), got


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


# ── Option 3 (owner 2026-10-15): each side's EXACT structure as a fit writes it, before anything is compared ────────
# (fitting.response_structure_failure). The hostile inputs of Codex rounds 1-9, each on side a, side b and both.
def _peak(o, k=0):
    return o["individual_peaks"][k]


def _with_span(o, lo, hi):
    p = _peak(o)["params"]["fwhm"]
    p["min"], p["max"] = lo, hi


def _linked_as_written(c, m, off="0.5", ratio="0.5", others=True, root=None):
    """Component c linked to m exactly as a fit writes it (_make_peak_params; support follows the root)."""
    for name, rec in c["params"].items():
        if name == "area":
            continue
        expr = {"center": f"p{m['id']}_center + {off}", "amplitude": f"p{m['id']}_amplitude * {ratio}"}.get(
            name, f"p{m['id']}_{name}" if others else None)
        c["params"][name] = {**rec, "vary": False, "expr": expr, "min": None, "max": None} if expr else rec
    root = root or m
    c["support"] = {**c["support"], "follows": root["id"], "supported": root["support"]["supported"]}
    return c


def _proper_link(o, **kw):
    m, c = _peak(o, 0), _peak(o, 1)
    c["shape"] = m["shape"]
    _linked_as_written(c, m, **kw)
    return o


def _unlinked(o, *names):
    for name in names:
        _peak(o, 1)["params"][name].update(vary=True, expr=None)
    return o


def _with_chain(o, n=1100):
    base = _peak(o)
    for i in range(n):                                                    # links through n more components
        c = copy.deepcopy(base)
        c["id"] = f"k{i}"
        o["individual_peaks"].append(c)
        if o["starts"] and o["starts"].get("ran"):                         # the starts list every component, in order
            o["starts"]["fit"]["components"].append({**o["starts"]["fit"]["components"][0], "id": c["id"]})
    for i in range(n):
        nxt = o["individual_peaks"][-n + i + 1] if i < n - 1 else base
        _linked_as_written(o["individual_peaks"][-n + i], nxt, off="0.0", ratio="1.0", root=base)


def _with_link(o, expr):
    ip = _peak(o, 1)
    ip["params"]["center"] = {**ip["params"]["center"], "vary": False, "expr": expr.replace("p1_", f"p{_peak(o)['id']}_")}


def _dup_alt_id(o):
    alt = o["starts"]["alternatives"][0]
    alt["components"][1]["id"] = alt["components"][0]["id"]


def _alt_param(o, **extra):
    o["starts"]["alternatives"][0]["components"][0]["params"].update(extra)


def _with_alternative(o):
    st, ips = o["starts"], o["individual_peaks"]
    st["alternatives"] = [{"chi2r": st["fit"]["chi2r"] * 0.9, "n_starts": 1,
                           "largest_centre_shift_from_start": st["fit"]["largest_centre_shift_from_start"],
                           "largest_fraction_difference_pp": 1.0,
                           "components": [{**c, "area": ip["params"]["area"]["value"],
                                           "params": {k: v["value"] for k, v in ip["params"].items() if k != "area"}}
                                          for c in st["fit"]["components"] for ip in ips if ip["id"] == c["id"]]}]
    st["n_in_alternatives"] = 1
    return o


def _gaussian_master_gl_child(o):
    """Codex round 10: component 0 a Gaussian (no gl_ratio), component 1 a GL whose gl_ratio links to p<0>_gl_ratio."""
    m, c = _peak(o, 0), _peak(o, 1)
    m["shape"] = "gaussian"
    m["params"].pop("gl_ratio", None)
    c["shape"] = "pseudo_voigt_gl"
    c["params"]["gl_ratio"] = {**c["params"]["gl_ratio"], "vary": False, "expr": f"p{m['id']}_gl_ratio"}


HOSTILE = {
    "huge integer energy": lambda o: o["energy"].__setitem__(0, 10 ** 400),
    "huge integer bound": lambda o: _peak(o)["params"]["center"].__setitem__("max", 10 ** 400),
    "integer bound span overflows": lambda o: _with_span(o, -(10 ** 308), 10 ** 308),
    "float bound span overflows": lambda o: _with_span(o, -1e308, 1e308),
    "energy span x samples overflows": lambda o: (o["energy"].__setitem__(0, -1e306), o["energy"].__setitem__(-1, 1e306)),
    "signal overflows": lambda o: (o["counts"].__setitem__(0, 1e308), o["background_y"].__setitem__(0, -1e308)),
    "link chain too deep": _with_chain,
    "link to two parameters": lambda o: _with_link(o, "p1_center + p1_fwhm"),
    "link naming nothing": lambda o: _with_link(o, "nothing_here * 2"),
    "link with a quoted name": lambda o: _with_link(o, "'p1_l1' and p1_center"),
    "link with a comment": lambda o: _with_link(o, "p1_center + 0.5  # p1_fwhm"),
    "link with a call": lambda o: _with_link(o, "abs(p1_center)"),
    "link subtracting": lambda o: _with_link(o, "p1_center - 0.5"),
    "link to itself": lambda o: _peak(o)["params"]["fwhm"].update(vary=False, expr=f"p{_peak(o)['id']}_fwhm"),
    "link to another parameter": lambda o: _with_link(o, "p1_fwhm"),
    "varying linked parameter": lambda o: _peak(o, 1)["params"]["fwhm"].update(vary=True, expr=f"p{_peak(o)['id']}_fwhm"),
    "duplicate component ids": lambda o: o["individual_peaks"].append(copy.deepcopy(_peak(o))),
    "id not a fit's": lambda o: _peak(o).__setitem__("id", "1 x"),
    "parameter named value/min/expr": lambda o: _peak(o)["params"].update(value={**_peak(o)["params"]["center"], "expr": None}),
    "parameter missing": lambda o: _peak(o)["params"].pop("fwhm"),
    "unknown lineshape": lambda o: _peak(o).__setitem__("shape", "voigt_true"),
    "duplicate ids in an alternative": lambda o: _dup_alt_id(_with_alternative(o)),
    "alternative carrying value/min/expr": lambda o: _alt_param(_with_alternative(o), value=1.0, min=0.0, expr=1.0),
    "alternative out of order": lambda o: _with_alternative(o)["starts"]["alternatives"][0]["components"].reverse(),
    # Codex round 10
    "link to a parameter its master lacks": lambda o: _gaussian_master_gl_child(o),
    "link number 01": lambda o: _with_link(o, "p1_center + 01"),
    "link number 00.5": lambda o: _with_link(o, "p1_center + 00.5"),
    "link number 1e+999": lambda o: _with_link(o, "p1_center + 1e+999"),
    "link number inf": lambda o: _with_link(o, "p1_center + inf"),
    "no components": lambda o: (o.__setitem__("individual_peaks", []), o.__setitem__("starts", None)),
    "integer a float cannot hold": lambda o: o["counts"].__setitem__(0, 9007199254740993),
    "software field no server records": lambda o: o["software"].__setitem__("zz", "x"),
    # Codex round 11: links and support exactly as a fit writes them
    # each with the support a linked component carries, so the LINK rule alone refuses it
    "fwhm linked alone": lambda o: _unlinked(_proper_link(o), "center", "amplitude"),
    "fwhm linked alone, support unlinked": lambda o: _unlinked(_proper_link(o), "center", "amplitude")[
        "individual_peaks"][1]["support"].pop("follows"),                 # round 11's case exactly
    "centre linked alone": lambda o: _unlinked(_proper_link(o, others=False), "amplitude"),
    "amplitude linked alone": lambda o: _unlinked(_proper_link(o, others=False), "center"),
    "link offset -0.0": lambda o: _proper_link(o, off="-0.0"),
    "link ratio -0.0": lambda o: _proper_link(o, ratio="-0.0"),
    "some shape parameters linked": lambda o: (_proper_link(o, others=False),
                                               _peak(o, 1)["params"]["fwhm"].update(vary=False, expr=f"p{_peak(o)['id']}_fwhm",
                                                                                     min=None, max=None)),
    "shape parameter linked to itself": lambda o: (_proper_link(o), _peak(o, 1)["params"]["fwhm"].update(
        expr="p" + str(_peak(o, 1)["id"]) + "_fwhm")),
    "linked component following nothing": lambda o: _proper_link(o)["individual_peaks"][1]["support"].pop("follows"),
    "linked component following another": lambda o: _proper_link(o)["individual_peaks"][1]["support"].update(follows="zz"),
    "linked component's own verdict": lambda o: _proper_link(o)["individual_peaks"][1]["support"].update(
        supported=not _peak(o, 0)["support"]["supported"]),
    "unlinked component following another": lambda o: _peak(o, 1)["support"].update(follows=_peak(o, 0)["id"]),
    # Codex round 12
    "linked parameter with bounds": lambda o: _proper_link(o)["individual_peaks"][1]["params"]["center"].update(
        min=280.0, max=300.0),
    "linked amplitude with a floor": lambda o: _proper_link(o)["individual_peaks"][1]["params"]["amplitude"].update(min=0.0),
    "link to a null-id master": lambda o: (_peak(o, 0).__setitem__("id", None),
                                           o["starts"]["fit"]["components"][0].__setitem__("id", None),
                                           _proper_link(o)),
    # Codex round 13
    "linked component's own width held": lambda o: _proper_link(o, others=False)["individual_peaks"][1]["params"][
        "fwhm"].update(vary=False),
    "link to a component of another lineshape": lambda o: (_proper_link(o), _peak(o, 0).__setitem__("shape", "gaussian"),
                                                         _peak(o, 0)["params"].pop("gl_ratio", None)),
}


_LINKS = [(0.5, 0.5, True), (0.5, 0.5, False), (-0.5, 2.0, True), (1e-05, 1.0, True), (-0.0, 0.5, True)]


def _linked_fit(client, splitting, ratio, fix_fwhm, master_ref=None, record=False, **req):  # noqa: F811
    x, y, specs = SS._well_posed()
    specs = [dict(s) for s in specs]
    specs[1].update(constrain_to=specs[0]["id"] if master_ref is None else master_ref, splitting=splitting,
                    area_ratio=ratio, fix_fwhm=fix_fwhm)
    R, O = _seal(client, x, y, specs, background={"method": "shirley"}, fit_method="least_squares", n_perturb=0,
                 **{"n_starts": 3, **req})
    return (R, O) if record else O


@pytest.mark.parametrize("splitting,ratio,fix_fwhm", _LINKS)
def test_a_link_as_a_fit_writes_it_is_compared(client, splitting, ratio, fix_fwhm):  # noqa: F811
    """Positive controls written by run_fit itself (Codex round 12), and the hostile cases' helper writes the same
    link structure — every expression, flag and bound of the linked component — so their refusal is the rule's."""
    o = _linked_fit(client, splitting, ratio, fix_fwhm)
    assert fitting.response_structure_failure(o) is None, fitting.response_structure_failure(o)
    assert _compare(client, o, copy.deepcopy(o))["same"]
    h = _proper_link(_record(client), off=str(float(splitting) + 0.0), ratio=str(float(ratio)), others=fix_fwhm)
    meta = lambda c: {k: (v["expr"], v["vary"], v["min"], v["max"]) for k, v in c["params"].items() if k != "area"}
    assert meta(h["individual_peaks"][1]) == meta(o["individual_peaks"][1])
    assert h["individual_peaks"][1]["support"].keys() == o["individual_peaks"][1]["support"].keys()


@pytest.mark.parametrize("ref", [1.0, True])
def test_a_master_named_by_an_equal_id_is_followed(client, ref):  # noqa: F811
    """Codex round 12: constrain_to 1.0 (or true) for the peak with id 1 links to it AND its support follows it — the
    server reads the reference one way for both (it compared string spellings for the support, "1.0" != "1")."""
    R, o = _linked_fit(client, 0.5, 0.5, True, master_ref=ref, record=True)
    assert o["individual_peaks"][0]["id"] == 1 and o["individual_peaks"][1]["support"]["follows"] == 1
    assert o["individual_peaks"][1]["support"]["supported"] == o["individual_peaks"][0]["support"]["supported"]
    assert fitting.response_structure_failure(o) is None, fitting.response_structure_failure(o)
    assert _compare(client, o, copy.deepcopy(o))["same"]
    v = client.post("/api/verify-fit", json={"R": R, "O": o}).get_json()      # the verifier walks the links the same way
    assert v["state"] == "consistent", v


@pytest.mark.parametrize("ref", [1.0, True])
def test_the_required_refit_removes_a_child_named_by_an_equal_id(client, ref):  # noqa: F811
    """Removing component 1 removes what is linked to it, found the same way: the child named by 1.0 / true goes too
    (with the string spelling it stayed, its expression naming a removed parameter)."""
    R, o = _linked_fit(client, 0.5, 0.5, True, master_ref=ref, record=True, n_starts=0, require_component=1)
    assert o["required"] == {"ran": False, "reason": "nothing_left"}, o["required"]     # both went: nothing is left
    assert fitting.response_structure_failure(o) is None, fitting.response_structure_failure(o)


def test_a_chain_within_the_depth_is_compared(client):  # noqa: F811
    o = _record(client)
    _with_chain(o, n=20)
    assert fitting.response_structure_failure(o) is None, fitting.response_structure_failure(o)


@pytest.mark.parametrize("name", sorted(HOSTILE))
@pytest.mark.parametrize("side", ["a", "b", "both"])
def test_a_side_not_of_a_fits_exact_structure_is_refused(client, name, side):  # noqa: F811
    a = _record(client)
    h = copy.deepcopy(a)
    HOSTILE[name](h)
    pair = {"a": (h, a), "b": (a, h), "both": (h, copy.deepcopy(h))}[side]
    r = client.post("/api/compare-fits", json={"a": pair[0], "b": pair[1]})
    assert r.status_code == 400, (name, side, r.status_code, r.get_json())
    assert r.get_json()["error"].startswith((side if side != "both" else "a") + " is not a fit response: "), r.get_json()


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
    """Each side passes alone; the comparison measures b's longer curves on a's wide grid."""
    a = _record(client)
    n = len(a["energy"])
    span = 1.7e308 / (2 * n)
    a["energy"] = [i * span / (n - 1) for i in range(n)]
    b = _resized(a, 10 * n)
    assert _compare(client, a, a)["same"] is True
    got = _compare(client, a, b, status=400)
    assert "on a's grid" in got["error"], got


def test_no_real_record_is_refused():
    """The 202 + 126 records of seal 1b's run v2, when present: every one has the exact structure, and compares `same`."""
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
            assert fitting.response_structure_failure(O) is None
            r = c.post("/api/compare-fits", json={"a": O, "b": O})
            assert r.status_code == 200 and r.get_json()["same"], r.get_json()


# real fits of every lineshape and link form the page can send: never refused
SHAPE_CASES = [(shape, link, lock) for shape in sorted(SHAPES) for link in (False, True) for lock in (False, True)]


@pytest.mark.parametrize("shape,link,lock", SHAPE_CASES)
def test_every_lineshape_link_and_lock_a_fit_writes_is_compared(client, shape, link, lock):  # noqa: F811
    x, y, specs = SS._well_posed()
    specs = [{**s, "shape": shape, **SHAPES[shape]} for s in specs]
    if lock:
        specs[0].update(fix_fwhm=True, fix_center=True)
    if link:
        specs[1].update(constrain_to=specs[0]["id"], splitting=1e-05, area_ratio=0.5, fix_fwhm=True)
    R, O = _seal(client, x, y, specs, background={"method": "shirley"}, fit_method="least_squares", n_perturb=0, n_starts=3)
    assert fitting.response_structure_failure(O) is None, (shape, link, lock, fitting.response_structure_failure(O))
    got = _compare(client, O, copy.deepcopy(O))
    assert got["same"] and got["starts"]["same"], got


@pytest.mark.parametrize("offset", [0.00001, -2.5e-7, 1e5, 10.9, -0.5, 0.0])
def test_a_link_offset_the_page_can_send_is_compared(client, offset):  # noqa: F811
    x, y, specs = SS._well_posed()
    specs = [dict(s) for s in specs]
    specs[1].update(constrain_to=specs[0]["id"], splitting=offset, area_ratio=0.5, fix_fwhm=True)
    R, O = _seal(client, x, y, specs, background={"method": "shirley"})
    exprs = [v["expr"] for ip in O["individual_peaks"] for v in ip["params"].values() if isinstance(v, dict) and v.get("expr")]
    assert any(e.endswith(" + " + repr(float(offset))) for e in exprs), exprs
    assert _compare(client, O, copy.deepcopy(O))["same"]


def test_random_mutations_never_answer_500(client):  # noqa: F811
    """A seeded fuzz over a real response with an alternative: 3,000 random structural and numeric mutations, on a
    random side — every answer is 200 or 400, never 500. (It does not establish WHICH is right for a value change;
    the key-level oracle below does, for deletions and additions.)"""
    import random
    rng = random.Random(20261015)
    base = _with_alternative(_proper_link(_record(client)))
    assert "follows" in base["individual_peaks"][1]["support"]
    values = [None, True, False, 0, -1, 1.5, 1e308, -1e308, 10 ** 400, "", "x", "p1_center", [], [1], {}, {"value": 1},
              float("inf"), float("nan")]

    def paths(o, at=()):
        yield at
        if isinstance(o, dict):
            for k, v in o.items():
                yield from paths(v, at + (k,))
        elif isinstance(o, list):
            for i, v in enumerate(o[:3]):
                yield from paths(v, at + (i,))
    every = [p for p in paths(base) if p]
    counts = {200: 0, 400: 0}
    for _ in range(3000):
        h = copy.deepcopy(base)
        for _k in range(rng.randint(1, 3)):
            at = rng.choice(every)
            parent = h
            try:
                for step in at[:-1]:
                    parent = parent[step]
                if isinstance(parent, dict) and rng.random() < 0.2:
                    parent.pop(at[-1], None)
                elif isinstance(parent, dict) and rng.random() < 0.1:
                    parent[rng.choice(["value", "min", "expr", "zz"])] = rng.choice(values)
                else:
                    parent[at[-1]] = rng.choice(values)
            except (KeyError, IndexError, TypeError):
                pass
        pair = (h, base) if rng.random() < 0.5 else (base, h)
        r = client.post("/api/compare-fits", data=json.dumps({"a": pair[0], "b": pair[1]}), content_type="application/json")
        assert r.status_code in (200, 400), (r.status_code, r.get_data(as_text=True)[:300])
        counts[r.status_code] += 1
    assert counts[400] > 0 and counts[200] > 0, counts


def _optional(at, key):
    """A key a response MAY omit, by its object's PATH (Codex round 11: never by key name alone): the software fields
    recorded since 2026-10-15. (A linked component's support.follows is REQUIRED; the base below holds one.)"""
    return at == ("software",) and key in fitting._NUMERICS_KEYS_SINCE_2026_10_15


def _dict_paths(o, at=()):
    if isinstance(o, dict):
        yield at
        for k, v in o.items():
            yield from _dict_paths(v, at + (k,))
    elif isinstance(o, list):
        for i, v in enumerate(o[:3]):
            yield from _dict_paths(v, at + (i,))


def test_every_deleted_or_added_key_is_refused(client):  # noqa: F811
    """An ORACLE the random fuzz lacks: a fit response has exactly its keys, so deleting a key it must have, or adding
    any key, anywhere — every object of a real response with an alternative, on either side — is refused."""
    base = _with_alternative(_proper_link(_record(client)))
    assert "follows" in base["individual_peaks"][1]["support"]
    checked = 0
    for at in _dict_paths(base):
        node = base
        for step in at:
            node = node[step]
        for key in list(node) + ["zz_added"]:
            if _optional(at, key):
                continue
            h = copy.deepcopy(base)
            target = h
            for step in at:
                target = target[step]
            if key == "zz_added":
                target[key] = 1.0
            else:
                del target[key]
            for pair in ((h, base), (base, h)):
                r = client.post("/api/compare-fits", data=json.dumps({"a": pair[0], "b": pair[1]}), content_type="application/json")
                assert r.status_code == 400, (at, key, r.status_code, r.get_json())
            checked += 1
    assert checked > 100, checked


# real fits the server writes: every id it accepts, more methods and backgrounds, a required-component check
@pytest.mark.parametrize("ids", [("", "2"), ("é", "b"), (None, "2"), (True, False), ("1", "1_x"),
                                 (9007199254740993, "2"), (10 ** 400, "2")])
def test_any_id_the_server_accepts_is_compared(client, ids):  # noqa: F811
    x, y, specs = SS._well_posed()
    specs = [{**s, "id": i} for s, i in zip(specs, ids)]
    specs[1].update(constrain_to=ids[0], splitting=0.5, area_ratio=0.5, fix_fwhm=True)
    R, O = _seal(client, x, y, specs, background={"method": "shirley"}, fit_method="least_squares", n_perturb=0, n_starts=3)
    assert fitting.response_structure_failure(O) is None, (ids, fitting.response_structure_failure(O))
    assert _compare(client, O, copy.deepcopy(O))["same"]


@pytest.mark.parametrize("method,bg", [
    ("leastsq", {"method": "smart"}), ("nelder", {"method": "linear"}), ("least_squares", {"method": "none"}),
    ("least_squares", {"method": "tougaard"}), ("least_squares", {"method": "smart_exp"}),
    ("least_squares", {"method": "manual", "manual_bg": [[281.0, 210.0], [292.0, 190.0]]}),
    ("differential_evolution", {"method": "shirley"}), ("basinhopping", {"method": "shirley"}),
])
def test_every_method_and_background_a_fit_writes_is_compared(client, method, bg):  # noqa: F811
    x, y, specs = SS._well_posed()
    R, O = _seal(client, x, y, specs, background=bg, fit_method=method, n_perturb=0, n_starts=3)
    assert fitting.response_structure_failure(O) is None, (method, bg, fitting.response_structure_failure(O))
    assert _compare(client, O, copy.deepcopy(O))["same"]


def test_a_required_component_check_is_compared(client):  # noqa: F811
    x, y, specs = SS._well_posed()
    R, O = _seal(client, x, y, specs, background={"method": "shirley"}, fit_method="least_squares", n_perturb=0,
                 require_component=specs[0]["id"])
    assert O["required"] and O["required"]["ran"], O["required"]
    assert fitting.response_structure_failure(O) is None, fitting.response_structure_failure(O)
    assert _compare(client, O, copy.deepcopy(O))["same"]


def test_ids_equal_as_values_are_refused_as_one_id():
    """Codex rounds 12-13: a link names its master by equality, so two ids equal as values (1, 1.0, true) cannot be
    told apart — /api/fit refused them as duplicates already; run_fit's graph check now does too (it compared
    spellings only, so the walks and the parameter builder could pick different masters by order)."""
    for pair in ((True, 1), (1, 1.0), (0, False)):
        with pytest.raises(ValueError, match="share the id"):
            fitting._validate_constraint_graph([{"id": pair[0], "shape": "gaussian"}, {"id": pair[1], "shape": "gaussian"}])
    x, y, specs = SS._well_posed()          # round 13's reproducer, through run_fit itself
    g = {k: v for k, v in specs[0].items() if k != "id"}
    specs = [{**g, "id": True, "constrain_to": "r", "splitting": 0.5}, {**g, "id": 1}, {**g, "id": "r", "center": 287.0},
             {**g, "id": "c", "constrain_to": 1, "splitting": 0.5}]
    with pytest.raises(ValueError, match="share the id"):
        fitting.run_fit(energy=x, counts=y, peak_specs=specs, background_method="shirley", n_perturb=0)
    assert fitting._link_masters([{"id": 1}, {"id": "c", "constrain_to": 1.0}]) == {"1": None, "c": "1"}


@pytest.mark.parametrize("master", ["e", "é"])
def test_a_linked_parameter_is_judged_on_its_masters_bounds_whatever_the_id(client, master):  # noqa: F811
    """Codex round 13: the comparator found a linked parameter's bounds through an ASCII-only pattern, so a master
    "é" lost them and the same perturbation compared differently. Both spellings must judge it alike: a child width
    moved by 0.005 eV is within rounding on its master's bounds' scale (0.1-15 eV) for both."""
    x, y, specs = SS._well_posed()
    specs = [{**specs[0], "id": master}, {**specs[1], "id": "b", "constrain_to": master, "splitting": 0.5,
                                          "area_ratio": 0.5, "fix_fwhm": True}]
    o = _seal(client, x, y, specs, background={"method": "shirley"}, fit_method="least_squares", n_perturb=0)[1]
    h = copy.deepcopy(o)
    h["individual_peaks"][1]["params"]["fwhm"]["value"] += 0.005
    assert same_fit.fit_differences(o, h) == []
