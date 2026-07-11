"""
Candidate pool (`autofit.candidates.build_candidate_pool`) — the pluggable
candidate-generation layer (goal steps 2/4/5): merge local-max, CWT-ridge,
and grammar sources into an OVERCOMPLETE provenance-tagged pool with
duplicate suppression; conservative SEEDING gates decide which pool
features become pre-seeded slots; everything (incl. gate failures) is
surfaced for the honesty layer.  Selection — not detection — judges.

All synthetic, deterministic seeds.  These are MECHANICS tests — gate
VALUES here exercise the machinery; the engine's operating-point values
(trivia floor 0.02 / cap 6, Stage-2 recalibration 2026-07-10) are pinned
at the wiring level.  Curvature-seed blocking is CONTAINMENT-only (a slot
window must actually contain the feature's center): the Stage-2 Step-1
diagnosis measured the old window+margin test blocking top-5 curvature
detections (z 107–273) that NO slot could center — "covered by grammar"
was a fiction.  Near-edge ambiguity is SELECTION's job (absent-slot
pruning), not detection's.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from stress_cases import _pv  # noqa: E402

from autofit.candidates import build_candidate_pool  # noqa: E402

ETA = 0.30

GATES = dict(
    noise_floor=1.0,
    min_fraction_of_max=0.25,
    amplitude_snr=5.0,
    coincidence_ev=0.5,
    max_total_seeds=2,
    smooth_points=5,
    fwhm_clip=(0.5, 2.0),
)


def _noisy(sig, level, seed):
    rng = np.random.default_rng(seed)
    return rng.poisson(np.maximum(sig + level, 0.0)).astype(float)


def _dominant_seed(center, fwhm=1.1, amp=40000.0, frac=1.0, snr=200.0):
    return {"role": "preseed_dominant_0", "center_be": center,
            "fwhm_init": fwhm, "amplitude_net": amp,
            "fraction_of_max": frac, "local_snr": snr}


def _find(pool, center, tol=0.35):
    return [f for f in pool.features
            if f.window is None and abs(f.center_be - center) <= tol]


# ── the two measured real-data loss classes, as synthetic stand-ins ───────

def test_pool_seeds_shoulder_class():
    """ds8 class: OOG dominant + no-local-max shoulder on its flank.  The
    shoulder must enter the pool with curvature provenance AND be seeded
    (the dominant channel structurally cannot see it)."""
    x = np.arange(186.0, 205.0, 0.05)
    dom_c, f = 191.0, 1.2
    sh_c = dom_c - 0.9 * f
    sig = (_pv(x, 40000.0, dom_c, f, ETA)
           + _pv(x, 12000.0, sh_c, f, ETA)
           + _pv(x, 9000.0, 196.5, 1.2, ETA))          # in-window main
    y = _noisy(sig, 300.0, seed=42)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x),
        all_windows=[(195.5, 197.5)],
        labeled_windows={"SYN:main_a": (195.5, 197.5)},
        dominant_seeds=[_dominant_seed(dom_c)],
        **GATES)

    sh = _find(pool, sh_c)
    assert sh, ("shoulder missing from the pool: "
                + str([round(f.center_be, 2) for f in pool.features
                       if f.window is None]))
    assert "curvature_shoulder" in sh[0].provenance
    assert sh[0].seeded_role == "preseed_curvature_0"
    assert sh[0].gate_fails == ()
    assert len(pool.curvature_seeds) == 1
    seed = pool.curvature_seeds[0]
    assert seed.center_be == pytest.approx(sh_c, abs=0.35)
    assert GATES["fwhm_clip"][0] <= seed.fwhm_init <= GATES["fwhm_clip"][1]
    assert seed.prom_z >= 7.0

    dom = _find(pool, dom_c)
    assert dom and dom[0].seeded_role == "preseed_dominant_0"
    assert "local_max" in dom[0].provenance


def test_pool_seeds_suppressed_second_max():
    """ds7/Scan_1 class: TWO resolved local maxima 0.9 eV apart; the blunt
    1.0 eV duplicate suppression upstream seeded only the first.  The pool's
    curvature channel must seed the second (provenance union: it is both a
    local max and a curvature ridge)."""
    x = np.arange(274.4, 293.5, 0.1)[:191]             # real grid geometry
    c1, c2, f = 278.4, 279.3, 1.1
    sig = (_pv(x, 22000.0, c1, f, ETA)
           + _pv(x, 19000.0, c2, f, ETA)
           + _pv(x, 9000.0, 287.0, 1.4, ETA))
    y = _noisy(sig, 1500.0, seed=7)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x),
        all_windows=[(284.0, 292.0)],
        labeled_windows={"C 1s:like": (284.0, 292.0)},
        dominant_seeds=[_dominant_seed(c1, amp=22000.0)],
        **GATES)

    second = _find(pool, c2, tol=0.3)
    assert second, "suppressed second maximum missing from the pool"
    ft = second[0]
    assert "curvature_shoulder" in ft.provenance
    assert ft.seeded_role == "preseed_curvature_0"
    assert ft.center_be == pytest.approx(c2, abs=0.2)
    assert len(pool.curvature_seeds) == 1


# ── overcompleteness with conservative seeding ─────────────────────────────

def test_pool_zero_seeds_on_covered_spectrum():
    """Every prominent feature inside grammar windows: pool lists them
    (honesty) but seeds NOTHING — grammar-covered spectra run unmodified."""
    x = np.arange(190.0, 205.0, 0.05)
    sig = (_pv(x, 9000.0, 196.5, 1.2, ETA)
           + _pv(x, 4000.0, 199.5, 1.4, ETA))
    y = _noisy(sig, 300.0, seed=11)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x),
        all_windows=[(195.5, 197.5), (198.5, 200.5)],
        labeled_windows={},
        dominant_seeds=[],
        **GATES)
    assert pool.curvature_seeds == []
    main = _find(pool, 196.5)
    assert main and main[0].in_grammar_window
    assert "in_grammar_window" in main[0].gate_fails
    assert main[0].seeded_role is None


def test_pool_zero_seeds_on_negatives():
    """No-hallucination pre-condition at the seeding layer: pure noise,
    linear drift, a single-point spike, a single broad peak, and a
    peakless step must seed NOTHING.  Backgrounds are ENGINE-computed
    (Shirley) as in production — a zeros background makes the height
    gates vacuous (the raw baseline masquerades as net signal), which is
    an input the engine never produces.  Pool-level curvature FEATURES on
    a negative draw are tolerated by design (measured H0 rate ~4%/spectrum
    at the prom_z gate); SEEDS are not."""
    from autofit.engine import _compute_background
    from autofit.grammar import BackgroundType

    x = np.arange(190.0, 205.0, 0.05)
    ys = []
    for seed in range(3):
        ys.append(_noisy(np.zeros_like(x), 500.0, 900 + seed))
        ys.append(_noisy(40.0 * (x - x[0]), 300.0, 910 + seed))
        ys.append(_noisy(_pv(x, 30000.0, 197.5, 3.5, ETA), 300.0, 920 + seed))
        step = 3000.0 / (1.0 + np.exp(-(x - 200.0) / 1.0))
        ys.append(_noisy(step, 500.0, 930 + seed))
        spiked = _noisy(np.zeros_like(x), 500.0, 940 + seed)
        spiked[100 + seed * 40] *= 12.0
        ys.append(spiked)

    for y in ys:
        bg = _compute_background(x, y, BackgroundType.SHIRLEY)
        pool = build_candidate_pool(
            x, y, bg, all_windows=[(195.5, 197.5)], labeled_windows={},
            dominant_seeds=[], **GATES)
        assert pool.curvature_seeds == []
        assert all(f.seeded_role is None for f in pool.features)


def test_pool_coincident_ridge_merges_with_dominant_seed():
    """The dominant peak's own CWT ridge must MERGE with the local-max
    feature (provenance union), never spawn a second seed at the same
    position."""
    x = np.arange(186.0, 205.0, 0.05)
    sig = _pv(x, 40000.0, 191.0, 1.2, ETA) + _pv(x, 9000.0, 196.5, 1.2, ETA)
    y = _noisy(sig, 300.0, seed=13)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x), all_windows=[(195.5, 197.5)],
        labeled_windows={}, dominant_seeds=[_dominant_seed(191.0)], **GATES)
    dom = _find(pool, 191.0, tol=0.3)
    assert len(dom) == 1, "dominant must be ONE merged pool feature"
    assert {"local_max", "curvature_shoulder"} <= set(dom[0].provenance)
    assert dom[0].seeded_role == "preseed_dominant_0"
    assert pool.curvature_seeds == []


def test_pool_seed_cap_respected_and_surfaced():
    """max_total_seeds bounds dominant+curvature seeds together; the
    over-cap feature stays in the pool with an explicit gate failure."""
    x = np.arange(182.0, 205.0, 0.05)
    sig = (_pv(x, 40000.0, 191.0, 1.2, ETA)            # dominant (seeded)
           + _pv(x, 24000.0, 187.0, 1.2, ETA)          # 2nd OOG feature
           + _pv(x, 20000.0, 184.0, 1.2, ETA)          # 3rd OOG feature
           + _pv(x, 9000.0, 196.5, 1.2, ETA))
    y = _noisy(sig, 300.0, seed=17)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x), all_windows=[(195.5, 197.5)],
        labeled_windows={}, dominant_seeds=[_dominant_seed(191.0)], **GATES)
    assert len(pool.curvature_seeds) == 1              # cap 2 − 1 dominant
    assert pool.curvature_seeds[0].center_be == pytest.approx(187.0, abs=0.3)
    third = _find(pool, 184.0, tol=0.3)
    assert third and "preseed_cap" in third[0].gate_fails


def test_pool_subfraction_curvature_candidate_not_seeded():
    """Codex review (run A finding 3): a curvature-channel candidate BELOW
    the 0.25 fraction-of-max dominance gate must NOT be seeded even with a
    strong prominence-z — it stays in the pool with the explicit
    'below_fraction_of_max' failure (that regime is residual-proposal
    territory, exactly like the dominant channel's weak-bump rule)."""
    x = np.arange(182.0, 205.0, 0.05)
    sig = (_pv(x, 40000.0, 191.0, 1.2, ETA)            # dominant (seeded)
           + _pv(x, 6000.0, 186.0, 1.2, ETA)           # 15% OOG feature —
           + _pv(x, 9000.0, 196.5, 1.2, ETA))          # strong z, sub-gate
    y = _noisy(sig, 300.0, seed=53)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x), all_windows=[(195.5, 197.5)],
        labeled_windows={}, dominant_seeds=[_dominant_seed(191.0)], **GATES)
    weak = _find(pool, 186.0, tol=0.3)
    assert weak, "the sub-gate feature must still be IN the pool (overcomplete)"
    ft = weak[0]
    assert "curvature_shoulder" in ft.provenance
    assert ft.prom_z is not None and ft.prom_z >= 7.0     # detected strongly
    assert ft.fraction_of_max is not None and ft.fraction_of_max < 0.25
    assert ft.seeded_role is None
    assert "below_fraction_of_max" in ft.gate_fails
    assert pool.curvature_seeds == []


def test_pool_seeds_in_crack_feature():
    """Stage-2 chokepoint 1 (measured: ds7's 289.8 at z=107 / 287.1 at
    z=273): a strong curvature feature whose center sits in a CRACK between
    grammar windows — inside the OLD ±margin zone but containable by NO
    slot — must be seeded.  Coverage claims require containment."""
    x = np.arange(186.0, 208.0, 0.05)
    crack_c = 198.0                                    # between the windows
    sig = (_pv(x, 40000.0, 191.0, 1.2, ETA)            # OOG dominant
           + _pv(x, 9000.0, 196.5, 1.2, ETA)           # in-window main
           + _pv(x, 12000.0, crack_c, 1.2, ETA)        # in-crack feature
           + _pv(x, 8000.0, 200.5, 1.4, ETA))          # second window species
    y = _noisy(sig, 300.0, seed=61)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x),
        all_windows=[(195.5, 197.7), (198.3, 201.5)],  # crack: 197.7–198.3
        labeled_windows={},
        dominant_seeds=[_dominant_seed(191.0)],
        **{**GATES, "max_total_seeds": 6})
    ft = _find(pool, crack_c, tol=0.3)
    assert ft, "in-crack feature missing from the pool"
    assert ft[0].seeded_role is not None, \
        f"in-crack feature not seeded: gate_fails={ft[0].gate_fails}"
    assert not ft[0].in_grammar_window
    # and the genuinely in-window species stays unseeded (containment)
    inwin = _find(pool, 200.5, tol=0.4)
    assert inwin and inwin[0].seeded_role is None
    assert "in_grammar_window" in inwin[0].gate_fails


def test_pool_trivia_floor_mechanics():
    """With the Stage-2 trivia floor (min_fraction_of_max=0.02): a ~1%
    curvature blip stays unseeded; a ~6% flank species (the measured
    ds8-class expert-modeled regime) seeds."""
    x = np.arange(182.0, 205.0, 0.05)
    sig = (_pv(x, 40000.0, 191.0, 1.2, ETA)
           + _pv(x, 2400.0, 186.5, 1.3, ETA)           # 6% species
           + _pv(x, 9000.0, 196.5, 1.2, ETA))
    y = _noisy(sig, 300.0, seed=67)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x), all_windows=[(195.5, 197.5)],
        labeled_windows={}, dominant_seeds=[_dominant_seed(191.0)],
        **{**GATES, "min_fraction_of_max": 0.02, "max_total_seeds": 6})
    flank = _find(pool, 186.5, tol=0.3)
    assert flank and flank[0].seeded_role is not None, \
        f"6% flank species must seed under the trivia floor: " \
        f"{flank[0].gate_fails if flank else 'ABSENT'}"
    assert flank[0].fraction_of_max < 0.25   # would have failed the old gate


def test_pool_grammar_entries_present():
    x = np.arange(190.0, 205.0, 0.05)
    y = _noisy(_pv(x, 9000.0, 196.5, 1.2, ETA), 300.0, seed=19)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x), all_windows=[(195.5, 197.5)],
        labeled_windows={"SYN:main_a": (195.5, 197.5)},
        dominant_seeds=[], **GATES)
    gram = [f for f in pool.features if f.provenance == ("grammar",)]
    assert len(gram) == 1
    assert gram[0].window == (195.5, 197.5)
    assert gram[0].label == "SYN:main_a"


def test_pool_payload_is_json_safe_and_carries_tunables():
    x = np.arange(186.0, 205.0, 0.05)
    sig = _pv(x, 40000.0, 191.0, 1.2, ETA) + _pv(x, 9000.0, 196.5, 1.2, ETA)
    y = _noisy(sig, 300.0, seed=23)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x), all_windows=[(195.5, 197.5)],
        labeled_windows={"SYN:main_a": (195.5, 197.5)},
        dominant_seeds=[_dominant_seed(191.0)], **GATES)
    payload = pool.payload()
    s = json.dumps(payload)          # must not raise (no numpy scalars)
    assert "UNVERIFIED" in s
    assert payload["sources_run"] == ["local_max", "curvature_shoulder",
                                      "grammar"]
    assert any(f["provenance"] == ["local_max", "curvature_shoulder"]
               or f["provenance"] == ["curvature_shoulder", "local_max"]
               for f in payload["features"])
    assert all("gate_fails" in f and "seeded_role" in f
               for f in payload["features"])


def test_pool_descending_grid_equivalence():
    x = np.arange(186.0, 205.0, 0.05)
    dom_c, f = 191.0, 1.2
    sh_c = dom_c - 0.9 * f
    sig = (_pv(x, 40000.0, dom_c, f, ETA) + _pv(x, 12000.0, sh_c, f, ETA)
           + _pv(x, 9000.0, 196.5, 1.2, ETA))
    y = _noisy(sig, 300.0, seed=42)
    kw = dict(all_windows=[(195.5, 197.5)], labeled_windows={},
              dominant_seeds=[_dominant_seed(dom_c)], **GATES)
    asc = build_candidate_pool(x, y, np.zeros_like(x), **kw)
    desc = build_candidate_pool(x[::-1], y[::-1], np.zeros_like(x), **kw)
    assert [s.center_be for s in asc.curvature_seeds] == \
           pytest.approx([s.center_be for s in desc.curvature_seeds], abs=1e-9)
    assert len(asc.features) == len(desc.features)


def test_pool_local_max_chaff_filtered():
    """Pure-noise smoothed local maxima (local_snr ~ 0.4 above the computed
    background) stay OUT of the pool payload — overcomplete does not mean
    noise-transcript.  Background as the engine supplies it (its detection
    background, which absorbs the flat baseline)."""
    from autofit.engine import _compute_background
    from autofit.grammar import BackgroundType

    x = np.arange(190.0, 205.0, 0.05)
    y = _noisy(np.zeros_like(x), 500.0, seed=31)
    bg = _compute_background(x, y, BackgroundType.SHIRLEY)
    pool = build_candidate_pool(
        x, y, bg, all_windows=[], labeled_windows={},
        dominant_seeds=[], **GATES)
    assert [f for f in pool.features if f.window is None] == []


def test_pool_every_unseeded_feature_says_why():
    """Honesty surface completeness: every detection entry that is NOT
    seeded carries at least one gate_fails reason (incl. local-max-only
    entries whose seeding decision happened upstream)."""
    x = np.arange(274.4, 293.5, 0.1)[:191]
    sig = (_pv(x, 22000.0, 278.4, 1.1, ETA)
           + _pv(x, 19000.0, 279.3, 1.1, ETA)
           + _pv(x, 9000.0, 287.0, 1.4, ETA))
    y = _noisy(sig, 1500.0, seed=7)
    pool = build_candidate_pool(
        x, y, np.zeros_like(x), all_windows=[(284.0, 292.0)],
        labeled_windows={},
        dominant_seeds=[_dominant_seed(278.4, amp=22000.0)], **GATES)
    for ft in pool.features:
        if ft.window is None and ft.seeded_role is None:
            assert ft.gate_fails, f"unseeded {ft.center_be} gives no reason"
