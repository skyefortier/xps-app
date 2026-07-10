"""
REAL-DATA acceptance gates for the candidate-generation fix (2026-07-10).

The raw spectra are LOCAL-ONLY (unpublished; never committed — privacy
rail); these tests SKIP LOUDLY when the data directories are absent.
Numeric positions here are measured expectations, same policy as the
positions already recorded in PROGRESS.md.

ANTI-OVERFIT: the detector/gate constants were frozen from synthetic
calibration BEFORE these scans were evaluated (scripts/
calibrate_cwt_detector.py); this file is the HELD-OUT confirmation, not a
tuning target.

DETECTION BAR (cheap, no fits — runs whenever the local data exists):
on BOTH datasets, the class-defining features the old pipeline lost enter
the candidate pool with provenance AND are seeded:
- ds7/C1s Scan_1: the ~279.3 eV feature (a gate-passing second local max
  that PRESEED_MIN_SEPARATION_BE discarded, 0.90 eV from the dominant)
- ds7/C1s Scan_5: the same physics charge-shifted (+~1.5 eV -> 280.8)
- ds8/C1s Scan, Scan_0, Scan_2: the low-BE shoulder (~278.6-278.7) with NO
  local maximum — structurally invisible to any local-max detector.
Two-sided: scans WITHOUT the class feature must gain NO curvature seeds.

INTEGRATION BAR (env-gated RUN_AUTOFIT_GATE=1, ~10 min): the full IC
pipeline emits the seeded components in its final model on one scan per
dataset.
"""

import glob
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

REPO = Path(__file__).resolve().parents[2]
DS7 = REPO / "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
DS8 = (REPO / "docs/autofit/test_data/"
       "8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, "
       "400 um.DATA")

pytestmark = pytest.mark.skipif(
    not (DS7.is_dir() and DS8.is_dir()),
    reason=("LOUD SKIP — real held-out C 1s datasets not present at "
            "docs/autofit/test_data/{7,8}* (local-only, never committed); "
            "the detection acceptance bar was NOT evaluated"),
)

# (dataset dir, scan file stem) -> expected seeded curvature feature window
EXPECTED_SEEDED = {
    ("ds7", "C1s Scan_1"): (279.15, 279.50),   # the goal's ~279.3 feature
    ("ds7", "C1s Scan_5"): (280.65, 281.00),   # same class, charge-shifted
    ("ds8", "C1s Scan"): (278.40, 279.00),     # no-local-max shoulder
    ("ds8", "C1s Scan_0"): (278.50, 279.10),
    ("ds8", "C1s Scan_2"): (278.40, 279.00),
}


def _scans():
    out = []
    for ds, dsdir in (("ds7", DS7), ("ds8", DS8)):
        for path in sorted(glob.glob(f"{dsdir}/C1s*.VGD")):
            out.append((ds, Path(path).stem, path))
    return out


@pytest.fixture(scope="module")
def c1s_grammar():
    from autofit.grammar import MaterialClass, Phase, resolve
    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
                  regions=("C 1s",), material="graphite")
    return resolve([phase], "C 1s", allow_structural_fallback=True)


def _pool_for(path, grammar):
    import autofit.engine as eng
    from autofit.candidates import build_candidate_pool
    from vgd_parser import parse_vgd

    be, cts = parse_vgd(path)
    x = np.asarray(be, dtype=float)
    y = np.asarray(cts, dtype=float)
    cands = grammar.candidates
    diag = dict(grammar.diagnostic_windows)
    det_bg = eng._compute_background(x, y, cands[0].background)
    dom = eng.detect_out_of_grammar_dominants(x, y, det_bg, cands, diag)
    pool = build_candidate_pool(
        x, y, det_bg,
        all_windows=eng._all_grammar_windows(cands, diag),
        labeled_windows=diag,
        dominant_seeds=[s.payload() for s in dom],
        window_margin_ev=eng._preseed_window_margin(cands),
        noise_floor=1.0,
        min_fraction_of_max=eng.PRESEED_MIN_FRACTION_OF_MAX,
        amplitude_snr=eng.PRESEED_AMPLITUDE_SNR,
        coincidence_ev=eng.PROPOSAL_COINCIDENCE_BE,
        max_total_seeds=eng.PRESEED_MAX,
        smooth_points=eng.PRESEED_SMOOTH_POINTS,
        fwhm_clip=(eng.PROPOSAL_FWHM_MIN, eng.PROPOSAL_FWHM_MAX),
        local_window_ev=eng.PROPOSAL_WINDOW_WIDTH,
    )
    return pool, dom, (x, y)


def test_detection_bar_all_real_scans(c1s_grammar):
    """THE detection bar (goal): on BOTH datasets every class-defining
    lost feature ENTERS the pool with provenance and is seeded; scans
    without the class feature gain NO curvature seeds (two-sided)."""
    seen = set()
    for ds, scan, path in _scans():
        pool, dom, _ = _pool_for(path, c1s_grammar)
        assert len(dom) >= 1, f"{ds}/{scan}: dominant channel lost its seed"

        expected = EXPECTED_SEEDED.get((ds, scan))
        if expected is not None:
            seen.add((ds, scan))
            lo, hi = expected
            hits = [s for s in pool.curvature_seeds if lo <= s.center_be <= hi]
            assert hits, (
                f"{ds}/{scan}: expected seeded curvature feature in "
                f"[{lo}, {hi}]; pool seeds = "
                f"{[round(s.center_be, 2) for s in pool.curvature_seeds]}")
            seed = hits[0]
            assert seed.prom_z >= 7.0
            feat = next(f for f in pool.features
                        if f.seeded_role == seed.role)
            assert "curvature_shoulder" in feat.provenance
            assert not feat.in_grammar_window
        else:
            # two-sided: no class feature -> no curvature seeds; sub-gate
            # features stay visible with explicit gate failures
            assert pool.curvature_seeds == [], (
                f"{ds}/{scan}: unexpected curvature seed(s) "
                f"{[round(s.center_be, 2) for s in pool.curvature_seeds]}")
            for f in pool.features:
                if f.window is None and f.seeded_role is None:
                    assert f.gate_fails, (
                        f"{ds}/{scan}: unseeded {f.center_be} without a "
                        "recorded gate failure")
    assert seen == set(EXPECTED_SEEDED), \
        f"expected scans missing from the data dir: {set(EXPECTED_SEEDED) - seen}"


@pytest.mark.skipif(os.environ.get("RUN_AUTOFIT_GATE") != "1",
                    reason="LOUD SKIP — integration bar (full IC pipeline, "
                           "~10 min) runs with RUN_AUTOFIT_GATE=1")
@pytest.mark.parametrize("ds,scan,window", [
    ("ds7", "C1s Scan_1", (279.0, 279.7)),
    ("ds8", "C1s Scan", (278.3, 279.2)),
])
def test_integration_bar_selection_keeps_seeded_feature(
        c1s_grammar, ds, scan, window):
    """INTEGRATION bar (secondary): the EXISTING selection layer, given the
    seeded pool, emits the class feature in its final model."""
    from autofit.methods import get_method
    from vgd_parser import parse_vgd

    dsdir = DS7 if ds == "ds7" else DS8
    be, cts = parse_vgd(str(dsdir / f"{scan}.VGD"))
    x = np.asarray(be, dtype=float)
    y = np.asarray(cts, dtype=float)
    res = get_method("ic_model_comparison").run(
        x, y, grammar=c1s_grammar, peak_specs=None,
        options={"n_refits": 4, "rng_seed": 0, "enable_proposal_pass": True})
    assert res.success
    feats = res.analysis["preseeded_features"]
    lo, hi = window
    assert any(f["provenance"] == "curvature_shoulder"
               and lo <= f["center_be"] <= hi for f in feats), feats
    emitted = [p for p in res.peaks
               if p["role"].startswith("preseed_curvature_")
               and lo <= p["center"] <= hi]
    assert emitted, (
        f"{ds}/{scan}: seeded feature not in the final model; peaks = "
        f"{[(p['role'], round(p['center'], 2)) for p in res.peaks]}")
    assert emitted[0]["region"] == "unassigned"
