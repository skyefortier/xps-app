# The `caM` unit — LA's m continuous on the page and in the local engine (2026-09-25)

Branch `fix-cam-continuous` off main `3ea3b8b`. Queued by the owner after
A03 and the fail-open sweep ("Then the caM clamp"). The record defined the
unit as two halves (A03 plan §5/§6; CLAUDE.md): the page draws LA with m
ROUNDED to an integer 2m+1 kernel while the server fits m continuously, and
the local engine rounds m in its clamp and carries it at its start.

## 1. Contract

The server's continuous m is deliberate (`_la_casaxps_true`: "m flows
through continuously so lmfit's finite-difference Jacobian in m is
non-singular" — rounding made the function locally constant in m and
poisoned the covariance of every other parameter). So, as for DS+G
(2026-09-22), the PAGE MIRRORS THE SERVER; nothing on the server changes.

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
| 1 | `laTrueCasaXPS_array` | integer m = round(caM), kernel 2m+1, σ = m/3, own convolution and peak search | literal mirror of `_la_casaxps_true`: m clamped to [0, 499], continuous σ = m/3, half-width max(1, ⌈3.5σ⌉), unit-sum kernel, `np.convolve(base, k, 'same')` + the server's trim when the kernel is longer than the grid (index formula pinned against numpy on 3,000 random (N, K)), normalisation at `argmin |ε|` (first minimum), fallback max, m < 1e-3 = bare base curve |
| 2 | `evalPeakArray` LA gate | array path only when `Math.round(caM) > 0` | every LA through the array path (it handles m < 1e-3 itself) |
| 3 | `laTrueCasaXPS` (scalar) | base curve, m ignored | unchanged; comment corrected; parity guard (C) proves no shipped caller |
| 4 | m input (`renderPeakForm`) | `Math.round(caM)`, step 1, "Integer 0–499" | the value to 2 dp, step 0.1, "continuous" |
| 5 | `runFitLocal` clamp | `Math.round(v)` | continuous clamp to [0, 499] |
| 6 | `runFitLocal` `isDiscrete` (Jacobian skip, sensitivity, certificate, dof, per-component support p) | `caM` discrete → never moved, not a dof | nothing discrete: m is optimised, certified and counted |
| 7 | local-fit caveat (`_localFitDetail`, `_LOCALFIT_TOOLTIP`, fallback banner) | "differ … for LA components (m held at its start locally)" | "differ … where the model has several minima" (§4) |
| 8 | `peakToBackendSpec` (`m`, `fix_m`), `_applyBackendParams` (writes `par.m`), exports (`p.caM`), Find Peaks mapping (`o.caM = p.m`), `syncKeys` / `LINK_SYNC_KEYS`, `_STARTS_MODEL_FIELDS`, Python twins | carry the value as is | unchanged (they already carried the fractional server value) |
| 9 | defaults (`caM: 50`, `fixCaM: true`; server `fix_m` default true) | — | unchanged |

## 4. The re-measurement (`scripts/local_server_gap.js` → `docs/findings/cam/local_server_gap_after_cam.json`)

W1's 18 targets, local engine vs server from the same scaled start.

| U 4f target | local χ²ᵣ vs server, A03 | after this unit | max Δarea, A03 → after |
|---|---:|---:|---:|
| Scan_0, 2, 3, 7 (same minimum) | −0.2 to +0.5 % | +0.1 to +0.8 % | ≤ 1.74 % → ≤ 0.34 % |
| Scan_1 | +1.3 % | +1.6 % | 1.95 % → 1.57 % |
| Scan_4 | +9.6 % | +4.9 % | 8.32 % → 4.30 % |
| Scan_5 | +10.1 % | +9.2 % | 6.65 % → 5.25 % |
| Scan_6 | −5.0 % | −5.7 % | 8.88 % → 11.25 % |
| Scan_8 | +12.7 % | +13.0 % | 8.31 % → 7.91 % |

C 1s unchanged (8 of 9 within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is
findings §2). On the four U 4f targets where both engines reach the same
minimum every component now agrees within 3.0 meV, 0.49 % FWHM, 0.34 %
area, 0.02 pp.

Reading: the `caM` half of the gap is closed — on Scan_6, the one target
A03's control arm attributed to the clamp, the local engine now MOVES m and
lands 5.7 % BELOW the server (the server, m free, stops in a worse
minimum; with m held it reaches 2.629, the local 2.639). Everything left is
a different minimum, in BOTH directions: the local engine above the server
on Scan_4/5/8 (+4.9 to +13 %), below it on Scan_6. That is the
worse-minimum finding A03 recorded, not a model difference.

**The "starting point" label.** The owner's condition was a re-measurement
after the `caM` clamp and the worse-minimum work. The first is done; the
second is not, and three of nine U 4f targets still land in a worse local
minimum. Recommendation: the label STAYS; its wording now names only
"several minima" and the absent uncertainties. Owner's call.

## 5. Verification

- `tests/js/lineshape_parity.test.js`: (A) LACX m > 0 and (D) LACX m > 0
  (fractional m, the 1e-3 threshold, 499) are hard assertions; new (D‴)
  sweeps the LA box on six more grids incl. 9- and 2-point grids (kernel
  longer than the grid). `tests/js/lineshape_roundtrip.test.js`: no shape
  has a known gap; LA m locked at 499 and at a fractional 8.66 round-trip
  with the curve compared. `tests/js/local_lm_descent.test.js`: the
  W1-round-1 test pinning "held caM is not a dof" replaced by one pinning
  continuous recovery of m (8.66 from 5), a locked m unmoved, and one more
  dof when free. JS suite: 418 tests, 416 pass, 2 todo (the scalar
  evaluators of the two convolved shapes, by design).
- Browser check (`browser_check_cam.py`, dev :5151): committed
  UCl4-graphite U4f Scan loads with m 8.2 shown as "8.2"; Run Fit → LA
  drawn vs fitted 1.1e-13 of amplitude (was 5.6e-3), Results area equal to
  the server curve's (was −0.66 %); Batch Fit onto U4f Scan_1 converges and
  moves m (6.49 → 7.66); no page errors.
- Python suite: recorded below.

## 6. Release-note line

LA(α, β, m) components are now drawn, integrated and exported with the same
continuous m the server fits (the page rounded it to a whole number of
points): opening a saved U 4f project moves an LA component's area by
0.33 % at the median and 1.2 % at most, to the curve that was actually
fitted. Batch Fit now fits m instead of holding it. m is shown to 0.01.

## 7. Codex rounds

(filled in as they run)
