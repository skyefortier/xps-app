"""The envelope is the background plus the sum of its components — to rounding.

Owner 2026-10-10 (after the 2026-09-17 report of an envelope above the sum of its
components on a UCl4 spectrum: the page's asym-GL had been drawn with a different width
than the server fitted, fixed in cf4938d on 2026-08-31). Shared by the server tests
(tests/test_envelope_identity.py) and the page tests
(tests/test_browser_envelope_identity.py).

THE BOUND, point by point, for curves made by ONE implementation (the server's arrays; the
page's own composed envelope after an edit): the envelope e and our sum s = b + Σ c_k are each
a sum of the same n + 1 terms, added in some order: each within γ_n · S of the exact sum,
S = |b| + Σ |c_k| (Higham, recursive summation). So |e − s| ≤ 2 γ_n S ≤ 4 (n + 2) u S, with
margin for the component-plus-background additions and subtractions of the page's drawn
datasets (one more rounding per term), for n ≤ 2^20. A component evaluated twice by the same
code on the same values gives the same bits, except where its evaluation contains a reduction
whose order the library may change with memory alignment — the server's LA (`np.convolve`,
a BLAS dot: CLAUDE.md "Reproducibility"). For it, `conv_term`: the convolution's terms are all
non-negative (a positive Lorentzian core, a positive Gaussian kernel), so a dot of K terms is
within γ_K of its own value, and the normalisation by the curve's (equally computed) value at
the centre adds that value's γ_K (to first order — the quotient's exact factor is
(1 + θ1)/(1 + θ2), |θ| ≤ γ_K): each evaluation within 2 γ_K |c| to first order, two
evaluations 4 γ_K |c| (exactly, two normalised evaluations differ by at most
4 γ_K / (1 − γ_K)² |c|), K = 2 max(1, ⌈3.5 m / 3⌉) + 1 (the kernel length, F `_la_casaxps_true`).
What that leaves out — the second-order part of the quotient, the division and the final
multiplication by the amplitude, a few u |c| in all (Codex round 2: ≈ 4.0000000013 u |c| at the
largest K, 1167) — is covered by the summation term's own margin: 4 (n + 2) u S against the
2 γ_n S the sums need (≈ 2 n u S) leaves (2 n + 8) u S ≥ 10 u S ≥ 10 u |c| per point for
every n ≥ 1.

NOT a rounding bound: the page's DRAWN components after a server fit are the page's own
(JavaScript) evaluators, not the server's arrays; two implementations of a transcendental
formula agree to a shape-, argument- and library-dependent accuracy for which no general
derivation is offered here. The page tests therefore split the drawn identity into parts that
each have a proper check: the drawn envelope IS the server's fitted_y and the drawn background
IS the server's background_y (exactly), the server's own identity holds (this bound), and each
drawn component equals the server's component curve within the project's page-server PARITY
tolerance (tests/js/lineshape_roundtrip.test.js TIGHT_TOL, 1e-6 of the component's amplitude) —
named as parity, not rounding."""
import numpy as np

U = 2.0 ** -53


def conv_term(curve, m):
    """4 γ_K |c| for an LA component with kernel parameter m (data points): see the module
    docstring. m = 0 is no convolution (0)."""
    if m <= 0:
        return np.zeros_like(np.asarray(curve, float))
    K = 2 * max(1, int(np.ceil(3.5 * m / 3))) + 1
    return 4 * K * U / (1 - K * U) * np.abs(np.asarray(curve, float))


def envelope_gap(envelope, background, components, extra=0.0):
    """Largest |e − (b + Σ c)| / (4 (n + 2) u S + extra) over the points: ≤ 1 means within
    rounding (`extra`: an LA component's conv_term, point by point). Also returns the largest gap
    relative to max |e| (for reporting)."""
    e = np.asarray(envelope, float)
    b = np.asarray(background, float)
    cs = [np.asarray(c, float) for c in components]
    assert e.shape == b.shape and all(c.shape == e.shape for c in cs), "the curves have different lengths"
    assert np.all(np.isfinite(e)) and np.all(np.isfinite(b)) and all(np.all(np.isfinite(c)) for c in cs)
    s = b.copy()
    S = np.abs(b).copy()
    for c in cs:
        s = s + c
        S = S + np.abs(c)
    tol = 4 * (len(cs) + 2) * U * S + extra
    gap = np.abs(e - s)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(tol > 0, gap / tol, np.where(gap > 0, np.inf, 0.0))
    return float(ratio.max()), float(gap.max() / max(np.abs(e).max(), np.finfo(float).tiny))


def assert_envelope_identity(envelope, background, components, label="", extra=0.0):
    ratio, rel = envelope_gap(envelope, background, components, extra)
    assert ratio <= 1.0, (f"{label}: the envelope is not the background plus its components: largest gap "
                          f"{ratio:.3g} x the rounding bound ({rel:.3g} of the envelope's height)")
    return ratio, rel


def response_extra(res):
    """The conv_term of every LA component of a run_fit response."""
    extra = np.zeros(len(res["fitted_y"]))
    for p in res["individual_peaks"]:
        if p.get("shape") == "la_casaxps":
            extra = extra + conv_term(p["y"], p["params"]["m"]["value"])
    return extra


def assert_response_identity(res, label=""):
    """A /api/fit (run_fit) response: fitted_y = background_y + Σ individual_peaks[].y."""
    return assert_envelope_identity(res["fitted_y"], res["background_y"],
                                    [p["y"] for p in res["individual_peaks"]], label, response_extra(res))
