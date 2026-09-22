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

### 3b. Server limit found in round 2 (not this unit's to change)

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
there), and the server's own output there is arbitrary. The fix belongs to
the server: normalise by the maximum whenever the centre lies outside the
padded grid — after which the page mirrors it trivially.

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
