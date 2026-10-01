"""Owner item (1) ALONE, for the measurement (scripts/bg_math_impl_measure.py,
variant item1_only): main's background algorithms exactly as main runs them — its
absolute 1e-6 stop, the UPDATED iterate returned, Tougaard's convolution on grids
uniform to 1e-6 of the step, no certificate — with ONE change: endpoint averaging
sets the two edge levels only and every integral reads the raw data. Copied from
main's fitting.py (6bda9d1), not from the branch. Codex implementation round 1: the
previous "levels_abs" variant kept the branch's return-the-pre-step-point rule, which
moved backgrounds by ~1e-7 at averaging 1 and redrew request seeds."""
import numpy as np


def _levels(ys, n_avg):
    n = len(ys)
    k = max(1, min(int(n_avg), n // 4)) if n >= 4 else 1
    return float(np.mean(ys[:k])), float(np.mean(ys[-k:]))


def _asc(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return (x[::-1].copy(), y[::-1].copy(), True) if x[0] > x[-1] else (x.copy(), y.copy(), False)


def shirley_background(x, y, n_iter=200, tol=1e-6, n_avg=1):
    if len(x) < 2:
        return np.zeros_like(y)
    xs, ys, flipped = _asc(x, y)
    b_low, b_high = _levels(ys, n_avg)                      # main: ys[0], ys[-1] of the averaged DATA
    B = np.linspace(b_low, b_high, len(ys))
    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        cum_right = np.zeros(len(ys))
        for i in range(len(ys) - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = b_high + (b_low - b_high) * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break
    return B[::-1] if flipped else B


def smart_background(x, y, n_iter=200, tol=1e-6, n_avg=1):
    if len(x) < 2:
        return np.zeros_like(y)
    return np.minimum(shirley_background(x, y, n_iter, tol, n_avg=n_avg), np.asarray(y, dtype=float))


def smart_experimental_background(x, y, n_iter=200, tol=1e-6, n_avg=1):
    # main's function unchanged: it already read the levels only
    if len(x) < 2:
        return np.zeros_like(y)
    xs, ys, flipped = _asc(x, y)
    n = len(ys)
    b_low, b_high = _levels(ys, n_avg)
    step = b_low - b_high
    B = np.linspace(b_low, b_high, n)
    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(ys - B, 0.0)
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            dx = xs[i + 1] - xs[i]
            cum_right[i] = cum_right[i + 1] + (signal[i] + signal[i + 1]) / 2 * dx
        total = cum_right[0]
        if total <= 0.0:
            break
        B = b_high + step * (cum_right / total)
        B = np.minimum(B, ys)
        if np.max(np.abs(B - B_prev)) < tol:
            break
    B = np.minimum(B, ys)
    return B[::-1] if flipped else B


def shirley_linear_background(x, y, n_iter=200, tol=1e-6, n_avg=1):
    # main's function unchanged: it already read the levels only
    if len(x) < 2:
        return np.zeros_like(y)
    xs, ys, flipped = _asc(x, y)
    n = len(ys)
    IL, IH = _levels(ys, n_avg)
    linear = np.linspace(IL, IH, n)
    flat = ys - linear
    step_h = abs(IL - IH)
    if step_h < 1e-12:
        return linear[::-1] if flipped else linear
    B = np.zeros(n)
    for _ in range(n_iter):
        B_prev = B.copy()
        signal = np.maximum(flat - B, 0.0)
        cum_right = np.zeros(n)
        for i in range(n - 2, -1, -1):
            cum_right[i] = cum_right[i + 1] + 0.5 * (signal[i] + signal[i + 1]) * (xs[i + 1] - xs[i])
        total = cum_right[0]
        if total <= 0.0:
            break
        B = step_h * cum_right / total
        if np.max(np.abs(B - B_prev)) < tol:
            break
    result = np.minimum(linear + B, ys)
    return result[::-1] if flipped else result


def tougaard_background(x, y, n_avg=1):
    n = len(x)
    if n < 2:
        return np.zeros_like(y, dtype=float)
    B_coef, C_coef = 2866.0, 1643.0
    xa = np.asarray(x, dtype=float)
    ya = np.asarray(y, dtype=float)
    flipped = bool(xa[0] < xa[-1])
    if flipped:
        xa, ya = xa[::-1].copy(), ya[::-1].copy()
    a_high, c0 = _levels(ya, n_avg)                          # main: ya[0], ya[-1] of the averaged DATA
    net = ya - c0
    dx = float(abs(xa[1] - xa[0]))
    diffs = np.diff(xa)
    uniform = bool(dx > 0.0 and np.max(np.abs(diffs - diffs[0])) <= 1e-6 * dx)
    if uniform:
        m = np.arange(n, dtype=float)
        T = m * dx
        k = (B_coef * T) / (C_coef + T * T) ** 2
        bg = np.convolve(net, k[::-1])[n - 1:] * dx
    else:
        w = np.abs(np.gradient(xa))
        bg = np.zeros(n)
        for i in range(n):
            T = np.abs(xa[i:] - xa[i])
            kernel = (B_coef * T) / (C_coef + T * T) ** 2
            bg[i] = float(np.sum(kernel * net[i:] * w[i:]))
    out = np.full(n, c0) if bg[0] == 0.0 else c0 + bg * ((a_high - c0) / bg[0])
    return out[::-1] if flipped else out
