"""The exact counts / T test of scripts/noise_counting_time.py: it finds every true lattice (incl. the two that the
heuristic quantum search missed in the round-3 review) and proves the absence of one where there is none."""
import os
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import noise_counting_time as nct  # noqa: E402


def _contains(iv, t):
    t = Fraction(t)
    return any(a <= t <= b for a, b in iv)


def test_round_three_counterexamples_are_found():
    for counts, t in ((np.array([1000, 203000, 345000, 100000000, 100000001]), 10000),
                      (np.array([1000, 123456, 200000, 500000, 100000001, 100000002]), 1000)):
        iv, _, deferred = nct.admissible_times(counts / float(t), [(Fraction(1, 10), Fraction(3 * t))])
        assert deferred == 0
        assert _contains(iv, t), iv


def test_poisson_counts_over_a_decoded_time_are_found_with_their_multiples():
    rng = np.random.default_rng(3)
    t = 0.2
    counts = rng.poisson(5000 + 3000 * np.exp(-np.linspace(-3, 3, 191) ** 2))
    iv, _, _ = nct.admissible_times(counts / t, [(Fraction(1, 100), Fraction(1))])
    assert _contains(iv, Fraction(1, 5)) and _contains(iv, Fraction(2, 5))
    assert min(a for a, _ in iv) <= Fraction(1, 5) * (1 + Fraction(1, 10**9))


def test_a_smooth_correction_leaves_no_admissible_time():
    rng = np.random.default_rng(4)
    counts = rng.poisson(5000 + 3000 * np.exp(-np.linspace(-3, 3, 191) ** 2))
    y = counts / 0.2 * (1 + 0.01 * np.linspace(0, 1, 191))         # a transmission-like factor
    iv, _, deferred = nct.admissible_times(y, [(Fraction(1, 10**9), Fraction(100))])
    assert iv == [] and deferred == 0


def test_a_near_grid_beyond_rounding_is_refused():
    iv, _, _ = nct.admissible_times(np.array([1.0, 2.0, 3.0 + 4e-15]), [(Fraction(1, 10**6), Fraction(10))])
    assert iv == []


def test_negative_values_are_never_counts():
    assert nct.admissible_times(np.array([-1.0, 2.0, 3.0]), [(Fraction(1, 2), Fraction(2))])[0] == []


def test_the_gap_bound_is_below_every_admissible_time():
    counts = np.array([7, 9, 30, 31, 400])
    y = counts / 3.0
    b = nct.gap_bound(y)
    iv, _, _ = nct.admissible_times(y, [(Fraction(1, 10**6), Fraction(30))])
    assert b <= 3 and _contains(iv, 3) and min(a for a, _ in iv) >= b


def test_the_integer_like_statistic_sees_counts_and_not_corrected_counts():
    rng = np.random.default_rng(5)
    counts = rng.poisson(800 + 400 * np.exp(-np.linspace(-3, 3, 191) ** 2))
    r, m = nct.rayleigh(counts / 0.2, Fraction(1, 5))
    assert m == 191 and r > 0.999
    r, m = nct.rayleigh(counts / 0.2 * (1 + 0.01 * np.linspace(0, 1, 191)), Fraction(1, 5))
    assert m * r * r < 9                                       # p = exp(-m R²) > 1e-4


def test_an_offset_lattice_is_refused_although_its_gaps_are_multiples():
    counts = np.array([10, 13, 17, 30, 31, 52])
    y = (counts + 0.3) / 4.0                                   # every gap a multiple of 1/4, the values not
    iv, _, _ = nct.admissible_times(y, [(Fraction(1, 10), Fraction(8))])
    assert not _contains(iv, 4) and iv == []
