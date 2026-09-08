"""Find Peaks honours the Background panel's endpoint averaging (F3 round two).

The audit-F3 fix (2026-07-17) gave engine._compute_background an
``endpoint_avg`` knob defaulting to 1, which matched the frontend default at
the time. The frontend default is now 3 (docs/superpowers/plans/
2026-09-03-endpoint-averaging-default.md), so a Find Peaks run that still
fits at 1 diverges from every manual fit on a fresh tab — guaranteed, not
latent. This unit threads ``endpoint_avg`` the way ``fit_full_window`` is:
request option -> method whitelist -> compare_models -> every fit_candidate
and _compute_background call, plus the two direct calls in the bayesian and
sparse_map methods. Default 1 everywhere keeps the parity fixtures
byte-stable.

Structural guard (the class-killer): every background/fit call in the
autofit package must pass endpoint_avg explicitly, so a future call site
cannot silently fall back to 1.
"""
import re
from pathlib import Path

import numpy as np
import pytest

from autofit.engine import _compute_background, fit_candidate
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.methods import get_method
from autofit.methods.base import poisson_like_weights

GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
                 regions=("C 1s",), material="graphite")

ROOT = Path(__file__).resolve().parents[2]


def _synthetic_c1s(seed=0):
    rng = np.random.default_rng(seed)
    x = np.arange(280.0, 294.0, 0.1)
    g = lambda c, a, w: a * np.exp(-((x - c) ** 2) / (2 * w * w))
    y = 400 + g(284.4, 12000, 0.8) + g(286.2, 1500, 1.2) + g(290.8, 600, 2.0)
    return x, y + rng.normal(0, 20, len(x))


# ── engine ───────────────────────────────────────────────────────────────────

def test_fit_candidate_background_uses_the_requested_endpoint_avg():
    x, y = _synthetic_c1s()
    w = poisson_like_weights(y)
    model = resolve([GRAPHITE], "C 1s").candidates[0]
    out1 = fit_candidate(x, y, w, model, endpoint_avg=1)
    out10 = fit_candidate(x, y, w, model, endpoint_avg=10)
    np.testing.assert_allclose(out10.background, _compute_background(x, y, model.background, endpoint_avg=10))
    np.testing.assert_allclose(out1.background, _compute_background(x, y, model.background, endpoint_avg=1))
    assert np.max(np.abs(out10.background - out1.background)) > 1.0, "averaging must change the anchor on noisy data"


def _calls(src: str, name: str):
    """Every call of `name(` in src (definitions excluded), as the text up to the
    matching close paren."""
    out = []
    for m in re.finditer(r'(?<!def )\b' + re.escape(name) + r'\(', src):
        i, depth = m.end(), 1
        while depth and i < len(src):
            depth += {'(': 1, ')': -1}.get(src[i], 0)
            i += 1
        call = src[m.start():i]
        if re.fullmatch(re.escape(name) + r'\(\s*\)', call):
            continue   # a prose mention like "see fit_candidate() docstring", not a call
        out.append(call)
    return out


@pytest.mark.parametrize("fname, callee", [
    ("autofit/engine.py", "_compute_background"),
    ("autofit/engine.py", "fit_candidate"),
    ("autofit/engine.py", "_attempt_proposal"),
    ("autofit/engine.py", "_bound_fixed_refit"),
    ("autofit/engine.py", "_apply_decisive_override"),
    ("autofit/engine.py", "run_stability_analysis"),
    ("autofit/methods/bayesian_exchange_mc.py", "_compute_background"),
    ("autofit/methods/sparse_map.py", "_compute_background"),
    ("autofit/methods/ic_model_comparison.py", "compare_models"),
])
def test_every_background_affecting_call_passes_endpoint_avg(fname, callee):
    src = (ROOT / fname).read_text()
    calls = _calls(src, callee)
    assert calls, f"no calls of {callee} found in {fname}"
    missing = [c[:80] for c in calls if "endpoint_avg=" not in c]
    assert not missing, f"{fname}: {callee} called without endpoint_avg: {missing}"


# ── methods forward the option ───────────────────────────────────────────────

def test_least_squares_method_honours_endpoint_avg():
    x, y = _synthetic_c1s()
    specs = [{"id": "1", "shape": "gaussian", "center": 284.6, "amplitude": 9000, "fwhm": 1.0}]
    m = get_method("least_squares")
    r1 = m.run(x, y, peak_specs=specs, options={"background_method": "shirley", "endpoint_avg": 1})
    r10 = m.run(x, y, peak_specs=specs, options={"background_method": "shirley", "endpoint_avg": 10})
    assert r1.success and r10.success
    # the method result carries peaks + analysis, not the background array;
    # a different anchor level changes the fitted amplitude on noisy data
    a1, a10 = r1.peaks[0]["amplitude"], r10.peaks[0]["amplitude"]
    assert abs(a1 - a10) > 1e-6, (a1, a10)
    assert r1.analysis != r10.analysis


class _Recorded(Exception):
    pass


def test_ic_model_comparison_forwards_endpoint_avg(monkeypatch):
    import autofit.methods.ic_model_comparison as icm
    seen = {}

    def fake(*a, **kw):
        seen.update(kw)
        raise _Recorded()

    monkeypatch.setattr(icm, "compare_models", fake)
    x, y = _synthetic_c1s()
    with pytest.raises(_Recorded):
        get_method("ic_model_comparison").run(x, y, grammar=resolve([GRAPHITE], "C 1s"),
                                              options={"endpoint_avg": 7})
    assert seen.get("endpoint_avg") == 7


@pytest.mark.parametrize("method_id", ["bayesian_exchange_mc", "sparse_map"])
def test_direct_background_methods_forward_endpoint_avg(monkeypatch, method_id):
    import importlib
    mod = importlib.import_module(f"autofit.methods.{method_id}")
    seen = {}

    def fake(x, y, bg, endpoint_avg=None, **kw):
        seen["endpoint_avg"] = endpoint_avg
        raise _Recorded()

    monkeypatch.setattr(mod, "_compute_background", fake)
    x, y = _synthetic_c1s()
    with pytest.raises(_Recorded):
        get_method(method_id).run(x, y, grammar=resolve([GRAPHITE], "C 1s"), options={"endpoint_avg": 7})
    assert seen.get("endpoint_avg") == 7


@pytest.mark.parametrize("method_id", ["least_squares", "ic_model_comparison", "bayesian_exchange_mc", "sparse_map"])
def test_endpoint_avg_is_an_adjustable_default_for_background_methods(method_id):
    from app import _ANALYZE_METHODS
    assert _ANALYZE_METHODS[method_id].get("endpoint_avg") == 1, "default 1 keeps parity fixtures byte-stable"


@pytest.mark.parametrize("method_id", ["max_entropy", "multivariate_mcr"])
def test_methods_without_a_background_do_not_advertise_endpoint_avg(method_id):
    from app import _ANALYZE_METHODS
    assert "endpoint_avg" not in _ANALYZE_METHODS.get(method_id, {})
