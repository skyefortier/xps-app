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


def test_on_the_committed_graphite_models_the_anchor_is_always_required():
    import json
    from pathlib import Path
    path = Path("/Users/skyefortier/xps-app/.claude/worktrees/investigate-optimizer-disagreement/docs/findings/optimizer-disagreement/targets.json")
    if not path.exists():
        pytest.skip("target file not present")
    targets = [t for t in json.loads(path.read_text()) if any(s.get("name") == "Graphite" for s in t["specs"])]
    assert len(targets) == 70
    worst = float("inf")
    for t in targets[::7]:                                  # a tenth of them keeps the test under a minute
        g = next(s for s in t["specs"] if s.get("name") == "Graphite")
        b = t["background"]
        res = fitting.run_fit(np.asarray(t["be"], float), np.round(np.asarray(t["inten"], float), 2), t["specs"],
                              background_method=b["method"], bg_start_idx=b["start_idx"], bg_end_idx=b["end_idx"],
                              endpoint_avg=b["endpoint_avg"], n_perturb=0, fit_kws={"method": "least_squares"},
                              require_component=g["id"])
        assert res["required"]["required"] is True, t["tab"]
        if res["required"]["f"] is not None:
            worst = min(worst, res["required"]["f"])
    assert worst > 10


def test_the_fit_itself_is_unchanged_by_the_check():
    import json
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    kw = {**KW, "fit_kws": {"method": "leastsq"}}
    a = fitting.run_fit(X, y, specs, **kw)
    b = fitting.run_fit(X, y, specs, require_component="1", **kw)
    strip = lambda r: json.dumps({k: v for k, v in r.items() if k != "required"}, sort_keys=True)  # noqa: E731
    assert strip(a) == strip(b) and a["required"] is None and b["required"]["ran"] is True


def test_a_component_linked_to_the_removed_one_goes_with_it():
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs.append({"id": "9", "shape": "pseudo_voigt_gl", "center": 285.5, "amplitude": 100.0, "fwhm": 0.7, "gl_ratio": 0.3,
                  "amplitude_min": 0, "constrain_to": "1", "splitting": 1.0, "area_ratio": 0.1})
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    assert res["required"]["ran"] is True and res["required"]["required"] is False


def test_validation_and_never_failing_the_fit(client, monkeypatch):
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4), 2)
    specs = _autofit_model(1000, [(10000, 284.8, 1.4)])
    with pytest.raises(ValueError, match="not one of the peaks"):
        fitting.run_fit(X, y, specs, require_component="42", **KW)
    with pytest.raises(ValueError, match="at least two"):
        fitting.run_fit(X, y, specs[:1], require_component="1", **KW)
    real = fitting._component_required
    monkeypatch.setattr(fitting, "_component_required", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    assert res["success"] is True and res["required"]["ran"] is False and "boom" in res["required"]["error"]
    monkeypatch.setattr(fitting, "_component_required", real)
    csv = "\n".join(f"{a:.3f},{b:.2f}" for a, b in zip(X, y))
    sid = client.post("/api/upload", data={"file": (io.BytesIO(csv.encode()), "s.csv")}).get_json()["session_id"]
    bad = client.post("/api/fit", json={"session_id": sid, "background": {"method": "linear"}, "peaks": specs,
                                        "fit_method": "least_squares", "n_perturb": 0, "require_component": {"id": 1}})
    assert bad.status_code == 400
    ok = client.post("/api/fit", json={"session_id": sid, "background": {"method": "linear"}, "peaks": specs,
                                       "fit_method": "least_squares", "n_perturb": 0, "require_component": "1"})
    assert ok.status_code == 200 and ok.get_json()["required"]["ran"] is True
