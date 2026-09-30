"""Does each background method's implementation SOLVE the problem it states?
(background math foundation, 2026-09-30; revised after Codex round 1.)

Every statement is written here INDEPENDENTLY of fitting.py — its own endpoint
preprocessing, its own integrals, its own reference solver — and evaluated on the
method's output with the method's OWN reading of endpoint averaging:

  reading "data"   the first / last n_avg points of the DATA are replaced by their
                   mean before anything else (shirley, smart's integrand, tougaard,
                   shirley_linear's integrand)
  reading "levels" only the two edge LEVELS are read as those means; the relation
                   integrates the measured data (smart_exp)

Statements (T the discrete Shirley map, trapezoid rule, ascending grid,
T(B)_i = b_low + (b_high - b_low) Q_i / Q_n, Q_i = INT_{x_0}^{x_i} max(D - B, 0),
D the data under the method's reading):
  shirley         B = T(B)
  smart           B = min(T(B), I)            (constrained Shirley)
  smart_exp       B = min(T(B), I)
  shirley_linear  B = min(L + (b_high - b_low)... ) — see shirley_linear_residual
  linear          B affine in E through the raw end points
  tougaard        B = C0 + lam SUM_{E' <= E} K(E - E') (D(E') - C0) w(E'), lam from B(E_high) = D(E_high)
  manual          piecewise-affine through the anchors, constant outside

The Shirley relation can have MORE THAN ONE solution (Codex round 1: 4-point
spectra with a family of exact solutions); nothing here claims uniqueness. The
reference solver reports convergence only when the RETURNED point satisfies the
statement (finite residual <= REF_TOL of the span).

Usage: python scripts/background_defining_statements.py OUT.jsonl
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import fitting  # noqa: E402

REF_TOL = 1e-13          # a reference solution's residual, of the span
KB, KC = 2866.0, 1643.0  # Tougaard universal cross-section coefficients (eV^2)


# ── preprocessing (independent) ──────────────────────────────────────────────

def band(n, n_avg):
    """How many edge points an average of n_avg reads (production's rule: at most n//4)."""
    return max(1, min(int(n_avg), n // 4)) if n >= 4 else 1


def replace_end_bands(y, n_avg):
    """reading "data": the first / last band of the data replaced by its mean (n_avg > 1, n >= 4)."""
    y = np.asarray(y, float).copy()
    n = len(y)
    if n_avg <= 1 or n < 4:
        return y
    k = min(int(n_avg), n // 4)
    if k < 1:
        return y
    y[:k], y[-k:] = y[:k].mean(), y[-k:].mean()
    return y


def ascending(x, *arrays):
    x = np.asarray(x, float)
    flip = bool(x[0] > x[-1])
    out = [x[::-1].copy() if flip else x.copy()]
    for a in arrays:
        a = np.asarray(a, float)
        out.append(a[::-1].copy() if flip else a.copy())
    return flip, out


def reading(x, y, n_avg, how):
    """(ascending x, data D under the reading, raw y, b_low, b_high, flip)."""
    flip, (xa, ya) = ascending(x, y)
    if how == "data":
        D = replace_end_bands(ya, n_avg)
        return xa, D, ya, float(D[0]), float(D[-1]), flip
    k = band(len(ya), n_avg)
    return xa, ya.copy(), ya, float(ya[:k].mean()), float(ya[-k:].mean()), flip


def span_of(y):
    y = np.asarray(y, float)
    return float(np.max(y) - np.min(y)) or 1.0


# ── the Shirley map and its statements ───────────────────────────────────────

def shirley_map(xa, D, B, b_low, b_high):
    s = np.maximum(D - B, 0.0)
    Q = np.concatenate([[0.0], np.cumsum(0.5 * (s[:-1] + s[1:]) * np.diff(xa))])
    if not Q[-1] > 0.0:
        return None                                   # the relation is undefined: no net signal
    return b_low + (b_high - b_low) * Q / Q[-1]


def _res(a, b, sp):
    if b is None or not np.all(np.isfinite(b)) or not np.all(np.isfinite(a)):
        return float("inf")
    return float(np.max(np.abs(a - b)) / sp)


def shirley_residual(x, y, B, n_avg=1, how="data"):
    """max |B - T(B)| / span under the reading `how`; inf where the relation is undefined."""
    xa, D, ya, bl, bh, flip = reading(x, y, n_avg, how)
    Ba = np.asarray(B, float)[::-1] if flip else np.asarray(B, float)
    return _res(Ba, shirley_map(xa, D, Ba, bl, bh), span_of(ya))


def constrained_residual(x, y, B, n_avg=1, how="levels"):
    """B = min(T(B), I) (I the RAW data: every implementation clamps against it) under the
    reading `how` for the integrand. Returns (residual, violation of B <= I, fraction active)."""
    xa, D, ya, bl, bh, flip = reading(x, y, n_avg, how)
    Ba = np.asarray(B, float)[::-1] if flip else np.asarray(B, float)
    sp = span_of(ya)
    T = shirley_map(xa, D, Ba, bl, bh)
    res = _res(Ba, None if T is None else np.minimum(T, ya), sp)
    return res, float(max(0.0, np.max(Ba - ya)) / sp), float(np.mean(Ba >= ya))


def solve(x, y, n_avg=1, how="levels", constrained=False, B0=None, max_iter=100000):
    """The reference solution: fixed-point iteration of the statement from B0 (default the
    line between the edge levels) until the RETURNED point's residual is <= REF_TOL of the
    span. Returns (B in the input order, iterations, converged, residual)."""
    xa, D, ya, bl, bh, flip = reading(x, y, n_avg, how)
    sp = span_of(ya)
    B = np.linspace(bl, bh, len(ya)) if B0 is None else (np.asarray(B0, float)[::-1] if flip else np.asarray(B0, float)).copy()
    res = float("inf")
    for k in range(1, max_iter + 1):
        T = shirley_map(xa, D, B, bl, bh)
        if T is None:
            break
        Bn = np.minimum(T, ya) if constrained else T
        B = Bn
        T2 = shirley_map(xa, D, B, bl, bh)
        res = _res(B, None if T2 is None else (np.minimum(T2, ya) if constrained else T2), sp)
        if res <= REF_TOL:
            break
    out = B[::-1] if flip else B
    return out, k, bool(res <= REF_TOL), res


def net_area(x, y, B):
    return float(abs(np.trapezoid(np.asarray(y, float) - np.asarray(B, float), np.asarray(x, float))))


# ── shirley_linear ───────────────────────────────────────────────────────────

def shirley_linear_residual(x, y, B, n_avg=1):
    """Its statement (Codex round 1): B = min(L + d (1 - F(B)), I), L the line between the
    averaged edge levels AFFINE IN THE POINT INDEX (as the implementation draws it; Codex
    round 2), d = |b_low - b_high|, F the cumulative fraction of max(I - B, 0)
    from the low-BE edge. Returns (residual, low-edge excess of the unclamped curve / span,
    high-edge mismatch of the unclamped curve / span, fraction clamped)."""
    flip, (xa, ya, Ba) = ascending(x, y, B)
    k = band(len(ya), n_avg)
    bl, bh = float(ya[:k].mean()), float(ya[-k:].mean())
    sp = span_of(ya)
    L = np.linspace(bl, bh, len(ya))
    d = abs(bl - bh)
    s = np.maximum(ya - Ba, 0.0)
    Q = np.concatenate([[0.0], np.cumsum(0.5 * (s[:-1] + s[1:]) * np.diff(xa))])
    if not Q[-1] > 0:
        return float("inf"), None, None, float(np.mean(Ba >= ya))
    U = L + d * (1.0 - Q / Q[-1])
    return (_res(Ba, np.minimum(U, ya), sp), float((U[0] - bl) / sp), float(abs(U[-1] - bh) / sp),
            float(np.mean(Ba >= ya)))


# ── linear, manual ───────────────────────────────────────────────────────────

def linear_residual(x, y, B):
    x, y, B = (np.asarray(v, float) for v in (x, y, B))
    line = y[0] + (y[-1] - y[0]) * (x - x[0]) / (x[-1] - x[0])
    return float(np.max(np.abs(B - line)) / span_of(y))


def manual_reference(x, anchors):
    a = sorted(anchors, key=lambda p: p[0])
    ax, ay = np.array([p[0] for p in a], float), np.array([p[1] for p in a], float)
    out = np.empty(len(x))
    for i, e in enumerate(np.asarray(x, float)):
        if e <= ax[0]:
            out[i] = ay[0]
        elif e >= ax[-1]:
            out[i] = ay[-1]
        else:
            j = int(np.searchsorted(ax, e) - 1)
            out[i] = ay[j] + (e - ax[j]) / (ax[j + 1] - ax[j]) * (ay[j + 1] - ay[j])
    return out


# ── tougaard (independent) ───────────────────────────────────────────────────

def _desc(x, y, n_avg, how):
    xa, ya = np.asarray(x, float), np.asarray(y, float)
    flip = bool(xa[0] < xa[-1])
    if flip:
        xa, ya = xa[::-1].copy(), ya[::-1].copy()
    if how == "data":
        D = replace_end_bands(ya, n_avg)
        return xa, D, float(D[-1]), float(D[0]), flip       # C0 at the low-BE edge (index -1), anchor at index 0
    k = band(len(ya), n_avg)
    return xa, ya.copy(), float(ya[-k:].mean()), float(ya[:k].mean()), flip


def _weights(xa):
    n = len(xa)
    w = np.empty(n)
    w[0], w[-1] = abs(xa[1] - xa[0]), abs(xa[-1] - xa[-2])
    w[1:-1] = np.abs(xa[2:] - xa[:-2]) / 2.0
    return w


def tougaard_loss(x, y, n_avg=1, how="data", kernel=None):
    """The loss integral SUM_{j >= i} K(|x_j - x_i|) (D_j - C0) w_j on the descending grid
    (independent double sum). Returns (loss, xa, D, C0, D_high, flip)."""
    xa, D, c0, dhi, flip = _desc(x, y, n_avg, how)
    K = kernel or (lambda T: KB * T / (KC + T * T) ** 2)
    w = _weights(xa)
    net = D - c0
    loss = np.array([float(np.sum(K(np.abs(xa[i:] - xa[i])) * net[i:] * w[i:])) for i in range(len(xa))])
    return loss, xa, D, c0, dhi, flip


def tougaard_statement(x, y, n_avg=1, how="data", kernel=None):
    """The Tougaard statement's solution. When the discrete loss sum at the high-BE edge is
    zero the anchor does not fix lam (Codex rounds 2-3): with equal anchor levels (D_high = C0)
    the solutions form a family, one per lam, and its lam = 0 member, the flat C0, is returned
    (every member is flat only when the whole loss vector vanishes); with unequal levels there
    is no solution and None is returned."""
    loss, xa, D, c0, dhi, flip = tougaard_loss(x, y, n_avg, how, kernel)
    if loss[0] == 0.0:
        return np.full(len(xa), c0) if dhi == c0 else None
    out = c0 + loss * ((dhi - c0) / loss[0])
    return out[::-1] if flip else out


def tougaard_refined(x, y, n_avg=1, how="data", factor=10):
    """The same statement with the integral on a grid `factor` times finer (D linearly
    interpolated), sampled back — independent of fitting.py."""
    xa, D, c0, dhi, flip = _desc(x, y, n_avg, how)
    fine = np.linspace(xa[0], xa[-1], (len(xa) - 1) * factor + 1)
    Df = np.interp(fine[::-1], xa[::-1], D[::-1])[::-1]
    w = _weights(fine)
    net = Df - c0
    loss = np.array([float(np.sum(KB * np.abs(fine[i:] - fine[i]) / (KC + (fine[i:] - fine[i]) ** 2) ** 2 * net[i:] * w[i:]))
                     for i in range(len(fine))])
    if loss[0] == 0.0:
        return None
    Bf = c0 + loss * ((dhi - c0) / loss[0])
    back = np.interp(xa[::-1], fine[::-1], Bf[::-1])[::-1]
    return back[::-1] if flip else back


def tougaard_beyond_peak_fraction(x, y, n_avg=1):
    """The share of the high-BE edge's loss integral that comes from losses beyond the
    kernel's maximum, T > sqrt(C/3)."""
    xa, D, c0, dhi, flip = _desc(x, y, n_avg, "data")
    T = np.abs(xa - xa[0])
    f = KB * T / (KC + T * T) ** 2 * (D - c0) * _weights(xa)
    tot = float(np.sum(f))
    return float(np.sum(f[T > np.sqrt(KC / 3)]) / tot) if tot else None


# ── the corpus measurement ───────────────────────────────────────────────────

def measure(rf):
    i0, i1 = rf.bg_indices()
    x = np.asarray(rf.roi_be, float)[i0:i1]
    y = np.asarray(rf.roi_intensity, float)[i0:i1]
    ep = int(rf.endpoint_avg or 1)
    sp = span_of(y)
    rec = {"project": rf.project, "tab": rf.name, "saved_method": rf.bg_method, "n": len(x), "endpoint_avg": ep, "span": sp,
           "window_ev": float(abs(x[-1] - x[0]))}

    # shirley: its own reading ("data")
    Bs = fitting.shirley_background(x, y, n_avg=ep)
    ref, k, ok, rres = solve(x, y, ep, "data")
    alt1, _, ok1, _ = solve(x, y, ep, "data", B0=np.full(len(y), float(np.min(y))))
    rec["shirley"] = {"residual": shirley_residual(x, y, Bs, ep, "data"), "ref_iters": k, "ref_converged": ok,
                      "vs_ref": _res(Bs, ref, sp), "second_start_agrees": _res(ref, alt1, sp) if ok1 else None,
                      "exceeds_data": float(max(0.0, np.max(Bs - y)) / sp), "exceeds_fraction": float(np.mean(Bs > y)),
                      "first_step_undefined": shirley_map(*[reading(x, y, ep, "data")[i] for i in (0, 1)],
                                                          np.linspace(*[reading(x, y, ep, "data")[i] for i in (3, 4)], len(y)),
                                                          *[reading(x, y, ep, "data")[i] for i in (3, 4)]) is None}
    B5 = fitting.shirley_background(x, y, n_iter=5, n_avg=ep)                  # F7: the page's preview default, same reading
    rec["shirley_5_iter"] = {"vs_converged": _res(B5, Bs, sp), "net_area_pct": 100 * (net_area(x, y, B5) - net_area(x, y, Bs)) / net_area(x, y, Bs)}
    rec["shirley_units"] = {}
    for scale in (1e-3, 1e-6):                                                  # F5: the absolute stop, same reading
        Bsc = fitting.shirley_background(x, y * scale, n_avg=ep)
        refc, _, okc, _ = solve(x, y * scale, ep, "data")
        rec["shirley_units"][str(scale)] = {"vs_ref": _res(Bsc, refc, span_of(y * scale)) if okc else None,
                                            "net_area_pct": 100 * (net_area(x, y * scale, Bsc) - net_area(x, y * scale, refc)) / net_area(x, y * scale, refc)}

    # F1: the two readings of endpoint averaging, each reading's own reference
    refL, _, okL, _ = solve(x, y, ep, "levels")
    rec["F1_shirley_readings"] = {"vs": _res(ref, refL, sp), "net_area_pct": 100 * (net_area(x, y, ref) - net_area(x, y, refL)) / net_area(x, y, refL)}

    # smart (integrand "data", clamp raw) and smart_exp ("levels", clamp raw)
    for name, fn, how in (("smart", fitting.smart_background, "data"), ("smart_exp", fitting.smart_experimental_background, "levels")):
        B = fn(x, y, n_avg=ep)
        res, viol, act = constrained_residual(x, y, B, ep, how)
        rec[name] = {"residual": res, "violation": viol, "active_fraction": act}
    Bm, Be = fitting.smart_background(x, y, n_avg=ep), fitting.smart_experimental_background(x, y, n_avg=ep)
    rec["smart_vs_smart_exp"] = {"vs": _res(Bm, Be, sp), "net_area_pct": 100 * (net_area(x, y, Bm) - net_area(x, y, Be)) / net_area(x, y, Be)}
    cref, _, cok, _ = solve(x, y, ep, "levels", constrained=True)
    rec["constrained_vs_unconstrained"] = {"net_area_pct": 100 * (net_area(x, y, cref) - net_area(x, y, refL)) / net_area(x, y, refL),
                                           "converged": bool(cok and okL)}

    # linear
    rec["linear"] = {"residual": linear_residual(x, y, fitting.linear_background(x, y))}

    # tougaard: its own reading ("data"), independent integral, anchor, refinement, kernel sensitivity
    Bt = fitting.tougaard_background(x, y, n_avg=ep)
    st = tougaard_statement(x, y, ep, "data")
    rf10 = tougaard_refined(x, y, ep, "data")
    lin = tougaard_statement(x, y, ep, "data", kernel=lambda T: T / KC ** 2)   # the small-loss linear kernel
    _, _, D, c0, dhi, flip = tougaard_loss(x, y, ep, "data")
    hi = Bt[-1] if flip else Bt[0]
    rec["tougaard"] = {"residual": _res(Bt, st, sp), "anchor_miss": float(abs(hi - dhi) / sp),
                       "discretisation_refined": _res(Bt, rf10, sp),
                       "net_area_vs_refined_pct": 100 * (net_area(x, y, Bt) - net_area(x, y, rf10)) / net_area(x, y, rf10) if rf10 is not None else None,
                       "beyond_kernel_peak_fraction": tougaard_beyond_peak_fraction(x, y, ep),
                       "linear_kernel_vs": _res(Bt, lin, sp),
                       "F1_readings_vs": _res(st, tougaard_statement(x, y, ep, "levels"), sp)}

    # shirley_linear
    Bsl = fitting.shirley_linear_background(x, y, n_avg=ep)
    r, lo, hi_m, cf = shirley_linear_residual(x, y, Bsl, ep)
    rec["shirley_linear"] = {"residual": r, "low_edge_excess": lo, "high_edge_mismatch": hi_m, "clamped_fraction": cf}
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
