OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0d8f8-b82c-7311-899b-9581523af5e8
--------
user
RECHECK, round 3 (the one round the owner allowed for option 2), of unit fix-dsg-page-evaluator: git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round 2 (docs/autofit/codex/dsg_page_evaluator_r2_verdict_runA.md / runB.md, both NO-GO) confirmed round-1 closed and found: MAJOR the server normalises by the value interpolated at the centre, which for a centre far outside the padded grid is the clamped end value of a ~1e-20 tail whose rounding sign picks one of two unrelated curves, so the page cannot mirror it; MINOR precision figures quoted at the harness amplitude; MINOR the underflow zone's description.

The owner's decision (plan §6): option 2 with a hard condition - the server change must be a NEW GUARDED BRANCH (centre outside the padded grid -> normalise by the maximum), not a modification of the existing normalisation, PROVEN byte-identical for every in-range centre on the committed battery, else stop; then mirror on the page; one Codex round; no interim notice; the kernel-underflow limit (§3a) documented and left (it degrades honestly: an all-zero curve reads as a zero-amplitude component and step (b) flags it as not supported by the data).

What changed (commit "fix(DS+G): a centre outside the padded grid ..."): fitting._ds_g_dscore_gauss gained `if center < x_padded[0] or center > x_padded[-1]: peak_val = float(np.max(np.abs(result))); if peak_val <= 0: return zeros` with the pre-existing code verbatim in the else. scripts/dsg_outside_centre_identity.py loads main's fitting.py (git show main:fitting.py) beside the new module and compares np.array_equal: 3,780 box x grid x centre cases (8 grids incl. descending and a 30-point window; centres at the window centre, half a step off, at each data edge and 1e-9 inside each padded edge) and 2,000 random draws with the centre uniform inside the padded grid - 5,780 of 5,780 identical; run_fit on the committed UCl4-graphite C1s Scan with its Graphite line as DS+G (leastsq, n_perturb 0 and 3): whole JSON byte-identical; the committed batteries hold no DS+G and pass unchanged; the two outside cases go from maxima 5.4e4 / 2.6e3 x amplitude to 1. Output committed: docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt. The page's dsgConvolved_array mirrors the branch (centre outside [xp[0], xp[nTot-1]] -> maxAbs; else interp at centre with the fallbacks). Tests: tests/test_dsg_outside_centre.py (outside -> max 1; inside incl. the padded edges themselves -> interp-at-centre rule; the boundary is the padded grid, not the data window); parity (D'') both round-2 reproducers plus a centre just outside (6.5 eV, pad 1 eV) and just inside (5.999 eV); docs corrected. JS suite: all pass, 5 documented todo. Precision figures now quoted at unit amplitude (<= 2e-14 base grid, < 1e-6 measured <= 6e-14 on the other grids); the underflow zone described as even padded length only, up to m = 0.003 on 120 points at 0.1 eV.

Verify: (1) the branch is ONLY reached for a centre strictly outside the padded grid (x_padded[0] and [-1] are the grid's first and last points; what about center == x_padded[0] exactly, NaN centre, a 1-point grid where x_padded is built from a 0.05 default step); (2) the in-range path is verbatim the old code (compare against main's fitting.py yourself); (3) the proof's coverage - is there any in-range case the script's centres miss where the branch could be taken (descending grids: x_padded is always ascending; lo/hi computed from min/max?); (4) the page mirror uses the same boundary (xp[0], xp[nTot-1]) and the same fallback order; (5) does any OTHER caller of _ds_g_dscore_gauss (Find Peaks' engine, autofit/parity.evaluate_peak, the seed's background hashing) see a change for in-range centres - it cannot if the function is byte-identical there, but check the seed (_request_seed hashes the computed background, not shapes) and the batteries; (6) the round-2 MINORs closed; (7) whether the interim-notice decision and §3a are stated accurately. Anything else in the unit's diff still open.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check the diff against `main`, challenge the guarded branch and identity proof, then review the page parity and documentation. I’ll keep this read-only and give a verdict within this run.

exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g '*dsg*' -g '*DSG*' -g '*dscore*' -g '*plan*' | head -100" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
scripts/dsg_outside_centre_identity.py
docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md
docs/superpowers/plans/2026-04-26-bkgrd-sub-toggle-plan.md
tests/test_dsg_outside_centre.py
docs/autofit/codex/dsg_page_evaluator_verdict_runB.md
docs/autofit/codex/dsgla_m0_collapse_verdict_runB.md
docs/autofit/codex/dsg_page_evaluator_r3_verdict_runB.md
docs/autofit/codex/dsgla_m0_collapse_r2_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_recheck2_prompt.txt
docs/autofit/codex/dsg_page_evaluator_r2_verdict_runB.md
docs/autofit/codex/dsg_page_evaluator_recheck_prompt.txt
docs/autofit/codex/dsg_page_evaluator_r2_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_review_prompt.txt
docs/autofit/codex/dsgla_m0_collapse_r2_review_prompt.txt
docs/autofit/codex/dsgla_m0_collapse_r2_verdict_runB.md
docs/autofit/codex/dsgla_m0_collapse_review_prompt.txt
docs/autofit/codex/dsg_page_evaluator_verdict_runA.md
docs/autofit/codex/dsgla_m0_collapse_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_r3_verdict_runA.md

exec
/bin/zsh -lc 'git status --short; git diff --stat main..HEAD; git diff --name-only main..HEAD' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 19ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZqgyZOTt' (errno=Operation not permitted)
CLAUDE.md
docs/autofit/codex/dsg_page_evaluator_r2_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_r2_verdict_runB.md
docs/autofit/codex/dsg_page_evaluator_recheck_prompt.txt
docs/autofit/codex/dsg_page_evaluator_review_prompt.txt
docs/autofit/codex/dsg_page_evaluator_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_verdict_runB.md
docs/findings/2026-09-fit-determinacy.md
docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt
docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md
fitting.py
scripts/dsg_outside_centre_identity.py
scripts/local_server_gap.js
scripts/voigt_saved_vs_refit.js
templates/index.html
tests/js/lineshape_parity.test.js
tests/js/lineshape_roundtrip.test.js
tests/js/local_lm_descent.test.js
tests/test_dsg_outside_centre.py

exec
/bin/zsh -lc 'cat scripts/dsg_outside_centre_identity.py tests/test_dsg_outside_centre.py; cat docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt; cat docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
#!/usr/bin/env python3
"""Byte-identity proof for the DS+G guarded branch (2026-09-25).

The server's _ds_g_dscore_gauss gained ONE guarded branch: a centre outside
the padded grid is normalised by the curve's maximum. For every centre
INSIDE the padded grid the output must be byte-identical to the function
before the change. This script loads the pre-change module (fitting.py as
committed on main, given as argv[1]) beside the current one and compares
np.array_equal (exact bytes, NaN-free) on:
  1. the parity box alpha {0, 0.25, 0.49} x beta {0.05, 0.7, 2} x m {0.001,
     0.05, 0.4, 2, 4} on eight grids (steps 0.02-0.5 eV, ascending and
     descending, off-grid centres, short windows), centres at the window
     centre, at each window edge, and just inside each PADDED edge;
  2. 2000 random draws over the fit's bounds with centres uniform inside the
     padded grid;
  3. run_fit on the committed UCl4-graphite C1s Scan with the Graphite line
     as DS+G at Find Peaks' parameters (the model of the browser check),
     n_perturb 0 and 3: the whole JSON response, byte for byte;
  4. and, for the record, the cases OUTSIDE the padded grid where the two
     functions differ (the guarded branch doing its job).
Usage: python scripts/dsg_outside_centre_identity.py /path/to/fitting_main.py
"""
import copy
import importlib.util
import json
import sys
import warnings

import numpy as np

warnings.filterwarnings("ignore")   # the kernel-underflow zone (plan §3a) divides by zero on purpose
sys.path.insert(0, ".")
import fitting  # noqa: E402

spec = importlib.util.spec_from_file_location("fitting_main", sys.argv[1])
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
f_new, f_old = fitting._SHAPE_FUNCS["ds_g"], old._SHAPE_FUNCS["ds_g"]


def padded_range(x, beta, m):
    step = max(float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 0.05, 1e-6)
    n_pad = max(int(np.ceil(max(10.0 * m, 20.0 * max(beta, 1e-6)) / step)), 1)
    lo, hi = (min(x[0], x[-1]) - n_pad * step, max(x[0], x[-1]) + n_pad * step)
    return lo, hi


grids = []
for step, n in ((0.02, 500), (0.05, 200), (0.0503, 181), (0.1, 120), (0.1, 30), (0.5, 21), (0.2, 61)):
    x = 284.5 - step * n / 2 + step * np.arange(n)
    grids.append(("asc %.4g x%d" % (step, n), x))
    grids.append(("desc %.4g x%d" % (step, n), x[::-1].copy()))
identical = differ = 0
worst = 0.0
for label, x in grids:
    for a in (0.0, 0.25, 0.49):
        for b in (0.05, 0.7, 2.0):
            for m in (0.001, 0.05, 0.4, 2.0, 4.0):
                lo, hi = padded_range(x, b, m)
                for c in (284.5, 284.525, x.min(), x.max(), lo + 1e-9, hi - 1e-9):
                    y0 = f_old(x, amplitude=1.0, center=c, alpha=a, beta=b, m_gauss=m)
                    y1 = f_new(x, amplitude=1.0, center=c, alpha=a, beta=b, m_gauss=m)
                    if np.array_equal(y0, y1):
                        identical += 1
                    else:
                        differ += 1
                        worst = max(worst, float(np.max(np.abs(y0 - y1))))
print(f"1. box x grids x centres inside the padded grid: {identical} byte-identical, {differ} differ (worst |delta| {worst:.3g})")

rng = np.random.default_rng(20260925)
identical = differ = 0
for _ in range(2000):
    step = float(rng.choice([0.02, 0.05, 0.1, 0.2]))
    n = int(rng.integers(20, 400))
    x = 284.5 - step * n / 2 + step * np.arange(n)
    if rng.random() < 0.5:
        x = x[::-1].copy()
    a, b, m = rng.uniform(0, 0.495), rng.uniform(0.05, 2.0), rng.uniform(0.001, 4.0)
    lo, hi = padded_range(x, b, m)
    c = rng.uniform(lo, hi)
    amp = float(rng.uniform(1, 1e5))
    y0 = f_old(x, amplitude=amp, center=c, alpha=a, beta=b, m_gauss=m)
    y1 = f_new(x, amplitude=amp, center=c, alpha=a, beta=b, m_gauss=m)
    if np.array_equal(y0, y1):
        identical += 1
    else:
        differ += 1
print(f"2. 2000 random draws, centre inside the padded grid: {identical} byte-identical, {differ} differ")

from autofit.reference import load_reference_fits, peak_to_backend_spec  # noqa: E402
rf = [r for r in load_reference_fits("docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip") if r.name == "C1s Scan"][0]
peaks = copy.deepcopy(rf.peaks)
g = [p for p in peaks if "raph" in p["name"]][0]
g.update(shape="DSG_LA", laAlpha=0.2, laBeta=0.05, laM=0.8)
specs = [peak_to_backend_spec(p, peaks) for p in peaks]
i0, i1 = rf.bg_indices()
for n_perturb in (0, 3):
    kw = dict(background_method=rf.bg_method, bg_start_idx=i0, bg_end_idx=i1, endpoint_avg=rf.endpoint_avg, n_perturb=n_perturb, fit_kws={"method": "leastsq"})
    r_new = json.dumps(fitting.run_fit(rf.roi_be, np.round(rf.roi_intensity, 2), specs, **kw), sort_keys=True)
    r_old = json.dumps(old.run_fit(rf.roi_be, np.round(rf.roi_intensity, 2), specs, **kw), sort_keys=True)
    print(f"3. run_fit (leastsq, n_perturb {n_perturb}) on the C1s Scan with a DS+G Graphite line: {'byte-identical JSON' if r_new == r_old else 'DIFFERS'} ({len(r_new)} bytes)")

for label, x, c in (("centre 10 eV outside [-5, 5]", (np.arange(200) - 99.5) * 0.05, 10.0), ("centre -10 eV, low-BE side", np.linspace(-5, 5, 201), -10.0)):
    y0 = f_old(x, amplitude=1.0, center=c, alpha=0.49, beta=0.05, m_gauss=0.05)
    y1 = f_new(x, amplitude=1.0, center=c, alpha=0.49, beta=0.05, m_gauss=0.05)
    print(f"4. {label}: old max {np.max(np.abs(y0)):.3g}, new max {np.max(np.abs(y1)):.3g} (the guarded branch)")
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
1. box x grids x centres inside the padded grid: 3780 byte-identical, 0 differ (worst |delta| 0)
2. 2000 random draws, centre inside the padded grid: 2000 byte-identical, 0 differ
3. run_fit (leastsq, n_perturb 0) on the C1s Scan with a DS+G Graphite line: byte-identical JSON (43172 bytes)
3. run_fit (leastsq, n_perturb 3) on the C1s Scan with a DS+G Graphite line: byte-identical JSON (43169 bytes)
4. centre 10 eV outside [-5, 5]: old max 5.35e+04, new max 1 (the guarded branch)
4. centre -10 eV, low-BE side: old max 2.61e+03, new max 1 (the guarded branch)
# DS+G page evaluator — a grid-aware mirror of the server's convolution (2026-09-22)

Branch `fix-dsg-page-evaluator` off main `b3c9e37` (A03 deployed). Owner's
brief: "Port the server's convolution to a grid-aware page evaluator.
Acceptance: the existing todo tests (parity sweep DS+G box at 1e-6, the
round-trip case), PLUS convergence demonstrated across the full β/m range the
optimiser can reach — including the corners that produced 1e52, not only the
Find Peaks box. Nothing de-listed, nothing changed in Find Peaks." Interim
red notice skipped unless a third Codex round or more than a day.

## 1. The defect (A03 sweep, section (D))

The page drew, integrated and exported a DS+G component with `laCasaXPS`, a
numerical quadrature whose step resolved the Lorentzian core (β/3) but not
the Gaussian kernel (σ = m/2.355). At β = 2, m = 0.05 the step was 0.67 eV
against σ = 0.021 eV and the curve was 1e52 × amplitude; across the fitted
box the page's area was 23–64 % of the server's. On the exact box Find Peaks
emits for a graphitic C 1s line (`autofit/regions/c1s.py`: β fixed at 0.05,
α 0–0.3, m in the graphitic FWHM range 0.4–1.2, polymers 0.8–1.8) the page's
curve was off by up to 13.7 % of amplitude and its area 5–21 % low for
α 0.15–0.3 (α = 0 was fine). Every A- and M-family candidate is built on
that slot, so an applied suggestion was drawn and quantified wrong; the
manual dropdown was the same path. 0 of the 530 committed peak records use
DS+G.

## 2. The fix

`dsgConvolved_array(beArr, center, alpha, beta, m)` in `templates/index.html`
is a literal mirror of `fitting._ds_g_dscore_gauss` for m ≥ 0.001 (the
m < 0.001 delta branch, `dsgDeltaKernel_array`, was already mirrored):

- α clipped to [0, 0.495], β ≥ 1e-6, m ≥ 0 — as the server;
- step = median |Δx| (numpy's median), ≥ 1e-6;
- padded grid ±max(10 m, 20 β) at that step, `np.linspace` semantics
  (always ascending, endpoint set exactly);
- DS core on the padded grid, non-finite → 0; half-cosine tapers over each
  pad (`np.linspace(0, π, n_pad)`);
- Gaussian kernel of σ = m/(2√(2 ln 2)) on the same step, centred at
  (n − 1)/2, normalised to unit sum over the FULL padded length;
- the server's circular convolution `irfft(rfft(ds)·rfft(ifftshift(k)))`
  computed as what it is: `_circularConvolve` — a zero-padded linear
  convolution by radix-2 FFT (`_fftRadix2`, length the power of two
  ≥ 2n − 1) folded back to n. Every wrapped contribution the server
  includes is included; O(n log n) on any grid. (The first cut summed
  directly within 8 σ and clipped at the array ends; Codex round 1 showed a
  centre outside the window 0.41 × amplitude off — the DS tail reaches the
  padded array's far end and the server's FFT wraps it — and 13 s per
  curve at 0.001 eV. Both gone.)
- `np.interp` back to the data grid; normalised by the value interpolated AT
  the centre (fallbacks as the server's); non-finite → 0.

`evalPeakArray` routes every DS+G through it (the delta branch inside). The
scalar `evalPeak` DSG_LA branch keeps the name `laCasaXPS` but is now the
normalised DS core with m ignored — the same status as its LACX branch;
guard (C) of the parity harness proves no shipped caller reaches it. The
old quadrature is deleted, not tuned.

Cost (FFT, one curve at the box's far corner β 2, m 4, α 0.49): 1.1 ms on a
241-point 0.05 eV grid, 8 ms at 0.02 eV (601 points), 13 ms at 0.005 eV,
58 ms at 0.001 eV over 10 eV (the first cut: 13 s); Find Peaks-like
parameters 0.2–1.1 ms; a local fit of a DS+G component converges in 38 ms.

## 3. Acceptance (measured)

| check | result |
|---|---|
| parity sweep (D), DS+G box α {0, 0.25, 0.49} × β {0.05, 0.7, 2} × m {0.001, 0.05, 0.4, 2, 4}, base grid | ≤ 2e-14 of amplitude (3e-15 at the harness amplitude, 1.95e-14 at unit amplitude; was 1e52 at β 2, m 0.05) — now a hard assertion at 1e-6 |
| (D′) the same box on: 0.1 eV step; 0.02 eV step; descending grid; centre half a step off-grid; descending + 0.03 eV off-grid; a 30-point window narrower than the pad; a 0.0503 eV step | < 1e-6 on every combination (measured ≤ 6e-14) — hard assertions |
| (A) DS+G at the base peak (was todo) | hard, passes |
| round trip page → server → page, DS+G (was todo), and DS+G m locked at 0.05 and at 4 (curve comparison was disabled) | hard, pass |
| (B) scalar vs array evaluator, DS+G | now `todo` like LACX: the convolution is a grid operation; guard (C) holds |
| Find Peaks box (β 0.05, α 0–0.3, m 0.4–1.8, 0.05 and 0.1 eV grids) | agrees with the server to 1e-6 (was 5–21 % low in area) |
| (D″) regressions: a centre 10 eV outside a [−5, 5] window; a 6-point irregular grid; alternating 0.05/0.06 steps (median ≠ mean); a 0.001 eV grid over 10 eV at β 2, m 4, α 0.49; 2- and 1-point grids | < 1e-6 (5e-12 relative on the outside-centre case whose server maximum is 48; 3.5e-13 at 0.001 eV) — hard; each curve under 2 s asserted |
| (D″) m = 0.001, 0.002, 0.02, 0.05 on a 0.1 eV grid | page equals server at every m; at m ≤ 0.002 BOTH are an all-zero curve — a KNOWN SERVER LIMIT (§3a), pinned as such |

### 3a. Server limit found on the way (not this unit's to change)

Just above the 0.001 delta threshold on a coarse grid the server's Gaussian
kernel underflows: σ = m/2.355 is far below the step, no padded-grid sample
carries weight (for an even padded length the nearest sample is half a
step from the centre), the kernel normalises to NaN and
`_ds_g_dscore_gauss` returns an all-zero curve for the component (its final
"suppress NaN/Inf" turns it to zeros). It happens only for an EVEN padded
length (the nearest sample is half a step from the centre); an odd length
has a sample at the centre and the kernel collapses to a delta instead. On
a 120-point 0.1 eV grid the zone is 0.001 ≤ m ≤ 0.003 (m = 0.00305 is
already a normal curve); on 121 points there is none. A fit will not settle there (a zero curve fits
nothing), but a LOCKED m in that zone is fitted as zero. The page mirrors
it exactly (a vanished curve drawn as vanished, never a curve the server
did not fit). Recorded for the owner; the fix belongs to the server (a
kernel that collapses to a delta below the grid's resolution, as the
threshold branch does).

### 3b. Server limit found in round 2 — FIXED by a guarded branch (2026-09-25, owner's option 2)

The server normalises the convolved curve by its value interpolated AT THE
CENTRE, falling back to the curve's maximum only when that value is ≤ 0.
With the centre far OUTSIDE the padded grid (e.g. 10 eV outside a
[−5, 5] window at β 0.05, m 0.05, or 15 eV outside on the low-BE side)
the interpolated value is the clamped end value of a tail of order 1e-20 —
rounding noise whose SIGN decides which of two unrelated curves the server
returns: the max-normalised tail (sign negative) or that tail divided by
~1e-20 (sign positive). The page mirrors the rule and the arithmetic, but
not the rounding sign of a 1e-20 number, and Codex round 2 reproduced a
case where the two sides fall on different branches (server maximum 1,
page 5e16). No committed model is near this regime (a component centred
outside its own window has no physical reading, and a fit does not settle
there), and the server's own output there is arbitrary.

Owner's condition (2026-09-25): a NEW GUARDED BRANCH, not a modification
of the existing normalisation, PROVEN byte-identical for every centre
inside the padded grid — otherwise stop and take option 1. Done:
`_ds_g_dscore_gauss` now has `if center < x_padded[0] or center >
x_padded[-1]: peak_val = max|result|` with the pre-existing code in the
`else`. Proof (`scripts/dsg_outside_centre_identity.py`, main's function
loaded from `git show main:fitting.py` beside the new one, output in
`docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt`):
3,780 box × grid × centre cases (centres at the window centre, off-grid,
at each data edge and 1e-9 inside each padded edge) and 2,000 random
draws with the centre inside the padded grid — 5,780 of 5,780
`np.array_equal`; `run_fit` on the committed UCl4-graphite C1s Scan with
its Graphite line as DS+G (n_perturb 0 and 3, Levenberg-Marquardt, the
byte-identical method): the whole JSON response identical; the committed
batteries hold no DS+G component and pass unchanged. The two outside
cases: old maximum 5.4e4 and 2.6e3 × amplitude, new 1. The page mirrors
the branch (`dsgConvolved_array`); both reproducers are hard regressions
in (D″), plus a centre just outside and just inside the padded edge.

Nothing changed on the server, in `autofit/`, in Find Peaks or in the
dropdown. Python suite untouched by this unit (no Python change); JS suite
and browser check in §5.

## 4. Sites

`laCasaXPS` (rewritten), `dsgConvolved_array` (new), `evalPeakArray`;
every function-extractor list that names the lineshape block
(`tests/js/lineshape_roundtrip.test.js`, `local_lm_descent.test.js`,
`scripts/local_server_gap.js`, `scripts/voigt_saved_vs_refit.js`) now lists
`dsgConvolved_array`; `tests/js/lineshape_parity.test.js` (A), (B), (D),
(D′); `tests/js/lineshape_roundtrip.test.js`; CLAUDE.md; findings §7.

## 5. Verification

- JS suite: 392 tests, 387 pass, 0 fail, 5 todo (`node --test tests/js/*.test.js`).
  The five: LACX m > 0 in (A), (B) and (D); (B) DS+G (scalar evaluator
  ignores m, by design); the LACX round trip.
- Python suite: untouched by this unit (no Python change); the A03 run on
  the same server code was 989 passed / 7 skipped.
- Browser check (`browser_check_dsg.py`, dev gunicorn :5151 with the
  production `--timeout 300`): the committed UCl4-graphite C1s Scan with its
  Graphite line switched to DS+G at Find Peaks' parameters (β 0.05, α 0.2,
  m 0.8), Run Fit (fitted α 0, β 0.053, m 0.62): the curve the page draws
  for it equals the server's fitted curve to 1.2e-12 of amplitude (the five
  GL lines 1e-13); its Results area equals the server curve's to 0.0000 %;
  the chart dataset is the drawn curve; a `ds_g` Find Peaks candidate maps
  to DSG_LA with its α, β, m; no page errors.

## 5a. Finding on the way: a DS+G Run Fit costs the server ~110 s

Not this unit's change (fitting.py is untouched) and present on main
today. On the committed UCl4-graphite C1s Scan (191 points, 0.1 eV) with
the Graphite line switched to DS+G at Find Peaks' parameters (β 0.05,
α 0.2, m 0.8) and five GL lines: the plain fit takes 0.4 s (640 DS+G
evaluations, 0.3 ms each), but each of the page's `n_perturb: 3` restarts
takes ~18 s (28,821 evaluations — the perturbed descent runs to the
optimiser's evaluation budget), and with `n_starts: 3` the request takes
110 s. Production's gunicorn `--timeout 300` covers it; a dev server on the
30 s default returns a worker timeout and the page reports "Fit failed".
Every A- and M-family Find Peaks candidate applied and re-fitted pays this.
Logged for its own look (why the perturbed DS+G descent does not converge;
whether the restarts should be skipped or capped for this shape).

## 6. Codex rounds

**Round 1 (`docs/autofit/codex/dsg_page_evaluator_verdict_run{A,B}.md`):
NO-GO ×2.** Fixed:
1. MAJOR — the first cut's direct sum clipped at the padded array's ends
   and so omitted the wrapped contributions the server's circular FFT
   includes: a centre 10 eV outside a [−5, 5] window was 0.41 × amplitude
   off (the normalisation at the clamped centre scales every value), a
   6-point irregular grid 2.9e-4. Replaced by the same circular
   convolution, computed by FFT (`_fftRadix2`, `_circularConvolve`); both
   reproducers are regression tests, agreeing to 5e-12 and 1e-16.
2. MAJOR — quadratic cost on fine grids (13.5 s per curve at 0.001 eV).
   The FFT makes it O(n log n): 58 ms at 0.001 eV, 8 ms at 0.02 eV; a test
   asserts each regression curve under 2 s.
3. MINOR — (D′)'s "irregular-ish" grid was uniform, and its m = 0.001 case
   passed on a curve that had vanished on BOTH sides. A genuinely
   irregular grid (alternating 0.05/0.06 steps) is in (D″); the vanished
   curve is the server's own kernel underflow just above the delta
   threshold on a coarse grid — characterised in §3a and pinned as a known
   server limit (page equals server; the server curve is asserted to be
   zero there so a server change surfaces).
4. MINOR — findings §7 said ≤ 3e-15 across seven grids; that was the base
   grid (the seven are < 1e-6, measured ≤ 5.5e-15). Corrected.

**Round 2 (`dsg_page_evaluator_r2_verdict_run{A,B}.md`): NO-GO ×2.**
Round-1 items 1–3 confirmed closed. Found: MAJOR — the normalisation
conditioning of §3b (centre far outside the padded grid; the server's own
output there is decided by the sign of rounding noise); MINOR — the
precision figures were quoted at the harness amplitude (at unit amplitude
1.95e-14 base grid, 5.8e-14 at 0.02 eV; corrected above); MINOR — the
underflow zone's description (corrected in §3a: even lengths only, up to
m = 0.003 on 120 points). **Stopped here per the owner's rule (a third
round): the remaining MAJOR is a server conditioning limit outside this
unit, documented in §3b with the fix that belongs to the server;
everything physically reachable on the page is a hard 1e-6 assertion.**
The interim red notice was NOT added: its wording ("the page's curve and
area for this shape are not yet exact") would now be false. Decision to
the owner.

**Owner decision (2026-09-25): option 2 with a hard condition** — the
server change as a new guarded branch, byte-identical for in-range centres
on the committed battery, else stop; then mirror on the page and one Codex
round; no interim notice; §3a documented and left (it degrades honestly:
an all-zero curve reads as a zero-amplitude component, which step (b)
flags as not supported by the data). Done as §3b records. Logged
separately, not urgent: the ~110 s DS+G Run Fit (§5a) — likely the same
evaluation-budget question as the Find Peaks speed item.

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md AGENTS.md; do if test -f "$p"; then cat "$p"; fi; done; git diff main..HEAD -- fitting.py templates/index.html' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-d2og7fn6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-NimlRXwS' (errno=Operation not permitted)
diff --git a/fitting.py b/fitting.py
index 78fec0d..03a6690 100644
--- a/fitting.py
+++ b/fitting.py
@@ -288,13 +288,26 @@ def _ds_g_dscore_gauss(
     result = np.interp(x, x_padded, ds_conv)
 
     # ── Normalise so value at x = center equals amplitude ─────────────────────
-    # Interpolate at exact center rather than nearest grid point to avoid
-    # normalization error when center falls between data points.
-    peak_val = float(np.interp(center, x_padded, ds_conv))
-    if peak_val <= 0.0:
-        peak_val = np.max(np.abs(result))
-    if peak_val <= 0.0:
-        return np.zeros_like(x)
+    if center < x_padded[0] or center > x_padded[-1]:
+        # NEW GUARDED BRANCH (2026-09-25, unit fix-dsg-page-evaluator): the
+        # centre lies OUTSIDE the padded grid, so "the value at the centre"
+        # is np.interp's clamped end value — the tail of a curve whose peak
+        # is not on the grid, of order 1e-20 once the tapers have acted, and
+        # its SIGN decided which of two unrelated curves came back (the
+        # max-normalised tail, or that tail divided by ~1e-20; Codex round 2
+        # of the unit). Normalise by the curve's maximum instead. A centre
+        # inside the padded grid takes the branch below, unchanged.
+        peak_val = float(np.max(np.abs(result)))
+        if peak_val <= 0.0:
+            return np.zeros_like(x)
+    else:
+        # Interpolate at exact center rather than nearest grid point to avoid
+        # normalization error when center falls between data points.
+        peak_val = float(np.interp(center, x_padded, ds_conv))
+        if peak_val <= 0.0:
+            peak_val = np.max(np.abs(result))
+        if peak_val <= 0.0:
+            return np.zeros_like(x)
 
     result = amplitude * result / peak_val
 
diff --git a/templates/index.html b/templates/index.html
index f272259..07977d7 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4043,45 +4043,16 @@ function laCasaXPSCore(eps, alpha, beta) {
 }
 
 function laCasaXPS(x, center, alpha, beta, mGauss) {
-  // LA(α, β, m) — CasaXPS convention
-  // α: dimensionless asymmetry index (0–0.5) — tail toward HIGHER binding energy
-  // β: Lorentzian half-width (eV)
-  // m: Gaussian FWHM (eV) convolved with the DS core
-  // Returns value normalised to 1 at x = center.
-  //
-  // m below the same 0.001 eV threshold the backend uses
-  // (fitting.py _ds_g_dscore_gauss) means a delta kernel: skip the
-  // convolution and return the normalised DS core directly. The quadrature
-  // below degenerates as sigma → 0 (its Gaussian weights divide by
-  // 2·sigma², collapsing the curve to ~0), so this branch is a correctness
-  // fix, not just a fast path. Pinned by tests/js/lineshape_parity.test.js.
-  if (mGauss < 0.001) {
-    const peakVal = laCasaXPSCore(0, alpha, beta);
-    if (!(peakVal > 0)) return 0;
-    return laCasaXPSCore(x - center, alpha, beta) / peakVal;
-  }
-  const sigma = mGauss / (2.0 * Math.sqrt(2.0 * Math.LN2));
-  // Wide window: DS power-law tail decays slowly (~1/ε^1.85), need large range.
-  const halfRange = 6 * sigma + 50 * beta;
-  // Scale N so dEps ≤ β/3 (resolves the Lorentzian core) with floor of 300
-  const N = Math.max(300, Math.ceil(2 * halfRange / (beta / 3)));
-  const dEps = 2 * halfRange / N;
-  // Cosine taper: smoothly fade the DS core to zero over the outer 40% of
-  // the window, eliminating cliff artifacts from the power-law tail cutoff.
-  const taperStart = 0.6 * halfRange;
-  const u0 = x - center;
-  let val = 0, norm = 0;
-  for (let k = 0; k <= N; k++) {
-    const eps = -halfRange + k * dEps;
-    const absEps = Math.abs(eps);
-    const taper = absEps > taperStart
-      ? 0.5 * (1 + Math.cos(Math.PI * (absEps - taperStart) / (halfRange - taperStart)))
-      : 1.0;
-    const ds = laCasaXPSCore(eps, alpha, beta) * taper;
-    val  += ds * Math.exp(-((u0 - eps) * (u0 - eps)) / (2 * sigma * sigma));
-    norm += ds * Math.exp(-(eps * eps)                / (2 * sigma * sigma));
-  }
-  return norm > 0 ? val / norm : 0;
+  // Per-point DS+G fallback for the scalar evaluator's DSG_LA branch: the
+  // NORMALISED DS core, m IGNORED — exactly as its LACX branch ignores m. The Gaussian
+  // convolution is a GRID operation and lives in dsgConvolved_array (called
+  // through evalPeakArray, the only shipped path — parity guard (C)). Until
+  // 2026-09-22 this function was a numerical quadrature whose step resolved
+  // the Lorentzian core (β/3) but not the Gaussian kernel, and was wrong by
+  // up to 1e52 × amplitude across the fitted β/m range (A03 sweep).
+  const peakVal = laCasaXPSCore(0, alpha, beta);
+  if (!(peakVal > 0)) return 0;
+  return laCasaXPSCore(x - center, alpha, beta) / peakVal;
 }
 
 // True LA(α, β, m) [CasaXPS] — piecewise-asymmetric Lorentzian + integer-kernel Gauss conv.
@@ -4224,10 +4195,152 @@ function dsgDeltaKernel_array(beArr, center, alpha, beta) {
   return core;
 }
 
+// In-place iterative radix-2 FFT (Cooley–Tukey) on arrays of a power-of-two
+// length; inverse = true divides by n. Double precision, as numpy's pocketfft.
+function _fftRadix2(re, im, inverse) {
+  const n = re.length;
+  for (let i = 1, j = 0; i < n; i++) {                   // bit-reversal permutation
+    let bit = n >> 1;
+    for (; j & bit; bit >>= 1) j ^= bit;
+    j ^= bit;
+    if (i < j) { let t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
+  }
+  for (let len = 2; len <= n; len <<= 1) {
+    const ang = (inverse ? 2 : -2) * Math.PI / len;
+    const wr = Math.cos(ang), wi = Math.sin(ang);
+    for (let i = 0; i < n; i += len) {
+      let cr = 1, ci = 0;
+      for (let k = 0; k < len / 2; k++) {
+        const ar = re[i + k], ai = im[i + k];
+        const br = re[i + k + len / 2] * cr - im[i + k + len / 2] * ci;
+        const bi = re[i + k + len / 2] * ci + im[i + k + len / 2] * cr;
+        re[i + k] = ar + br; im[i + k] = ai + bi;
+        re[i + k + len / 2] = ar - br; im[i + k + len / 2] = ai - bi;
+        const ncr = cr * wr - ci * wi; ci = cr * wi + ci * wr; cr = ncr;
+      }
+    }
+  }
+  if (inverse) for (let i = 0; i < n; i++) { re[i] /= n; im[i] /= n; }
+}
+
+// Circular convolution of two real arrays of the same length n — what
+// numpy's irfft(rfft(a)·rfft(b)) returns — as a zero-padded linear
+// convolution (FFT length the power of two ≥ 2n − 1) folded back to n.
+function _circularConvolve(a, b) {
+  const n = a.length;
+  let N = 1; while (N < 2 * n - 1) N <<= 1;
+  const ar = new Float64Array(N), ai = new Float64Array(N), br = new Float64Array(N), bi = new Float64Array(N);
+  for (let i = 0; i < n; i++) { ar[i] = a[i]; br[i] = b[i]; }
+  _fftRadix2(ar, ai, false); _fftRadix2(br, bi, false);
+  for (let i = 0; i < N; i++) { const r = ar[i] * br[i] - ai[i] * bi[i]; const im = ar[i] * bi[i] + ai[i] * br[i]; ar[i] = r; ai[i] = im; }
+  _fftRadix2(ar, ai, true);
+  const out = new Float64Array(n);
+  for (let i = 0; i < n; i++) out[i] = ar[i] + (i + n < 2 * n - 1 ? ar[i + n] : 0);
+  return out;
+}
+
+// DS+G with Gaussian broadening, a literal mirror of the server's
+// fitting._ds_g_dscore_gauss (m ≥ 0.001; below that the delta branch above):
+// the DS core on a grid PADDED by ±max(10 m, 20 β) at the data step
+// (np.linspace semantics, always ascending), a half-cosine taper over each
+// pad, a Gaussian kernel of σ = m / 2√(2 ln 2) on the same step normalised to
+// unit sum over the FULL padded length, circular convolution
+// (irfft(rfft(ds)·rfft(ifftshift(kernel))) on the server), linear
+// interpolation back to the data grid, and normalisation by the value
+// interpolated AT the centre. The convolution is the server's circular one,
+// computed by FFT (_circularConvolve) so every wrapped contribution is
+// included and the cost is O(n log n) on any grid (a first cut summed
+// directly within 8 σ and clipped at the array ends: Codex round 1 showed
+// a centre outside the window 0.41 × amplitude off, and 13 s per curve at
+// 0.001 eV). Pinned by tests/js/lineshape_parity.test.js (D)/(D′), the full
+// β/m box incl. the corners that made the old quadrature explode. Returns
+// the curve normalised to 1 at the centre; the caller applies the amplitude.
+function dsgConvolved_array(beArr, center, alpha, beta, mGauss) {
+  const N = beArr.length;
+  const a = _dsgAlpha(alpha);
+  const b = Math.max(beta, 1e-6);
+  const m = Math.max(mGauss, 0);
+  if (m < 0.001) return dsgDeltaKernel_array(beArr, center, a, b);
+  // step = median |Δx| (numpy: the mean of the two middle values for an even count)
+  let step = 0.05;
+  if (N > 1) {
+    const d = new Array(N - 1);
+    for (let i = 1; i < N; i++) d[i - 1] = Math.abs(beArr[i] - beArr[i - 1]);
+    d.sort((u, v) => u - v);
+    const n = d.length;
+    step = n % 2 ? d[(n - 1) / 2] : 0.5 * (d[n / 2 - 1] + d[n / 2]);
+  }
+  step = Math.max(step, 1e-6);
+  const padEv = Math.max(10 * m, 20 * b);
+  const nPad = Math.max(Math.ceil(padEv / step), 1);
+  const asc = N > 1 ? beArr[N - 1] > beArr[0] : true;
+  const lo = (asc ? beArr[0] : beArr[N - 1]) - nPad * step;
+  const hi = (asc ? beArr[N - 1] : beArr[0]) + nPad * step;
+  const nTot = N + 2 * nPad;
+  const xp = new Float64Array(nTot);
+  const dxLin = (hi - lo) / (nTot - 1);
+  for (let i = 0; i < nTot; i++) xp[i] = lo + i * dxLin;
+  xp[nTot - 1] = hi;                                   // np.linspace sets the endpoint exactly
+  const ds = new Float64Array(nTot);
+  for (let i = 0; i < nTot; i++) { const v = laCasaXPSCore(xp[i] - center, a, b); ds[i] = Number.isFinite(v) ? v : 0; }
+  if (nPad > 1) {
+    for (let k = 0; k < nPad; k++) {
+      const th = Math.PI * k / (nPad - 1);                // np.linspace(0, π, nPad)[k]
+      ds[k] *= 0.5 * (1 - Math.cos(th));
+      ds[nTot - nPad + k] *= 0.5 * (1 + Math.cos(th));
+    }
+  }
+  const sigma = m / (2 * Math.sqrt(2 * Math.LN2));
+  const kHalf = (nTot - 1) / 2;
+  const kernel = new Float64Array(nTot);
+  let ksum = 0;
+  for (let t = 0; t < nTot; t++) { const kg = (t - kHalf) * step; kernel[t] = Math.exp(-0.5 * (kg / sigma) * (kg / sigma)); ksum += kernel[t]; }
+  for (let t = 0; t < nTot; t++) kernel[t] /= ksum;
+  // The server's circular convolution, exactly: irfft(rfft(ds)·rfft(ifftshift(kernel)))
+  // is the length-nTot circular convolution of ds with the shifted kernel;
+  // computed here as a zero-padded linear convolution by radix-2 FFT, folded
+  // back to length nTot (out[i] = lin[i] + lin[i + nTot]). Every wrapped
+  // contribution the server includes — a DS tail that runs into the padded
+  // array's far end, a centre outside the window — is included; the cost is
+  // O(n log n) on any grid (13 ms at 0.001 eV over a 10 eV window).
+  const fl = Math.floor(nTot / 2);                        // np.fft.ifftshift's shift
+  const ks = new Float64Array(nTot);
+  for (let t = 0; t < nTot; t++) ks[t] = kernel[(t + fl) % nTot];
+  const conv = _circularConvolve(ds, ks);
+  // np.interp(query, xp, conv): xp ascending; clamped outside; linear inside
+  const interp = q => {
+    if (q <= xp[0]) return conv[0];
+    if (q >= xp[nTot - 1]) return conv[nTot - 1];
+    let lo2 = 0, hi2 = nTot - 1;
+    while (hi2 - lo2 > 1) { const mid = (lo2 + hi2) >> 1; if (xp[mid] <= q) lo2 = mid; else hi2 = mid; }
+    const x0 = xp[lo2], x1 = xp[hi2];
+    const tt = x1 !== x0 ? (q - x0) / (x1 - x0) : 0;
+    return conv[lo2] + tt * (conv[hi2] - conv[lo2]);
+  };
+  const out = new Array(N);
+  for (let i = 0; i < N; i++) out[i] = interp(beArr[i]);
+  // Normalisation: at the interpolated centre when it lies inside the padded
+  // grid (the server's rule, with its fallbacks); by the curve's maximum when
+  // it lies OUTSIDE it (the server's guarded branch of 2026-09-25 — there the
+  // "value at the centre" was the clamped end value of a 1e-20 tail, and its
+  // rounding sign chose between two unrelated curves).
+  let peakVal;
+  const maxAbs = () => { let mx = 0; for (let i = 0; i < N; i++) mx = Math.max(mx, Math.abs(out[i])); return mx; };
+  if (center < xp[0] || center > xp[nTot - 1]) {
+    peakVal = maxAbs();
+  } else {
+    peakVal = interp(center);
+    if (!(peakVal > 0)) peakVal = maxAbs();
+  }
+  if (!(peakVal > 0)) return new Array(N).fill(0);
+  for (let i = 0; i < N; i++) { const v = out[i] / peakVal; out[i] = Number.isFinite(v) ? v : 0; }
+  return out;
+}
+
 // Compute per-peak intensities across an array of BE values. Special-cases
 // LACX with non-zero m so the Gaussian convolution sees the whole grid, and
-// DSG_LA below the 0.001 delta-kernel threshold so the normalisation sees
-// the whole grid (see dsgDeltaKernel_array above).
+// DSG_LA (every m: the delta branch below 0.001, the convolution above) so
+// the padding, kernel and normalisation see the whole grid.
 function evalPeakArray(beArr, p) {
   if (p.shape === 'LACX' && Math.round(p.caM || 0) > 0) {
     const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
@@ -4236,11 +4349,11 @@ function evalPeakArray(beArr, p) {
     for (let i = 0; i < beArr.length; i++) out[i] = amp * yArr[i];
     return out;
   }
-  if (p.shape === 'DSG_LA' && (p.laM || 0) < 0.001) {
+  if (p.shape === 'DSG_LA') {
     // (p.laM || 0): negative laM matches the backend's clamp-to-0-then-delta
     // path; NaN/undefined coerce to 0 → delta, which peakToBackendSpec's
     // non-finite→default sanitisation makes unreachable in fit flows.
-    const yArr = dsgDeltaKernel_array(beArr, p.center, _dsgAlpha(p.laAlpha), p.laBeta);
+    const yArr = dsgConvolved_array(beArr, p.center, p.laAlpha, p.laBeta, p.laM || 0);
     const amp = p.amplitude;
     return yArr.map(v => amp * v);
   }

exec
/bin/zsh -lc "git diff main..HEAD -- CLAUDE.md docs/findings/2026-09-fit-determinacy.md tests/js scripts/local_server_gap.js scripts/voigt_saved_vs_refit.js; rg -n '_ds_g_dscore_gauss|_request_seed|dsgConvolved_array|dsGNormCache' fitting.py autofit templates/index.html; rg --files -g 'package.json' -g '*requirements*' -g 'pyproject.toml' -g 'AGENTS.md' -g '*battery*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2iYNsU2z' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3jbLN2Dc' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index e54491f..d4550d8 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -132,13 +132,24 @@ to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
 `_make_peak_params._set` now widens a limit to a held value), and the
 server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
 held parameter is held at its value; what the page draws is what the
-server fitted. Tracked gaps, `todo` in both files: LACX with m > 0 (the page draws
+server fitted. Tracked gap, `todo` in both files: LACX with m > 0 (the page draws
 a rounded integer kernel; the server fits m continuously — the `caM` clamp
-unit) and DS+G with m ≥ 0.05 (the page's quadrature `laCasaXPS` sizes its
-step to the Lorentzian core, not the Gaussian kernel, and is wrong by up to
-80 % of amplitude across the fitted β/m range — 1e52 × at β = 2, m = 0.05;
-0 of the 530 peak records in the seven committed projects use DS+G; its own unit). Details in
-`docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+unit). DS+G was the other gap until 2026-09-22 (the page's quadrature
+`laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
+and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
+in area on the very box Find Peaks emits for a graphitic C 1s line);
+`dsgConvolved_array` now mirrors the server's padded-grid convolution for
+every m — the same FFT circular convolution — pinned at 1e-6 across the
+full β/m box on eight grids, irregular grids and centres outside the
+window (`docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md`). Two
+server limits found there: a DS+G m just above the 0.001 delta threshold
+on a coarse grid (m ≤ 0.003 at 0.1 eV, even padded length) underflows the
+kernel and returns an all-zero curve — left as is, it reads as a
+zero-amplitude component and step (b) flags it; and a centre OUTSIDE the
+padded grid was normalised by rounding noise — fixed 2026-09-25 by a NEW
+GUARDED BRANCH (normalise by the maximum), proven byte-identical for every
+in-range centre against main's function (`scripts/dsg_outside_centre_identity.py`). Details of
+A03 in `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
 
 ---
 
@@ -234,7 +245,7 @@ them to (use grep to find current line numbers — the file evolves):
 - `peakToBackendSpec` LACX branch
 - `applyBackendResult` LACX backend-param mapping
 - `runFit` JS LM free-params block + per-param clamps + linked-peak sync
-- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`)
+- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`; DS+G's grid-aware twin is `dsgConvolved_array` — a convolved shape's scalar `evalPeak` branch ignores m and must have no caller, parity guard (C))
 - `_migrateLineshapeAliases` if backwards-compat alias needed
 
 ### UCl4 U 4f Asymmetric Broadening
diff --git a/docs/findings/2026-09-fit-determinacy.md b/docs/findings/2026-09-fit-determinacy.md
index dce89de..9844615 100644
--- a/docs/findings/2026-09-fit-determinacy.md
+++ b/docs/findings/2026-09-fit-determinacy.md
@@ -338,6 +338,20 @@ area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
 the 530 peak records in the seven committed projects use DS+G (and none of
 the 202 measurement targets), so no saved figure is affected; it is the
 fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
-recorded as its own unit. The general lesson repeats §6's: a harness that
+FIXED the same day in `fix-dsg-page-evaluator` after the owner asked whether
+Find Peaks emits DS+G: it does (every A- and M-family C 1s candidate's
+graphitic main line, β fixed at 0.05, α 0–0.3, m 0.4–1.8), and on that box
+the page's area was 5–21 % low for α 0.15–0.3. `dsgConvolved_array` mirrors
+the server's padded-grid convolution by the same FFT circular convolution:
+< 1e-6 of amplitude (measured ≤ 2e-14 at unit amplitude) across the whole
+β/m box on the base grid and seven other grids, and on the reviewers'
+reproducers (a centre outside the window, irregular grids, a 0.001 eV
+grid); two SERVER limits found on the way (plan §3a: kernel underflow for
+m ≤ 0.003 on an even padded length at 0.1 eV gives an all-zero curve;
+§3b: a centre far outside the padded grid was normalised by rounding
+noise — fixed 2026-09-25 by a guarded branch proven byte-identical for
+in-range centres); nothing changed in Find Peaks or the dropdown
+(a science decision is not altered to work around a rendering bug —
+owner, 2026-09-22). The general lesson repeats §6's: a harness that
 evaluates one representative point per shape proves nothing about the range
 the optimiser can reach.
diff --git a/scripts/local_server_gap.js b/scripts/local_server_gap.js
index 370c215..0344a54 100644
--- a/scripts/local_server_gap.js
+++ b/scripts/local_server_gap.js
@@ -29,7 +29,7 @@ function extractFn(name) {
   throw new Error('unbalanced ' + name);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
diff --git a/scripts/voigt_saved_vs_refit.js b/scripts/voigt_saved_vs_refit.js
index db893cb..72cb798 100644
--- a/scripts/voigt_saved_vs_refit.js
+++ b/scripts/voigt_saved_vs_refit.js
@@ -29,7 +29,7 @@ function extractFn(name) {
   throw new Error('unbalanced ' + name);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic', 'laCasaXPSCore', 'laCasaXPS',
-  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
+  'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array', 'evalPeakArray', 'getPeak', '_applyBackendParams', '_bgWindowIndices'];
 const state = { peaks: [] };
 const fns = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, _applyBackendParams, _bgWindowIndices };')(state);
 const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3', 'python3'].find(p => p === 'python3' || fs.existsSync(p));
diff --git a/tests/js/lineshape_parity.test.js b/tests/js/lineshape_parity.test.js
index 260f3c1..9e7b849 100644
--- a/tests/js/lineshape_parity.test.js
+++ b/tests/js/lineshape_parity.test.js
@@ -156,21 +156,18 @@ for (const shape of ['Gaussian', 'Lorentzian', 'GL', 'Voigt', 'DS', 'asym-GL'])
 //   consistent with backend continuous-m + ceil(3.5*sigma) kernel vs
 //   frontend rounded-m + 2m+1 kernel. Small, monotonic, unit-2 material.
 //
-//   DSG_LA: error is HIGHEST at m=0 (101.8% at laAlpha=0.18/laBeta=0.7 —
-//   the frontend curve is ~zero everywhere) and DECREASES as m grows —
-//   the OPPOSITE shape from LACX. Root cause is NOT a kernel-discretization
-//   gap: JS laCasaXPS() (templates/index.html) sets
-//   `sigma = mGauss / (2*sqrt(2*ln2))`, so mGauss -> 0 drives sigma -> 0 and
-//   its Gaussian-weighted quadrature divides by `2*sigma*sigma` — a literal
-//   division-by-zero/degenerate-weight bug, not a discretization mismatch.
-//   NARROWER than the above sweep alone suggests, though: measured against
-//   the SCHEMA DEFAULT (laM=0.4, laAlpha=0.10, laBeta=0.3, 2026-08-31):
-//   laM=0 -> 100%, 0.1 -> 11.8%, 0.2 -> 0.05%, 0.4 (DEFAULT) -> 0.02%,
-//   0.6+ -> 0%. The shipped default is NOT affected; only laM at or very
-//   near zero (roughly <=0.1) is, and when it fires the peak visibly
-//   vanishes/flattens on screen — loud, not a quiet export-only drift like
-//   LACX/asym-GL were. Its own unit, normal priority — do not fold it into
-//   the LACX kernel-construction fix, and do not hold anything for it.
+//   DSG_LA: FIXED 2026-09-22 (unit fix-dsg-page-evaluator). The page's
+//   evaluator used to be a numerical quadrature (laCasaXPS) whose step
+//   resolved the Lorentzian core (β/3) but not the Gaussian kernel, so it
+//   was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and by 4-14 % of
+//   amplitude on the very box Find Peaks emits for a graphitic C 1s line
+//   (β 0.05, α 0-0.3, m 0.4-1.8) — the A03 sweep, section (D) below. The
+//   m < 0.001 delta branch (dsgDeltaKernel_array) had been mirrored in
+//   2026-08; dsgConvolved_array now mirrors the server's padded-grid
+//   convolution for every m (< 1e-6 of amplitude, measured ≤ 2e-14, across
+//   the fitted box, every grid step, orientation and off-grid centre tested
+//   below).
+//
 test('(A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)', { todo: 'unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)' }, () => {
   const p = basePeak('LACX');
   const x = grid(p.center);
@@ -194,7 +191,7 @@ test('(A) frontend vs backend parity: LACX at m=0 (no convolution)', () => {
     `LACX at m=0: frontend vs backend max diff = ${(rel * 100).toFixed(4)}% of amplitude (tol ${TIGHT_TOL * 100}%)`);
 });
 
-test('(A) frontend vs backend parity: DSG_LA at moderate m — KNOWN GAP, unaddressed', { todo: 'DSG_LA numerical-quadrature-vs-FFT residual, shrinks as m grows (~1.7% at laM=1, ~0.04% at laM=50, measured 2026-08-30) — separate root cause from LACX, see file comment above' }, () => {
+test('(A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)', () => {
   const p = basePeak('DSG_LA');
   const x = grid(p.center);
   const jsY = evalPeakArray(x, p);
@@ -263,7 +260,8 @@ test('(A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid c
 // this mechanism for real callers.
 const ALL_SHAPES = ['Gaussian', 'Lorentzian', 'Voigt', 'GL', 'asym-GL', 'DS', 'DSG_LA', 'LACX'];
 for (const shape of ALL_SHAPES) {
-  const opts = shape === 'LACX' ? { todo: 'evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header' } : undefined;
+  const opts = shape === 'LACX' ? { todo: 'evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header' }
+    : shape === 'DSG_LA' ? { todo: 'evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)' } : undefined;
   test(`(B) evalPeak vs evalPeakArray agree pointwise: ${shape}`, opts, () => {
     const p = basePeak(shape);
     const x = grid(p.center);
@@ -346,9 +344,11 @@ const SWEEP = {
   'DS':         { dsAlpha: [0, 0.25, 0.5], dsGamma: [0, 1, 5], fwhm: FWHM_RANGE },
   'DSG_LA (delta kernel)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0, 0.0009] },
   'LACX (m = 0)': { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0], fwhm: FWHM_RANGE },
+  // the full β/m box the optimiser can reach, incl. the corner that made the
+  // old quadrature 1e52 × amplitude (β 2, m 0.05) and the delta threshold
+  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] },
 };
 const SWEEP_KNOWN_GAP = {
-  'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.05, 0.4, 2, 4] },
   'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
 };
 function sweepShape(label) { return label.split(' ')[0]; }
@@ -393,3 +393,90 @@ for (const [label, ranges] of Object.entries(SWEEP_KNOWN_GAP)) {
       `${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
   });
 }
+
+// ── (D′) DS+G convergence beyond the base grid (unit fix-dsg-page-evaluator) ──
+// The convolution is a GRID operation: the server pads at the data step,
+// builds its kernel on it and normalises at the interpolated centre. So the
+// box is swept again on a coarser and a finer step, a DESCENDING grid (real
+// acquisitions), a centre half a step off-grid, a short window, and a
+// window narrower than the pad — every case at the 1e-6 tolerance.
+function gridOf(center, step, n, { descending = false, offset = 0 } = {}) {
+  const x = [];
+  for (let i = 0; i < n; i++) x.push(center - (step * n) / 2 + step * i + offset);
+  return descending ? x.reverse() : x;
+}
+const DSG_GRID_CASES = [
+  { label: 'step 0.1 eV, 120 pts', step: 0.1, n: 120 },
+  { label: 'step 0.02 eV, 500 pts', step: 0.02, n: 500 },
+  { label: 'step 0.05 eV, descending', step: 0.05, n: 200, descending: true },
+  { label: 'step 0.05 eV, centre half a step off-grid', step: 0.05, n: 200, offset: 0.025 },
+  { label: 'step 0.1 eV, descending, centre 0.03 eV off-grid', step: 0.1, n: 120, descending: true, offset: 0.03 },
+  { label: 'short window: 30 pts at 0.1 eV (narrower than the pad)', step: 0.1, n: 30 },
+  { label: 'irregular-ish step 0.0503 eV (median step), 181 pts', step: 0.0503, n: 181 },
+];
+const DSG_BOX = { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] };
+for (const g of DSG_GRID_CASES) {
+  test(`(D′) DS+G convolution converges on another grid: ${g.label}`, () => {
+    const cases = combos(DSG_BOX).map(c => ({ c, p: { ...basePeak('DSG_LA'), ...c } }));
+    const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: gridOf(k.p.center, g.step, g.n, g) }; });
+    const beYs = backendEvalMany(specs);
+    const worst = cases.map((k, i) => ({ c: k.c, rel: maxRelDiff(evalPeakArray(specs[i].x, k.p), beYs[i], k.p.amplitude) })).sort((a, b) => b.rel - a.rel);
+    assert.ok(worst[0].rel < TIGHT_TOL,
+      `${g.label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} combinations diverge; worst ${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
+  });
+}
+
+// ── (D″) DS+G: the cases Codex round 1 broke the first cut with, and the ──
+// server's own degenerate zone. The first cut summed the convolution
+// directly within 8 σ and clipped at the padded array's ends; the server's
+// FFT is CIRCULAR, so a DS tail that reaches the far end wraps — visible
+// with a centre outside the window (0.41 × amplitude off) and on a
+// short irregular grid. _circularConvolve now does what the FFT does.
+const DSG_REGRESSIONS = [
+  { label: 'centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)', x: Array.from({ length: 200 }, (_, i) => (i - 99.5) * 0.05), center: 10, laAlpha: 0.25, laBeta: 0.05, laM: 0.4 },
+  { label: 'a 6-point irregular grid', x: [-3, -2.9, -2.8, 0, 2, 3], center: 0, laAlpha: 0.25, laBeta: 0.05, laM: 0.05 },
+  { label: 'genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)', x: (() => { const o = []; let v = 280; for (let i = 0; i < 200; i++) { o.push(v); v += i % 2 ? 0.06 : 0.05; } return o; })(), center: 285.3, laAlpha: 0.3, laBeta: 0.7, laM: 1.2 },
+  { label: 'a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)', x: Array.from({ length: 10001 }, (_, i) => 280 + 0.001 * i), center: 285, laAlpha: 0.49, laBeta: 2, laM: 4 },
+  // the guarded branch (server 2026-09-25, mirrored): a centre OUTSIDE the padded grid is normalised by the maximum
+  { label: 'centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)', x: Array.from({ length: 21 }, (_, i) => -5 + 0.5 * i), center: 10, laAlpha: 0.49, laBeta: 0.05, laM: 0.05 },
+  { label: 'centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001', x: Array.from({ length: 201 }, (_, i) => -5 + 0.05 * i), center: -10, laAlpha: 0.49, laBeta: 0.05, laM: 0.001 },
+  { label: 'centre just outside the padded grid (6.5 eV, pad 1 eV)', x: Array.from({ length: 200 }, (_, i) => (i - 99.5) * 0.05), center: 6.5, laAlpha: 0.25, laBeta: 0.05, laM: 0.05 },
+  { label: 'centre just inside the padded grid (5.999 eV, pad 1 eV)', x: Array.from({ length: 200 }, (_, i) => (i - 99.5) * 0.05), center: 5.999, laAlpha: 0.25, laBeta: 0.05, laM: 0.05 },
+  { label: 'a 2-point grid', x: [284.4, 284.6], center: 284.5, laAlpha: 0.2, laBeta: 0.3, laM: 0.4 },
+  { label: 'a 1-point grid', x: [284.5], center: 284.5, laAlpha: 0.2, laBeta: 0.3, laM: 0.4 },
+];
+for (const c of DSG_REGRESSIONS) {
+  test(`(D″) DS+G regression: ${c.label}`, () => {
+    const p = { ...basePeak('DSG_LA'), amplitude: 1, center: c.center, laAlpha: c.laAlpha, laBeta: c.laBeta, laM: c.laM };
+    const { shape, params } = backendParamsFromRequest(p);
+    const beY = backendEval(shape, params, c.x);
+    const t0 = Date.now();
+    const jsY = evalPeakArray(c.x, p);
+    const ms = Date.now() - t0;
+    const rel = maxRelDiff(jsY, beY, 1);
+    assert.ok(rel < TIGHT_TOL, `${c.label}: max diff ${rel.toExponential(3)} of amplitude (server max ${Math.max(...beY.map(Math.abs)).toExponential(2)})`);
+    assert.ok(ms < 2000, `${c.label}: ${ms} ms for one curve — the cost must stay bounded (O(n log n))`);
+  });
+}
+
+// KNOWN SERVER LIMIT (not this unit's to change; recorded for the owner):
+// just above the 0.001 delta threshold the server's Gaussian kernel can
+// UNDERFLOW on a coarse grid — σ = m/2.355 far below the step, so no
+// padded-grid sample carries kernel weight (for an even padded length the
+// nearest sample is half a step from the centre) — and the server returns
+// an all-zero curve for the component. The page mirrors it exactly (a
+// vanished curve drawn as vanished, never a curve the server did not fit).
+// The zone closes quickly: at 0.1 eV, m = 0.02 is already ordinary.
+for (const laM of [0.001, 0.002, 0.02, 0.05]) {
+  test(`(D″) DS+G at m = ${laM} on a 0.1 eV grid: page equals server${laM <= 0.002 ? ' (both an all-zero curve — the server kernel underflows; known server limit)' : ''}`, () => {
+    const x = Array.from({ length: 120 }, (_, i) => 290 - 0.1 * i);
+    const p = { ...basePeak('DSG_LA'), amplitude: 1, center: 284.5, laAlpha: 0.25, laBeta: 0.7, laM };
+    const { shape, params } = backendParamsFromRequest(p);
+    const beY = backendEval(shape, params, x);
+    const jsY = evalPeakArray(x, p);
+    assert.ok(maxRelDiff(jsY, beY, 1) < TIGHT_TOL, `m = ${laM}: page vs server ${maxRelDiff(jsY, beY, 1).toExponential(3)}`);
+    const serverMax = Math.max(...beY.map(Math.abs));
+    if (laM <= 0.002) assert.equal(serverMax, 0, `m = ${laM}: the server curve is expected to vanish here (kernel underflow) — if it no longer does, the server changed; update this characterisation`);
+    else assert.ok(serverMax > 0.9, `m = ${laM}: a real curve`);
+  });
+}
diff --git a/tests/js/lineshape_roundtrip.test.js b/tests/js/lineshape_roundtrip.test.js
index b0153d6..4103c52 100644
--- a/tests/js/lineshape_roundtrip.test.js
+++ b/tests/js/lineshape_roundtrip.test.js
@@ -15,10 +15,10 @@
 // page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
 // server FITTED (individual_peaks[].y).
 //
-// Two shapes carry a known drawn-vs-fitted gap and are marked todo with the
-// unit that owns it: LACX (the page sends m free and draws it ROUNDED —
-// the caM clamp unit) and DSG_LA (the page's quadrature — see the parity
-// harness's section (D)).
+// One shape carries a known drawn-vs-fitted gap and is marked todo with the
+// unit that owns it: LACX (the page sends m free and draws it ROUNDED — the
+// caM clamp unit). DSG_LA was the other until 2026-09-22 (the page's
+// quadrature; now dsgConvolved_array mirrors the server).
 const { test } = require('node:test');
 const assert = require('node:assert');
 const { execFileSync } = require('node:child_process');
@@ -41,7 +41,7 @@ function extractFn(name) {
   assert.fail(`unbalanced braces extracting ${name}`);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'getPeak', 'peakToBackendSpec', '_applyBackendParams'];
 const state = { peaks: [] };
 const env = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, peakToBackendSpec, _applyBackendParams };')(state);
@@ -92,7 +92,6 @@ const CASES = {
 };
 const TIGHT_TOL = 1e-6;      // of amplitude; both curves are the same closed form on the same grid
 const KNOWN_GAP = {
-  'DSG_LA': 'DSG_LA: the page quadrature (laCasaXPS) diverges from the server across the fitted range — parity harness section (D); own unit',
   'LACX':   'LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit',
 };
 
@@ -190,10 +189,10 @@ const LOCKED_AT_BOUNDS = [
   { label: 'LA beta 5 locked (m = 0)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 5, caM: 0, fixCaBeta: true, fixCaM: true }, held: { beta: 5, m: 0 } },
   // the page's input allows α = 0.5; the server's evaluator clips α to 0.495 and so, since round 3, does the page's
   { label: 'DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)', truth: { shape: 'DSG_LA', laAlpha: 0.5, laBeta: 0.5, laM: 0, fixLaAlpha: true, fixLaM: true }, held: { alpha: 0.5, m_gauss: 0 } },
-  // the convolved shapes' m locks at m > 0: request and server-held value are pinned; the drawn-vs-fitted
-  // comparison sits under the evaluator gaps marked todo above (curve: false)
-  { label: 'DS+G m 0.05 locked (request and hold only)', truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.05, fixLaM: true }, held: { m_gauss: 0.05 }, curve: false },
-  { label: 'DS+G m 4 locked (request and hold only)',    truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 4, fixLaM: true }, held: { m_gauss: 4 }, curve: false },
+  // LA's m lock at m > 0: request and server-held value are pinned; the drawn-vs-fitted
+  // comparison sits under the caM evaluator gap marked todo above (curve: false)
+  { label: 'DS+G m 0.05 locked', truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.05, fixLaM: true }, held: { m_gauss: 0.05 } },
+  { label: 'DS+G m 4 locked',    truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 4, fixLaM: true }, held: { m_gauss: 4 } },
   { label: 'LA m 499 locked (request and hold only)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 }, curve: false },
 ];
 for (const c of LOCKED_AT_BOUNDS) {
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 5c42284..024ca96 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -35,7 +35,7 @@ function extractFn(name) {
 }
 
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
fitting.py:152:def _ds_g_dscore_gauss(
fitting.py:785:    "ds_g": _ds_g_dscore_gauss,
fitting.py:1148:def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
fitting.py:1640:        random_seed = _request_seed(
templates/index.html:4048:  // convolution is a GRID operation and lives in dsgConvolved_array (called
templates/index.html:4137:    // the server clips it (_ds_g_dscore_gauss: 0 ≤ α ≤ 0.495) so a locked
templates/index.html:4153:// _ds_g_dscore_gauss `m_gauss < 0.001` path EXACTLY, including its
templates/index.html:4159:// The server's DS+G clips α to [0, 0.495] (_ds_g_dscore_gauss); the page
templates/index.html:4243:// fitting._ds_g_dscore_gauss (m ≥ 0.001; below that the delta branch above):
templates/index.html:4258:function dsgConvolved_array(beArr, center, alpha, beta, mGauss) {
templates/index.html:4356:    const yArr = dsgConvolved_array(beArr, p.center, p.laAlpha, p.laBeta, p.laM || 0);
scripts/run_stress_battery.py
scripts/gen_c1s_battery_fixture.py
scripts/gen_region_battery_fixture.py
scripts/summarize_stress_battery.py
scripts/gen_u4f_battery_fixture.py
requirements.txt
requirements-dev.txt
tests/autofit/test_u4f_parity_battery.py
tests/autofit/test_c1s_parity_battery.py
tests/autofit/battery_common.py
tests/autofit/fixtures/c1s_battery_expected.json
tests/autofit/fixtures/u4f_battery_expected.json
tests/autofit/fixtures/b1s_battery_expected.json
tests/autofit/fixtures/cl2p_battery_expected.json
docs/autofit/inventory/stress_battery_runs.jsonl

exec
/bin/zsh -lc "sed -n '152,325p' fitting.py; cat tests/test_dsg_outside_centre.py; cat docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt; sed -n '1,260p' docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
def _ds_g_dscore_gauss(
    x: np.ndarray,
    amplitude: float,
    center: float,
    alpha: float,    # CasaXPS: dimensionless asymmetry index, 0 ≤ α < 0.5
    beta: float,     # CasaXPS: Lorentzian half-width (eV)
    m_gauss: float,  # CasaXPS: Gaussian FWHM (eV) for convolution
) -> np.ndarray:
    """
    DS+G lineshape (formerly mislabeled "LA(α,β,m) [CasaXPS]") —
    Doniach-Šunjić asymmetric core convolved analytically with a Gaussian
    instrument-broadening kernel. NOT to be confused with the true CasaXPS
    LA shape (see _la_casaxps_true), which uses a piecewise-asymmetric
    Lorentzian with point-domain Gaussian convolution.

    The DS core with asymmetry index α and Lorentzian half-width β is convolved
    with a Gaussian of FWHM m for instrument broadening.

    Tail direction: eps = x − center > 0 → HIGHER binding energy (physically
    correct: low-energy electron-hole pair excitations produce intensity on the
    high-BE side only).

    Parameters
    ----------
    alpha   : dimensionless asymmetry index, 0 ≤ α < 0.5
              (0 = symmetric Lorentzian, ~0.1–0.3 for metallic systems)
    beta    : Lorentzian half-width at half-maximum (eV); controls core width
    m_gauss : Gaussian FWHM (eV) for instrument/phonon broadening (0 = none)

    Fixes (v2)
    ----------
    1. Convolution uses a padded grid (±10·m on each side) with cosine taper
       to eliminate cliff artifacts at array boundaries.
    2. Explicit FFT convolution with a properly normalised Gaussian kernel,
       so DS tail direction is preserved regardless of m value.
    """
    alpha   = float(np.clip(alpha, 0.0, 0.495))
    beta    = max(float(beta),    1e-6)
    m_gauss = max(float(m_gauss), 0.0)

    # ── DS core evaluator (independent of m_gauss) ───────────────────────────
    #
    # eps = x − center: positive on HIGH-BE side (where tail belongs)
    # DS formula:  cos(πα/2 − (1−α)·arctan2(ε, β)) / (ε² + β²)^((1−α)/2)
    #
    # Sign convention proof:
    #   At ε >> β (high BE):  arctan2(ε, β) → +π/2
    #     phase → πα/2 − (1−α)·π/2 → −π(1−2α)/2  (negative for α < 0.5)
    #     cos(phase) > 0, and denominator grows as |ε|^(1−α)
    #     → slow power-law decay toward HIGH BE  ✓
    #   At ε << −β (low BE): arctan2(ε, β) → −π/2
    #     phase → πα/2 + (1−α)·π/2 → π/2  (for small α)
    #     cos(phase) → 0, faster falloff
    #     → steeper decay toward LOW BE  ✓

    def _ds_core(xgrid):
        """Evaluate DS kernel on arbitrary grid. Independent of m_gauss."""
        eps = xgrid - center
        r2 = eps ** 2 + beta ** 2
        r2 = np.maximum(r2, 1e-30)
        rPow = r2 ** ((1.0 - alpha) / 2.0)
        phase = np.pi * alpha / 2.0 - (1.0 - alpha) * np.arctan2(eps, beta)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            core = np.cos(phase) / rPow
        core = np.where(np.isfinite(core), core, 0.0)
        return core

    # ── No Gaussian broadening — just return normalised DS core ──────────────
    if m_gauss < 0.001:
        ds_core = _ds_core(x)
        peak_val = float(np.interp(center, x if x[-1] > x[0] else x[::-1],
                                   ds_core if x[-1] > x[0] else ds_core[::-1]))
        if peak_val <= 0.0:
            peak_val = np.max(np.abs(ds_core))
        if peak_val <= 0.0:
            return np.zeros_like(x)
        return amplitude * ds_core / peak_val

    # ── Build padded grid for convolution ─────────────────────────────────────
    # Pad by ±10·m_gauss (≈ ±4.25σ) to avoid truncation artifacts.
    # The DS power-law tail decays as |ε|^(α−1), which is slow for small α,
    # so generous padding is essential.
    step = float(np.median(np.abs(np.diff(x)))) if len(x) > 1 else 0.05
    step = max(step, 1e-6)

    pad_ev = max(10.0 * m_gauss, 20.0 * beta)  # eV of padding on each side
    n_pad = int(np.ceil(pad_ev / step))
    n_pad = max(n_pad, 1)

    # Determine sort direction of input x
    ascending = (x[-1] > x[0]) if len(x) > 1 else True

    # Create padded energy grid extending beyond the data range
    if ascending:
        x_pad_lo = x[0] - n_pad * step
        x_pad_hi = x[-1] + n_pad * step
    else:
        x_pad_lo = x[-1] - n_pad * step
        x_pad_hi = x[0] + n_pad * step

    n_total = len(x) + 2 * n_pad
    x_padded = np.linspace(x_pad_lo, x_pad_hi, n_total)  # always ascending

    # Evaluate DS core on padded grid
    ds_padded = _ds_core(x_padded)

    # ── Cosine taper on pad regions ───────────────────────────────────────────
    # Smoothly ramp to zero at the array edges to kill any residual signal
    # that would cause Gibbs-like ringing in FFT convolution.
    taper = np.ones(n_total)
    if n_pad > 1:
        # Left taper: 0→1 over n_pad points (half cosine)
        taper[:n_pad] = 0.5 * (1.0 - np.cos(np.linspace(0, np.pi, n_pad)))
        # Right taper: 1→0 over n_pad points
        taper[-n_pad:] = 0.5 * (1.0 + np.cos(np.linspace(0, np.pi, n_pad)))
    ds_padded *= taper

    # ── FFT convolution with Gaussian kernel ──────────────────────────────────
    # σ_eV = m_gauss / (2√(2·ln2))  (convert FWHM to sigma)
    sigma_ev = m_gauss / (2.0 * np.sqrt(2.0 * np.log(2.0)))

    # Kernel grid centred at zero, same length as padded array (for FFT)
    n_k = len(x_padded)
    k_half = (n_k - 1) / 2.0
    k_grid = (np.arange(n_k) - k_half) * step  # eV relative to centre
    gauss_kernel = np.exp(-0.5 * (k_grid / sigma_ev) ** 2)
    gauss_kernel /= gauss_kernel.sum()  # normalise to unit area

    # FFT convolution (circular, but padding makes edge effects negligible)
    ft_ds = np.fft.rfft(ds_padded)
    ft_gk = np.fft.rfft(np.fft.ifftshift(gauss_kernel))
    ds_conv = np.fft.irfft(ft_ds * ft_gk, n=n_total)

    # ── Interpolate back to original x grid ───────────────────────────────────
    # x_padded is always ascending; np.interp handles arbitrary query points.
    result = np.interp(x, x_padded, ds_conv)

    # ── Normalise so value at x = center equals amplitude ─────────────────────
    if center < x_padded[0] or center > x_padded[-1]:
        # NEW GUARDED BRANCH (2026-09-25, unit fix-dsg-page-evaluator): the
        # centre lies OUTSIDE the padded grid, so "the value at the centre"
        # is np.interp's clamped end value — the tail of a curve whose peak
        # is not on the grid, of order 1e-20 once the tapers have acted, and
        # its SIGN decided which of two unrelated curves came back (the
        # max-normalised tail, or that tail divided by ~1e-20; Codex round 2
        # of the unit). Normalise by the curve's maximum instead. A centre
        # inside the padded grid takes the branch below, unchanged.
        peak_val = float(np.max(np.abs(result)))
        if peak_val <= 0.0:
            return np.zeros_like(x)
    else:
        # Interpolate at exact center rather than nearest grid point to avoid
        # normalization error when center falls between data points.
        peak_val = float(np.interp(center, x_padded, ds_conv))
        if peak_val <= 0.0:
            peak_val = np.max(np.abs(result))
        if peak_val <= 0.0:
            return np.zeros_like(x)

    result = amplitude * result / peak_val

    # Final safety: suppress any NaN/Inf
    return np.where(np.isfinite(result), result, 0.0)


# ─────────────────────────────────────────────────────────────────────────────
# Background functions
# ─────────────────────────────────────────────────────────────────────────────

def _apply_endpoint_averaging(y: np.ndarray, n_avg: int) -> np.ndarray:
    """Return a copy of *y* with the first/last *n_avg* points replaced by their mean."""
    n = len(y)
    if n_avg <= 1 or n < 4:
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
1. box x grids x centres inside the padded grid: 3780 byte-identical, 0 differ (worst |delta| 0)
2. 2000 random draws, centre inside the padded grid: 2000 byte-identical, 0 differ
3. run_fit (leastsq, n_perturb 0) on the C1s Scan with a DS+G Graphite line: byte-identical JSON (43172 bytes)
3. run_fit (leastsq, n_perturb 3) on the C1s Scan with a DS+G Graphite line: byte-identical JSON (43169 bytes)
4. centre 10 eV outside [-5, 5]: old max 5.35e+04, new max 1 (the guarded branch)
4. centre -10 eV, low-BE side: old max 2.61e+03, new max 1 (the guarded branch)
# DS+G page evaluator — a grid-aware mirror of the server's convolution (2026-09-22)

Branch `fix-dsg-page-evaluator` off main `b3c9e37` (A03 deployed). Owner's
brief: "Port the server's convolution to a grid-aware page evaluator.
Acceptance: the existing todo tests (parity sweep DS+G box at 1e-6, the
round-trip case), PLUS convergence demonstrated across the full β/m range the
optimiser can reach — including the corners that produced 1e52, not only the
Find Peaks box. Nothing de-listed, nothing changed in Find Peaks." Interim
red notice skipped unless a third Codex round or more than a day.

## 1. The defect (A03 sweep, section (D))

The page drew, integrated and exported a DS+G component with `laCasaXPS`, a
numerical quadrature whose step resolved the Lorentzian core (β/3) but not
the Gaussian kernel (σ = m/2.355). At β = 2, m = 0.05 the step was 0.67 eV
against σ = 0.021 eV and the curve was 1e52 × amplitude; across the fitted
box the page's area was 23–64 % of the server's. On the exact box Find Peaks
emits for a graphitic C 1s line (`autofit/regions/c1s.py`: β fixed at 0.05,
α 0–0.3, m in the graphitic FWHM range 0.4–1.2, polymers 0.8–1.8) the page's
curve was off by up to 13.7 % of amplitude and its area 5–21 % low for
α 0.15–0.3 (α = 0 was fine). Every A- and M-family candidate is built on
that slot, so an applied suggestion was drawn and quantified wrong; the
manual dropdown was the same path. 0 of the 530 committed peak records use
DS+G.

## 2. The fix

`dsgConvolved_array(beArr, center, alpha, beta, m)` in `templates/index.html`
is a literal mirror of `fitting._ds_g_dscore_gauss` for m ≥ 0.001 (the
m < 0.001 delta branch, `dsgDeltaKernel_array`, was already mirrored):

- α clipped to [0, 0.495], β ≥ 1e-6, m ≥ 0 — as the server;
- step = median |Δx| (numpy's median), ≥ 1e-6;
- padded grid ±max(10 m, 20 β) at that step, `np.linspace` semantics
  (always ascending, endpoint set exactly);
- DS core on the padded grid, non-finite → 0; half-cosine tapers over each
  pad (`np.linspace(0, π, n_pad)`);
- Gaussian kernel of σ = m/(2√(2 ln 2)) on the same step, centred at
  (n − 1)/2, normalised to unit sum over the FULL padded length;
- the server's circular convolution `irfft(rfft(ds)·rfft(ifftshift(k)))`
  computed as what it is: `_circularConvolve` — a zero-padded linear
  convolution by radix-2 FFT (`_fftRadix2`, length the power of two
  ≥ 2n − 1) folded back to n. Every wrapped contribution the server
  includes is included; O(n log n) on any grid. (The first cut summed
  directly within 8 σ and clipped at the array ends; Codex round 1 showed a
  centre outside the window 0.41 × amplitude off — the DS tail reaches the
  padded array's far end and the server's FFT wraps it — and 13 s per
  curve at 0.001 eV. Both gone.)
- `np.interp` back to the data grid; normalised by the value interpolated AT
  the centre (fallbacks as the server's); non-finite → 0.

`evalPeakArray` routes every DS+G through it (the delta branch inside). The
scalar `evalPeak` DSG_LA branch keeps the name `laCasaXPS` but is now the
normalised DS core with m ignored — the same status as its LACX branch;
guard (C) of the parity harness proves no shipped caller reaches it. The
old quadrature is deleted, not tuned.

Cost (FFT, one curve at the box's far corner β 2, m 4, α 0.49): 1.1 ms on a
241-point 0.05 eV grid, 8 ms at 0.02 eV (601 points), 13 ms at 0.005 eV,
58 ms at 0.001 eV over 10 eV (the first cut: 13 s); Find Peaks-like
parameters 0.2–1.1 ms; a local fit of a DS+G component converges in 38 ms.

## 3. Acceptance (measured)

| check | result |
|---|---|
| parity sweep (D), DS+G box α {0, 0.25, 0.49} × β {0.05, 0.7, 2} × m {0.001, 0.05, 0.4, 2, 4}, base grid | ≤ 2e-14 of amplitude (3e-15 at the harness amplitude, 1.95e-14 at unit amplitude; was 1e52 at β 2, m 0.05) — now a hard assertion at 1e-6 |
| (D′) the same box on: 0.1 eV step; 0.02 eV step; descending grid; centre half a step off-grid; descending + 0.03 eV off-grid; a 30-point window narrower than the pad; a 0.0503 eV step | < 1e-6 on every combination (measured ≤ 6e-14) — hard assertions |
| (A) DS+G at the base peak (was todo) | hard, passes |
| round trip page → server → page, DS+G (was todo), and DS+G m locked at 0.05 and at 4 (curve comparison was disabled) | hard, pass |
| (B) scalar vs array evaluator, DS+G | now `todo` like LACX: the convolution is a grid operation; guard (C) holds |
| Find Peaks box (β 0.05, α 0–0.3, m 0.4–1.8, 0.05 and 0.1 eV grids) | agrees with the server to 1e-6 (was 5–21 % low in area) |
| (D″) regressions: a centre 10 eV outside a [−5, 5] window; a 6-point irregular grid; alternating 0.05/0.06 steps (median ≠ mean); a 0.001 eV grid over 10 eV at β 2, m 4, α 0.49; 2- and 1-point grids | < 1e-6 (5e-12 relative on the outside-centre case whose server maximum is 48; 3.5e-13 at 0.001 eV) — hard; each curve under 2 s asserted |
| (D″) m = 0.001, 0.002, 0.02, 0.05 on a 0.1 eV grid | page equals server at every m; at m ≤ 0.002 BOTH are an all-zero curve — a KNOWN SERVER LIMIT (§3a), pinned as such |

### 3a. Server limit found on the way (not this unit's to change)

Just above the 0.001 delta threshold on a coarse grid the server's Gaussian
kernel underflows: σ = m/2.355 is far below the step, no padded-grid sample
carries weight (for an even padded length the nearest sample is half a
step from the centre), the kernel normalises to NaN and
`_ds_g_dscore_gauss` returns an all-zero curve for the component (its final
"suppress NaN/Inf" turns it to zeros). It happens only for an EVEN padded
length (the nearest sample is half a step from the centre); an odd length
has a sample at the centre and the kernel collapses to a delta instead. On
a 120-point 0.1 eV grid the zone is 0.001 ≤ m ≤ 0.003 (m = 0.00305 is
already a normal curve); on 121 points there is none. A fit will not settle there (a zero curve fits
nothing), but a LOCKED m in that zone is fitted as zero. The page mirrors
it exactly (a vanished curve drawn as vanished, never a curve the server
did not fit). Recorded for the owner; the fix belongs to the server (a
kernel that collapses to a delta below the grid's resolution, as the
threshold branch does).

### 3b. Server limit found in round 2 — FIXED by a guarded branch (2026-09-25, owner's option 2)

The server normalises the convolved curve by its value interpolated AT THE
CENTRE, falling back to the curve's maximum only when that value is ≤ 0.
With the centre far OUTSIDE the padded grid (e.g. 10 eV outside a
[−5, 5] window at β 0.05, m 0.05, or 15 eV outside on the low-BE side)
the interpolated value is the clamped end value of a tail of order 1e-20 —
rounding noise whose SIGN decides which of two unrelated curves the server
returns: the max-normalised tail (sign negative) or that tail divided by
~1e-20 (sign positive). The page mirrors the rule and the arithmetic, but
not the rounding sign of a 1e-20 number, and Codex round 2 reproduced a
case where the two sides fall on different branches (server maximum 1,
page 5e16). No committed model is near this regime (a component centred
outside its own window has no physical reading, and a fit does not settle
there), and the server's own output there is arbitrary.

Owner's condition (2026-09-25): a NEW GUARDED BRANCH, not a modification
of the existing normalisation, PROVEN byte-identical for every centre
inside the padded grid — otherwise stop and take option 1. Done:
`_ds_g_dscore_gauss` now has `if center < x_padded[0] or center >
x_padded[-1]: peak_val = max|result|` with the pre-existing code in the
`else`. Proof (`scripts/dsg_outside_centre_identity.py`, main's function
loaded from `git show main:fitting.py` beside the new one, output in
`docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt`):
3,780 box × grid × centre cases (centres at the window centre, off-grid,
at each data edge and 1e-9 inside each padded edge) and 2,000 random
draws with the centre inside the padded grid — 5,780 of 5,780
`np.array_equal`; `run_fit` on the committed UCl4-graphite C1s Scan with
its Graphite line as DS+G (n_perturb 0 and 3, Levenberg-Marquardt, the
byte-identical method): the whole JSON response identical; the committed
batteries hold no DS+G component and pass unchanged. The two outside
cases: old maximum 5.4e4 and 2.6e3 × amplitude, new 1. The page mirrors
the branch (`dsgConvolved_array`); both reproducers are hard regressions
in (D″), plus a centre just outside and just inside the padded edge.

Nothing changed on the server, in `autofit/`, in Find Peaks or in the
dropdown. Python suite untouched by this unit (no Python change); JS suite
and browser check in §5.

## 4. Sites

`laCasaXPS` (rewritten), `dsgConvolved_array` (new), `evalPeakArray`;
every function-extractor list that names the lineshape block
(`tests/js/lineshape_roundtrip.test.js`, `local_lm_descent.test.js`,
`scripts/local_server_gap.js`, `scripts/voigt_saved_vs_refit.js`) now lists
`dsgConvolved_array`; `tests/js/lineshape_parity.test.js` (A), (B), (D),
(D′); `tests/js/lineshape_roundtrip.test.js`; CLAUDE.md; findings §7.

## 5. Verification

- JS suite: 392 tests, 387 pass, 0 fail, 5 todo (`node --test tests/js/*.test.js`).
  The five: LACX m > 0 in (A), (B) and (D); (B) DS+G (scalar evaluator
  ignores m, by design); the LACX round trip.
- Python suite: untouched by this unit (no Python change); the A03 run on
  the same server code was 989 passed / 7 skipped.
- Browser check (`browser_check_dsg.py`, dev gunicorn :5151 with the
  production `--timeout 300`): the committed UCl4-graphite C1s Scan with its
  Graphite line switched to DS+G at Find Peaks' parameters (β 0.05, α 0.2,
  m 0.8), Run Fit (fitted α 0, β 0.053, m 0.62): the curve the page draws
  for it equals the server's fitted curve to 1.2e-12 of amplitude (the five
  GL lines 1e-13); its Results area equals the server curve's to 0.0000 %;
  the chart dataset is the drawn curve; a `ds_g` Find Peaks candidate maps
  to DSG_LA with its α, β, m; no page errors.

## 5a. Finding on the way: a DS+G Run Fit costs the server ~110 s

Not this unit's change (fitting.py is untouched) and present on main
today. On the committed UCl4-graphite C1s Scan (191 points, 0.1 eV) with
the Graphite line switched to DS+G at Find Peaks' parameters (β 0.05,
α 0.2, m 0.8) and five GL lines: the plain fit takes 0.4 s (640 DS+G
evaluations, 0.3 ms each), but each of the page's `n_perturb: 3` restarts
takes ~18 s (28,821 evaluations — the perturbed descent runs to the
optimiser's evaluation budget), and with `n_starts: 3` the request takes
110 s. Production's gunicorn `--timeout 300` covers it; a dev server on the
30 s default returns a worker timeout and the page reports "Fit failed".
Every A- and M-family Find Peaks candidate applied and re-fitted pays this.
Logged for its own look (why the perturbed DS+G descent does not converge;
whether the restarts should be skipped or capped for this shape).

## 6. Codex rounds

**Round 1 (`docs/autofit/codex/dsg_page_evaluator_verdict_run{A,B}.md`):
NO-GO ×2.** Fixed:
1. MAJOR — the first cut's direct sum clipped at the padded array's ends
   and so omitted the wrapped contributions the server's circular FFT
   includes: a centre 10 eV outside a [−5, 5] window was 0.41 × amplitude
   off (the normalisation at the clamped centre scales every value), a
   6-point irregular grid 2.9e-4. Replaced by the same circular
   convolution, computed by FFT (`_fftRadix2`, `_circularConvolve`); both
   reproducers are regression tests, agreeing to 5e-12 and 1e-16.
2. MAJOR — quadratic cost on fine grids (13.5 s per curve at 0.001 eV).
   The FFT makes it O(n log n): 58 ms at 0.001 eV, 8 ms at 0.02 eV; a test
   asserts each regression curve under 2 s.
3. MINOR — (D′)'s "irregular-ish" grid was uniform, and its m = 0.001 case
   passed on a curve that had vanished on BOTH sides. A genuinely
   irregular grid (alternating 0.05/0.06 steps) is in (D″); the vanished
   curve is the server's own kernel underflow just above the delta
   threshold on a coarse grid — characterised in §3a and pinned as a known
   server limit (page equals server; the server curve is asserted to be
   zero there so a server change surfaces).
4. MINOR — findings §7 said ≤ 3e-15 across seven grids; that was the base
   grid (the seven are < 1e-6, measured ≤ 5.5e-15). Corrected.

**Round 2 (`dsg_page_evaluator_r2_verdict_run{A,B}.md`): NO-GO ×2.**
Round-1 items 1–3 confirmed closed. Found: MAJOR — the normalisation
conditioning of §3b (centre far outside the padded grid; the server's own
output there is decided by the sign of rounding noise); MINOR — the
precision figures were quoted at the harness amplitude (at unit amplitude
1.95e-14 base grid, 5.8e-14 at 0.02 eV; corrected above); MINOR — the
underflow zone's description (corrected in §3a: even lengths only, up to
m = 0.003 on 120 points). **Stopped here per the owner's rule (a third
round): the remaining MAJOR is a server conditioning limit outside this
unit, documented in §3b with the fix that belongs to the server;
everything physically reachable on the page is a hard 1e-6 assertion.**
The interim red notice was NOT added: its wording ("the page's curve and
area for this shape are not yet exact") would now be false. Decision to
the owner.

**Owner decision (2026-09-25): option 2 with a hard condition** — the
server change as a new guarded branch, byte-identical for in-range centres
on the committed battery, else stop; then mirror on the page and one Codex
round; no interim notice; §3a documented and left (it degrades honestly:
an all-zero curve reads as a zero-amplitude component, which step (b)
flags as not supported by the data). Done as §3b records. Logged
separately, not urgent: the ~110 s DS+G Run Fit (§5a) — likely the same
evaluation-budget question as the Find Peaks speed item.

exec
/bin/zsh -lc "git diff main..HEAD -- CLAUDE.md docs/findings/2026-09-fit-determinacy.md; sed -n '1148,1198p' fitting.py; sed -n '1,140p' tests/js/lineshape_parity.test.js; ls -d venv /Users/skyefortier/xps-app/venv 2>/dev/null; rg -n 'evaluate_peak|_SHAPE_FUNCS|ds_g' autofit/parity.py autofit/engine.py tests/autofit/battery_common.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-1D6SN8YE' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-bzU3U5te' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index e54491f..d4550d8 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -132,13 +132,24 @@ to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
 `_make_peak_params._set` now widens a limit to a held value), and the
 server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
 held parameter is held at its value; what the page draws is what the
-server fitted. Tracked gaps, `todo` in both files: LACX with m > 0 (the page draws
+server fitted. Tracked gap, `todo` in both files: LACX with m > 0 (the page draws
 a rounded integer kernel; the server fits m continuously — the `caM` clamp
-unit) and DS+G with m ≥ 0.05 (the page's quadrature `laCasaXPS` sizes its
-step to the Lorentzian core, not the Gaussian kernel, and is wrong by up to
-80 % of amplitude across the fitted β/m range — 1e52 × at β = 2, m = 0.05;
-0 of the 530 peak records in the seven committed projects use DS+G; its own unit). Details in
-`docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
+unit). DS+G was the other gap until 2026-09-22 (the page's quadrature
+`laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
+and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
+in area on the very box Find Peaks emits for a graphitic C 1s line);
+`dsgConvolved_array` now mirrors the server's padded-grid convolution for
+every m — the same FFT circular convolution — pinned at 1e-6 across the
+full β/m box on eight grids, irregular grids and centres outside the
+window (`docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md`). Two
+server limits found there: a DS+G m just above the 0.001 delta threshold
+on a coarse grid (m ≤ 0.003 at 0.1 eV, even padded length) underflows the
+kernel and returns an all-zero curve — left as is, it reads as a
+zero-amplitude component and step (b) flags it; and a centre OUTSIDE the
+padded grid was normalised by rounding noise — fixed 2026-09-25 by a NEW
+GUARDED BRANCH (normalise by the maximum), proven byte-identical for every
+in-range centre against main's function (`scripts/dsg_outside_centre_identity.py`). Details of
+A03 in `docs/superpowers/plans/2026-09-22-a03-voigt-eta-identity.md`.
 
 ---
 
@@ -234,7 +245,7 @@ them to (use grep to find current line numbers — the file evolves):
 - `peakToBackendSpec` LACX branch
 - `applyBackendResult` LACX backend-param mapping
 - `runFit` JS LM free-params block + per-param clamps + linked-peak sync
-- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`)
+- `evalPeak` switch + grid-aware `laTrueCasaXPS_array` evaluator (called via `evalPeakArray`; DS+G's grid-aware twin is `dsgConvolved_array` — a convolved shape's scalar `evalPeak` branch ignores m and must have no caller, parity guard (C))
 - `_migrateLineshapeAliases` if backwards-compat alias needed
 
 ### UCl4 U 4f Asymmetric Broadening
diff --git a/docs/findings/2026-09-fit-determinacy.md b/docs/findings/2026-09-fit-determinacy.md
index dce89de..9844615 100644
--- a/docs/findings/2026-09-fit-determinacy.md
+++ b/docs/findings/2026-09-fit-determinacy.md
@@ -338,6 +338,20 @@ area is 23 % of the server's; at β = 2, m = 0.4 (the default m) 64 %. 0 of
 the 530 peak records in the seven committed projects use DS+G (and none of
 the 202 measurement targets), so no saved figure is affected; it is the
 fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
-recorded as its own unit. The general lesson repeats §6's: a harness that
+FIXED the same day in `fix-dsg-page-evaluator` after the owner asked whether
+Find Peaks emits DS+G: it does (every A- and M-family C 1s candidate's
+graphitic main line, β fixed at 0.05, α 0–0.3, m 0.4–1.8), and on that box
+the page's area was 5–21 % low for α 0.15–0.3. `dsgConvolved_array` mirrors
+the server's padded-grid convolution by the same FFT circular convolution:
+< 1e-6 of amplitude (measured ≤ 2e-14 at unit amplitude) across the whole
+β/m box on the base grid and seven other grids, and on the reviewers'
+reproducers (a centre outside the window, irregular grids, a 0.001 eV
+grid); two SERVER limits found on the way (plan §3a: kernel underflow for
+m ≤ 0.003 on an even padded length at 0.1 eV gives an all-zero curve;
+§3b: a centre far outside the padded grid was normalised by rounding
+noise — fixed 2026-09-25 by a guarded branch proven byte-identical for
+in-range centres); nothing changed in Find Peaks or the dropdown
+(a science decision is not altered to work around a rendering bug —
+owner, 2026-09-22). The general lesson repeats §6's: a harness that
 evaluates one representative point per shape proves nothing about the range
 the optimiser can reach.
def _request_seed(x, counts, background, shapes, prefixes, params, *, fit_kws, n_perturb) -> int:
    """The seed for every random draw of one fit: a pure function of the
    NUMBERS THE OPTIMISER IS HANDED — energies, counts and the computed
    background curve (little-endian float64), the lineshape of each component
    in fitting order, each lmfit parameter's effective role, the method,
    solver options and ``n_perturb``.

    A parameter's role is what it can do to the fit: a constrained one is its
    expression (its own start value and bounds are overridden), a fixed one
    is its value (its bounds cannot act), a free one is its value and bounds.
    Settings are hashed by their EFFECT, never as sent, so nothing the fit
    ignores can change the draws: a peak's name or colour, the
    ``fix_gl_ratio`` the page still sends for a Gaussian, stale shape
    parameters kept after a shape switch, the ``endpoint_avg`` a linear
    background does not use, anchor order, and the peaks' internal IDs —
    parameter names and constraint references are rewritten by component
    POSITION (``prefixes`` lists each component's lmfit prefix in fitting
    order), because the page never reuses an ID and the same model rebuilt
    after deleting a peak would otherwise fit differently. (Measured in review: each such
    no-op edit moved an area fraction by 15-45 percentage points while the
    request was hashed as sent.) It is a seed, not an identity: 32 bits
    collide, never use it as a cache key. Changing this derivation changes
    what saved projects regenerate: bump the version tag and say so.
    """
    kws = dict(fit_kws or {})
    solver = {k: v for k, v in dict(kws.pop("fit_kws", None) or {}).items() if k != "seed"}
    # longest prefix first so "p1_" cannot match inside "p11_"
    alias = sorted(((pre, f"c{k}_") for k, pre in enumerate(prefixes)), key=lambda a: -len(a[0]))

    def by_position(text):
        for pre, pos in alias:
            text = re.sub(r"(?<![A-Za-z0-9_])" + re.escape(pre), pos, text)
        return text

    roles = []
    for name, par in params.items():
        name = by_position(name)
        if par.expr is not None:
            roles.append([name, "expr", by_position(par.expr)])
        elif not par.vary:
            roles.append([name, "fixed", par.value])
        else:
            roles.append([name, "free", par.value, par.min, par.max])
    rest = _canonical({"shapes": list(shapes), "params": roles, "fit_kws": kws, "solver": solver,
                       "n_perturb": n_perturb})
    h = hashlib.sha256(b"xps-fit-seed-v1\0")
    for arr in (x, counts, background):
        a = np.ascontiguousarray(arr, dtype="<f8") + 0.0       # -0.0 -> 0.0 (the CSV path keeps "-0.00")
        h.update(str(a.size).encode() + b"\0" + a.tobytes())
    h.update(json.dumps(rest, sort_keys=True, separators=(",", ":"), allow_nan=True).encode())
    return int.from_bytes(h.digest()[:4], "little")            # 32 bits: what scipy's seed accepts
// Lineshape parity harness — the invariant that was missing until the
// 2026-08-30 asym-GL/LACX bug (see docs/autofit/codex/asym_gl_mismatch_*).
//
// Two DISTINCT invariants, both silently unchecked before this file:
//
//   (A) FRONTEND vs BACKEND: for every shape, the frontend's array evaluator
//       (evalPeakArray, called for chart data build paths) must numerically
//       match fitting.py's registered shape function (_SHAPE_FUNCS) over a
//       realistic BE grid and parameter sweep, including m>0 for the two
//       Gaussian-convolved shapes (DSG_LA, LACX). This is what asym-GL failed
//       — the frontend chart and the backend fit disagreed by ~10% of peak
//       height on real U 4f data.
//
//   (B) FRONTEND vs FRONTEND: the two JS evaluators for a single point,
//       evalPeak(x, p) and evalPeakArray(...)[i] at the same x, must agree
//       with each other. This is a SEPARATE bug class from (A) — even a
//       frontend that's perfectly correct vs. the backend can still disagree
//       with itself if it has two code paths computing "the same" curve.
//       This is exactly what the LACX per-point fallback did: evalPeak()
//       silently ignores Gaussian convolution (m) while evalPeakArray()
//       applies it correctly, so any evalPeak() caller — export/save/Results
//       panel — showed a materially different number than the chart.
//
// NOTE on (B)'s exact formulation: convolution is a GRID operation (it needs
// neighboring points to define a kernel), so it is not well-posed to ask for
// "the convolved value at an isolated point" via evalPeakArray([x], p)[0] —
// with only one point in the array, laTrueCasaXPS_array's own peak-finding +
// renormalization logic collapses to a degenerate constant (amplitude,
// trivially, for ANY x/alpha/beta) regardless of what evalPeak() does. That
// isn't a meaningful comparison for any shape, correct or not. Instead (B)
// asserts evalPeak(x, p) against evalPeakArray(realisticGrid, p)[indexOfX] —
// same real grid the chart/export code actually uses — which is the
// meaningful version of "do the two evaluators agree."

const { test } = require('node:test');
const assert = require('node:assert');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');

function extract(re, name) {
  const m = html.match(re);
  assert.ok(m, name + ' not found in templates/index.html');
  return m[0];
}

// ── Extract the shipped lineshape block (gaussian … evalPeakArray) ─────────
const evalCtx = eval('(function(){\n'
  + extract(/function gaussian\(x, center, fwhm\) \{[\s\S]*?\nfunction evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}/,
            'lineshape block') + '\n'
  + 'return { evalPeak, evalPeakArray };\n})()');
const { evalPeak, evalPeakArray } = evalCtx;

// ── Python bridge: call fitting.py's OWN _SHAPE_FUNCS, never a reimpl ──────
// A git-worktree checkout does NOT get its own venv/ (confirmed 2026-07-11,
// see memory xps-autofit-session-ops) — the venv only exists in the main
// repo checkout, so a worktree run must fall back to that absolute path.
function findPython() {
  const candidates = [
    process.env.XPS_PYTHON,
    path.join(REPO_ROOT, 'venv/bin/python3'),          // main checkout's own venv
    '/Users/skyefortier/xps-app/venv/bin/python3',      // worktree -> main repo venv
    'python3',
  ].filter(Boolean);
  for (const c of candidates) {
    try {
      if (c === 'python3' || fs.existsSync(c)) return c;
    } catch { /* keep looking */ }
  }
  return 'python3';
}
const PYTHON = findPython();
const BRIDGE = path.join(__dirname, 'lineshape_parity_backend.py');

function backendEval(shape, params, x) {
  const input = JSON.stringify({ shape, params, x });
  const out = execFileSync(PYTHON, [BRIDGE], { input, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
  return JSON.parse(out);
}

// ── Realistic BE grid: 10 eV window, 0.05 eV step (200 pts) around center ──
function grid(center) {
  const x = [];
  for (let i = 0; i < 200; i++) x.push(center - 5.0 + 0.05 * i);
  return x;
}

function maxRelDiff(a, b, amplitude) {
  let m = 0;
  for (let i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i]));
  return m / amplitude;
}

// ── One representative peak per shape (distinctive, non-default values) ───
const AMPLITUDE = 17794.0;
const CENTER = 391.8;
const FWHM = 1.83;

function basePeak(shape) {
  return {
    id: 1, name: 'P', color: '#000', center: CENTER, amplitude: AMPLITUDE, fwhm: FWHM,
    shape,
    glMix: 55, asymmetry: 0.59,
    dsAlpha: 0.22, dsGamma: 0.05,
    laAlpha: 0.18, laBeta: 0.7, laM: 0.9,
    caAlpha: 1.4, caBeta: 0.8, caM: 50,
    linked: null, isChargeReference: false, visible: true,
  };
}

// backend shape id + kwargs builder per frontend shape
const BACKEND = {
  'Gaussian':   p => ({ shape: 'gaussian',       params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm } }),
  'Lorentzian': p => ({ shape: 'lorentzian',      params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm } }),
  'Voigt':      p => ({ shape: 'pseudo_voigt_gl', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, gl_ratio: 0.5 } }),
  'GL':         p => ({ shape: 'pseudo_voigt_gl', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, gl_ratio: p.glMix / 100 } }),
  'asym-GL':    p => ({ shape: 'asymmetric_gl',   params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, asymmetry: p.asymmetry, gl_ratio: p.glMix / 100 } }),
  'DS':         p => ({ shape: 'doniach_sunjic',  params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.dsAlpha, gamma_asym: p.dsGamma } }),
  'DSG_LA':     p => ({ shape: 'ds_g',            params: { amplitude: p.amplitude, center: p.center, alpha: p.laAlpha, beta: p.laBeta, m_gauss: p.laM } }),
  'LACX':       p => ({ shape: 'la_casaxps',      params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.caAlpha, beta: p.caBeta, m: p.caM } }),
};

const TIGHT_TOL = 1e-6; // relative to amplitude; both sides are closed-form double-precision math

// ── (A) Frontend vs backend, shapes that must match tightly ───────────────
// Gaussian/Lorentzian/GL/Voigt/DS: no convolution, identical formulas on
// both sides — proven to agree by the earlier Codex sweep. asym-GL: fixed
// by unit-1 commit 1 (frontend rewritten to the backend's piecewise
// two-constant-width formula) — this assertion is what proves that fix.
for (const shape of ['Gaussian', 'Lorentzian', 'GL', 'Voigt', 'DS', 'asym-GL']) {
  test(`(A) frontend vs backend parity: ${shape}`, () => {
    const p = basePeak(shape);
    const x = grid(p.center);
    const jsY = evalPeakArray(x, p);
    const { shape: beShape, params } = BACKEND[shape](p);
    const beY = backendEval(beShape, params, x);
    const rel = maxRelDiff(jsY, beY, p.amplitude);
/Users/skyefortier/xps-app/venv
autofit/parity.py:30:    _SHAPE_FUNCS,
autofit/parity.py:42:def evaluate_peak(be: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
autofit/parity.py:44:    f = _SHAPE_FUNCS[spec["shape"]]
autofit/parity.py:54:    if s == "ds_g":
autofit/parity.py:65:        total = total + evaluate_peak(be, s)
autofit/engine.py:14:  ``LA_ASYMMETRIC`` (α, β=Lorentzian-HWHM, m_gauss) is main's ``ds_g``; the
autofit/engine.py:42:from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background
autofit/engine.py:327:        if shape_name not in _SHAPE_FUNCS:
autofit/engine.py:329:                f"Shape {shape_name!r} not registered in fitting._SHAPE_FUNCS"
autofit/engine.py:331:        sub = Model(_SHAPE_FUNCS[shape_name], prefix=_slot_prefix(slot.role))

codex
The server diff adds a strict outside-grid guard and leaves the old normalization intact in `else`. I’m checking the exact padded edges and tiny-kernel cases next, where FFT rounding could still affect page/server parity.

exec
/bin/zsh -lc "nl -ba docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md | sed -n '85,155p'; sed -n '1,100p' tests/js/lineshape_parity_backend.py; rg -n 'battery|pytest' tests/autofit/test_c1s_parity_battery.py tests/autofit/test_u4f_parity_battery.py; git log -3 --oneline" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
    85	has a sample at the centre and the kernel collapses to a delta instead. On
    86	a 120-point 0.1 eV grid the zone is 0.001 ≤ m ≤ 0.003 (m = 0.00305 is
    87	already a normal curve); on 121 points there is none. A fit will not settle there (a zero curve fits
    88	nothing), but a LOCKED m in that zone is fitted as zero. The page mirrors
    89	it exactly (a vanished curve drawn as vanished, never a curve the server
    90	did not fit). Recorded for the owner; the fix belongs to the server (a
    91	kernel that collapses to a delta below the grid's resolution, as the
    92	threshold branch does).
    93	
    94	### 3b. Server limit found in round 2 — FIXED by a guarded branch (2026-09-25, owner's option 2)
    95	
    96	The server normalises the convolved curve by its value interpolated AT THE
    97	CENTRE, falling back to the curve's maximum only when that value is ≤ 0.
    98	With the centre far OUTSIDE the padded grid (e.g. 10 eV outside a
    99	[−5, 5] window at β 0.05, m 0.05, or 15 eV outside on the low-BE side)
   100	the interpolated value is the clamped end value of a tail of order 1e-20 —
   101	rounding noise whose SIGN decides which of two unrelated curves the server
   102	returns: the max-normalised tail (sign negative) or that tail divided by
   103	~1e-20 (sign positive). The page mirrors the rule and the arithmetic, but
   104	not the rounding sign of a 1e-20 number, and Codex round 2 reproduced a
   105	case where the two sides fall on different branches (server maximum 1,
   106	page 5e16). No committed model is near this regime (a component centred
   107	outside its own window has no physical reading, and a fit does not settle
   108	there), and the server's own output there is arbitrary.
   109	
   110	Owner's condition (2026-09-25): a NEW GUARDED BRANCH, not a modification
   111	of the existing normalisation, PROVEN byte-identical for every centre
   112	inside the padded grid — otherwise stop and take option 1. Done:
   113	`_ds_g_dscore_gauss` now has `if center < x_padded[0] or center >
   114	x_padded[-1]: peak_val = max|result|` with the pre-existing code in the
   115	`else`. Proof (`scripts/dsg_outside_centre_identity.py`, main's function
   116	loaded from `git show main:fitting.py` beside the new one, output in
   117	`docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt`):
   118	3,780 box × grid × centre cases (centres at the window centre, off-grid,
   119	at each data edge and 1e-9 inside each padded edge) and 2,000 random
   120	draws with the centre inside the padded grid — 5,780 of 5,780
   121	`np.array_equal`; `run_fit` on the committed UCl4-graphite C1s Scan with
   122	its Graphite line as DS+G (n_perturb 0 and 3, Levenberg-Marquardt, the
   123	byte-identical method): the whole JSON response identical; the committed
   124	batteries hold no DS+G component and pass unchanged. The two outside
   125	cases: old maximum 5.4e4 and 2.6e3 × amplitude, new 1. The page mirrors
   126	the branch (`dsgConvolved_array`); both reproducers are hard regressions
   127	in (D″), plus a centre just outside and just inside the padded edge.
   128	
   129	Nothing changed on the server, in `autofit/`, in Find Peaks or in the
   130	dropdown. Python suite untouched by this unit (no Python change); JS suite
   131	and browser check in §5.
   132	
   133	## 4. Sites
   134	
   135	`laCasaXPS` (rewritten), `dsgConvolved_array` (new), `evalPeakArray`;
   136	every function-extractor list that names the lineshape block
   137	(`tests/js/lineshape_roundtrip.test.js`, `local_lm_descent.test.js`,
   138	`scripts/local_server_gap.js`, `scripts/voigt_saved_vs_refit.js`) now lists
   139	`dsgConvolved_array`; `tests/js/lineshape_parity.test.js` (A), (B), (D),
   140	(D′); `tests/js/lineshape_roundtrip.test.js`; CLAUDE.md; findings §7.
   141	
   142	## 5. Verification
   143	
   144	- JS suite: 392 tests, 387 pass, 0 fail, 5 todo (`node --test tests/js/*.test.js`).
   145	  The five: LACX m > 0 in (A), (B) and (D); (B) DS+G (scalar evaluator
   146	  ignores m, by design); the LACX round trip.
   147	- Python suite: untouched by this unit (no Python change); the A03 run on
   148	  the same server code was 989 passed / 7 skipped.
   149	- Browser check (`browser_check_dsg.py`, dev gunicorn :5151 with the
   150	  production `--timeout 300`): the committed UCl4-graphite C1s Scan with its
   151	  Graphite line switched to DS+G at Find Peaks' parameters (β 0.05, α 0.2,
   152	  m 0.8), Run Fit (fitted α 0, β 0.053, m 0.62): the curve the page draws
   153	  for it equals the server's fitted curve to 1.2e-12 of amplitude (the five
   154	  GL lines 1e-13); its Results area equals the server curve's to 0.0000 %;
   155	  the chart dataset is the drawn curve; a `ds_g` Find Peaks candidate maps
#!/usr/bin/env python3
"""Backend-shape evaluator bridge for tests/js/lineshape_parity.test.js.

Reads a JSON spec from stdin:
    {"shape": "<key in fitting._SHAPE_FUNCS>", "params": {...}, "x": [...]}
or a JSON list of such specs.
Writes a JSON array of y-values (or a list of arrays) to stdout.

Calls fitting.py's OWN registered shape functions (_SHAPE_FUNCS) directly —
never a reimplementation — so the JS parity test is always comparing against
whatever the backend actually ships, with no fixture staleness risk.
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from fitting import _SHAPE_FUNCS  # noqa: E402


def _eval(spec: dict) -> list[float]:
    x = np.array(spec["x"], dtype=float)
    fn = _SHAPE_FUNCS[spec["shape"]]
    return [float(v) for v in fn(x, **spec["params"])]


def main() -> None:
    spec = json.load(sys.stdin)
    # A list of specs (the A03 parameter sweep) is answered with a list of
    # curves in one interpreter start; a single spec as before.
    if isinstance(spec, list):
        json.dump([_eval(s) for s in spec], sys.stdout)
    else:
        json.dump(_eval(spec), sys.stdout)


if __name__ == "__main__":
    main()
tests/autofit/test_u4f_parity_battery.py:2:U 4f characterization battery — pins the MANUAL fit path's LACX + linked
tests/autofit/test_u4f_parity_battery.py:4:fits (structure mirrors test_c1s_parity_battery.py; shared logic in
tests/autofit/test_u4f_parity_battery.py:5:battery_common.py).
tests/autofit/test_u4f_parity_battery.py:8:    venv/bin/python scripts/gen_u4f_battery_fixture.py
tests/autofit/test_u4f_parity_battery.py:17:against a refit FROM the refit (battery_common, stationarity="refit"): the
tests/autofit/test_u4f_parity_battery.py:21:import pytest
tests/autofit/test_u4f_parity_battery.py:23:import battery_common as bc
tests/autofit/test_u4f_parity_battery.py:26:FIXTURE = "u4f_battery_expected.json"
tests/autofit/test_u4f_parity_battery.py:48:_FITS = bc.battery_fits(REGION)
tests/autofit/test_u4f_parity_battery.py:53:def test_battery_roster():
tests/autofit/test_u4f_parity_battery.py:55:                     "scripts/gen_u4f_battery_fixture.py")
tests/autofit/test_u4f_parity_battery.py:58:@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
tests/autofit/test_u4f_parity_battery.py:63:@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
tests/autofit/test_c1s_parity_battery.py:2:C 1s characterization battery — the Stage-2 parity / regression safety net.
tests/autofit/test_c1s_parity_battery.py:7:fixtures/c1s_battery_expected.json pin today's ``fitting.run_fit`` numerics
tests/autofit/test_c1s_parity_battery.py:19:3. ``test_battery_fixture_*`` — the same refit reproduces the frozen
tests/autofit/test_c1s_parity_battery.py:22:   numerics changes: ``venv/bin/python scripts/gen_c1s_battery_fixture.py``.
tests/autofit/test_c1s_parity_battery.py:26:excluded by the same rules the generator applies, so fixture and battery
tests/autofit/test_c1s_parity_battery.py:35:import pytest
tests/autofit/test_c1s_parity_battery.py:37:from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
tests/autofit/test_c1s_parity_battery.py:42:FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "c1s_battery_expected.json")
tests/autofit/test_c1s_parity_battery.py:52:def _battery_fits():
tests/autofit/test_c1s_parity_battery.py:56:            if battery_eligible(rf, region="C 1s")[0]:
tests/autofit/test_c1s_parity_battery.py:61:_FITS = _battery_fits()
tests/autofit/test_c1s_parity_battery.py:69:def test_battery_roster():
tests/autofit/test_c1s_parity_battery.py:71:        f"C 1s battery shrank to {len(_FITS)} fits (< {MIN_BATTERY_SIZE}) — "
tests/autofit/test_c1s_parity_battery.py:75:    assert len(projects) >= 3, f"battery covers only {projects}"
tests/autofit/test_c1s_parity_battery.py:78:        "battery roster no longer matches the frozen fixture — regenerate "
tests/autofit/test_c1s_parity_battery.py:79:        "scripts/gen_c1s_battery_fixture.py only if this change is intentional"
tests/autofit/test_c1s_parity_battery.py:83:@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
tests/autofit/test_c1s_parity_battery.py:92:@pytest.mark.parametrize("rf", _FITS, ids=_IDS)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cvjAfL01' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3ingR6EW' (errno=Operation not permitted)
ce9fb66 fix(DS+G): a centre outside the padded grid is normalised by the curve's maximum - a NEW GUARDED BRANCH on the server, proven byte-identical for every in-range centre; mirrored on the page
b02278d docs(DS+G): Codex round 2 (NO-GO x2) - stopped per the owner's rule; the remaining MAJOR is a server normalisation-conditioning limit (plan §3b); precision and underflow-zone figures corrected
591a649 fix(DS+G): Codex round 1 (NO-GO x2) - the server's circular convolution by FFT (wrapped contributions included, O(n log n)); irregular grids, an outside centre, 1- and 2-point grids and the server's kernel-underflow zone pinned

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/*.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -m pytest -q -p no:cacheprovider tests/test_dsg_outside_centre.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 exited 1 in 301ms:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pytest/__main__.py", line 9, in <module>
    raise SystemExit(pytest.console_main())
                     ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -m pytest -q -s -p no:cacheprovider tests/test_dsg_outside_centre.py tests/autofit/test_c1s_parity_battery.py tests/autofit/test_u4f_parity_battery.py' in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 exited 2 in 2340ms:

==================================== ERRORS ====================================
______________ ERROR collecting tests/test_dsg_outside_centre.py _______________
tests/test_dsg_outside_centre.py:14: in <module>
    import fitting
fitting.py:33: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
__________ ERROR collecting tests/autofit/test_c1s_parity_battery.py ___________
tests/autofit/test_c1s_parity_battery.py:37: in <module>
    from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
autofit/parity.py:29: in <module>
    from fitting import (
fitting.py:33: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
__________ ERROR collecting tests/autofit/test_u4f_parity_battery.py ___________
tests/autofit/test_u4f_parity_battery.py:23: in <module>
    import battery_common as bc
tests/autofit/battery_common.py:16: in <module>
    from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
autofit/parity.py:29: in <module>
    from fitting import (
fitting.py:33: in <module>
    from lmfit import Model, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/__init__.py:38: in <module>
    from .confidence import conf_interval, conf_interval2d
../../../venv/lib/python3.12/site-packages/lmfit/confidence.py:10: in <module>
    from .minimizer import MinimizerException
../../../venv/lib/python3.12/site-packages/lmfit/minimizer.py:41: in <module>
    from .parameter import Parameter, Parameters
../../../venv/lib/python3.12/site-packages/lmfit/parameter.py:14: in <module>
    from .jsonutils import decode4js, encode4js
../../../venv/lib/python3.12/site-packages/lmfit/jsonutils.py:8: in <module>
    import dill
../../../venv/lib/python3.12/site-packages/dill/__init__.py:33: in <module>
    from .session import (
../../../venv/lib/python3.12/site-packages/dill/session.py:25: in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:315: in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:308: in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py:223: in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
E   FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
=========================== short test summary info ============================
ERROR tests/test_dsg_outside_centre.py - FileNotFoundError: [Errno 2] No usab...
ERROR tests/autofit/test_c1s_parity_battery.py - FileNotFoundError: [Errno 2]...
ERROR tests/autofit/test_u4f_parity_battery.py - FileNotFoundError: [Errno 2]...
!!!!!!!!!!!!!!!!!!! Interrupted: 3 errors during collection !!!!!!!!!!!!!!!!!!!!
3 errors in 1.98s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();
const specs=[];
for(const n of [1,21,121,200,201]) for(const step0 of [.05,.1,.5]) for(const b of [.05,.7]) for(const m of [.001,.05,.4]) {
 const x=Array.from({length:n},(_,i)=>n===1?0:-5+step0*i);
 const d=x.slice(1).map((v,i)=>Math.abs(v-x[i])).sort((a,b)=>a-b), j=d.length>>1;
 const step=n===1?.05:(d.length%2?d[j]:(d[j-1]+d[j])/2), pad=Math.max(1,Math.ceil(Math.max(10*m,20*b)/step));
 for(const side of [-1,1]) for(const delta of [0,1e-9,.000001]) {
 const edge=side<0?x[0]-pad*step:x[n-1]+pad*step, c=edge-side*delta;
 specs.push({shape:'\\''ds_g'\\'',x,params:{amplitude:1,center:c,alpha:.49,beta:b,m_gauss:m},meta:{n,step0,b,m,side,delta,edge}});
 }
}
const out=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''tests/js/lineshape_parity_backend.py'\\''],{input:JSON.stringify(specs),encoding:'\\''utf8'\\'',maxBuffer:64*1024*1024}));
const results=specs.map((s,i)=>{const p=s.params; const js=ev(s.x,{shape:'\\''DSG_LA'\\'',amplitude:1,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss}); return {meta:s.meta,center:p.center,err:Math.max(...js.map((v,j)=>Math.abs(v-out[i][j]))),jsMax:Math.max(...js.map(Math.abs)),pyMax:Math.max(...out[i].map(Math.abs))};}).sort((a,b)=>b.err-a.err);
console.log(JSON.stringify({total:results.length,failures:results.filter(r=>r.err>1e-6).length,worst:results.slice(0,12)},null,2));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 exited 1 in 1314ms:
Traceback (most recent call last):
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
    from fitting import _SHAPE_FUNCS  # noqa: E402
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
    from lmfit import Model, Parameters
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
    from .confidence import conf_interval, conf_interval2d
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
    from .minimizer import MinimizerException
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
    from .parameter import Parameter, Parameters
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
    from .jsonutils import decode4js, encode4js
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
    import dill
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
    from .session import (
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
<ref *1> node:child_process:955
    throw err;
    ^

Error: spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE
    at Object.spawnSync (node:internal/child_process:1120:20)
    at spawnSync (node:child_process:902:24)
    at Object.execFileSync (node:child_process:945:15)
    at [eval]:16:25
    at runScriptInThisContext (node:internal/vm:209:10)
    at node:internal/process/execution:446:12
    at [eval]-wrapper:6:24
    at runScriptInContext (node:internal/process/execution:444:60)
    at evalFunction (node:internal/process/execution:279:30)
    at evalTypeScript (node:internal/process/execution:291:3) {
  errno: -32,
  code: 'EPIPE',
  syscall: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3',
  path: '/Users/skyefortier/xps-app/venv/bin/python3',
  spawnargs: [ 'tests/js/lineshape_parity_backend.py' ],
  error: [Circular *1],
  status: 1,
  signal: null,
  output: [
    null,
    '',
    'Traceback (most recent call last):\n' +
      '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>\n' +
      '    from fitting import _SHAPE_FUNCS  # noqa: E402\n' +
      '    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n' +
      '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>\n' +
      '    from lmfit import Model, Parameters\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\n' +
      '    from .confidence import conf_interval, conf_interval2d\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\n' +
      '    from .minimizer import MinimizerException\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\n' +
      '    from .parameter import Parameter, Parameters\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\n' +
      '    from .jsonutils import decode4js, encode4js\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\n' +
      '    import dill\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\n' +
      '    from .session import (\n' +
      '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\n' +
      '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\n' +
      '                               ^^^^^^^^^^^^^^^^^^^^^\n' +
      '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\n' +
      '    return _os.fsdecode(_gettempdir())\n' +
      '                        ^^^^^^^^^^^^^\n' +
      '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\n' +
      '    tempdir = _get_default_tempdir()\n' +
      '              ^^^^^^^^^^^^^^^^^^^^^^\n' +
      '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\n' +
      '    raise FileNotFoundError(_errno.ENOENT,\n' +
      "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']\n"
  ],
  pid: 1780,
  stdout: '',
  stderr: 'Traceback (most recent call last):\n' +
    '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>\n' +
    '    from fitting import _SHAPE_FUNCS  # noqa: E402\n' +
    '    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n' +
    '  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>\n' +
    '    from lmfit import Model, Parameters\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>\n' +
    '    from .confidence import conf_interval, conf_interval2d\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>\n' +
    '    from .minimizer import MinimizerException\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>\n' +
    '    from .parameter import Parameter, Parameters\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>\n' +
    '    from .jsonutils import decode4js, encode4js\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>\n' +
    '    import dill\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>\n' +
    '    from .session import (\n' +
    '  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>\n' +
    '    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())\n' +
    '                               ^^^^^^^^^^^^^^^^^^^^^\n' +
    '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir\n' +
    '    return _os.fsdecode(_gettempdir())\n' +
    '                        ^^^^^^^^^^^^^\n' +
    '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir\n' +
    '    tempdir = _get_default_tempdir()\n' +
    '              ^^^^^^^^^^^^^^^^^^^^^^\n' +
    '  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir\n' +
    '    raise FileNotFoundError(_errno.ENOENT,\n' +
    "FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']\n"
}

Node.js v22.22.2

 exited 1 in 64933ms:
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 10.301903
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block
ok 2 - a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block
  ---
  duration_ms: 15.702006
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 1.687816
  type: 'test'
  ...
# Subtest: the fixture set covers both outcomes
ok 4 - the fixture set covers both outcomes
  ---
  duration_ms: 1.94909
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
ok 5 - anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
  ---
  duration_ms: 6.817404
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
ok 6 - anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
  ---
  duration_ms: 3.875102
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
ok 7 - anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
  ---
  duration_ms: 3.741336
  type: 'test'
  ...
# Subtest: anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
ok 8 - anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
  ---
  duration_ms: 2.528898
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
ok 9 - anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
  ---
  duration_ms: 2.647086
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
ok 10 - anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
  ---
  duration_ms: 1.789934
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
ok 11 - anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
  ---
  duration_ms: 1.751425
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
ok 12 - anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
  ---
  duration_ms: 2.166549
  type: 'test'
  ...
# Subtest: anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
ok 13 - anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
  ---
  duration_ms: 2.247132
  type: 'test'
  ...
# Subtest: an anchor amplitude of 0 is refused before anything is computed
ok 14 - an anchor amplitude of 0 is refused before anything is computed
  ---
  duration_ms: 1.999287
  type: 'test'
  ...
# Subtest: an anchor amplitude of -5 is refused before anything is computed
ok 15 - an anchor amplitude of -5 is refused before anything is computed
  ---
  duration_ms: 1.53191
  type: 'test'
  ...
# Subtest: an anchor amplitude of NaN is refused before anything is computed
ok 16 - an anchor amplitude of NaN is refused before anything is computed
  ---
  duration_ms: 1.584837
  type: 'test'
  ...
# Subtest: an anchor amplitude of Infinity is refused before anything is computed
ok 17 - an anchor amplitude of Infinity is refused before anything is computed
  ---
  duration_ms: 1.528451
  type: 'test'
  ...
# Subtest: a response that lacks the fitted data or the component curve cannot vouch for an anchor
ok 18 - a response that lacks the fitted data or the component curve cannot vouch for an anchor
  ---
  duration_ms: 4.970197
  type: 'test'
  ...
# Subtest: an exact fit that needs the component is supported (chi-square with it is zero)
ok 19 - an exact fit that needs the component is supported (chi-square with it is zero)
  ---
  duration_ms: 1.849124
  type: 'test'
  ...
# Subtest: removing a component that costs nothing is the definition of unsupported
ok 20 - removing a component that costs nothing is the definition of unsupported
  ---
  duration_ms: 1.688709
  type: 'test'
  ...
# Subtest: the support check precedes every write of the charge-correction inputs
ok 21 - the support check precedes every write of the charge-correction inputs
  ---
  duration_ms: 0.751492
  type: 'test'
  ...
# Subtest: the fallback "first peak" anchor is held to the same rule
ok 22 - the fallback "first peak" anchor is held to the same rule
  ---
  duration_ms: 1.617939
  type: 'test'
  ...
# Subtest: rolling back to a Custom reference shows its target field again
ok 23 - rolling back to a Custom reference shows its target field again
  ---
  duration_ms: 1.28221
  type: 'test'
  ...
# Subtest: source ROI overwrites a different target ROI during propagation
ok 24 - source ROI overwrites a different target ROI during propagation
  ---
  duration_ms: 1.570431
  type: 'test'
  ...
# Subtest: blank source ROI leaves the target ROI unchanged (never wipes it)
ok 25 - blank source ROI leaves the target ROI unchanged (never wipes it)
  ---
  duration_ms: 0.356396
  type: 'test'
  ...
# Subtest: a blank source ROI bound (one side) falls back per-field
ok 26 - a blank source ROI bound (one side) falls back per-field
  ---
  duration_ms: 0.249344
  type: 'test'
  ...
# Subtest: background fields still propagate from source (no regression)
ok 27 - background fields still propagate from source (no regression)
  ---
  duration_ms: 0.252333
  type: 'test'
  ...
# Subtest: blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
ok 28 - blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
  ---
  duration_ms: 0.362034
  type: 'test'
  ...
# Subtest: unrelated target UI fields are preserved untouched
ok 29 - unrelated target UI fields are preserved untouched
  ---
  duration_ms: 1.334365
  type: 'test'
  ...
# Subtest: legacy source without endpointAvg propagates 1, not the target default
ok 30 - legacy source without endpointAvg propagates 1, not the target default
  ---
  duration_ms: 2.024895
  type: 'test'
  ...
# Subtest: window at the ROI bounds covers every point, including the last one
ok 31 - window at the ROI bounds covers every point, including the last one
  ---
  duration_ms: 3.362888
  type: 'test'
  ...
# Subtest: off-grid bound inside the ROI never pulls in a point outside it
ok 32 - off-grid bound inside the ROI never pulls in a point outside it
  ---
  duration_ms: 0.375107
  type: 'test'
  ...
# Subtest: bound order does not matter
ok 33 - bound order does not matter
  ---
  duration_ms: 1.698574
  type: 'test'
  ...
# Subtest: ascending grid gives the same point set as descending
ok 34 - ascending grid gives the same point set as descending
  ---
  duration_ms: 0.337274
  type: 'test'
  ...
# Subtest: blank or NaN bound falls back to the full range
ok 35 - blank or NaN bound falls back to the full range
  ---
  duration_ms: 0.358964
  type: 'test'
  ...
# Subtest: fewer than two points in range falls back to the full range
ok 36 - fewer than two points in range falls back to the full range
  ---
  duration_ms: 0.364522
  type: 'test'
  ...
# Subtest: exactly two points in range is a usable window
ok 37 - exactly two points in range is a usable window
  ---
  duration_ms: 0.373776
  type: 'test'
  ...
# Subtest: computeBackgroundCore uses exactly the helper window
ok 38 - computeBackgroundCore uses exactly the helper window
  ---
  duration_ms: 1.459424
  type: 'test'
  ...
# Subtest: no request builder uses the old nearest-index idiom for the bg window
ok 39 - no request builder uses the old nearest-index idiom for the bg window
  ---
  duration_ms: 1.163004
  type: 'test'
  ...
# Subtest: both /api/fit request builders send the inclusive window as end_idx = i1 + 1
ok 40 - both /api/fit request builders send the inclusive window as end_idx = i1 + 1
  ---
  duration_ms: 2.128196
  type: 'test'
  ...
# Subtest: new tabs default to endpoint averaging 3, via one constant
ok 41 - new tabs default to endpoint averaging 3, via one constant
  ---
  duration_ms: 3.320929
  type: 'test'
  ...
# Subtest: legacy fallbacks resolve a saved ui without endpointAvg to 1
ok 42 - legacy fallbacks resolve a saved ui without endpointAvg to 1
  ---
  duration_ms: 2.795882
  type: 'test'
  ...
# Subtest: no bare endpointAvg || '1' fallback survives outside the constant
ok 43 - no bare endpointAvg || '1' fallback survives outside the constant
  ---
  duration_ms: 3.027778
  type: 'test'
  ...
# Subtest: Find Peaks records the averaging its engine used and applies it on apply
ok 44 - Find Peaks records the averaging its engine used and applies it on apply
  ---
  duration_ms: 2.035111
  type: 'test'
  ...
# Subtest: undo/redo carry the averaging recorded by the Find Peaks apply action
ok 45 - undo/redo carry the averaging recorded by the Find Peaks apply action
  ---
  duration_ms: 0.894565
  type: 'test'
  ...
# Subtest: averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
ok 46 - averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
  ---
  duration_ms: 0.558299
  type: 'test'
  ...
# Subtest: FP_TIER_META defines all three tiers with a color and short label
ok 47 - FP_TIER_META defines all three tiers with a color and short label
  ---
  duration_ms: 1.85367
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: empty query matches everything
ok 48 - _fpRegionMatchesFilter: empty query matches everything
  ---
  duration_ms: 0.508517
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by symbol (case-insensitive, prefix)
ok 49 - _fpRegionMatchesFilter: matches by symbol (case-insensitive, prefix)
  ---
  duration_ms: 0.395576
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by element name substring
ok 50 - _fpRegionMatchesFilter: matches by element name substring
  ---
  duration_ms: 1.878033
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by level/subshell
ok 51 - _fpRegionMatchesFilter: matches by level/subshell
  ---
  duration_ms: 0.742808
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches the full region label
ok 52 - _fpRegionMatchesFilter: matches the full region label
  ---
  duration_ms: 0.237992
  type: 'test'
  ...
# Subtest: _fpRegionOptionLabel: includes the tier tag, region, and element name
ok 53 - _fpRegionOptionLabel: includes the tier tag, region, and element name
  ---
  duration_ms: 0.561877
  type: 'test'
  ...
# Subtest: _fpRegionOptionLabel: structure_only region is tagged distinctly from curated
ok 54 - _fpRegionOptionLabel: structure_only region is tagged distinctly from curated
  ---
  duration_ms: 0.337416
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: no query returns everything, sorted stably by input order
ok 55 - _fpBuildRegionOptions: no query returns everything, sorted stably by input order
  ---
  duration_ms: 1.594666
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: filters by query, each option carries its tier
ok 56 - _fpBuildRegionOptions: filters by query, each option carries its tier
  ---
  duration_ms: 0.74616
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: an unmatched query yields an empty list (never throws)
ok 57 - _fpBuildRegionOptions: an unmatched query yields an empty list (never throws)
  ---
  duration_ms: 0.303335
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: tolerates a missing/empty coverage array
ok 58 - _fpBuildRegionOptions: tolerates a missing/empty coverage array
  ---
  duration_ms: 0.19182
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: single curated selection shows its own note
ok 59 - _fpTierNoteFor: single curated selection shows its own note
  ---
  duration_ms: 0.24263
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: single fallback (machine) selection is honestly labeled
ok 60 - _fpTierNoteFor: single fallback (machine) selection is honestly labeled
  ---
  duration_ms: 0.22517
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: structure_only selection says no reference position
ok 61 - _fpTierNoteFor: structure_only selection says no reference position
  ---
  duration_ms: 0.156023
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: no selection is an empty string (never throws)
ok 62 - _fpTierNoteFor: no selection is an empty string (never throws)
  ---
  duration_ms: 0.145287
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: multi-region selection lists each region+tier
ok 63 - _fpTierNoteFor: multi-region selection lists each region+tier
  ---
  duration_ms: 0.192389
  type: 'test'
  ...
# Subtest: runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
ok 64 - runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
  ---
  duration_ms: 1.892993
  type: 'test'
  ...
# Subtest: _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
ok 65 - _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
  ---
  duration_ms: 0.590313
  type: 'test'
  ...
# Subtest: _fpBestTier: curated wins over machine and structure_only
ok 66 - _fpBestTier: curated wins over machine and structure_only
  ---
  duration_ms: 7.66402
  type: 'test'
  ...
# Subtest: _fpBestTier: machine wins over structure_only when no curated present
ok 67 - _fpBestTier: machine wins over structure_only when no curated present
  ---
  duration_ms: 0.313514
  type: 'test'
  ...
# Subtest: _fpBestTier: empty entries -> null (an element with zero practical coverage)
ok 68 - _fpBestTier: empty entries -> null (an element with zero practical coverage)
  ---
  duration_ms: 0.191355
  type: 'test'
  ...
# Subtest: FP_TIER_RANK: strictly orders curated > machine > structure_only
ok 69 - FP_TIER_RANK: strictly orders curated > machine > structure_only
  ---
  duration_ms: 0.205046
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click on a fresh region replaces an existing single selection
ok 70 - _fpNextSelection: plain click on a fresh region replaces an existing single selection
  ---
  duration_ms: 1.746125
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click replaces a multi-region selection with just the clicked one
ok 71 - _fpNextSelection: plain click replaces a multi-region selection with just the clicked one
  ---
  duration_ms: 2.318266
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click on the ONLY already-selected region is a no-op (stays selected)
ok 72 - _fpNextSelection: plain click on the ONLY already-selected region is a no-op (stays selected)
  ---
  duration_ms: 0.471169
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click ADDS a second region (ctrl-click co-fit)
ok 73 - _fpNextSelection: additive click ADDS a second region (ctrl-click co-fit)
  ---
  duration_ms: 0.366969
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click on an already-selected region REMOVES it
ok 74 - _fpNextSelection: additive click on an already-selected region REMOVES it
  ---
  duration_ms: 0.563032
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click on the last remaining region empties the selection
ok 75 - _fpNextSelection: additive click on the last remaining region empties the selection
  ---
  duration_ms: 0.740186
  type: 'test'
  ...
# Subtest: _fpNextSelection: never mutates the `current` Set passed in
ok 76 - _fpNextSelection: never mutates the `current` Set passed in
  ---
  duration_ms: 0.344749
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: translates role:param@max with no raw identifiers
ok 77 - _fpBoundaryHitLabel: translates role:param@max with no raw identifiers
  ---
  duration_ms: 5.425501
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: @min reads as lower limit
ok 78 - _fpBoundaryHitLabel: @min reads as lower limit
  ---
  duration_ms: 0.478257
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: unparseable input degrades honestly, never throws
ok 79 - _fpBoundaryHitLabel: unparseable input degrades honestly, never throws
  ---
  duration_ms: 0.223691
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: detection-family "absorbing a neighbor" variant
ok 80 - _fpWidthFlagLabel: detection-family "absorbing a neighbor" variant
  ---
  duration_ms: 0.520002
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: ordinary-cap "no known-broad justification" variant reads distinctly
ok 81 - _fpWidthFlagLabel: ordinary-cap "no known-broad justification" variant reads distinctly
  ---
  duration_ms: 0.340602
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: DS+G and asym-GL variants still extract role + width cleanly
ok 82 - _fpWidthFlagLabel: DS+G and asym-GL variants still extract role + width cleanly
  ---
  duration_ms: 0.239986
  type: 'test'
  ...
# Subtest: _fpPlainMessage: structural_only stub (no cited or sourced data)
ok 83 - _fpPlainMessage: structural_only stub (no cited or sourced data)
  ---
  duration_ms: 0.645651
  type: 'test'
  ...
# Subtest: _fpPlainMessage: an EMPTY structural_only array must NOT trigger the stub (Codex-caught)
ok 84 - _fpPlainMessage: an EMPTY structural_only array must NOT trigger the stub (Codex-caught)
  ---
  duration_ms: 0.295507
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a MIXED request that succeeded must NOT trigger the stub either (Codex-caught, round 2)
ok 85 - _fpPlainMessage: a MIXED request that succeeded must NOT trigger the stub either (Codex-caught, round 2)
  ---
  duration_ms: 0.699207
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a MIXED request that failed for an unrelated reason must NOT trigger the stub
ok 86 - _fpPlainMessage: a MIXED request that failed for an unrelated reason must NOT trigger the stub
  ---
  duration_ms: 0.702486
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no survivors
ok 87 - _fpPlainMessage: no survivors
  ---
  duration_ms: 0.323925
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no survivors + truncated mentions the honest count
ok 88 - _fpPlainMessage: no survivors + truncated mentions the honest count
  ---
  duration_ms: 0.217548
  type: 'test'
  ...
# Subtest: _fpPlainMessage: clean winner with nothing flagged reads as clean
ok 89 - _fpPlainMessage: clean winner with nothing flagged reads as clean
  ---
  duration_ms: 0.175233
  type: 'test'
  ...
# Subtest: _fpPlainMessage: data-driven (region-unassigned) components need review
ok 90 - _fpPlainMessage: data-driven (region-unassigned) components need review
  ---
  duration_ms: 0.20124
  type: 'test'
  ...
# Subtest: _fpPlainMessage: decisive_override reads CONDITIONAL and names the fixed parameter
ok 91 - _fpPlainMessage: decisive_override reads CONDITIONAL and names the fixed parameter
  ---
  duration_ms: 0.449186
  type: 'test'
  ...
# Subtest: _fpPlainMessage: unstable_last_resort reads LOW CONFIDENCE, never hides the caveat
ok 92 - _fpPlainMessage: unstable_last_resort reads LOW CONFIDENCE, never hides the caveat
  ---
  duration_ms: 0.285704
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no_clean_survivor names the boundary hit in plain words
ok 93 - _fpPlainMessage: no_clean_survivor names the boundary hit in plain words
  ---
  duration_ms: 0.282309
  type: 'test'
  ...
# Subtest: _fpPlainMessage: unphysical widths surface as LOW CONFIDENCE with no raw ceiling jargon
ok 94 - _fpPlainMessage: unphysical widths surface as LOW CONFIDENCE with no raw ceiling jargon
  ---
  duration_ms: 0.525981
  type: 'test'
  ...
# Subtest: _fpPlainMessage: filtered dominant alternative is mentioned honestly
ok 95 - _fpPlainMessage: filtered dominant alternative is mentioned honestly
  ---
  duration_ms: 1.758487
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a CONDITIONAL result never reads as a clean pass
ok 96 - _fpPlainMessage: a CONDITIONAL result never reads as a clean pass
  ---
  duration_ms: 0.273964
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: sub-minute seconds
ok 97 - _fpFormatElapsed: sub-minute seconds
  ---
  duration_ms: 1.403966
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: minutes + seconds
ok 98 - _fpFormatElapsed: minutes + seconds
  ---
  duration_ms: 0.338932
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: never negative, tolerates junk input
ok 99 - _fpFormatElapsed: never negative, tolerates junk input
  ---
  duration_ms: 0.245041
  type: 'test'
  ...
# Subtest: _fpProgressText: real candidate-sweep message
ok 100 - _fpProgressText: real candidate-sweep message
  ---
  duration_ms: 0.258135
  type: 'test'
  ...
# Subtest: _fpProgressText: starting phase before any candidate has run
ok 101 - _fpProgressText: starting phase before any candidate has run
  ---
  duration_ms: 0.347962
  type: 'test'
  ...
# Subtest: _fpProgressText: missing/malformed poll degrades to a generic message, never throws
ok 102 - _fpProgressText: missing/malformed poll degrades to a generic message, never throws
  ---
  duration_ms: 0.204512
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 103 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 17.271157
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 104 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 8.56462
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 105 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 6.890275
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 106 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 12.989808
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 107 - a converged backend result is applied (sanity)
  ---
  duration_ms: 4.499554
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 108 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.99675
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 109 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 4.4641
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 110 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 4.398962
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 111 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 3.207005
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 112 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 1.46553
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 113 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 1.207916
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 114 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 2.098275
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 115 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 5.45476
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 116 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 7.056162
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 117 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 3.075913
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 118 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 7.366746
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 119 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 1.007151
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 120 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 5.236702
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 121 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.814106
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 122 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.583899
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 123 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 5.054485
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 124 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 2.535082
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 125 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.666304
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 126 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 5.978415
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 127 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.345901
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 128 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 4.088387
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 129 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 0.506688
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 130 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 4.318449
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 131 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 1.256101
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 132 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 5.658709
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 133 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.446224
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 134 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 4.44576
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 135 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.524504
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 136 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.230698
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 137 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 3.550776
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 138 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 7.043755
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 139 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 4.149015
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 140 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 4.05642
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 141 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 4.348685
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 142 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 3.857884
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 143 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 5.136946
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 144 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 4.295031
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice names it experimental and states the runtime range
ok 145 - FP_STRINGS.experimentalNotice names it experimental and states the runtime range
  ---
  duration_ms: 2.527149
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice says BOTH "starting point" and "not a final answer" -- either alone is not the safety claim
ok 146 - FP_STRINGS.experimentalNotice says BOTH "starting point" and "not a final answer" -- either alone is not the safety claim
  ---
  duration_ms: 0.681199
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice does not overclaim correctness and does not describe the app as broken/frozen
ok 147 - FP_STRINGS.experimentalNotice does not overclaim correctness and does not describe the app as broken/frozen
  ---
  duration_ms: 0.557323
  type: 'test'
  ...
# Subtest: the notice banner element and its dismiss button are wired to the actual dismiss function, not just present somewhere in the page
ok 148 - the notice banner element and its dismiss button are wired to the actual dismiss function, not just present somewhere in the page
  ---
  duration_ms: 1.290254
  type: 'test'
  ...
# Subtest: both notice functions read/write the SAME localStorage key -- a mismatched key would show the notice every time despite dismissal
ok 149 - both notice functions read/write the SAME localStorage key -- a mismatched key would show the notice every time despite dismissal
  ---
  duration_ms: 3.339624
  type: 'test'
  ...
# Subtest: the gate function early-returns (hides, does not show) when already dismissed, and only sets text+shows in the un-dismissed path
ok 150 - the gate function early-returns (hides, does not show) when already dismissed, and only sets text+shows in the un-dismissed path
  ---
  duration_ms: 3.320977
  type: 'test'
  ...
# Subtest: openFindPeaksModal calls the notice gate so it actually shows on open
ok 151 - openFindPeaksModal calls the notice gate so it actually shows on open
  ---
  duration_ms: 1.333142
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed has a clear, non-bare label
ok 152 - FP_STRINGS.materials.mixed has a clear, non-bare label
  ---
  duration_ms: 17.286694
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint is advisory, never claims correction
ok 153 - FP_STRINGS.materials.mixed hint is advisory, never claims correction
  ---
  duration_ms: 0.594923
  type: 'test'
  ...
# Subtest: FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
ok 154 - FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
  ---
  duration_ms: 0.292802
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
ok 155 - FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
  ---
  duration_ms: 0.372349
  type: 'test'
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Subtest: (A) frontend vs backend parity: Gaussian
not ok 156 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1627.881633
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
    startSubtestAfterBootstrap (node:internal/test_runner/harness:296:17)
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
not ok 157 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1520.2519
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: GL
not ok 158 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1402.006821
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: Voigt
not ok 159 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1411.100725
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DS
not ok 160 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1453.508236
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
not ok 161 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1526.552051
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)
not ok 162 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1534.632263
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:171:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:176:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX at m=0 (no convolution)
not ok 163 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1496.175439
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:182:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:188:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
not ok 164 - (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
  ---
  duration_ms: 1490.829181
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:194:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:199:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
not ok 165 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1447.568207
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
not ok 166 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1495.430266
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
not ok 167 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1549.924657
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
not ok 168 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1496.656217
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
not ok 169 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1466.302104
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:235:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:242:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 170 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.374596
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 171 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.158206
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 172 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.549405
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 173 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.233299
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 174 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.248258
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 175 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.295761
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
not ok 176 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA # TODO evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)
  ---
  duration_ms: 4.051575
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA at x=393.3: evalPeak=7298.4050340345175, evalPeakArray[i]=8703.575517573383, rel diff=7.8969%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:272:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 177 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.576143
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7170.363795150584, rel diff=24.2055%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:272:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (C) evalPeak() has no direct callers outside evalPeakArray()
ok 178 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 3.352366
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
not ok 179 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1461.285958
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
not ok 180 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1537.868241
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Voigt
not ok 181 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1473.122318
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: GL
not ok 182 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1485.514819
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
not ok 183 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1463.08193
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DS
not ok 184 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1422.16044
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
not ok 185 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1493.769392
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
not ok 186 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1535.194176
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0)
not ok 187 - (D) sweep across the fitted range: DSG_LA (m > 0)
  ---
  duration_ms: 1389.14333
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP
not ok 188 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1395.189892
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:389:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:390:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
not ok 189 - (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
  ---
  duration_ms: 1473.175398
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
not ok 190 - (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
  ---
  duration_ms: 1415.577169
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
not ok 191 - (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
  ---
  duration_ms: 1373.158184
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
not ok 192 - (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
  ---
  duration_ms: 1464.496306
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
not ok 193 - (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
  ---
  duration_ms: 1490.311421
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
not ok 194 - (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
  ---
  duration_ms: 1418.839982
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
not ok 195 - (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
  ---
  duration_ms: 1366.473483
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
not ok 196 - (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
  ---
  duration_ms: 1357.867219
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 6-point irregular grid
not ok 197 - (D″) DS+G regression: a 6-point irregular grid
  ---
  duration_ms: 1381.552286
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
not ok 198 - (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
  ---
  duration_ms: 1350.62224
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
not ok 199 - (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
  ---
  duration_ms: 1368.310877
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
not ok 200 - (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
  ---
  duration_ms: 1357.85292
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
not ok 201 - (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
  ---
  duration_ms: 1370.059328
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
not ok 202 - (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
  ---
  duration_ms: 1361.707438
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
not ok 203 - (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
  ---
  duration_ms: 1379.742006
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 2-point grid
not ok 204 - (D″) DS+G regression: a 2-point grid
  ---
  duration_ms: 1429.038905
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 1-point grid
not ok 205 - (D″) DS+G regression: a 1-point grid
  ---
  duration_ms: 1370.740048
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
not ok 206 - (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1376.104495
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
not ok 207 - (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1347.904919
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
not ok 208 - (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1341.625283
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
not ok 209 - (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1327.792612
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
not ok 210 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1624.921012
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
not ok 211 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1514.682266
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
not ok 212 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1404.186751
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
not ok 213 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1427.265318
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
not ok 214 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1443.574602
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
not ok 215 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1520.837509
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 216 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
  ---
  duration_ms: 1534.654444
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
not ok 217 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX # TODO LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit
  ---
  duration_ms: 1497.08603
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
not ok 218 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1479.894098
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:131:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:138:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
not ok 219 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1456.715566
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:146:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:148:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
not ok 220 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1496.41863
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
not ok 221 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1550.228889
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
not ok 222 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1496.443822
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
not ok 223 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1463.526601
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
not ok 224 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1474.830501
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
not ok 225 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1537.895339
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
not ok 226 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1471.962124
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
not ok 227 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1478.635183
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
not ok 228 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1458.693466
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
not ok 229 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1422.879348
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
not ok 230 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1508.37671
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
not ok 231 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1531.693329
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
not ok 232 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1391.171634
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
not ok 233 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1394.902265
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
not ok 234 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1471.929555
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
not ok 235 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1414.436686
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
not ok 236 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1373.702263
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
not ok 237 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1464.803547
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
not ok 238 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
  ---
  duration_ms: 1490.072969
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
not ok 239 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
  ---
  duration_ms: 1419.921704
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
not ok 240 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
  ---
  duration_ms: 1365.724077
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
not ok 241 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
  ---
  duration_ms: 1359.004185
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
not ok 242 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1379.284637
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:213:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:214:33)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
not ok 243 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1351.172051
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:224:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:232:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
not ok 244 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1369.352352
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:242:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/lineshape_roundtrip.test.js:251:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 245 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1824.969117
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 246 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 328.564235
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 247 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 14.834093
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 248 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 10.123856
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 249 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 13.902351
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 250 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 12.653573
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 251 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 11.466465
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 252 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 13.906102
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 253 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 63.422106
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 254 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 32.744627
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 255 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 8.237379
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 256 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 20.678017
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 257 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 12.906703
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 258 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 10.975452
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 259 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 14.684015
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 260 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1834.670581
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 261 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 88.374232
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 262 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 24.788467
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 263 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 17.265796
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 264 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 113.794017
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 265 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1433.223709
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 266 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 27.652564
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 267 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 16.659856
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 268 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 10.189357
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 269 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1846.488469
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: reduced chi-square does not count the held caM as a varied parameter
ok 270 - reduced chi-square does not count the held caM as a varied parameter
  ---
  duration_ms: 21.849061
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 271 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 14.020488
  type: 'test'
  ...
# Subtest: plain, indented, multi-declarator, same-line, multiline, ASI declarations
ok 272 - plain, indented, multi-declarator, same-line, multiline, ASI declarations
  ---
  duration_ms: 9.79786
  type: 'test'
  ...
# Subtest: populated containers, ALL_CAPS containers, parenthesised and conditional initialisers
ok 273 - populated containers, ALL_CAPS containers, parenthesised and conditional initialisers
  ---
  duration_ms: 3.630008
  type: 'test'
  ...
# Subtest: destructuring, labelled, unbraced-if, top-level block and static class fields
ok 274 - destructuring, labelled, unbraced-if, top-level block and static class fields
  ---
  duration_ms: 4.701849
  type: 'test'
  ...
# Subtest: function-local declarations and primitive consts are not module state
ok 275 - function-local declarations and primitive consts are not module state
  ---
  duration_ms: 3.412275
  type: 'test'
  ...
# Subtest: comments, strings, regex and nested template literals cannot hide or fake a declaration
ok 276 - comments, strings, regex and nested template literals cannot hide or fake a declaration
  ---
  duration_ms: 2.497281
  type: 'test'
  ...
# Subtest: appending a forbidden declaration to each real inline script is found
ok 277 - appending a forbidden declaration to each real inline script is found
  ---
  duration_ms: 496.55465
  type: 'test'
  ...
# Subtest: destructuring defaults and rest create containers even when the right-hand side is primitive
ok 278 - destructuring defaults and rest create containers even when the right-hand side is primitive
  ---
  duration_ms: 0.440098
  type: 'test'
  ...
# Subtest: static fields with string or computed keys, class expressions and static blocks are reported
ok 279 - static fields with string or computed keys, class expressions and static blocks are reported
  ---
  duration_ms: 0.749857
  type: 'test'
  ...
# Subtest: a const whose initialiser is a class expression WITH static fields is not skipped
ok 280 - a const whose initialiser is a class expression WITH static fields is not skipped
  ---
  duration_ms: 0.427785
  type: 'test'
  ...
# Subtest: static fields on an anonymous superclass expression are attributed to the subclass
ok 281 - static fields on an anonymous superclass expression are attributed to the subclass
  ---
  duration_ms: 0.468874
  type: 'test'
  ...
# Subtest: a static block is reported as a whole, whatever it does
ok 282 - a static block is reported as a whole, whatever it does
  ---
  duration_ms: 0.306823
  type: 'test'
  ...
# Subtest: an unbound class expression with static state is reported under an un-allowlistable name
ok 283 - an unbound class expression with static state is reported under an un-allowlistable name
  ---
  duration_ms: 0.235943
  type: 'test'
  ...
# Subtest: computed class keys are evaluated in the enclosing scope: a class declared inside one is reported
ok 284 - computed class keys are evaluated in the enclosing scope: a class declared inside one is reported
  ---
  duration_ms: 0.784074
  type: 'test'
  ...
# Subtest: catch-clause bindings at module scope are enumerated
ok 285 - catch-clause bindings at module scope are enumerated
  ---
  duration_ms: 0.277717
  type: 'test'
  ...
# Subtest: a RegExp literal is a mutable object, not an immutable constant
ok 286 - a RegExp literal is a mutable object, not an immutable constant
  ---
  duration_ms: 0.158089
  type: 'test'
  ...
# Subtest: a class without static state reports nothing at all
ok 287 - a class without static state reports nothing at all
  ---
  duration_ms: 0.174987
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 288 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 265.653814
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 289 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 106.709585
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 290 - the known class-C holders are gone from module scope
  ---
  duration_ms: 8.033846
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 291 - async operations capture their owning record before the first await
  ---
  duration_ms: 2.372698
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 292 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.642866
  type: 'test'
  ...
# Subtest: tolFromSlider clamps to [0.25, 5.0] and snaps to 0.25
ok 293 - tolFromSlider clamps to [0.25, 5.0] and snaps to 0.25
  ---
  duration_ms: 2.098282
  type: 'test'
  ...
# Subtest: coerceTolToEv maps legacy modes onto the base, passes numbers through
ok 294 - coerceTolToEv maps legacy modes onto the base, passes numbers through
  ---
  duration_ms: 0.298827
  type: 'test'
  ...
# Subtest: blendedSearch matches elements by symbol/name
ok 295 - blendedSearch matches elements by symbol/name
  ---
  duration_ms: 0.430692
  type: 'test'
  ...
# Subtest: blendedSearch matches compounds, tagged compound
ok 296 - blendedSearch matches compounds, tagged compound
  ---
  duration_ms: 0.260143
  type: 'test'
  ...
# Subtest: blendedSearch numeric query yields energy rows
ok 297 - blendedSearch numeric query yields energy rows
  ---
  duration_ms: 0.327534
  type: 'test'
  ...
# Subtest: blendedSearch caps results and empty query returns []
ok 298 - blendedSearch caps results and empty query returns []
  ---
  duration_ms: 0.913396
  type: 'test'
  ...
# Subtest: parseChemKey: exact spin-orbit key
ok 299 - parseChemKey: exact spin-orbit key
  ---
  duration_ms: 0.505857
  type: 'test'
  ...
# Subtest: parseChemKey: subshell-only p attaches to BOTH spin-orbit lines (Si 2p)
ok 300 - parseChemKey: subshell-only p attaches to BOTH spin-orbit lines (Si 2p)
  ---
  duration_ms: 0.227614
  type: 'test'
  ...
# Subtest: parseChemKey: 1s has no split
ok 301 - parseChemKey: 1s has no split
  ---
  duration_ms: 0.758404
  type: 'test'
  ...
# Subtest: compoundCandidatesFrom returns legacy candidates within tol, honest proximity
ok 302 - compoundCandidatesFrom returns legacy candidates within tol, honest proximity
  ---
  duration_ms: 2.39019
  type: 'test'
  ...
# Subtest: capConfidenceByTier: curated/machine keep candidate label + raw energyMatch
ok 303 - capConfidenceByTier: curated/machine keep candidate label + raw energyMatch
  ---
  duration_ms: 0.416645
  type: 'test'
  ...
# Subtest: capConfidenceByTier: legacy noun is "Legacy hint", energy annotated, never Strong
ok 304 - capConfidenceByTier: legacy noun is "Legacy hint", energy annotated, never Strong
  ---
  duration_ms: 0.180415
  type: 'test'
  ...
# Subtest: mergeAndRankCandidates: element-only golden order is Δ-primary
ok 305 - mergeAndRankCandidates: element-only golden order is Δ-primary
  ---
  duration_ms: 0.304599
  type: 'test'
  ...
# Subtest: adding compounds does not perturb the element subsequence
ok 306 - adding compounds does not perturb the element subsequence
  ---
  duration_ms: 0.212563
  type: 'test'
  ...
# Subtest: mergeAndRankCandidates: a clear Δ winner ranks first regardless of tier
ok 307 - mergeAndRankCandidates: a clear Δ winner ranks first regardless of tier
  ---
  duration_ms: 0.158206
  type: 'test'
  ...
# Subtest: augerApparentBE shifts with source; photoelectronBE is source-invariant
ok 308 - augerApparentBE shifts with source; photoelectronBE is source-invariant
  ---
  duration_ms: 0.230242
  type: 'test'
  ...
# Subtest: compound BE equals input be_ev (no ccShift, source-invariant)
ok 309 - compound BE equals input be_ev (no ccShift, source-invariant)
  ---
  duration_ms: 0.426028
  type: 'test'
  ...
# Subtest: elementOverlayVisible no longer depends on the palette being open
ok 310 - elementOverlayVisible no longer depends on the palette being open
  ---
  duration_ms: 0.241208
  type: 'test'
  ...
# Subtest: tierColor is a single source of truth for the three data tiers
ok 311 - tierColor is a single source of truth for the three data tiers
  ---
  duration_ms: 0.263344
  type: 'test'
  ...
# Subtest: tierColor falls back safely for unknown/missing tiers
ok 312 - tierColor falls back safely for unknown/missing tiers
  ---
  duration_ms: 0.128624
  type: 'test'
  ...
# Subtest: tierNote is the single source for tier wording; reviewed text is canonical
ok 313 - tierNote is the single source for tier wording; reviewed text is canonical
  ---
  duration_ms: 0.162434
  type: 'test'
  ...
# Subtest: nextColorIdx returns the first index whose palette residue is unused
ok 314 - nextColorIdx returns the first index whose palette residue is unused
  ---
  duration_ms: 0.263563
  type: 'test'
  ...
# Subtest: nextColorIdx falls back to max(used)+1 once every residue is taken
ok 315 - nextColorIdx falls back to max(used)+1 once every residue is taken
  ---
  duration_ms: 0.135599
  type: 'test'
  ...
# Subtest: nextColorIdx: a new pick shares no rendered residue with existing overlays (while residues remain)
ok 316 - nextColorIdx: a new pick shares no rendered residue with existing overlays (while residues remain)
  ---
  duration_ms: 0.122015
  type: 'test'
  ...
# Subtest: nextColorIdx ignores invalid entries (non-integer/negative) when computing the used set
ok 317 - nextColorIdx ignores invalid entries (non-integer/negative) when computing the used set
  ---
  duration_ms: 0.102634
  type: 'test'
  ...
# Subtest: clampToViewport: an in-bounds position passes through unchanged
ok 318 - clampToViewport: an in-bounds position passes through unchanged
  ---
  duration_ms: 0.213747
  type: 'test'
  ...
# Subtest: clampToViewport: negative / above-left position clamps to the margin
ok 319 - clampToViewport: negative / above-left position clamps to the margin
  ---
  duration_ms: 0.162464
  type: 'test'
  ...
# Subtest: clampToViewport: far off-screen (stale) position clamps inside the viewport
ok 320 - clampToViewport: far off-screen (stale) position clamps inside the viewport
  ---
  duration_ms: 0.14355
  type: 'test'
  ...
# Subtest: clampToViewport: non-finite (corrupt saved) coords fall back to the margin
ok 321 - clampToViewport: non-finite (corrupt saved) coords fall back to the margin
  ---
  duration_ms: 0.140634
  type: 'test'
  ...
# Subtest: overlays and compound markers have independent (decoupled) version constants
ok 322 - overlays and compound markers have independent (decoupled) version constants
  ---
  duration_ms: 0.119949
  type: 'test'
  ...
# Subtest: serializeRefOverlays is total: null for empty/nullish/malformed sel
ok 323 - serializeRefOverlays is total: null for empty/nullish/malformed sel
  ---
  duration_ms: 0.24544
  type: 'test'
  ...
# Subtest: serializeRefOverlays captures selection and never emits identify keys
ok 324 - serializeRefOverlays captures selection and never emits identify keys
  ---
  duration_ms: 0.232312
  type: 'test'
  ...
# Subtest: round-trip preserves a valid colorIdx verbatim
ok 325 - round-trip preserves a valid colorIdx verbatim
  ---
  duration_ms: 0.317892
  type: 'test'
  ...
# Subtest: deserialize: absent or envelope-malformed → clean empty (no throw)
ok 326 - deserialize: absent or envelope-malformed → clean empty (no throw)
  ---
  duration_ms: 0.252953
  type: 'test'
  ...
# Subtest: deserialize: newer internal version is ignored (no misread of a future shape)
ok 327 - deserialize: newer internal version is ignored (no misread of a future shape)
  ---
  duration_ms: 0.269921
  type: 'test'
  ...
# Subtest: deserialize entry repair: keep valid, skip no-sym, repair invalid colorIdx, keep unknown tier
ok 328 - deserialize entry repair: keep valid, skip no-sym, repair invalid colorIdx, keep unknown tier
  ---
  duration_ms: 0.28154
  type: 'test'
  ...
# Subtest: post-load next pick renders a color distinct from all restored while residues remain
ok 329 - post-load next pick renders a color distinct from all restored while residues remain
  ---
  duration_ms: 0.216076
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers is total: null for empty/nullish/non-array
ok 330 - serializeRefCompoundMarkers is total: null for empty/nullish/non-array
  ---
  duration_ms: 0.214076
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers is total for malformed ARRAY ENTRIES (no throw; all-invalid → null)
ok 331 - serializeRefCompoundMarkers is total for malformed ARRAY ENTRIES (no throw; all-invalid → null)
  ---
  duration_ms: 0.202566
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept
ok 332 - serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept
  ---
  duration_ms: 0.327223
  type: 'test'
  ...
# Subtest: compound markers round-trip at global scope; absent/malformed/newer → empty
ok 333 - compound markers round-trip at global scope; absent/malformed/newer → empty
  ---
  duration_ms: 0.410269
  type: 'test'
  ...
# Subtest: compound markers: non-finite be dropped, absent sym tolerated (partial-invalid)
ok 334 - compound markers: non-finite be dropped, absent sym tolerated (partial-invalid)
  ---
  duration_ms: 0.206028
  type: 'test'
  ...
# Subtest: summary wording: counts of STARTS and of SOLUTIONS, never certification
ok 335 - summary wording: counts of STARTS and of SOLUTIONS, never certification
  ---
  duration_ms: 30.811307
  type: 'test'
  ...
# Subtest: no alternative: one line, no table
ok 336 - no alternative: one line, no table
  ---
  duration_ms: 24.925047
  type: 'test'
  ...
# Subtest: alternatives: "Your fit" first, own areas per component, the moved component named and coloured
ok 337 - alternatives: "Your fit" first, own areas per component, the moved component named and coloured
  ---
  duration_ms: 17.528516
  type: 'test'
  ...
# Subtest: RED band: applying asks first and NAMES the component and the distance
ok 338 - RED band: applying asks first and NAMES the component and the distance
  ---
  duration_ms: 15.894513
  type: 'test'
  ...
# Subtest: adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
ok 339 - adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
  ---
  duration_ms: 15.984519
  type: 'test'
  ...
# Subtest: below the red band there is no dialog
ok 340 - below the red band there is no dialog
  ---
  duration_ms: 34.740135
  type: 'test'
  ...
# Subtest: a locked parameter is never moved by an alternative
ok 341 - a locked parameter is never moved by an alternative
  ---
  duration_ms: 10.752476
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
ok 342 - evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
  ---
  duration_ms: 10.165896
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
ok 343 - evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
  ---
  duration_ms: 13.336306
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
ok 344 - evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
  ---
  duration_ms: 11.796237
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
ok 345 - evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
  ---
  duration_ms: 10.775848
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
ok 346 - evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
  ---
  duration_ms: 11.152424
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
ok 347 - evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
  ---
  duration_ms: 12.319612
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
ok 348 - evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
  ---
  duration_ms: 7.89889
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
ok 349 - evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
  ---
  duration_ms: 8.936491
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
ok 350 - evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
  ---
  duration_ms: 8.662169
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
ok 351 - evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
  ---
  duration_ms: 7.836882
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
ok 352 - evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
  ---
  duration_ms: 9.486313
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
ok 353 - evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
  ---
  duration_ms: 13.029607
  type: 'test'
  ...
# Subtest: a cosmetic edit (name, colour, visibility) does not invalidate the evidence
ok 354 - a cosmetic edit (name, colour, visibility) does not invalidate the evidence
  ---
  duration_ms: 9.309933
  type: 'test'
  ...
# Subtest: preview overlays a COPY and toggles off; the model is untouched
ok 355 - preview overlays a COPY and toggles off; the model is untouched
  ---
  duration_ms: 9.413302
  type: 'test'
  ...
# Subtest: a record is keyed like the live tab (project save of a non-active tab)
ok 356 - a record is keyed like the live tab (project save of a non-active tab)
  ---
  duration_ms: 9.494779
  type: 'test'
  ...
# Subtest: what is saved: the counts, never the alternatives' parameter sets
ok 357 - what is saved: the counts, never the alternatives' parameter sets
  ---
  duration_ms: 12.084191
  type: 'test'
  ...
# Subtest: a loaded summary (no parameter sets) still renders its line and offers nothing to apply
ok 358 - a loaded summary (no parameter sets) still renders its line and offers nothing to apply
  ---
  duration_ms: 8.946465
  type: 'test'
  ...
# Subtest: wiring: the trigger is decided with the other request inputs, BEFORE the first await
ok 359 - wiring: the trigger is decided with the other request inputs, BEFORE the first await
  ---
  duration_ms: 12.524115
  type: 'test'
  ...
# Subtest: persistence and export sites carry the summary
ok 360 - persistence and export sites carry the summary
  ---
  duration_ms: 2.382713
  type: 'test'
  ...
# Subtest: the tooltip reports what the starts found and claims nothing about the data
ok 361 - the tooltip reports what the starts found and claims nothing about the data
  ---
  duration_ms: 0.693248
  type: 'test'
  ...
# Subtest: the recorded adoption is worded once, for the exports
ok 362 - the recorded adoption is worded once, for the exports
  ---
  duration_ms: 9.013638
  type: 'test'
  ...
# Subtest: round-trip A -> B -> A restores every ACTIVE parameter (all shapes)
ok 363 - round-trip A -> B -> A restores every ACTIVE parameter (all shapes)
  ---
  duration_ms: 5.364354
  type: 'test'
  ...
# Subtest: DS+G -> GL -> DS+G leaves laAlpha/laBeta/laM and the curve unchanged
ok 364 - DS+G -> GL -> DS+G leaves laAlpha/laBeta/laM and the curve unchanged
  ---
  duration_ms: 22.084445
  type: 'test'
  ...
# Subtest: switching carries the effective eV width, both directions of laM<->fwhm
ok 365 - switching carries the effective eV width, both directions of laM<->fwhm
  ---
  duration_ms: 0.352379
  type: 'test'
  ...
# Subtest: a genuinely-new param is defaulted; a carried-over one is preserved
ok 366 - a genuinely-new param is defaulted; a carried-over one is preserved
  ---
  duration_ms: 0.224997
  type: 'test'
  ...
# Subtest: export columns read the ACTIVE shape, never a stale accumulated param
ok 367 - export columns read the ACTIVE shape, never a stale accumulated param
  ---
  duration_ms: 0.414355
  type: 'test'
  ...
# Subtest: multi-hop round-trip DS+G -> LACX -> GL -> DS+G restores active params
ok 368 - multi-hop round-trip DS+G -> LACX -> GL -> DS+G restores active params
  ---
  duration_ms: 6.310964
  type: 'test'
  ...
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 369 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 26.350838
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 370 - ascending and descending BE input give the identical background
  ---
  duration_ms: 1.273602
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 371 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.691982
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 372 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 9.62778
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 373 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 4.115666
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 374 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 1.525827
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 375 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 16.947968
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 376 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 8.633448
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 377 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 7.974518
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 378 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 10.888614
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 379 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 13.737724
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 380 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 19.901852
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 381 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 9.353837
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 382 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 9.113428
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 383 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 11.793582
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 384 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 4.967666
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 385 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 3.018618
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 386 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 1.178618
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 387 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 6.433633
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 388 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 9.383366
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 389 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 8.572951
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 390 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 4.661353
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 391 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.209604
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 392 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 6.701673
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 393 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 4.712753
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 394 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 5.438809
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 395 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 14.239348
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 396 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 4.507173
  type: 'test'
  ...
1..396
# tests 396
# suites 0
# pass 313
# fail 78
# cancelled 0
# skipped 0
# todo 5
# duration_ms 64945.712969

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -u -c '
import ast, pathlib, subprocess, types, sys
import fitting
source = subprocess.check_output([\"git\",\"show\",\"main:fitting.py\"],text=True)
old = types.ModuleType(\"fitting_main\")
sys.modules[\"fitting_main\"] = old
exec(compile(source, \"main:fitting.py\", \"exec\"), old.__dict__)
new_src = pathlib.Path(\"fitting.py\").read_text()
old_fn = next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name == \"_ds_g_dscore_gauss\")
new_fn = next(n for n in ast.parse(new_src).body if isinstance(n,ast.FunctionDef) and n.name == old_fn.name)
guard = next(n for n in new_fn.body if isinstance(n,ast.If) and isinstance(n.test,ast.BoolOp))
idx=new_fn.body.index(guard)
new_fn.body[idx:idx+1]=guard.orelse
print(\"AST identical after removing outside guard:\", ast.dump(old_fn)==ast.dump(new_fn), flush=True)
import numpy as np
for x in [np.array([0.]),np.linspace(-5,5,21),np.linspace(-5,5,21)[::-1]]:
 step=max(float(np.median(np.abs(np.diff(x)))) if len(x)>1 else .05,1e-6)
 pad=max(int(np.ceil(1/step)),1)*step
 lo,hi=min(x[0],x[-1])-pad,max(x[0],x[-1])+pad
 for c in [lo,hi,np.nextafter(lo,hi),np.nextafter(hi,lo),float(\"nan\")]:
  kw=dict(amplitude=1.,center=c,alpha=.49,beta=.05,m_gauss=.001)
  a=old._ds_g_dscore_gauss(x,**kw); b=fitting._ds_g_dscore_gauss(x,**kw)
  print(\"extra identity\",len(x),float(x[0]),c, a.tobytes()==b.tobytes(), flush=True)
proof=pathlib.Path(\"scripts/dsg_outside_centre_identity.py\").read_text()
start=proof.index(\"spec = importlib.util.spec_from_file_location\")
end=proof.index(\"f_new, f_old\",start)
proof=proof[:start]+proof[end:]
exec(compile(proof,\"identity_proof_in_memory\",\"exec\"))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 exited 1 in 1309ms:
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py", line 33, in <module>
    from lmfit import Model, Parameters
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
    from .confidence import conf_interval, conf_interval2d
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
    from .minimizer import MinimizerException
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
    from .parameter import Parameter, Parameters
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
    from .jsonutils import decode4js, encode4js
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
    import dill
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
    from .session import (
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
    TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                               ^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator']

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();
const specs=[];
for(const n of [1,21,121,200,201]) for(const step0 of [.05,.1,.5]) for(const b of [.05,.7]) for(const m of [.001,.05,.4]) {
 const x=Array.from({length:n},(_,i)=>n===1?0:-5+step0*i);
 const d=x.slice(1).map((v,i)=>Math.abs(v-x[i])).sort((a,b)=>a-b), j=d.length>>1;
 const step=n===1?.05:(d.length%2?d[j]:(d[j-1]+d[j])/2), pad=Math.max(1,Math.ceil(Math.max(10*m,20*b)/step));
 for(const side of [-1,1]) for(const delta of [0,1e-9,.000001]) {
 const edge=side<0?x[0]-pad*step:x[n-1]+pad*step, c=edge-side*delta;
 specs.push({shape:'\\''ds_g'\\'',x,params:{amplitude:1,center:c,alpha:.49,beta:b,m_gauss:m},meta:{n,step0,b,m,side,delta,edge}});
 }
}
const out=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'', '\\''import tempfile,runpy; tempfile.tempdir=\"/tmp\"; runpy.run_path(\"tests/js/lineshape_parity_backend.py\",run_name=\"__main__\")'\\''],{input:JSON.stringify(specs),encoding:'\\''utf8'\\'',maxBuffer:64*1024*1024}));
const results=specs.map((s,i)=>{const p=s.params; const js=ev(s.x,{shape:'\\''DSG_LA'\\'',amplitude:1,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss}); return {meta:s.meta,center:p.center,err:Math.max(...js.map((v,j)=>Math.abs(v-out[i][j]))),jsMax:Math.max(...js.map(Math.abs)),pyMax:Math.max(...out[i].map(Math.abs))};}).sort((a,b)=>b.err-a.err);
console.log(JSON.stringify({total:results.length,failures:results.filter(r=>r.err>1e-6).length,worst:results.slice(0,12)},null,2));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import pytest
raise SystemExit(pytest.main(['\\''-q'\\'','\\''-s'\\'','\\''-p'\\'','\\''no:cacheprovider'\\'','\\''tests/test_dsg_outside_centre.py'\\'','\\''tests/autofit/test_c1s_parity_battery.py'\\'','\\''tests/autofit/test_u4f_parity_battery.py'\\'']))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 2335ms:
/Users/skyefortier/.matplotlib is not a writable directory
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/fitting.py:279: RuntimeWarning: invalid value encountered in divide
  gauss_kernel /= gauss_kernel.sum()  # normalise to unit area
{
  "total": 540,
  "failures": 210,
  "worst": [
    {
      "meta": {
        "n": 201,
        "step0": 0.1,
        "b": 0.05,
        "m": 0.001,
        "side": 1,
        "delta": 0,
        "edge": 16.099999999999994
      },
      "center": 16.099999999999994,
      "err": 449197075652706300,
      "jsMax": 1,
      "pyMax": 449197075652706300
    },
    {
      "meta": {
        "n": 121,
        "step0": 0.5,
        "b": 0.05,
        "m": 0.001,
        "side": 1,
        "delta": 0,
        "edge": 56
      },
      "center": 56,
      "err": 403860815767457540,
      "jsMax": 403860815767457540,
      "pyMax": 1
    },
    {
      "meta": {
        "n": 121,
        "step0": 0.5,
        "b": 0.05,
        "m": 0.05,
        "side": 1,
        "delta": 0,
        "edge": 56
      },
      "center": 56,
      "err": 403860815767457540,
      "jsMax": 403860815767457540,
      "pyMax": 1
    },
    {
      "meta": {
        "n": 201,
        "step0": 0.5,
        "b": 0.05,
        "m": 0.001,
        "side": 1,
        "delta": 0,
        "edge": 96
      },
      "center": 96,
      "err": 376847915758775300,
      "jsMax": 376847915758775300,
      "pyMax": 1
    },
    {
      "meta": {
        "n": 201,
        "step0": 0.5,
        "b": 0.05,
        "m": 0.05,
        "side": 1,
        "delta": 0,
        "edge": 96
      },
      "center": 96,
      "err": 376847915758775300,
      "jsMax": 376847915758775300,
      "pyMax": 1
    },
    {
      "meta": {
        "n": 200,
        "step0": 0.5,
        "b": 0.05,
        "m": 0.05,
        "side": 1,
        "delta": 0,
        "edge": 95.5
      },
      "center": 95.5,
      "err": 136681348207546240,
      "jsMax": 1,
      "pyMax": 136681348207546240
    },
    {
      "meta": {
        "n": 1,
        "step0": 0.05,
        "b": 0.7,
        "m": 0.001,
        "side": 1,
        "delta": 0,
        "edge": 14
      },
      "center": 14,
      "err": 89299950621391980,
      "jsMax": 1,
      "pyMax": 89299950621391980
    },
    {
      "meta": {
        "n": 1,
        "step0": 0.1,
        "b": 0.7,
        "m": 0.001,
        "side": 1,
        "delta": 0,
        "edge": 14
      },
      "center": 14,
      "err": 89299950621391980,
      "jsMax": 1,
      "pyMax": 89299950621391980
    },
    {
      "meta": {
        "n": 1,
        "step0": 0.5,
        "b": 0.7,
        "m": 0.001,
        "side": 1,
        "delta": 0,
        "edge": 14
      },
      "center": 14,
      "err": 89299950621391980,
      "jsMax": 1,
      "pyMax": 89299950621391980
    },
    {
      "meta": {
        "n": 201,
        "step0": 0.05,
        "b": 0.05,
        "m": 0.001,
        "side": 1,
        "delta": 0,
        "edge": 6.049999999999996
      },
      "center": 6.049999999999996,
      "err": 51774864883230960,
      "jsMax": 1,
      "pyMax": 51774864883230960
    },
    {
      "meta": {
        "n": 121,
        "step0": 0.5,
        "b": 0.05,
        "m": 0.001,
        "side": -1,
        "delta": 0,
        "edge": -6
      },
      "center": -6,
      "err": 35161357450226590,
      "jsMax": 1,
      "pyMax": 35161357450226590
    },
    {
      "meta": {
        "n": 121,
        "step0": 0.5,
        "b": 0.05,
        "m": 0.05,
        "side": -1,
        "delta": 0,
        "edge": -6
      },
      "center": -6,
      "err": 35161357450226590,
      "jsMax": 1,
      "pyMax": 35161357450226590
    }
  ]
}

 succeeded in 7627ms:
.........................................................................................................................
121 passed in 7.12s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -u -c '
import tempfile; tempfile.tempdir=\"/tmp\"
import ast, pathlib, subprocess, types, sys
import fitting
source = subprocess.check_output([\"git\",\"show\",\"main:fitting.py\"],text=True)
old = types.ModuleType(\"fitting_main\")
sys.modules[\"fitting_main\"] = old
exec(compile(source, \"main:fitting.py\", \"exec\"), old.__dict__)
new_src = pathlib.Path(\"fitting.py\").read_text()
old_fn = next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name == \"_ds_g_dscore_gauss\")
new_fn = next(n for n in ast.parse(new_src).body if isinstance(n,ast.FunctionDef) and n.name == old_fn.name)
guard = next(n for n in new_fn.body if isinstance(n,ast.If) and isinstance(n.test,ast.BoolOp))
idx=new_fn.body.index(guard)
new_fn.body[idx:idx+1]=guard.orelse
print(\"AST identical after removing outside guard:\", ast.dump(old_fn)==ast.dump(new_fn), flush=True)
import numpy as np
for x in [np.array([0.]),np.linspace(-5,5,21),np.linspace(-5,5,21)[::-1]]:
 step=max(float(np.median(np.abs(np.diff(x)))) if len(x)>1 else .05,1e-6)
 pad=max(int(np.ceil(1/step)),1)*step
 lo,hi=min(x[0],x[-1])-pad,max(x[0],x[-1])+pad
 for c in [lo,hi,np.nextafter(lo,hi),np.nextafter(hi,lo),float(\"nan\")]:
  kw=dict(amplitude=1.,center=c,alpha=.49,beta=.05,m_gauss=.001)
  a=old._ds_g_dscore_gauss(x,**kw); b=fitting._ds_g_dscore_gauss(x,**kw)
  print(\"extra identity\",len(x),float(x[0]),c, a.tobytes()==b.tobytes(), flush=True)
proof=pathlib.Path(\"scripts/dsg_outside_centre_identity.py\").read_text()
start=proof.index(\"spec = importlib.util.spec_from_file_location\")
end=proof.index(\"f_new, f_old\",start)
proof=proof[:start]+proof[end:]
exec(compile(proof,\"identity_proof_in_memory\",\"exec\"))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
codex
The padded-edge probe found a remaining parity failure: at an exact padded endpoint, the preserved normalization can still divide by FFT rounding noise. One case gives a page maximum of about `4e17` at unit amplitude while the server returns `1`. The guarded-branch tests and C1s/U4f batteries passed: 121 tests.

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const cp=require('\\''child_process'\\''), fs=require('\\''fs'\\'');
const orig=cp.execFileSync;
cp.execFileSync=function(file,args,opts) {
 if(String(file).includes('\\''python'\\'') && args && args[0] && args[0].endsWith('\\''.py'\\'')) {
  const script=args[0];
  args=['\\''-c'\\'','\\''import tempfile,runpy,sys; tempfile.tempdir=\"/tmp\"; p=sys.argv[1]; sys.argv=sys.argv[1:]; runpy.run_path(p,run_name=\"__main__\")'\\'',script,...args.slice(1)];
 }
 return orig.call(this,file,args,opts);
};
for(const name of fs.readdirSync('\\''tests/js'\\'').filter(n=>n.endsWith('\\''.test.js'\\''))) require('\\''./tests/js/'\\''+name);
' 2>&1 | tail -16" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();
const specs=[];

for(const c of [6,5.999999999,5.999999,5.999,6.000000001,-6,-5.999999999]) specs.push({shape:'\\''ds_g'\\'',x:Array.from({length:21},(_,i)=>-5+.5*i),params:{amplitude:1,center:c,alpha:.49,beta:.05,m_gauss:.05},meta:{center:c}});
const out=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'', '\\''import tempfile,runpy; tempfile.tempdir=\"/tmp\"; runpy.run_path(\"tests/js/lineshape_parity_backend.py\",run_name=\"__main__\")'\\''],{input:JSON.stringify(specs),encoding:'\\''utf8'\\'',maxBuffer:64*1024*1024}));
const results=specs.map((s,i)=>{const p=s.params; const js=ev(s.x,{shape:'\\''DSG_LA'\\'',amplitude:1,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss}); return {meta:s.meta,center:p.center,err:Math.max(...js.map((v,j)=>Math.abs(v-out[i][j]))),jsMax:Math.max(...js.map(Math.abs)),pyMax:Math.max(...out[i].map(Math.abs))};}).sort((a,b)=>b.err-a.err);
console.log(JSON.stringify({total:results.length,failures:results.filter(r=>r.err>1e-6).length,worst:results.slice(0,12)},null,2));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 1990ms:
/Users/skyefortier/.matplotlib is not a writable directory
{
  "total": 7,
  "failures": 1,
  "worst": [
    {
      "meta": {
        "center": -5.999999999
      },
      "center": -5.999999999,
      "err": 7.469421625137329,
      "jsMax": 351839274.1965769,
      "pyMax": 351839266.72715527
    },
    {
      "meta": {
        "center": 5.999999999
      },
      "center": 5.999999999,
      "err": 7.450580596923828e-8,
      "jsMax": 176384356.58782282,
      "pyMax": 176384356.58782285
    },
    {
      "meta": {
        "center": 5.999999
      },
      "center": 5.999999,
      "err": 8.731149137020111e-11,
      "jsMax": 176384.1019083924,
      "pyMax": 176384.1019083924
    },
    {
      "meta": {
        "center": 5.999
      },
      "center": 5.999,
      "err": 9.50350909079134e-14,
      "jsMax": 176.121691041411,
      "pyMax": 176.121691041411
    },
    {
      "meta": {
        "center": -6
      },
      "center": -6,
      "err": 6.661338147750939e-16,
      "jsMax": 1,
      "pyMax": 1
    },
    {
      "meta": {
        "center": 6.000000001
      },
      "center": 6.000000001,
      "err": 4.787836793695988e-16,
      "jsMax": 1,
      "pyMax": 1
    },
    {
      "meta": {
        "center": 6
      },
      "center": 6,
      "err": 3.3306690738754696e-16,
      "jsMax": 1,
      "pyMax": 1
    }
  ]
}

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '4317,4343p'; nl -ba tests/js/lineshape_parity.test.js | sed -n '451,475p'; nl -ba tests/test_dsg_outside_centre.py | sed -n '32,56p'; nl -ba docs/findings/2026-09-fit-determinacy.md | sed -n '340,357p'; rg -n 'def load_reference_fits|def discover|\\.proj.zip|test_data' autofit/reference.py tests/autofit/battery_common.py | head -35; sed -n '1570,1650p' fitting.py; rg -n 'unsupported|zero.amplitude|support.*peak|peak.*support' fitting.py | tail -25" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
  4317	    const tt = x1 !== x0 ? (q - x0) / (x1 - x0) : 0;
  4318	    return conv[lo2] + tt * (conv[hi2] - conv[lo2]);
  4319	  };
  4320	  const out = new Array(N);
  4321	  for (let i = 0; i < N; i++) out[i] = interp(beArr[i]);
  4322	  // Normalisation: at the interpolated centre when it lies inside the padded
  4323	  // grid (the server's rule, with its fallbacks); by the curve's maximum when
  4324	  // it lies OUTSIDE it (the server's guarded branch of 2026-09-25 — there the
  4325	  // "value at the centre" was the clamped end value of a 1e-20 tail, and its
  4326	  // rounding sign chose between two unrelated curves).
  4327	  let peakVal;
  4328	  const maxAbs = () => { let mx = 0; for (let i = 0; i < N; i++) mx = Math.max(mx, Math.abs(out[i])); return mx; };
  4329	  if (center < xp[0] || center > xp[nTot - 1]) {
  4330	    peakVal = maxAbs();
  4331	  } else {
  4332	    peakVal = interp(center);
  4333	    if (!(peakVal > 0)) peakVal = maxAbs();
  4334	  }
  4335	  if (!(peakVal > 0)) return new Array(N).fill(0);
  4336	  for (let i = 0; i < N; i++) { const v = out[i] / peakVal; out[i] = Number.isFinite(v) ? v : 0; }
  4337	  return out;
  4338	}
  4339	
  4340	// Compute per-peak intensities across an array of BE values. Special-cases
  4341	// LACX with non-zero m so the Gaussian convolution sees the whole grid, and
  4342	// DSG_LA (every m: the delta branch below 0.001, the convolution above) so
  4343	// the padding, kernel and normalisation see the whole grid.
   451	    const { shape, params } = backendParamsFromRequest(p);
   452	    const beY = backendEval(shape, params, c.x);
   453	    const t0 = Date.now();
   454	    const jsY = evalPeakArray(c.x, p);
   455	    const ms = Date.now() - t0;
   456	    const rel = maxRelDiff(jsY, beY, 1);
   457	    assert.ok(rel < TIGHT_TOL, `${c.label}: max diff ${rel.toExponential(3)} of amplitude (server max ${Math.max(...beY.map(Math.abs)).toExponential(2)})`);
   458	    assert.ok(ms < 2000, `${c.label}: ${ms} ms for one curve — the cost must stay bounded (O(n log n))`);
   459	  });
   460	}
   461	
   462	// KNOWN SERVER LIMIT (not this unit's to change; recorded for the owner):
   463	// just above the 0.001 delta threshold the server's Gaussian kernel can
   464	// UNDERFLOW on a coarse grid — σ = m/2.355 far below the step, so no
   465	// padded-grid sample carries kernel weight (for an even padded length the
   466	// nearest sample is half a step from the centre) — and the server returns
   467	// an all-zero curve for the component. The page mirrors it exactly (a
   468	// vanished curve drawn as vanished, never a curve the server did not fit).
   469	// The zone closes quickly: at 0.1 eV, m = 0.02 is already ordinary.
   470	for (const laM of [0.001, 0.002, 0.02, 0.05]) {
   471	  test(`(D″) DS+G at m = ${laM} on a 0.1 eV grid: page equals server${laM <= 0.002 ? ' (both an all-zero curve — the server kernel underflows; known server limit)' : ''}`, () => {
   472	    const x = Array.from({ length: 120 }, (_, i) => 290 - 0.1 * i);
   473	    const p = { ...basePeak('DSG_LA'), amplitude: 1, center: 284.5, laAlpha: 0.25, laBeta: 0.7, laM };
   474	    const { shape, params } = backendParamsFromRequest(p);
   475	    const beY = backendEval(shape, params, x);
    32	
    33	def test_centre_inside_the_padded_grid_keeps_the_interpolated_centre_normalisation():
    34	    x = (np.arange(200) - 99.5) * 0.05
    35	    lo, hi = _padded(x, 0.05, 0.05)
    36	    for c in (0.0, 0.013, 4.9, -4.9, lo + 1e-9, hi - 1e-9, lo, hi):   # the edges themselves are INSIDE
    37	        y = DSG(x, amplitude=1.0, center=c, alpha=0.25, beta=0.05, m_gauss=0.05)
    38	        # the pre-existing rule: the value interpolated at the centre is 1 (when the
    39	        # centre lies within the DATA grid, that value is on the returned curve)
    40	        if x.min() <= c <= x.max():
    41	            assert abs(float(np.interp(c, x, y)) - 1.0) < 1e-9, c
    42	        assert np.isfinite(y).all()
    43	
    44	
    45	def test_the_branch_boundary_is_the_padded_grid_not_the_data_window():
    46	    """A centre between the data window's edge and the padded grid's edge is
    47	    INSIDE: the old rule still applies there (interp at the centre, with its
    48	    fallbacks), so nothing that ran before changed."""
    49	    x = np.linspace(280, 290, 201)
    50	    lo, hi = _padded(x, 0.7, 0.4)                            # pad = 20 * 0.7 = 14 eV
    51	    c = hi - 0.5
    52	    y = DSG(x, amplitude=3.0, center=c, alpha=0.2, beta=0.7, m_gauss=0.4)
    53	    # clamped-end normalisation: the last (highest-x) data point is nearest the centre
    54	    assert np.isfinite(y).all() and y.max() > 0
    55	    y_out = DSG(x, amplitude=3.0, center=hi + 0.5, alpha=0.2, beta=0.7, m_gauss=0.4)
    56	    assert abs(np.max(np.abs(y_out)) - 3.0) < 1e-12
   340	fit's own bounds (β 0.05–2, m 0.05–4) nonetheless. Not fixed in A03 (scope);
   341	FIXED the same day in `fix-dsg-page-evaluator` after the owner asked whether
   342	Find Peaks emits DS+G: it does (every A- and M-family C 1s candidate's
   343	graphitic main line, β fixed at 0.05, α 0–0.3, m 0.4–1.8), and on that box
   344	the page's area was 5–21 % low for α 0.15–0.3. `dsgConvolved_array` mirrors
   345	the server's padded-grid convolution by the same FFT circular convolution:
   346	< 1e-6 of amplitude (measured ≤ 2e-14 at unit amplitude) across the whole
   347	β/m box on the base grid and seven other grids, and on the reviewers'
   348	reproducers (a centre outside the window, irregular grids, a 0.001 eV
   349	grid); two SERVER limits found on the way (plan §3a: kernel underflow for
   350	m ≤ 0.003 on an even padded length at 0.1 eV gives an all-zero curve;
   351	§3b: a centre far outside the padded grid was normalised by rounding
   352	noise — fixed 2026-09-25 by a guarded branch proven byte-identical for
   353	in-range centres); nothing changed in Find Peaks or the dropdown
   354	(a science decision is not altered to work around a rendering bug —
   355	owner, 2026-09-22). The general lesson repeats §6's: a harness that
   356	evaluates one representative point per shape proves nothing about the range
   357	the optimiser can reach.
tests/autofit/battery_common.py:20:DATA = os.path.join(REPO, "docs", "autofit", "test_data")
tests/autofit/battery_common.py:45:    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
autofit/reference.py:4:Reads the v3 ``.proj.zip`` / ``.proj.json`` project format (the same format
autofit/reference.py:43:    Return the list of raw tab dicts from a ``.proj.zip`` or ``.proj.json``.
autofit/reference.py:51:    if path.suffix == ".zip" or path.name.endswith(".proj.zip"):
autofit/reference.py:305:def load_reference_fits(path: str | Path) -> list[ReferenceFit]:
        if x[i1 - 1] != x[i0]:
            slope = (y[i1 - 1] - y[i0]) / (x[i1 - 1] - x[i0])
        else:
            slope = 0.0
        bg = y[i0] + slope * (x - x[i0])
    elif bg_method in ("none", "flat", "", "manual"):
        bg = np.zeros_like(y)
    else:
        raise ValueError(f"Unknown background method '{background_method}'")

    if bg_inner is not None:
        # Embed the anchor-window integral background into a full-ROI
        # array; flat-hold the endpoint value outside [i0, i1]. In the
        # common case where the user keeps bg anchors at the ROI edges
        # this is a no-op (i0=0, i1=len(y)).
        bg = np.zeros_like(y)
        if len(bg_inner) > 0:
            bg[i0:i1] = bg_inner
            if i0 > 0:
                bg[:i0] = bg_inner[0]
            if i1 < len(y):
                bg[i1:] = bg_inner[-1]

    y_sub = y - bg

    # Poisson weights: σ = √(raw counts), weight = 1/σ
    # Use raw counts (before background subtraction) for uncertainty estimate,
    # since the noise comes from the total photon counting statistics.
    # Floor at 1.0 to avoid division by zero for zero-count channels.
    sigma = np.sqrt(np.maximum(y, 1.0))
    weights = 1.0 / sigma

    # ── Build composite lmfit model ───────────────────────────────────────────
    # Sort so unconstrained (master) peaks come before constrained ones
    ordered = sorted(
        peak_specs,
        key=lambda s: 0 if s.get("constrain_to") is None else 1,
    )

    composite_model: Model | None = None
    all_params = Parameters()

    for spec in ordered:
        shape = spec.get("shape", "pseudo_voigt_gl")
        if shape not in _SHAPE_FUNCS:
            raise ValueError(f"Unknown peak shape '{shape}'. Choices: {AVAILABLE_SHAPES}")
        func = _SHAPE_FUNCS[shape]
        prefix = f"p{spec['id']}_"
        m = Model(func, prefix=prefix)
        p = _make_peak_params(m, spec, prefix, ordered)
        all_params.update(p)
        composite_model = m if composite_model is None else composite_model + m

    if composite_model is None:
        raise RuntimeError("No peaks were built")
    if require_component is not None:
        ids = [str(spec["id"]) for spec in peak_specs]
        if str(require_component) not in ids:
            raise ValueError(f"require_component '{require_component}' is not one of the peaks")
        if len(ids) < 2:
            raise ValueError("require_component needs at least two components")

    # Every random draw below (the perturbed restarts; the populations of the
    # two stochastic methods, which lmfit otherwise takes from numpy's GLOBAL
    # generator) comes from this one seed, so an identical request gives
    # identical DRAWS. (Not an identical Trust-Region result: see CLAUDE.md,
    # "Reproducibility".)
    if caller_seed is not None:
        random_seed = int(caller_seed)
    else:
        random_seed = _request_seed(
            x, y, bg, [spec.get("shape", "pseudo_voigt_gl") for spec in ordered],
            [f"p{spec['id']}_" for spec in ordered], all_params,
            fit_kws=fit_kws, n_perturb=n_perturb)
    # spawn(3) yields the same first two children as spawn(2): adding the
    # scattered-starts stream leaves every existing draw (and its pins) alone.
    perturb_rng, solver_rng, starts_rng = (np.random.default_rng(child)
                                           for child in np.random.SeedSequence(random_seed).spawn(3))
    if isinstance(n_starts, bool) or not isinstance(n_starts, (int, np.integer)) or not 0 <= n_starts <= MAX_N_STARTS:
        raise ValueError(f"n_starts must be an integer between 0 and {MAX_N_STARTS}")

1351:# inflates chi2_with and can mark a real component unsupported; redundancy
1355:# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
1859:        support = _component_support(y_sub, fitted_sub, peak_y, weights, n_free_comp, result.nvarys)

 succeeded in 62470ms:
/Users/skyefortier/.matplotlib is not a writable directory
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Ra6S7ayw' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-LGdg1lLw' (errno=Operation not permitted)
AST identical after removing outside guard: True
extra identity 1 0.0 -1.0 True
extra identity 1 0.0 1.0 True
extra identity 1 0.0 -0.9999999999999999 True
extra identity 1 0.0 0.9999999999999999 True
extra identity 1 0.0 nan True
extra identity 21 -5.0 -6.0 True
extra identity 21 -5.0 6.0 True
extra identity 21 -5.0 -5.999999999999999 True
extra identity 21 -5.0 5.999999999999999 True
extra identity 21 -5.0 nan True
extra identity 21 5.0 -6.0 True
extra identity 21 5.0 6.0 True
extra identity 21 5.0 -5.999999999999999 True
extra identity 21 5.0 5.999999999999999 True
extra identity 21 5.0 nan True
1. box x grids x centres inside the padded grid: 3780 byte-identical, 0 differ (worst |delta| 0)
2. 2000 random draws, centre inside the padded grid: 2000 byte-identical, 0 differ
3. run_fit (leastsq, n_perturb 0) on the C1s Scan with a DS+G Graphite line: byte-identical JSON (43172 bytes)
3. run_fit (leastsq, n_perturb 3) on the C1s Scan with a DS+G Graphite line: byte-identical JSON (43169 bytes)
4. centre 10 eV outside [-5, 5]: old max 5.35e+04, new max 1 (the guarded branch)
4. centre -10 eV, low-BE side: old max 2.61e+03, new max 1 (the guarded branch)

exec
/bin/zsh -lc "sed -n '1355,1417p' fitting.py; sed -n '15,62p' tests/autofit/battery_common.py; sed -n '840,940p' fitting.py; rg -n 'MIN.*DSG|m_gauss.*min|m_gauss.*0.05' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
# F >= 1.1e3 and 3 of 752 components are unsupported (F 0.95-3.9).
SUPPORT_MIN_F = 10.0


def _component_support(y_sub, fitted_sub, comp_y, weights, n_free_comp, n_free_total) -> dict[str, Any]:
    w2 = np.asarray(weights, float) ** 2
    r = np.asarray(y_sub, float) - np.asarray(fitted_sub, float)
    ok = np.isfinite(r) & np.isfinite(comp_y) & np.isfinite(w2)
    chi_with = float(np.sum(w2[ok] * r[ok] ** 2))
    chi_without = float(np.sum(w2[ok] * (r[ok] + np.asarray(comp_y, float)[ok]) ** 2))
    delta = chi_without - chi_with
    p = max(1, int(n_free_comp))
    dof = max(1, int(ok.sum()) - int(n_free_total))
    if delta <= 0:
        f = 0.0
    elif chi_with == 0:
        f = float("inf")
    else:
        f = (delta / p) / (chi_with / dof)
    return {"f": None if not np.isfinite(f) else f, "delta_chi2": delta,
            "supported": bool(delta > 0 and (chi_with == 0 or f >= SUPPORT_MIN_F))}


# ── "Is this component REQUIRED?" — the refit test ───────────────────────────
# `support` (above) holds the OTHER components at their fitted values, so it
# cannot see redundancy under overlap: a component the others could absorb if
# they were refitted still passes. The test for that is the refit itself:
# remove the component, refit the rest from their fitted values under the
# request's own bounds, and compare the fit to the data with and without it:
#     F = ((chi2_without_refit - chi2_with) / p) / (chi2_with / dof)
# p = the component's free parameters, dof = n - nvarys of the full model.
# One extra fit, so it is done only when asked for (Auto-Fit asks for its
# charge-reference anchor: an anchor that is not required must not set the
# energy reference of a whole spectrum). Same threshold as `support`.
def _component_required(fit_reduced, params_full, removed_prefixes, y_sub, weights,
                        chi2_with, n_free_comp, n_free_total) -> dict[str, Any]:
    """``fit_reduced(params)`` is the run's own fitter for the reduced model
    (the same candidate machinery and seeding the fit used, so differential
    evolution's box/refinement and the request seed apply to the refit too).
    ``removed_prefixes`` is the removed component AND everything linked to it,
    transitively. The reduced start is built in dependency order: plain
    parameters first, expressions after, so a child ordered before its parent
    in the request still resolves."""
    kept = [(name, par) for name, par in params_full.items() if not any(name.startswith(r) for r in removed_prefixes)]
    # ALL retained parameters exist before any expression is assigned, so a
    # chain of links in any request order resolves (lmfit evaluates an
    # expression when it is set).
    start = Parameters()
    for name, par in kept:
        start.add(name, value=par.value, min=par.min, max=par.max, vary=par.vary)
    for name, par in kept:
        if par.expr:
            start[name].set(expr=par.expr)
    refit = fit_reduced(start)
    chi2_without = float(refit.chisqr) if refit.chisqr is not None else float("inf")
    delta = chi2_without - chi2_with
    p = max(1, int(n_free_comp))
    dof = max(1, len(y_sub) - int(n_free_total))
    # No tolerance of any kind (Codex rounds 2-3: a floor on the chi-square
    # change relative to the data's power, and then an "exactness" cutoff on
    # the reduced fit, each masked a resolved anchor at high dynamic range —
    # the same lesson as the DE unit). Known limit, accepted: on NOISE-FREE
    # data whose full fit is numerically exact (chi2_with ~ 1e-28) F is not

from autofit.parity import battery_eligible, eval_parity_relmax, refit_record
from autofit.reference import load_reference_fits

REPO = os.path.join(os.path.dirname(__file__), "..", "..")
DATA = os.path.join(REPO, "docs", "autofit", "test_data")
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")

# Default tolerances (C 1s levels).  Per-region batteries may override:
#
# - eval_tol: the residual after each Voigt is evaluated with the mix the
#   server RECORDED for the saved fit (A03, 2026-09-22; before that the
#   twin evaluated every Voigt at 0.3 against curves fitted with eta free,
#   and the ~7e-3 U 4f residual then read as "background-anchor drift" was
#   that mismatch). Measured now: U 4f median 2.0e-7, max 7.9e-4 (on a tab
#   whose LACX lines have m = 0, so not the convolution; the recomputed
#   'smart' background is the candidate, not attributed); Cl 2p <= 6.8e-7;
#   C 1s at the 1e-5 default.
# - fixture_rtol: bounded below by CROSS-PROCESS FP wobble in the LACX
#   convolution path (~6e-6 relative on fitted params; exactly 0.0 within
#   one process).  Simple shapes (C 1s) reproduce at 1e-6.
EVAL_PARITY_TOL = 1e-5
CENTER_DRIFT_TOL_EV = 0.005
REL_DRIFT_TOL = 0.005
FIXTURE_CHI_RTOL = 1e-6
FIXTURE_PARAM_RTOL = 1e-6


def battery_fits(region):
    fits = []
    for zp in sorted(glob.glob(os.path.join(DATA, "*.proj.zip"))):
        for rf in load_reference_fits(zp):
            if battery_eligible(rf, region=region)[0]:
                fits.append(rf)
    return fits


def load_fixture(name):
    with open(os.path.join(FIXTURE_DIR, name)) as f:
        return {(r["project"], r["name"]): r for r in json.load(f)["records"]}


def assert_roster(fits, expected, min_size, min_projects, gen_script):
    assert len(fits) >= min_size, (
        f"battery shrank to {len(fits)} fits (< {min_size}) — reference data "
        "or eligibility rules changed"
    )
    projects = {rf.project for rf in fits}
    fwhm           : float – full width at half max (eV)
    fwhm_min       : float – lower bound   (default 0.1)
    fwhm_max       : float – upper bound   (default 15.0)
    gl_ratio       : float – Lorentzian fraction for *_gl shapes  [0–1]
    asymmetry      : float – high-BE broadening factor for asymmetric_gl [0–1]
    alpha          : float – DS asymmetry index
    constrain_to   : str   – id of master peak (spin‑orbit slave)
    splitting      : float – centre offset from master (eV)
    area_ratio     : float – amplitude = master_amplitude × area_ratio
    fix_fwhm       : bool  – if True, lock FWHM to master value
    """
    shape = spec["shape"]
    p = model.make_params()

    center = spec.get("center", 285.0)
    amp = spec.get("amplitude", 1000.0)
    fwhm = spec.get("fwhm", 1.5)
    asymmetry = spec.get("asymmetry", 0.0)

    def _set(name, value, min_=None, max_=None, expr=None, vary=True):
        full = prefix + name
        if full not in p:
            return
        if not vary and expr is None:
            # A HELD parameter is held at the value requested. The bounds are
            # the optimiser's search limits; lmfit clips a value outside them
            # even when it does not vary, which silently changed a locked
            # DS+G m of 0 (the page's delta-kernel branch, drawn without
            # convolution) into 0.05 (a convolved fit) — A03 Codex round 2's
            # locked-at-bounds round trips. Widen the limit to the value.
            if min_ is not None and value < min_:
                min_ = value
            if max_ is not None and value > max_:
                max_ = value
        p[full].set(value=value)
        if expr is not None:
            p[full].expr = expr
            p[full].vary = False
        else:
            if min_ is not None:
                p[full].min = min_
            if max_ is not None:
                p[full].max = max_
            p[full].vary = vary

    # Constrain to a master peak (spin‑orbit doublet)?
    master_id = spec.get("constrain_to")
    if master_id is not None:
        # Find the master spec to get its prefix
        master_spec = next((s for s in all_specs if s["id"] == master_id), None)
        if master_spec is None:
            raise ValueError(f"Master peak '{master_id}' not found for spin‑orbit constraint")
        m_prefix = f"p{master_spec['id']}_"
        splitting = float(spec.get("splitting", 0.0))
        area_ratio = float(spec.get("area_ratio", 1.0))

        _set("center", center, expr=f"{m_prefix}center + {splitting}")
        _set("amplitude", amp, expr=f"{m_prefix}amplitude * {area_ratio}")
        _set("fwhm", fwhm, expr=f"{m_prefix}fwhm" if spec.get("fix_fwhm", True) else None,
             min_=spec.get("fwhm_min", 0.1), max_=spec.get("fwhm_max", 15.0))
        if shape in ("pseudo_voigt_gl", "asymmetric_gl"):
            _set("gl_ratio", spec.get("gl_ratio", 0.3),
                 expr=f"{m_prefix}gl_ratio" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "asymmetric_gl":
            _set("asymmetry", asymmetry,
                 expr=f"{m_prefix}asymmetry" if spec.get("fix_fwhm", True) else None,
                 min_=spec.get("asymmetry_min", 0.0),
                 max_=spec.get("asymmetry_max", 1.0))
        if shape == "doniach_sunjic":
            _set("alpha", spec.get("alpha", 0.1),
                 expr=f"{m_prefix}alpha" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=0.5)
            _set("gamma_asym", spec.get("gamma_asym", 0.0),
                 expr=f"{m_prefix}gamma_asym" if spec.get("fix_fwhm", True) else None,
                 min_=0.0, max_=1.0)
        if shape == "ds_g":
            fix = spec.get("fix_fwhm", True)
            _set("alpha",   spec.get("alpha",   0.10), expr=f"{m_prefix}alpha"   if fix else None, min_=0.0,  max_=0.49)
            _set("beta",    spec.get("beta",    0.3),  expr=f"{m_prefix}beta"    if fix else None, min_=0.05, max_=2.0)
            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
        if shape == "la_casaxps":
            fix = spec.get("fix_fwhm", True)
            _set("alpha", spec.get("alpha", 1.0),
                 expr=f"{m_prefix}alpha" if fix else None,
                 min_=0.1, max_=5.0)
            _set("beta",  spec.get("beta",  1.0),
                 expr=f"{m_prefix}beta" if fix else None,
                 min_=0.1, max_=5.0)
            _set("m",     spec.get("m",    50.0),
                 expr=f"{m_prefix}m" if fix else None,
                 min_=0.0, max_=499.0)
        return p

    # Free (master or unconstrained) peak
    # Non-DS+G peaks (satellites, etc.) get a default ±2 eV constraint to prevent
    # the optimizer from drifting to physically unreasonable positions.
    c_min = spec.get("center_min")
    c_max = spec.get("center_max")
    if shape != "ds_g" and c_min is None:
        c_min = center - 2.0
920:            _set("m_gauss", spec.get("m_gauss", 0.4),  expr=f"{m_prefix}m_gauss" if fix else None, min_=0.0,  max_=4.0)
969:        _set("m_gauss", spec.get("m_gauss", 0.4),  min_=0.05, max_=4.0,

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();
const specs=[];

for(const c of [56,55.999999999,55.999999,56.000000001]) specs.push({shape:'\\''ds_g'\\'',x:Array.from({length:121},(_,i)=>-5+.5*i),params:{amplitude:1,center:c,alpha:.49,beta:.05,m_gauss:.05},meta:{center:c}});
const out=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'', '\\''import tempfile,runpy; tempfile.tempdir=\"/tmp\"; runpy.run_path(\"tests/js/lineshape_parity_backend.py\",run_name=\"__main__\")'\\''],{input:JSON.stringify(specs),encoding:'\\''utf8'\\'',maxBuffer:64*1024*1024}));
const results=specs.map((s,i)=>{const p=s.params; const js=ev(s.x,{shape:'\\''DSG_LA'\\'',amplitude:1,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss}); return {meta:s.meta,center:p.center,err:Math.max(...js.map((v,j)=>Math.abs(v-out[i][j]))),jsMax:Math.max(...js.map(Math.abs)),pyMax:Math.max(...out[i].map(Math.abs))};}).sort((a,b)=>b.err-a.err);
console.log(JSON.stringify({total:results.length,failures:results.filter(r=>r.err>1e-6).length,worst:results.slice(0,12)},null,2));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 2048ms:
/Users/skyefortier/.matplotlib is not a writable directory
{
  "total": 4,
  "failures": 1,
  "worst": [
    {
      "meta": {
        "center": 56
      },
      "center": 56,
      "err": 403860815767457540,
      "jsMax": 403860815767457540,
      "pyMax": 1
    },
    {
      "meta": {
        "center": 55.999999999
      },
      "center": 55.999999999,
      "err": 3.2782554626464844e-7,
      "jsMax": 176384984.05135277,
      "pyMax": 176384984.05135244
    },
    {
      "meta": {
        "center": 55.999999
      },
      "center": 55.999999,
      "err": 3.2014213502407074e-10,
      "jsMax": 176384.10238322598,
      "pyMax": 176384.10238322566
    },
    {
      "meta": {
        "center": 56.000000001
      },
      "center": 56.000000001,
      "err": 7.771561172376096e-16,
      "jsMax": 1,
      "pyMax": 1
    }
  ]
}

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 node -e '
const fs=require('\\''fs'\\''), cp=require('\\''child_process'\\'');
const html=fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'');
const block=html.match(/function gaussian\\(x, center, fwhm\\) \\{[\\s\\S]*?\\nfunction evalPeakArray\\(beArr, p\\) \\{[\\s\\S]*?\\n\\}/)[0];
const ev=new Function(block+'\\''; return evalPeakArray;'\\'')();
const specs=[];

for(const alpha of [0,.25,.49]) for(const beta of [.05,.7,2]) for(const m of [.001,.05,.4,2,4]) specs.push({shape:'\\''ds_g'\\'',x:Array.from({length:500},(_,i)=>391.8-5+.02*i),params:{amplitude:1,center:391.8,alpha,beta,m_gauss:m},meta:{alpha,beta,m}});
const out=JSON.parse(cp.execFileSync('\\''/Users/skyefortier/xps-app/venv/bin/python3'\\'',['\\''-c'\\'', '\\''import tempfile,runpy; tempfile.tempdir=\"/tmp\"; runpy.run_path(\"tests/js/lineshape_parity_backend.py\",run_name=\"__main__\")'\\''],{input:JSON.stringify(specs),encoding:'\\''utf8'\\'',maxBuffer:64*1024*1024}));
const results=specs.map((s,i)=>{const p=s.params; const js=ev(s.x,{shape:'\\''DSG_LA'\\'',amplitude:1,center:p.center,laAlpha:p.alpha,laBeta:p.beta,laM:p.m_gauss}); return {meta:s.meta,center:p.center,err:Math.max(...js.map((v,j)=>Math.abs(v-out[i][j]))),jsMax:Math.max(...js.map(Math.abs)),pyMax:Math.max(...out[i].map(Math.abs))};}).sort((a,b)=>b.err-a.err);
console.log(JSON.stringify({total:results.length,failures:results.filter(r=>r.err>1e-6).length,worst:results.slice(0,1)},null,2));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c '
import tempfile; tempfile.tempdir=\"/tmp\"
from pathlib import Path
from collections import Counter
from autofit.reference import load_reference_fits
c=Counter()
for p in Path(\"docs/autofit/test_data\").glob(\"*.proj.zip\"):
 for r in load_reference_fits(p):
  c.update(k.get(\"shape\") for k in r.peaks)
print(c)
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 203ms:
Counter({'GL': 232, 'Voigt': 110, 'LACX': 108, 'asym-GL': 64, 'Gaussian': 16})

 succeeded in 2237ms:
/Users/skyefortier/.matplotlib is not a writable directory
{
  "total": 45,
  "failures": 0,
  "worst": [
    {
      "meta": {
        "alpha": 0,
        "beta": 0.05,
        "m": 4
      },
      "center": 391.8,
      "err": 5.784261958297066e-14,
      "jsMax": 1.000000000003924,
      "pyMax": 1.0000000000039129
    }
  ]
}

codex
The identity proof reproduced: all 5,780 cases matched `main`, as did both full fit JSON responses. Exact endpoints, NaN centres, descending grids and one-point grids also retained identical server output. The failure is in page parity: a centre just inside the padded edge can exceed the `1e-6` tolerance too. I’m finishing the documentation checks and test summary.

exec
/bin/zsh -lc "git status --short; nl -ba docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md | tail -20; rg --files tests/autofit | rg 'parity|region|b1s|cl2p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9vN0YHsg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iBaAB6tJ' (errno=Operation not permitted)
?? docs/autofit/codex/dsg_page_evaluator_r3_verdict_runA.md
?? docs/autofit/codex/dsg_page_evaluator_r3_verdict_runB.md
?? docs/autofit/codex/dsg_page_evaluator_recheck2_prompt.txt
   200	output there is decided by the sign of rounding noise); MINOR — the
   201	precision figures were quoted at the harness amplitude (at unit amplitude
   202	1.95e-14 base grid, 5.8e-14 at 0.02 eV; corrected above); MINOR — the
   203	underflow zone's description (corrected in §3a: even lengths only, up to
   204	m = 0.003 on 120 points). **Stopped here per the owner's rule (a third
   205	round): the remaining MAJOR is a server conditioning limit outside this
   206	unit, documented in §3b with the fix that belongs to the server;
   207	everything physically reachable on the page is a hard 1e-6 assertion.**
   208	The interim red notice was NOT added: its wording ("the page's curve and
   209	area for this shape are not yet exact") would now be false. Decision to
   210	the owner.
   211	
   212	**Owner decision (2026-09-25): option 2 with a hard condition** — the
   213	server change as a new guarded branch, byte-identical for in-range centres
   214	on the committed battery, else stop; then mirror on the page and one Codex
   215	round; no interim notice; §3a documented and left (it degrades honestly:
   216	an all-zero curve reads as a zero-amplitude component, which step (b)
   217	flags as not supported by the data). Done as §3b records. Logged
   218	separately, not urgent: the ~110 s DS+G Run Fit (§5a) — likely the same
   219	evaluation-budget question as the Find Peaks speed item.
tests/autofit/test_b1s_cl2p_batteries.py
tests/autofit/test_u4f_parity_gate.py
tests/autofit/test_cl2p_freewidth.py
tests/autofit/test_u4f_parity_battery.py
tests/autofit/fixtures/b1s_battery_expected.json
tests/autofit/fixtures/cl2p_battery_expected.json
tests/autofit/test_region_provenance_honesty.py
tests/autofit/test_c1s_parity_gate.py
tests/autofit/test_b1s_cl2p_parity_gates.py
tests/autofit/test_c1s_parity_battery.py

exec
/bin/zsh -lc "ps -axo pid,ppid,etime,command | rg 'node -e|python3' | cut -c 1-220" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 0ms:
zsh:1: operation not permitted: ps

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c 'import tempfile; tempfile.tempdir='\\''/tmp'\\''
import pytest
raise SystemExit(pytest.main(['\\''-q'\\'','\\''-s'\\'','\\''-p'\\'','\\''no:cacheprovider'\\'','\\''tests/autofit/test_b1s_cl2p_batteries.py'\\'']))'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 2786ms:
................
16 passed in 2.33s

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python3 -c '
import tempfile; tempfile.tempdir=\"/tmp\"
import numpy as np, fitting, warnings
warnings.filterwarnings(\"ignore\")
for n in (120,121):
 x=290-.1*np.arange(n)
 for m in (.001,.003,.00305):
  y=fitting._ds_g_dscore_gauss(x,1,284.5,.25,.7,m)
  print(n,m,float(np.max(abs(y))))
print(\"zero component support:\",fitting._component_support(np.ones(120),np.ones(120),np.zeros(120),np.ones(120),3,6))
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator
 succeeded in 1893ms:
/Users/skyefortier/.matplotlib is not a writable directory
120 0.001 0.0
120 0.003 0.0
120 0.00305 1.0163843751732495
121 0.001 1.0332685438058629
121 0.003 1.0332685438058629
121 0.00305 1.0332685438058629
zero component support: {'f': 0.0, 'delta_chi2': 0.0, 'supported': False}

 succeeded in 170031ms:
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 396 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 3.642742
  type: 'test'
  ...
1..396
# tests 396
# suites 0
# pass 391
# fail 0
# cancelled 0
# skipped 0
# todo 5
# duration_ms 170057.410102

codex
The review has one remaining major finding and two documentation minors. All 137 targeted Python tests passed, the underflow boundary matched §3a, and an all-zero component was marked unsupported. The no-notice decision is recorded accurately. The full JS rerun is still running; its result won’t change the reproduced padded-edge parity failure.

codex
- **MAJOR — normalization remains unstable at and inside the padded boundary.** [templates/index.html:4332](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/templates/index.html:4332). Reproducer: `x[i] = -5 + 0.5*i`, 121 points, amplitude `1`, centre `56`, α `0.49`, β `0.05`, m `0.05`. The padded grid ends exactly at `56`, so both implementations correctly retain the old branch. **Server maximum: `1`; page maximum: `4.0386081576745754e17`.** The endpoint normalization still depends on FFT rounding sign. This also affects strictly interior centres: on 21 points spanning `[-5,5]`, centre `-5.999999999` with the same parameters gives maximum page/server difference **`7.4694` amplitudes**. The identity proof compares old/new server output, so it cannot catch this page-parity failure. Widening the guard would violate the owner’s preservation condition.

- **MINOR — precision correction remains incomplete.** [docs/findings/2026-09-fit-determinacy.md:346](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/docs/findings/2026-09-fit-determinacy.md:346) still claims measured error ≤ `2e-14` across the base and seven additional grids. On the 500-point, `0.02 eV` grid centred at `391.8`, unit amplitude, α `0`, β `0.05`, m `4`, I reproduced **`5.7843e-14`**. The plan’s separate bounds are accurate; this summary is not.

- **MINOR — verification text still denies the server change.** [docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md:129](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md:129), repeated at line 147, says “no Python change” and cites an earlier run on “the same server code.” A reviewer relying on that section receives incorrect validation provenance for this commit.

Verified: the strict guard and preserved `else` satisfy the server-isolation requirement. Removing the new guard yields an identical function AST to `main`. All 5,780 identity cases and both fit JSON comparisons reproduced; additional exact-edge, NaN, descending and one-point cases retained byte-identical server output. Caller and seed inspection found no separate in-range change; the 530 committed peak records contain no DS+G.

Tests: **137 targeted Python tests passed; JS: 391 passed, 5 todo, 0 failed**, using an in-memory startup adjustment for the read-only environment. §3a’s underflow characterization and unsupported-component behavior checked out. The owner’s no-interim-notice decision is accurately recorded. No files changed.

**VERDICT: NO-GO**
tokens used
80,974
- **MAJOR — normalization remains unstable at and inside the padded boundary.** [templates/index.html:4332](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/templates/index.html:4332). Reproducer: `x[i] = -5 + 0.5*i`, 121 points, amplitude `1`, centre `56`, α `0.49`, β `0.05`, m `0.05`. The padded grid ends exactly at `56`, so both implementations correctly retain the old branch. **Server maximum: `1`; page maximum: `4.0386081576745754e17`.** The endpoint normalization still depends on FFT rounding sign. This also affects strictly interior centres: on 21 points spanning `[-5,5]`, centre `-5.999999999` with the same parameters gives maximum page/server difference **`7.4694` amplitudes**. The identity proof compares old/new server output, so it cannot catch this page-parity failure. Widening the guard would violate the owner’s preservation condition.

- **MINOR — precision correction remains incomplete.** [docs/findings/2026-09-fit-determinacy.md:346](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/docs/findings/2026-09-fit-determinacy.md:346) still claims measured error ≤ `2e-14` across the base and seven additional grids. On the 500-point, `0.02 eV` grid centred at `391.8`, unit amplitude, α `0`, β `0.05`, m `4`, I reproduced **`5.7843e-14`**. The plan’s separate bounds are accurate; this summary is not.

- **MINOR — verification text still denies the server change.** [docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md:129](/Users/skyefortier/xps-app/.claude/worktrees/fix-dsg-page-evaluator/docs/superpowers/plans/2026-09-22-dsg-page-evaluator.md:129), repeated at line 147, says “no Python change” and cites an earlier run on “the same server code.” A reviewer relying on that section receives incorrect validation provenance for this commit.

Verified: the strict guard and preserved `else` satisfy the server-isolation requirement. Removing the new guard yields an identical function AST to `main`. All 5,780 identity cases and both fit JSON comparisons reproduced; additional exact-edge, NaN, descending and one-point cases retained byte-identical server output. Caller and seed inspection found no separate in-range change; the 530 committed peak records contain no DS+G.

Tests: **137 targeted Python tests passed; JS: 391 passed, 5 todo, 0 failed**, using an in-memory startup adjustment for the read-only environment. §3a’s underflow characterization and unsupported-component behavior checked out. The owner’s no-interim-notice decision is accurately recorded. No files changed.

**VERDICT: NO-GO**
