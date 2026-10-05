"""The ALTERNATIVE restore comparison, measured for the owner (background math, 2026-10-03).

Before this unit the page SAVED its own 5-iteration preview background beside the
SERVER's fit, which the server made against its own converged background — so for an
older server fit the stored curve is not the background the fit used. That background
is recoverable from what the save does hold: the stored envelope (the server's
fitted_y, raw level) minus the saved fitted peaks. This compares THAT implied
background with the one the record's settings give now, at the owner's rule's
tolerance (fit_equality.SAME_MINIMUM_REL of the background's own scale), on every
committed saved fit — under BOTH window rules: the old request's (nearest index,
end-exclusive, `ReferenceFit.bg_indices`) and today's (`_bgWindowIndices`: inclusive).

The fit's points are found as the page finds them (`_restoredFitGrid`): the stored
energies are the raw samples (exactly or as saved to 4 dp), or — when the charge
correction changed after the fit, so they sit at a constant offset — the run of samples
whose counts reproduce the fit's own record (stored background + subtracted counts, else
its stored RMSE). Until 2026-10-03 an offset run was taken at the FIRST position that
fitted, which on a uniform grid is any position: 16 fits were compared on samples
2.4-6 eV away from their own.

    venv/bin/python scripts/bg_math_restore_alternative.py [--json OUT]
"""
import argparse
import collections
import glob
import json
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path[:0] = [ROOT, os.path.join(ROOT, "tests")]
import fitting  # noqa: E402
from fit_equality import SAME_MINIMUM_REL  # noqa: E402
from autofit.parity import background_like_run_fit, evaluate_model, recorded_voigt_eta  # noqa: E402
from autofit.reference import load_reference_fits  # noqa: E402

def r4(v):
    return np.round(np.asarray(v, float) * 1e4) / 1e4


def fit_grid(rf):
    """(x, y, model_x) as the page's _restoredFitGrid: every reading that reproduces the
    stored energies (the ROI selection, an in-order match exact / 4 dp, every constant-offset
    run), the fit's record (stored counts, else its RMSE) choosing among several; the
    components evaluated at the samples' own energies (no key in the committed saves: the
    saved peaks, today's frame). None when unresolved."""
    fr = rf.fit_result
    stored = np.asarray(fr.get("be") or [], float)
    corr, inten = np.asarray(rf.corrected_be, float), np.asarray(rf.raw_intensity, float)
    n = len(stored)
    if n == 0:
        return None
    cands = {}
    def add(idx):
        if idx is not None and len(idx) == n:
            cands[tuple(idx)] = list(idx)
    roi = np.nonzero(rf.roi_mask)[0]
    if len(roi) == n and np.all((corr[roi] == stored) | (r4(corr[roi]) == stored)):
        add(roi)
    for rounded in (False, True):
        idx, k = [], 0
        for i in range(len(corr)):
            if k < n and (corr[i] == stored[k] or (rounded and r4(corr[i]) == stored[k])):
                idx.append(i); k += 1
        add(idx)
    for j in range(len(corr) - n + 1):
        c = corr[j:j + n] + (stored[0] - corr[j])
        if np.all((c == stored) | (r4(c) == r4(stored))):
            add(range(j, j + n))
    cl = list(cands.values())
    if not cl:
        return None
    pick = cl[0]
    if len(cl) > 1:
        bs, bi, fy, rmse = fr.get("bgSubtracted"), fr.get("bgIntensity"), fr.get("fittedY"), fr.get("rmse")
        seen = (np.asarray(bs, float) + np.asarray(bi, float)
                if isinstance(bs, list) and isinstance(bi, list) and len(bs) == n and len(bi) == n else None)
        by_rmse = seen is None and isinstance(rmse, (int, float)) and isinstance(fy, list) and len(fy) == n
        if seen is None and not by_rmse:
            return None
        def dev(idx):
            if seen is not None:
                return float(np.max(np.abs(seen - inten[idx])))
            return abs(float(np.sqrt(np.mean((inten[idx] - np.asarray(fy, float)) ** 2))) - rmse)
        scored = sorted((dev(c), k, c) for k, c in enumerate(cl))
        if not (scored[0][0] < scored[1][0]):
            return None
        pick = scored[0][2]
    pick = np.asarray(pick)
    return corr[pick], inten[pick], corr[pick]


def legacy_voigts(rf):
    out = []
    for p in rf.peaks:
        if p.get("shape") == "Voigt":
            v = recorded_voigt_eta(p)
            if v is not None and v != 0.5:
                out.append((p.get("name"), v))
    return out


def today_window(rf, x):
    """_bgWindowIndices (both bounds parse, else the whole grid; inclusive), as a [i0, i1) slice."""
    try:
        a, b = float(rf.ui.get("bgStart")), float(rf.ui.get("bgEnd"))
    except (TypeError, ValueError):
        return 0, len(x)
    if not (np.isfinite(a) and np.isfinite(b)):
        return 0, len(x)
    idx = np.nonzero((x >= min(a, b)) & (x <= max(a, b)))[0]
    return (int(idx[0]), int(idx[-1]) + 1) if len(idx) >= 2 else (0, len(x))


def old_window(rf, x):
    be = x
    s = rf.ui.get("bgStart"); e = rf.ui.get("bgEnd")
    try: bs = float(s)
    except (TypeError, ValueError): bs = be[0]
    try: be_ = float(e)
    except (TypeError, ValueError): be_ = be[-1]
    return int(np.argmin(np.abs(be - bs))), int(np.argmin(np.abs(be - be_)))


ap = argparse.ArgumentParser()
ap.add_argument("--json")
a = ap.parse_args()
rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "docs/autofit/test_data/*.proj.zip"))):
    for rf in load_reference_fits(f):
        row = {"project": rf.project, "tab": rf.name, "bgType": (rf.ui or {}).get("bgType")}
        fy = rf.fit_result.get("fittedY")
        if not isinstance(fy, list) or not fy:
            row["verdict"] = "no stored envelope"; rows.append(row); continue
        g = fit_grid(rf)
        fy = np.asarray([np.nan if v is None else v for v in fy], float)
        if g is None or len(fy) != len(g[0]):
            row["verdict"] = "envelope on other points"; rows.append(row); continue
        x, y, mx = g
        specs = rf.backend_peak_specs()
        specs = [dict(s, gl_ratio=recorded_voigt_eta(p)) if p.get("shape") == "Voigt" and recorded_voigt_eta(p) is not None else s
                 for s, p in zip(specs, rf.peaks)]
        implied = fy - evaluate_model(mx, specs)
        for rule, (i0, i1) in (("old", old_window(rf, x)), ("today", today_window(rf, x))):
            try:
                now = background_like_run_fit(x, y, rf.bg_method, i0, i1, rf.endpoint_avg)
            except fitting.BackgroundNotConverged as e:
                row[rule] = None; row["why"] = str(e)[:80]; continue
            scale = max(float(np.max(np.abs(implied))), float(np.max(np.abs(now))))
            env = max(float(np.max(np.abs(fy))), float(np.max(np.abs(fy - implied))))
            d = float(np.max(np.abs(implied - now)))
            row[rule] = d / scale if scale else (0.0 if d == 0 else float("inf"))
            row[rule + "_ok"] = d <= SAME_MINIMUM_REL * scale + fitting.BG_REL_TOL * env
        row["voigt"] = legacy_voigts(rf)
        ok = [row.get(r + "_ok", False) for r in ("old", "today")]
        row["verdict"] = ("reloads (today's window)" if ok[1] else "differs (today's window only)" if ok[0]
                          else "differs (either window)")
        if row["voigt"] and ok[1]:
            row["verdict"] = "stale (pre-A03 Voigt only)"
        rows.append(row)
c = collections.Counter(r["verdict"] for r in rows)
print(f"{len(rows)} saved fits: {dict(c)}")
for r in sorted((r for r in rows if r["verdict"] == "differs (either window)"), key=lambda r: -(r["today"] or 0)):
    print(f"  differs under either window: {r['project'][:30]:30s} {r['tab']:16s} {r['bgType']:9s} "
          f"today {100 * r['today']:.3g} %, old window {100 * r['old']:.3g} % of its own scale")
win = sorted(100 * r["today"] for r in rows if r["verdict"] == "differs (today's window only)")
if win:
    print(f"  differs only through today's window: {len(win)}, median {np.median(win):.3g} %, max {win[-1]:.3g} %")
for r in rows:
    if r.get("voigt"):
        print(f"  pre-A03 Voigt: {r['project'][:30]:30s} {r['tab']:16s} {r['voigt']} -> {r['verdict']}")
ok = [r["today"] for r in rows if r["verdict"].startswith("reloads")]
if ok:
    print(f"reloads: implied vs recomputed median {np.median(ok):.2e}, max {max(ok):.2e} of the background's own scale")
if a.json:
    json.dump(rows, open(a.json, "w"), indent=1)
