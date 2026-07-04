"""
Resolution-enhancement (iterative deconvolution) validation — the
decision-matrix "max-entropy" MENU SLOT (entry 6); the implementation is
NOT a maximum-entropy solve (see the method docstring's honest labeling).

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
    """Iterative deconvolution inherently amplifies background noise (~10×
    here — exactly why the payload carries the AMPLIFIES-NOISE warning).
    The meaningful invariant: flat-region artifacts stay SMALL relative to
    the real features, so no artifact could be mistaken for a comparable
    peak."""
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
    assert "UNCALIBRATED" in a["warning"]         # σ-estimated stopping caveat
    assert "10.1016/0368-2048(81)85037-2" in a["basis"]
    # honest algorithm identity (Codex Stage-9 blocker): no MaxEnt claim
    assert "NOT a constrained maximum-entropy" in a["algorithm"]
    assert "negative_kl_to_flat" in a
    assert "baseline_offset" in a
    assert result.peaks == []           # sharpening, not quantification
    assert a["unverified_tunables"]
    import json
    json.dumps(a)


def test_interior_artifacts_bounded_and_true_peaks_dominate(result):
    """Codex Stage-9 test gap: a single left-flat bound allows misleading
    shoulder/inter-peak artifacts.  Measured behavior on this synthetic:
    noise amplification DOES create secondary maxima (documented warning),
    largest in the boundary margins where deconvolution is ill-posed
    (edge_margin_ev in the payload).  Pins:
    - in the INTERIOR, the two most prominent maxima are the true peaks
      (position within 0.3 eV);
    - every OTHER interior maximum has prominence < 25% of the weakest
      true feature — artifacts can never masquerade as comparable peaks."""
    sharp = np.array(result.analysis["sharpened_spectrum"])
    margin = result.analysis["edge_margin_ev"]
    interior = (X >= X[0] + margin) & (X <= X[-1] - margin)
    proms = []
    for i in range(1, len(sharp) - 1):
        if not interior[i]:
            continue
        if sharp[i] >= sharp[i - 1] and sharp[i] >= sharp[i + 1]:
            left = sharp[max(0, i - 20):i + 1].min()
            right = sharp[i:i + 21].min()
            prom = sharp[i] - max(left, right)
            if prom > 5.0 * result.analysis["noise_sigma"]:
                proms.append((prom, float(X[i])))
    proms.sort(reverse=True)
    assert len(proms) >= 2, f"true peaks not found: {proms}"
    top2 = sorted(be for _, be in proms[:2])
    for f_be, (c, _a, _w) in zip(top2, TRUE):
        assert abs(f_be - c) < 0.3, (f_be, c)
    weakest_true = proms[1][0]
    for prom, be in proms[2:]:
        assert prom < 0.25 * weakest_true, (
            f"interior artifact at {be} eV with prominence {prom:.0f} "
            f"(≥25% of the weakest true feature {weakest_true:.0f})")


def _reconv_chi(a, blurred):
    """Independently reconvolve the emitted spectrum and score it vs data."""
    sharp = np.array(a["sharpened_spectrum"]) - a["baseline_offset"]
    k = np.exp(-4 * np.log(2) * ((np.arange(-73, 74) * 0.05) / KERNEL_FWHM) ** 2)
    k /= k.sum()
    edge = np.convolve(np.ones(len(X)), k, mode="same")
    model = np.convolve(sharp, k, mode="same") / edge + a["baseline_offset"]
    return float(np.sum(((blurred - model) / a["noise_sigma"]) ** 2) / len(X))


def test_emitted_spectrum_reconvolves_to_data(result):
    """The emitted sharpened_spectrum (with its baseline_offset) must
    reconvolve to the ORIGINAL data at the reported χ² (catches any
    offset/edge bookkeeping drift)."""
    _, blurred = _spectrum()
    a = result.analysis
    assert _reconv_chi(a, blurred) == pytest.approx(
        a["reduced_chi_sq_reconvolution"], rel=1e-6)


def test_nonconverged_chi_sq_matches_emitted_spectrum():
    """Codex Stage-9 re-check MAJOR: on max_iter exhaustion the loop's last
    χ² predated the final multiplicative update, so the reported
    reduced_chi_sq_reconvolution did not describe the emitted spectrum.
    Pin the reconvolution identity on the NON-converged path too."""
    _, blurred = _spectrum()
    res = get_method("max_entropy").run(
        X, blurred, options={"kernel_fwhm_ev": KERNEL_FWHM,
                             "noise_sigma": 3.0, "max_iter": 3})
    a = res.analysis
    assert res.diagnostics["chi_sq_target_reached"] is False
    assert res.diagnostics["iterations"] == 3
    assert a["reduced_chi_sq_reconvolution"] > 1.0   # genuinely non-converged
    assert _reconv_chi(a, blurred) == pytest.approx(
        a["reduced_chi_sq_reconvolution"], rel=1e-6)


def test_kernel_validation():
    _, blurred = _spectrum()
    m = get_method("max_entropy")
    with pytest.raises(ValueError, match="finite"):
        m.run(X, blurred, options={"kernel_fwhm_ev": float("nan")})
    with pytest.raises(ValueError, match="as wide as the spectrum"):
        m.run(X, blurred, options={"kernel_fwhm_ev": 50.0})


def test_estimated_sigma_path_flagged():
    _, blurred = _spectrum()
    res = get_method("max_entropy").run(X, blurred,
                                        options={"kernel_fwhm_ev": KERNEL_FWHM})
    assert res.success
    assert res.analysis["noise_sigma_source"].startswith("estimated")


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
