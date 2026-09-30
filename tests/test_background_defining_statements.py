"""Each background method is tested against its DEFINING STATEMENT — the
equation or constrained problem its answer must satisfy — evaluated directly on
its output by an independent checker (scripts/background_defining_statements.py:
its own endpoint preprocessing, integrals and reference solver), under the
method's OWN reading of endpoint averaging, on synthetic spectra and on every
committed spectrum. Background math foundation, 2026-09-30, revised after Codex
round 1; findings: docs/findings/background-math/README.md. Where an
implementation does NOT meet a statement, or a claim is limited, the test pins the
measured fact (a finding the owner decides on).
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
ROUND = 1e-9          # of the span: a residual at rounding level (measured <= 3.3e-11 where a statement holds)


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
X = np.arange(280.0, 296.0, 0.05)
PEAKS = 20000 * np.exp(-4 * np.log(2) * ((X - 284.5) / 0.9) ** 2) + 4000 * np.exp(-4 * np.log(2) * ((X - 286.5) / 1.3) ** 2)
QP = np.concatenate([[0.0], np.cumsum(0.5 * (PEAKS[:-1] + PEAKS[1:]) * np.diff(X))])


def _truth(step):
    """A spectrum whose background satisfies the Shirley relation EXACTLY (trapezoid rule)."""
    bg = 1000 + step * QP / QP[-1]
    return PEAKS + bg, bg


def test_the_committed_spectra_are_all_here():
    assert len(SPECTRA) == 121


def test_the_constructed_truth_satisfies_the_relation():
    for step in (400.0, 4000.0):
        y, bg = _truth(step)
        assert D.shirley_residual(X, y, bg, 1, "data") < 1e-14


# ── shirley: B = T(B), reading "data" ────────────────────────────────────────

@pytest.mark.parametrize("descending", [True, False])
def test_shirley_solves_the_shirley_relation(descending):
    y, _ = _truth(400.0)
    y = np.random.default_rng(0).poisson(y).astype(float)
    x, y = (X[::-1].copy(), y[::-1].copy()) if descending else (X, y)
    for ep in (1, 3, 10):
        assert D.shirley_residual(x, y, fitting.shirley_background(x, y, n_avg=ep), ep, "data") < ROUND


def test_shirley_solves_its_relation_on_every_committed_spectrum():
    assert max(D.shirley_residual(x, y, fitting.shirley_background(x, y, n_avg=ep), ep, "data") for _, x, y, ep in SPECTRA) < ROUND


def test_FINDING_the_shirley_relation_can_have_several_solutions():
    # Codex round 1 (runs A, B): exact solutions of B = T(B) (and of B = min(T(B), I)) that differ,
    # with different net areas — the relation is not well posed in general; an implementation
    # returns the solution its iteration reaches from the straight line between the edge levels.
    for E, I, sols in (
        ([0, 1, 2, 3], [1, 1.72, 1.98, 2], [[1, 1.40, 1.90, 2], [1, 1.45, 1.95, 2], [1, 1.50, 2.00, 2]]),
        ([0, 1, 2, 3], [1, 1.45, 1.90, 2], [[1, 1.30, 1.80, 2], [1, 1.375, 1.875, 2]]),
    ):
        E, I = np.array(E, float), np.array(I, float)
        areas = set()
        for B in sols:
            B = np.array(B, float)
            assert D.shirley_residual(E, I, B, 1, "data") < 1e-12
            assert D.constrained_residual(E, I, np.minimum(B, I), 1, "data")[0] < 1e-12
            areas.add(round(D.net_area(E, I, np.minimum(B, I)), 9))
        assert len(areas) == len(sols)


def test_FINDING_when_the_data_lie_below_the_edge_line_the_iteration_cannot_start():
    # Codex round 1 (run A): the positive-part integral of the first guess is zero, so the
    # relation is undefined there; production returns the line (shirley) or the data (smart,
    # smart_exp), none of which solves its statement — although solutions exist.
    E, I = np.array([0, 1, 2, 3, 4], float), np.array([10, 5, 5, 17, 20], float)
    B = fitting.shirley_background(E, I)
    assert np.allclose(B, np.linspace(10, 20, 5))
    assert D.shirley_residual(E, I, B, 1, "data") == float("inf")
    assert D.shirley_residual(E, I, np.array([10, 10, 10, 15, 20.0]), 1, "data") < 1e-12     # a solution exists
    assert np.array_equal(fitting.smart_experimental_background(E, I), I)
    # none of the committed spectra is in this case
    for _, x, y, ep in SPECTRA:
        xa, Dd, ya, bl, bh, _ = D.reading(x, y, ep, "data")
        assert D.shirley_map(xa, Dd, np.linspace(bl, bh, len(ya)), bl, bh) is not None


def test_the_reference_solver_reports_convergence_only_for_a_solution():
    # Codex round 1: a flag on the last update certified points that do not satisfy the statement
    _, x, y, ep = SPECTRA[0]
    B, k, ok, res = D.solve(x, y, ep, "data", max_iter=1)
    assert not ok and res > D.REF_TOL
    B, k, ok, res = D.solve(x, y, ep, "data")
    assert ok and res <= D.REF_TOL and D.shirley_residual(x, y, B, ep, "data") <= D.REF_TOL


def test_FINDING_the_two_readings_of_endpoint_averaging():
    # shirley integrates the endpoint-averaged DATA; smart_exp reads only the edge LEVELS and
    # integrates the measured data. Each reading's own solution, on the 13 committed spectra with
    # n_avg > 1: up to 1.05e-3 of the span apart, <= 0.33 % of net area (findings F1).
    gaps = []
    for _, x, y, ep in SPECTRA:
        if ep > 1:
            a, _, oka, _ = D.solve(x, y, ep, "data")
            b, _, okb, _ = D.solve(x, y, ep, "levels")
            assert oka and okb
            gaps.append(np.max(np.abs(a - b)) / D.span_of(y))
    assert len(gaps) == 13 and 1e-4 < max(gaps) < 1.1e-3


def test_FINDING_the_shirley_stop_is_absolute():
    # 1e-6 INTENSITY UNITS, not relative: the same spectrum in other units stops elsewhere;
    # negligible on the committed spectra (findings F5)
    _, x, y, ep = next(s for s in SPECTRA if s[3] == 1)
    rel = []
    for scale in (1.0, 1e-6):
        ref, _, ok, _ = D.solve(x, y * scale, ep, "data")
        assert ok
        rel.append(np.max(np.abs(fitting.shirley_background(x, y * scale, n_avg=ep) - ref)) / D.span_of(y * scale))
    assert rel[0] < ROUND and rel[1] > 10 * rel[0]


# ── smart and smart_exp: B = min(T(B), I) ────────────────────────────────────

def test_smart_solves_the_constrained_problem_when_it_reads_the_data_as_measured():
    # the clamp identity: shirley integrates s = max(I - B, 0) and s(min(B, I)) = s(B), so the
    # clamped Shirley solution is itself a solution of the constrained problem — a correspondence
    # between solutions, not a uniqueness result
    for _, x, y, _ in SPECTRA:
        res, viol, _ = D.constrained_residual(x, y, fitting.smart_background(x, y, n_avg=1), 1, "data")
        assert res < ROUND and viol == 0.0


def test_FINDING_smart_with_endpoint_averaging_solves_no_single_statement():
    # its integrand reads the averaged data, its clamp the raw data: on the committed spectra with
    # n_avg > 1 it misses the constrained statement under either reading (findings F1)
    for _, x, y, ep in SPECTRA:
        if ep > 1:
            B = fitting.smart_background(x, y, n_avg=ep)
            worst = min(D.constrained_residual(x, y, B, ep, how)[0] for how in ("data", "levels"))
            if ep >= 25:
                assert worst > 1e-5


@pytest.mark.parametrize("descending", [True, False])
def test_smart_exp_solves_the_constrained_problem(descending):
    y = np.random.default_rng(0).poisson(_truth(400.0)[0]).astype(float)
    x, y = (X[::-1].copy(), y[::-1].copy()) if descending else (X, y)
    for ep in (1, 3, 10):
        res, viol, active = D.constrained_residual(x, y, fitting.smart_experimental_background(x, y, n_avg=ep), ep, "levels")
        assert res < ROUND and viol == 0.0 and active > 0


def test_smart_exp_solves_the_constrained_problem_on_every_committed_spectrum():
    for _, x, y, ep in SPECTRA:
        res, viol, _ = D.constrained_residual(x, y, fitting.smart_experimental_background(x, y, n_avg=ep), ep, "levels")
        assert res < ROUND and viol == 0.0


def test_smart_and_smart_exp_return_the_same_background_at_n_avg_1_on_every_committed_spectrum():
    # an empirical agreement (the problem can have several solutions; both iterations start from
    # the same line), not a theorem — findings F3
    for _, x, y, _ in SPECTRA:
        a, b = fitting.smart_background(x, y, n_avg=1), fitting.smart_experimental_background(x, y, n_avg=1)
        assert np.max(np.abs(a - b)) / D.span_of(y) < ROUND


# ── the noise bias (findings F2) ─────────────────────────────────────────────

def _bias(step, draws=300):
    y0, _ = _truth(step)
    a_true = np.trapezoid(PEAKS, X)
    rng = np.random.default_rng(1)
    s, c = [], []
    for _ in range(draws):
        y = rng.poisson(y0).astype(float)
        s.append(np.trapezoid(y - fitting.shirley_background(X, y), X) / a_true - 1)
        c.append(np.trapezoid(y - fitting.smart_experimental_background(X, y), X) / a_true - 1)
    return np.array(s), np.array(c)


def test_FINDING_the_constraint_adds_a_positive_net_area_bias():
    # paired over the same draws: the constraint's increment is positive and resolved at both
    # step sizes (measured +0.90 % +- 0.02 and +1.28 % +- 0.04 over 1000 draws)
    for step in (400.0, 4000.0):
        s, c = _bias(step)
        d = c - s
        assert d.mean() > 10 * d.std() / np.sqrt(len(d))


def test_FINDING_unconstrained_shirley_is_not_unbiased_in_general():
    # Codex round 1: at a small step there is no resolved bias (measured -0.03 % +- 0.06), at a
    # ten times larger step unconstrained Shirley is biased high (+2.29 % +- 0.17 over 1000 draws)
    s, _ = _bias(4000.0)
    assert s.mean() > 5 * s.std() / np.sqrt(len(s))


# ── linear, tougaard, manual ─────────────────────────────────────────────────

def test_linear_is_the_affine_line_through_the_endpoints():
    for _, x, y, _ in SPECTRA:
        assert D.linear_residual(x, y, fitting.linear_background(x, y)) < ROUND


def test_tougaard_solves_its_integral_relation_and_meets_its_anchor():
    # an independent double sum under its own reading ("data"); the anchor B(E_high) = D(E_high);
    # within 1e-5 of the span of an independent 10x-refined integral
    for _, x, y, ep in SPECTRA[::4]:
        Bt = fitting.tougaard_background(x, y, n_avg=ep)
        sp = D.span_of(y)
        assert np.max(np.abs(Bt - D.tougaard_statement(x, y, ep, "data"))) / sp < ROUND
        loss, xa, Dd, c0, dhi, flip = D.tougaard_loss(x, y, ep, "data")
        assert abs((Bt[-1] if flip else Bt[0]) - dhi) / sp < ROUND
        assert np.max(np.abs(Bt - D.tougaard_refined(x, y, ep, "data"))) / sp < 1e-5


def test_FINDING_tougaard_when_the_discrete_loss_sum_vanishes():
    # Codex round 2: a two-point window has no term with T > 0, so the anchor does not fix lam.
    # Unequal anchor levels: no solution; production's flat C0 misses the high-BE anchor.
    E, I = np.array([0.0, 1.0]), np.array([10.0, 20.0])
    assert D.tougaard_statement(E, I) is None
    assert np.array_equal(fitting.tougaard_background(E, I), [10.0, 10.0])
    # Equal levels: every lam solves it, and production's flat C0 is a solution
    E, I = np.array([0.0, 1.0]), np.array([10.0, 10.0])
    assert np.array_equal(fitting.tougaard_background(E, I), D.tougaard_statement(E, I))


def test_FINDING_the_kernel_shape_matters_on_the_wider_windows():
    # Codex round 1: the U 4f windows (31-35 eV) exceed the kernel maximum (23.4 eV); a share of the
    # loss integral comes from beyond it and a linear small-loss kernel moves the background by
    # up to ~4 % of the span (findings F6)
    u4f = [(x, y, ep) for n, x, y, ep in SPECTRA if "U4f" in n]
    share = max(D.tougaard_beyond_peak_fraction(x, y, ep) for x, y, ep in u4f)
    moved = max(np.max(np.abs(fitting.tougaard_background(x, y, n_avg=ep) - D.tougaard_statement(x, y, ep, "data", kernel=lambda T: T / D.KC ** 2))) / D.span_of(y)
                for x, y, ep in u4f)
    assert share > 0.2 and moved > 0.02


def test_the_servers_manual_background_is_the_piecewise_affine_curve_through_the_anchors():
    x = np.linspace(296.0, 280.0, 321)
    anchors = [[282.0, 1000.0], [289.5, 1400.0], [284.0, 1050.0], [294.0, 1500.0]]
    res = fitting.run_fit(x, np.full_like(x, 5000.0), [{"id": 1, "shape": "gaussian", "center": 286.0, "amplitude": 100.0, "fwhm": 1.0, "amplitude_min": 0}],
                          background_method="manual", manual_bg=anchors, n_perturb=0, fit_kws={"method": "leastsq"})
    assert np.max(np.abs(np.asarray(res["background_y"]) - D.manual_reference(x, anchors))) < 1e-9


# ── shirley_linear ───────────────────────────────────────────────────────────

def test_FINDING_shirley_linear_solves_a_reversed_step_that_misses_the_low_edge():
    # Codex round 1: it HAS a statement, B = min(L + d (1 - F(B)), I); it meets the high-BE edge,
    # but its step is largest at the LOW-BE edge — the reverse of inelastic scattering — and the
    # unclamped curve sits d above the low-BE level there (findings F4)
    lows, clamped = [], []
    for _, x, y, ep in SPECTRA:
        r, lo, hi, cf = D.shirley_linear_residual(x, y, fitting.shirley_linear_background(x, y, n_avg=ep), ep)
        assert r < ROUND and hi < ROUND
        lows.append(lo); clamped.append(cf)
    assert np.median(lows) > 0.01 and np.median(clamped) > 0.3


def test_FINDING_shirley_linear_equal_edge_levels_return_the_line_unclamped():
    # Codex round 2: equal edge levels skip the equation and the clamp; the equation's answer
    # here is min(L, I) = [10, 10, 5, 10, 10] (d = 0), production returns a flat 10 above the data
    E, I = np.arange(5.0), np.array([10.0, 15.0, 5.0, 15.0, 10.0])
    B = fitting.shirley_linear_background(E, I)
    assert np.array_equal(B, [10.0] * 5)
    assert D.shirley_linear_residual(E, I, np.minimum(B, I))[0] < ROUND
    assert D.shirley_linear_residual(E, I, B)[0] == pytest.approx(0.5)


def test_shirley_linear_line_is_affine_in_index_not_energy():
    # Codex round 2: on a non-uniform grid the implementation's L is np.linspace (by index);
    # the statement is satisfied with that L, and an energy-affine L would differ by ~4.5 %
    E, I = np.array([0.0, 0.1, 0.2, 2.0, 4.0]), np.array([10.0, 20.0, 30.0, 25.0, 12.0])
    B = fitting.shirley_linear_background(E, I)
    assert D.shirley_linear_residual(E, I, B)[0] < ROUND
    by_index = np.linspace(I[0], I[-1], len(I))
    by_energy = I[0] + (I[-1] - I[0]) * (E - E[0]) / (E[-1] - E[0])
    assert np.max(np.abs(by_index - by_energy)) / D.span_of(I) > 0.04


def test_degenerate_windows():
    # README "Degenerate windows": fewer than two points give zeros; equal end energies give
    # the flat first intensity for linear; averaging reads at most n // 4 points per edge
    one = (np.array([1.0]), np.array([5.0]))
    for f in (fitting.shirley_background, fitting.smart_background, fitting.smart_experimental_background,
              fitting.shirley_linear_background, fitting.tougaard_background):
        assert np.array_equal(f(*one), [0.0])
    assert np.array_equal(fitting.linear_background(np.array([2.0, 2.0]), np.array([3.0, 7.0])), [3.0, 3.0])
    assert D.band(8, 10) == 2 and D.band(3, 10) == 1
    y = np.arange(8.0)
    assert np.array_equal(fitting._apply_endpoint_averaging(y, 10), [0.5, 0.5, 2, 3, 4, 5, 6.5, 6.5])
