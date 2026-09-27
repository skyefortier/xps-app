"""Unit F2 (2026-09-26): holes in the acceptance rule — "nothing is a fit
unless it converged and is determined".

- A model with at least as many free parameters as data points is refused as
  undetermined (it read as a near-perfect, fully supported fit: sweep M2).
- The required-anchor verdict needs a CONVERGED refit (sweep M3): an
  unconverged refit gives no verdict.

The basinhopping outcome (sweep H2) and the page's handling of a NaN reply
(sweep M1) are pinned in tests/test_basinhopping_outcome.py and
tests/js/fit_acceptance.test.js.
"""

import io
from types import SimpleNamespace

import numpy as np
import pytest
from lmfit import Parameters

import fitting
from app import create_app


def _gl(x, c, a, w):
    return a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)


def _two_gl_specs():
    # two GL components, every parameter free: centre, fwhm, amplitude, gl mix = 8
    return [
        {"id": "1", "shape": "pseudo_voigt_gl", "center": 284.5, "fwhm": 1.0, "amplitude": 1000.0,
         "gl_ratio": 0.3, "fix_gl_ratio": False, "amplitude_min": 0},
        {"id": "2", "shape": "pseudo_voigt_gl", "center": 286.0, "fwhm": 1.0, "amplitude": 400.0,
         "gl_ratio": 0.3, "fix_gl_ratio": False, "amplitude_min": 0},
    ]


def _data(n):
    x = np.linspace(283.0, 288.0, n)
    y = 100.0 + _gl(x, 284.5, 1000.0, 1.0) + _gl(x, 286.0, 400.0, 1.0)
    return x, y


@pytest.mark.parametrize("n", [6, 8])          # the sweep's reproduction (6 < 8) and zero dof (8 = 8)
def test_no_degrees_of_freedom_is_refused_as_undetermined(n):
    x, y = _data(n)
    with pytest.raises(ValueError, match=r"not determined by these data: 8 free parameters for %d data points" % n):
        fitting.run_fit(x, y, _two_gl_specs(), background_method="none", fit_kws={"method": "least_squares"})


def test_one_degree_of_freedom_is_still_a_fit_and_linked_or_locked_parameters_do_not_count():
    x, y = _data(9)                              # 8 free, 9 points: dof 1 — determined, fitted as before
    res = fitting.run_fit(x, y, _two_gl_specs(), background_method="none", fit_kws={"method": "least_squares"})
    assert res["statistics"]["n_free_params"] == 8
    # locking the mixes leaves 6 free: 7 points are then enough
    x7, y7 = _data(7)
    specs = _two_gl_specs()
    for s in specs:
        s["fix_gl_ratio"] = True
    res = fitting.run_fit(x7, y7, specs, background_method="none", fit_kws={"method": "least_squares"})
    assert res["statistics"]["n_free_params"] == 6


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_api_fit_returns_the_refusal_as_a_400_with_its_message(client):
    x, y = _data(6)
    csv = "\n".join(f"{a:.4f},{b:.2f}" for a, b in zip(x, y))
    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "tiny.csv")}).get_json()["session_id"]
    resp = client.post("/api/fit", json={"session_id": sid, "background": {"method": "none"},
                                         "peaks": _two_gl_specs(), "fit_method": "least_squares"})
    assert resp.status_code == 400
    assert "not determined by these data" in resp.get_json()["error"]


def test_an_unconverged_refit_gives_no_required_verdict():
    """The sweep's reproduction: a refit stopped early read required: true
    (F 992) for an anchor that is redundant (F 1.17 once the refit completes)."""
    params = Parameters()
    params.add("p1_amplitude", value=1.0)
    params.add("p2_amplitude", value=1.0)
    y_sub = np.ones(50)
    stopped = SimpleNamespace(success=False, chisqr=992.0, message="max evaluations reached")
    out = fitting._component_required(lambda p: stopped, params, ["p1_"], y_sub, np.ones(50),
                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
    assert out["required"] is None
    assert out["f"] is None
    assert out["refit_converged"] is False
    assert out["reason"] == "refit_not_converged"
    assert "max evaluations" in out["message"]
    # a converged refit still gives its verdict, unchanged
    done = SimpleNamespace(success=True, chisqr=1.0 + 1.17 / 48, message="ok")
    out = fitting._component_required(lambda p: done, params, ["p1_"], y_sub, np.ones(50),
                                      chi2_with=1.0, n_free_comp=1, n_free_total=2)
    assert out["refit_converged"] is True and out["required"] is False
    assert out["f"] == pytest.approx(1.17)
