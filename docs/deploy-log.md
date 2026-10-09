# Deploy log

What went to production (i9 LaunchAgent, xps.fortierlab.org), newest first.
One entry per deploy; an item that changes behaviour for every user gets its
own bullet even when it shipped inside a larger unit, so it can be found
later. Procedure: [DEPLOY.md](../DEPLOY.md). The xps2 droplet is deployed by
the owner and may lag.

## 2026-10-09 — Background math: solved, checked, drawn as fitted; saved fits judged on reload (`bg-math-implement`, c39e67e)

- **Release note (backgrounds):** endpoint averaging now sets only the two edge
  levels a background is anchored to; every method computes from the measured
  data (Shirley, Smart and Tougaard used to replace the window's end points by
  their average), and Linear uses the same averaged edge levels. Every
  background runs to convergence and is checked against its own defining
  equation; when it has no solution (most often a window with no peak in it)
  the page says "… background not converged" under the method menu, suggests
  Linear for a window with no peak, and nothing is fitted, subtracted or
  exported against it. The "Shirley iterations" setting is gone. "Smart" and
  "Smart (experimental)" were the same calculation: one entry, "Smart"; files
  using either still load. **The page now draws exactly the background the
  server fits**, and uploads your data at full precision (it rounded
  intensities to two decimals).
- **Release note (saved fits — every user sees this):** a saved fit is judged
  on reload. The background it was actually fitted against (its stored fitted
  curve less its peaks) is compared with the one its settings give today. A fit
  saved before 2026-09-25 has no record of its charge correction, so it can
  never be confirmed: it reloads **marked out of date** (statistics not shown or
  exported; amber notice with the difference, or "matches as far as can be
  told") — press Run Fit. A file without the fitted curve or the energies it
  was fitted on loads its **peaks only** — press Run Fit. On the lab's 121
  committed saved fits: 0 current, 81 out of date (15 matching as far as can
  be told, 66 differing — most by under 1 % of the background's scale, at most
  5 %; 41 also hold a pre-2026-09-22 Voigt the page cannot draw as fitted), 40
  peaks only. A malformed record (non-numeric raw data, a non-finite or
  negative stored RMSE, values that overflow, more than 2^20 points) is
  refused with a plain reason, never shown as current.
- **Release note (fits):** the random restarts are now seeded from your data,
  window, settings and model rather than from the computed background, so this
  version changes them once. On the committed fits backgrounds moved by at most
  0.001 % of net area; six fits that sit between two solutions landed in
  another (1–29 pp); the scattered-starts line flags four of them.
- Codex: 34 implementation rounds (17 before the owner round of 2026-10-03,
  GO ×2 at round 17; rounds 18–34 on the owner round and the restore rule).
  Owner rulings: a fit without its fit key is never confirmed current
  (2026-10-05); every acceptance compares finite quantities only (2026-10-06);
  rounds 25–31 category (c); round 34's findings all R2 (no finding reachable
  from real data), each fixed by a refusal. Plan:
  `docs/superpowers/plans/2026-10-01-background-math-implement.md` §5, §7.
- Suites at c39e67e: pytest 1194 passed / 7 skipped; JS 582 pass / 2 todo (CI
  floor 582). Browser check on dev :5151 and on production through
  xps.fortierlab.org: a server Run Fit on a Shirley C 1s completes with current
  statistics and no not-converged note; the committed
  `Cl2p_projfit_test.proj.zip` loads through the page's file input with its 3
  fits marked out of date; no page errors. LaunchAgent running, last exit 0;
  `/api/health` ok on :5050 and publicly; reference data loaded (legacy + 6
  curated elements). xps2 droplet: the owner's.
- Student note `docs/comms/2026-10-03-background-math-note.md`: the owner sends
  it.

## 2026-10-01 — Find Peaks archived (`archive-find-peaks`)

- **Release note:** Find Peaks is archived: it is no longer offered in the
  Actions menu. Saved projects whose peaks came from Find Peaks load and fit
  exactly as before.
- Hidden, not deleted (owner, 2026-09-30): its only entry point, the
  Actions-menu item, is an HTML comment saying how to restore it; the modal and
  its code, `/api/analyze`, `autofit/` and every Find Peaks test are kept. A
  cached result or applied-peak provenance is never read outside its block.
  Parked with it, with what would bring each back: `docs/autofit/PROGRESS.md`
  "PARKED" (finalists' extra screen starts, the noise-floor F test, the
  math-first migration, Unit B — deferred, not dropped).
- **CI now runs the page's JS suite** (it never had — Find Peaks' own JS tests
  included). A second node reporter writes node's structured results; the
  guard (`scripts/ci_check_node_events.py`) fails on any skip (any nesting,
  any reason), failure, a test file that did not run to completion, a counter
  that does not reconcile, or fewer passes than the current count (508; raise
  it when tests are added).
- Codex: 7 rounds (rounds 2–6 all on the CI guard); round 7 GO ×2, no
  findings. Python 1111 passed / 7 skipped; JS 510 / 508 pass / 2 todo; real
  browser check in the suite (menu, save, reload with an injected stale Find
  Peaks cache, Run Fit) and on production through xps.fortierlab.org (no Find
  Peaks entry or text with the Actions menu open; the code still present; a
  server Run Fit completes with current statistics; no page errors). No
  student note.

## 2026-09-30 — Run Fit checks that a fit reached its minimum (`fix-runfit-certificate`, unit A2)

- **Release note:** Run Fit's result is no longer "complete" just because the
  optimiser stopped. After the usual search (unchanged: the fit and its
  perturbed restarts exactly as before) the server continues the returned fit
  from where it stopped until continuing no longer improves it — Trust-Region
  restarts until one improves chi-square by less than Trust-Region's own
  tolerance, at most 50; otherwise the fit is reported as not converged, with
  the reason. The same check judges each scattered start and Auto-Fit's
  required-component refit. On the 202 committed fits: Trust-Region 202 / 202
  converged, areas moved > 1 pp on 4 (every one to a lower chi-square);
  Levenberg-Marquardt 197 → 202 converged, > 1 pp on 2 (largest 13 pp,
  chi2r 21.0 → 15.5); scattered starts "did not converge" 30 → 3 (LM);
  median +0.04–0.07 s per Run Fit, 90th percentile under 1 s. **Re-running a
  saved multi-component fit may shift its areas** where the old fit had
  stopped short.
- **New line under Results** when finishing the fit moved a component's centre
  more than 1 eV ("Fit continued past where the optimiser stopped; C-O moved
  −1.47 eV"): a notice, not a confirmation; bound to the fit; saved while
  current; CSV / XLSX. 0 of the 202 committed fits trigger it.
- **Levenberg-Marquardt is no longer byte-reproducible where the certificate
  moves a fit** (it then carries Trust-Region's arithmetic); repeat presses
  agree to 0.074 pp (main: 0.23 pp — main was already not byte-identical on LA
  models). Tests compare fits within rounding (`tests/fit_equality.py`, owner
  decision).
- The response adds `certificate` and each component's `shape` (additive).
- Codex: 10 rounds — every finding after round 1 was in the within-rounding
  comparison; round 10 GO ×2, no findings. Python 1085 passed / 7 skipped; JS
  506 / 504 pass / 2 todo; browser check on dev and on production through
  xps.fortierlab.org (a certified Run Fit on 1-GTA C1s Scan; the notice
  renders with no button, exports, and disappears after an edit; no page
  errors). Student note held for the owner.

## 2026-09-29 — Find Peaks does not read the clock (`fix-find-peaks-determinism`, unit A1)

- **Release note:** Find Peaks' answer no longer depends on how busy the
  server is. It used to stop refits, the screen and the sweep on wall-clock
  budgets (25 s per candidate, 240 s per analysis), so the same spectrum could
  get a different model under load (1-GTA C1s Scan_6: AG2 under load, MG2
  idle). Every candidate is now screened and gets its full count of refits.
  A fit's convergence is decided by restarting from where it stopped until a
  restart no longer improves χ² by more than the optimiser's own tolerance —
  not by the optimiser's success flag. The old warm restart at the
  evaluation-cap stall point, which reported success ~30 evaluations later at
  a point that was not a minimum, is removed. **Find Peaks takes longer**
  (page request, idle: 236–239 s vs 208–213 s; under heavy load ~350 s,
  where it used to cut work short) and **may suggest a different model than
  before on some spectra**: of 7 committed C 1s scans 4 unchanged, 8-JT
  Scan_5 and Scan_7 MG2 → MG3 (the screen's single start lands MG2 in a poor
  local minimum — owner: ship as is, the known single-start problem made
  consistent; a finalists-only extra-starts unit follows), 1-GTA Scan_2
  MG3 → MG2 (an "empty slot" credit that came from mis-flagged refits is gone).
- **The Find Peaks progress poll judges a job lost by its heartbeat** (2 s,
  lost after 30 s without one), not by a 600 s total, so a long counted
  analysis is waited for.
- Load acceptance: winner, tier, candidates, ranks and roles identical idle /
  idle / 8 CPU burners; numbers within Trust-Region's rounding jitter (≤ 0.24
  meV, ≤ 9.4e-4 pp). Real-data gates 27 / 27 (main 26 / 27).
- Codex: rounds 1–2 NO-GO ×2 (a capped certificate restart could certify;
  the poll's total-time cap; the heartbeat outliving a worker killed past
  `except Exception`; unreadable progress records polled forever), round 3
  GO ×2 with no findings. Python 1034 passed / 7 skipped; JS 502 / 500 pass /
  2 todo. Browser check on dev and on production through xps.fortierlab.org
  (page Find Peaks on 1-GTA C1s Scan_6 → MG2, 976 of 977 polls with a
  heartbeat ≤ 2.7 s old, then Run Fit on the server; no page errors).
- Finding corrected: 8-JT Scan_7's "χ²ᵣ 37.6 vs 5.21" was a genuine
  constrained local minimum in a worse basin, not a fit stopped short of its
  minimum (`docs/findings/fit-termination-scope/README.md`).

## 2026-09-27 — long fits start and poll (`fix-fit-start-poll-r5`, sweep unit 2)

- **Release note:** Run Fit (including "Use this solution") and Auto-Fit no
  longer hold one web request open for the whole fit. The page starts the fit
  and checks on it every half second, so a fit that runs for minutes —
  basinhopping on a large C 1s model — now finishes instead of failing with
  Cloudflare's HTTP 524 at ~100 s. Results are identical to before (the same
  `run_fit`; Levenberg-Marquardt byte-identical). Switching tabs or editing
  the model during a fit stops it on the server too; closing the page cancels
  it; a fit nobody is polling is cancelled after 3 minutes.
- **Each server worker runs one fit at a time** (others wait "queued") and
  admits at most 6; beyond that the page is told "The server is busy with
  other fits. Try again in a moment." (HTTP 503).
- Public-URL check right after deploy (`scripts/public_fit_poll_check.py`,
  the five largest committed C 1s models, basinhopping, through
  xps.fortierlab.org): all five PASS — fits 209–312 s, 328–491 requests each,
  longest single request 1.16 s, no 524.
- Codex: rounds 1–2 NO-GO ×2, round 3 split, round 4 NO-GO ×2 (parked),
  round 5 (owner-approved) GO ×2 with no findings. Round 5 fixed an Auto-Fit
  refused by its preflight cancelling a running Run Fit (spinner stuck) and
  Batch Fit hiding another fit's spinner. Rebased onto main as one commit
  (per-round history on `fix-fit-start-poll`). Python 1026 passed / 7
  skipped; JS 496 / 494 pass / 2 todo; production browser check (Run Fit and
  Auto-Fit through start/poll, tab-switch and edit cancel the server job, start
  unreachable → local fallback, a second Run Fit supersedes, an Auto-Fit
  refusal leaves a running Run Fit alone; no page errors).

## 2026-09-27 — background twins: the page draws the background the server fits (`fix-background-twins-on-f2`, sweep unit 4)

- **Release note:** the background the page draws, freezes into a fit,
  saves and fits against in the browser is now the one the server fits
  against, for Shirley, Smart and Smart (experimental) — exactly, on the
  tested spectra, at every endpoint averaging. It differed by up to 1.2 % of
  the intensity span for Smart at endpoint averaging 10, by up to 1.4 % for
  Smart (experimental) (which also integrated a descending grid from the
  wrong end), and on data dipping below the baseline or with decimal
  endpoints the page's Shirley could land on a different curve entirely
  (33–63 % of the span in review). **Saved projects using these backgrounds
  may redraw slightly differently** — to the curve their fit actually used.
- Why it took four rounds: an iterative background turns a one-ulp
  difference into a different fixed point, so the page's twins now mirror
  fitting.py's arithmetic operation for operation (numpy's linspace start,
  numpy's pairwise mean for endpoint averaging). Pinned by
  `tests/js/background_parity.test.js` against fitting.py's own functions.
- Known gaps, pinned, unchanged: `shirley_linear` (de-listed) on descending
  grids; linear on non-uniform grids; the UI's Shirley iteration count vs the
  server's convergence (sealed-fit-record memo Part 5).
- Codex: rounds 1–3 NO-GO ×2, round 4 GO ×2 (one MINOR, np.mean(−0) = +0,
  fixed after the GO — owner accepted without another round); Python 1006
  passed / 7 skipped; JS 477 / 475 pass / 2 todo; production browser check
  (page background = server `background_y` exactly for shirley, smart,
  smart_exp at endpoint average 10; no page errors).

## 2026-09-27 — Auto-Fit C1s gate reads the data the fit would use (`fix-noise-floor-on-f2`, sweep unit F3, first half)

- **Release note:** Auto-Fit C1s Graphite is offered only when the midpoint
  of the data the fit would actually use is in 270–315 eV — for the active
  tab the live selection, never the tab's stale saved window or a typed ROI
  reaching past the data. Before, a C 1s tab could be refused (or another
  region offered the C 1s auto-fit) from a window it no longer had.
- The other half of F3 (Find Peaks' 1.0-count occupancy floor → a scale-free
  test) was parked for an owner decision
  (`docs/findings/noise-floor-occupancy/`) and is not in this deploy.
- Rebuilt onto F2 without the parked unit 2 (same changes, patch-id
  identical). Codex GO ×2 in rounds 1–3; Python 1006 passed / 7 skipped; JS
  459 / 457 pass / 2 todo; production browser check (gate true on C1s Scan,
  false on U4f Scan; Run Fit; no page errors).

## 2026-09-27 — acceptance-rule holes (`fix-acceptance-holes`, sweep unit F2)

- **Release note:** basinhopping results are now verified: the search is
  refined to a converged Trust-Region fit and competes with a plain
  Trust-Region fit from the same start, so it is never worse than the default
  method; it no longer runs perturbed restarts (they quadrupled its time for
  no change in χ²ᵣ: median 386 s → 96 s on 16 multi-component targets).
- **A server reply containing a non-finite number** (an uncertainty that
  could not be computed) is a failed fit with a message — it used to switch
  to the in-page engine silently, replacing a converged server result.
- **A model with at least as many free parameters as data points is
  refused** (server and in-page engine), with the counts in the message; it
  used to read as a near-perfect, "supported" fit.
- **Auto-Fit refuses its Graphite anchor when the refit without it did not
  converge**, and reports an HTTP failure (e.g. a Cloudflare 524) with its
  status.
- Found on the way: Cloudflare ends a proxied request at ~100 s (88 s
  passed, 125 s gave 524), so the largest basinhopping models still fail
  through the public URL; new CLAUDE.md rule "Timing claims are measured
  through the public URL" (`docs/findings/2026-09-26-public-request-ceiling.md`).
- Codex: round 1 split, round 2 split, round 3 GO ×2, round 4 GO ×2 (no
  findings); Python 1006 passed / 7 skipped; JS 450 / 448 pass / 2 todo;
  production browser check (load project, Run Fit, no page errors).

## 2026-09-26 — statistics after an edit belong to the previous model (`fix-stale-statistics`, sweep unit F1)

- **Release note:** statistics now follow the model they came from. After
  any edit to a component, a lock, the background, the ROI, the anchors or
  the charge correction — or a Find Peaks apply / undo that keeps an older
  result — the previous fit's χ², RMSE, R-factor and uncertainties are
  marked as belonging to the previous model and are not shown, exported or
  drawn as the fit (the Results panel says so; exports carry a WARNING;
  saves record it). Undo back to the fitted values and they return.
- **Every project saved before this release** shows its statistics with a
  note that they cannot be confirmed to describe the saved model, on every
  tab, until Run Fit is pressed (owner: the fix is legacy verification in
  the sealed record's adapter, logged in its memo).
- **Auto-Fit, and a Run Fit that falls back to the in-page engine, now
  discard a result whose model was edited while it ran**, as Run Fit already
  did for server results.
- One mechanism: the step (b) fit key, now stamped by every result creator;
  keys compared with each form field read the way its consumer reads it
  (new design rule "Two readings of one field" in CLAUDE.md).
- Codex: round 1 NO-GO ×2 (7 findings), round 2 NO-GO ×2 (2), round 3 GO ×2;
  Python 994 passed / 7 skipped; JS 440 / 438 pass / 2 todo; browser-checked
  on :5151 and in production.

## 2026-09-25 — LA's m continuous on the page; held exactly by the local engine (`fix-cam-continuous`)

- **Release note:** LA(α, β, m) components are now drawn, integrated and
  exported with the same continuous m the server fits (the page rounded it
  to a whole number of points): opening a saved U 4f project moves an LA
  component's area by 0.33 % at the median and 1.2 % at most, to the curve
  that was actually fitted. m is shown to 0.01. Batch Fit keeps m exactly
  at the value it is given (it used to round it to a whole number).
- Page vs server on the 108 committed LA components: max 0.97 % of
  amplitude → 7e-16. Every LA parity and round-trip check is now a hard
  assertion.
- Fitting m in the local engine was tried and withdrawn after two Codex
  rounds: LA's curve jumps at every m = 6k/7 and a smooth optimiser cannot
  fit it (owner: right call; Batch Fit fitting m declined — it would close
  only Scan_6, and the starting-point label stays either way).
- Codex GO x2 (round 3); Python 993 passed / 7 skipped; JS 422 / 420 pass /
  2 todo; browser-checked.

## 2026-09-25 — ROI past the data + peak centre outside the data (`fix-roi-clamp`)

- **Release note:** when the Region of Interest extends past your data, the
  page now says so under the ROI fields ("ROI extends past your data —
  clipped to X–Y eV"), and warns in amber when BE min is above BE max or
  the window misses the data. A peak whose centre lies outside the fitted
  data gets an "outside data" badge on its card. Nothing is moved: the
  fields, the peaks and every fit, Find Peaks request and save behave
  exactly as before — the page always used only the data inside the ROI.
- Measured on the committed projects: the quiet hint shows on 30 of 166
  tabs (median overshoot 0.39 eV); no peak is centred outside its data.
  Review later whether the 18 % is noise (owner).
- Manual fit and Find Peaks use the same window except for one edge point
  when an energy lies within 5e-5 eV of an ROI edge — a symptom of the
  upload rounding, filed under audit item 8 / R6-1, not patched separately.
- Also: the required-anchor test that passed 2 of 3 on main (Trust-Region
  jitter on a test that never formed its premise) now holds the anchor;
  20 of 20 separate-process runs pass.
- Codex GO x2 (round 2); Python 993 passed / 7 skipped; JS 411 / 406 pass /
  5 todo; browser check 16/16.

## 2026-09-25 — DS+G page evaluator (`fix-dsg-page-evaluator`)

- **Release note:** DS+G components are now drawn, integrated and exported
  exactly as the server fits them. Until now the page used a numerical
  quadrature that was wrong across most of the shape's range, and on the
  parameters Find Peaks proposes for a graphitic C 1s line (every A- and
  M-family candidate) the page showed the component 5–21 % low in area.
  Nothing in Find Peaks or the shape dropdown changed.
- The page's `dsgConvolved_array` mirrors the server's padded-grid
  convolution with the same FFT circular convolution: < 1e-6 of amplitude
  (measured ≤ 6e-14) across the full α/β/m box the optimiser can reach, on
  eight grids, irregular grids and 1- and 2-point grids; browser check on a
  committed C 1s scan agrees to 1e-12.
- **Server change, one guarded branch:** a DS+G centre OUTSIDE the padded
  grid is normalised by the curve's maximum (it was normalised by a ~1e-20
  tail whose rounding sign picked one of two unrelated curves). Proven
  byte-identical to the previous function for every centre inside the padded
  grid: 5,780 of 5,780 cases `np.array_equal`, and `run_fit` on a committed
  C 1s model with a DS+G line returns identical JSON
  (`scripts/dsg_outside_centre_identity.py`,
  `docs/findings/dsg-evaluator/identity_proof_vs_main_b3c9e37.txt`).
- Server limits documented and left (plan §3a, §3c): a DS+G m just above the
  0.001 delta threshold on a coarse grid can underflow the kernel and return
  an all-zero curve (it then reads as "not supported by the data"); a centre
  inside the padded grid but outside the measured data is still normalised
  by the old rule, where the page can diverge loudly. Only a peak centred
  outside the data reaches the second; the next unit warns on it.
- Codex: round 3 NO-GO x2 on the §3c residual only (owner: option 1, deploy).
  Python 991 passed / 7 skipped / 1 pre-existing flaky test (being fixed
  next); JS 396 / 391 pass / 5 todo; browser-checked.

## 2026-09-22 — A03: Voigt η identity, parameter-range sweep, U 4f gap re-measured (`fix-voigt-eta-identity`)

- **Release note:** Voigt components are now fitted at the fixed 50/50 mix
  the page has always drawn; until now Run Fit let their mix vary on the
  server and the page reported the 50/50 curve's area under the other
  mix's parameters (up to 20 % off per component). Re-fitting a saved
  project with Voigt components moves an area fraction by 0.36 pp at the
  median and 0.69 pp at most on the 55 committed tabs (a Voigt component's
  own area by 3.2 % at the median, 15 % at most). Use GL to fit the mix.
  Also fixed: an asym-GL mix of exactly 0 or a DS α of exactly 0 was sent
  to the server as 50 / 0.1; a locked value outside the optimiser's search
  limits (a DS+G m locked at 0) was moved onto the limit before fitting;
  the page now clips DS+G α to 0.495 as the server does. Such requests
  also draw a different random seed.
- Measured: on the 90 committed Voigt targets the server's free η ended at
  pure Gaussian on 60 of 180 components and pure Lorentzian on 16; the
  displayed 0.5 curve was 13.9 % off the fitted one at the median.
- New harnesses: page → server → page identity for every shape
  (`tests/js/lineshape_roundtrip.test.js`, incl. every shape parameter
  locked at each bound, and the Python twins pinned to the page); parity
  sweep of each shape's free parameters across the fit's bounds. Known
  gaps, `todo`: LACX with m > 0 (`caM` clamp unit) and DS+G with m ≥ 0.05
  (the page's quadrature is wrong across the fitted β/m range — next unit,
  ahead of the ROI clamp).
- U 4f gap re-measured (W1's 18 targets): max area gap 20.8 → 8.9 %,
  fraction 1.4 → 0.77 pp; the Voigt part is gone; the residual is one
  target's `caM` clamp and three where the local engine stops in a worse
  minimum. The "starting point" label stays.
- U 4f and Cl 2p parity batteries re-based (expert fits saved under the old
  request; fixtures regenerated; each Voigt evaluated with the mix the
  server recorded for that fit).
- Codex GO ×2 (round 6); suite 989 passed / 7 skipped; JS 375 / 368 pass /
  7 todo; browser-checked.

## 2026-09-22 — Auto-Fit "is the anchor required?", step (c) (`feature-autofit-required-refit`)

- **Release note:** Auto-Fit C1s now also refits the model without its
  Graphite anchor and refuses to set the charge correction from an anchor
  the other components can absorb.
- `POST /api/fit` accepts `require_component: <peak id>` and returns
  `required` (the refit without that component, through the run's own
  fitter, F ≥ 10, no tolerance of any kind). Closes the
  redundancy-under-overlap limit of the anchor check; all 70 committed
  Graphite anchors are required (F ≥ 54).
- Codex GO ×2 (round 4); suite 983 passed / 7 skipped.

## 2026-09-22 — "not supported by the data", step (b) (`feature-unsupported-components`)

- **Release note:** a component the fit drove to zero is now reported as
  "not supported by the data": its centre, width and uncertainties are not
  shown, it is excluded from Quantify, and both engines allow a zero
  amplitude.
- Definition: with the other components held as fitted, removing the
  component does not make the fit significantly worse (the Auto-Fit
  anchor's F statistic, F ≥ 10). Computed by the server per component
  (`individual_peaks[].support`) and by the local engine from its own
  residuals; a linked component follows its root ancestor.
- The verdict is bound to the fit that produced it (model + background /
  ROI / anchors / charge shift) and lapses on any edit until a new fit;
  exports write a Status only from a current verdict.
- Sites: sidebar card, Results table (percentages over supported
  components), uncertainty panel, Quantify (listed beneath), chart / stack
  / figure labels, CSV/XLSX (Status column, empty cells, no At%, WARNING),
  TSV header, the scattered-starts table. Local amplitude floor 1 → 0.
- Measured on the 202 committed targets: 3 of 752 components (three C 1s
  re-fits), 0 of 95 fresh starts — survivorship-biased (a collapsed
  component may have been deleted before saving).
- Codex GO ×2 (round 6); suite 975 passed / 7 skipped.

## 2026-09-22 — scattered-starts check, step (a) (`feature-scattered-starts-check`)

- **CORRECTNESS FIX FOR EVERY RUN FIT: a result is discarded if the model
  was edited while the fit was running.** The peak controls stay editable
  during a fit; a centre changed and locked mid-fit used to keep its edited
  value under the server's χ², σ and fitted curve. `runFit` now compares the
  model-plus-context key taken before its first await with the key at
  completion and, if they differ, applies nothing ("Fit discarded (model
  edited)", previous peaks and result kept). Independent of the starts check.
- Scattered-starts check: every Run Fit with ≥ 2 unlinked components runs 3
  more fits of the same method from seeded scattered starts. The student's
  result remains the fit; "N of 3 scattered starts reached this solution";
  lower-χ²ᵣ solutions listed beside it with each component's own area % and
  move from the student's start; Preview; "Use this solution" (atomic re-fit,
  one undo, recorded, exported) with a confirmation naming the component when
  it moved > 1 eV. Evidence is bound to the fit that produced it (model +
  background/ROI/anchors/charge shift) and disappears from the panel, saves
  and exports after any such change. Measured: alternative on 0 of 94
  re-fits, 6 of 84 fresh starts; median +0.54 s per Run Fit.
- `POST /api/fit` accepts `n_starts` (0–10) and returns `starts`.
- Codex GO ×2 (round 3); suite 968 passed / 7 skipped.

## 2026-09-21 — Auto-Fit anchor support check (`fix-autofit-zero-graphite-cc`)

- Auto-Fit C1s no longer derives the charge correction from a Graphite
  component the data do not support (with/without-component F statistic from
  the `/api/fit` response). Shipped by owner decision after six Codex rounds,
  all NO-GO, with documented limits: false rejection under a gross
  single-channel artefact; redundancy under overlap out of scope.
- Rollback after a rejected Auto-Fit restores the Custom-reference field.

## 2026-09-21 — request-derived seeding (`fix-seed-perturbation`)

- Every random draw in `run_fit` comes from a seed derived from the numbers
  the optimiser is handed. Before → after on 202 targets × 5 presses:
  fractions moving > 1 pp between presses 8 → 0 (Trust-Region), 12 → 0 (LM).
  Trust-Region is not bit-reproducible (owner: accept and disclose).
- **`run_fit` refuses methods outside the five supported ones** (closes
  unseeded lmfit methods reachable through `/api/analyze`).

## 2026-09-20 — Differential Evolution fix (`fix-de-finite-bounds`), findings merge

- Differential Evolution runs from the page's requests (was HTTP 422 for
  every fit with a free amplitude); never worse than the default method from
  the same start; generated search limits never reported or stored.
- `investigate-optimizer-disagreement` merged (docs and scripts only).
