# F2 — holes in the acceptance rule (2026-09-26)

Branch `fix-acceptance-holes` off main `07e8f46` (F1 deployed). Owner's
brief, second of the three sweep units: "nothing is a fit unless it
converged and is determined":

- basinhopping success from the real scipy result;
- a NaN in an /api/fit reply is a failed fit with a message, not a local
  fallback;
- n_free > n_data is refused as undetermined;
- the required verdict requires a converged refit.

Source findings: `docs/findings/2026-09-25-fail-open-guards-sweep.md` H2, M1,
M2, M3 (`sweep-fail-open-guards`). Medium effort.

## 1. Sites

| # | hole | site | before | after |
|---|---|---|---|---|
| 1 | basinhopping always "converged" (H2) | `fitting.fit_model` → new `_basinhopping_candidate` | lmfit sets `success = True` before minimising and its basinhopping never reads scipy's result | the DE pattern in full (owner decision, §2): search → unconditional `least_squares` refinement from its point under the request's bounds (the refinement's convergence is the verdict; no χ² comparison, no tolerance) → competition with a `least_squares` fit from the same start (verified beats unverified, then lower χ²). An unverifiable search is `success: false` with its own message. `fit_model` is the ONE fitter, so the main fit, every perturbed restart and the required refit all go through it; scattered starts do not run for basinhopping. |
| 2 | a 2xx `/api/fit` reply with NaN switched to the local engine (M1) | page `_readFitReply` (new), used by `runFit` and `runAutoFitC1sGraphite` (the only two `/api/fit` callers) | `resp.json()` threw a SyntaxError, which `_asTransport` classified as a transport failure → `runFitLocal` replaced the server's converged result, verdicts and starts evidence | the body is read as text (a failure THERE is transport: the connection dropped) and parsed by the page; a body that was read but is not JSON is the server's reply → `serverError`, a failed fit with its message ("contains a non-finite number (NaN or Infinity) …" / "could not be read"), previous peaks and result kept, no fallback. Auto-Fit fails closed with the same message (it used to say "failed to converge or produced an unphysical graphite position"). The server is unchanged: the page, not a sanitiser, decides that a non-finite reply is not a fit. |
| 3 | n_data ≤ n_free read as a near-perfect, fully supported fit (M2) | `fitting.run_fit` before the fit; page `runFitLocal` after its free-parameter list | lmfit `redchi = χ²/max(1, nfree)`; the support / required F tests clamp dof to 1; the local engine clamps too | refused: `ValueError` "not determined by these data: N free parameters for M data points leaves no degrees of freedom …" (HTTP 400 on `/api/fit`; the same message through Find Peaks' refit, `/api/analyze`); the local engine fails with the same text, nothing written. A COUNT, not a threshold. Refused at n_free ≥ n_data (§2). |
| 4 | the required verdict ignored its refit's convergence (M3) | `fitting._component_required`; page `applyAutoFitResult` | `required` computed whether or not the refit converged (a refit stopped early read "required", F 992, for a redundant anchor); the page never read `refit_converged` | an unconverged refit returns `required: null, f: null, refit_converged: false, reason: "refit_not_converged"` (+ the solver message); Auto-Fit REFUSES that anchor before any charge-correction input is touched (red notice) — an anchor whose necessity could not be established must not set the energy reference of the whole spectrum. A check that did not RUN at all (older server, exception, nothing left, main fit not converged) still never blocks, as documented. |

| 5 | Auto-Fit parsed a non-2xx reply (owner, 2026-09-27) | page `runAutoFitC1sGraphite` | a Cloudflare 524 or gunicorn 500 reached `_readFitReply` and read as "the server's reply could not be read" — F2's own message misfiring | `resp.ok === false` is a failed REQUEST with its status in the message ("Auto-fit failed: Fit request failed (HTTP 524)."; a JSON `error` body's text when there is one), before any parsing, as Run Fit has done since A0 |

## 2. Decisions

- **Basinhopping (owner, 2026-09-26).** The brief said "success from the real
  scipy result". Measured first (scipy's flag recorded by a pass-through
  wrapper around the name lmfit calls): on a 1-in-8 sample of the 202
  committed targets (24 of 26 run), scipy marks **23 of 24** basinhopping fits
  failed — BFGS "Desired error not necessarily achieved due to precision
  loss" — while their χ²ᵣ equals Trust-Region's from the same start (median
  relative difference 1.3e-9; one 0.14 % worse; several better). Taken
  literally the method would fail on almost every correct fit. Owner chose:
  verify by refinement AND compete with a plain `least_squares` fit from the
  same start — the guarantee differential evolution already has ("never worse
  than the default method from the same start"). The wrapper was removed; no
  monkeypatching remains.
- **n_free = n_data is refused too.** The brief says "n_free > n_data". At
  equality there are zero degrees of freedom: the model interpolates every
  point, reduced χ² is undefined (lmfit divides by max(1, 0)) and the F tests
  run on a clamped dof of 1 — the same fault as the sweep's reproduction. The
  refusal is at n_free ≥ n_data; one degree of freedom is fitted as before.
- **An unconverged required-refit blocks Auto-Fit.** "The required verdict
  requires a converged refit": the server gives no verdict, and the page does
  not let an anchor with no verdict set the charge reference. The documented
  "a check that did not run never blocks" is kept for checks that did not
  run.

- **No perturbed restarts for basinhopping (owner, 2026-09-26).** Measured
  after the refinement change, with the page's request (`n_perturb` 3), on 16
  committed multi-component targets spread over 2–7 components (4 processes,
  8 physical cores — production runs 4 workers): median 386 s, max 1066 s,
  **14 of 16 over the 300 s server timeout**. Without the restarts: median
  96 s, max 256 s, none over 300 s, and χ²ᵣ identical on all 16 (worst
  relative difference 1e-8) — a global search gains nothing from them, the
  reason the scattered-starts check already excludes basinhopping and DE.
  `run_fit` skips the perturb loop for basinhopping (the request's
  `n_perturb` is still hashed into the seed; nothing else changes). DE keeps
  its restarts (2–75 s; not in the brief).

## 3. Measurements

| measurement | before F2 | after F2 |
|---|---|---|
| basinhopping, 1-in-8 sample of the 202 targets (26), `n_perturb` 0 | lmfit `success: true` on all (unconditional); scipy's own flag "failed" on 23 of 24 (BFGS precision loss) at Trust-Region's minimum | 26 of 26 verified; never worse than Trust-Region from the same start; up to 19 % lower χ²ᵣ; median relative difference −1.9e-10 |
| basinhopping wall time, page request, 16 multi-component targets | — | with restarts: median 386 s, max 1066 s, 14/16 > 300 s → restarts skipped: median 96 s, max 256 s, 0/16 > 300 s |

The public URL has a lower ceiling (Cloudflare 524 between 88 s and 125 s):
5 of those 16 still exceed it without restarts. Reported separately, not
fixed here: `docs/findings/2026-09-26-public-request-ceiling.md`.

## 4. Verification

- Python: `tests/test_fit_acceptance_holes.py` (refusal at 6 and 8 points for
  8 free parameters, fitted at 9; locked mixes free the count; `/api/fit`
  400 with the message; unconverged refit → no verdict, converged refit
  unchanged); `tests/test_basinhopping_outcome.py` (never worse than
  Trust-Region; search → refine → compete call sequence; an unverifiable
  search is not converged; a failed refinement rescued by the competitor;
  the required refit verified the same way; no perturbed restarts);
  `test_fit_reproducibility.py` updated (one seeded basinhopping
  minimisation per fit; the call sequence).
- JS: `fit_acceptance` (a 200 reply with NaN, and one that is not JSON, are
  failed fits; a body that cannot be READ is still transport → local);
  `stale_statistics` (Auto-Fit on a NaN reply fails closed, rolls back);
  `autofit_required` (unconverged refit refused before any charge input);
  `local_lm_descent` (the local engine refuses 6 free parameters for 5 and
  6 points, fits 40). Mocks gain `text()` (`withText`).
- Browser (:5151, committed UCl4-graphite project, replies intercepted where
  the case cannot be produced on demand): NaN reply → "Fit failed" with the
  non-finite message, no local overlay, peaks and result unchanged; a
  5-point ROI → "16 free parameters for 5 data points"; Auto-Fit with an
  unconverged refit → refused, charge correction unchanged. No page errors.

## 5. Codex rounds

**Round 1 — run A GO, run B NO-GO** (`f2_acceptance_holes_verdict_run{A,B}.md`):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B): the required-refit guard read only `refit.success`; differential evolution can return `success: true, box_unverified: true` (its boxed search converged, both verifications failed) — reproduced as `required: true, refit_converged: true`, F ≈ 1.2e6 | `_component_required` treats `box_unverified` as not verified: no verdict, `refit_converged: false` (the main fit's acceptance rule already rejects such a candidate). Regression test. |
| 2 | MINOR (A, B): the non-finite diagnosis matched "NaN" inside a JSON string of a malformed body | JSON strings are blanked before the token test; the malformed body now reads "could not be read". Regression test (string, token, escaped quote, valid JSON with the word). |

**Round 2 — run A GO, run B NO-GO** (`f2_acceptance_holes_r2_verdict_run{A,B}.md`;
both confirmed the round-1 required-refit fix with real solver probes across
all five methods):

| # | finding | fix |
|---|---|---|
| 1 | MAJOR (B), MINOR (A): the string-blanking regex was quadratic on an unterminated string of escaped quotes — 128 KB took 10 s on the page's thread | one linear scan tracking string and escape state (no regex); 128 KB stress case in the tests (< 500 ms) |
| 2 | MINOR (A, B): a body cut off INSIDE a string still read "non-finite number" | the scan keeps a string open to the end of the body; the truncated case reads "could not be read" |

**Round 3 — GO ×2** (`f2_acceptance_holes_r3_verdict_run{A,B}.md`; both
measured the round-2 scanner at ~4 ms on the 128 KB stress case, < 124 ms on
10 MB bodies, the old one at 9.6 s). One MINOR from both, fixed: a minus sign
before `Infinity` counted without a boundary before it (`x-Infinity`,
`--Infinity` read "non-finite number"); the sign now needs a boundary too.
Regression test. Round 4 confirms the fix.

**Round 4 — GO ×2, no findings** (`f2_acceptance_holes_r4_verdict_run{A,B}.md`;
500+ scanner probes each, 10 MB malformed bodies in ≤ 129 ms, the round-3
regression test fails on HEAD~1). **Ready for deploy.**

## 6. Release note

- Basinhopping results are now verified: the search is refined to a
  converged Trust-Region fit and competes with a plain Trust-Region fit from
  the same start, so it is never worse than the default method; it no longer
  runs perturbed restarts (they quadrupled its time for no change in χ²ᵣ).
- A server reply containing a non-finite number (an uncertainty that could
  not be computed) is a failed fit with a message — it used to switch to the
  in-page engine silently.
- A model with at least as many free parameters as data points is refused
  with the counts in the message (it used to read as a near-perfect,
  "supported" fit).
- Auto-Fit refuses its Graphite anchor when the refit without it did not
  converge, and reports an HTTP failure (e.g. a Cloudflare 524) with its
  status instead of "the server's reply could not be read".
