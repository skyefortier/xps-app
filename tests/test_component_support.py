"""Per-component "support" in the /api/fit response (unit step (b), 2026-09-22).

Owner decision 2026-09-18: a component whose amplitude the fit drove to its
floor is an explicit outcome — NOT SUPPORTED BY THE DATA — and its centre,
width and sigma are not reported. The statistic is the one shipped for the
Auto-Fit anchor (with/without-component F, no intensity floor); the server
computes it once per component so every consumer reads one field.
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


def _g(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _spectrum():
    rng = np.random.default_rng(3)
    x = np.arange(280.0, 295.0, 0.1)
    y = rng.poisson(200.0 + _g(x, 284.8, 4000.0, 1.1) + _g(x, 288.6, 900.0, 1.4)).astype(float)
    return x, y


def _specs(extra=None):
    s = [{"id": 1, "name": "A", "shape": "pseudo_voigt_gl", "center": 284.6, "amplitude": 3500.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0},
         {"id": 2, "name": "B", "shape": "pseudo_voigt_gl", "center": 288.9, "amplitude": 700.0, "fwhm": 1.2, "gl_ratio": 0.3, "amplitude_min": 0}]
    return s + (extra or [])


KW = dict(background_method="linear", n_perturb=0, fit_kws={"method": "least_squares"})


def test_every_component_carries_a_support_verdict():
    x, y = _spectrum()
    res = fitting.run_fit(x, y, _specs(), **KW)
    for ip in res["individual_peaks"]:
        sup = ip["support"]
        assert set(sup) >= {"f", "delta_chi2", "supported"}
        assert sup["supported"] is True and sup["f"] > 1000


def test_a_component_with_nothing_to_fit_is_unsupported_and_still_returned_in_full():
    # a third component where the data hold nothing: the fit drives it to its floor
    x, y = _spectrum()
    ghost = {"id": 3, "name": "ghost", "shape": "gaussian", "center": 292.5, "center_min": 291.5, "center_max": 293.5,
             "amplitude": 300.0, "amplitude_min": 0, "fwhm": 1.0}
    res = fitting.run_fit(x, y, _specs([ghost]), **KW)
    assert res["success"] is True
    by = {str(ip["id"]): ip for ip in res["individual_peaks"]}
    assert by["3"]["support"]["supported"] is False
    assert by["3"]["support"]["delta_chi2"] <= 0 or by["3"]["support"]["f"] < fitting.SUPPORT_MIN_F
    assert by["1"]["support"]["supported"] and by["2"]["support"]["supported"]
    # the parameters are still there for anyone who wants them; the PAGE decides what to show
    assert "center" in by["3"]["params"] and "area" in by["3"]["params"]


def test_the_statistic_matches_the_auto_fit_anchor_definition():
    y_sub = np.array([1.0, 2.0, 3.0, 2.0, 1.0])
    fitted = np.array([1.0, 2.0, 2.5, 2.0, 1.0])
    comp = np.array([0.0, 0.0, 2.5, 0.0, 0.0])
    w = np.ones(5)
    sup = fitting._component_support(y_sub, fitted, comp, w, n_free_comp=3, n_free_total=3)
    chi_with = 0.25
    chi_without = (3.0 - 2.5 + 2.5) ** 2      # residual + component at the one differing point
    f = ((chi_without - chi_with) / 3) / (chi_with / (5 - 3))
    assert sup["f"] == pytest.approx(f) and sup["delta_chi2"] == pytest.approx(chi_without - chi_with)
    assert sup["supported"] is (f >= fitting.SUPPORT_MIN_F)
    # removing a component that costs nothing
    zero = fitting._component_support(y_sub, fitted, np.zeros(5), w, 3, 3)
    assert zero["supported"] is False and zero["f"] == 0.0
    # an exact fit that needs the component
    exact = fitting._component_support(y_sub, y_sub, comp, w, 3, 3)
    assert exact["supported"] is True and exact["f"] is None       # infinite, serialised as null


def test_a_linked_component_follows_its_parent():
    x, y = _spectrum()
    specs = _specs() + [{"id": 3, "shape": "pseudo_voigt_gl", "center": 288.0, "amplitude": 100.0, "fwhm": 1.2,
                         "gl_ratio": 0.3, "amplitude_min": 0, "constrain_to": 2, "splitting": -0.9, "area_ratio": 0.001}]
    res = fitting.run_fit(x, y, specs, **KW)
    by = {str(ip["id"]): ip for ip in res["individual_peaks"]}
    assert by["3"]["support"]["follows"] == 2
    assert by["3"]["support"]["supported"] == by["2"]["support"]["supported"] is True


def test_the_page_can_read_it_through_the_api(client):
    x, y = _spectrum()
    csv = "\n".join(f"{a:.3f},{b:.2f}" for a, b in zip(x, y))
    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
    body = client.post("/api/fit", json={"session_id": sid, "background": {"method": "linear"}, "peaks": _specs(),
                                          "fit_method": "least_squares", "n_perturb": 3}).get_json()
    assert all(ip["support"]["supported"] is True for ip in body["individual_peaks"])


def test_on_the_committed_targets_the_three_known_unsupported_components_are_the_only_ones():
    # The amplitude-floor measurement (plan §6) found exactly three, on three
    # C 1s re-fits; the server statistic must reproduce that.
    import json
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "docs/findings/optimizer-disagreement/amplitude_floor.jsonl"
    if not path.exists():
        pytest.skip("measurement file not present")
    R = [json.loads(l) for l in path.read_text().splitlines()]
    flagged = {(r["tab"], c["name"]) for r in R for c in r.get("components", []) if c["unsupported"] and not c["linked"]}
    assert flagged == {("C1s Scan_4", "Unknown 2"), ("C1s Scan_0", "Unknown 2"), ("C1s Scan_6", "Adventitious 2")}


def test_a_grandchild_follows_the_root_whatever_the_request_order():
    # Codex round 1: request order [3, 2, 1] with links 3 -> 2 -> 1 and an
    # unsupported root gave [False, True, True] after a single forward pass.
    x, y = _spectrum()
    root = {"id": 7, "shape": "gaussian", "center": 292.5, "center_min": 291.5, "center_max": 293.5,
            "amplitude": 300.0, "amplitude_min": 0, "fwhm": 1.0}
    child = {"id": 8, "shape": "gaussian", "center": 293.0, "amplitude": 30.0, "fwhm": 1.0, "amplitude_min": 0,
             "constrain_to": 7, "splitting": 0.5, "area_ratio": 0.1}
    grandchild = {"id": 9, "shape": "gaussian", "center": 293.5, "amplitude": 3.0, "fwhm": 1.0, "amplitude_min": 0,
                  "constrain_to": 8, "splitting": 0.5, "area_ratio": 0.1}
    for order in ([grandchild, child, root], [root, child, grandchild], [child, grandchild, root]):
        res = fitting.run_fit(x, y, order + _specs(), **KW)
        by = {str(ip["id"]): ip for ip in res["individual_peaks"]}
        assert by["7"]["support"]["supported"] is False
        assert by["8"]["support"]["supported"] is False and by["8"]["support"]["follows"] == 7
        assert by["9"]["support"]["supported"] is False and by["9"]["support"]["follows"] == 7
