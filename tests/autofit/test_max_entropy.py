"""
Max-entropy resolution-enhancement validation (decision-matrix entry 6).

Synthetic ground truth: two narrow Gaussians broadened by a KNOWN Gaussian
kernel + noise.  Deconvolution with the true kernel must sharpen the
doublet back toward resolvability WITHOUT inventing structure elsewhere,
stop at the χ² target, and carry the noise-amplification warning.
"""

import numpy as np
import pytest

from autofit.methods import get_method

X = np.arange(280.0, 292.0, 0.05)
KERNEL_FWHM = 1.2
TRUE = [(285.0, 1000.0, 0.55), (286.1, 800.0, 0.55)]


def _gauss(c, a, w):
    return a * np.exp(-4 * np.log(2) * ((X - c) / w) ** 2)


def _spectrum(seed=9, noise=3.0):
    truth = 50.0 + sum(_gauss(c, a, w) for c, a, w in TRUE)
    k = np.exp(-4 * np.log(2) * ((np.arange(-73, 74) * 0.05) / KERNEL_FWHM) ** 2)
    k /= k.sum()
    broadened = np.convolve(truth, k, mode="same")
    rng = np.random.default_rng(seed)
    return truth, broadened + rng.normal(0, noise, len(X))


def _valley_depth(y):
    """Contrast of the inter-peak valley: 1 − y(valley)/min(peak maxima)."""
    i1 = np.argmin(np.abs(X - TRUE[0][0]))
    i2 = np.argmin(np.abs(X - TRUE[1][0]))
    lo, hi = sorted((i1, i2))
    seg = y[lo:hi + 1]
    peaks = min(y[lo], y[hi])
    return 1.0 - float(seg.min()) / float(peaks) if peaks > 0 else 0.0


@pytest.fixture(scope="module")
def result():
    _, blurred = _spectrum()
    return get_method("max_entropy").run(
        X, blurred, options={"kernel_fwhm_ev": KERNEL_FWHM, "noise_sigma": 3.0})


def test_sharpening_improves_doublet_contrast(result):
    assert result.success
    _, blurred = _spectrum()
    sharp = np.array(result.analysis["sharpened_spectrum"])
    assert _valley_depth(sharp) > _valley_depth(blurred) + 0.1, (
        "deconvolution failed to improve the doublet valley contrast")


def test_stops_at_chi_sq_target(result):
    assert result.diagnostics["chi_sq_target_reached"] is True
    assert result.diagnostics["reduced_chi_sq"] <= 1.0 + 1e-9
    # honest reconvolution: sharpened ⊛ kernel ≈ data at the noise level,
    # i.e. we did NOT overfit past the target
    assert result.analysis["reduced_chi_sq_reconvolution"] > 0.2


def test_artifact_structure_bounded_relative_to_real_features(result):
    """MaxEnt inherently amplifies background noise (~10× here — exactly why
    the payload carries the AMPLIFIES-NOISE warning).  The meaningful
    invariant: flat-region artifacts stay SMALL relative to the real
    features, so no artifact could be mistaken for a comparable peak."""
    sharp = np.array(result.analysis["sharpened_spectrum"])
    flat = sharp[X < 283.0]
    excursion = float(np.max(flat) - np.median(flat))
    assert excursion < 0.15 * float(sharp.max()), (
        f"flat-region artifact {excursion:.0f} exceeds 15% of the main "
        f"feature ({sharp.max():.0f}) — amplification out of control")


def test_honesty_payload(result):
    a = result.analysis
    assert a["kernel"]["provenance"].startswith("USER-SUPPLIED")
    assert "AMPLIFIES NOISE" in a["warning"]
    assert "10.1016/0368-2048(81)85037-2" in a["basis"]
    assert result.peaks == []           # sharpening, not quantification
    assert a["unverified_tunables"]
    import json
    json.dumps(a)


def test_kernel_is_required_no_default():
    _, blurred = _spectrum()
    m = get_method("max_entropy")
    with pytest.raises(ValueError, match="kernel_fwhm_ev"):
        m.run(X, blurred)
    with pytest.raises(ValueError, match="positive"):
        m.run(X, blurred, options={"kernel_fwhm_ev": -1.0})
    with pytest.raises(ValueError, match="unknown max_entropy options"):
        m.run(X, blurred, options={"kernel_fwhm_ev": 1.0, "bogus": 1})


def test_deterministic(result):
    _, blurred = _spectrum()
    r2 = get_method("max_entropy").run(
        X, blurred, options={"kernel_fwhm_ev": KERNEL_FWHM, "noise_sigma": 3.0})
    assert r2.analysis["sharpened_spectrum"] == result.analysis["sharpened_spectrum"]
