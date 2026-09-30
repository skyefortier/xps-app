"""Each background method is tested against its DEFINING STATEMENT — the
equation or constrained problem its answer must satisfy — evaluated directly
on its output by an independent checker (scripts/background_defining_statements.py),
on synthetic spectra and on every committed spectrum (docs/autofit/test_data).
Background math foundation, 2026-09-30; findings:
docs/findings/background-math/README.md. Where an implementation does NOT meet
the statement, the test pins the measured gap (a finding the owner decides on)
so that it cannot grow unnoticed or be closed without updating the finding.
"""
import glob
import os
import sys

import numpy as np
import pytest

import fitting

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import background_defining_statements as D  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "docs", "autofit", "test_data")
ROUND = 1e-9          # of the span: a residual at rounding level (measured <= 2e-11 where the statement holds)


def _spectra():
    from autofit.reference import load_reference_fits
    out = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            i0, i1 = rf.bg_indices()
            out.append((f"{rf.project}::{rf.name}", np.asarray(rf.roi_be, float)[i0:i1],
                        np.asarray(rf.roi_intensity, float)[i0:i1], int(rf.endpoint_avg or 1)))
    return out


SPECTRA = _spectra()


def _synthetic(descending=True, seed=0):
    rng = np.random.default_rng(seed)
    x = np.arange(280.0, 296.0, 0.05)
    g = lambda c, a, w: a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
    peaks = g(284.5, 20000, 0.9) + g(286.5, 4000, 1.3)
    y = rng.poisson(peaks + 1000 + 400 * np.cumsum(peaks) / peaks.sum()).astype(float)
    return (x[::-1].copy(), y[::-1].copy()) if descending else (x, y)


def test_the_committed_spectra_are_all_here():
    assert len(SPECTRA) == 121


# ── shirley: B = T(B) ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("descending", [True, False])
def test_shirley_solves_the_shirley_relation(descending):
    x, y = _synthetic(descending)
    B = fitting.shirley_background(x, y)
    assert D.shirley_residual(x, y, B) < ROUND


def test_shirley_solves_the_shirley_relation_on_every_committed_spectrum_read_as_measured():
    res = [D.shirley_residual(x, y, fitting.shirley_background(x, y, n_avg=1)) for _, x, y, _ in SPECTRA]
    assert max(res) < ROUND


def test_the_shirley_fixed_point_is_unique():
    # the same fixed point from a start below the data as from the linear start
    for _, x, y, ep in SPECTRA[::10]:
        a = D.unconstrained_solution(x, y, ep)[0]
        b = D._fixed_point(x, y, ep, False, B0=np.full(len(y), float(np.min(y))))[0]
        assert np.max(np.abs(a - b)) / D.span_of(y) < ROUND


def test_FINDING_shirley_with_endpoint_averaging_integrates_the_averaged_data():
    # With n_avg > 1 shirley_background replaces the first / last points OF THE DATA by their
    # mean, so its relation integrates a modified spectrum; smart_exp reads only the edge
    # LEVELS from the averaged ends and integrates the measured data. Two readings of one
    # field. Measured on the 13 committed spectra with n_avg > 1: up to 1.05e-3 of the span,
    # 0.32 % of net area. Pinned until the owner decides (findings §F1).
    gaps = [D.shirley_residual(x, y, fitting.shirley_background(x, y, n_avg=ep), ep)
            for _, x, y, ep in SPECTRA if ep > 1]
    assert len(gaps) == 13
    assert max(gaps) > 1e-4 and max(gaps) < 1.1e-3


def test_FINDING_the_shirley_stop_is_absolute():
    # 1e-6 COUNTS, not relative: the same spectrum in other units stops elsewhere. Negligible on
    # the committed spectra (<= 2.3e-3 % of net area at 1e-6 of the units) — findings §F5.
    _, x, y, _ = next(s for s in SPECTRA if s[3] == 1)
    rel = []
    for scale in (1.0, 1e-6):
        B = fitting.shirley_background(x, y * scale)
        Bu = D.unconstrained_solution(x, y * scale, 1)[0]
        rel.append(np.max(np.abs(B - Bu)) / D.span_of(y * scale))
    assert rel[0] < ROUND and rel[1] > rel[0]


# ── smart and smart_exp: B = min(T(B), y) ────────────────────────────────────

def test_smart_solves_the_constrained_problem_when_it_reads_the_data_as_measured():
    # Not a post-hoc clamp of a different problem: the implemented Shirley integrates the
    # POSITIVE PART of the net signal, s = max(y - B, 0), and s(min(B, y)) = s(B), so the
    # clamped fixed point is itself a fixed point of B = min(T(B), y) (findings §smart).
    for _, x, y, _ in SPECTRA:
        B = fitting.smart_background(x, y, n_avg=1)
        res, viol, _ = D.constrained_residual(x, y, B, 1)
        assert res < ROUND and viol == 0.0


@pytest.mark.parametrize("descending", [True, False])
def test_smart_exp_solves_the_constrained_problem(descending):
    x, y = _synthetic(descending)
    for ep in (1, 3, 10):
        res, viol, active = D.constrained_residual(x, y, fitting.smart_experimental_background(x, y, n_avg=ep), ep)
        assert res < ROUND and viol == 0.0 and active > 0


def test_smart_exp_solves_the_constrained_problem_on_every_committed_spectrum():
    for _, x, y, ep in SPECTRA:
        res, viol, _ = D.constrained_residual(x, y, fitting.smart_experimental_background(x, y, n_avg=ep), ep)
        assert res < ROUND and viol == 0.0


def test_the_constrained_solution_is_unique_and_smart_and_smart_exp_are_the_same_method():
    for _, x, y, _ in SPECTRA[::5]:
        c1 = D.constrained_solution(x, y, 1)[0]
        c2 = D.constrained_solution(x, y, 1, B0=np.minimum(D.unconstrained_solution(x, y, 1)[0], y))[0]
        sp = D.span_of(y)
        assert np.max(np.abs(c1 - c2)) / sp < ROUND
        assert np.max(np.abs(fitting.smart_background(x, y, n_avg=1) - c1)) / sp < ROUND
        assert np.max(np.abs(fitting.smart_experimental_background(x, y, n_avg=1) - c1)) / sp < ROUND


def test_FINDING_the_constraint_on_noisy_counts_biases_the_net_area_high():
    # B <= I is justified for the EXPECTED intensity (net signal is a non-negative rate); imposed
    # on Poisson counts it binds on noise dips and lowers B. Known true Shirley-shaped background,
    # 300 Poisson draws: unconstrained Shirley is unbiased, the constrained problem is biased high
    # (measured +0.82 % +- 0.07 % s.e. against -0.12 % +- 0.11 %) — findings §F2.
    rng = np.random.default_rng(1)
    x = np.arange(280.0, 296.0, 0.05)
    g = lambda c, a, w: a * np.exp(-4 * np.log(2) * ((x - c) / w) ** 2)
    peaks = g(284.5, 20000, 0.9) + g(286.5, 4000, 1.3)
    truth = peaks + 1000 + 400 * np.cumsum(peaks) / peaks.sum()
    a_true = np.trapezoid(peaks, x)
    err = {"shirley": [], "constrained": []}
    for _ in range(300):
        y = rng.poisson(truth).astype(float)
        err["shirley"].append(np.trapezoid(y - fitting.shirley_background(x, y), x) / a_true - 1)
        err["constrained"].append(np.trapezoid(y - fitting.smart_experimental_background(x, y), x) / a_true - 1)
    s, c = np.array(err["shirley"]), np.array(err["constrained"])
    se = lambda v: v.std() / np.sqrt(len(v))
    assert abs(s.mean()) < 3 * se(s)                           # unbiased
    assert c.mean() - s.mean() > 5 * np.hypot(se(s), se(c))    # biased high


# ── linear, tougaard, manual ─────────────────────────────────────────────────

def test_linear_is_the_affine_line_through_the_endpoints():
    for _, x, y, _ in SPECTRA:
        assert D.linear_residual(x, y, fitting.linear_background(x, y)) < ROUND


def test_tougaard_solves_its_integral_relation():
    # the implementation (a convolution on uniform grids) equals the explicit double sum,
    # and the double sum is within 1e-5 of the span of the integral on a 10x finer grid
    for _, x, y, ep in SPECTRA[::4]:
        Bt = fitting.tougaard_background(x, y, n_avg=ep)
        sp = D.span_of(y)
        assert np.max(np.abs(Bt - D.tougaard_reference(x, y, ep))) / sp < ROUND
        assert np.max(np.abs(Bt - D.tougaard_refined(x, y, ep))) / sp < 1e-5


def test_tougaard_meets_its_two_anchor_conditions():
    x, y = _synthetic(True)
    B = fitting.tougaard_background(x, y)
    assert B[-1] == y[-1] and B[0] == pytest.approx(y[0], rel=1e-12)   # C0 at the low-BE edge; J at the high-BE edge


def test_the_servers_manual_background_is_the_piecewise_affine_curve_through_the_anchors():
    x = np.linspace(296.0, 280.0, 321)
    anchors = [[282.0, 1000.0], [289.5, 1400.0], [284.0, 1050.0], [294.0, 1500.0]]
    y = np.full_like(x, 5000.0)
    res = fitting.run_fit(x, y, [{"id": 1, "shape": "gaussian", "center": 286.0, "amplitude": 100.0, "fwhm": 1.0, "amplitude_min": 0}],
                          background_method="manual", manual_bg=anchors, n_perturb=0, fit_kws={"method": "leastsq"})
    assert np.max(np.abs(np.asarray(res["background_y"]) - D.manual_reference(x, anchors))) < 1e-9


# ── shirley_linear: no defining statement ────────────────────────────────────

def test_FINDING_shirley_linear_has_no_defining_statement():
    # Its unclamped curve is the line between the edge levels PLUS a Shirley-shaped step of the
    # full edge difference that is largest at the LOW-BE edge — so it starts |b_low - b_high|
    # above the low-BE level, a condition no background assumption produces; only the final
    # clamp to the data brings the edge back. On the committed spectra the clamp is active on
    # a median 43 % of the points (up to 72 %). De-listed; findings §F4: not to return.
    frac = []
    for _, x, y, ep in SPECTRA:
        _, cf = D.edge_conditions(x, y, fitting.shirley_linear_background(x, y, n_avg=ep), ep)
        frac.append(cf)
    assert np.median(frac) > 0.3
