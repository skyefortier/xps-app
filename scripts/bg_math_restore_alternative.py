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


def fit_grid(rf, amp_bound=0.0):
    """(x, y, model_x) as the page's _restoredFitGrid (Codex impl rounds 18-20): every
    in-order assignment of raw samples to the stored energies at one offset, within the
    save's 4-dp rounding (h) and the arithmetic, branching where two samples fit; each must
    meet the fit's RMSE within the old upload's 0.005 plus the arithmetic; the stored counts
    (6 significant figures) choose among those left; several distinct survivors refuse.
    No key in the committed saves: the offset is searched. None when unresolved."""
    U = 2.0 ** -53
    fr = rf.fit_result
    stored = [float(v) for v in fr.get("be") or []]
    corr = [float(v) for v in np.asarray(rf.corrected_be, float)]
    I = [float(v) for v in np.asarray(rf.raw_intensity, float)]
    n, N = len(stored), len(corr)
    if n == 0:
        return None
    h = 5e-5 if all(round(v * 1e4) / 1e4 == v for v in stored) else 0.0
    order = sorted((i for i in range(N) if np.isfinite(corr[i])), key=lambda i: corr[i])
    sc = [corr[i] for i in order]
    import bisect
    eps = lambda a, b: 4 * U * (abs(a) + abs(b))
    def within(k, lo, hi):
        a, b = stored[k] - h - hi, stored[k] + h - lo
        pad = eps(stored[k], max(abs(a), abs(b)))
        t = bisect.bisect_left(sc, a - pad)
        out = []
        while t < len(sc) and sc[t] <= b + pad:
            out.append(order[t]); t += 1
        return out
    fy = fr.get("fittedY"); rmse = fr.get("rmse")
    has_rmse = isinstance(rmse, (int, float)) and np.isfinite(rmse) and isinstance(fy, list) and len(fy) == n
    bs, bi = fr.get("bgSubtracted"), fr.get("bgIntensity")
    has_counts = (isinstance(bs, list) and isinstance(bi, list) and len(bs) == n and len(bi) == n
                  and all(isinstance(v, (int, float)) for v in bs + bi))
    sig6 = has_counts and all(float(f"{v:.6g}") == v for v in bs + bi)
    half6 = lambda v: 0.0 if v == 0 else 0.5 * 10.0 ** (np.floor(np.log10(abs(v))) - 5)
    pow10 = lambda v: f"{abs(v):.5e}".startswith("1.00000e")
    below = lambda v: 0.0 if v == 0 else (half6(v) / 10 if v > 0 and pow10(v) else half6(v))
    above = lambda v: 0.0 if v == 0 else (half6(v) / 10 if v < 0 and pow10(v) else half6(v))
    max_i = max((abs(v) for v in I if np.isfinite(v)), default=0.0)
    max_f = max((abs(float(v)) for v in fy), default=0.0) if has_rmse else 0.0
    def rmse_ok(c):
        if not has_rmse:
            return True
        r = [I[c[k]] - fy[k] for k in range(n)]
        big = max_i + max_f + 2 * amp_bound          # path-independent, as the page (Codex impl round 26)
        rc = np.sqrt(sum(v * v for v in r) / n)
        return abs(rc - rmse) <= 0.005 + 8 * U * big + (n + 4) * U * (rc + abs(rmse))
    def counts_ok(c):
        for k in range(n):
            a = 16 * U * (abs(bs[k]) + abs(bi[k]) + abs(I[c[k]]))
            lo = (below(bs[k]) + below(bi[k]) if sig6 else 0.0) + a
            hi = (above(bs[k]) + above(bi[k]) if sig6 else 0.0) + a
            d = I[c[k]] - (bs[k] + bi[k])
            if not (-lo <= d <= hi):
                return False
        return True
    ok, amb = {}, False
    def search(lo0, hi0):
        stack, steps = [(0, -1, lo0, hi0, ())], 0
        while stack:
            k, prev, lo, hi, idx = stack.pop()
            if k == n:
                if rmse_ok(idx) and idx not in ok:
                    ok[idx] = (idx, lo, hi)
                continue
            for i in within(k, lo, hi):
                if i <= prev:
                    continue
                e = eps(stored[k], corr[i])
                nlo, nhi = max(lo, stored[k] - h - corr[i] - e), min(hi, stored[k] + h - corr[i] + e)
                if nlo <= nhi:
                    stack.append((k + 1, i, nlo, nhi, idx + (i,)))
            steps += 1
            if steps > 64 * (n + 1):
                return True
        return False
    tried = set()
    for j in range(N):
        if not np.isfinite(corr[j]):
            continue
        d = stored[0] - corr[j]
        if d in tried:
            continue
        tried.add(d)
        e = eps(stored[0], corr[j])
        if search(d - h - e, d + h + e):
            return None
    cl = list(ok.values())
    if has_counts and (len(cl) > 1 or not has_rmse):
        bc = [r for r in cl if counts_ok(r[0])]
        if bc or not has_rmse:
            cl = bc
    if not cl:
        return None
    first = cl[0][0]
    if not all(all(corr[i] == corr[first[k]] and I[i] == I[first[k]] for k, i in enumerate(r[0])) for r in cl):
        return None
    moved = all(not (lo <= 0 <= hi) for _, lo, hi in cl)
    pick = np.asarray(first)
    c = np.asarray(corr)
    return c[pick], np.asarray(I)[pick], c[pick], moved


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
        g = fit_grid(rf, 2 * sum(abs(float(p.get("amplitude") or 0)) for p in rf.peaks))
        fy = np.asarray([np.nan if v is None else v for v in fy], float)
        if g is None or len(fy) != len(g[0]):
            row["verdict"] = "envelope on other points"; rows.append(row); continue
        x, y, mx, moved = g
        specs = rf.backend_peak_specs()
        specs = [dict(s, gl_ratio=recorded_voigt_eta(p)) if p.get("shape") == "Voigt" and recorded_voigt_eta(p) is not None else s
                 for s, p in zip(specs, rf.peaks)]
        # the committed fits predate the full-precision upload and carry no key: the server
        # evaluated them at toFixed(4) energies (the page's rule); a local-engine fit at its own
        from decimal import Decimal, ROUND_HALF_UP
        to4 = (np.asarray(mx, float) if rf.fit_result.get("engine") == "local" else
               np.array([float(Decimal(float(v)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)) for v in mx]))
        m0 = evaluate_model(to4, specs)
        sens = np.zeros_like(m0)         # no allowance (Codex impl round 22): uncertainty can only read as a difference
        implied = fy - m0
        for rule, (i0, i1) in (("old", old_window(rf, x)), ("today", today_window(rf, x))):
            try:
                now = background_like_run_fit(x, y, rf.bg_method, i0, i1, rf.endpoint_avg)
            except fitting.BackgroundNotConverged as e:
                row[rule] = None; row["why"] = str(e)[:80]; continue
            scale = max(float(np.max(np.abs(implied))), float(np.max(np.abs(now))))
            env = max(float(np.max(np.abs(fy))), float(np.max(np.abs(fy - implied))))
            d = float(np.max(np.abs(implied - now)))
            beyond = float(np.max(np.maximum(0.0, np.abs(implied - now) - sens)))
            row[rule] = d / scale if scale else (0.0 if d == 0 else float("inf"))
            row[rule + "_ok"] = beyond <= SAME_MINIMUM_REL * scale + fitting.BG_REL_TOL * env
        row["voigt"] = legacy_voigts(rf)
        ok = [row.get(r + "_ok", False) for r in ("old", "today")]
        # owner 2026-10-05: without the fit's own key its charge frame is not on record, so a
        # keyless fit is never confirmed current (whether its stored energies show a move or not)
        row["unconfirmed"] = not rf.fit_result.get("startsModelKey")
        row["moved"] = bool(moved)
        row["verdict"] = ("reloads (today's window)" if ok[1] else "differs (today's window only)" if ok[0]
                          else "differs (either window)")
        if row["voigt"] and ok[1]:
            row["verdict"] = "stale (pre-A03 Voigt only)"
        if row["unconfirmed"]:
            row["verdict"] = "stale (unconfirmed: no fit key)" + (" — matches today's as far as can be reconstructed" if ok[1] else "")
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
