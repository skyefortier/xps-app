# Codex adversarial review — endpoint-averaging default 3 (feature-endpoint-avg-default-3) — round 1, RUN B (2026-09-08, reviewed at 1fd0ddb / code 239e8d8)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 83,167.
Prompt: docs/autofit/codex/endpoint_avg_default_unit_review_prompt.txt
Evidence at review time: node 158 pass / 0 fail / 3 known-gap todo; 3 new browser tests watched failing on main; full pytest on the branch worktree 761 passed, 7 skipped.
Round 1: NO-GO x2 — (1) the production Save Fit writer is _doSaveFit(), not TabManager.toJSON(): saved-at-3 -> reload -> 1 (BLOCKER/MAJOR, both); (2) v1 file without a background block inherits 3 (MINOR A / MAJOR B); (3) Find Peaks never sends endpoint_avg and the engine computes at 1 while the UI shows 3 (MAJOR, both; pre-existing plumbing gap made routine by the new default); (4) batch propagation preserves the target's endpointAvg, so mixed defaults propagate inconsistently (MINOR, both; the sealed-record memo already requires propagating it).

**Findings**

1. **MAJOR — The actual Save Fit writer still drops `endpointAvg`.** The UI calls [`_doSaveFit()`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:8767), which constructs its own background block without this field. The patched `TabManager.toJSON()` is not that writer. Consequently, **fit at 3 → Save Fit → reload resolves to 1**, changing the reconstructed background. A read-only Node probe using the actual writer and loader confirmed this. The [new browser test](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/tests/test_browser_endpoint_avg_default.py:153) tests the wrong writer, so it passes despite this failure. Add the field to `_doSaveFit()` and test the downloaded file’s round-trip.

2. **MAJOR — A v1 file without a background block inherits 3.** In [`fromJSON()`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:3295), the legacy assignment is inside `if (data.background)`. The accepted `{version: 1, peaks: [...]}` path therefore retains the fresh target’s `endpointAvg: '3'` and redraws the loaded peaks against it. The Node probe confirmed record and DOM both remain 3. Resolve the missing endpoint independently of whether the background block exists. Neither browser loader test covers this case.

3. **MAJOR — Find Peaks still fits at 1 while a fresh spectrum displays 3.** [`runFindPeaks()`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/templates/index.html:14124) sends the advanced options JSON without reading `#bg-endpoint-avg`. Default options omit it. The least-squares method defaults to 1; model comparison calls [`_compute_background()` without the argument](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/autofit/engine.py:880), also yielding 1. Model comparison’s option whitelist additionally rejects `endpoint_avg`, so adding it only to the frontend payload is insufficient. Applying suggestions to a fresh, unfitted tab reconstructs their background using the UI’s 3. This omission predates the patch, but the patch introduces the default mismatch. The claim that the frontend always sends the value is false for these flows.

4. **MINOR — Batch propagation preserves the target’s endpoint setting.** [`propagateFitUi()`](/Users/skyefortier/xps-app/.claude/worktrees/feature-endpoint-avg-default-3/static/js/batch_propagation.js:19) does not copy `endpointAvg`; its existing test explicitly requires target preservation. A legacy source propagating to a fresh target therefore fits at 3, while a fresh source propagating to a legacy target fits at 1. It uses neither an undefined source fallback nor an accidental DOM capture. This is existing behavior, now routinely exposed by mixed defaults; explicitly decide whether propagating the background should also propagate its averaging setting.

The remaining path audit found:

| Path | Endpoint behavior |
|---|---|
| Fresh upload, folder upload, `setSpectrum` | Reach `createTab`; record and DOM start at 3. |
| Project JSON / v2 multi-tab restore | Actual deserializer is `_loadProjectJSON` around line 9275; line 3235 is serialization. Missing stays absent until DOM restoration or background reconstruction resolves it to 1. Valid saved values survive. |
| Activation / Organize Tabs / close-tab | No pre-activation contamination found. Activation captures the outgoing record before changing `activeId`; Organize only reorders; closing the active tab clears its ID before replacement activation. |
| `.spec.json` | Missing UI or missing field resolves to 1; saved values win. DOM restoration occurs synchronously before subsequent capture. |
| C1s graphite auto-fit | Reads and sends the endpoint explicitly. Snapshot/rollback omit the field, but this operation does not mutate it; inactive-tab rollback preserves it through the UI spread. |
| Undo / history | Undo restores peaks only. History restores peaks and frozen fit arrays, then captures current UI; neither restores endpoint settings. This is an existing limitation, not a new default assignment. |
| Stack A/A2 | Uses frozen background arrays; endpoint defaults do not alter them. |
| Stack B | Uses source UI, with missing endpoint resolving to 1—even for never-activated legacy sources. |
| Spectrum/project save, ZIP, overlays | Spectrum/project writers preserve UI. ZIP feeds records through the same project loader; overlays do not write endpoint settings. Stack tabs’ own value of 1 is inert. |

No strict background-block reader rejecting the additive field was found. `autofit/reference.py` reads project `ui.endpointAvg` with fallback 1 and is unaffected.

The browser tests **do** cover an existing `.spec.json` UI block lacking the field and a v1 saved value of 9; those specific wrong implementations would fail. They miss the actual save writer, absent v1 background block, Find Peaks, and batch behavior. Project lifecycle and stack fallback have no new behavioral coverage.

Validation was source inspection plus isolated Node probes with DOM stubs; pytest and Playwright were not run.

VERDICT: NO-GO — Save Fit loses the setting, a supported legacy loader path inherits 3, and Find Peaks still computes at 1 despite the new UI default.
