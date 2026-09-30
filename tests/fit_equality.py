"""Two fit responses are the SAME FIT when they agree within rounding (unit A2,
2026-09-29).

Owner decisions: the requirement is that re-running a fit regenerates it within
meaningful precision, not bit-identity (2026-09-21); since the minimum
certificate (A2) moves fits onto Trust-Region's arithmetic, Levenberg-Marquardt
and Nelder-Mead are held to that too — and so must these comparisons, which
must still FAIL when a fit lands in a different minimum
(`tests/test_fit_equality.py` proves it does, for small, unsupported and
swapped components too).

EVERY QUANTITY ON ITS OWN SCALE, NO EXEMPTIONS. Two scales, both the
certificate's own (a fit is certified when a restart improves chi-square by
less than ftol, relative):
  * the OBJECTIVE — chi-square in the statistics and in the scattered starts'
    chi2r — to OBJECTIVE_REL = 10 x ftol (1e-7); same-minimum presses on the
    committed targets differ by <= 8.9e-9 relative;
  * everything the objective determines only to second order — curves,
    parameters, areas — to SAME_MINIMUM_REL = 10 x sqrt(ftol) (1e-3) OF ITS
    OWN SCALE: each component's curve against that component's own height;
    its centre (and every centre shift) against its own half-maximum width
    (a scattered-start alternative's centres against the half-maximum width of
    its own curve, evaluated from its parameters through the server's lineshape,
    and that curve against its own height, like a returned component's);
    a bounded parameter against its bound span ALONE (a value pinned at a
    bound, 1e-14 vs 1e-12, is the same value), a LINKED parameter against the
    span of the bounded master its expression follows, through any chain of links;
    a scattered-start alternative's bare parameter values take the same bounds
    from the model (the returned fit's matching parameter); the fitted curve against the signal;
    percentages of 100; everything else relatively. Measured press-to-press
    on the tests' models: <= 1.4e-6.
No component is exempt — not a small one beside a dominant line, not one the
support statistic calls unsupported, not one with a huge sigma: Codex A2 rounds
1-3 built distinct certified minima (a 10-count line at -0.25 or +0.25 eV
beside a 1e6-count one, the saddle between them 6e-10 relative in chi2, the
centre's sigma 17 eV) that any statistical criterion accepts; on its own
scale the centre moved five widths. The resolution is what "a relative,
rounding-scale tolerance" means: minima closer than 1e-3 of EVERY quantity's
own scale are not told apart. The comparison fails closed: a component driven
exactly to zero amplitude would be compared on its own ~0 height and would
fail, never pass wrongly (the tests' models have none).
NOT compared: the optimiser's message; the certificate's restart count /
moved flag / moves (how the point was reached — its `certified` verdict is
compared); and the reported UNCERTAINTIES (stderr), which are not reproducible
within one minimum near a bound — committed evidence: B4C-UCl4 U4f Scan_1,
two presses of the identical request, chi2 8.9e-9 apart, one GL-mix sigma
0.544 vs 0.129 (docs/findings/runfit-certificate/data/{V3,rep_V3}_leastsq.jsonl).
Everything that is not a real number — structure, flags, ids, counts, the
seed — must be identical; non-finite values must sit in the same places.
"""
import inspect
import math
import re

import numpy as np

import fitting

SAME_MINIMUM_REL = 10 * math.sqrt(fitting.CERTIFY_FTOL)
OBJECTIVE_REL = 10 * fitting.CERTIFY_FTOL

_OBJECTIVE = ("chi_square", "reduced_chi_square", "chi2r", "not_better_chi2r")
_LOG_OBJECTIVE = ("aic", "bic")                     # n ln(chi2 / n) + 2k: an absolute difference of n x relative
_POSITIONS = ("center", "center_shift_from_start", "ev")
_PERCENTAGES = ("area_percent", "largest_fraction_difference_pp")
_SIGNAL_CURVES = ("fitted_y", "residuals", "background_y")
_NOT_COMPARED = ("message", "stderr")


def _as_curve(v):
    return np.array([np.nan if e is None else e for e in v], dtype=float)


def _curve_from_params(x, params):
    """The component's curve from its parameters alone, through the server's own lineshape
    (the one whose arguments are exactly these parameters); None if none matches."""
    keys = set(params)
    curves = []
    for func in fitting._SHAPE_FUNCS.values():
        if set(list(inspect.signature(func).parameters)[1:]) == keys:
            try:
                curves.append(np.asarray(func(np.asarray(x, float), **{k: float(v) for k, v in params.items()}), float))
            except Exception:
                continue
    return curves


def _half_max_width(x, y):
    y = np.abs(_as_curve(y))
    y = y[np.isfinite(y)]
    if not y.size or y.max() == 0:
        return None
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 1.0
    return max(int(np.count_nonzero(y >= y.max() / 2)), 1) * step


def assert_same_fit(a, b, rel=SAME_MINIMUM_REL, objective_rel=OBJECTIVE_REL):
    x = np.asarray(a["energy"], float)
    net = np.asarray(a["counts"], float) - np.asarray(a["background_y"], float)
    signal = float(np.max(np.abs(net[np.isfinite(net)]))) if np.isfinite(net).any() else 1.0
    span = float(np.ptp(x)) or 1.0
    n_data = int((a.get("statistics") or {}).get("n_data") or len(x))
    width = {}
    for pa, pb in zip(a.get("individual_peaks") or [], b.get("individual_peaks") or []):
        ws = [w for w in (_half_max_width(x, pa.get("y") or []), _half_max_width(x, pb.get("y") or [])) if w]
        width[str(pa.get("id"))] = min(ws) if ws else span
    # every fitted parameter's bounds by its lmfit name (p<id>_<name>), so a LINKED parameter
    # (expr, no bounds of its own) is judged on the span of the master it follows
    info_of = {}
    for pk in a.get("individual_peaks") or []:
        for name, info in (pk.get("params") or {}).items():
            if isinstance(info, dict):
                info_of[f"p{pk.get('id')}_{name}"] = info

    def linked_bounds(info, seen=()):
        # through a chain of links (p4_m -> p3_m -> p2_m) to the bounded master
        for ref in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", info.get("expr") or ""):   # any lmfit identifier
            master = info_of.get(ref)
            if master is None or ref in seen:
                continue
            if master.get("min") is not None and master.get("max") is not None:
                return (master["min"], master["max"])
            found = linked_bounds(master, seen + (ref,))
            if found:
                return found
        return None

    problems = []

    def curve(xs, ys, where, scale_from_self):
        A, B = _as_curve(xs), _as_curve(ys)
        if A.shape != B.shape:
            problems.append(f"{where}: length {A.size} vs {B.size}"); return
        fa, fb = np.isfinite(A), np.isfinite(B)
        if not np.array_equal(fa, fb) or not np.array_equal(A[~fa], B[~fb], equal_nan=True):
            problems.append(f"{where}: non-finite values in different places"); return
        if not fa.any():
            return
        scale = max(float(np.max(np.abs(A[fa]))), float(np.max(np.abs(B[fb])))) if scale_from_self else signal
        d = float(np.max(np.abs(A[fa] - B[fb])))
        if d > rel * scale:
            problems.append(f"{where}: differ by {d:.3g} (> {rel:g} x {scale:.3g})")

    def key_of(path):
        for p in reversed(path):
            if p != "value" and not p.isdigit():
                return p
        return ""

    def number(x_, y_, path, comp_id, bounds, widths):
        where = ".".join(path)
        if isinstance(x_, bool) or isinstance(y_, bool) or not isinstance(x_, (int, float)) or not isinstance(y_, (int, float)):
            if x_ != y_:
                problems.append(f"{where}: {x_!r} vs {y_!r}")
            return
        x_, y_ = float(x_), float(y_)
        if not (math.isfinite(x_) and math.isfinite(y_)):
            if not (x_ == y_ or (math.isnan(x_) and math.isnan(y_))):
                problems.append(f"{where}: {x_!r} vs {y_!r}")
            return
        k = key_of(path)
        if k in _OBJECTIVE:
            tol = objective_rel * max(abs(x_), abs(y_))
        elif k in _LOG_OBJECTIVE:
            tol = objective_rel * n_data
        elif k in _POSITIONS:
            tol = rel * (widths.get(comp_id) or span)
        elif k in _PERCENTAGES:
            tol = rel * 100.0
        elif bounds and bounds[0] is not None and bounds[1] is not None:
            tol = rel * abs(bounds[1] - bounds[0])          # the span alone (Codex A2 round 7: max(span, |value|) widened a narrow bound far from zero)
        else:
            tol = rel * max(abs(x_), abs(y_))
        if abs(x_ - y_) > tol:
            problems.append(f"{where}: {x_!r} vs {y_!r}")

    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 1.0

    def model_bounds(comp_id, name):
        # the model's metadata for a bare parameter value (a scattered-start alternative is the
        # same model): its bounds, or those of the bounded master it is linked to
        info = info_of.get(f"p{comp_id}_{name}")
        if info is None:
            return None
        if info.get("min") is not None and info.get("max") is not None:
            return (info["min"], info["max"])
        return linked_bounds(info) if info.get("expr") else None

    def alternative_widths(xa, xb):
        # a scattered-start alternative has no curves in the response: each component's curve
        # is evaluated from its own parameters through the server's lineshape, and its
        # half-maximum width — the returned components' definition — scales its centres; never
        # the returned fit's width (Codex A2 rounds 4-5). No matching lineshape: one grid
        # step (fails closed).
        out = {}
        for ca, cb in zip(xa.get("components") or [], xb.get("components") or []):
            ws = []
            for c in (ca, cb):
                for yc in (_curve_from_params(x, c["params"]) if isinstance(c.get("params"), dict) else []):
                    w = _half_max_width(x, yc)
                    if w:
                        ws.append(w)
            out[str(ca.get("id"))] = min(ws) if ws else step
        return out

    def cmp(x_, y_, path, comp_id=None, bounds=None, widths=None):
        widths = width if widths is None else widths
        where = ".".join(path) or "response"
        if path and path[-1] in _NOT_COMPARED:
            return
        if path[:1] == ("certificate",) and len(path) >= 2 and path[1] != "certified":
            return
        if isinstance(x_, dict) and isinstance(y_, dict):
            if set(x_) != set(y_):
                problems.append(f"{where}: keys {sorted(set(x_) ^ set(y_))}"); return
            cid = str(x_["id"]) if "id" in x_ else comp_id
            b_ = (x_.get("min"), x_.get("max")) if "value" in x_ and ("min" in x_ or "max" in x_) else None
            if b_ is not None and (b_[0] is None or b_[1] is None) and x_.get("expr"):
                b_ = linked_bounds(x_) or b_
            if len(path) >= 2 and path[-2] == "alternatives":
                widths = alternative_widths(x_, y_)
                # an alternative's component curves, evaluated from its parameters, against their
                # own height — the returned components' rule (Codex A2 round 7)
                for i, (ca, cb) in enumerate(zip(x_.get("components") or [], y_.get("components") or [])):
                    if isinstance(ca.get("params"), dict) and isinstance(cb.get("params"), dict):
                        for ya, yb in zip(_curve_from_params(x, ca["params"]), _curve_from_params(x, cb["params"])):
                            curve(list(ya), list(yb), f"{where}.components.{i}.curve", True)
            if path and path[-1] == "params" and comp_id is not None and all(not isinstance(v, dict) for v in x_.values()):
                for k in x_:                                           # bare values: the model's bounds
                    cmp(x_[k], y_[k], path + (k,), comp_id, model_bounds(comp_id, k), widths)
                return
            for k in x_:
                if k == "y" and len(path) >= 2 and path[-2] == "individual_peaks":
                    curve(x_[k], y_[k], where + ".y", True)          # a component: against its own height
                else:
                    cmp(x_[k], y_[k], path + (k,), cid, b_ if k == "value" else None, widths)
            return
        if isinstance(x_, list) and isinstance(y_, list):
            if path and path[-1] in _SIGNAL_CURVES:
                curve(x_, y_, where, False); return
            if path and path[-1] in ("energy", "counts"):
                curve(x_, y_, where, True); return
            if len(x_) != len(y_):
                problems.append(f"{where}: length {len(x_)} vs {len(y_)}"); return
            for i, (p, q) in enumerate(zip(x_, y_)):
                cmp(p, q, path + (str(i),), comp_id, None, widths)
            return
        if isinstance(x_, float) or isinstance(y_, float):
            number(x_, y_, path, comp_id, bounds, widths)
            return
        if x_ != y_:
            problems.append(f"{where}: {x_!r} vs {y_!r}")

    cmp(a, b, ())
    assert not problems, "not the same fit:\n  " + "\n  ".join(problems)
