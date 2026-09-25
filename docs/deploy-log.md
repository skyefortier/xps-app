# Deploy log

What went to production (i9 LaunchAgent, xps.fortierlab.org), newest first.
One entry per deploy; an item that changes behaviour for every user gets its
own bullet even when it shipped inside a larger unit, so it can be found
later. Procedure: [DEPLOY.md](../DEPLOY.md). The xps2 droplet is deployed by
the owner and may lag.

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
