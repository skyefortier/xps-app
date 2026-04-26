"""
Regression: _la_casaxps_true must return len(output) == len(x) for any
input length, including the case where the input grid is shorter than
the Gaussian convolution kernel (2m+1 points).

np.convolve(..., mode='same') returns max(len(a), len(v)), not len(a),
so without an explicit trim the function returned a kernel-length array
when the input grid was shorter than the kernel — breaking the lmfit
residual computation in composite fits and surfacing as cryptic shape
mismatches like "operands could not be broadcast together with shapes
(995,) (349,)".
"""
import sys
sys.path.insert(0, "/home/skye/xps-app")
import numpy as np
from fitting import _la_casaxps_true


def test_short_input_returns_input_length():
    # When len(x) < 2m+1 the kernel is longer than the input. Output must
    # still match len(x). Span the boundary where len(x) crosses 2m+1.
    for n in [10, 50, 100, 101, 102, 200, 500]:
        x = np.linspace(370, 405, n)
        y = _la_casaxps_true(x, 1000, 380, 1.5, 1.0, 1.0, m=50)
        assert len(y) == n, f"len mismatch for n={n}: got {len(y)}"
    print("OK — short-input length contract holds across 2m+1 boundary")


def test_zero_kernel():
    # m=0 still works (no convolution branch).
    x = np.linspace(370, 405, 10)
    y = _la_casaxps_true(x, 1000, 380, 1.5, 1.0, 1.0, m=0)
    assert len(y) == 10
    print("OK — m=0 short-input passes through unconvolved")


if __name__ == "__main__":
    test_short_input_returns_input_length()
    test_zero_kernel()
