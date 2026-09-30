"""Two fit responses are the SAME FIT when they agree within rounding (unit A2,
2026-09-29).

Owner decisions: the requirement is that re-running a fit regenerates it within
meaningful precision, not bit-identity (2026-09-21); since the minimum
certificate (A2) moves fits onto Trust-Region's arithmetic, Levenberg-Marquardt
and Nelder-Mead are held to that too — and so must these comparisons, which
must still FAIL when a fit lands in a different minimum
(`tests/test_fit_equality.py` proves it does, for small, unsupported and
swapped components too).

ONE METRIC, THE FIT'S OWN. A fit is certified when a restart improves
chi-square by less than ftol (relative), so two certified points of one minimum
differ, in the objective's own weighted norm, by about ftol x chi2. Every
curve — the fitted curve and EACH component's — is therefore compared as
D = sum(w^2 (y_a - y_b)^2), with the fit's weights w = 1/sqrt(max(counts, 1)),
against OBJECTIVE_REL x chi2 (OBJECTIVE_REL = 10 x ftol = 1e-7; same-minimum
presses on the committed targets differ in chi2 by <= 8.9e-9 relative). That
needs no scale of its own — no signal height, no energy span, no floor — so a
small or statistically unsupported component relocated to another minimum
counts its full weighted norm, and a zero-amplitude component's jitter counts
~0 (Codex A2 rounds 1-2). A PARAMETER is compared in units of its own
uncertainty on the same scale: |dp| <= sqrt(OBJECTIVE_REL x dof) x sigma_p
(if the fitted curve is within tolerance, delta_p^T H delta_p <= tol, so every
parameter is within that bound — Cauchy-Schwarz in the H norm). A component
the fit DETERMINES (a free parameter with a sigma) is judged by its
parameters, not its curve: two overlapping components may trade intensity
along a flat direction of one minimum, moving each curve past the objective
tolerance while the sum stays within it (seen in the full suite); a component
it does not determine is judged by its curve in the objective norm;
one the fit reports no uncertainty for is not determined by it and is covered
by its curve instead; the uncertainties themselves relatively, to
SAME_MINIMUM_REL. chi2 values (the statistics, the scattered starts'
chi2r) at OBJECTIVE_REL; the support statistic (delta-chi2, F) relatively, to
SAME_MINIMUM_REL, floored by the objective tolerance. Quantities with no curve (the scattered starts' alternatives):
area percentages to SAME_MINIMUM_REL (10 x sqrt(ftol) = 1e-3) of 100, centres to
that fraction of the component's own half-maximum width, other numbers
relatively. Everything that is not a real number — structure, flags, ids,
counts, the seed — must be identical; non-finite values must sit in the same
places. Not compared: the optimiser's message and the certificate's restart
count / moved flag / moves (how the point was reached; its `certified`
verdict is compared).
"""
import math

import numpy as np

import fitting

SAME_MINIMUM_REL = 10 * math.sqrt(fitting.CERTIFY_FTOL)
OBJECTIVE_REL = 10 * fitting.CERTIFY_FTOL

_OBJECTIVE = ("chi_square", "reduced_chi_square", "chi2r", "not_better_chi2r")
_LOG_OBJECTIVE = ("aic", "bic")                     # n ln(chi2 / n) + 2k: an absolute difference of n x relative
_POSITIONS = ("center", "center_shift_from_start", "ev")
_PERCENTAGES = ("area_percent", "largest_fraction_difference_pp")
_WEIGHTED_CURVES = ("fitted_y", "residuals")


def _as_curve(v):
    return np.array([np.nan if e is None else e for e in v], dtype=float)


def _finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _determined(peak):
    """The fit determines this component: a freely varying parameter with a finite uncertainty."""
    for name, info in (peak.get("params") or {}).items():
        if name == "area" or not isinstance(info, dict):
            continue
        sd = info.get("stderr")
        if info.get("vary", True) and not info.get("expr") and _finite(sd) and sd > 0:
            return True
    return False


def _half_max_width(x, y):
    y = np.abs(_as_curve(y))
    y = y[np.isfinite(y)] if y.size else y
    if not y.size or y.max() == 0:
        return None
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 1.0
    return max(int(np.count_nonzero(y >= y.max() / 2)), 1) * step


def assert_same_fit(a, b, rel=SAME_MINIMUM_REL, objective_rel=OBJECTIVE_REL):
    x = np.asarray(a["energy"], float)
    w2 = 1.0 / np.maximum(np.asarray(a["counts"], float), 1.0)
    stats_a, stats_b = a.get("statistics") or {}, b.get("statistics") or {}
    chis = [v for v in (stats_a.get("chi_square"), stats_b.get("chi_square")) if _finite(v)]
    chi = max(chis) if chis else 0.0
    n_data = int(stats_a.get("n_data") or len(x))
    dof = max(1, n_data - int(stats_a.get("n_free_params") or 0))
    curve_tol = objective_rel * chi                    # in the objective's own weighted norm
    sigma_units = math.sqrt(objective_rel * dof)       # a parameter's share of that, in units of its sigma
    span = float(np.ptp(x)) or 1.0
    width = {}
    for pa, pb in zip(a.get("individual_peaks") or [], b.get("individual_peaks") or []):
        ws = [w for w in (_half_max_width(x, pa.get("y") or []), _half_max_width(x, pb.get("y") or [])) if w]
        width[str(pa.get("id"))] = min(ws) if ws else span
    problems = []

    def masks(A, B, where):
        if A.shape != B.shape:
            problems.append(f"{where}: length {A.size} vs {B.size}"); return None
        fa, fb = np.isfinite(A), np.isfinite(B)
        if not np.array_equal(fa, fb) or not np.array_equal(A[~fa], B[~fb], equal_nan=True):
            problems.append(f"{where}: non-finite values in different places"); return None
        return fa

    def weighted_curve(xs, ys, where):
        A, B = _as_curve(xs), _as_curve(ys)
        ok = masks(A, B, where)
        if ok is None:
            return
        d = float(np.sum(w2[ok] * (A[ok] - B[ok]) ** 2)) if A.size == w2.size else float("inf")
        if not d <= curve_tol:
            problems.append(f"{where}: differ by {d:.3g} in the fit's weighted norm (> {objective_rel:g} x chi2 {chi:.6g})")

    def exact_curve(xs, ys, where):
        A, B = _as_curve(xs), _as_curve(ys)
        ok = masks(A, B, where)
        if ok is not None and not np.array_equal(A[ok], B[ok]):
            d = float(np.max(np.abs(A[ok] - B[ok])))
            scale = float(np.max(np.abs(A[ok]))) if ok.any() else 0.0
            if d > rel * scale:
                problems.append(f"{where}: differ by {d:.3g}")

    def key_of(path):
        for p in reversed(path):
            if p not in ("value",) and not p.isdigit():
                return p
        return ""

    def number(x_, y_, path, comp_id, sigmas):
        where = ".".join(path)
        if isinstance(x_, bool) or isinstance(y_, bool) or not isinstance(y_, (int, float)) or not isinstance(x_, (int, float)):
            if x_ != y_:
                problems.append(f"{where}: {x_!r} vs {y_!r}")
            return
        x_, y_ = float(x_), float(y_)
        if not (math.isfinite(x_) and math.isfinite(y_)):
            if not (x_ == y_ or (math.isnan(x_) and math.isnan(y_))):
                problems.append(f"{where}: {x_!r} vs {y_!r}")
            return
        k = key_of(path)
        if sigmas is not None:                           # a fitted parameter's value
            if sigmas is False:
                return                                   # undetermined by the fit (no sigma): its curve decides
            tol = sigma_units * max(sigmas)
        elif k in _OBJECTIVE:
            tol = objective_rel * max(abs(x_), abs(y_))
        elif k in _LOG_OBJECTIVE:
            tol = objective_rel * n_data
        elif k in _POSITIONS:
            tol = rel * (width.get(comp_id) or span)
        elif k in _PERCENTAGES:
            tol = rel * 100.0
        else:
            tol = rel * max(abs(x_), abs(y_))
        if abs(x_ - y_) > tol:
            problems.append(f"{where}: {x_!r} vs {y_!r}")

    def cmp(x_, y_, path, comp_id=None):
        where = ".".join(path) or "response"
        if path and path[-1] == "message":
            return
        if path[:1] == ("certificate",) and len(path) >= 2 and path[1] != "certified":
            return
        if isinstance(x_, dict) and isinstance(y_, dict):
            if set(x_) != set(y_):
                problems.append(f"{where}: keys {sorted(set(x_) ^ set(y_))}"); return
            cid = str(x_["id"]) if "id" in x_ else comp_id
            if path and path[-1] == "support" and "delta_chi2" in x_:
                support(x_, y_, path); return
            if len(path) >= 2 and path[-2] == "individual_peaks":
                if _determined(x_) and _determined(y_):
                    # its parameters (sigma units) decide: two overlapping components may trade
                    # intensity along a flat direction of ONE minimum (the sum — fitted_y — stays
                    # within tolerance), which moves each curve further than 10 x ftol x chi2
                    A, B = _as_curve(x_.get("y") or []), _as_curve(y_.get("y") or [])
                    masks(A, B, where + ".y")
                else:
                    weighted_curve(x_.get("y") or [], y_.get("y") or [], where + ".y")
                for k in x_:
                    if k == "params":
                        params(x_[k], y_[k], path + (k,), cid)
                    elif k != "y":
                        cmp(x_[k], y_[k], path + (k,), cid)
                return
            for k in x_:
                cmp(x_[k], y_[k], path + (k,), cid)
            return
        if isinstance(x_, list) and isinstance(y_, list):
            if path and path[-1] in _WEIGHTED_CURVES:
                weighted_curve(x_, y_, where); return
            if path and path[-1] in ("energy", "counts", "background_y"):
                exact_curve(x_, y_, where); return
            if len(x_) != len(y_):
                problems.append(f"{where}: length {len(x_)} vs {len(y_)}"); return
            for i, (p, q) in enumerate(zip(x_, y_)):
                cmp(p, q, path + (str(i),), comp_id)
            return
        if isinstance(x_, float) or isinstance(y_, float):
            number(x_, y_, path, comp_id, None)
            return
        if x_ != y_:
            problems.append(f"{where}: {x_!r} vs {y_!r}")

    def support(sa, sb, path):
        # delta = sum w^2 (r + y_c)^2 - sum w^2 r^2 is FIRST order in the component's curve: a
        # curve within curve_tol moves it by <= 2 sqrt(chi2_without x curve_tol) (Cauchy-Schwarz);
        # F = (delta / p) / (chi2 / dof) follows delta and chi2 relatively
        for k in sa:
            if k not in ("delta_chi2", "f"):
                cmp(sa[k], sb[k], path + (k,))
        da, db = sa["delta_chi2"], sb["delta_chi2"]
        if not (_finite(da) and _finite(db)):
            number(da, db, path + ("delta_chi2",), None, None); return
        dmax = max(abs(da), abs(db))
        # relative to itself (a flat direction shared with a neighbour moves it), floored by
        # the objective tolerance (a zero-amplitude component's delta is ~0 either way)
        if abs(da - db) > rel * dmax + curve_tol:
            problems.append(f"{'.'.join(path + ('delta_chi2',))}: {da!r} vs {db!r}")
        fa, fb = sa["f"], sb["f"]
        if _finite(fa) and _finite(fb):
            if abs(fa - fb) > rel * max(abs(fa), abs(fb)) + objective_rel * dof:
                problems.append(f"{'.'.join(path + ('f',))}: {fa!r} vs {fb!r}")
        elif fa != fb:
            problems.append(f"{'.'.join(path + ('f',))}: {fa!r} vs {fb!r}")

    def params(pa, pb, path, cid):
        if set(pa) != set(pb):
            problems.append(f"{'.'.join(path)}: keys {sorted(set(pa) ^ set(pb))}"); return
        for name in pa:
            ia, ib = pa[name], pb[name]
            p = path + (name,)
            if name == "area":                           # the integral of the component's curve: its curve decides
                cmp(ia.get("stderr") is None, ib.get("stderr") is None, p + ("stderr is None",))
                continue
            for k in ia:
                if k == "value":
                    sa, sb = ia.get("stderr"), ib.get("stderr")
                    sig = (abs(sa), abs(sb)) if _finite(sa) and _finite(sb) and sa and sb else False
                    if not ia.get("vary", True) or ia.get("expr"):
                        sig = None                       # fixed or constrained: its own rules (exact / its master's)
                    number(ia[k], ib[k], p + (k,), cid, sig) if sig is not None else cmp(ia[k], ib[k], p + (k,), cid)
                elif k == "stderr":
                    sa, sb = ia[k], ib[k]
                    if (sa is None) != (sb is None) or (_finite(sa) != _finite(sb)):
                        problems.append(f"{'.'.join(p + (k,))}: {sa!r} vs {sb!r}")
                    elif _finite(sa) and abs(sa - sb) > rel * max(abs(sa), abs(sb)):
                        problems.append(f"{'.'.join(p + (k,))}: {sa!r} vs {sb!r}")     # a reported uncertainty, relatively
                else:
                    cmp(ia[k], ib[k], p + (k,), cid)

    cmp(a, b, ())
    assert not problems, "not the same fit:\n  " + "\n  ".join(problems)
