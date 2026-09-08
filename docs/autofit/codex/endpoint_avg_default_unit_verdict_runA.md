# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 1, RUN A (2026-09-08, reviewed at 1fd0ddb / code 239e8d8)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 76,258.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_review_prompt.txt
Evidence at review time: node 158 pass / 0 fail / 3 known-gap todo; 3 new browser tests watched failing on main; full pytest on the branch worktree 761 passed, 7 skipped.
Round 1: NO-GO x2 — (1) the production Save Fit writer is _doSaveFit(), not TabManager.toJSON(): saved-at-3 -> reload -> 1 (BLOCKER/MAJOR, both); (2) v1 file without a background block inherits 3 (MINOR A / MAJOR B); (3) Find Peaks never sends endpoint_avg and the engine computes at 1 while the UI shows 3 (MAJOR, both; pre-existing plumbing gap made routine by the new default); (4) batch propagation preserves the target's endpointAvg, so mixed defaults propagate inconsistently (MINOR, both; the sealed-record memo already requires propagating it).

**Findings**

The change misses the actual Save Fit writer. A Node probe confirmed that saving at 3 and reloading produces 1. The nine targeted Node tests passed; pytest and Playwright were not run.

The path audit found:

| Path | Endpoint behavior |
|---|---|
| Fresh upload, folder upload, `setSpectrum` → `createTab` | New spectrum gets 3. |
| Project JSON / v2 `fromJSON` → `_loadProjectJSON` | Preserves saved values; missing field stays absent until activation restores 1. |
| Organize Tabs / close-tab / `_syncActiveToRecord` | No inactive-record contamination found. Organize only reorders; capture targets the current active spectrum; closing the active tab clears `activeId` before activating its replacement. |
| `.spec.json` | Missing field, including missing `ui`, resolves to 1 in both record and DOM; valid saved values survive. |
| v1 fit loading | Missing field resolves to 1 **only when `background` exists**. |
| Batch propagation | Preserves the **target’s** endpoint setting; does not copy the source’s. |
| Auto-fit C1s snapshot/restore | Neither snapshots nor writes endpoint averaging. The operation itself leaves that field unchanged and explicitly sends its DOM value to `/api/fit`. |
| Undo / history | Undo restores peaks only. History restores peaks and frozen fit arrays, then captures current UI; neither restores endpoint settings. This is existing behavior, not a new migration to 3. |
| Stack A/A2 / B | A/A2 uses frozen background arrays. B reconstructs from source UI, with missing endpoint averaging resolving to 1 independently of the DOM. |
| Project ZIP / reference overlays | ZIP uses the project serializer/loader; overlays add separate metadata. Neither introduces endpoint defaults. |

No strict saved-background reader was found that rejects the added field. `autofit/reference.py` continues reading project `ui.endpointAvg`, defaulting to 1.

1. **BLOCKER — The production Save Fit path still loses endpoint averaging.**  
   [`_doSaveFit()`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:8779) constructs its own background object without `endpointAvg`. The changed `TabManager.toJSON()` has no production call site in the template and returns version 2.

   Reproduction: fit a fresh spectrum at 3 → Save Fit → reload the downloaded `.fit.json`. The new loader resolves its missing field to 1, reconstructing the saved peaks against a different background. The extracted-function probe confirmed **3 → omitted → 1**.

   Fix the actual writer and test the downloaded artifact. The [browser test](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/tests/test_browser_endpoint_avg_default.py:153) calls the wrong serializer, so all six new tests can pass despite this defect. Conversely, its existing assertions do catch both `.spec.json` with `ui` present but endpoint absent and a v1 loader that always forces 1 despite a saved value.

2. **MAJOR — Find Peaks still computes at 1 while new-spectrum UI and previews use 3.**  
   [`runFindPeaks()`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:14123) sends ROI and method options without reading `#bg-endpoint-avg`. Engine [candidate fitting](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/autofit/engine.py:880) and detection call `_compute_background` without its averaging argument, retaining 1. “Refit my current peaks” likewise defaults to 1 unless manually supplied through advanced options.

   On a fresh tab, applied suggestions are consequently previewed against averaging 3 although fitted at 1. The missing plumbing predates this change, but the new default makes divergence routine. The claim that the frontend “always sends endpoint_avg” is false. Wiring requires backend support too: model comparison’s option whitelist currently rejects `endpoint_avg`.

3. **MINOR — Accepted v1 files without a background block inherit 3.**  
   The fallback is inside [`if (data.background)`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:3294). Loading an accepted peaks-only legacy file onto a fresh spectrum leaves endpoint averaging at 3; the probe confirmed this. This is an untested exception to the stated missing-field contract. Resolve the endpoint independently of that conditional, or explicitly reject incomplete fit files. I found no evidence that the normal historical writer emitted this shape.

4. **MINOR — Batch propagation now routinely mixes averaging settings across targets.**  
   [`propagateFitUi()`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/static/js/batch_propagation.js:20) deliberately preserves target `endpointAvg`; existing tests pin that behavior. A legacy source propagated to fresh targets leaves them at 3; a new source propagated to legacy targets leaves them absent → 1. There is no DOM leakage, but “propagate background settings” does not produce identical averaging. This existing policy becomes consequential when defaults differ by tab origin and should be explicitly documented or reconsidered.

VERDICT: NO-GO — Save Fit loses the new endpoint setting on round-trip, and Find Peaks continues fitting at 1 while fresh-spectrum previews use 3.
