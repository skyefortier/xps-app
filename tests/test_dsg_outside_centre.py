"""The DS+G guarded branch (2026-09-25, unit fix-dsg-page-evaluator).

A centre OUTSIDE the padded grid is normalised by the curve's maximum: the
old rule normalised by np.interp's clamped end value — the tail of a curve
whose peak is not on the grid, of order 1e-20 after the tapers — and the
rounding SIGN of that number chose between two unrelated curves (the
max-normalised tail, or the tail divided by ~1e-20). A centre inside the
padded grid takes the pre-existing code path, byte for byte
(scripts/dsg_outside_centre_identity.py proves it against main's function;
docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt).
"""
import numpy as np

import fitting

DSG = fitting._SHAPE_FUNCS["ds_g"]


def _padded(x, beta, m):
    step = max(float(np.median(np.abs(np.diff(x)))), 1e-6)
    n_pad = max(int(np.ceil(max(10.0 * m, 20.0 * beta) / step)), 1)
    return min(x[0], x[-1]) - n_pad * step, max(x[0], x[-1]) + n_pad * step


def test_centre_outside_the_padded_grid_is_normalised_by_the_maximum():
    x = (np.arange(200) - 99.5) * 0.05                       # [-5, 5]; pad = max(10*0.05, 20*0.05) = 1 eV
    for c in (10.0, -10.0, 6.5, -6.5):                       # all outside [-6, 6]
        y = DSG(x, amplitude=1.0, center=c, alpha=0.49, beta=0.05, m_gauss=0.05)
        assert np.isfinite(y).all()
        assert np.max(np.abs(y)) == 1.0, (c, np.max(np.abs(y)))


def test_centre_inside_the_padded_grid_keeps_the_interpolated_centre_normalisation():
    x = (np.arange(200) - 99.5) * 0.05
    lo, hi = _padded(x, 0.05, 0.05)
    for c in (0.0, 0.013, 4.9, -4.9, lo + 1e-9, hi - 1e-9, lo, hi):   # the edges themselves are INSIDE
        y = DSG(x, amplitude=1.0, center=c, alpha=0.25, beta=0.05, m_gauss=0.05)
        # the pre-existing rule: the value interpolated at the centre is 1 (when the
        # centre lies within the DATA grid, that value is on the returned curve)
        if x.min() <= c <= x.max():
            assert abs(float(np.interp(c, x, y)) - 1.0) < 1e-9, c
        assert np.isfinite(y).all()


def test_the_branch_boundary_is_the_padded_grid_not_the_data_window():
    """A centre between the data window's edge and the padded grid's edge is
    INSIDE: the old rule still applies there (interp at the centre, with its
    fallbacks), so nothing that ran before changed."""
    x = np.linspace(280, 290, 201)
    lo, hi = _padded(x, 0.7, 0.4)                            # pad = 20 * 0.7 = 14 eV
    c = hi - 0.5
    y = DSG(x, amplitude=3.0, center=c, alpha=0.2, beta=0.7, m_gauss=0.4)
    # clamped-end normalisation: the last (highest-x) data point is nearest the centre
    assert np.isfinite(y).all() and y.max() > 0
    y_out = DSG(x, amplitude=3.0, center=hi + 0.5, alpha=0.2, beta=0.7, m_gauss=0.4)
    assert abs(np.max(np.abs(y_out)) - 3.0) < 1e-12
