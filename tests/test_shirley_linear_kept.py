"""The shirley_linear implementation is KEPT after the UI de-listing
(owner decision 2026-09-03: remove from the menu, never delete the code path,
so a saved file that used it still fits). Pins the backend route and the
frontend twin + its computeBackgroundCore route by name."""
import re
from pathlib import Path

import numpy as np

import fitting

ROOT = Path(__file__).resolve().parents[1]


def test_backend_still_fits_with_shirley_linear():
    x = 295.0 - 0.1 * np.arange(120)
    y = 800 + 3000 * np.exp(-((x - 286.5) ** 2) / 0.5) + np.where(x < 286.5, 400.0, 0.0)
    r = fitting.run_fit(x, y, [dict(id="1", name="p", center=286.5, amplitude=3000, fwhm=1.2, shape="gaussian")],
                        background_method="shirley_linear", bg_start_idx=0, bg_end_idx=len(x))
    assert r["success"] is True
    assert len(r["background_y"]) == len(x)


def test_frontend_twin_and_route_still_present():
    html = (ROOT / "templates" / "index.html").read_text()
    assert re.search(r"function shirleyLinearBackground\(", html)
    assert "type === 'shirley_linear'" in html, "computeBackgroundCore must still route shirley_linear"
    assert 'option value="shirley_linear"' in html, "the option must stay in the DOM (hidden) for saved files"
