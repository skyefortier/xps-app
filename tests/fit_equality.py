"""Two fit responses are the SAME FIT when they agree within rounding (unit A2,
2026-09-29).

Owner decisions: the requirement is that re-running a fit regenerates it within
meaningful precision, not bit-identity (2026-09-21); since the minimum
certificate (A2) moves fits onto Trust-Region's arithmetic, Levenberg-Marquardt
and Nelder-Mead are held to that too — and so must these comparisons, which
must still FAIL when a fit lands in a different minimum
(`tests/test_fit_equality.py` proves it does, including for a small component
beside a dominant one).

The tolerances are the certificate's own scales, not tuned numbers. A fit is
certified when a restart improves chi-square by less than ftol (relative), so
two certified points of one minimum agree in the OBJECTIVE to ~ftol:
OBJECTIVE_REL = 10 x ftol (1e-7; measured on the committed targets: same-
minimum presses differ by <= 8.9e-9 relative under the certificate). Near a
minimum chi-square is quadratic, so the PARAMETERS are determined only to
~sqrt(ftol) of their scale: SAME_MINIMUM_REL = 10 x sqrt(ftol) (1e-3; measured
press to press on the tests' models: <= 1.4e-6).

Each quantity is judged on ITS OWN scale — a component's curve against that
component's height, its centre against its own width — so a small component
next to a dominant one cannot relocate unnoticed (Codex A2 round 1). A
component the fit calls NOT SUPPORTED in both responses has undetermined
parameters (that is what the verdict says), so only its verdict is compared.
Everything that is not a real number — structure, flags, ids, counts, the
seed — must be identical; non-finite values must sit in the same places. Not
compared: the optimiser's message and the certificate's restart count / moved
flag (how the point was reached; its `certified` verdict is compared).
"""
import math

import numpy as np

import fitting

SAME_MINIMUM_REL = 10 * math.sqrt(fitting.CERTIFY_FTOL)
OBJECTIVE_REL = 10 * fitting.CERTIFY_FTOL

_SIGNAL_CURVES = ("fitted_y", "residuals", "background_y")
_OBJECTIVE = ("chi_square", "reduced_chi_square")
_LOG_OBJECTIVE = ("aic", "bic")                     # n ln(chi2 / n) + 2k: an absolute difference of n x relative
_POSITIONS = ("center", "center_shift_from_start", "ev")
_PERCENTAGES = ("area_percent", "largest_fraction_difference_pp")


def _as_curve(v):
    return np.array([np.nan if e is None else e for e in v], dtype=float)


def _half_max_width(x, y):
    y = np.abs(np.asarray(y, float))
    if not y.size or not np.isfinite(y).all() or y.max() == 0:
        return None
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 1.0
    return max(int(np.count_nonzero(y >= y.max() / 2)), 1) * step


def assert_same_fit(a, b, rel=SAME_MINIMUM_REL, objective_rel=OBJECTIVE_REL):
    x = np.asarray(a["energy"], float)
    signal = float(np.nanmax(np.abs(np.asarray(a["counts"], float) - np.asarray(a["background_y"], float)))) or 1.0
    span = float(np.ptp(x)) or 1.0
    n_data = len(x)
    width = {}
    for pa, pb in zip(a.get("individual_peaks") or [], b.get("individual_peaks") or []):
        wa, wb = _half_max_width(x, pa.get("y") or []), _half_max_width(x, pb.get("y") or [])
        width[str(pa.get("id"))] = min(w for w in (wa, wb, span) if w)
    problems = []

    def curve(xs, ys, where, scale):
        A, B = _as_curve(xs), _as_curve(ys)
        if A.shape != B.shape:
            problems.append(f"{where}: length {A.size} vs {B.size}"); return
        if not np.array_equal(np.isfinite(A), np.isfinite(B)) or not np.array_equal(np.isnan(A), np.isnan(B)):
            problems.append(f"{where}: non-finite values in different places"); return
        ok = np.isfinite(A)
        if (~ok).any() and not np.array_equal(A[~ok], B[~ok], equal_nan=True):
            problems.append(f"{where}: different infinities"); return
        d = float(np.max(np.abs(A[ok] - B[ok]))) if ok.any() else 0.0
        if d > rel * scale:
            problems.append(f"{where}: curves differ by {d:.3g} (> {rel:g} x {scale:.3g})")

    def number(x_, y_, path, comp_id, bounds):
        where = ".".join(path)
        if isinstance(x_, bool) or isinstance(y_, bool) or not isinstance(y_, (int, float)):
            problems.append(f"{where}: {x_!r} vs {y_!r}"); return
        if not (math.isfinite(x_) and math.isfinite(y_)):
            if not (x_ == y_ or (math.isnan(x_) and math.isnan(y_))):
                problems.append(f"{where}: {x_!r} vs {y_!r}")
            return
        last = path[-1] if path[-1] != "value" else path[-2]
        if last in _OBJECTIVE:
            tol = objective_rel * max(abs(x_), abs(y_))
        elif last in _LOG_OBJECTIVE:
            tol = objective_rel * n_data
        elif last in _POSITIONS:
            tol = rel * (width.get(comp_id) or span)
        elif last in _PERCENTAGES:
            tol = rel * 100.0
        elif bounds and bounds[0] is not None and bounds[1] is not None:
            tol = rel * max(abs(bounds[1] - bounds[0]), abs(x_), abs(y_))
        else:
            tol = rel * max(abs(x_), abs(y_))
        if abs(x_ - y_) > tol:
            problems.append(f"{where}: {x_!r} vs {y_!r}")

    def cmp(x_, y_, path, comp_id=None, bounds=None):
        where = ".".join(path) or "response"
        if path and path[-1] == "message":
            return
        if path[:1] == ("certificate",) and len(path) >= 2 and path[1] != "certified":
            return
        if isinstance(x_, dict) and isinstance(y_, dict):
            if set(x_) != set(y_):
                problems.append(f"{where}: keys {sorted(set(x_) ^ set(y_))}"); return
            cid = str(x_["id"]) if "id" in x_ else comp_id
            b_ = (x_.get("min"), x_.get("max")) if "value" in x_ and ("min" in x_ or "max" in x_) else None
            if path and path[-1].isdigit() and len(path) >= 2 and path[-2] == "individual_peaks":
                sa, sb = (x_.get("support") or {}).get("supported"), (y_.get("support") or {}).get("supported")
                if sa is False and sb is False:        # undetermined by this fit: only the verdict is the result
                    cmp(x_.get("id"), y_.get("id"), path + ("id",))
                    return
                own = max(float(np.nanmax(np.abs(_as_curve(x_.get("y") or [0])))), float(np.nanmax(np.abs(_as_curve(y_.get("y") or [0])))))
                curve(x_.get("y") or [], y_.get("y") or [], where + ".y", own or 1.0)
                for k in x_:
                    if k != "y":
                        cmp(x_[k], y_[k], path + (k,), cid)
                return
            for k in x_:
                cmp(x_[k], y_[k], path + (k,), cid, b_ if k == "value" else None)
            return
        if isinstance(x_, list) and isinstance(y_, list):
            if path and path[-1] in _SIGNAL_CURVES:
                curve(x_, y_, where, signal); return
            if len(x_) != len(y_):
                problems.append(f"{where}: length {len(x_)} vs {len(y_)}"); return
            if x_ and all(isinstance(e, (int, float)) and not isinstance(e, bool) or e is None for e in x_ + y_) and path and path[-1] in ("energy", "counts"):
                curve(x_, y_, where, 0.0 + 1e-300); return
            for i, (p, q) in enumerate(zip(x_, y_)):
                cmp(p, q, path + (str(i),), comp_id)
            return
        if isinstance(x_, float) or isinstance(y_, float):
            if not isinstance(x_, (int, float)) or isinstance(x_, bool):
                problems.append(f"{where}: {x_!r} vs {y_!r}"); return
            number(float(x_), y_ if isinstance(y_, bool) else (float(y_) if isinstance(y_, (int, float)) else y_), path, comp_id, bounds)
            return
        if x_ != y_:
            problems.append(f"{where}: {x_!r} vs {y_!r}")

    cmp(a, b, ())
    assert not problems, "not the same fit:\n  " + "\n  ".join(problems)
