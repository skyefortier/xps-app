# F1 — statistics after an edit belong to the previous model (2026-09-25)

Branch `fix-stale-statistics` off main `4475023` (caM unit deployed). Owner's
brief, first of the three sweep units: "Reuse step (b)'s fit key (model +
background/ROI/anchors/charge shift). When the current key does not match
the key the statistics came from, mark χ², σ and R stale in the Results
panel, CSV, XLSX, TSV, figure export and saves — say plainly they belong to
the previous model, or omit them. Do not build a second binding mechanism;
this is a down payment on the sealed fit record and must be absorbable by
it. Enumerate every consumer of the statistics first."

Source finding: `docs/findings/2026-09-25-fail-open-guards-sweep.md` H1
(`sweep-fail-open-guards`).

## 1. The one mechanism

The key already exists and already binds two things to their fit:
`_startsModelKey(peaks, ui, ccShift, anchors)` — every peak field a request
reads, background type and window, endpoint averaging, Shirley iterations,
ROI, manual anchors, charge shift. `fitResult.startsModelKey` (the starts
evidence) and `p.support.fitKey` (step (b)'s verdicts) both hold it, taken
after the result is applied, and are compared with `_startsLiveKey()` /
`_startsRecordKey(t)` at every read. F1 adds NO new key and no new field
name: every creator of a fit result stamps `fitResult.startsModelKey`, and
ONE accessor classifies a result against a key:

- `current` — the key matches: the statistics describe the model shown;
- `stale` — the key differs: they belong to the previous model;
- `unverified` — the result carries no key (saved before this unit, or an
  older local / Auto-Fit result): whether it described the saved model
  cannot be known. Shown, with a plain note to re-run. Treating these as
  stale would hide χ² and σ on nearly every existing lab project.

The sealed fit record absorbs this directly: its record will carry the key
and the statistics together; `_statsState` becomes a read of the seal.

## 2. Creators of a fit result

| creator | stamps the key today | after |
|---|---|---|
| `runFit` (server) | yes, after `applyBackendResult` | unchanged |
| `runFitLocal` (fallback; Batch Fit targets) | no | yes, after the values are committed |
| `applyAutoFitResult` | no; and it locks every centre and refines the charge shift AFTER applying (so its verdicts are re-stamped by `_restampSupport`) | stamped at creation AND re-stamped by `_restampSupport` (those changes are part of its result) |
| `_loadSpectrumFile` | restores a saved `startsModelKey` if present | unchanged (an older file has none → `unverified`) |
| project load (`fromJSON` / tab records) | the saved `fitResult` object, key included if present | unchanged |
| `_historyRestoreSnap`, `_autoFitRestore` | restore an older result WITH its key | unchanged — the comparison judges it |
| `applyFindPeaks` (default mode), undo / redo | keep the old result over a replaced model | unchanged — the key comparison now makes that result `stale` (CLAUDE.md lists these as "not covered"; they are covered here for the statistics) |
| `clearAllPeaks`, `closeTab`, Batch Fit's copy, `.fit.json` import | set `fitResult = null` | unchanged |

## 3. Consumers of χ², σ, R (and the stored fitted curve)

| # | consumer | reads | `stale` | `unverified` |
|---|---|---|---|---|
| 1 | Results panel (`renderResults`): statistic card, RMSE card, R panel, σ in the peak table | `chiReduced`, `rmse`, `rFactor`, `backendResult` σ | amber banner: the statistics belong to the previous model, Run Fit; statistic, RMSE and R shown as "—"; σ omitted | a plain note; values shown |
| 2 | Header statistic + status bar (`_applyStatDisplay`, `_fitStatusText`, caption) | `chiReduced` | "χ²ᵣ — (model changed)"; status value "—"; tooltip says why | value shown; tooltip adds the note |
| 3 | Status-bar R (`_updateRFactorUI`) | `rFactor` | cleared, tooltip says why | shown |
| 4 | Uncertainty panel (`_validateUncertainties`) | `backendResult` σ, bounds | nothing: no per-parameter rule is judged on the previous model's σ (the Results banner is the one line; the panel's boxes are titled "Uncertainty Warnings" / "Locked Parameters", neither fits) | unchanged |
| 5 | CSV / XLSX (`exportFitTable`) | `chiReduced`, σ | statistic line omitted, σ cells empty, a WARNING line naming why | values kept, a NOTE line |
| 6 | TSV (`exportResults`) | no statistics; Model / Residual computed from the current peaks | a NOTE: those columns are the edited, unfitted model | unchanged |
| 7 | Publication figure (`_doPublicationExport`) | `chiReduced` | χ² annotation omitted | "(unverified)" appended |
| 8 | `_doSaveSpectrum`, `_doSaveFit` | `chi`, `chiReduced`, `rmse`, key, `fittedY` | key saved as always, so a reload judges the result again (a stale save reloads stale); `statisticsState: 'stale'` and a plain `statisticsNote` added; the spectrum file's `fittedY` is the current model + background (it then matches the file's `residuals`, which were always the current model) | `statisticsState: 'unverified'` |
| 9 | `_doSaveProject` (per tab) | the tab's `fitResult` | the same two fields, judged against the RECORD's key | the same |
| 10 | History snapshots (`_autoSnapshot`, `_renderHistoryList`) | `chiReduced`, `rFactor` at snapshot | NOT a consumer: a snapshot is taken only by the three creators, right after a result is applied, so peaks, result and key are one state; restoring one brings back its key and the comparison judges it | — |
| 11 | Chart (`updatePlot`, stored `fittedY` → envelope and residuals) | `fittedY` | not used (edits already null it; Find Peaks apply and undo did not): the envelope is composed from the current peaks | used |
| 12 | Stack tabs (`_buildEntryRenderData` Path A) | the source's `fittedY` | not used; Path A2/B (from the source's peaks) | used |
| 13 | Scattered-starts panel, support verdicts | already keyed by the same key | unchanged | unchanged |
| 14 | Batch Fit summary | the fit's own return value (fresh) | not a consumer of a stored result | — |
| 15 | Quantify | areas from the current peaks, no statistics | not a consumer | — |

Refresh: when the live key changes the Results panel re-renders if its
rendered state differs (it carries `data-stats-state`), and the header,
status bar and R are re-applied — from `updatePlot`, next to
`_refreshStartsEvidence`, so every edit path that repaints reaches it.

Residual, logged for the sealed fit record: each peak carries
`p._backendParams` (the server's per-parameter value, σ and bounds of the
LAST fit), persisted whole with the peak. It is not displayed anywhere
(the σ above come from `fitResult.backendResult`), but it rides in a stale
save; the save's `statisticsState` / `statisticsNote` cover the file.
`autofit/parity.py` reads `_backendParams.gl_ratio.value` from saved peaks,
so it is not stripped here — the sealed record owns per-parameter results.

## 4. Verification

- JS: `tests/js/stale_statistics.test.js` (12 tests: the accessor; every
  creator stamps the key and `_restampSupport` re-stamps the result; the
  Results panel current / stale / unverified, header, status bar, R,
  uncertainty panel on stubs; CSV / XLSX / TSV run for real on stubs;
  chart / stack / figure / spectrum-save curve gates; the saves' fields;
  the refresh re-renders once per state change and writes R on both
  paths). Existing sandboxes in `local_lm_descent`, `fit_acceptance`,
  `unsupported_components` given the accessor (or a `'current'` stub).
- Browser (`scratchpad/browser_check_f1.py`, :5151, committed UCl4-graphite
  project): on load every tab is `unverified` (committed before this unit)
  → note shown, values kept; Run Fit → `current`; centre edit → `stale`:
  header "χ²ᵣ — (model changed)", status "—", "R: —", banner, no σ, no R
  panel, chart envelope NOT the stored curve; CSV head carries the
  WARNING; spectrum save has `statisticsState: 'stale'` + key; undo →
  `current` again; project save → reload → `current` (the key survives the
  round trip); the stale spectrum save reloads `stale`; a stack entry over
  the edited source does not use the stored curve. Auto-Fit C1s Graphite on
  C1s Scan_3 → `current` with every centre locked (the re-stamp). No page
  errors.
- pytest: `test_browser_find_peaks_full_window.py`'s default-path guard
  hand-wrote an R display the injected result did not carry; the fixture
  now stores `rFactor` where a fit puts it. New test there: a KEYED result
  kept over a Find Peaks apply is `stale` (header, status, R, banner).

## 5. Codex rounds

(filled in as they run)
