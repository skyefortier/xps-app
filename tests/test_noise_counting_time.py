"""The exact counts / T test of scripts/noise_counting_time.py: it finds every true lattice (incl. the two that the
heuristic quantum search missed in the round-3 review), proves the absence of one where there is none, and never
reports a set left unresolved by deferred constraints as admissible (counting-time review round 1). Also the
property-set reader's branches the committed files do not exercise."""
import math
import os
import struct
import sys
from fractions import Fraction

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import noise_counting_time as nct  # noqa: E402
import vgd_properties as vp  # noqa: E402


def _iv(res):
    return res["intervals"]


def _contains(iv, t):
    t = Fraction(t)
    return any(a <= t <= b for a, b in iv)


def test_round_three_counterexamples_are_found():
    for counts, t in ((np.array([1000, 203000, 345000, 100000000, 100000001]), 10000),
                      (np.array([1000, 123456, 200000, 500000, 100000001, 100000002]), 1000)):
        res = nct.admissible_times(counts / float(t), [(Fraction(1, 10), Fraction(3 * t))])
        assert res["status"] == "admissible"
        assert _contains(_iv(res), t), res


def test_poisson_counts_over_a_decoded_time_are_found_with_their_multiples():
    rng = np.random.default_rng(3)
    t = 0.2
    counts = rng.poisson(5000 + 3000 * np.exp(-np.linspace(-3, 3, 191) ** 2))
    res = nct.admissible_times(counts / t, [(Fraction(1, 100), Fraction(1))])
    assert res["status"] == "admissible"
    iv = _iv(res)
    assert _contains(iv, Fraction(1, 5)) and _contains(iv, Fraction(2, 5))
    assert min(a for a, _ in iv) <= Fraction(1, 5) * (1 + Fraction(1, 10**9))


def test_a_smooth_correction_leaves_no_admissible_time():
    rng = np.random.default_rng(4)
    counts = rng.poisson(5000 + 3000 * np.exp(-np.linspace(-3, 3, 191) ** 2))
    y = counts / 0.2 * (1 + 0.01 * np.linspace(0, 1, 191))         # a transmission-like factor
    res = nct.admissible_times(y, [(Fraction(1, 10**9), Fraction(100))])
    assert res["status"] == "excluded" and _iv(res) == [] and res["excluded_by"][0] in ("gap", "value")


def test_a_near_grid_beyond_rounding_is_refused():
    res = nct.admissible_times(np.array([1.0, 2.0, 3.0 + 4e-15]), [(Fraction(1, 10**6), Fraction(10))])
    assert res["status"] == "excluded"


def test_a_value_below_minus_its_rounding_is_never_counts_but_one_within_it_is_zero():
    res = nct.admissible_times(np.array([-1.0, 2.0, 3.0]), [(Fraction(1, 2), Fraction(2))])
    assert res["status"] == "excluded" and res["excluded_by"] == ("negative", None)
    res = nct.admissible_times(np.array([-math.ulp(0.0), 1.0, 2.0]), [(Fraction(1, 2), Fraction(2))])
    assert res["status"] == "admissible" and _contains(_iv(res), 1)


def test_deferred_constraints_are_unresolved_never_admissible():
    res = nct.admissible_times(np.array([1.0, math.sqrt(2)]), [(Fraction(1), Fraction(1_000_000))])
    assert res["status"] == "unresolved" and res["deferred"] > 0


def test_the_reader_packs_vector_elements_and_signs_i1():
    assert vp._value(struct.pack("<HHIhh", 0x1002, 0, 2, 1, 2), 0) == (("VECTOR", [("I2", 1), ("I2", 2)]), 12)
    assert vp._value(struct.pack("<HHb3x", 16, 0, -1), 0) == (("I1", -1), 8)


def test_the_gap_bound_is_below_every_admissible_time():
    counts = np.array([7, 9, 30, 31, 400])
    y = counts / 3.0
    b = nct.gap_bound(y)
    iv = _iv(nct.admissible_times(y, [(Fraction(1, 10**6), Fraction(30))]))
    assert b <= 3 and _contains(iv, 3) and min(a for a, _ in iv) >= b


def test_the_integer_like_statistic_sees_counts_and_not_corrected_counts():
    rng = np.random.default_rng(5)
    counts = rng.poisson(800 + 400 * np.exp(-np.linspace(-3, 3, 191) ** 2))
    v, m = nct.integer_alignment(counts / 0.2, Fraction(1, 5))
    assert m == 191 and v > 0.999
    v, m = nct.integer_alignment(counts / 0.2 * (1 + 0.01 * np.linspace(0, 1, 191)), Fraction(1, 5))
    assert nct.alignment_p(v, m) > 1e-4


def test_the_integer_like_statistic_has_power_on_ten_points_and_refuses_half_integers():
    v, m = nct.integer_alignment(np.arange(100, 110) / 0.2, Fraction(1, 5))
    assert m == 10 and nct.C_MAX * nct.alignment_p(v, m) < 0.01    # round 1: Rayleigh gave 0.046 here
    v, m = nct.integer_alignment((np.arange(100, 110) + 0.5) / 0.2, Fraction(1, 5))
    assert v < -0.999 and nct.alignment_p(v, m) > 0.5               # Rayleigh read R = 1 here


def test_round_one_run_b_deferral_counterexample_is_unresolved():
    res = nct.admissible_times(np.array([1e8, 2e8 + 1]), [(Fraction(1), Fraction(2))])
    assert res["status"] == "unresolved" and res["deferred"] > 0     # a superset, never reported as admissible


def test_an_offset_lattice_is_refused_although_its_gaps_are_multiples():
    counts = np.array([10, 13, 17, 30, 31, 52])
    y = (counts + 0.3) / 4.0                                   # every gap a multiple of 1/4, the values not
    res = nct.admissible_times(y, [(Fraction(1, 10), Fraction(8))])
    assert res["status"] == "excluded" and res["excluded_by"][0] == "value"
