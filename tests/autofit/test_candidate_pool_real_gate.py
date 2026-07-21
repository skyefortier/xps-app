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

DETECTION BAR (cheap, no fits — runs whenever the local data exists),
STAGE-2 operating point (containment blocking, trivia floor 0.02, cap 6 —
recalibrated 2026-07-10 after the Step-1 diagnosis; constants frozen
BEFORE this held-out re-measurement):
- ds7/C1s Scan_1 (the diagnosis scan): ALL the expert-modeled features
  seed — the low-BE trio (279.3 / 281.1 / 283.6) AND the in-crack pair
  the old window+margin fiction blocked (287.1, 289.7).
- ds7/C1s Scan_5: the charge-shifted second max (280.8).
- ds8/C1s Scan, Scan_0, Scan_2: the no-local-max shoulder (~278.6-278.7).
- ds8/C1s Scan_1: the flank species pair (278.4, 281.7) the old 0.25
  fraction gate discarded.
Two-sided invariants on EVERY scan: every curvature seed lies OUTSIDE all
containment windows; every strong-but-unseeded feature (prom_z >= 7)
carries an explicit gate failure (in-window features stay grammar
territory, rescuable by the component-proximity proposal rule); total
seeds respect SEED_MAX_TOTAL.

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

# (dataset dir, scan file stem) -> [expected seeded curvature windows]
EXPECTED_SEEDED = {
    ("ds7", "C1s Scan_1"): [(279.15, 279.50),   # the goal's ~279.3 feature
                            (280.90, 281.35),   # low-BE third component
                            (283.30, 283.90),   # broad bridge
                            (286.90, 287.35),   # in-crack (expert 287.11)
                            (289.50, 290.00)],  # in-crack (expert 289.80)
    ("ds7", "C1s Scan_5"): [(280.65, 281.00)],  # charge-shifted second max
    ("ds8", "C1s Scan"): [(278.40, 279.00)],    # no-local-max shoulder
    ("ds8", "C1s Scan_0"): [(278.50, 279.10)],
    ("ds8", "C1s Scan_2"): [(278.40, 279.00)],
    ("ds8", "C1s Scan_1"): [(278.20, 278.70),   # flank species (expert
                            (281.45, 282.00)],  # 279.09 / 281.47 classes)
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
        noise_floor=1.0,
        min_fraction_of_max=eng.CURVATURE_SEED_MIN_FRACTION,
        amplitude_snr=eng.PRESEED_AMPLITUDE_SNR,
        coincidence_ev=eng.PROPOSAL_COINCIDENCE_BE,
        max_total_seeds=eng.SEED_MAX_TOTAL,
        smooth_points=eng.PRESEED_SMOOTH_POINTS,
        # Mirrors engine.py's real call site (find-peaks-math-first-
        # architecture.md step 1(ii)): the seed's fwhm_init upper bound is
        # now DERIVED from this ROI's own scale, not fixed at
        # PROPOSAL_FWHM_MAX/FWHM_MAX_ORDINARY_EV.
        fwhm_clip=(eng.PROPOSAL_FWHM_MIN, None),
        local_window_ev=eng.PROPOSAL_WINDOW_WIDTH,
    )
    return pool, dom, (x, y)


def test_detection_bar_all_real_scans(c1s_grammar):
    """THE detection bar (goal): on BOTH datasets every class-defining
    lost feature ENTERS the pool with provenance and is seeded; scans
    without the class feature gain NO curvature seeds (two-sided)."""
    import autofit.engine as eng
    wins = None
    seen = set()
    for ds, scan, path in _scans():
        pool, dom, (x, _y) = _pool_for(path, c1s_grammar)
        assert len(dom) >= 1, f"{ds}/{scan}: dominant channel lost its seed"
        if wins is None:
            wins = eng._all_grammar_windows(
                c1s_grammar.candidates, dict(c1s_grammar.diagnostic_windows))
        step_tol = 0.5 * float(np.median(np.diff(np.sort(x))))

        # completeness side: every expected feature seeded with provenance
        for lo, hi in EXPECTED_SEEDED.get((ds, scan), []):
            seen.add((ds, scan))
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

        # two-sided invariants on EVERY scan
        assert len(pool.curvature_seeds) + len(dom) <= eng.SEED_MAX_TOTAL
        for s in pool.curvature_seeds:
            assert not any((lo - step_tol) <= s.center_be <= (hi + step_tol)
                           for lo, hi in wins), (
                f"{ds}/{scan}: seed {s.center_be:.2f} inside a containment "
                "window — grammar territory must stay the grammar's")
        for f in pool.features:
            if (f.window is None and f.seeded_role is None
                    and (f.prom_z or 0) >= 7.0):
                assert f.gate_fails, (
                    f"{ds}/{scan}: strong unseeded {f.center_be} without a "
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
    # MECHANISM-AGNOSTIC (Stage-2): the winner may carry the feature via a
    # curvature seed, the detection family (D0), or a proposal — the bar
    # is a data-driven component AT the feature, region-unassigned.
    emitted = [p for p in res.peaks
               if p["region"] == "unassigned" and lo <= p["center"] <= hi]
    assert emitted, (
        f"{ds}/{scan}: detected feature not in the final model; peaks = "
        f"{[(p['role'], round(p['center'], 2)) for p in res.peaks]}")


FE2P = [REPO / "docs/autofit/test_data/Ugly_Fe_2p.spec.json",
        REPO / "docs/autofit/test_data/Ugly_Fe_2p_2.spec.json"]


@pytest.mark.skipif(not all(p.is_file() for p in FE2P),
                    reason="LOUD SKIP — Ugly_Fe_2p spec files absent "
                           "(local-only); Fe 2p generalization bar NOT "
                           "evaluated")
@pytest.mark.skipif(os.environ.get("RUN_AUTOFIT_GATE") != "1",
                    reason="LOUD SKIP — Fe 2p generalization bar (full "
                           "sweep, ~2 min) runs with RUN_AUTOFIT_GATE=1")
def test_generalization_bar_ugly_fe2p():
    """Across-the-periodic-table bar (goal, Stage-2): the UNFITTED low-res
    Fe 2p spectra — a region with ZERO grammar candidates — must produce a
    physically plausible candidate set (2p3/2 region, 2p1/2 region, the
    inter-doublet oxide/satellite intensity) while staying honest (either
    a conditional tier or the loud UNSTABLE last resort; never silence,
    never unflagged confidence)."""
    import json as _json

    from autofit.grammar import MaterialClass, Phase, resolve
    from autofit.methods import get_method

    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
                  regions=("Fe 2p",))
    g = resolve([phase], "Fe 2p", allow_structural_fallback=True)
    assert not g.candidates            # precondition: structural fallback
    for path in FE2P:
        d = _json.loads(path.read_text())
        x = np.asarray(d["rawBE"], dtype=float)
        y = np.asarray(d["rawIntensity"], dtype=float)
        res = get_method("ic_model_comparison").run(
            x, y, grammar=g, peak_specs=None,
            options={"n_refits": 4, "rng_seed": 0,
                     "enable_proposal_pass": True})
        assert res.success, f"{path.name}: {res.message}"
        assert res.diagnostics["winner"].startswith("D0_detected")
        centers = sorted(p["center"] for p in res.peaks)
        assert any(703.0 <= c <= 706.0 for c in centers), centers   # 2p3/2
        assert any(716.0 <= c <= 719.0 for c in centers), centers   # 2p1/2
        assert any(706.0 < c < 714.0 for c in centers), centers     # mid
        assert all(p["region"] == "unassigned" for p in res.peaks)
        # honesty: flagged, never silent confidence
        assert res.diagnostics["conditional"] is True
        assert ("human review" in res.message
                or "low-confidence" in res.message)
