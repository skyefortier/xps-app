# The `caM` unit — LA's m continuous on the page and in the local engine (2026-09-25)

Branch `fix-cam-continuous` off main `3ea3b8b`. Queued by the owner after
A03 and the fail-open sweep ("Then the caM clamp"). The record defined the
unit as two halves (A03 plan §5/§6; CLAUDE.md): the page draws LA with m
ROUNDED to an integer 2m+1 kernel while the server fits m continuously, and
the local engine rounds m in its clamp and carries it at its start.

## 1. Contract (final, after Codex round 2)

The server's continuous m is deliberate (`_la_casaxps_true`: "m flows
through continuously so lmfit's finite-difference Jacobian in m is
non-singular" — rounding made the function locally constant in m and
poisoned the covariance of every other parameter). So:

- **The page DRAWS what the server fits:** it mirrors the continuous-m
  kernel exactly, as it does DS+G's (2026-09-22). Nothing on the server
  changes.
- **The local engine HOLDS m, exactly.** It used to make a free `caM` free
  and then round it in its clamp, silently fitting a fractional 8.2 as 8.
  Freeing it properly was tried and withdrawn (§7): LA's curve is
  DISCONTINUOUS in m — the kernel half-width max(1, ⌈3.5 m/3⌉) jumps at
  every m = 6k/7 — and a smooth optimiser cannot fit a discontinuous
  parameter; two Codex rounds each found new reachable failures of the
  patches. Fitting m in Batch Fit, if wanted, is a derivative-free
  one-dimensional search — its own unit.

## 2. Measured before (`scripts/lacx_page_vs_server.js`)

All 108 LA components in the seven committed projects, at their saved
parameters on their tab's ROI grid (106 carry a fractional, server-fitted
m; 107 are unlocked):

| | before | after |
|---|---:|---:|
| max page − server, of amplitude | median 0.29 %, max 0.97 % | max 7.4e-16 |
| area, page vs server | median 0.33 %, max 1.18 % | max 5.6e-14 % |

`docs/findings/cam/lacx_page_vs_server_{before,after}.json`. The "before"
column is also what a student sees change on opening a saved U 4f project:
the page's LA areas move by 0.33 % at the median, 1.2 % at most, to the
curve the server actually fitted.

## 3. Sites

| # | site | before | after |
|---|---|---|---|
| 1 | `laTrueCasaXPS_array` (+ `_laKernelHalf`, the kernel half-width it uses) | integer m = round(caM), kernel 2m+1, σ = m/3, own convolution and peak search | literal mirror of `_la_casaxps_true`: m clamped to [0, 499], continuous σ = m/3, half-width max(1, ⌈3.5σ⌉), unit-sum kernel, `np.convolve(base, k, 'same')` + the server's trim when the kernel is longer than the grid (index formula pinned against numpy on 3,000 random (N, K)), normalisation at `argmin |ε|` (first minimum), fallback max, m < 1e-3 = bare base curve |
| 2 | `evalPeakArray` LA gate | array path only when `Math.round(caM) > 0` | every LA through the array path (it handles m < 1e-3 itself) |
| 3 | `laTrueCasaXPS` (scalar) | base curve, m ignored | unchanged; comment corrected; parity guard (C) proves no shipped caller |
| 4 | m input (`renderPeakForm`) | `Math.round(caM)`, step 1, "Integer 0–499" | the value to 2 dp, step 0.1, "continuous" |
| 5 | `runFitLocal` free-parameter block + clamp | a free `caM` made free, then `Math.round`ed by the clamp | `caM` never made free: held at its exact value |
| 6 | `runFitLocal` `isDiscrete` (Jacobian skip, sensitivity, certificate, dof, per-component support p) | `caM` discrete → never moved, not a dof | nothing discrete (no free parameter is); m is not a dof because it is not free |
| 7 | local-fit caveat (`_localFitDetail`, `_LOCALFIT_TOOLTIP`, fallback banner) | "differ … for LA components (m held at its start locally)" | unchanged — true again, and now exactly (§4) |
| 8 | `peakToBackendSpec` (`m`, `fix_m`), `_applyBackendParams` (writes `par.m`), exports (`p.caM`), Find Peaks mapping (`o.caM = p.m`), `syncKeys` / `LINK_SYNC_KEYS`, `_STARTS_MODEL_FIELDS`, Python twins | carry the value as is | unchanged (they already carried the fractional server value) |
| 9 | defaults (`caM: 50`, `fixCaM: true`; server `fix_m` default true) | — | unchanged |

## 4. The re-measurement (`scripts/local_server_gap.js` → `docs/findings/cam/local_server_gap_after_cam.json`)

W1's 18 targets, local engine (m held exactly) vs server from the same
scaled start; the control arm is the server with LA's m held at the SAME
exact value.

| U 4f target | local vs server, m free (χ²ᵣ; max Δarea) | local vs server, m held |
|---|---|---|
| Scan_0, 2, 3, 7 | −0.2 to +0.6 %; ≤ 2.07 % | +0.1 to +0.8 %; ≤ 0.60 %, ≤ 0.04 pp |
| Scan_1 | +1.4 %; 2.22 % | +1.7 %; 2.12 %, 0.12 pp |
| Scan_4 | +10.1 %; 8.64 % | +5.4 %; 5.34 %, 0.19 pp |
| Scan_5 | +10.4 %; 6.81 % | +9.7 %; 5.49 %, 0.24 pp |
| Scan_6 | −4.8 %; 8.62 % | +1.1 %; 1.60 %, 0.07 pp |
| Scan_8 | +12.8 %; 8.47 % | +13.2 %; 8.23 %, 0.32 pp |

C 1s unchanged (8 of 9 within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is
findings §2). The picture is A03's: where the server holds m too, the
engines agree except on the three worse-minimum targets (Scan_4/5/8, the
local engine 5–13 % above); on Scan_6 the whole gap is m moving on the
server. The "starting point" label stays, on both grounds, and the caveat
("differ … for LA components (m held at its start locally) or where the
model has several minima") is true — now exactly, since m is held at its
value rather than rounded.

A note on the withdrawn attempt: with m free and the piece-confined
derivative, the local engine reached the same minimum as the server on
Scan_6's neighbourhood and even a lower one (−5.7 %) — the gain was real,
but the method was not sound on a discontinuous parameter (§7).

## 5. Verification

- `tests/js/lineshape_parity.test.js`: (A) LACX m > 0 and (D) LACX m > 0
  (fractional m, the 1e-3 threshold, 499) are hard assertions; new (D‴)
  sweeps the LA box on six more grids incl. 9- and 2-point grids (kernel
  longer than the grid). `tests/js/lineshape_roundtrip.test.js`: no shape
  has a known gap; LA m locked at 499 and at a fractional 8.66 round-trip
  with the curve compared. `tests/js/local_lm_descent.test.js`: the local
  engine holds m exactly (a fractional 5.37 stays 5.37, free or locked, not
  a dof); the four Codex reproducers of rounds 1–2 converge. JS suite
  (final): 422 tests, 420 pass, 2 todo (the scalar evaluators of the two
  convolved shapes, by design).
- Browser check (`browser_check_cam.py`, dev :5151): committed
  UCl4-graphite U4f Scan loads with m 8.2 shown as "8.2"; Run Fit → LA
  drawn vs fitted 1.1e-13 of amplitude (was 5.6e-3), Results area equal to
  the server curve's (was −0.66 %); Batch Fit onto U4f Scan_1 converges;
  no page errors. Re-run on the final commit: Batch Fit onto U4f Scan_1
  converges and keeps m at exactly 6.4945… (the value it was given); LA
  drawn vs fitted 1.1e-13; areas exact.
- Python suite: 993 passed, 7 skipped (on the round-0 commit df388ce; the
  round-1 change is page-only).

## 6. Release-note line

LA(α, β, m) components are now drawn, integrated and exported with the same
continuous m the server fits (the page rounded it to a whole number of
points): opening a saved U 4f project moves an LA component's area by
0.33 % at the median and 1.2 % at most, to the curve that was actually
fitted. m is shown to 0.01. Batch Fit keeps m exactly at the value it is
given (it used to round it to a whole number).

## 7. Codex rounds

**Round 1 (`docs/autofit/codex/cam_continuous_verdict_run{A,B}.md`):
NO-GO ×2, one finding, the same in both.** MAJOR — LA's curve JUMPS where
the kernel half-width max(1, ⌈3.5 m/3⌉) changes (m = 6k/7), so a
central-difference step for m that straddles a jump is not a derivative;
with m now free, local fits that converge with m held stalled and failed
(run A: 201 points at 0.03 eV, m 48; run B: 61 points at 0.05 eV,
m 18/7 − 0.001). lmfit escapes it only because its step is ~1e-8. Fixed
in the local engine's Jacobian, not in the mirror: one shared
`_laKernelHalf(m)` (used by the evaluator and the Jacobian, so they cannot
disagree) and a difference that stays inside the current piece —
one-sided when one side crosses, the step halved when both would. Both
reproducers are regression tests (they fail on df388ce, pass now; freeing
m never ends worse than holding it). `scripts/cam_transition_sweep.js`
(→ `docs/findings/cam/transition_sweep.json`): 210 local LA fits started
around 7 transitions × 5 offsets × 3 grid steps × 2 starts — 0 fail with m
free, 0 with m held, 0 end worse free than held. The §4 re-measurement,
re-run on the fixed engine, is unchanged to the digits quoted.

**Round 2 (`cam_continuous_r2_verdict_run{A,B}.md`): NO-GO ×2.** Round 1's
reproducers pass, but: (1) MAJOR — the LM STEP still crosses the jumps: a
fit started exactly on a transition (m = 18/7) with amplitude and m free
exhausts damping (every positive step, down to Δm ≈ 3e-12, lands across
the jump and raises χ²); 17 failures in 540 near-truth starts. (2) MAJOR —
a regression introduced by round 1's fix: next to the no-convolution
threshold (noiseless m = 0 data, start m = 0.001) the piece-confined
derivative is zero, SENS_MIN fails the fit before the certificate can
reach m = 0 (main converges). Both are consequences of fitting a
discontinuous parameter with a smooth method; each patch had uncovered the
next reachable failure — the pattern of the DE and anchor units. So the
free-m half was WITHDRAWN rather than patched a third time: the local
engine holds m exactly (§1), the piece-confined derivative is removed,
all four reproducers are regression tests that converge, and the control
arm of `local_server_gap.js` now holds the server's m at the same exact
value. The page half (the user-facing defect) was clean in both rounds.

**Round 3 (`cam_continuous_r3_verdict_run{A,B}.md`): GO ×2.** Both
confirmed caM never enters the local parameter vector, clamp, derivative
or certificate and counts neither as a dof nor in component support;
linked children take the parent's exact value; Batch Fit's copy and
scaling preserve it; the 108-component rerun and the §4 table match their
JSON. Two documentation MINORs fixed after the GO: `_laKernelHalf`'s
comment still described the withdrawn derivative, and
`scripts/cam_transition_sweep.js` labelled its arms free/held although
both now hold m — relabelled unlocked/locked, its round-1 free-m result
marked historical. Python suite on the final commit: 993 passed, 7
skipped.

## 8. Owner decisions at deploy (2026-09-25)

- Deploy approved; withdrawing the fit-m half after two failed rounds "was
  the right call".
- Batch Fit fitting m (a derivative-free search): DECLINED — it would only
  close Scan_6; Scans 4/5/8 are a worse-minimum problem, so the
  starting-point label stays either way.

