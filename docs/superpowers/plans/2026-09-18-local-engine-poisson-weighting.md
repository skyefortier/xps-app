# Local engine: Poisson weighting (unit W1) — plan, evidence, site table

Status: approved as the unit after A0 (owner, 2026-09-16/18). Branch
`feature-local-lm-poisson-weighting`. Rule for this unit (owner): weight
the local engine like the server, MEASURE the remaining gap, and retire or
reword the "starting point" designation and the student note's 126 %
sentence ON EVIDENCE. Do not assume weighting closes the gap.

## What changes

`runFitLocal` minimises Σ (w·(data − model))² with
`w = 1/√max(raw counts, 1)`, raw = background-subtracted + background —
the same weights `fitting.run_fit` applies. Its statistic becomes a real
reduced χ² (Σ(w·r)²/(n − k)), comparable with the server's.

## Evidence (measured BEFORE implementing; prototype = the shipped
functions extracted from `templates/index.html` with only the residual
weighted; 18 Batch Fit targets of the committed UCl4-graphite project,
each compared with the server fit from the same scaled start; areas
evaluated with the page's own semantics)

| set | engine | max Δcentre | max ΔFWHM | max Δarea | max Δfraction |
|---|---|---:|---:|---:|---:|
| C 1s, 8 of 9 targets (GL / asym-GL) | unweighted (A0) | 679 meV | 43.6 % | 125.7 % | 28.5 pp |
| C 1s, 8 of 9 targets | **weighted** | **3.8 meV** | **0.50 %** | **1.40 %** | **0.32 pp** |
| C 1s Scan_4 | weighted | 41.9 meV | 9.0 % | 99.9 % | 15.1 pp |
| U 4f, 9 targets (2×LACX + 2×Voigt) | unweighted (A0) | 44.5 meV | 17.3 % | 20.3 % | 1.3 pp |
| U 4f, 9 targets | weighted | 39.7 meV | 17.2 % | 20.8 % | 1.4 pp |

Weighted χ²ᵣ agrees with the server's to 3 digits on the 8 C 1s targets.
Feeding the local engine the SERVER's background changes nothing material
(the JS/Python background twins are not the cause here).

Why a gap remains (so the designation stays, reworded):

1. **C 1s Scan_4 — a finding, not an exception.** The local engine reaches
   χ²ᵣ 18.21 where the server's default Trust-Region method reports 19.06;
   restarted from the local solution the server also reaches 18.21, and so
   do Levenberg–Marquardt and basin-hopping from the original start, all
   by driving one component to zero. The server's answer was a local
   minimum and the six-component model is over-specified on that scan.
   Recorded with the 72-fit sensitivity result in
   `docs/findings/2026-09-fit-determinacy.md` §2.
2. **U 4f — not weighting at all.** The whole area gap sits in the two
   "Voigt" satellites: the server fits their η FREE from 0.3 (it reached
   0.99 and 0.00) while the page draws and fits η = 0.5 (audit A03). The
   main LACX lines agree to ~1 % with `caM` held at its rounded start
   (8 vs the server's 8.66). Closing this needs A03, then the `caM` clamp.
3. The local engine still produces no parameter uncertainties.
4. **Different amplitude lower bounds (Codex W1 round 1) — an OPEN
   DECISION, not a parity task.** Local floor 1, server 0; a component of
   true amplitude 0.1 gives a ~900 % area gap. Neither bound is assumed
   right: 0 is degenerate (centre/width unidentifiable, σ meaningless), 1
   is unit-dependent (wrong for CPS data and weak satellites). The merits
   and options are in `docs/findings/2026-09-fit-determinacy.md` §3; the
   owner decides before anything is implemented.
5. **Same formula, not bit-identical inputs.** `uploadToBackend` rounds
   intensities to 2 dp before the server weights them; the local engine
   uses full precision (weight 0.9976 vs 1 at intensity 1.0049). And both
   engines weight by √intensity whether the data are counts or CPS: that
   is the server's convention, not a calibrated counting uncertainty for
   rate data.

Decision: the designation STAYS and is reworded to the truth — "local fit,
Poisson-weighted like the server, no uncertainties: a starting point …
can differ from the server fit for Voigt/LA components or where the model
has several minima, or for very weak components (bounds)". It is retired
only when A03 and the `caM` clamp are done, the amplitude-bound decision
is made, and a re-measurement supports it. The claims above are about the 18 measured
targets, not a general guarantee.

## Site table (enumerated up front — method note 2026-09-18)

Everything keyed on the local objective goes through these helpers; the
unit changes the helpers and the literal texts, then each consumer is
covered by a behavioural or structural test.

| site | function(s) | change |
|---|---|---|
| engine | `runFitLocal` | weighted residual; `objective: 'poisson_weighted_chi_square'`, `weighting`; returns `chiReduced` |
| identity | `_isLocalFit`, new `_isLocalProvenance` | local = `engine === 'local'` OR the A0 unweighted objective (old saves) |
| statistic label | `_fitStatLabel`, `_fitStatusText`, `_applyStatCaption`, `_applyStatDisplay`, tooltips | weighted local → "χ²ᵣ (local)"; A0-era unweighted results keep "Residual variance" |
| caveat text | `_LOCAL_FIT_CAVEAT*`, `_localFitCaveat` | per objective: weighted wording vs legacy unweighted wording |
| banners | `_updateLocalModelBanner`, `renderResults`, `renderQuantify`, overlay, local-fit notice | reworded, objective-aware |
| batch | `runPropagation` summary/progress | statistic label per objective |
| chart/figure/stack/history/preview | `updatePlot`, `_doPublicationExport`, `_buildStackDatasets`, `renderStackLegend`, `_renderHistoryList` | unchanged logic (keyed on `_isLocalFit`/`_isLocalModel`); figure stat label per objective |
| exports | `exportFitTable` (CSV, XLSX), `exportResults` (TSV) | label + warning per objective |
| saves/loads | `_doSaveSpectrum`, `_doSaveFit`, `_doSaveProject`, `_loadSpectrumFile`, `fromJSON`, `_loadProjectJSON` | persist `weighting`; provenance checks via `_isLocalProvenance` |
| undo / auto-fit rollback / batch copy | `_provenanceOf`, `_peaksSnapshot`, `_pushUndoFor`, `_autoFitSnapshot/Restore` | unchanged (carry provenance objects); `_provenanceOf` records the objective it finds |
| scanner | `scripts/scan_batch_fit_signature.py` | docstring: from this unit local results are weighted and identified by file metadata (POST-FIX), the ratio signature only finds pre-A0/A0 files |
| docs | `CLAUDE.md`, follow-up student note | engine description; corrected note |
| tests | `tests/js/local_lm_descent.test.js`, `tests/js/fit_acceptance.test.js` | weighted oracle; analytic weighted recovery; server-parity pin on GL targets; label/caveat texts per objective |
