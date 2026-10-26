"""Unit B (design + measurement only): candidate estimators of a spectrum's noise from the data alone, with no fit
model. Nothing here is used by the application. docs/findings/noise-estimator/README.md states each one's
assumptions and where it fails; scripts/noise_synthetic_benchmark.py measures them against known noise.

Every estimator takes the intensities y (in the file's own units, on an evenly stepped grid in point order) and
returns a NoiseModel: the per-point variance it implies, var(y_i), and its parameters.

Notation. s_i = the (unknown) noise-free signal; e_i = y_i − s_i the noise. "Scaled Poisson" means
var(e_i) = k · s_i for one constant k per spectrum: k = 1 for raw counts, k = 1/t for counts divided by a counting
time t (counts per second), k = 1/m for the mean of m sweeps. The estimators below replace s_i by the observed
y_i (or a local mean) where they need it, which biases them at very low counts.

MAD → σ uses the Gaussian consistency factor 1.4826 throughout; a robust scale is used so that the points on a
peak's flanks — where a difference of the SIGNAL is large — count as outliers rather than as noise.
"""
from dataclasses import dataclass, field

import numpy as np

MAD_TO_SIGMA = 1.482602218505602


def _robust_sigma(z):
    z = np.asarray(z, float)
    z = z[np.isfinite(z)]
    if z.size < 3:
        return float("nan")
    return MAD_TO_SIGMA * float(np.median(np.abs(z - np.median(z))))


# binomial difference filters of order 1, 2 and 4: each annihilates polynomials of degree below its order — a
# constant (order 1), a straight line (order 2), a cubic (order 4) of the signal does not enter the difference
DIFF = {1: np.array([-1.0, 1.0]), 2: np.array([1.0, -2.0, 1.0]), 4: np.array([1.0, -4.0, 6.0, -4.0, 1.0])}


def _normalised_differences(y, order, lag=1):
    """z_i = Σ c_j y_{i+jL} / √(Σ c_j² · max(y_{i+jL}, 1)): under scaled Poisson with independent points,
    var(z_i) ≈ k for every i (the signal's own variation aside)."""
    c = DIFF[order]
    n = len(y) - (len(c) - 1) * lag
    if n < 3:
        return np.array([])
    idx = np.arange(n)[:, None] + lag * np.arange(len(c))[None, :]
    num = (y[idx] * c).sum(axis=1)
    den = np.sqrt((np.maximum(y[idx], 1.0) * c ** 2).sum(axis=1))
    return num / den


@dataclass
class NoiseModel:
    name: str
    a: float = 0.0           # constant variance term
    k: float = 0.0           # variance per unit intensity (scaled Poisson)
    extra: dict = field(default_factory=dict)

    def variance(self, y):
        y = np.asarray(y, float)
        return self.a + self.k * np.maximum(y, 1.0)


def poisson_file_units(y):
    """What the fit assumes today (fitting.py:3006): var = max(y, 1) in the file's units — k = 1, a = 0."""
    return NoiseModel("poisson_file_units", a=0.0, k=1.0)


def scaled_poisson_differences(y, order=2, lag=1):
    """k = (robust σ of the normalised differences)². Assumes: scaled Poisson; neighbouring points independent;
    the signal's own difference small next to the noise at most points (it is annihilated up to order − 1)."""
    y = np.asarray(y, float)
    z = _normalised_differences(y, order, lag)
    return NoiseModel(f"scaled_d{order}" + (f"_lag{lag}" if lag > 1 else ""), k=_robust_sigma(z) ** 2,
                      extra={"n": int(z.size)})


def constant_differences(y, order=2, lag=1):
    """σ = robust σ of the order-N difference / √(Σ c²): ONE constant variance for the whole spectrum. Assumes the
    noise does not depend on the intensity (no shot noise) and neighbouring points are independent."""
    y = np.asarray(y, float)
    c = DIFF[order]
    n = len(y) - (len(c) - 1) * lag
    idx = np.arange(n)[:, None] + lag * np.arange(len(c))[None, :]
    d = (y[idx] * c).sum(axis=1)
    return NoiseModel(f"constant_d{order}" + (f"_lag{lag}" if lag > 1 else ""),
                      a=(_robust_sigma(d) / np.sqrt(float(np.dot(c, c)))) ** 2, k=0.0)


def der_snr(y):
    """DER_SNR (Stoehr et al. 2008, ADASS XVII): σ = 1.482602 / √6 · median |2y_i − y_{i−2} − y_{i+2}| — the
    second difference at lag 2 and the median of its absolute value (not the MAD about its median). Constant
    noise; points two apart independent (so it tolerates correlation between immediate neighbours)."""
    y = np.asarray(y, float)
    d = 2 * y[2:-2] - y[:-4] - y[4:]
    return NoiseModel("der_snr", a=(MAD_TO_SIGMA / np.sqrt(6.0) * float(np.median(np.abs(d)))) ** 2, k=0.0)


def variance_mean_regression(y, bins=12):
    """var = a + k·y: the robust variance of second differences in bins of the local mean, fitted by weighted least
    squares with a, k ≥ 0. Tests the scaled-Poisson hypothesis itself (a ≈ 0) and admits a constant (read or
    background) term. Needs a spread of intensities in the spectrum; a narrow range leaves a and k confounded.
    The local mean a difference is binned by is taken from the points JUST OUTSIDE it (y_{i−2}, y_{i+2}), not from
    the points it is made of: binning by a mean built from the same noisy points selects on the noise (for flat
    independent noise the second difference and its own weighted mean have covariance −v, and narrow bins of that
    mean pull the difference's variance from 6v towards 4v — Codex Unit B round 1). With correlated noise the
    outside points are not independent either. The weights are a heuristic (MAD-based, overlapping differences)."""
    y = np.asarray(y, float)
    d2 = (y[:-2] - 2 * y[1:-1] + y[2:])[1:-1]                 # differences centred on i = 2 … n−3
    m = (y[:-4] + y[4:]) / 2.0                                  # the local mean from y_{i−2} and y_{i+2}
    order = np.argsort(m)
    groups = [g for g in np.array_split(order, bins) if g.size >= 8]
    xs, vs, ws = [], [], []
    for g in groups:
        s = _robust_sigma(d2[g])
        if np.isfinite(s):
            xs.append(float(np.median(m[g]))); vs.append(s ** 2 / 6.0); ws.append(g.size)
    xs, vs, ws = map(np.asarray, (xs, vs, ws))
    if xs.size < 2 or np.ptp(xs) == 0:
        return NoiseModel("varmean", a=float(np.median(vs)) if vs.size else float("nan"), k=0.0, extra={"bins": int(xs.size)})
    # each bin's variance estimate has a relative error ~ 1/√(n/2): weight by n / (its expected variance)², the
    # expectation taken from the model itself (iteratively reweighted, starting from var ∝ mean) — never from the
    # bin's own estimate, which can be 0
    A = np.vstack([np.ones_like(xs), xs]).T
    expected = np.maximum(xs, 1.0)
    for _ in range(3):
        W = ws / expected ** 2
        a, k = np.linalg.lstsq(A * np.sqrt(W)[:, None], vs * np.sqrt(W), rcond=None)[0]
        if a < 0:                                               # a constrained to 0: refit k alone
            a, k = 0.0, float(np.sum(W * xs * vs) / np.sum(W * xs * xs))
        elif k < 0:
            a, k = float(np.sum(W * vs) / np.sum(W)), 0.0
        model = a + k * xs
        if not np.all(model > 0):
            break
        expected = model
    return NoiseModel("varmean", a=float(a), k=float(k), extra={"bins": int(xs.size)})


def flat_ends(y, frac=0.1):
    """k = var / mean on the first and last `frac` of the window after removing a straight line from each end
    (the approach of docs/findings/find-peaks-scale §2). Assumes both ends are free of peaks and of curvature, and
    independent points: removing a fitted line also removes part of a correlated noise (for a 24-point end with
    5-point moving-average noise the expected variance is ≈ 0.70 of the true one — Codex Unit B round 1)."""
    y = np.asarray(y, float)
    n = max(5, int(round(frac * len(y))))
    ks = []
    for seg in (y[:n], y[-n:]):
        x = np.arange(seg.size, dtype=float)
        p = np.polyfit(x, seg, 1)
        r = seg - np.polyval(p, x)
        ks.append(float(np.var(r, ddof=2) / max(np.mean(seg), 1.0)))
    return NoiseModel("flat_ends", k=float(np.mean(ks)), extra={"ends": ks})


ESTIMATORS = {
    "poisson_file_units": poisson_file_units,
    "scaled_d1": lambda y: scaled_poisson_differences(y, 1),
    "scaled_d2": lambda y: scaled_poisson_differences(y, 2),
    "scaled_d4": lambda y: scaled_poisson_differences(y, 4),
    "scaled_d2_lag3": lambda y: scaled_poisson_differences(y, 2, lag=3),
    "constant_d2": lambda y: constant_differences(y, 2),
    "constant_d4": lambda y: constant_differences(y, 4),
    "der_snr": der_snr,
    "varmean": variance_mean_regression,
    "flat_ends": flat_ends,
}


# the lag-1 correlation a difference filter c gives INDEPENDENT noise of constant variance: Σ c_j c_{j+1} / Σ c_j²
WHITE_RHO1 = {o: float(np.dot(c[:-1], c[1:]) / np.dot(c, c)) for o, c in DIFF.items()}     # −0.5, −2/3, −0.8


def _rho1(z):
    keep = np.abs(z - np.median(z)) < 4 * _robust_sigma(z)      # the peaks' flanks out, as the MAD does
    a, b = z[:-1][keep[:-1] & keep[1:]], z[1:][keep[:-1] & keep[1:]]
    return float(np.corrcoef(a, b)[0, 1]) if a.size > 3 else float("nan")


def correlation_diagnostics(y):
    """Not estimators — what the data say about whether neighbouring points are independent.
    rho1_dN = lag-1 correlation of the normalised N-th differences, against WHITE_RHO1[N] for independent points
    (−0.5 for N = 1, −0.8 for N = 4; approximate after the normalisation and the clipping); smoothing or
    interpolation CAN move it (a 3-point moving average leaves rho1_d4 at −0.8). The signal's own differences move
    it too (towards +1 where they dominate), less for higher N — so rho1_d4 is the cleaner reading.
    lag_profile = k from lag-L second differences relative to L = 1 (flat for independent noise until the signal's
    curvature lifts it; rising from L = 1 when neighbours are positively correlated)."""
    y = np.asarray(y, float)
    out = {f"rho1_d{o}": _rho1(_normalised_differences(y, o)) for o in (1, 4)}
    k1 = scaled_poisson_differences(y, 2, 1).k
    out["lag_profile"] = [scaled_poisson_differences(y, 2, L).k / k1 if k1 > 0 else float("nan") for L in (1, 2, 3, 4)]
    return out


def common_quantum(y, max_divisor=1000):
    """Is y on a grid u·ℤ for some u? Raw counts divided by a counting time t lie on u = 1/t (origin 0), and then the
    smallest gap g between sorted distinct values is m·u for the smallest count difference m among them, so every
    gap is an integer multiple of g / m. For each m = 1 … max_divisor: assign every gap and every value its nearest
    integer multiple of g / m, REFINE u by least squares from those assignments (the rounded g itself is not exact:
    its error, amplified by a gap's quotient, defeated a fixed candidate — Codex Unit B round 2), reassign, and accept
    u when every value lies within the arithmetic's own error of an integer multiple of it: the values' rounding
    (each within half an ulp of its largest magnitude) plus u's own uncertainty times the multiple. Checking the
    VALUES, not only the gaps, also refuses an offset lattice (0.2, 1.2, 2.2 has gaps of 1 but is not on 1·ℤ).
    Returns u, or None — "no quantum u ≥ g / max_divisor"; a finer quantum (a smallest count difference above
    max_divisor) cannot be told from none."""
    v = np.unique(np.asarray(y, float))
    if v.size < 3:
        return None
    gaps = np.diff(v)
    g = float(gaps.min())
    ulp = np.spacing(float(np.max(np.abs(v))))
    for m in range(1, max_divisor + 1):
        u = g / m
        for _ in range(4):                                      # assign, refine, reassign
            n = np.round(v / u)
            if not np.any(n):
                break
            u_new = float(np.dot(n, v) / np.dot(n, n))
            if u_new == u:
                break
            u = u_new
        n = np.round(v / u)
        resid = np.abs(v - n * u)
        allowed = 2 * ulp + np.abs(n) * 4 * np.spacing(u)       # value rounding + u's own rounding × the multiple
        if np.all(resid <= allowed) and np.all(n[1:] > n[:-1]):
            return u
    return None


def reduced_chi2(residual, variance, n_free):
    r = np.asarray(residual, float)
    return float(np.sum(r * r / np.asarray(variance, float)) / max(1, r.size - n_free))
