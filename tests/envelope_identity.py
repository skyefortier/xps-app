"""The envelope is the background plus the sum of its components — to rounding.

Owner 2026-10-10 (after the 2026-09-17 report of an envelope above the sum of its
components on a UCl4 spectrum: the page's asym-GL had been drawn with a different width
than the server fitted, fixed in cf4938d on 2026-08-31). Shared by the server tests
(tests/test_envelope_identity.py) and the page tests
(tests/test_browser_envelope_identity.py).

THE BOUND, point by point: the envelope e and our sum s = b + Σ c_k are each a sum of the
same n + 1 terms (the background b and n components c_k), added in some order: each
within γ_n · S of the exact sum, S = |b| + Σ |c_k| (Higham, recursive summation). A
component evaluated twice (once inside a composite model, once on its own) can differ by
an ulp of itself where its evaluation involves a BLAS-backed inner product (LA's
np.convolve: CLAUDE.md, "Reproducibility"). So |e − s| ≤ (2 γ_n + 2 u) S ≤ 4 (n + 2) u S
with ample margin for n ≤ 2^20. A difference beyond that is not rounding: the envelope
is not the sum of what is drawn.

FFT-EVALUATED COMPONENTS (DS+G: the page's dsgConvolved_array, the server's _ds_g) carry
an error that is NORMWISE, not pointwise — at a point far out in a tail it can exceed any
multiple of the local sum. Its bound (`fft_term`): for c = A · (ds ⊛ ks) / peakVal with a
radix-2 FFT of length L (Higham, Accuracy and Stability, Thm 24.2: each transform within
log2(L) η of its norm, η = u + γ4 (√2 + u) ≈ 6.7 u; the product one more u; the
unnormalised forward / inverse pair maps 2-norms by √L and 1 / √L, and |FFT(x)|_∞ ≤ |x|_1),
|computed − exact|_∞ ≤ (3 log2(L) η + u) · max(|ds|_2 |ks|_1, |ds|_1 |ks|_2) per convolution;
dividing by peakVal (itself such a value) doubles it; the page and the server each make
one: T = 4 A (3 log2(L) η + u) M / peakVal, added to the point's bound. M, peakVal and L
are the page's own (tests/test_browser_envelope_identity.py reads them from a copy of
dsgConvolved_array); the server's transform (numpy pocketfft, length ≤ L) is within the
same bound. First order; the second-order terms are below 1e-12 of it."""
import numpy as np

U = 2.0 ** -53


ETA = U + 4 * U / (1 - 4 * U) * (np.sqrt(2) + U)         # η of Higham Thm 24.2 (γ4 (√2 + u) + u)


def fft_term(amplitude, m_norm, peak_val, L):
    """T = 4 A (3 log2(L) η + u) M / peakVal: the bound on one FFT-evaluated component's
    rounding at every point, page and server together (see the module docstring)."""
    return 4 * abs(amplitude) * (3 * np.log2(L) * ETA + U) * m_norm / peak_val


def envelope_gap(envelope, background, components, extra=0.0):
    """Largest |e − (b + Σ c)| / (4 (n + 2) u S + extra) over the points: ≤ 1 means within
    rounding (`extra`: the FFT components' Σ T, fft_term). Also returns the largest gap
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


def assert_response_identity(res, label=""):
    """A /api/fit (run_fit) response: fitted_y = background_y + Σ individual_peaks[].y."""
    return assert_envelope_identity(res["fitted_y"], res["background_y"],
                                    [p["y"] for p in res["individual_peaks"]], label)
