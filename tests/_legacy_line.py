"""The floating-point line the synthetic fit fixtures were found with.

Since background-math round 11 the linear background is the line through the window's
ends evaluated EXACTLY and rounded once (fitting._line_through). On ordinary windows
that differs from the old y0 + slope (x - x0) by at most an ulp — but the synthetic
two-basin model of tests/test_scattered_starts.py (shared by tests/test_fit_equality.py
and tests/test_runfit_certificate.py) is chaotic in the LAST BIT of its input: one ulp
at 3 of its 300 background points moves Levenberg-Marquardt's stall (chi2r ~286, not a
minimum) and with it which basin the certificate and the scattered starts reach, and
puts Trust-Region's alignment-dependent continuation on a basin boundary (identical
requests then differ run to run — the accepted, disclosed property in CLAUDE.md). Those
modules test the starts / certificate / equality machinery on a FIXED input, so they
pin the background arithmetic the model was found with; the exact line is pinned by
tests/test_background_certificate.py and tests/js/background_not_converged.test.js."""
import numpy as np
import pytest

import fitting


def _legacy_line_through(x, x0, y0, x1, y1, span=None):
    y0, y1 = float(y0), float(y1)          # exact edge levels (Fractions) since 2026-10-03
    if x1 != x0:
        slope = (y1 - y0) / (x1 - x0)
    elif y1 == y0:
        slope = 0.0
    else:
        raise fitting.BackgroundNotConverged(
            "Linear background not converged: its two end points are at the same energy "
            "with different intensities, so no line passes through both.")
    return fitting._explicit_background(y0 + slope * (np.asarray(x, dtype=float) - x0), "Linear")


@pytest.fixture(autouse=True)
def legacy_line(monkeypatch):
    monkeypatch.setattr(fitting, "_line_through", _legacy_line_through)
