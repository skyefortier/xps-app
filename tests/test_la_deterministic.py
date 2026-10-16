"""The LA unit (2026-10-15): LA(α,β,m)'s convolution in ONE fixed summation order (fitting._convolve_same_fixed_order).

np.convolve's inner product is BLAS ddot, whose rounding (Apple Accelerate on the lab's machine) differed between
processes: the same base and kernel gave different outputs in fresh processes, so a recorded LA curve was not
reproduced by its own verification (seal 1b: every unconfirmed record held LA). These tests pin the replacement:
numpy's 'same' semantics to rounding, and the same bits at every alignment, in every process, through a whole
fit and its verification."""
import hashlib
import json
import os
import subprocess
import sys

import numpy as np
import pytest

import fitting
import test_scattered_starts as SS
from test_seal_1a_server import SHAPES

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _np_same_trimmed(b, k):
    ref = np.convolve(b, k, mode="same")
    if len(ref) > len(b):
        e = len(ref) - len(b)
        ref = ref[e // 2:e // 2 + len(b)]
    return ref


def test_the_fixed_order_convolution_is_numpys_same_to_rounding():
    rng = np.random.default_rng(20261015)
    worst = 0.0
    for _ in range(3000):
        n = int(rng.integers(1, 400))
        k = 2 * int(rng.integers(0, 300)) + 1                 # LA's kernels are odd, any length vs the grid
        b, kr = rng.random(n), rng.random(k)
        kr /= kr.sum()
        ref, got = _np_same_trimmed(b, kr), fitting._convolve_same_fixed_order(b, kr)
        assert got.shape == ref.shape == (n,)
        worst = max(worst, float(np.max(np.abs(got - ref)) / max(np.max(np.abs(ref)), 1e-300)))
    assert worst < 1e-14, worst


def test_the_same_bits_at_every_memory_alignment():
    rng = np.random.default_rng(1)
    base = rng.random(700)
    s = 40 / 3
    half = int(np.ceil(3.5 * s))
    k = np.arange(-half, half + 1, dtype=float)
    kern = np.exp(-k ** 2 / (2 * s * s))
    kern /= kern.sum()

    def at(off, a):
        buf = np.empty(len(a) + 16)
        v = buf[off:off + len(a)]
        v[:] = a
        return v
    outs = {fitting._convolve_same_fixed_order(at(i, base), at(j, kern)).tobytes() for i in range(16) for j in range(16)}
    assert len(outs) == 1


_CHILD = r"""
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
import numpy as np
import fitting
rng = np.random.default_rng(5)
h = hashlib.sha256()
for _ in range(120):
    n = int(rng.integers(40, 900))
    x = np.linspace(370, 415, n)
    p = dict(amplitude=1.0, center=float(rng.uniform(372, 413)), fwhm=float(rng.uniform(0.3, 4)),
             alpha=float(rng.uniform(0.1, 5)), beta=float(rng.uniform(0.1, 5)), m=float(rng.uniform(0.5, 300)))
    h.update(fitting._la_casaxps_true(x, **p).tobytes())
print(h.hexdigest())
"""


def test_the_same_bits_in_every_process():
    """The failure seal 1b saw: np.convolve gave different bits in fresh processes. Five fresh processes, one digest."""
    digests = {subprocess.run([sys.executable, "-c", _CHILD, ROOT], capture_output=True, text=True, check=True).stdout.strip()
               for _ in range(5)}
    assert len(digests) == 1, digests


_VERIFY_CHILD = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
import fitting
d = json.load(open(sys.argv[2]))
print(json.dumps(fitting.verify_fit(d["O"], **d["args"])["state"]))
"""


@pytest.mark.parametrize("m", [0.6, 6.0, 40.0])
def test_an_la_fit_verifies_consistent_in_fresh_processes(tmp_path, m):
    x, y, specs = SS._well_posed()
    specs = [{**specs[0], "shape": "la_casaxps", **{**SHAPES["la_casaxps"], "m": m}, "fix_m": False},
             {**specs[1], "shape": "gaussian"}]
    args = dict(energy=list(map(float, x)), counts=list(map(float, y)), peak_specs=specs, background_method="shirley",
                n_perturb=0, fit_kws={"method": "least_squares"})
    O = json.loads(json.dumps(fitting.run_fit(**{**args, "energy": np.asarray(x), "counts": np.asarray(y)})))
    path = tmp_path / "record.json"
    path.write_text(json.dumps({"O": O, "args": args}))
    states = [json.loads(subprocess.run([sys.executable, "-c", _VERIFY_CHILD, ROOT, str(path)], capture_output=True,
                                        text=True, check=True).stdout) for _ in range(4)]
    assert states == ["consistent"] * 4, states
