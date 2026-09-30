"""Does each background method's implementation SOLVE the problem it claims to?
(background math foundation, 2026-09-30.)

For every method in fitting.py the defining statement is written out here as
an independent check — never by calling the method's own loop — and evaluated
on the method's output:

  shirley   B = T(B)                          (the Shirley integral relation)
  smart     B = min(T(B), y)                  (constrained Shirley: B <= y, and
                                               the relation holds wherever the
                                               constraint is not active)
  smart_exp B = min(T(B), y)                  (the same constrained problem)
  linear    B affine in E through the two endpoint levels
  tougaard  B = C0 + lam * sum K(E - E') (J(E') - C0) dE' over E' < E,
            lam fixed by B(E_high) = J(E_high)
  manual    B piecewise-affine through the anchors, constant outside
  shirley_linear — has no defining statement (see the findings); checked
            against the two conditions any background must meet at a flat
            window edge instead.

T is the discrete Shirley map on an ascending grid, trapezoid quadrature:
  T(B)_i = b_low + (b_high - b_low) * Q_i / Q_n,
  Q_i = sum_{k<i} (s_k + s_{k+1})/2 (x_{k+1} - x_k),   s = max(y - B, 0),
with b_low / b_high the endpoint levels (the mean of the first / last
min(n_avg, n//4) points, as the implementations read them).

Residuals are relative to the data's span, max(y) - min(y).

Usage: python scripts/background_defining_statements.py OUT.jsonl
  (every committed spectrum in docs/autofit/test_data/*.proj.zip, every method)
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import fitting  # noqa: E402


def ascending(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x[0] > x[-1]:
        return x[::-1].copy(), y[::-1].copy(), True
    return x.copy(), y.copy(), False


def endpoint_levels(y_asc, n_avg):
    n = len(y_asc)
    cap = max(1, min(int(n_avg), n // 4)) if n >= 4 else 1
    return float(np.mean(y_asc[:cap])), float(np.mean(y_asc[-cap:]))


def shirley_map(x_asc, y_asc, B, b_low, b_high):
    """T(B): the discrete Shirley relation's right-hand side (independent of fitting.py)."""
    s = np.maximum(y_asc - B, 0.0)
    seg = 0.5 * (s[:-1] + s[1:]) * np.diff(x_asc)
    Q = np.concatenate([[0.0], np.cumsum(seg)])          # Q_i = integral from x_0 to x_i
    total = Q[-1]
    if total <= 0.0:
        return np.full_like(B, np.nan)
    return b_low + (b_high - b_low) * Q / total


def span_of(y):
    y = np.asarray(y, float)
    return float(np.max(y) - np.min(y)) or 1.0


def _asc_B(B, flip):
    B = np.asarray(B, float)
    return B[::-1] if flip else B


def shirley_residual(x, y, B, n_avg=1):
    """max |B - T(B)| / span: the unconstrained Shirley relation."""
    xa, ya, flip = ascending(x, y)
    Ba = _asc_B(B, flip)
    bl, bh = endpoint_levels(ya, n_avg)
    T = shirley_map(xa, ya, Ba, bl, bh)
    return float(np.max(np.abs(Ba - T)) / span_of(ya))


def constrained_residual(x, y, B, n_avg=1):
    """The constrained Shirley problem, B = min(T(B), y): at every point either
    the relation holds (B = T(B) <= y) or the constraint is active (B = y and
    T(B) >= y). Returns (residual, violation of B <= y, fraction active)."""
    xa, ya, flip = ascending(x, y)
    Ba = _asc_B(B, flip)
    bl, bh = endpoint_levels(ya, n_avg)
    T = shirley_map(xa, ya, Ba, bl, bh)
    sp = span_of(ya)
    res = float(np.max(np.abs(Ba - np.minimum(T, ya))) / sp)
    viol = float(max(0.0, np.max(Ba - ya)) / sp)
    active = float(np.mean(Ba >= ya))
    return res, viol, active


def _fixed_point(x, y, n_avg, project, B0=None, max_iter=200000):
    xa, ya, flip = ascending(x, y)
    bl, bh = endpoint_levels(ya, n_avg)
    B = np.linspace(bl, bh, len(ya)) if B0 is None else _asc_B(B0, flip).copy()
    stop = 64 * np.finfo(float).eps * max(span_of(ya), float(np.max(np.abs(ya))))
    for k in range(1, max_iter + 1):
        T = shirley_map(xa, ya, B, bl, bh)
        if not np.all(np.isfinite(T)):
            return _asc_B(B, flip), k, False
        Bn = np.minimum(T, ya) if project else T
        d = float(np.max(np.abs(Bn - B)))
        B = Bn
        if d <= stop:
            return _asc_B(B, flip), k, True
    return _asc_B(B, flip), max_iter, False


def constrained_solution(x, y, n_avg=1, B0=None, max_iter=200000):
    """The constrained Shirley problem solved to a fixed point by the projected
    iteration B <- min(T(B), y), until the change is at rounding level.
    Independent of fitting.py. Returns (B, iterations, converged)."""
    return _fixed_point(x, y, n_avg, True, B0, max_iter)


def unconstrained_solution(x, y, n_avg=1, max_iter=200000):
    """The Shirley relation B = T(B) iterated to a fixed point (independent)."""
    return _fixed_point(x, y, n_avg, False, None, max_iter)


def net_area(x, y, B):
    return float(abs(np.trapezoid(np.asarray(y, float) - np.asarray(B, float), np.asarray(x, float))))


def linear_residual(x, y, B):
    """B affine in E through (E_first, y_first) and (E_last, y_last) — raw endpoints, as
    fitting.linear_background reads them (it takes no endpoint averaging)."""
    x, y, B = (np.asarray(v, float) for v in (x, y, B))
    line = y[0] + (y[-1] - y[0]) * (x - x[0]) / (x[-1] - x[0])
    return float(np.max(np.abs(B - line)) / span_of(y))


def tougaard_reference(x, y, n_avg=1, rule="rectangle"):
    """The Tougaard statement evaluated by an explicit double sum (independent of the
    implementation's convolution): C0 = the averaged low-BE edge level, the loss integral
    over lower-BE emitters of K(T) (J - C0), lam from B(E_high) = J(E_high).
    rule "rectangle" is the implementation's quadrature (sum K * net * w); "trapezoid"
    integrates the same integrand by the trapezoid rule — their difference estimates the
    discretisation error of the integral relation itself."""
    xa, ya = np.asarray(x, float), np.asarray(y, float)
    if n_avg > 1:
        ya = fitting._apply_endpoint_averaging(ya, n_avg)
    flip = bool(xa[0] < xa[-1])
    if flip:
        xa, ya = xa[::-1].copy(), ya[::-1].copy()
    Bk, Ck = 2866.0, 1643.0
    c0 = float(ya[-1])
    net = ya - c0
    n = len(xa)
    bg = np.zeros(n)
    w = np.abs(np.gradient(xa))
    for i in range(n):
        T = np.abs(xa[i:] - xa[i])
        f = (Bk * T) / (Ck + T * T) ** 2 * net[i:]
        bg[i] = float(np.sum(f * w[i:])) if rule == "rectangle" else (float(np.trapezoid(f, T)) if len(T) > 1 else 0.0)
    out = np.full(n, c0) if bg[0] == 0.0 else c0 + bg * ((float(ya[0]) - c0) / bg[0])
    return out[::-1] if flip else out


def tougaard_refined(x, y, n_avg=1, factor=10):
    """The Tougaard integral relation evaluated on a grid `factor` times finer (J linearly
    interpolated), with the same C0 and high-BE anchor, sampled back at the data points:
    its difference from the implementation estimates the discretisation error of the
    integral relation on the data's own grid."""
    xa, ya = np.asarray(x, float), np.asarray(y, float)
    if n_avg > 1:
        ya = fitting._apply_endpoint_averaging(ya, n_avg)
    asc = xa[0] < xa[-1]
    xs, ys = (xa, ya) if asc else (xa[::-1], ya[::-1])
    fine = np.linspace(xs[0], xs[-1], (len(xs) - 1) * factor + 1)
    yf = np.interp(fine, xs, ys)
    out_f = fitting.tougaard_background(fine, yf, n_avg=1)
    back = np.interp(xs, fine, out_f)
    return back if asc else back[::-1]


def manual_reference(x, anchors):
    """Piecewise-affine through the anchors (sorted by energy), constant outside."""
    a = sorted(anchors, key=lambda p: p[0])
    ax, ay = np.array([p[0] for p in a], float), np.array([p[1] for p in a], float)
    out = np.empty(len(x))
    for i, e in enumerate(np.asarray(x, float)):
        if e <= ax[0]:
            out[i] = ay[0]
        elif e >= ax[-1]:
            out[i] = ay[-1]
        else:
            k = int(np.searchsorted(ax, e) - 1)
            out[i] = ay[k] + (e - ax[k]) / (ax[k + 1] - ax[k]) * (ay[k + 1] - ay[k])
    return out


def edge_conditions(x, y, B, n_avg=1):
    """What any background must meet at a flat window edge: B equals the edge level at
    both ends. Returns the larger mismatch / span, and the fraction of points where the
    result equals the data (a clamp was active)."""
    xa, ya, flip = ascending(x, y)
    Ba = _asc_B(B, flip)
    bl, bh = endpoint_levels(ya, n_avg)
    sp = span_of(ya)
    return float(max(abs(Ba[0] - bl), abs(Ba[-1] - bh)) / sp), float(np.mean(Ba >= ya))


def measure(rf):
    i0, i1 = rf.bg_indices()
    x = np.asarray(rf.roi_be, float)[i0:i1]
    y = np.asarray(rf.roi_intensity, float)[i0:i1]
    ep = int(rf.endpoint_avg or 1)
    sp = span_of(y)
    rec = {"project": rf.project, "tab": rf.name, "saved_method": rf.bg_method, "n": len(x), "endpoint_avg": ep, "span": sp}
    Bs = fitting.shirley_background(x, y, n_avg=ep)
    Bu, ku, oku = unconstrained_solution(x, y, ep)
    rec["shirley"] = {"residual": shirley_residual(x, y, Bs, ep), "exceeds_data": float(max(0.0, np.max(Bs - y)) / sp),
                      "exceeds_fraction": float(np.mean(Bs > y)),
                      "vs_fixed_point": float(np.max(np.abs(Bs - Bu)) / sp), "fixed_point_iters": ku, "fixed_point_ok": oku}
    B5 = fitting.shirley_background(x, y, n_iter=5, n_avg=ep)       # the page's drawing default
    rec["shirley_5_iter"] = {"residual": shirley_residual(x, y, B5, ep), "vs_fixed_point": float(np.max(np.abs(B5 - Bu)) / sp),
                             "net_area_pct": 100 * (net_area(x, y, B5) - net_area(x, y, Bu)) / max(net_area(x, y, Bu), 1e-300)}
    Bc, kc, okc = constrained_solution(x, y, ep)
    Bc2, _, _ = constrained_solution(x, y, ep, B0=np.minimum(Bu, y))
    A_true = net_area(x, y, Bc)
    for name, fn in (("smart", fitting.smart_background), ("smart_exp", fitting.smart_experimental_background)):
        B = fn(x, y, n_avg=ep)
        res, viol, act = constrained_residual(x, y, B, ep)
        rec[name] = {"residual": res, "violation": viol, "active_fraction": act,
                     "vs_true_constrained": float(np.max(np.abs(B - Bc)) / sp),
                     "net_area_vs_true_pct": 100 * (net_area(x, y, B) - A_true) / max(A_true, 1e-300)}
    rec["true_constrained"] = {"iters": kc, "converged": okc, "active_fraction": float(np.mean(Bc >= y)),
                               "start_independent": float(np.max(np.abs(Bc - Bc2)) / sp),
                               "residual": constrained_residual(x, y, Bc, ep)[0],
                               "net_area_vs_unconstrained_pct": 100 * (A_true - net_area(x, y, Bu)) / max(net_area(x, y, Bu), 1e-300)}
    rec["linear"] = {"residual": linear_residual(x, y, fitting.linear_background(x, y))}
    Bt = fitting.tougaard_background(x, y, n_avg=ep)
    ref, trap = tougaard_reference(x, y, ep, "rectangle"), tougaard_reference(x, y, ep, "trapezoid")
    rec["tougaard"] = {"residual": float(np.max(np.abs(Bt - ref)) / sp),
                       "discretisation_refined": float(np.max(np.abs(Bt - tougaard_refined(x, y, ep))) / sp),
                       "net_area_vs_refined_pct": 100 * (net_area(x, y, Bt) - net_area(x, y, tougaard_refined(x, y, ep))) / max(net_area(x, y, tougaard_refined(x, y, ep)), 1e-300),
                       "window_ev": float(abs(x[-1] - x[0])), "kernel_peak_ev": float(np.sqrt(1643.0 / 3))}
    # endpoint averaging: shirley integrates the endpoint-averaged DATA; smart_exp averages only
    # the edge LEVELS and integrates the measured data (B_u is that reading's fixed point)
    rec["shirley_endpoint_reading"] = {"net_area_pct": 100 * (net_area(x, y, Bs) - net_area(x, y, Bu)) / max(net_area(x, y, Bu), 1e-300)}
    # start-independence of the unconstrained relation (a second start: the data themselves)
    Bu2, _, _ = _fixed_point(x, y, ep, False, B0=np.full(len(y), float(np.min(y))))   # a start below the data (B0 = y leaves no net signal)
    rec["shirley"]["start_independent"] = float(np.max(np.abs(Bu - Bu2)) / sp)
    # the absolute 1e-6-count stop under a change of units
    rec["shirley_units"] = {}
    for scale in (1e-3, 1e-6):
        Bsc = fitting.shirley_background(x, y * scale, n_avg=ep)
        Buc, _, _ = unconstrained_solution(x, y * scale, ep)
        rec["shirley_units"][str(scale)] = {"vs_fixed_point": float(np.max(np.abs(Bsc - Buc)) / span_of(y * scale)),
                                            "net_area_pct": 100 * (net_area(x, y * scale, Bsc) - net_area(x, y * scale, Buc)) / max(net_area(x, y * scale, Buc), 1e-300)}
    Bsl = fitting.shirley_linear_background(x, y, n_avg=ep)
    xa, ya, _ = ascending(x, y)
    bl, bh = endpoint_levels(ya, ep)
    em, cf = edge_conditions(x, y, Bsl, ep)
    rec["shirley_linear"] = {"edge_mismatch": em, "clamped_fraction": cf,
                             "unclamped_low_edge_above_level_over_span": float(abs(bl - bh) / sp)}
    return rec


def main(out):
    from autofit.reference import load_reference_fits
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "autofit", "test_data")
    with open(out, "w") as f:
        for zp in sorted(glob.glob(os.path.join(here, "*.proj.zip"))):
            for rf in load_reference_fits(zp):
                f.write(json.dumps(measure(rf)) + "\n")
                f.flush()


if __name__ == "__main__":
    main(sys.argv[1])
