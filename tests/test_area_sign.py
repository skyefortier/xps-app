"""
run_fit's per-peak `area` must be positive regardless of grid direction.

Real XPS acquisitions store descending BE grids; trapezoid(peak_y, x)
on a descending x yields a NEGATIVE integral, so every stored
_backendParams.area for real data came out negative (e.g. -44163 for
the committed 1-GTA UCl4-graphite U4f Scan_0 LACX peak, amplitude
+13750). The user-facing Quantify path was unaffected only because the
frontend computes its own areas (`_peakArea`, always positive) — the
sign bug lived purely in the backend JSON/saved-project layer.

Convention pinned here: area = |∫ peak dE| (matches autofit/engine.py's
existing `abs(trapezoid(...))`), and ascending/descending grids agree.
"""
import numpy as np

# repo root comes from tests/conftest.py's sys.path insert, which resolves
# relative to this checkout (worktree-safe — an absolute main-repo path here
# would silently import the WRONG fitting.py from a worktree).
from fitting import run_fit

PEAK_SPECS = [{
    "id": "1",
    "shape": "gaussian",
    "center": 285.0, "amplitude": 5000.0, "fwhm": 1.2,
}]


def _synth(descending: bool):
    x = np.linspace(280.0, 290.0, 501)
    if descending:
        x = x[::-1].copy()
    y = 100.0 + 5000.0 * np.exp(-4 * np.log(2) * ((x - 285.0) / 1.2) ** 2)
    return x, y


def _fit_area(descending: bool) -> float:
    x, y = _synth(descending)
    result = run_fit(
        energy=x, counts=y, peak_specs=[dict(s) for s in PEAK_SPECS],
        background_method="linear", n_perturb=0,
    )
    assert result["success"]
    return result["individual_peaks"][0]["params"]["area"]["value"]


def test_area_positive_on_descending_grid():
    area = _fit_area(descending=True)
    assert area > 0, f"area on a descending (real-data) BE grid must be positive, got {area}"


def test_area_positive_on_ascending_grid():
    area = _fit_area(descending=False)
    assert area > 0, f"area on an ascending BE grid must be positive, got {area}"


def test_area_grid_direction_invariant():
    a_up = _fit_area(descending=False)
    a_down = _fit_area(descending=True)
    assert np.isclose(a_up, a_down, rtol=1e-6), (
        f"area must not depend on grid direction: ascending {a_up} vs descending {a_down}"
    )
