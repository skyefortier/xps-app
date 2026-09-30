"""Two fit responses are the SAME FIT when they agree within rounding (unit A2,
2026-09-29).

Owner decisions: the requirement is that re-running a fit regenerates it within
meaningful precision, not bit-identity (2026-09-21); since the minimum
certificate (A2) moves fits onto Trust-Region's arithmetic, Levenberg-Marquardt
and Nelder-Mead are held to that too — and so must these comparisons, which
must still FAIL when a fit lands in a different minimum
(`tests/test_fit_equality.py` proves it does).

The tolerance is the certificate's own scale, not a tuned number. A fit is
certified when a restart improves chi-square by less than ftol (relative); near
a minimum chi-square is quadratic, so its parameters are determined only to
~sqrt(ftol) of their scale, and rounding moves a certified point by that much
between presses. SAME_MINIMUM_REL = 10 x sqrt(ftol) = 1e-3. Measured press-to-
press differences on the tests' models: <= 1.4e-6 relative (Levenberg-
Marquardt, Nelder-Mead), <= 6.6e-5 (Trust-Region sigma). Another minimum
differs by far more: the scattered-starts check calls two solutions the same
only within 1 pp of area and 0.1 eV.

Rules: everything that is not a real number — structure, flags, ids, counts,
the seed — must be identical. Curves (fitted_y, residuals, each component's y,
background_y) agree to SAME_MINIMUM_REL of the data's signal scale; centres to
SAME_MINIMUM_REL of the fitted energy span (so are shifts); percentages to
SAME_MINIMUM_REL of 100; a parameter with finite bounds to
SAME_MINIMUM_REL of its bound span (a value pinned at a bound, 1e-14 vs 1e-12,
is the same value); every other number relatively. Not compared: the
optimiser's message and the certificate's restart count / moved flag (how the
point was reached; its `certified` verdict is compared).
"""
import math

import numpy as np

import fitting

SAME_MINIMUM_REL = 10 * math.sqrt(fitting.CERTIFY_FTOL)

_CURVES = ("fitted_y", "residuals", "background_y", "y")
_NOT_COMPARED = ("message",)
_ENERGIES = ("center", "ev", "center_shift_from_start")                  # positions: the fitted energy span
_PERCENTAGES = ("area_percent", "largest_fraction_difference_pp")        # percentages: of 100


def assert_same_fit(a, b, rel=SAME_MINIMUM_REL):
    signal = float(np.max(np.abs(np.asarray(a["counts"], float) - np.asarray(a["background_y"], float)))) or 1.0
    span = float(np.ptp(np.asarray(a["energy"], float))) or 1.0
    problems = []

    def cmp(x, y, path, bounds=None):
        where = ".".join(path)
        if path and path[-1] in _NOT_COMPARED:
            return
        if path[:1] == ("certificate",) and len(path) >= 2 and path[1] != "certified":
            return
        if isinstance(x, dict) and isinstance(y, dict):
            if set(x) != set(y):
                problems.append(f"{where}: keys {sorted(set(x) ^ set(y))}")
                return
            # a parameter's bounds decide its absolute scale
            b_ = (x.get("min"), x.get("max")) if "value" in x and ("min" in x or "max" in x) else None
            for k in x:
                cmp(x[k], y[k], path + (k,), b_ if k == "value" else None)
            return
        if isinstance(x, list) and isinstance(y, list):
            if len(x) != len(y):
                problems.append(f"{where}: length {len(x)} vs {len(y)}")
                return
            if path and path[-1] in _CURVES:
                d = float(np.max(np.abs(np.asarray(x, float) - np.asarray(y, float)))) if x else 0.0
                if d > rel * signal:
                    problems.append(f"{where}: curves differ by {d:.3g} (> {rel:g} x signal {signal:.3g})")
                return
            for i, (p, q) in enumerate(zip(x, y)):
                cmp(p, q, path + (str(i),))
            return
        if isinstance(x, float) or isinstance(y, float):
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float))) or isinstance(x, bool) or isinstance(y, bool):
                problems.append(f"{where}: {x!r} vs {y!r}")
                return
            if not (math.isfinite(x) and math.isfinite(y)):
                if not (x == y or (math.isnan(x) and math.isnan(y))):
                    problems.append(f"{where}: {x!r} vs {y!r}")
                return
            if path[-1] in _ENERGIES or (len(path) >= 2 and path[-2] == "center" and path[-1] == "value"):
                scale = span
            elif path[-1] in _PERCENTAGES:
                scale = 100.0
            elif bounds and bounds[0] is not None and bounds[1] is not None:
                scale = max(abs(bounds[1] - bounds[0]), abs(x), abs(y))
            else:
                scale = max(abs(x), abs(y))
            if abs(x - y) > rel * scale:
                problems.append(f"{where}: {x!r} vs {y!r}")
            return
        if x != y:
            problems.append(f"{where}: {x!r} vs {y!r}")

    cmp(a, b, ())
    assert not problems, "not the same fit:\n  " + "\n  ".join(problems[:12])
