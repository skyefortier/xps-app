OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0d98a-5ed3-7d00-83d2-2409a49d6ad3
--------
user
RECHECK, round 2, of unit fix-roi-clamp: git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round 1 (docs/autofit/codex/roi_clamp_verdict_runA.md / runB.md, both NO-GO) confirmed the warn-only reading of "clamp" and no writes to the fields, fit inputs, saves or evidence key, and found: (1) MAJOR Find Peaks' ROI auto-fill (_fpSyncSelectionUI) writes the fields without an input event, leaving the hint and badges stale; (2) MAJOR the plan's "manual fit and Find Peaks select identical points" ignored uploadToBackend's 4-dp rounding (manual filters then uploads; Find Peaks uploads then the server filters); (3) the badge tooltip revealed the centre of an unsupported component; (4) MINOR closing the last tab left the hint showing.

What changed (plan §3 and §8; commit "fix(roi): Codex round 1"): _fpSyncSelectionUI calls _refreshRoiAndCentreWarnings() after its write; every other programmatic writer of the ROI fields was listed and checked (maxROI, autoSetROI, _autoFitRestore and updateChargeCorrection redraw in the same function; the three callers of _restoreUI redraw right after) - verify that list; _outsideDataBadge(p, st, unsupported) omits the number for an unsupported component (the patcher passes _isUnsupported(p)); renderEmptyChart clears the hint; plan §3 now states the equivalence exactly (identical except an energy within 5e-5 eV of an ROI edge; pre-existing; logged, not changed) and tests pin both directions. The browser check was extended to the real Find Peaks selection path with the server's /api/analyze/meta coverage (C 1s suggests 278-298; the hint names 279.16-297.96), an unsupported badge, and closing every tab: 16/16. The rewritten required test: 20 of 20 separate-process runs pass (plan §6 now says the construction poses the premise rather than reproducing the free local minimum). JS suite 411 tests, 406 pass, 5 todo.

Verify each round-1 item is closed, then look again for: any writer of roi-min/roi-max or of a peak centre that neither redraws nor refreshes (grep for .value = on those ids, set('roi-...'), and for p.center = / updatePeakParam(... 'center' ... paths that bypass updatePlot, incl. Find Peaks apply, Auto-Fit apply, history/undo restore, alternative-solution adoption, linked-child sync, Batch Fit target copies); whether the unsupported rule is applied consistently (a linked child of an unsupported root; a stale verdict - _isUnsupported compares the fit key); whether the empty-state clear misses a path (a stack tab with no sources; a spectrum tab with rawBE of length 1); the hint's escaping (textContent) and the badge's (title via _escAttr); anything else in the unit's diff still open, and docs vs code.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll verify the round-1 fixes, audit the ROI and peak-centre update paths, then check edge cases and docs against the code. I’ll keep the review read-only and finish with a ranked verdict.

exec
/bin/zsh -lc "pwd; rg --files -g 'AGENTS.md' -g '*roi*' -g '*clamp*'; git status --short; git diff --stat main..HEAD" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md
tests/test_browser_batch_roi.py
tests/js/roi_clamp_centre_warning.test.js
docs/autofit/codex/roi_clamp_review_prompt.txt
docs/autofit/codex/roi_clamp_verdict_runB.md
docs/autofit/codex/roi_clamp_r2_verdict_runB.md
docs/autofit/codex/fe2p_roi_widen_verdict_runA.md
docs/autofit/codex/roi_clamp_verdict_runA.md
docs/autofit/codex/fe2p_roi_widen_review_prompt.txt
docs/autofit/codex/roi_clamp_r2_verdict_runA.md
docs/autofit/codex/roi_clamp_recheck_prompt.txt
docs/autofit/codex/fe2p_roi_widen_verdict_runB.md
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-begxkKlB' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-3fn8nZCc' (errno=Operation not permitted)
?? docs/autofit/codex/roi_clamp_r2_verdict_runA.md
?? docs/autofit/codex/roi_clamp_r2_verdict_runB.md
?? docs/autofit/codex/roi_clamp_recheck_prompt.txt
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-PL7d0CU6' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Lm73eUlf' (errno=Operation not permitted)
 CLAUDE.md                                          |   11 +
 docs/autofit/codex/roi_clamp_review_prompt.txt     |   51 +
 docs/autofit/codex/roi_clamp_verdict_runA.md       | 4266 +++++++++++++
 docs/autofit/codex/roi_clamp_verdict_runB.md       | 6440 ++++++++++++++++++++
 .../2026-09-25-roi-clamp-and-centre-warning.md     |  176 +
 templates/index.html                               |  108 +-
 tests/js/roi_clamp_centre_warning.test.js          |  165 +
 tests/js/unsupported_components.test.js            |    1 +
 tests/test_component_required.py                   |   31 +-
 9 files changed, 11238 insertions(+), 11 deletions(-)

exec
/bin/zsh -lc 'for d in /Users /Users/skyefortier /Users/skyefortier/xps-app /Users/skyefortier/xps-app/.claude /Users/skyefortier/xps-app/.claude/worktrees /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp; do if [ -f "$d/AGENTS.md" ]; then cat "$d/AGENTS.md"; fi; done
git diff main..HEAD -- templates/index.html tests/js/roi_clamp_centre_warning.test.js tests/js/unsupported_components.test.js tests/test_component_required.py CLAUDE.md docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DnGYK02M' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6KFbcamD' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index d4550d8..7e8b8bd 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -814,6 +814,17 @@ invariants worth knowing before touching the code:
 - **Auto-Fit C1s Graphite** (Actions menu): one-click C1s peak model
   + charge correction. Enabled only when the active ROI midpoint is in
   270–315 eV.
+- **ROI past the data / centre outside the data** (2026-09-25, warn only):
+  `getROIData()` has always clamped an ROI to the data it selects; the page
+  now SAYS so under the ROI fields ("ROI extends past your data — clipped
+  to X–Y eV" when a field reaches more than one sampling step past the
+  data; amber when min > max or the window misses the data) and badges a
+  peak card whose centre lies outside the selected data ("outside data").
+  Neither the fields nor the peaks are ever moved; the fit, Find Peaks
+  (same inclusive mask on the same corrected energies) and saves read the
+  ROI exactly as before. `_roiWindowStatus` / `_refreshRoiAndCentreWarnings`,
+  refreshed in place from `updatePlot`; plan
+  `docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md`.
 - **Manual anchor background**: place anchors on the chart for
   per-spectrum hand-tuned background curves; persisted as
   `tab.manualAnchors`.
diff --git a/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md b/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md
new file mode 100644
index 0000000..b27bd6a
--- /dev/null
+++ b/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md
@@ -0,0 +1,176 @@
+# ROI past the data + peak centre outside the data — warn, don't reinterpret (2026-09-25)
+
+Branch `fix-roi-clamp` off main `c4015ae` (DS+G evaluator deployed). Owner's
+brief: "ROI CLAMP + CENTRE-OUTSIDE-DATA WARNING (one unit, UI only, no
+fitting math). (1) ROI beyond the data range silently clips to the data edge,
+which users read as truncation. Clamp the ROI to the data range and show a
+quiet hint ('ROI extends past your data — clipped to X–Y eV'). roi-min/roi-max
+are shared by manual fit and Find Peaks, so one fix covers both — verify
+that. Check the saved-ROI restore path (ui.roiMin / roiMax) so loading an
+old file doesn't silently change behaviour. (2) Peak centre outside the data
+window: warn on the peak card. It is the only way to reach the §3c DS+G
+limit. Do not auto-move the user's ROI or peaks. Warn; don't reinterpret.
+Enumerate the consumer sites first."
+
+Also in this branch: the flaky required-anchor test (commit 2e7cc33; §6).
+
+## 1. What "clipped" means today, precisely
+
+`getROIData()` keeps the corrected energies (raw − `ccShift`) that lie in
+[roi-min, roi-max], inclusive; an empty field is ±∞. An ROI past the data
+therefore selects the data up to its edge: the fit, the background, the
+chart's fitted region and every area already use the CLAMPED window. The
+defect is that nothing says so — the fields still read, say, 270–320 eV
+over data that stop at 280–295 eV. So "clamp" is already the behaviour; the
+unit makes it VISIBLE, and leaves the typed values alone (the owner: do not
+auto-move the ROI).
+
+## 2. Consumer sites — every reader of the ROI and of a peak centre
+
+ROI readers (`roi-min`, `roi-max`, `ui.roiMin`, `ui.roiMax`, `getROIData`):
+
+| # | site | what it reads | window semantics | this unit |
+|---|---|---|---|---|
+| 1 | `getROIData` | DOM fields | inclusive filter of corrected BE; empty = ±∞; min > max → EMPTY | unchanged; the hint's source of truth |
+| 2 | `runFit` (Run Fit, `/api/fit`) | `getROIData` | as 1 (the request carries the filtered arrays) | unchanged |
+| 3 | `runFitLocal` via Batch Fit `runPropagation` | `getROIData` on each target, target keeps its own ROI (`propagateFitUi` keep) | as 1 | unchanged; summary row notes a clipped target |
+| 4 | Find Peaks `/api/analyze` payload (`fpMethodMeta` block) | DOM fields as numbers + `getCorrectedBE()` | server `app._validate_analyze_request`: `(corrected >= be_min) & (corrected <= be_max)` — the SAME inclusive mask on the SAME corrected frame | unchanged — verified identical to 1 (§3); an EMPTY field differs (page: full range; server: 400 "must be numbers") — logged, not changed |
+| 5 | Find Peaks ROI auto-fill (`coverage` block) | writes `entries[0].roi.be_min/max` (curated nominal window, can exceed the data) | — | unchanged; the hint now fires when the suggested window overshoots |
+| 6 | `updatePlot` (chart fitted region, preview) | `getROIData` | as 1 | hosts the hint + centre-warning refresh |
+| 7 | `renderPeakList` / `_patchPeakCardsForSupport` (area %) | `getROIData` | as 1 | cards get the centre warning |
+| 8 | `renderResults` fallback grid, `exportResults`, figure export, `_doSaveSpectrum`, `applyAutoFitResult`, `runAutoFitC1sGraphite`, `handleChartClick` | `getROIData` | as 1 | unchanged |
+| 9 | `zoomToROI` | DOM fields, swapped if min > max | axis only | unchanged |
+| 10 | `isC1sTab` (Auto-Fit enable gate) | `ui.roiMin/roiMax` MIDPOINT of the typed values | typed window, not the data it selects | unchanged — logged: with an ROI past the data the gate judges a window the fit never sees |
+| 11 | `_buildEntryRenderData` Path B (stack tabs) | `ui.roiMin/roiMax`, SWAPPED if min > max | differs from 1 for an inverted ROI (1 selects nothing) | unchanged — logged; the source tab's hint says "no data selected" |
+| 12 | `_captureUI` / `_restoreUI` / `toJSON` / `fromJSON` / `_doSaveFit` / `_autoFitSnapshot` / `_autoFitRestore` | read/write the field values verbatim | — | unchanged: loading a file restores the same numbers and the fit selects the same data as before; the hint is computed from the live fields and data, so an old file only GAINS a message |
+| 13 | `updateChargeCorrection` | shifts both fields by the correction delta | ROI follows the data | unchanged; the hint re-evaluates after the redraw |
+| 14 | `autoSetROI` / `maxROI` | write fields from the data range (`toFixed(1)`) | may land a rounding step inside or outside the data edge | unchanged; the hint's criterion (§4) ignores sub-step overshoot |
+| 15 | `_STARTS_UI_FIELDS` (fit-evidence key) | `roiMin`, `roiMax` | — | unchanged (the hint writes nothing into the model or key) |
+| 16 | Python twin `autofit/reference.py` `ReferenceFit._roi_bounds` / `roi_mask` | saved `ui` | inclusive, empty = ±∞ | unchanged |
+| 17 | `_getSuggestedPresets` | `bg-start` / `bg-end` (not the ROI) | — | not an ROI reader (named `roiMin` locally) |
+
+Peak-centre readers relevant to "outside the data": the card header and
+summary (`renderPeakList`, patched in place by `_patchPeakCardsForSupport`).
+The data window a component is fitted against is the ROI selection of
+row 1, so the warning compares `p.center` with min/max of `getROIData().be`
+— the grid the request carries.
+
+## 3. "One fix covers both" — verified, with one exact qualification
+
+Manual fit (row 2) and Find Peaks (row 4) apply the same inclusive
+[min, max] filter to the same corrected energies, with one difference in
+ORDER (Codex round 1): manual fit filters first and then uploads the
+selection rounded to 4 dp (`uploadToBackend`), while Find Peaks uploads
+the corrected energies rounded to 4 dp and the server filters those. The
+selections are therefore identical except for an energy lying within
+5e-5 eV of an ROI edge, which the rounding can move across it (Codex's
+reproducer: 21 energies 280.00004 + 0.1 i, ROI 280.00002–282.1 — manual 21
+points, Find Peaks 20). Real ROIs are typed to 0.1–0.5 eV and energies
+rarely carry more than 4 decimals, so the one window the hint names is the
+window both use for every ROI a user sets; both directions are pinned in
+`tests/js/roi_clamp_centre_warning.test.js`. The edge divergence is
+pre-existing and is not changed here (it would change Find Peaks'
+request); logged with the empty-field divergence (row 4) for the
+fail-open sweep.
+
+## 4. The hint
+
+Under the ROI inputs, one line, computed on every redraw of a spectrum tab
+(hidden on stack tabs):
+
+- ROI reaches more than ONE SAMPLING STEP past the data on either side
+  (a step = median |Δ corrected BE|; within a step there is no sample the
+  window could have included, so a `toFixed(1)` rounding of the edge is not
+  "past the data" — a grid-relative criterion, not an intensity threshold):
+  quiet — "ROI extends past your data — clipped to X–Y eV." (X, Y = the
+  first and last selected energies);
+- min > max: amber — "BE min is above BE max — no data is selected.";
+- no overlap: amber — "ROI does not overlap your data (X–Y eV) — no data is
+  selected.";
+- otherwise nothing.
+
+Measured on the committed projects (166 spectrum tabs): 30 show the quiet
+hint (overshoot median 0.39 eV, max 4.85 eV; 8 over 1 eV), none is
+inverted or disjoint.
+
+## 5. The centre warning
+
+A peak whose centre lies outside [min, max] of the selected energies gets a
+badge on its card, "outside data", with a tooltip naming the centre and the
+window and saying that a component centred outside the measured data is
+almost always a placement error — the fit sees only its tail. Nothing is
+moved. Patched in place from every redraw (never a re-render under a typing
+student) and on card creation. Measured: 0 of 530 committed peaks.
+
+## 6. The flaky test (same branch, commit 2e7cc33)
+
+`test_component_required.py::test_a_redundant_anchor_is_supported_but_not_required`
+passed 2 of 3 on main. Cause: NOT an unseeded path — every process drew the
+identical seed; the variation is Trust-Region's documented last-digit
+jitter. It reached the assertion because the construction did not
+reproduce its own premise: starting the other components at the exact
+truth lets the fit drive the anchor to residue (~0.01), so the held-others
+F landed at 11–24 against the threshold of 10. Codex's original
+reproduction had a large anchor (1,081–1,894, F ≈ 1e6) because that fit
+stopped in a minimum where the anchor carries weight. Fixed by holding the
+anchor at 1,500 (inside that range) so the fit must carry it,
+parametrised over Trust-Region and Levenberg-Marquardt: F ≈ 4e7, refit
+without it ~1e4× better, 5 of 5 runs of the file pass, and 20 of 20
+separate-process runs of the test itself pass (after Codex round 1).
+Holding the anchor POSES the premise (a fit carrying a large redundant
+anchor) rather than reproducing the free local minimum Codex found; the
+property under test — a refit without the component fits as well, so it
+is not required, even though the held-others statistic supports it — is
+the same.
+
+## 7. Verification
+
+- `tests/js/roi_clamp_centre_warning.test.js` (12): every hint state, the
+  sub-step criterion, the corrected frame, a descending grid, the centre
+  check incl. its edges and the no-data case, and structural guards that
+  the new helpers assign no field value, move no peak, write no fit state
+  and trigger no edit or re-render; `getROIData`'s filter and the Find
+  Peaks payload pinned unchanged; Batch Fit reads the status BESIDE
+  `getROIData`.
+- JS suite (after round 1): 411 tests, 406 pass, 0 fail, 5 todo (the
+  documented LACX gap and the scalar DS+G evaluator).
+- Browser check (`browser_check_roi.py`, dev gunicorn :5151): the committed
+  UCl4-graphite C1s Scan loads with its saved ROI 279.0–298.5 over data
+  279.16–298.16 — fields unchanged, the fit selects the same 191 points,
+  the quiet hint appears; inside → no hint; inverted and disjoint → amber;
+  270–320 → hint, fields left at 270 / 320; a centre moved to 296.5 eV →
+  "outside data" badge patched into the SAME card element, centre
+  unmoved, cleared when it returns, present after a full re-render; a tab
+  switch and back restores the fields verbatim and recomputes the hint;
+  Run Fit's grid equals `getROIData()`'s; a stack tab hides the hint;
+  Batch Fit onto C1s Scan_8 converges and its summary row names the
+  clipped window; no page errors.
+- Python suite: 993 passed, 7 skipped on the round-0 tree; re-run on the
+  round-1 commit recorded below.
+
+## 8. Codex rounds
+
+**Round 1 (`docs/autofit/codex/roi_clamp_verdict_run{A,B}.md`): NO-GO ×2.**
+Both confirmed the warn-only reading of "clamp" and found no write to the
+fields, the fit inputs, saves or the evidence key. Fixed:
+1. MAJOR — Find Peaks' ROI auto-fill (`_fpSyncSelectionUI`, table row 5)
+   writes the fields programmatically, which fires no `input` event, so
+   the hint and badges stayed stale. It now refreshes them. Every other
+   programmatic writer was checked: `maxROI`, `autoSetROI`,
+   `_autoFitRestore` and `updateChargeCorrection` redraw in the same
+   function; the three callers of `_restoreUI` redraw right after.
+   Browser-checked on the real selection path (C 1s suggests 278–298; the
+   hint names 279.16–297.96).
+2. MAJOR — §3's "identical" was wrong at the rounding edge; stated exactly
+   above and pinned both ways.
+3. MAJOR/MINOR — the badge's tooltip revealed the centre of a component
+   step (b) suppresses; it now warns without the number for an
+   unsupported component. Pinned and browser-checked.
+4. MINOR — closing the last tab left the hint showing (`closeTab` goes
+   straight to `renderEmptyChart`, as does `updatePlot`'s no-data
+   branch); `renderEmptyChart` now clears it.
+Also: both reviewers noted that five runs do not prove the flake gone and
+that holding the anchor poses the premise rather than reproducing the
+free local minimum. The second is stated in the test's docstring; for the
+first, 20 more separate-process runs are recorded in §6.
+
diff --git a/templates/index.html b/templates/index.html
index 07977d7..11ef805 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -816,6 +816,11 @@
   }
 
   /* Multiplet link indicator */
+  /* ROI past the data / centre outside the data (2026-09-25): warn, never move */
+  .roi-hint { font-size: 10px; line-height: 1.4; color: var(--text3); margin: 2px 0 6px; }
+  .roi-hint.amber { color: var(--amber); }
+  .outside-data-badge { font-size: 9px; padding: 1px 4px; border-radius: 3px; margin-left: 4px;
+    color: var(--amber); border: 1px solid var(--amber); white-space: nowrap; cursor: help; }
   .unsupported-badge {
     font-size: 9px;
     padding: 1px 5px;
@@ -2063,6 +2068,7 @@
                 <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
               </div>
             </div>
+            <div id="roi-hint" class="roi-hint" style="display:none" aria-live="polite"></div>
             <div style="display:flex;gap:6px">
               <button class="btn btn-sm" onclick="autoSetROI()">Auto from data</button>
               <button class="btn btn-sm" onclick="maxROI()" title="Set ROI to the full raw spectrum range">Max</button>
@@ -5069,6 +5075,93 @@ function getROIData() {
   return { be, inten };
 }
 
+// ── ROI past the data / centre outside the data (2026-09-25) ─────────────
+// WARN, NEVER REINTERPRET. getROIData() already selects the corrected
+// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
+// the data in every fit, background, area and export — the defect was that
+// nothing said so. This reports the window actually used; it writes nothing
+// back into the fields, the peaks or the fit-evidence key. Find Peaks sends
+// the same two numbers against the same corrected energies to a server mask
+// of the same inclusive form, so this one window is the one both use.
+// Plan: docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
+function _roiWindowStatus() {
+  const corrBE = (typeof getCorrectedBE === 'function' && state.rawBE && state.rawBE.length) ? getCorrectedBE() : [];
+  if (!corrBE.length) return { state: 'no-data' };
+  let dMin = Infinity, dMax = -Infinity;
+  for (const v of corrBE) { if (v < dMin) dMin = v; if (v > dMax) dMax = v; }
+  const lo = parseFloat(document.getElementById('roi-min').value);
+  const hi = parseFloat(document.getElementById('roi-max').value);
+  const { be } = getROIData();
+  let sMin = Infinity, sMax = -Infinity;
+  for (const v of be) { if (v < sMin) sMin = v; if (v > sMax) sMax = v; }
+  const base = { dMin, dMax, lo, hi, sMin, sMax, n: be.length };
+  if (Number.isFinite(lo) && Number.isFinite(hi) && lo > hi) return { ...base, state: 'inverted' };
+  if (!be.length) return { ...base, state: 'no-overlap' };
+  // one sampling step = median |Δ corrected BE|: within a step there is no
+  // sample the window could have included, so a toFixed(1) rounding of an
+  // edge is not "past the data" (a grid-relative criterion, not a threshold
+  // on intensity)
+  const d = [];
+  for (let i = 1; i < corrBE.length; i++) d.push(Math.abs(corrBE[i] - corrBE[i - 1]));
+  d.sort((a, b) => a - b);
+  const step = d.length ? (d.length % 2 ? d[(d.length - 1) / 2] : 0.5 * (d[d.length / 2 - 1] + d[d.length / 2])) : 0;
+  const past = (Number.isFinite(lo) && lo < dMin - step) || (Number.isFinite(hi) && hi > dMax + step);
+  return { ...base, step, state: past ? 'past' : 'ok' };
+}
+function _roiHintFor(st) {
+  const f = v => v.toFixed(2);
+  if (st.state === 'past') return { cls: '', text: `ROI extends past your data — clipped to ${f(st.sMin)}–${f(st.sMax)} eV.` };
+  if (st.state === 'inverted') return { cls: 'amber', text: 'BE min is above BE max — no data is selected.' };
+  if (st.state === 'no-overlap') return { cls: 'amber', text: `ROI does not overlap your data (${f(st.dMin)}–${f(st.dMax)} eV) — no data is selected.` };
+  return null;
+}
+function _refreshRoiHint(st) {
+  const el = document.getElementById('roi-hint');
+  if (!el) return;
+  const h = st ? _roiHintFor(st) : null;
+  if (!h) { if (el.style.display !== 'none') { el.style.display = 'none'; el.textContent = ''; } return; }
+  if (el.textContent !== h.text) el.textContent = h.text;
+  el.className = 'roi-hint' + (h.cls ? ' ' + h.cls : '');
+  el.style.display = '';
+}
+// A component centred outside the selected data: the fit sees only its tail.
+// Almost always a placement error — and the one way to reach the DS+G
+// normalisation limit (plan 2026-09-22-dsg-page-evaluator §3c).
+function _centreOutsideData(p, st) {
+  return !!(st && st.n > 0 && Number.isFinite(p.center) && (p.center < st.sMin || p.center > st.sMax));
+}
+function _outsideDataBadge(p, st, unsupported) {
+  // a component the fit did not determine has its centre suppressed
+  // everywhere (unit step (b)); the warning must not report it either
+  const where = unsupported ? 'Its centre lies' : `Centre ${p.center.toFixed(2)} eV lies`;
+  const tip = `${where} outside the fitted data (${st.sMin.toFixed(2)}–${st.sMax.toFixed(2)} eV). `
+    + 'A component centred outside the measured data is almost always a placement error: the fit sees only its tail. Nothing has been moved.';
+  return `<span class="outside-data-badge" data-peak-id="${p.id}" title="${_escAttr(tip)}">outside data</span>`;
+}
+// Patched IN PLACE (the student may be typing in a card): add, update or
+// remove each card's badge; never re-render the list.
+function _patchPeakCardsForCentre(st) {
+  for (const p of state.peaks) {
+    const item = document.getElementById('peak-item-' + p.id);
+    if (!item) continue;
+    const name = item.querySelector('.peak-name');
+    if (!name) continue;
+    const badge = name.querySelector('.outside-data-badge');
+    const out = _centreOutsideData(p, st);
+    if (out) {
+      const html = _outsideDataBadge(p, st, typeof _isUnsupported === 'function' && _isUnsupported(p));
+      if (!badge) name.insertAdjacentHTML('beforeend', html);
+      else { const tmp = document.createElement('span'); tmp.innerHTML = html; const t = tmp.firstChild.getAttribute('title'); if (badge.getAttribute('title') !== t) badge.setAttribute('title', t); }
+    } else if (badge) badge.remove();
+  }
+}
+function _refreshRoiAndCentreWarnings() {
+  const st = _roiWindowStatus();
+  _refreshRoiHint(st);
+  _patchPeakCardsForCentre(st);
+  return st;
+}
+
 function maxROI() {
   if (!state.rawBE.length) return;
   const be = getCorrectedBE();
@@ -6054,6 +6147,7 @@ function renderPeakList() {
     item.addEventListener('mouseenter', () => _highlightChartPeak(p.id, true));
     item.addEventListener('mouseleave', () => _highlightChartPeak(p.id, false));
   }
+  if (state.rawBE && state.rawBE.length) _patchPeakCardsForCentre(_roiWindowStatus());
 }
 
 function renderPeakForm(p) {
@@ -9324,6 +9418,7 @@ function updatePlot() {
     const _emptyEl = document.getElementById('stack-empty-state');
     const _canvas = document.getElementById('mainChart');
     if (isStackTab(_activeTab)) {
+      _refreshRoiHint(null);   // a stack tab has no ROI of its own
       _updateStackChart(_activeTab);
       return;
     } else {
@@ -9477,6 +9572,7 @@ function updatePlot() {
   }
 
   _refreshStartsEvidence(false, true);   // background / ROI controls only repaint the chart: keep the visible consumers honest (fromPlot: the chart itself is being rebuilt)
+  _refreshRoiAndCentreWarnings();         // ROI past the data / centre outside the data: warn, never move
   // History snapshot preview overlay (cyan dashed, drawn on top)
   if (_historyPreview && _historyPreview.peaks && _historyPreview.peaks.length && plotBE.length) {
     const prevPeakY = evalAllPeaks(plotBE, _historyPreview.peaks);
@@ -9807,6 +9903,7 @@ function updatePlot() {
 }
 
 function renderEmptyChart() {
+  if (typeof _refreshRoiHint === 'function') _refreshRoiHint(null);   // no data: no window to describe
   // Reference mode (A7): overlays selected + no spectrum loaded (palette open or
   // closed) → draw markers on a labeled 0–1200 eV axis instead of the onboarding
   // card. No overlays → the onboarding card (the chart is torn down below).
@@ -11997,6 +12094,7 @@ async function runPropagation() {
     }
 
     // Run local fit
+    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
     const { be, inten } = getROIData();
     const bgI = computeBackground(be, inten);
     const bgSub = inten.map((v, idx) => v - bgI[idx]);
@@ -12008,7 +12106,7 @@ async function runPropagation() {
     // Read the statistic from the fit's own return value, not from live
     // state: the active tab can change while the fit runs.
     const ok = !!(outcome && outcome.success);
-    results.push({ name: tgt.name, ok,
+    results.push({ name: tgt.name, ok, roiHint: _roiHintFor(roiSt),
                    chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
                    message: ok ? null : ((outcome && outcome.message) || 'local fit did not converge') });
 
@@ -12023,9 +12121,10 @@ async function runPropagation() {
   const nOk = results.filter(r => r.ok).length;
   const nFail = results.length - nOk;
   prog.textContent = `Batch complete: ${nOk} converged as starting points, ${nFail} not fitted. Run Fit on each spectrum before reporting.`;
+  const roiNote = r => r.roiHint ? ` <span class="roi-hint${r.roiHint.cls ? ' ' + r.roiHint.cls : ''}" style="display:inline">${_escHtml(r.roiHint.text)}</span>` : '';
   summary.innerHTML = results.map(r => r.ok
-    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)</div>`
-    : `<div class="prop-row" style="color:var(--red,#f87171)">${_escHtml(r.name)}: NOT fitted &mdash; ${_escHtml(r.message)} (model copied, no result stored)</div>`
+    ? `<div class="prop-row">${_escHtml(r.name)}: converged &mdash; &#967;&#178;<sub>r</sub> = ${r.chi != null ? r.chi.toFixed(3) : 'n/a'} (local fit: a starting point, not a reportable result)${roiNote(r)}</div>`
+    : `<div class="prop-row" style="color:var(--red,#f87171)">${_escHtml(r.name)}: NOT fitted &mdash; ${_escHtml(r.message)} (model copied, no result stored)${roiNote(r)}</div>`
   ).join('') + `<div class="prop-row" style="color:var(--red,#f87171);margin-top:4px">&#9888; Charge corrections marked in red need verification</div>`;
   summary.style.display = 'block';
   btn.disabled = false;
@@ -15400,6 +15499,9 @@ function _fpSyncSelectionUI() {
   if (entries.length === 1 && entries[0].roi) {
     document.getElementById('roi-min').value = entries[0].roi.be_min;
     document.getElementById('roi-max').value = entries[0].roi.be_max;
+    // a programmatic write fires no 'input' event: the hint and the card
+    // badges describe the new window now (Codex round 1 of fix-roi-clamp)
+    if (typeof _refreshRoiAndCentreWarnings === 'function' && state.rawBE && state.rawBE.length) _refreshRoiAndCentreWarnings();
   }
   _fpRenderPtGrid(document.getElementById('fp-regions-filter').value);
   _fpRenderExpandedPanel();
diff --git a/tests/js/roi_clamp_centre_warning.test.js b/tests/js/roi_clamp_centre_warning.test.js
new file mode 100644
index 0000000..c17fae0
--- /dev/null
+++ b/tests/js/roi_clamp_centre_warning.test.js
@@ -0,0 +1,165 @@
+// ROI past the data / peak centre outside the data (2026-09-25).
+// WARN, NEVER REINTERPRET: the helpers report the window getROIData()
+// already uses and write nothing back. Plan:
+// docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md.
+const { test } = require('node:test');
+const assert = require('node:assert');
+const fs = require('node:fs');
+const path = require('node:path');
+
+const html = fs.readFileSync(path.join(__dirname, '../../templates/index.html'), 'utf8');
+const lines = html.split('\n');
+function extractFn(name) {
+  const re = new RegExp('^(async )?function ' + name + '\\(');
+  const start = lines.findIndex(l => re.test(l));
+  assert.ok(start >= 0, `function ${name} not found`);
+  let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) {
+    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
+    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
+  }
+  assert.fail('unbalanced ' + name);
+}
+const NAMES = ['getCorrectedBE', 'getROIData', '_roiWindowStatus', '_roiHintFor', '_refreshRoiHint', '_centreOutsideData', '_outsideDataBadge', '_escAttr'];
+const FP_UPLOAD_ROUND = v => +v.toFixed(4);   // uploadToBackend: energies to 4 dp
+function makeEnv({ rawBE, ccShift = 0, roiMin, roiMax }) {
+  const dom = { 'roi-min': { value: String(roiMin) }, 'roi-max': { value: String(roiMax) },
+    'roi-hint': { textContent: '', className: 'roi-hint', style: { display: 'none' } } };
+  const document = { getElementById: id => dom[id] || null };
+  const state = { rawBE, rawIntensity: rawBE.map(() => 100), ccShift, peaks: [] };
+  const fns = new Function('document', 'state', NAMES.map(extractFn).join('\n\n') + '\nreturn { ' + NAMES.join(', ') + ' };')(document, state);
+  return { ...fns, dom, state };
+}
+const grid = (lo, hi, step) => Array.from({ length: Math.round((hi - lo) / step) + 1 }, (_, i) => +(lo + step * i).toFixed(6));
+const DATA = grid(280, 295, 0.05);
+
+test('an ROI inside the data: no hint', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'ok');
+  assert.equal(e._roiHintFor(st), null);
+  e._refreshRoiHint(st);
+  assert.equal(e.dom['roi-hint'].style.display, 'none');
+});
+
+test('an ROI past the data by more than one step: the quiet hint names the window actually used', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 270, roiMax: 320 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'past');
+  const h = e._roiHintFor(st);
+  assert.equal(h.cls, '', 'quiet, not amber');
+  assert.equal(h.text, 'ROI extends past your data — clipped to 280.00–295.00 eV.');
+  e._refreshRoiHint(st);
+  assert.equal(e.dom['roi-hint'].style.display, '');
+  assert.equal(e.dom['roi-hint'].textContent, h.text);
+});
+
+test('one side past the data is enough; the window named is the selected data', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 283.2, roiMax: 300 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'past');
+  assert.equal(e._roiHintFor(st).text, 'ROI extends past your data — clipped to 283.20–295.00 eV.');
+});
+
+test('a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"', () => {
+  const e = makeEnv({ rawBE: grid(279.97, 295.03, 0.1), roiMin: 279.9, roiMax: 295.1 });   // 0.07 eV past each edge, step 0.1
+  assert.equal(e._roiWindowStatus().state, 'ok');
+});
+
+test('min above max: amber, no data selected (getROIData selects nothing)', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 293, roiMax: 282 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'inverted');
+  assert.equal(e.getROIData().be.length, 0);
+  assert.deepEqual(e._roiHintFor(st), { cls: 'amber', text: 'BE min is above BE max — no data is selected.' });
+});
+
+test('an ROI that misses the data entirely: amber, names the data range', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 700, roiMax: 740 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'no-overlap');
+  assert.deepEqual(e._roiHintFor(st), { cls: 'amber', text: 'ROI does not overlap your data (280.00–295.00 eV) — no data is selected.' });
+});
+
+test('empty fields mean the full range (as getROIData): no hint', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: '', roiMax: '' });
+  assert.equal(e._roiWindowStatus().state, 'ok');
+});
+
+test('the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it', () => {
+  const e = makeEnv({ rawBE: DATA, ccShift: 1.5, roiMin: 278.5, roiMax: 293.5 });   // corrected data 278.5–293.5
+  assert.equal(e._roiWindowStatus().state, 'ok');
+  const e2 = makeEnv({ rawBE: DATA, ccShift: 1.5, roiMin: 280, roiMax: 295 });     // past the corrected top by 1.5 eV
+  const st = e2._roiWindowStatus();
+  assert.equal(st.state, 'past');
+  assert.equal(e2._roiHintFor(st).text, 'ROI extends past your data — clipped to 280.00–293.50 eV.');
+});
+
+test('a descending acquisition behaves the same', () => {
+  const e = makeEnv({ rawBE: DATA.slice().reverse(), roiMin: 270, roiMax: 320 });
+  const st = e._roiWindowStatus();
+  assert.equal(st.state, 'past');
+  assert.equal(e._roiHintFor(st).text, 'ROI extends past your data — clipped to 280.00–295.00 eV.');
+});
+
+test('centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
+  const st = e._roiWindowStatus();
+  for (const [c, out] of [[287, false], [282, false], [293, false], [281.9, true], [293.05, true], [310, true]]) {
+    assert.equal(e._centreOutsideData({ id: 1, center: c }, st), out, `centre ${c}`);
+  }
+  const eNone = makeEnv({ rawBE: DATA, roiMin: 700, roiMax: 740 });
+  assert.equal(eNone._centreOutsideData({ id: 1, center: 310 }, eNone._roiWindowStatus()), false, 'no selected data: nothing to compare against (the ROI hint speaks instead)');
+  const badge = e._outsideDataBadge({ id: 7, center: 310 }, st);
+  assert.match(badge, /class="outside-data-badge" data-peak-id="7"/);
+  assert.match(badge, /Centre 310\.00 eV lies outside the fitted data \(282\.00–293\.00 eV\)/);
+  assert.match(badge, /Nothing has been moved/);
+});
+
+// WARN, NEVER REINTERPRET — structural guards on the new helpers
+test('the helpers write nothing: no assignment to a field value, a peak or the fit state', () => {
+  for (const name of ['_roiWindowStatus', '_roiHintFor', '_refreshRoiHint', '_centreOutsideData', '_outsideDataBadge', '_patchPeakCardsForCentre', '_refreshRoiAndCentreWarnings']) {
+    const src = extractFn(name);
+    assert.doesNotMatch(src, /\.value\s*=(?!=)/, `${name} assigns an input value`);
+    assert.doesNotMatch(src, /\bp\.(center|fwhm|amplitude)\s*=(?!=)/, `${name} moves a peak`);
+    assert.doesNotMatch(src, /state\.(peaks|fitResult|ccShift)\s*=(?!=)/, `${name} writes the fit state`);
+    assert.doesNotMatch(src, /\b(pushUndo|updatePeakParam|renderPeakList|updatePlot)\(/, `${name} triggers an edit or a re-render`);
+  }
+});
+
+test('the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)', () => {
+  const g = extractFn('getROIData');
+  assert.match(g, /corrBE\[i\] >= roiMin && corrBE\[i\] <= roiMax/, 'inclusive filter unchanged');
+  assert.match(html, /roi: \{ be_min: parseFloat\(document\.getElementById\('roi-min'\)\.value\),\s*\n\s*be_max: parseFloat\(document\.getElementById\('roi-max'\)\.value\) \}/, 'Find Peaks payload unchanged');
+  const rp = extractFn('runPropagation');
+  assert.match(rp, /const roiSt = _roiWindowStatus\(\);[^\n]*\n\s*const \{ be, inten \} = getROIData\(\);/, 'Batch Fit reads the status beside, not instead of, getROIData');
+});
+
+test('an unsupported component: the badge warns without reporting its suppressed centre', () => {
+  const e = makeEnv({ rawBE: DATA, roiMin: 282, roiMax: 293 });
+  const st = e._roiWindowStatus();
+  const b = e._outsideDataBadge({ id: 3, center: 310 }, st, true);
+  assert.doesNotMatch(b, /310/, 'the suppressed centre must not appear');
+  assert.match(b, /Its centre lies outside the fitted data \(282\.00–293\.00 eV\)/);
+});
+
+// "One fix covers both" (plan §3): manual fit filters the corrected
+// energies, then uploads them rounded to 4 dp; Find Peaks uploads the
+// corrected energies rounded to 4 dp and the SERVER applies the same
+// inclusive mask. The two selections are identical except for an energy
+// within 5e-5 eV of an ROI edge, where rounding can move it across. Pinned
+// both ways so the qualification stays true.
+function serverMask(corr, lo, hi) { return corr.map(FP_UPLOAD_ROUND).filter(v => v >= lo && v <= hi); }
+test('manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge', () => {
+  for (const [lo, hi] of [[270, 320], [283.2, 300], [282, 293], [281.37, 291.83]]) {
+    const e = makeEnv({ rawBE: DATA, roiMin: lo, roiMax: hi });
+    const page = e.getROIData().be.map(FP_UPLOAD_ROUND);
+    assert.deepStrictEqual(serverMask(DATA, lo, hi), page, `ROI ${lo}–${hi}`);
+  }
+});
+test('…and can differ by one edge point when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)', () => {
+  const raw = Array.from({ length: 21 }, (_, i) => 280.00004 + 0.1 * i);   // Codex round 1 reproducer
+  const e = makeEnv({ rawBE: raw, roiMin: 280.00002, roiMax: 282.1 });
+  assert.equal(e.getROIData().be.length, 21);
+  assert.equal(serverMask(raw, 280.00002, 282.1).length, 20, 'rounding 280.00004 to 280.0 moves it below the edge');
+});
diff --git a/tests/js/unsupported_components.test.js b/tests/js/unsupported_components.test.js
index 81bf8a8..7e002bd 100644
--- a/tests/js/unsupported_components.test.js
+++ b/tests/js/unsupported_components.test.js
@@ -113,6 +113,7 @@ function pageEnv(fns, extraArgs = {}) {
     _isLocalFit: () => false, _localFitCaveat: () => '', _localFitDetail: () => '', _startsPanelHtml: () => '', _validateUncertainties: () => ({ warnings: [], info: [] }),
     renderQuantify: () => {}, recalcQuantify: () => {}, _detectPeakRSF: () => ({ key: 'C 1s', rsf: 1 }), SCOFIELD_RSF: { 'C 1s': 1 }, notify: () => {},
     _clearDisallowedChargeRef: () => {}, _updateLocalModelBanner: () => {}, _updateLockAllBtn: () => {}, renderPeakForm: () => '', _highlightChartPeak: () => {},
+    _roiWindowStatus: () => ({ state: 'ok', n: 0 }), _patchPeakCardsForCentre: () => {},   // the ROI / centre warnings: tests/js/roi_clamp_centre_warning.test.js
     _isChargeRefAllowed: () => false, _fitStatLabel: () => 'χ²ᵣ', _isUnweightedLocal: () => false, _applyStatCaption: () => {}, _applyStatDisplay: () => {},
     _CHISQ_TOOLTIP: '', _LOCALFIT_TOOLTIP: '', _startsSummaryText: () => '', _startsChosenText: () => '', _startsIfCurrent: () => null,
     _isLocalModel: () => false, _updateRFactorUI: () => {}, _activeTab: () => ({}), _renderRFactorPanel: () => '', _statIsChi: true,
diff --git a/tests/test_component_required.py b/tests/test_component_required.py
index 78b4ef7..e48cac4 100644
--- a/tests/test_component_required.py
+++ b/tests/test_component_required.py
@@ -49,21 +49,36 @@ KW = dict(background_method="manual", manual_bg=[[280.0, 1000.0], [295.0, 1000.0
           fit_kws={"method": "least_squares"})
 
 
-def test_a_redundant_anchor_is_supported_but_not_required():
+@pytest.mark.parametrize("method", ["least_squares", "leastsq"])
+def test_a_redundant_anchor_is_supported_but_not_required(method):
     # Codex, Auto-Fit anchor unit round 6 (run B): two symmetric GL lines at
-    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. Auto-Fit's model puts an
-    # asymmetric-GL Graphite at 284.5 with the ±0.3 eV window; the fit gives it
-    # a large amplitude (F ~ 1e6 with the others HELD) — yet the other two
-    # components fit the data to rounding precision without it.
+    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. In that reproduction the
+    # full fit kept a LARGE Graphite (amplitude 1,081-1,894, held-others F ~
+    # 1e6) because it stopped in a minimum where the anchor carries weight;
+    # yet the other two components fit the data to rounding precision
+    # without it.
+    #
+    # The premise is posed deterministically by HOLDING the anchor at 1,500
+    # (inside that observed range). Until 2026-09-25 this test instead
+    # started the other components at the exact truth, which lets the fit
+    # drive the anchor to residue (~0.01) - the premise never formed, the
+    # held-others F landed at 11-24 against the threshold of 10, and
+    # Trust-Region's documented last-digit jitter (identical seed in every
+    # process) moved it across: the test passed 2 of 3 runs on main. Now
+    # F ~ 4e7 and the refit without the anchor is ~1e4 x better, under both
+    # methods, in every process.
     y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
-    specs = _autofit_model(1000, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
-    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
+    specs = _autofit_model(1500, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
+    specs[0]["fix_amplitude"] = True
+    kw = dict(KW, fit_kws={"method": method})
+    res = fitting.run_fit(X, y, specs, require_component="1", **kw)
     assert res["success"] is True
     g = next(ip for ip in res["individual_peaks"] if ip["id"] == "1")
     assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
+    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
     req = res["required"]
     assert req["ran"] is True and req["refit_converged"] is True
-    assert req["chi2_without_refit"] <= req["chi2_with"] * 1.001
+    assert req["chi2_without_refit"] < 1e-2 * req["chi2_with"]
     assert req["required"] is False
 
 

exec
/bin/zsh -lc "rg -n \"roi-min|roi-max|set\\('roi-|\\.center\\s*=|updatePeakParam\\(["'^'"\\n]*['\\\"]center|function (_isUnsupported|_componentSupport|_patchPeakCardsForSupport|_restoreUI|updatePlot|renderEmptyChart|_escAttr)|_restoreUI\\(\" templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
2064:                <input type="number" id="roi-min" value="706" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
2068:                <input type="number" id="roi-max" value="726" step="0.5" oninput="updatePlot();_recomputeAutoFitMenuState()">
3241:    this._restoreUI(tab.ui);
3395:        min: document.getElementById('roi-min').value,
3396:        max: document.getElementById('roi-max').value
3478:      this._restoreUI(active.ui);
3831:      roiMin:      document.getElementById('roi-min')?.value || '',
3832:      roiMax:      document.getElementById('roi-max')?.value || '',
3840:  _restoreUI(ui) {
3851:    set('roi-min', ui.roiMin);
3852:    set('roi-max', ui.roiMax);
4994:    const roiMinEl = document.getElementById('roi-min');
4995:    const roiMaxEl = document.getElementById('roi-max');
5062:  const roiMinRaw = parseFloat(document.getElementById('roi-min').value);
5063:  const roiMaxRaw = parseFloat(document.getElementById('roi-max').value);
5080:// energies inside [roi-min, roi-max], so an ROI past the data is clamped to
5092:  const lo = parseFloat(document.getElementById('roi-min').value);
5093:  const hi = parseFloat(document.getElementById('roi-max').value);
5170:  document.getElementById('roi-min').value = lo.toFixed(1);
5171:  document.getElementById('roi-max').value = hi.toFixed(1);
5181:  document.getElementById('roi-min').value = _roiLo.toFixed(1);
5182:  document.getElementById('roi-max').value = _roiHi.toFixed(1);
5445:  const roiMin = parseFloat(document.getElementById('roi-min').value);
5446:  const roiMax = parseFloat(document.getElementById('roi-max').value);
5985:      if (key === 'center') parent.center = p.center - p.linkOffset;
5999:      if (key === 'center') child.center = parent.center + child.linkOffset;
6196:          oninput="updatePeakParam(${p.id},'center',parseFloat(this.value));_patchPeakCardsForSupport()">
6224:          oninput="getPeak(${p.id}).linkOffset=parseFloat(this.value);getPeak(${p.id}).center=getPeak(${p.linked}).center+parseFloat(this.value);updatePeakParam(${p.id},'center',getPeak(${p.id}).center)">
6508:  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
6964:    roiMinDom:    document.getElementById('roi-min')?.value || '',
6965:    roiMaxDom:    document.getElementById('roi-max')?.value || '',
7021:  set('roi-min',   snap.roiMinDom);
7022:  set('roi-max',   snap.roiMaxDom);
7145:function _componentSupportCore(counts, fitted, comp, weights, nFreeComp, nFreeTotal) {
7156:function _componentSupportFromResponse(json, peakId) {
7187:function _isUnsupported(p, key) {
7209:function _patchPeakCardsForSupport() {
7401:    notify('ROI is empty. Set roi-min and roi-max before auto-fit.', 'red', true);
8230:      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
9410:function updatePlot() {
9905:function renderEmptyChart() {
10165:      min: document.getElementById('roi-min').value,
10166:      max: document.getElementById('roi-max').value
10546:  tabManager._restoreUI(active.ui);
12080:      tabManager._restoreUI(tgt.ui);
13944:function _escAttr(s) {
15500:    document.getElementById('roi-min').value = entries[0].roi.be_min;
15501:    document.getElementById('roi-max').value = entries[0].roi.be_max;
15721:      roi: { be_min: parseFloat(document.getElementById('roi-min').value),
15722:             be_max: parseFloat(document.getElementById('roi-max').value) },
16008:  // CURRENT #roi-min/#roi-max, i.e., the full window Find Peaks just used.

exec
/bin/zsh -lc "sed -n '3195,3270p' templates/index.html
sed -n '3440,3505p' templates/index.html
sed -n '4960,5018p' templates/index.html
sed -n '5130,5200p' templates/index.html
sed -n '5910,6020p' templates/index.html
sed -n '6480,6540p' templates/index.html
sed -n '6985,7045p' templates/index.html
sed -n '7160,7265p' templates/index.html
sed -n '9400,9465p' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
    const tab = {
      id,
      name: '▦ Stack ' + (_nextStackNum++),
      color: '#7a7a7a',           // inert — stack tabs render no dot
      isStack: true,
      entries: [],
      _nextColorIdx: 0,
      lineWidth: 1.5,
      verticalOffset: 0,
      // Inert spectrum-tab fields kept to satisfy existing lifecycle code paths.
      isSurvey: false, chargeVerified: true,
      rawBE: [], rawIntensity: [], ccShift: 0,
      peaks: [], nextId: 1, fitResult: null,
      markedElements: [], notes: '', sourcePath: null,
      ui: { bgType: 'shirley', bgStart: '', bgEnd: '', shirleyIter: '5',
            endpointAvg: '1', roiMin: '', roiMax: '',
            ccMethod: 'none', ccObs: '', ccLit: '' },
    };
    this.tabs.push(tab);
    this.activateTab(id);
    return tab;
  }

  activateTab(id) {
    if (this.activeId === id) return;
    const tab = this._getTab(id);
    if (!tab) return;
    // Cancel any armed placement mode so a click on the new tab's chart
    // isn't consumed by a placement aimed at the previous spectrum.
    if (placeMode) togglePlaceMode(placeMode);
    // Clear stale history preview from previous tab
    if (typeof _historyPreview !== 'undefined') _historyPreview = null;
    // Save current tab's live state
    this._syncActiveToRecord();
    this.activeId = id;

    // Swap global state fields — peaks uses reference sharing
    state.rawBE = tab.rawBE;
    state.rawIntensity = tab.rawIntensity;
    state.ccShift = tab.ccShift;
    state.peaks = tab.peaks;
    state.nextId = tab.nextId;
    state.fitResult = tab.fitResult;
    state.lineWidth = tab.lineWidth ?? 1.5;

    // Restore DOM form fields
    this._restoreUI(tab.ui);
    _updateUndoButtons();   // history is per tab: buttons reflect the incoming record
    const notesEl = document.getElementById('spectrum-notes');
    if (notesEl) notesEl.value = tab.notes || '';
    this._updateCCVerifiedUI(tab.chargeVerified ?? true);
    this._updateInfoBadge(tab);
    if (typeof _recomputeAutoFitMenuState === 'function') _recomputeAutoFitMenuState();
    // Update chi-squared display for this tab's fit result
    _applyStatDisplay(state.fitResult);
    if (state.fitResult && state.fitResult.rFactor == null) {
      state.fitResult.rFactor = _computeRFactor(state.fitResult);
    }
    _updateRFactorUI(state.fitResult ? state.fitResult.rFactor : null);
    _updateROIDisplay(state.fitResult ? state.fitResult.roiRange : null);
    // Reset Y zoom so chart auto-scales to this tab's data range
    // (prevents survey zoom from squishing narrow-region spectra)
    state._mainYMax = tab.yZoom || null;
    state._mainXMin = tab.xZoomMin ?? null;
    state._mainXMax = tab.xZoomMax ?? null;

    this.renderTabBar();
    renderPeakList();
    renderResults();
    _applyRightPanelMode(tab);
    if (typeof _refOnTabChange === 'function') _refOnTabChange();
    updatePlot();
  }

  closeTab(id) {
    const idx = this.tabs.findIndex(t => t.id === id);
      }

      // Fit loaded from external file — CC not verified for this spectrum
      active.chargeVerified = false;
      this._updateCCVerifiedUI(false);

      // Endpoint averaging is resolved whether or not the file carries a
      // background block: v1 files written before 2026-09-08 never recorded
      // it (those fits were made at 1), and an accepted peaks-only file must
      // not inherit the fresh target tab's new-tab default either (Codex
      // round 1, both runs).
      active.ui.endpointAvg = (data.background && data.background.endpointAvg) || LEGACY_ENDPOINT_AVG;

      // Apply background
      if (data.background) {
        active.ui.bgType = data.background.type || 'shirley';
        active.ui.bgStart = data.background.start || '';
        active.ui.bgEnd = data.background.end || '';
        active.ui.shirleyIter = data.background.shirleyIter || '5';
        // bgSubtractedView is missing from pre-feature saves → falsy default
        active.ui.bgSubtractedView = !!data.background.bgSubtractedView;
      }

      // Apply ROI
      if (data.roi) {
        active.ui.roiMin = data.roi.min || '';
        active.ui.roiMax = data.roi.max || '';
      }

      // Apply notes
      if (data.notes) active.notes = data.notes;
      const notesEl = document.getElementById('spectrum-notes');
      if (notesEl) notesEl.value = active.notes || '';

      // Apply manual anchor points
      if (data.manualAnchors) active.manualAnchors = data.manualAnchors;

      // Restore DOM from updated ui and re-render
      this._restoreUI(active.ui);
      renderPeakList();
      updatePlot();
      renderResults();   // installs the imported model's designation (or the plain placeholder) and clears stale widgets
      return;
    }

    // v2+ multi-tab data — route through _loadProjectJSON (has confirmation)
    _loadProjectJSON(data);
  }

  // ── Tab bar rendering ───────────────────────────

  renderTabBar() {
    const bar = document.getElementById('spectrum-tab-bar');
    if (!bar) return;
    bar.innerHTML = '';
    for (const tab of this.tabs) {
      const el = document.createElement('div');
      el.className = 'sp-tab'
        + (tab.id === this.activeId ? ' active' : '')
        + (tab.isStack ? ' is-stack' : '');
      const tabId = tab.id;

      const inner = document.createElement('span');
      inner.innerHTML =
        '<span class="sp-tab-dot" style="background:' + tab.color + '"></span>' +
        '<span>' + this._esc(tab.name) + '</span>' +
  } else if (method === 'au4f') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 83.98;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '83.98';
  } else if (method === 'b1s-b2o3') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 192.99;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '192.99';
  } else if (method === 'n1s-bn') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 398.31;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '398.31';
  } else if (method === 'b1s-bn') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    state.ccShift = isNaN(obs) ? 0 : obs - 190.74;
    refField.style.display = 'block';
    document.getElementById('cc-lit').value = '190.74';
  } else if (method === 'custom') {
    const obs = parseFloat(document.getElementById('cc-obs').value);
    const lit = parseFloat(document.getElementById('cc-lit').value);
    state.ccShift = (isNaN(obs) || isNaN(lit)) ? 0 : obs - lit;
    refField.style.display = 'block';
    targetField.style.display = 'block';
  } else {
    state.ccShift = 0;
  }

  // Shift all energy-dependent values by the change in correction
  const delta = state.ccShift - prevShift;
  if (delta !== 0) {
    // ROI boundaries
    const roiMinEl = document.getElementById('roi-min');
    const roiMaxEl = document.getElementById('roi-max');
    const roiMinVal = parseFloat(roiMinEl.value);
    const roiMaxVal = parseFloat(roiMaxEl.value);
    if (!isNaN(roiMinVal)) roiMinEl.value = (roiMinVal - delta).toFixed(1);
    if (!isNaN(roiMaxVal)) roiMaxEl.value = (roiMaxVal - delta).toFixed(1);

    // Background endpoints
    const bgStartEl = document.getElementById('bg-start');
    const bgEndEl = document.getElementById('bg-end');
    const bgStartVal = parseFloat(bgStartEl.value);
    const bgEndVal = parseFloat(bgEndEl.value);
    if (!isNaN(bgStartVal)) bgStartEl.value = (bgStartVal - delta).toFixed(1);
    if (!isNaN(bgEndVal)) bgEndEl.value = (bgEndVal - delta).toFixed(1);

    // Peak centers
    for (const p of state.peaks) {
      p.center -= delta;
    }

    // Manual background anchors. Anchors are DATA-ATTACHED like peak
    // centers (x = a data point's corrected BE at placement time, y = that
    // point's intensity), so they follow the same -delta migration as the
    // ROI/bg fields and peak centers above — NOT the reference-marker
    // convention (literature markers stay at nominal corrected BE). y is
function _centreOutsideData(p, st) {
  return !!(st && st.n > 0 && Number.isFinite(p.center) && (p.center < st.sMin || p.center > st.sMax));
}
function _outsideDataBadge(p, st, unsupported) {
  // a component the fit did not determine has its centre suppressed
  // everywhere (unit step (b)); the warning must not report it either
  const where = unsupported ? 'Its centre lies' : `Centre ${p.center.toFixed(2)} eV lies`;
  const tip = `${where} outside the fitted data (${st.sMin.toFixed(2)}–${st.sMax.toFixed(2)} eV). `
    + 'A component centred outside the measured data is almost always a placement error: the fit sees only its tail. Nothing has been moved.';
  return `<span class="outside-data-badge" data-peak-id="${p.id}" title="${_escAttr(tip)}">outside data</span>`;
}
// Patched IN PLACE (the student may be typing in a card): add, update or
// remove each card's badge; never re-render the list.
function _patchPeakCardsForCentre(st) {
  for (const p of state.peaks) {
    const item = document.getElementById('peak-item-' + p.id);
    if (!item) continue;
    const name = item.querySelector('.peak-name');
    if (!name) continue;
    const badge = name.querySelector('.outside-data-badge');
    const out = _centreOutsideData(p, st);
    if (out) {
      const html = _outsideDataBadge(p, st, typeof _isUnsupported === 'function' && _isUnsupported(p));
      if (!badge) name.insertAdjacentHTML('beforeend', html);
      else { const tmp = document.createElement('span'); tmp.innerHTML = html; const t = tmp.firstChild.getAttribute('title'); if (badge.getAttribute('title') !== t) badge.setAttribute('title', t); }
    } else if (badge) badge.remove();
  }
}
function _refreshRoiAndCentreWarnings() {
  const st = _roiWindowStatus();
  _refreshRoiHint(st);
  _patchPeakCardsForCentre(st);
  return st;
}

function maxROI() {
  if (!state.rawBE.length) return;
  const be = getCorrectedBE();
  const lo = _arrMin(be);
  const hi = _arrMax(be);
  document.getElementById('roi-min').value = lo.toFixed(1);
  document.getElementById('roi-max').value = hi.toFixed(1);
  document.getElementById('bg-start').value = hi.toFixed(1);
  document.getElementById('bg-end').value = lo.toFixed(1);
  updatePlot();
}

function autoSetROI() {
  if (!state.rawBE.length) return;
  const be = getCorrectedBE();
  const _roiLo = _arrMin(be), _roiHi = _arrMax(be);
  document.getElementById('roi-min').value = _roiLo.toFixed(1);
  document.getElementById('roi-max').value = _roiHi.toFixed(1);
  document.getElementById('bg-start').value = _roiHi.toFixed(1);
  document.getElementById('bg-end').value = _roiLo.toFixed(1);
  updatePlot();
}

// ═══════════════════════════════════════════════════
// PEAKS
// ═══════════════════════════════════════════════════
// Normalize charge-reference flags on a freshly-loaded peak list.
// Old saves do not have `isChargeReference` — default to false.
// If a save somehow has >1 true, keep the first and clear the rest.
function _normalizePeaksCRef(peaks) {
  if (!Array.isArray(peaks)) return peaks;
  let seen = false;
  return peaks.map(p => {
    const q = { ...p };
    if (typeof q.isChargeReference !== 'boolean') q.isChargeReference = false;
    if (q.isChargeReference) {
  renderPeakList();
  updatePlot();
  // Auto-expand the linked peak so the offset/ratio fields are immediately visible
  const body = document.getElementById('peak-body-' + p2.id);
  if (body) body.classList.add('open');
  notify('Multiplet pair added \u2014 edit offset & ratio below \u201c' + p2.name + '\u201d', 'green');
}

function removePeak(id) {
  pushUndo();
  state.peaks = state.peaks.filter(p => p.id !== id && p.linked !== id);
  _invalidateFittedY();
  renderPeakList();
  updatePlot();
}

function clearAllPeaks() {
  if (!state.peaks.length) return;
  if (!confirm('Are you sure you want to clear all peaks?')) return;
  pushUndo();
  state.peaks = [];
  state.fitResult = null;
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }
  renderPeakList();
  updatePlot();
}

function getPeak(id) { return state.peaks.find(p => p.id === id); }

function unlinkPeak(id) {
  if (!confirm('Unlink this peak? It will become fully independent.')) return;
  pushUndo();
  const p = getPeak(id);
  if (!p) return;
  p.linked = null;
  renderPeakList();
  updatePlot();
}

// Handler for the linked-peak "Ratio (I₂/I₁)" input.
// Clamps to [0.01, 2] so the user can't accidentally zero out both peaks by
// typing 0 (which historically back-propagated a zero amplitude to the parent).
// A ratio of 0 is not physically meaningful for a linked multiplet anyway —
// if the satellite truly has no intensity, it should not be linked.
function _onLinkRatioInput(id, rawVal) {
  const child = getPeak(id);
  if (!child || !child.linked) return;
  const parent = getPeak(child.linked);
  if (!parent) return;
  let r = parseFloat(rawVal);
  if (!isFinite(r) || r < 0.01) r = 0.01;
  if (r > 2) r = 2;
  child.linkRatio = r;
  child.amplitude = parent.amplitude * r;
  updatePeakParam(id, 'amplitude', child.amplitude);
}

function updatePeakParam(id, key, value) {
  _pushUndoDebounced();
  const p = getPeak(id);
  if (!p) return;
  // asymmetry: clamp to the backend's own bound (fitting.py np.clip(asymmetry,
  // 0, 1)) — a plain assignment let out-of-range values (e.g. pasted/loaded)
  // sit on the peak until a backend fit result overwrote them.
  if (key === 'asymmetry') value = Math.max(0, Math.min(1, value));
  p[key] = value;

  const syncKeys = ['center','amplitude','fwhm','shape','glMix','asymmetry','dsAlpha','dsGamma','laAlpha','laBeta','laM','caAlpha','caBeta','caM'];
  if (syncKeys.includes(key)) {
    // Resolve canonical parent: if p is a child, find its parent first
    let parent = p.linked ? getPeak(p.linked) : p;
    if (!parent) parent = p;

    if (p.linked && parent) {
      // p is a child — back-propagate changed value to parent
      if (key === 'center') parent.center = p.center - p.linkOffset;
      else if (key === 'amplitude') {
        // Only divide back to the parent when the ratio is meaningfully >0.
        // Otherwise (child was zeroed or ratio is tiny) leave the parent alone.
        if (p.linkRatio && p.linkRatio > 1e-6) {
          parent.amplitude = p.amplitude / p.linkRatio;
        }
      }
      else parent[key] = p[key];
      renderPeakControls(parent);
    }

    // Forward-propagate from parent to all children (including p if it is one)
    for (const child of state.peaks.filter(q => q.linked === parent.id)) {
      if (key === 'center') child.center = parent.center + child.linkOffset;
      else if (key === 'amplitude') child.amplitude = parent.amplitude * child.linkRatio;
      else child[key] = parent[key];
      if (child.id !== id) renderPeakControls(child);
    }
  }
  _invalidateFittedY();
  updatePlot();
}

function toggleLock(id, key, btn) {
  const p = getPeak(id);
  if (!p) return;
  p[key] = !p[key];
  btn.className = 'lock-btn' + (p[key] ? ' locked' : '');
  btn.innerHTML = p[key] ? '&#x1f512;' : '&#x1f513;';
  btn.title = (p[key] ? 'Unlock' : 'Lock') + ' during fitting';
  _updateLockAllBtn();
  _refreshStartsEvidence(true);      // a lock is part of the fitted model
}

const LOCK_ALL_KEYS = ['fixCenter', 'fixFwhm', 'fixAmplitude', 'fixAsymmetry', 'fixGlMix', 'fixDsAlpha', 'fixDsGamma'];
    spec.fix_m_gauss = !!p.fixLaM;
  } else if (shape === 'LACX') {
    spec.shape = 'la_casaxps';
    spec.alpha = Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0;
    spec.beta  = Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0;
    spec.m     = Number.isFinite(p.caM)     ? p.caM     : 50.0;
    spec.fix_alpha = !!p.fixCaAlpha;
    spec.fix_beta  = !!p.fixCaBeta;
    spec.fix_m     = !!p.fixCaM;
  } else {
    spec.shape = 'gaussian';
  }
  if (p.linked) {
    const parent = getPeak(p.linked);
    if (parent) {
      spec.constrain_to = String(p.linked);
      spec.splitting = p.linkOffset;
      spec.area_ratio = p.linkRatio;
      spec.fix_fwhm = true;
    }
  }
  return spec;
}

// Server parameter names -> the peak's fields, honouring the peak's locks.
// Shared by a fit result and by an alternative solution (previewed on a COPY
// of the peaks, or adopted as the start of a new fit).
function _applyBackendParams(p, par) {
  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
  if (par.amplitude && !p.fixAmplitude) p.amplitude = par.amplitude.value;
  if (par.fwhm      && !p.fixFwhm)     p.fwhm      = par.fwhm.value;
  // glMix is read only by GL / asym-GL; a Voigt's fixed 0.5 (A03) is not a
  // fitted value and must not overwrite the mix the peak carries for a later
  // switch to GL.
  if (par.gl_ratio  && (p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) p.glMix = par.gl_ratio.value * 100;
  if (par.asymmetry && p.shape === 'asym-GL' && !p.fixAsymmetry) p.asymmetry = par.asymmetry.value;
  if (par.alpha && p.shape === 'DS' && !p.fixDsAlpha) p.dsAlpha = par.alpha.value;
  if (par.gamma_asym && p.shape === 'DS' && !p.fixDsGamma) p.dsGamma = par.gamma_asym.value;
  if (par.alpha   && p.shape === 'DSG_LA' && !p.fixLaAlpha) p.laAlpha = par.alpha.value;
  if (par.beta    && p.shape === 'DSG_LA' && !p.fixLaBeta)  p.laBeta  = par.beta.value;
  if (par.m_gauss && p.shape === 'DSG_LA' && !p.fixLaM)     p.laM     = par.m_gauss.value;
  if (par.alpha   && p.shape === 'LACX' && !p.fixCaAlpha) p.caAlpha = par.alpha.value;
  if (par.beta    && p.shape === 'LACX' && !p.fixCaBeta)  p.caBeta  = par.beta.value;
  if (par.m       && p.shape === 'LACX' && !p.fixCaM)     p.caM     = par.m.value;
}

function applyBackendResult(result) {
  for (const ipeak of result.individual_peaks) {
    // Backend returns string IDs; state.peaks uses numeric IDs
    const p = getPeak(Number(ipeak.id)) || getPeak(ipeak.id);
    if (!p) continue;
    // Only apply parameters that were NOT locked — locked params must stay unchanged
    _applyBackendParams(p, ipeak.params);
    p._backendParams = ipeak.params;
  }
  // the verdict describes the model as it now stands (values applied) in its fit context
  _applySupport(state.peaks, result, _startsLiveKey());
}

// LEVENBERG-MARQUARDT FITTING (local JS engine)
// ═══════════════════════════════════════════════════
  // the fitting tab's record in the provisional cc frame (Codex round-2
  // MAJOR — a pre-existing defect for peaks/ccShift/DOM, not just the
  // newly-migrating anchors). activateTab already synced the provisional
  // live state into the record at switch-away, so overwriting the record
  // fields with the snapshot undoes exactly that.
  if (_activeTab() !== owner) {
    const t = owner;
    if (t.isStack) return;
    t.peaks = snap.peaks;
    t.fitResult = snap.fitResult;
    t.ccShift = snap.ccShift;
    t.manualAnchors = snap.manualAnchors || [];
    t.modelProvenance = snap.modelProvenance || null;
    t.nextId = snap.nextId;
    t.ui = { ...t.ui,
      ccMethod: snap.ccMethodDom, ccObs: snap.ccObsDom, ccLit: snap.ccLitDom,
      roiMin: snap.roiMinDom, roiMax: snap.roiMaxDom,
      bgStart: snap.bgStartDom, bgEnd: snap.bgEndDom };
    return;
  }
  state.peaks     = snap.peaks;
  state.fitResult = snap.fitResult;
  state.ccShift   = snap.ccShift;
  _setManualAnchors(snap.manualAnchors || []);
  { const _t = _activeTab(); if (_t) _t.modelProvenance = snap.modelProvenance || null; }
  state.nextId    = snap.nextId;
  const set = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
  set('cc-method', snap.ccMethodDom);
  set('cc-obs',    snap.ccObsDom);
  set('cc-lit',    snap.ccLitDom);
  // The provisional 'c1s' correction hid the custom-target field; putting the
  // method back without its field left Custom with no visible input (same
  // rule as the tab-restore path, no change event).
  { const rf = document.getElementById('cc-ref-field'), tf = document.getElementById('cc-target-field');
    if (rf) rf.style.display = (snap.ccMethodDom === 'none') ? 'none' : 'block';
    if (tf) tf.style.display = (snap.ccMethodDom === 'custom') ? 'block' : 'none'; }
  set('roi-min',   snap.roiMinDom);
  set('roi-max',   snap.roiMaxDom);
  set('bg-start',  snap.bgStartDom);
  set('bg-end',    snap.bgEndDom);
  const disp = document.getElementById('cc-shift-display');
  if (disp) {
    const sh = -state.ccShift;
    disp.textContent = (sh >= 0 ? '+' : '') + sh.toFixed(3) + ' eV';
  }
  if (typeof renderPeakList === 'function') renderPeakList();
  if (typeof updatePlot === 'function') updatePlot();
}

// Apply a successful auto-fit result. Mutates state and DOM so the tab
// ends in a self-consistent corrected frame with graphite at exactly 284.50.
// Pure decision: given (id, area) pairs and graphite's id, decide whether
// to emit the < 40% area-fraction warning toast. Returns null on no-warning,
// or { fractionPct, warning } on warning. Boundary: '< 0.40' so 0.40 itself
// does NOT warn.
//
// This logic is intentionally state-free so the Python port test in
// /tmp/test_autofit_decide_warning.py can validate it without simulating
// state.peaks or the backend.
function _autoFitDecideAreaWarning(peakAreas, graphiteId) {
  if (!Array.isArray(peakAreas)) return null;
  const comp = (ip && ip.y) || [], n = counts.length;
  if (!n || fit.length !== n || comp.length !== n) return null;
  let p = 0;
  for (const k in ((ip && ip.params) || {})) { const q = ip.params[k]; if (q && q.vary === true && (q.expr == null || q.expr === '')) p++; }
  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
  return _componentSupportCore(counts, fit, comp, counts.map(c => 1 / Math.sqrt(Math.max(c, 1))), p, nFree);
}
// Resolve links by ANCESTRY (a grandchild follows the root), independent of order.
function _supportRootOf(peaks, p, seen = new Set()) {
  if (!p.linked || seen.has(p.id)) return p;
  seen.add(p.id);
  const par = peaks.find(q => String(q.id) === String(p.linked));
  return par ? _supportRootOf(peaks, par, seen) : p;
}
// Write p.support for every peak from per-peak verdicts {id -> verdict|null}, stamped with the fit key.
function _applySupportVerdicts(peaks, verdictOf, fitKey) {
  for (const p of peaks) {
    const root = _supportRootOf(peaks, p);
    const v = verdictOf(root.id);
    p.support = v ? { f: v.f ?? null, delta_chi2: v.delta_chi2 ?? null, supported: !!v.supported, fitKey,
                      ...(root !== p ? { follows: root.id } : {}) } : null;
  }
}
function _applySupport(peaks, json, fitKey) {
  _applySupportVerdicts(peaks, id => _componentSupportFromResponse(json, id), fitKey);
}
// TRUE only for a verdict that describes the CURRENT model and fit context.
function _isUnsupported(p, key) {
  if (!(p && p.support && p.support.supported === false)) return false;
  if (!p.support.fitKey) return false;                              // a verdict from before keys existed: not applied
  if (key === undefined) key = typeof _startsLiveKey === 'function' ? _startsLiveKey() : null;
  return p.support.fitKey === key;
}
// A CURRENT verdict, either way (for exports: a stale or keyless verdict is "not established", never "supported").
function _currentSupport(p) {
  if (!(p && p.support && p.support.fitKey)) return null;
  return p.support.fitKey === _startsLiveKey() ? p.support : null;
}
// Re-stamp every verdict with the live key: for a caller that changes the
// model or context AS PART OF producing the result (Auto-Fit locks every
// centre and refines the charge correction after the fit is applied).
function _restampSupport() {
  const key = _startsLiveKey();
  for (const p of state.peaks) if (p.support) p.support.fitKey = key;
}
// Patch the sidebar cards in place for the current verdicts (a re-render would
// replace an input the student is typing in): header centre, the three summary
// values, the area % column (over the components the current verdicts
// support) and the badge.
function _patchPeakCardsForSupport() {
  const key = _startsLiveKey();
  // area % over the components the CURRENT verdicts support (as renderPeakList computes it)
  const { be: roiBE } = (typeof getROIData === 'function' && state.rawBE && state.rawBE.length) ? getROIData() : { be: [] };
  const areas = {};
  let total = 0;
  if (roiBE.length) for (const p of state.peaks) { areas[p.id] = _peakArea(p, roiBE); if (!_isUnsupported(p, key)) total += areas[p.id]; }
  for (const p of state.peaks) {
    const item = document.getElementById('peak-item-' + p.id);
    if (!item) continue;
    const un = _isUnsupported(p, key), dash = '\u2014';
    const info = item.querySelector('.peak-info');
    if (info) info.textContent = un ? dash : p.center.toFixed(2) + ' eV';
    const vals = item.querySelectorAll('.peak-summary-val');
    if (vals[0]) vals[0].textContent = un ? dash : p.center.toFixed(2);
    if (vals[1]) vals[1].textContent = un ? dash : p.fwhm.toFixed(2);
    if (vals[2]) vals[2].textContent = (un || !(total > 0 && areas[p.id] > 0)) ? dash : ((areas[p.id] / total) * 100).toFixed(1) + '%';
    const name = item.querySelector('.peak-name'), badge = name && name.querySelector('.unsupported-badge');
    if (un && name && !badge) name.insertAdjacentHTML('beforeend', ' ' + _unsupportedBadge(p.id));
    if (!un && badge) { badge.previousSibling && badge.previousSibling.nodeType === 3 && badge.previousSibling.textContent === ' ' ? badge.previousSibling.remove() : null; badge.remove(); }
  }
}
function _unsupportedBadge(id) { return `<span class="unsupported-badge" data-peak-id="${id}" title="${_escAttr(_UNSUPPORTED_TIP)}">${_UNSUPPORTED_LABEL}</span>`; }

const _AUTOFIT_ANCHOR_MIN_F = 10;
function _autoFitGraphiteIsSupported(gPeak, json) {
  const amp = gPeak && gPeak.amplitude;
  if (!Number.isFinite(amp) || amp <= 0) return false;
  const counts = (json && json.counts) || [], fit = (json && json.fitted_y) || [];
  const ip = ((json && json.individual_peaks) || []).find(q => String(q.id) === String(gPeak.id));
  const comp = (ip && ip.y) || [];
  const n = counts.length;
  if (!n || fit.length !== n || comp.length !== n) return false;          // nothing to judge against
  let withC = 0, withoutC = 0;
  for (let i = 0; i < n; i++) {
    if (!Number.isFinite(counts[i]) || !Number.isFinite(fit[i]) || !Number.isFinite(comp[i])) continue;
    const w = 1 / Math.max(counts[i], 1), r = counts[i] - fit[i];
    withC += w * r * r;
    withoutC += w * (r + comp[i]) * (r + comp[i]);
  }
  const delta = withoutC - withC;
  if (!(delta > 0)) return false;
  let p = 0;
  for (const k in (ip.params || {})) { const q = ip.params[k]; if (q && q.vary === true && (q.expr == null || q.expr === '')) p++; }
  p = Math.max(1, p);
  const nFree = (json.statistics && Number.isFinite(json.statistics.n_free_params)) ? json.statistics.n_free_params : 0;
  const dof = Math.max(1, n - nFree);
  if (withC === 0) return true;                                           // exact fit that the component is needed for
  return (delta / p) / (withC / dof) >= _AUTOFIT_ANCHOR_MIN_F;
}

function applyAutoFitResult(json, graphiteRaw, roi) {
  // 1. Locate the graphite peak in state.peaks (named "Graphite").
  const gPeak = state.peaks.find(p => p.name === 'Graphite') || state.peaks[0];
  if (!gPeak || !Number.isFinite(gPeak.center)) {
    notify('Auto-fit failed: graphite center not found in fit result.', 'red', true);
    return false;
      if (sc.y.ticks) sc.y.ticks.display = !offsetActive;
      if (sc.y.title) {
        sc.y.title.display = true;
        sc.y.title.text = offsetActive ? 'Intensity (offset stacked)' : 'Intensity (counts/s)';
      }
    }
  }
  state.chart.update('none');
}

function updatePlot() {
  // Stack-tab early branch: render multi-spectrum overlay, no peaks/fits.
  // Route through _updateStackChart so toolbar-pill toggles (Envelope,
  // Individual Peaks, Fill, Bkgrd Sub) and other state changes preserve
  // zoom by in-place updating. _updateStackChart delegates to
  // _renderStackChart automatically when no chart exists.
  {
    const _activeTab = (typeof tabManager !== 'undefined') ? tabManager._getTab(tabManager.activeId) : null;
    const _emptyEl = document.getElementById('stack-empty-state');
    const _canvas = document.getElementById('mainChart');
    if (isStackTab(_activeTab)) {
      _refreshRoiHint(null);   // a stack tab has no ROI of its own
      _updateStackChart(_activeTab);
      return;
    } else {
      if (_canvas) _canvas.style.display = '';
      if (_emptyEl) _emptyEl.style.display = 'none';
    }
  }

  // Full corrected spectrum (for raw data display and axis range)
  const corrBE = getCorrectedBE();
  const fullInten = state.rawIntensity;

  // ROI-filtered data (for fitting, background, peaks)
  const { be, inten } = getROIData();
  const invert = document.getElementById('invert-be').checked;
  const showIndividual = document.getElementById('show-individual').checked;
  const showResiduals = document.getElementById('show-residuals').checked;

  const _ob = document.getElementById('main-chart-wrap').querySelector('.onboard-wrap');
  if (_ob) _ob.remove();

  if (!corrBE.length) {
    renderEmptyChart();
    return;
  }

  // After a fit, freeze all curve data to the stored fit state so that
  // changing ROI never re-draws or recomputes the fit, background, or peaks.
  const haveFit = !!(state.fitResult && Array.isArray(state.fitResult.be) &&
                     state.fitResult.be.length > 0 &&
                     Array.isArray(state.fitResult.bgIntensity) &&
                     state.fitResult.bgIntensity.length === state.fitResult.be.length);

  // plotBE/plotBG/plotInten drive all fit-related curves (peaks, background, envelope).
  // When a fit exists, they come from the frozen fit state — ROI changes don't affect them.
  // Before fitting, they come from the current ROI so live peak previews still work.
  const plotBE = haveFit ? state.fitResult.be : be;
  const plotBG = haveFit ? state.fitResult.bgIntensity
                         : (be.length ? computeBackground(be, inten) : []);
  const plotInten = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                    ? state.fitResult.bgSubtracted.map((v, i) => v + plotBG[i])
                    : inten;
  const bgSubtracted = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                       ? state.fitResult.bgSubtracted

codex
The Find Peaks refresh and last-tab clear are present. I also found a fourth `_restoreUI` caller in Batch Fit, beyond the three listed in the plan; I’m checking its redraw sequence along with support-verdict changes that could leave a tooltip stale.

exec
/bin/zsh -lc "rg -n 'function (_refreshStartsEvidence|_startsLiveKey|getCorrectedBE|runFitLocal|_restoreSnapshot|.*[Uu]ndo|.*[Hh]istory|.*[Aa]dopt)|_applyBackendParams\\(|applyBackendResult\\(|state.peaks\\s*=|\\.center\\s*[-+*/]?=' templates/index.html
sed -n '8180,8290p' templates/index.html
sed -n '10490,10580p' templates/index.html
sed -n '12020,12125p' templates/index.html
sed -n '15910,16095p' templates/index.html
sed -n '9455,9585p' templates/index.html
rg --files -g '*package*' -g '*browser*roi*' -g '*AGENTS*' -g 'pytest.ini' -g 'pyproject.toml' -g '*requirements*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
2359:function _historyTab() {
2382:function _restoreSnapshotProvenance(tab, snap) {
2386:function _restoreSnapshotEndpointAvg(tab, snap) {
2400:function pushUndo(extra) {
2408:function _pushUndoFor(tab, extra) {
2422:function _pushUndoDebounced() {
2432:function _flushUndoDebounce() {
2439:function _updateUndoButtons() {
2447:function undo() {
2456:  state.peaks = snap;
2472:  state.peaks = snap;
3235:    state.peaks = tab.peaks;
3303:      state.peaks = []; state.fitResult = null;
3423:      state.peaks = _normalizePeaksCRef((data.peaks || []).map(p => ({...p, support: null})));
5011:      p.center -= delta;
5053:function getCorrectedBE() {
5920:  state.peaks = state.peaks.filter(p => p.id !== id && p.linked !== id);
5930:  state.peaks = [];
5985:      if (key === 'center') parent.center = p.center - p.linkOffset;
5999:      if (key === 'center') child.center = parent.center + child.linkOffset;
6224:          oninput="getPeak(${p.id}).linkOffset=parseFloat(this.value);getPeak(${p.id}).center=getPeak(${p.linked}).center+parseFloat(this.value);updatePeakParam(${p.id},'center',getPeak(${p.id}).center)">
6507:function _applyBackendParams(p, par) {
6508:  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
6526:function applyBackendResult(result) {
6532:    _applyBackendParams(p, ipeak.params);
7005:  state.peaks     = snap.peaks;
7423:  state.peaks = [];
7436:  state.peaks = newPeaks;
7510:    applyBackendResult(json);
7601:function _startsLiveKey() {
7617:function _refreshStartsEvidence(repaint, fromPlot) {
7764:    _applyBackendParams(p, par);
7939:    applyBackendResult(backendResult);
8138:function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
8230:      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
10527:  state.peaks = active.peaks;
12078:      state.peaks = tgt.peaks; state.nextId = tgt.nextId; state.ccShift = tgt.ccShift;
13885:function showHistoryModal() {
13899:function _closeHistoryPanel() {
13903:function _renderHistoryList() {
13980:function _historyPreviewSnap(snapId) {
14004:function _historyClearPreview() {
14011:function _historyRestoreSnap(snapId) {
14018:  state.peaks = _normalizePeaksCRef(JSON.parse(JSON.stringify(snap.peaks)));
14031:function _historyDeleteSnap(snapId) {
14143:function _manualUndoAnchor() {
15968:  state.peaks = peaks.map((p, i) => {
      if (p.shape === 'DSG_LA') {
        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
      }
      if (p.shape === 'LACX') {
        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
        if (!p.fixCaM)     { freeParams.push(Number.isFinite(p.caM)     ? p.caM     : 50);  paramMap.push({id: p.id, param: 'caM'}); }
      }
    }
  }
  if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');

  // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
  // (owner decision 2026-09-18: zero allowed in both engines; a component at
  // its floor is an explicit outcome). The active-set step holds a parameter
  // pushed into the wall, and paramScale is floored at 1, so a zero amplitude
  // is a valid, stationary point rather than a division by zero.
  function clamp(param, v) {
    if (param === 'fwhm')         return Math.max(0.1, Math.min(15, v));
    if (param === 'amplitude')    return Math.max(0, v);
    if (param === 'glMix')        return Math.max(0, Math.min(100, v));
    if (param === 'asymmetry')    return Math.max(0, Math.min(1, v));
    if (param === 'dsAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'dsGamma')      return Math.max(0, Math.min(5.0, v));
    if (param === 'laAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'laBeta')       return Math.max(0.05, Math.min(2.0, v));
    if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
    if (param === 'caAlpha')      return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caBeta')       return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caM')          return Math.max(0,   Math.min(499, Math.round(v)));
    return v;
  }
  const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];

  function applyParams(params) {
    for (let i = 0; i < params.length; i++) {
      const { id, param } = paramMap[i];
      const p = workPeak(id);
      if (p) p[param] = clamp(param, params[i]);
    }
    // Linked peaks follow their parent: centre + offset, amplitude x ratio,
    // and every lineshape parameter (the same constraint set the backend
    // enforces through lmfit expressions).
    for (const q of work) {
      if (!q.linked) continue;
      const parent = workPeak(q.linked);
      if (!parent) continue;
      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
      if (Number.isFinite(q.linkRatio))  q.amplitude = parent.amplitude * q.linkRatio;
      q.fwhm = parent.fwhm;
      for (const k of LINK_SYNC_KEYS) if (parent[k] !== undefined) q[k] = parent[k];
    }
  }

  function rawResiduals(params) {
    applyParams(params);
    const model = evalAllPeaks(be, work);
    return be.map((_, i) => bgSubtracted[i] - model[i]);
  }
  // weighted residual: what the optimiser minimises (chi = sum of squares)
  function residuals(params) {
    return rawResiduals(params).map((v, i) => v * _w[i]);
  }

  function chiSq(params) {
    const r = residuals(params);
    return r.reduce((s, v) => s + v * v, 0);
  }

  let params = freeParams.map((v, i) => clamp(paramMap[i].param, v));
  let chi = chiSq(params);
  if (!Number.isFinite(chi)) return fail('the model is not finite at the starting parameters.');
  let lambda = 0.001;
  // Feasible-descent certificate (see PROBE_REL below). Returns true when
  // no single-parameter feasible move improves the residual by more than
  // FTOL; otherwise moves to the best such point and returns false.
  function certify() {
    applyParams(params);                     // working copy = current point
    let bestChi = chi, bestParams = null;
    for (let j = 0; j < params.length; j++) {
      if (isDiscrete(j)) continue;
      for (const sgn of [-1, 1]) {
        const trial = [...params];
        trial[j] = clamp(paramMap[j].param, params[j] + sgn * PROBE_REL * paramScale(j, params));
        if (trial[j] === params[j]) continue;
        const c = chiSq(trial);
        if (Number.isFinite(c) && c < bestChi) { bestChi = c; bestParams = trial; }
      }
    }
    applyParams(params);
    if (bestParams && bestChi < chi * (1 - FTOL)) {
      params = bestParams; chi = bestChi; certifyRestarts++;
      lambda = Math.max(lambda, 1e-3);
      return false;
    }
    return true;
  }
  // Finite-difference step per parameter. A centre's natural scale is the
  // peak WIDTH, not its binding energy: h*|285 eV| = 0.03 eV is wider than
  // a narrow peak and gave misleading derivatives (Codex round 1).
  const H_REL = 1e-4;
  // Scale of parameter j at the parameter VECTOR `vec` — a pure function of
  // the vector, never of the mutable working copy (which the Jacobian loop
  // leaves at its last perturbation — Codex round 5). A centre's scale is
  // its peak's width: from the vector when the width is free, from the
  // (never perturbed) fixed value otherwise.
  const fwhmIndex = {};
  paramMap.forEach((d, k) => { if (d.param === 'fwhm') fwhmIndex[d.id] = k; });
    }
    if (hasPeaks) {
      if (!_ownerActive(owner)) { notify('Fit file not applied — the tab changed while the file was being read.', 'amber'); return; }
      _applyFitJSON(data); return;
    }

    // No recognized structure — try as spectral data (CSV-like)
    _loadSpectralFile(file);
  } catch (err) {
    notify('Failed to load file: ' + err.message, 'red');
  }
}

async function handleSessionLoad(event) {
  const file = event.target.files[0];
  if (!file) return;
  event.target.value = '';
  await _loadSessionFile(file);
}

function _loadSpectrumFile(data, sessionFile) {
  // Audit F1/F4/F5: reject unsafe peak ids/links/colors before rendering.
  const pe = _peaksLoadError(data && data.peaks);
  if (pe) { notify('Spectrum not loaded: ' + pe + '.', 'red', true); return; }
  // Create a new tab with the saved spectrum data
  const srcPath = data.sourcePath || (sessionFile ? sessionFile : '(restored)');
  const active = tabManager.createTab(
    (data.spectrumName || 'Spectrum') + '.json',
    data.rawBE,
    data.rawIntensity,
    srcPath
  );
  if (!active) return;
  // Apply saved settings on top of the created tab
  active.ccShift = data.ccShift || 0;
  state.ccShift = active.ccShift;
  active.peaks = _normalizePeaksCRef((data.peaks || []).map(p => ({...p})));
  state.peaks = active.peaks;
  active.nextId = data.nextId || 1;
  state.nextId = active.nextId;
  // Manual bg anchors: saved by _doSaveSpectrum but previously never read
  // back here — the one anchor-persisting load path that dropped them (the
  // v1 fit-file loader and the project tab deserializer both restore).
  // Same verbatim convention as those two paths. Assigned BEFORE the ui
  // restore below: _restoreUI refreshes the manual-anchor count label from
  // the active tab, so assigning after it left the label stale (Codex
  // round-2 MINOR).
  if (Array.isArray(data.manualAnchors)) {
    active.manualAnchors = data.manualAnchors;
  }
  // Saved-ui boundary: a file whose ui lacks endpointAvg was fitted at 1
  // (the field did not exist), so it must NOT inherit the new-tab default;
  // saved values are honoured verbatim. Restore the DOM either way so the
  // record and the inputs agree before any switch-away capture.
  const savedEp = data.ui && data.ui.endpointAvg;
  active.ui = { ...active.ui, ...(data.ui || {}), endpointAvg: savedEp || LEGACY_ENDPOINT_AVG };
  tabManager._restoreUI(active.ui);
  if (data.notes) active.notes = data.notes;
  active.modelProvenance = _isLocalProvenance(data.modelProvenance) ? data.modelProvenance : null;
  if (data.statistics) {
    const fr = { chi: data.statistics.chi, chiReduced: data.statistics.chiReduced, rmse: data.statistics.rmse };
    for (const k of ['engine', 'objective', 'weighting', 'status', 'caveat', 'starts', 'startsModelKey', 'chosenAlternative']) if (data.statistics[k]) fr[k] = data.statistics[k];
    if (data.statistics.reportable !== undefined && data.statistics.reportable !== null) fr.reportable = data.statistics.reportable;
    if (data.fittedY) fr.fittedY = data.fittedY;
    active.fitResult = fr;
    state.fitResult = fr;
  }
  const notesEl = document.getElementById('spectrum-notes');
  if (notesEl) notesEl.value = active.notes || '';
  renderPeakList();
  updatePlot();
  renderResults();   // installs the restored result's designation in Results/Quantify and the statistic display (unit A0)
  notify('Spectrum loaded as new tab: ' + active.name, 'green');
}

// ── Project-load resource caps (audit F8) ─────────────────────────────
// Generous bounds, far above any real spectrum (a Thermo Nexsa survey is
// well under 10^6 points), so no legitimate file is ever rejected. They
// exist only to stop a crafted file from inflating the JS heap and freezing
// the tab. Adjust here if a genuinely larger dataset ever needs to load.
const MAX_PROJECT_TABS      = 100;                  // tabs per project
const MAX_SPECTRUM_POINTS   = 1000000;              // rawBE / rawIntensity length per tab
const MAX_ZIP_SPECTRA       = 100;                  // manifest.spectra entries (zip path)
const MAX_ZIP_UNCOMPRESSED  = 500 * 1024 * 1024;    // 500 MB total inflated (zip-bomb guard)
const MAX_ZIP_COMPRESSED_FALLBACK = 50 * 1024 * 1024; // 50 MB, used only if sizes are unreadable

function _loadProjectJSON(data, sessionFile) {
  // Per-tab peaks live under data.tabs[i].peaks (v2+) and/or top-level
  // data.peaks (v1). Migrate both shapes.
  if (data && Array.isArray(data.peaks)) _migrateLineshapeAliases(data.peaks);
  if (data && Array.isArray(data.tabs)) {
  // Compute source amplitude scale reference (max raw intensity in ROI)
  const srcMaxInten = _arrMax(sourceTab.rawIntensity);
  // SOURCE SNAPSHOT before the first yield: the source record can change
  // between targets (an async rollback, an edit on it), and every target
  // must receive the model the user pressed the button with (Codex round 3).
  const srcPeaks = JSON.parse(JSON.stringify(sourceTab.peaks || []));
  const srcUi = { ...(sourceTab.ui || {}) };
  const srcShift = sourceTab.ccShift;
  // A model copied from a local-derived source stays a starting point on
  // every target until a successful fit supersedes it (unit A0).
  const srcProvenance = _provenanceOf(sourceTab);

  const results = [];

  for (let i = 0; i < targets.length; i++) {
    const tgt = targets[i];
    const tid = tgt.id;
    if (!_ownerLive(tgt)) continue;                 // closed (or replaced by a reload) since the batch started

    prog.textContent = `Fitting spectrum ${i + 1}/${targets.length}: ${tgt.name}…`;

    // Scale factor based on max intensity ratio
    const tgtMaxInten = _arrMax(tgt.rawIntensity);
    const scale = srcMaxInten > 0 ? tgtMaxInten / srcMaxInten : 1;

    // Deep-clone source peaks, scaled
    const clonedPeaks = srcPeaks.map(p => ({
      ...p,
      amplitude: p.linked ? p.amplitude : p.amplitude * scale,
      support: null           // a propagated model has not been fitted: nothing is established (a copied verdict could never match this tab's key anyway)
    }));

    // Copy peak nextId
    const nextId = Math.max(0, ...clonedPeaks.map(p => p.id)) + 1;

    // Propagate background + ROI settings from source (BatchPropagation is the
    // single source of truth for the merge — see static/js/batch_propagation.js).
    // ccShift is copied separately just below.
    const newUi = BatchPropagation.propagateFitUi(srcUi, tgt.ui);

    // Apply to target tab record (without switching UI) — undoable on that record
    _pushUndoFor(tgt, { endpointAvg: tgt.ui && tgt.ui.endpointAvg });
    tgt.peaks = clonedPeaks;
    tgt.nextId = nextId;
    tgt.ui = newUi;
    tgt.ccShift = srcShift;
    tgt.chargeVerified = false;
    // A propagated model has not been fitted yet: the target's previous
    // result belonged to its previous peaks (unit A0 acceptance rule).
    tgt.fitResult = null;
    tgt.modelProvenance = srcProvenance ? { ...srcProvenance, copiedFrom: sourceTab.name } : null;

    // Now activate this tab so state is populated. activateTab is a no-op
    // when the target is ALREADY active (the user switched to it during the
    // previous target's fit): then live state still holds the target's old
    // model and the post-fit sync would overwrite the propagated record —
    // load the record into live state explicitly (Codex round 3, run B).
    if (tabManager.activeId === tid) {
      state.peaks = tgt.peaks; state.nextId = tgt.nextId; state.ccShift = tgt.ccShift;
      state.fitResult = null;   // live copy of tgt.fitResult = null above (unit A0)
      tabManager._restoreUI(tgt.ui);
      renderPeakList();
    } else {
      tabManager.activateTab(tid);
    }

    // Small yield so progress message renders
    await new Promise(r => setTimeout(r, 20));
    if (_activeTab() !== tgt) {
      // The user switched tabs during the yield: fitting would read and
      // write whichever tab is active now. Stop here; targets already
      // fitted keep their results.
      notify('Batch fit stopped at ' + tgt.name + ' — the tab changed while it was running.', 'amber');
      break;
    }

    // Run local fit
    const roiSt = _roiWindowStatus();    // warn only: the fit below uses getROIData() exactly as before
    const { be, inten } = getROIData();
    const bgI = computeBackground(be, inten);
    const bgSub = inten.map((v, idx) => v - bgI[idx]);
    const outcome = runFitLocal(be, bgSub, bgI);

    // Sync result back to record
    tabManager._syncActiveToRecord();

    // Read the statistic from the fit's own return value, not from live
    // state: the active tab can change while the fit runs.
    const ok = !!(outcome && outcome.success);
    results.push({ name: tgt.name, ok, roiHint: _roiHintFor(roiSt),
                   chi: ok && Number.isFinite(outcome.chiReduced) ? outcome.chiReduced : null,
                   message: ok ? null : ((outcome && outcome.message) || 'local fit did not converge') });

    await new Promise(r => setTimeout(r, 10));
  }

  _snapshotSuppressed = false;

  // Return to source tab
  tabManager.activateTab(sourceId);

  const nOk = results.filter(r => r.ok).length;
  const nFail = results.length - nOk;
  prog.textContent = `Batch complete: ${nOk} converged as starting points, ${nFail} not fitted. Run Fit on each spectrum before reporting.`;
  const roiNote = r => r.roiHint ? ` <span class="roi-hint${r.roiHint.cls ? ' ' + r.roiHint.cls : ''}" style="display:inline">${_escHtml(r.roiHint.text)}</span>` : '';
  summary.innerHTML = results.map(r => r.ok
}

// One-time "these are unverified" confirmation, replacing the old
// required-reviewer-name gate. Same Promise/resolver pattern as
// _showAutoFitConfirmModal/_autoFitConfirmCancel.
let _findPeaksApplyConfirmResolver = null;
function _showFindPeaksApplyConfirmModal() {
  return new Promise(resolve => {
    _findPeaksApplyConfirmResolver = resolve;
    const proceed = document.getElementById('find-peaks-apply-confirm-proceed');
    proceed.onclick = () => {
      document.getElementById('find-peaks-apply-confirm-overlay').classList.remove('open');
      const r = _findPeaksApplyConfirmResolver; _findPeaksApplyConfirmResolver = null;
      if (r) r(true);
    };
    document.getElementById('find-peaks-apply-confirm-overlay').classList.add('open');
  });
}
function _findPeaksApplyConfirmCancel() {
  document.getElementById('find-peaks-apply-confirm-overlay').classList.remove('open');
  const r = _findPeaksApplyConfirmResolver; _findPeaksApplyConfirmResolver = null;
  if (r) r(false);
}

async function applyFindPeaks() {
  const owner = _opOwner();              // the record this apply belongs to
  const _fpLast = _fpGetLast();          // the ACTIVE tab's own result, or nothing
  if (!owner || !_fpLast) return;
  const peaks = (_fpLast.body.peaks || []);
  if (!peaks.length) { notify('Nothing to apply — the analysis emitted no peaks.', 'amber'); return; }
  if (state.peaks.length &&
      !confirm('Replace the ' + state.peaks.length + ' peak(s) on this tab ' +
               'with the ' + peaks.length + ' suggested peak(s)? ' +
               'You can undo this.')) return;
  if (!(await _showFindPeaksApplyConfirmModal())) return;
  if (!_ownerActive(owner)) {
    // The tab changed (or closed) while the confirmation was open: the
    // suggestions belong to the tab they were produced on, so nothing is
    // written anywhere.
    notify('Apply cancelled — the tab changed while the confirmation was open.', 'amber');
    return;
  }
  // the manual path's real undo: the replaced peak list must be Ctrl-Z
  // recoverable (Codex analyze review blocker). This action also changes
  // endpoint averaging (below), so the undo entry carries the pre-apply
  // value and undo/redo restore it with the peaks.
  pushUndo({ endpointAvg: document.getElementById('bg-endpoint-avg')?.value });
  // DURABLE provenance record: stamped on every applied peak (peak objects
  // round-trip through project save/load with extra fields intact, like
  // _rsfKey does) — no reviewer name anymore, but autoSuggested/verified
  // keep the "these came from Find Peaks and haven't been checked" fact
  // alive through save/load.
  const review = {
    autoSuggested: true, verified: false,
    method: _fpLast.method, regions: _fpLast.regions,
    winner: (_fpLast.body.diagnostics || {}).winner || null,
    at: new Date().toISOString(),
  };
  state.peaks = peaks.map((p, i) => {
    const fp = _fpPeakFromBackend(p, i);
    fp._findPeaks = review;
    return fp;
  });
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // the replaced model's provenance does not describe these peaks
  const active = tabManager.tabs.find(t => t.id === tabManager.activeId);
  if (active) active._findPeaksReview = review;
  // Find Peaks now sends the Background panel's endpoint averaging (see
  // runFindPeaks), so normally this is a no-op. It still guards preview ==
  // fit when the panel was changed between the run and the apply, or when
  // the Advanced JSON named a different value: the panel and the tab
  // record are set to what the engine actually used, with a notice.
  // (No _invalidateBgCache() here: with "fit the entire window" OFF the
  // frozen fit display must stay exactly as today — invalidating the cache
  // un-froze it, caught by test_checkbox_off_preserves_todays_cropped_behavior;
  // with it ON, state.fitResult is cleared below and the preview recomputes
  // from the panel value anyway.)
  const usedEp = (_fpLast && _fpLast.endpointAvg) || LEGACY_ENDPOINT_AVG;
  const epEl = document.getElementById('bg-endpoint-avg');
  const epChanged = !!epEl && epEl.value !== usedEp;
  if (epEl) epEl.value = usedEp;
  if (active) active.ui.endpointAvg = usedEp;   // unconditional: the record must match the fit even if the field was hand-edited
  if (epChanged) {
    notify('Find Peaks fitted with endpoint averaging ' + usedEp + '; the Background panel was set to ' +
           usedEp + ' so the preview matches the fit.', 'amber');
  }
  // The chart FREEZES its background/fit-curve display to state.fitResult's
  // OWN be/bgIntensity arrays once a fit exists (updatePlot's "haveFit"
  // branch) — a prior manual Run Fit or Auto-Fit C1s Graphite leaves this
  // set, frozen to THAT fit's own (possibly narrower) range. Applying new
  // Find Peaks peaks on top never touched it, so the chart kept showing
  // background/fit cropped to the OLD frozen range regardless of how wide
  // a window Find Peaks actually used — root cause of "fit + background
  // don't span the full selected window" (2026-07-14 bug report). Find
  // Peaks' own response has no be/fittedY/bgIntensity arrays to rebuild a
  // proper fitResult from, so when this run used "fit the entire window,"
  // clear it instead: updatePlot() then falls back to its existing
  // unfit-preview path (getROIData() + client-side computeBackground()),
  // exactly like peaks placed manually before any Run Fit — spanning the
  // CURRENT #roi-min/#roi-max, i.e., the full window Find Peaks just used.
  // Default (unchecked) leaves state.fitResult untouched — today's
  // behavior, unchanged.
  if (_fpLast && _fpLast.fitFullWindow) {
    state.fitResult = null;
    // Clearing state.fitResult fixes the CHART (updatePlot's "haveFit"
    // branch), but the status-bar widgets (χ²ᵣ, R-factor, "ROI: ...")
    // are a SEPARATE piece of DOM state that only refreshes when
    // explicitly told to (Codex review finding, 2026-07-14: this was
    // the other half of the bug report's exact symptom — the header
    // could still read the OLD fit's stale "ROI: 278.0-290.4 eV" even
    // after the chart itself had been fixed). Reset them to the SAME
    // "no committed fit yet" state TabManager.activateTab already uses
    // when a tab has no state.fitResult, rather than inventing a new
    // convention.
    const fqEl = document.getElementById('fit-quality');
    if (fqEl) { fqEl.innerHTML = '&#967;&#178; &mdash;'; fqEl.removeAttribute('data-xps-tip'); }
    const chiEl = document.getElementById('sb-chi');
    if (chiEl) chiEl.textContent = '—';
    _updateRFactorUI(null);
    _updateROIDisplay(null);
    // The right-side Results panel (#results-area) is a THIRD piece of
    // DOM state keyed off state.fitResult, separate from both the chart
    // and the status bar (Codex recheck finding, 2026-07-14): without
    // this call it kept showing the OLD fit's chi/RMSE/table after
    // state.fitResult was cleared, until some unrelated later action
    // happened to re-render it. renderResults() already handles
    // state.fitResult === null correctly (falls back to its own
    // "Run the fit to see results." placeholder).
    renderResults();
  }
  renderPeakList();
  updatePlot();
  closeFindPeaksModal();
  notify(_fpFmt(FP_STRINGS.toastApplied, { n: peaks.length }), 'amber', true);
}
</script>
</body>
</html>
  // plotBE/plotBG/plotInten drive all fit-related curves (peaks, background, envelope).
  // When a fit exists, they come from the frozen fit state — ROI changes don't affect them.
  // Before fitting, they come from the current ROI so live peak previews still work.
  const plotBE = haveFit ? state.fitResult.be : be;
  const plotBG = haveFit ? state.fitResult.bgIntensity
                         : (be.length ? computeBackground(be, inten) : []);
  const plotInten = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                    ? state.fitResult.bgSubtracted.map((v, i) => v + plotBG[i])
                    : inten;
  const bgSubtracted = haveFit && Array.isArray(state.fitResult.bgSubtracted)
                       ? state.fitResult.bgSubtracted
                       : plotInten.map((v, i) => v - plotBG[i]);

  const modelFull = evalAllPeaks(plotBE, state.peaks);
  // Use backend fitted_y when available (authoritative lmfit result);
  // fall back to JS-recomputed modelFull + bg for pre-fit / local-LM fits.
  const fittedYBacked = haveFit && state.fitResult.fittedY &&
                        state.fitResult.fittedY.length === plotBE.length
                        ? state.fitResult.fittedY : null;
  const rawResiduals = fittedYBacked
    ? plotInten.map((v, i) => v - fittedYBacked[i])
    : bgSubtracted.map((v, i) => v - modelFull[i]);
  // Percentage residuals: ((data - fit) / data) × 100, clamped to ±100%
  const residuals = rawResiduals.map((r, i) => {
    const d = fittedYBacked ? plotInten[i] : bgSubtracted[i];
    if (Math.abs(d) < 1e-10) return 0;
    return Math.max(-100, Math.min(100, (r / d) * 100));
  });

  const datasets = [];

  // Bkgrd Sub view: redraws the chart with the background subtracted.
  // The flag is read once per updatePlot() call so all dataset branches
  // see a consistent value. _isBgSubViewActive() is defensive — it
  // returns false if bg-type is "none" even when the pill is checked.
  const bgSubView = _isBgSubViewActive();

  // Individual peaks drawn first (bottom layer) — frozen to fit range after fit
  const showFill = document.getElementById('show-fill').checked;
  if (showIndividual && plotBE.length) {
    if (showFill) {
      // First add invisible background-level datasets as fill targets
      for (let pi = 0; pi < state.peaks.length; pi++) {
        const p = state.peaks[pi];
        datasets.push({
          label: '_bg_' + p.id,
          data: plotBE.map((b, i) => ({ x: b, y: bgSubView ? 0 : plotBG[i] })),
          borderColor: 'transparent',
          borderWidth: 0,
          pointRadius: 0,
          fill: false,
          hidden: false,
        });
      }
    }
    for (let pi = 0; pi < state.peaks.length; pi++) {
      const p = state.peaks[pi];
      const fillTarget = showFill ? { target: pi, above: p.color + '40', below: 'transparent' } : false;
      const peakY = evalPeakArray(plotBE, p);
      datasets.push({
        label: _isUnsupported(p) ? p.name + ' (' + _UNSUPPORTED_LABEL + ')' : p.name,
        _unsupported: _isUnsupported(p),
        data: plotBE.map((b, i) => ({ x: b, y: peakY[i] + (bgSubView ? 0 : plotBG[i]) })),
        borderColor: p.color,
        backgroundColor: p.color + '40',
        borderWidth: state.lineWidth ?? 1.5,
        pointRadius: 0,
        fill: fillTarget,
        tension: 0,
        _peakId: p.id
      });
    }
  }

  // Background — frozen to fit range after fit. Hidden in subtracted view.
  if (plotBE.length && !bgSubView) {
    datasets.push({
      label: 'Background',
      data: plotBE.map((b, i) => ({ x: b, y: plotBG[i] })),
      borderColor: '#4a5a78',
      borderWidth: 1,
      borderDash: [4, 3],
      pointRadius: 0,
      fill: false
    });
  }

  // Raw data — FULL spectrum range in raw view; ROI-only subtracted in
  // subtracted view (background only exists for the ROI window).
  const _cc = _chartColors();
  datasets.push({
    label: 'Data',
    data: bgSubView
      ? plotBE.map((b, i) => ({ x: b, y: plotInten[i] - plotBG[i] }))
      : corrBE.map((b, i) => ({ x: b, y: fullInten[i] })),
    borderColor: _cc.rawData,
    backgroundColor: document.body.classList.contains('light-theme')
      ? 'rgba(26,26,46,0.08)' : 'rgba(232,237,245,0.08)',
    pointRadius: 0,
    borderWidth: state.lineWidth ?? 1.5,
    tension: 0,
    fill: false
  });

  // Fit envelope — frozen to fit range after fit; use backend fitted_y when available
  const showEnvelope = document.getElementById('show-envelope').checked;
  if (showEnvelope && plotBE.length && (fittedYBacked || state.peaks.length)) {
    datasets.push({
      label: _isLocalModel() ? 'Fit (local, starting point)' : 'Fit',
      data: fittedYBacked
        ? plotBE.map((b, i) => ({ x: b, y: fittedYBacked[i] - (bgSubView ? plotBG[i] : 0) }))
        : plotBE.map((b, i) => ({ x: b, y: modelFull[i] + (bgSubView ? 0 : plotBG[i]) })),
      borderColor: '#ff2020',
      borderWidth: Math.min((state.lineWidth ?? 1.5) + 1, 6),
      pointRadius: 0,
      fill: false
    });
  }

  _refreshStartsEvidence(false, true);   // background / ROI controls only repaint the chart: keep the visible consumers honest (fromPlot: the chart itself is being rebuilt)
  _refreshRoiAndCentreWarnings();         // ROI past the data / centre outside the data: warn, never move
  // History snapshot preview overlay (cyan dashed, drawn on top)
  if (_historyPreview && _historyPreview.peaks && _historyPreview.peaks.length && plotBE.length) {
    const prevPeakY = evalAllPeaks(plotBE, _historyPreview.peaks);
    const isLight = document.body.classList.contains('light-theme');
    datasets.push({
      label: _isLocalFit(_historyPreview.fitResult) ? 'Preview (local, starting point)' : 'Preview',
      _historyPreview: true,   // the glow plugin keys on this flag, not on the label text
      data: plotBE.map((b, i) => ({ x: b, y: prevPeakY[i] + (bgSubView ? 0 : plotBG[i]) })),
      borderColor: isLight ? 'rgba(0,180,220,1.0)' : 'rgba(0,220,255,1.0)',
      borderWidth: 4,
requirements-dev.txt
requirements.txt
tests/test_browser_batch_roi.py

exec
/bin/zsh -lc "sed -n '2440,2490p' templates/index.html
sed -n '5030,5078p' templates/index.html
sed -n '7560,7655p' templates/index.html
sed -n '7740,7798p' templates/index.html
sed -n '8580,8645p' templates/index.html
sed -n '13935,14035p' templates/index.html
sed -n '7235,7340p' templates/index.html
rg -n 'renderPeakList\\(|updatePlot\\(' templates/index.html | awk '"'$1+0 >= 7900 && $1+0 <= 8700'"'
ls -d .venv venv /tmp/browser_check_roi.py 2>/dev/null
node --test tests/js/*.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
exec
/bin/zsh -lc "sed -n '9600,9720p' templates/index.html
sed -n '8520,8600p' templates/index.html
sed -n '7260,7350p' templates/index.html
sed -n '13940,13950p' templates/index.html
sed -n '14010,14032p' templates/index.html
sed -n '7758,7818p' templates/index.html
sed -n '15455,15520p' templates/index.html
rg -n 'length < 2|length <= 1|function computeBackground' templates/index.html
node --test tests/js/roi_clamp_centre_warning.test.js tests/js/unsupported_components.test.js | tail -12" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 280ms:
  duration_ms: 4.333307
  type: 'test'
  ...
1..37
# tests 37
# suites 0
# pass 37
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 272.407654

codex
The focused ROI/support tests pass: 37/37. The audited centre-update paths reach a redraw, and the tooltip uses the current support key. The full JS run hit Python import failures because the read-only sandbox has no writable temporary directory, so I can’t confirm the reported full-suite result here. I’m finishing the empty-state and documentation checks.

exec
/bin/zsh -lc "sed -n '6550,6650p' templates/index.html
sed -n '8380,8525p' templates/index.html
sed -n '4690,4750p' templates/index.html
sed -n '7890,7985p' templates/index.html
sed -n '1,90p' tests/test_component_required.py
rg -n 'uploadToBackend|corrected >=|corrected <=|be_min|be_max' app.py | head -45
rg -n 'function uploadToBackend|toFixed\\(4\\)' templates/index.html
rg -n 'function _fpPeakFromBackend|Object.assign|center:' templates/index.html | head -90
rg -n 'function _renderStackChart|function _updateStackChart|renderEmptyChart\\(' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:

let _bgSubFitInFlight = false;

// IDs of overlay controls that don't compose with subtracted view
// (they're full-spectrum / non-bg-aware). When subtracted view is
// effectively active we disable them with the existing app
// convention (opacity 0.4 + disabled attr + title tooltip), so users
// see why their checkbox appears inert. Identical pattern to how
// `shirley-iter` is gated when bg-type doesn't need iteration.
const _BG_SUB_DEPENDENT_CONTROL_IDS = ['smooth-enable', 'deriv1-enable', 'deriv2-enable'];

function _isBgSubViewActive() {
  const toggle = document.getElementById('bg-sub-toggle');
  if (!toggle || !toggle.checked) return false;
  // Even if the pill is checked, fall back to raw view when bg is
  // unavailable (defensive: covers the moment between bg-type=none
  // and the pill recompute, and any transient bg gap).
  const bgType = document.getElementById('bg-type')?.value || 'shirley';
  if (bgType === 'none') return false;
  if (!state.rawBE || state.rawBE.length < 2) return false;
  return true;
}

function _updateBgSubPillEnabled() {
  const pill = document.getElementById('bg-sub-pill');
  const toggle = document.getElementById('bg-sub-toggle');
  if (!pill || !toggle) return;
  const fitting = _bgSubFitInFlight;

  // Stack tabs: bg-sub semantics are per-entry. Enable the pill if at
  // least one entry has render data with a usable bg array. state.rawBE
  // is empty/inert for stack tabs so the spectrum-mode gating would
  // otherwise leave the toggle permanently disabled.
  const activeTab = (typeof tabManager !== 'undefined') ? tabManager._getTab(tabManager.activeId) : null;
  if (activeTab && activeTab.isStack) {
    let anyBg = false;
    for (const e of (activeTab.entries || [])) {
      if (!_entryHasFit(e)) continue;
      const rd = _getEntryRenderData(e);
      if (rd && Array.isArray(rd.bg) && rd.bg.length > 0) { anyBg = true; break; }
    }
    const disabled = !anyBg || fitting;
    toggle.disabled = disabled;
    pill.classList.toggle('disabled', disabled);
    if (fitting) {
      pill.title = 'Background subtraction toggle is locked while a fit is running.';
    } else if (!anyBg) {
      pill.title = 'No entries with a usable background in this stack.';
    } else {
      pill.title = 'Toggle background-subtracted chart view (per entry).';
    }
    return;
  }

  // Spectrum-tab path (unchanged).
  const bgType = document.getElementById('bg-type')?.value || 'shirley';
  const noBg = bgType === 'none';
  const noSpectrum = !state.rawBE || state.rawBE.length < 2;
  const disabled = noBg || noSpectrum || fitting;
  toggle.disabled = disabled;
  pill.classList.toggle('disabled', disabled);
  if (fitting) {
    pill.title = 'Background subtraction toggle is locked while a fit is running.';
  } else if (noSpectrum) {
    pill.title = 'Load a spectrum to enable background subtraction.';
  } else if (noBg) {
    pill.title = 'Background subtraction is unavailable when no background method is set.';
  } else {
    pill.title = 'Toggle background-subtracted chart view.';
  }
}

function _onBgSubToggle() {
  const toggle = document.getElementById('bg-sub-toggle');
  const pill = document.getElementById('bg-sub-pill');
  if (!toggle || !pill) return;
  pill.classList.toggle('active', toggle.checked);
  // Persist into the active tab's UI snapshot so save/restore round-trip.
  // Skip stack tabs — their ui block is inert and bg-sub is a view-mode
  // tweak applied per-entry at render time, not tab-scoped state.
  if (typeof tabManager !== 'undefined' && tabManager.activeId) {
    const t = tabManager._getTab(tabManager.activeId);
    if (t && !t.isStack && t.ui) t.ui.bgSubtractedView = toggle.checked;
  }
  _syncSubViewDependentControls();
  updatePlot();
}

// Disable controls that don't compose with subtracted view, so their
// checkboxes don't read as "broken" when toggling them does nothing
// visible. Re-enable when subtracted view is off. Tooltip mirrors the
// future-enhancement note in the plan.
function _syncSubViewDependentControls() {
  const subActive = _isBgSubViewActive();
  for (const id of _BG_SUB_DEPENDENT_CONTROL_IDS) {
    const el = document.getElementById(id);
    if (!el) continue;
    el.disabled = subActive;
    // Apply opacity to the wrapping label so the visual disable is
    // obvious — matches the shirley-iter / bg-endpoint-avg pattern.
    const wrap = el.closest('label') || el.parentElement;
      if (Jtr[j] !== 0) {
        const probe = clamp(paramMap[j].param, params[j] - Math.sign(Jtr[j]) * 1e-6 * paramScale(j, params));
        if (probe === params[j]) continue;          // blocked by the box
      }
      active.push(j);
      if (rNorm > 0) gradCos = Math.max(gradCos, Math.abs(Jtr[j]) / (Math.sqrt(JtJ[j][j]) * rNorm));
    }
    // Projected gradient test (gtol) over the active set only. A failed
    // certificate has moved the point: restart the iteration so the
    // derivatives and active set are rebuilt there.
    if (gradCos < GTOL) { if (certify()) { converged = true; break; } continue; }
    // Linear model of the residual, for the predicted reduction (ftol test).
    const JtJ0 = JtJ.map(row => row.slice());

    // Marquardt damping, then the DESCENT step on the active set:
    // JtJ_aa . dp_a = -Jt.r_a, dp = 0 for held parameters.
    const m = active.length;
    const A = active.map(a => active.map(b => (a === b ? JtJ[a][a] * (1 + lambda) + 1e-300 : JtJ[a][b])));
    const rhs = active.map(a => -Jtr[a]);
    const dpA = solveLinear(A, rhs, m);
    if (!dpA.every(Number.isFinite)) return fail('the normal equations are singular.', iterations);
    const dp = new Array(n).fill(0);
    active.forEach((a, k) => { dp[a] = dpA[k]; });
    const newParams = params.map((v, i) => clamp(paramMap[i].param, v + dp[i]));
    const step = newParams.map((v, i) => v - params[i]);
    const newChi = chiSq(newParams);

    if (Number.isFinite(newChi) && newChi < chi) {
      const actred = (chi - newChi) / Math.max(chi, 1e-300);
      // predicted reduction of the linearised problem: (2 Jt.r . (-dp) - dp.JtJ.dp) / chi
      let lin = 0, quad = 0;
      for (let a = 0; a < n; a++) {
        lin += Jtr[a] * step[a];
        for (let b = 0; b < n; b++) quad += step[a] * JtJ0[a][b] * step[b];
      }
      const prered = (-2 * lin - quad) / Math.max(chi, 1e-300);
      const relStep = Math.max(0, ...step.map((d, i) => Math.abs(d) / paramScale(i, params)));
      params = newParams;
      chi = newChi;
      acceptedSteps++;
      lambda *= 0.7;
      if (chi === 0 || (prered > 0 && actred <= FTOL && prered <= FTOL && actred / prered <= 2) || relStep <= XTOL) {
        if (certify()) { converged = true; break; }
      }
    } else {
      lambda *= 3;
      if (lambda > 1e8) {
        // Even a tiny steepest-descent step no longer reduces the residual,
        // yet the projected gradient is not small: stalled, not converged.
        return fail('the optimiser stalled (no step reduces the residual) after ' + iterations + ' iterations.', iterations);
      }
    }
  }
  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);

  // ── Converged: commit the working copy to the live peaks ──────────────────
  applyParams(params);
  for (const p of work) {
    const live = getPeak(p.id);
    if (!live) continue;
    Object.assign(live, p);
    // A local fit has no backend covariance; any _backendParams on the peak
    // belong to an earlier server fit (or, in Batch Fit, to the SOURCE
    // spectrum's fit) and must not travel with this result.
    delete live._backendParams;
  }

  // Degrees of freedom count the parameters this engine actually varies: the
  // integer-clamped caM is carried at its start value and is not one of them
  // (continuous parameters temporarily blocked at a wall still count).
  const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
  const dof = Math.max(1, be.length - nVaried);
  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
  const _raw = rawResiduals(params);
  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
  // "Not supported by the data": the same removal statistic the server
  // computes, from this engine's own residuals and weights (a component driven
  // to the zero floor is an outcome here too, not something to hide).
  {
    const model = evalAllPeaks(be, work);
    const verdicts = {};
    for (const wp of work) {
      if (wp.linked) continue;
      const comp = evalPeakArray(be, wp);
      const nFreeComp = paramMap.filter(d => d.id === wp.id && !isDiscrete(paramMap.indexOf(d))).length;
      verdicts[String(wp.id)] = _componentSupportCore(bgSubtracted, model, comp, _w, nFreeComp, nVaried);
    }
    _applySupportVerdicts(state.peaks, id => verdicts[String(id)] || null, _startsLiveKey());
  }

  // KNOWN LIMITATION: this engine produces no parameter uncertainties; the
  // results panel shows blank sigma for every parameter after a local fit.
  const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
  { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
  state.fitResult = { chi, chiReduced, rmse, be, bgSubtracted, bgIntensity, roiRange,
                      engine: 'local', status: 'converged',
                      objective: 'poisson_weighted_chi_square', weighting: '1/sqrt(max(counts,1))', iterations,
                      reportable: false, caveat: _LOCAL_FIT_CAVEAT };
  state.fitResult.rFactor = _computeRFactor(state.fitResult);

  _applyStatDisplay(state.fitResult);
  document.getElementById('sb-msg').textContent = 'Fit complete (local)';
  _updateRFactorUI(state.fitResult.rFactor);
  _updateROIDisplay(roiRange);

  renderPeakList();
  updatePlot();
  renderResults();

  _hideFitSpinner();
  notify('Local fit converged in ' + iterations + ' iteration' + (iterations === 1 ? '' : 's') +
         '. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3) + ' (Poisson-weighted; no uncertainties). Starting point only: run Fit before reporting.', 'amber');
  _autoSnapshot();
  return { success: true, engine: 'local', iterations, acceptedSteps, chiReduced, certifyRestarts };
}

function solveLinear(A, b, n) {
  const M = A.map((row, i) => [...row, b[i]]);
  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(M[row][col]) > Math.abs(M[maxRow][col])) maxRow = row;
    }
    [M[col], M[maxRow]] = [M[maxRow], M[col]];
    for (let row = col + 1; row < n; row++) {
      if (Math.abs(M[col][col]) < 1e-15) continue;
      const f = M[row][col] / M[col][col];
      for (let k = col; k <= n; k++) M[row][k] -= f * M[col][k];
    }
  }
  const x = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    if (Math.abs(M[i][i]) < 1e-15) { x[i] = 0; continue; }
    x[i] = M[i][n];
    for (let j = i + 1; j < n; j++) x[i] -= M[i][j] * x[j];
    x[i] /= M[i][i];
  }
  return x;
}

// ═══════════════════════════════════════════════════
// RESULTS
// ═══════════════════════════════════════════════════

// Build {peakId: paramMap} from backend fit result (null-safe)
function _buildStderrMap(fitResult) {
function computeBackgroundCore(be, intensity, settings) {
  const type = settings.bgType;
  const iter = parseInt(settings.shirleyIter) || 5;
  const nAvg = parseInt(settings.endpointAvg) || 1;

  // Manual anchor background uses its own anchor points, not bg-start/end
  if (type === 'manual') return manualAnchorBackground(be, intensity);

  // The background window — the one definition shared with both /api/fit
  // request builders (see _bgWindowIndices). A blank bound or a window with
  // fewer than two points falls back to the full range inside the helper;
  // slicing the full range below is then a no-op.
  const { i0, i1 } = _bgWindowIndices(be, settings.bgStart, settings.bgEnd);

  // Slice data to background region
  const beSub = be.slice(i0, i1 + 1);
  const inSub = intensity.slice(i0, i1 + 1);

  // Compute background on the sliced region — apply endpoint averaging for Shirley types
  let bgSub;
  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
  else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
  // Averaged for the same reason as Shirley types: the Tougaard amplitude
  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
  // directly. Mirrors fitting.py's run_fit / compute_background_only.
  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
  else return new Array(be.length).fill(0);

  // Extend background across full data range:
  // - Points before bg region: hold first bg value (flat)
  // - Points inside bg region: use computed bg
  // - Points after bg region: hold last bg value (flat)
  const full = new Array(be.length).fill(0);
  const bgLeft  = bgSub[0];
  const bgRight = bgSub[bgSub.length - 1];

  for (let i = 0; i < be.length; i++) {
    if (i < i0) full[i] = bgLeft;
    else if (i <= i1) full[i] = bgSub[i - i0];
    else full[i] = bgRight;
  }

  return full;
}

// Thin DOM-reading wrapper used by single-tab updatePlot. Stack render
// path calls computeBackgroundCore directly with source-tab settings.
function computeBackground(be, intensity) {
  return computeBackgroundCore(be, intensity, {
    bgType:      document.getElementById('bg-type').value,
    shirleyIter: document.getElementById('shirley-iter').value,
    endpointAvg: document.getElementById('bg-endpoint-avg').value,
    bgStart:     document.getElementById('bg-start').value,
    bgEnd:       document.getElementById('bg-end').value,
  });
}

// ═══════════════════════════════════════════════════
    if (resp.ok === false) {
      // HTTP failure: read a message if the body is JSON, but a 502 HTML
      // page is still a SERVER failure, never a reason to switch engines.
      let msg = null;
      try { const j = await resp.json(); msg = (j && (j.error || j.message)) || null; } catch (_) { /* non-JSON body */ }
      const err = new Error(msg || ('Fit request failed (HTTP ' + resp.status + ').'));
      err.serverError = true;
      throw err;
    }
    try { json = await resp.json(); } catch (e) { _asTransport(e); }
    if (json.error) {
      const err = new Error(json.error);
      err.serverError = true;
      throw err;
    }
    // ACCEPTANCE RULE: the backend reports lmfit's own convergence flag. A
    // result that did not converge is a failed fit, not a result (audit A08:
    // until this unit success:false was applied and announced as complete).
    if (json.success !== true) {
      const err = new Error(json.message || 'the optimizer did not converge.');
      err.notConverged = true;
      throw err;
    }
    backendResult = json;

    // If the user switched tabs while the fit was running, discard the result
    // rather than overwriting the now-active tab's peaks.
    if (!_ownerActive(fittingTab)) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit result discarded because you switched tabs during the fit.', 'amber');
      return;
    }

    // The peak controls stay editable while the fit runs. A result computed for
    // the model as it was must not be applied over an edited one (a newly locked
    // centre would keep its edited value under the server's statistics).
    if (_startsLiveKey() !== ctxAtRequest) {
      _hideFitSpinner();
      document.getElementById('sb-msg').textContent = 'Fit discarded (model edited)';
      notify('Fit result discarded because the model or its background / ROI settings were edited while the fit was running. Previous peaks and result kept. Run the fit again.', 'amber', true);
      return;
    }

    // Capture pre-fit values for uncertainty validation
    const _preFit = {};
    for (const p of state.peaks) {
      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
    }
    applyBackendResult(backendResult);
    { const _t = _activeTab(); if (_t) _t.modelProvenance = null; }   // a new result supersedes imported provenance
    const stats = backendResult.statistics || {};
    const chiReduced = stats.reduced_chi_square || 0;
    const rmse = Math.sqrt((backendResult.residuals || []).reduce((s, v) => s + v * v, 0) / Math.max(1, be.length));
    const roiRange = { min: _arrMin(be).toFixed(1), max: _arrMax(be).toFixed(1) };
    state.fitResult = { chi: chiReduced * Math.max(1, be.length - state.peaks.length * 3),
                        chiReduced, rmse, be, bgSubtracted, bgIntensity, backendResult,
                        fittedY: backendResult.fitted_y, roiRange, _preFit,
                        starts: backendResult.starts || null,
                        startsModelKey: _startsLiveKey(),     // model + context, taken AFTER the result was applied
                        chosenAlternative: opts.chosenAlternative || null };
    // a preview of an alternative always belongs to the PREVIOUS result (an identical
    // key does not make it this one's): clear it unconditionally
    if (_historyPreview && typeof _historyPreview.snapId === 'string' && _historyPreview.snapId.startsWith('alt:')) _historyPreview = null;
    state.fitResult.rFactor = _computeRFactor(state.fitResult);
    _applyStatDisplay(state.fitResult);
    document.getElementById('sb-msg').textContent = 'Fit complete (lmfit)';
    _updateRFactorUI(state.fitResult.rFactor);
    _updateROIDisplay(roiRange);
    _hideFitSpinner();
    notify('Fit complete. \u03c7\u00b2\u1d63 = ' + chiReduced.toFixed(3), 'green');
  } catch (e) {
    // Fall back to local Levenberg-Marquardt
    _hideFitSpinner();
    if (!_ownerActive(fittingTab)) {
      document.getElementById('sb-msg').textContent = 'Fit discarded (tab changed)';
      notify('Fit cancelled — tab switched during fit.', 'amber');
      return;
    }
    if (e && e.transportFailure && opts.startPeaks) {
      // Adopting an alternative needs the server: the local engine would start
      // from the live model, not from the alternative. Nothing was changed.
      document.getElementById('sb-msg').textContent = 'Fit failed';
      notify('The server could not be reached, so the alternative was not applied. Previous peaks and result kept.', 'red', true);
      return;
    }
    if (e && e.transportFailure) {
      // Server unreachable: the local optimiser is the honest fallback, and
      // the overlay saying so opens only if it actually converged.
      if (e.message) console.warn('Backend unreachable, falling back to local LM:', e.message);
      const local = runFitLocal(be, bgSubtracted, bgIntensity);
      if (local && local.success && !_snapshotSuppressed) {
        document.getElementById('localfit-warn-overlay').classList.add('open');
      }
      return;
    }
"""'Is this component REQUIRED?' — the refit test (unit step (c), 2026-09-22).

`support` holds the other components at their fitted values, so redundancy
under overlap escapes it (Auto-Fit anchor unit, Codex round 6: a large
Graphite component the other components could absorb if refitted). The refit
without the component is the test for that. It costs one fit, so it runs
only when asked (`require_component`); Auto-Fit asks for its anchor.
"""

import io

import numpy as np
import pytest

import fitting
from app import create_app


@pytest.fixture()
def client(tmp_path):
    app = create_app(upload_folder=str(tmp_path))
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _gl(x, a, c, w, mix=0.3):
    return fitting._SHAPE_FUNCS["pseudo_voigt_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=mix)


def _agl(x, a, c, w):
    return fitting._SHAPE_FUNCS["asymmetric_gl"](x, amplitude=a, center=c, fwhm=w, gl_ratio=0.3, asymmetry=0.25)


X = np.round(np.arange(280.0, 295.0001, 0.02), 4)


def _autofit_model(graphite_amp, others):
    specs = [{"id": "1", "name": "Graphite", "shape": "asymmetric_gl", "center": 284.5, "center_min": 284.2, "center_max": 284.8,
              "amplitude": graphite_amp, "fwhm": 0.7, "gl_ratio": 0.3, "asymmetry": 0.25, "asymmetry_min": 0.1, "asymmetry_max": 0.5,
              "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0}]
    for k, (a, c, w) in enumerate(others, start=2):
        specs.append({"id": str(k), "shape": "pseudo_voigt_gl", "center": c, "amplitude": a, "fwhm": w, "gl_ratio": 0.3,
                      "amplitude_min": 0, "fwhm_min": 0.4, "fwhm_max": 3.0})
    return specs


KW = dict(background_method="manual", manual_bg=[[280.0, 1000.0], [295.0, 1000.0]], n_perturb=3,
          fit_kws={"method": "least_squares"})


@pytest.mark.parametrize("method", ["least_squares", "leastsq"])
def test_a_redundant_anchor_is_supported_but_not_required(method):
    # Codex, Auto-Fit anchor unit round 6 (run B): two symmetric GL lines at
    # 284.8/1.4 eV and 283.3/1.8 eV, no graphite. In that reproduction the
    # full fit kept a LARGE Graphite (amplitude 1,081-1,894, held-others F ~
    # 1e6) because it stopped in a minimum where the anchor carries weight;
    # yet the other two components fit the data to rounding precision
    # without it.
    #
    # The premise is posed deterministically by HOLDING the anchor at 1,500
    # (inside that observed range). Until 2026-09-25 this test instead
    # started the other components at the exact truth, which lets the fit
    # drive the anchor to residue (~0.01) - the premise never formed, the
    # held-others F landed at 11-24 against the threshold of 10, and
    # Trust-Region's documented last-digit jitter (identical seed in every
    # process) moved it across: the test passed 2 of 3 runs on main. Now
    # F ~ 4e7 and the refit without the anchor is ~1e4 x better, under both
    # methods, in every process.
    y = np.round(1000 + _gl(X, 10000, 284.8, 1.4) + _gl(X, 15000, 283.3, 1.8), 2)
    specs = _autofit_model(1500, [(10000, 284.8, 1.4), (15000, 283.3, 1.8)])
    specs[0]["fix_amplitude"] = True
    kw = dict(KW, fit_kws={"method": method})
    res = fitting.run_fit(X, y, specs, require_component="1", **kw)
    assert res["success"] is True
    g = next(ip for ip in res["individual_peaks"] if ip["id"] == "1")
    assert g["support"]["supported"] is True, "held-others statistic passes: that is the gap"
    assert g["support"]["f"] > 1e6, g["support"]["f"]           # far from the threshold, not on it
    req = res["required"]
    assert req["ran"] is True and req["refit_converged"] is True
    assert req["chi2_without_refit"] < 1e-2 * req["chi2_with"]
    assert req["required"] is False


def test_a_real_graphite_anchor_is_required():
    rng = np.random.default_rng(0)
    y = rng.poisson(1000 + _agl(X, 86000, 284.5, 0.7) + _gl(X, 14000, 285.1, 1.9) + _gl(X, 2300, 286.4, 1.4)).astype(float)
    specs = _autofit_model(80000, [(14000, 285.1, 1.9), (2300, 286.4, 1.4)])
    res = fitting.run_fit(X, y, specs, require_component="1", **KW)
    req = res["required"]
265:        be_min = float(roi.get("be_min", float(corrected.min())))
266:        be_max = float(roi.get("be_max", float(corrected.max())))
268:        raise _AnalyzeError("roi.be_min/be_max must be numbers")
269:    mask = (corrected >= be_min) & (corrected <= be_max)
911:          "roi":            {"be_min": ..., "be_max": ...},   // corrected frame
6282:        <input type="number" value="${p.dsGamma.toFixed(4)}" step="0.001" min="0"
6399:async function uploadToBackend(be, inten) {
6400:  const csv = be.map((e, i) => e.toFixed(4) + ',' + inten[i].toFixed(2)).join('\n');
10890:      be[i].toFixed(4), inten[i].toFixed(2), bgIntensity[i].toFixed(2),
11317:  const chiStr = state.fitResult.chiReduced.toFixed(4);
11335:              p.shape, sc.gl, sc.alpha, '', '', rsfVals[i].toFixed(4), '', ''];
11338:      p.name, (_currentSupport(p) && _currentSupport(p).supported) ? 'supported' : '', p.center.toFixed(4), cse !== '' ? Number(cse).toFixed(5) : '',
11339:      p.fwhm.toFixed(4), fse !== '' ? Number(fse).toFixed(5) : '',
11343:      rsfVals[i].toFixed(4), normAreas[i].toFixed(4), atPcts[i].toFixed(2)
5234:  return Object.assign({
5237:    center: 710,
5787:      center: Math.round(beValue * 100) / 100,
5813:      center: Math.round(beValue * 100) / 100,
5818:      center: Math.round((beValue + preset.splitting) * 100) / 100,
5899:  const p1 = addPeak({ name: 'Peak ' + state.nextId + ' (\u2087/\u2082)', center: 380 });
5902:    center: p1.center + 10.9,
6424:    center: p.center,
6428:    fix_center: !!p.fixCenter,
6845:    center: 284.50,
6862:    { name: 'Adventitious 1', center: 284.80, fwhm: 1.4 },
6863:    { name: 'Adventitious 2', center: 286.20, fwhm: 1.6 },
6864:    { name: 'Adventitious 3', center: 287.80, fwhm: 1.8 },
6865:    { name: 'π→π* satellite', center: 291.00, fwhm: 2.5 },
6871:      center: a.center,
6889:      center: c1,
6905:      center: c2,
7937:      _preFit[p.id] = { center: p.center, fwhm: p.fwhm, amplitude: p.amplitude, glMix: p.glMix };
8440:    Object.assign(live, p);
11541:  const nameMap = { center: 'center', fwhm: 'fwhm', fwhm_l: 'fwhm', amplitude: 'amplitude', gl_ratio: 'glMix' };
12451:        ? Object.assign(base, {
12457:        : Object.assign(base, {
13264:      out.push(Object.assign({}, m, {
13351:      .map(m => Object.assign({}, m, { px: scales.x.getPixelForValue(m.be) }))
15006:                   fwhm_excess: 'extra width', center: 'position',
15893:function _fpPeakFromBackend(p, i) {
15894:  const o = { name: p.role || ('found ' + (i + 1)), center: p.center,
3311:      renderEmptyChart();
9186:function _renderStackChart(stackTab) {
9263:function _updateStackChart(stackTab, opts) {
9444:    renderEmptyChart();
9905:function renderEmptyChart() {
11824:renderEmptyChart();

 exited 1 in 57594ms:
TAP version 13
# Subtest: a supported but NOT required anchor is refused before any charge-correction input is touched
ok 1 - a supported but NOT required anchor is refused before any charge-correction input is touched
  ---
  duration_ms: 12.28936
  type: 'test'
  ...
# Subtest: a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block
ok 2 - a required anchor proceeds; a check that did not run (older server, error, non-converged) does not block
  ---
  duration_ms: 15.144721
  type: 'test'
  ...
# Subtest: the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
ok 3 - the request asks for the Graphite anchor by id, and the gate precedes the support gate and every cc write
  ---
  duration_ms: 1.810453
  type: 'test'
  ...
# Subtest: the fixture set covers both outcomes
ok 4 - the fixture set covers both outcomes
  ---
  duration_ms: 5.091863
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
ok 5 - anchors NOTHING — residue: 1e7 flat, 1e-4 bump rounded away, manual background (round 5)
  ---
  duration_ms: 6.49626
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
ok 6 - anchors NOTHING — residue: 10.009999 flat uploaded as 10.01, unrounded manual background (round 3)
  ---
  duration_ms: 4.938818
  type: 'test'
  ...
# Subtest: anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
ok 7 - anchors NOTHING — residue: 10 + 1e-4 bump, linear background (round 2)
  ---
  duration_ms: 3.968688
  type: 'test'
  ...
# Subtest: anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
ok 8 - anchors NOTHING — collapsed model: 30-count bump, manual background over-estimated at 1020 (round 1)
  ---
  duration_ms: 2.542246
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
ok 9 - anchors the correction — resolved 0.0058 line on a zero background, 17 samples survive the upload (round 5)
  ---
  duration_ms: 2.601757
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
ok 10 - anchors the correction — resolved 50-count line on a noise-free 1e6 background (round 4)
  ---
  duration_ms: 1.70735
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
ok 11 - anchors the correction — resolved 10 000-count line on a steep noisy ramp, 100 scans averaged (round 2)
  ---
  duration_ms: 1.742644
  type: 'test'
  ...
# Subtest: anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
ok 12 - anchors the correction — resolved 10 000-count anchor behind a 300 000-count one-channel spike (round 3)
  ---
  duration_ms: 5.04599
  type: 'test'
  ...
# Subtest: anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
ok 13 - anchors the correction — ordinary C 1s: 86 000-count graphite line with Poisson noise
  ---
  duration_ms: 4.283004
  type: 'test'
  ...
# Subtest: an anchor amplitude of 0 is refused before anything is computed
ok 14 - an anchor amplitude of 0 is refused before anything is computed
  ---
  duration_ms: 3.189992
  type: 'test'
  ...
# Subtest: an anchor amplitude of -5 is refused before anything is computed
ok 15 - an anchor amplitude of -5 is refused before anything is computed
  ---
  duration_ms: 1.79462
  type: 'test'
  ...
# Subtest: an anchor amplitude of NaN is refused before anything is computed
ok 16 - an anchor amplitude of NaN is refused before anything is computed
  ---
  duration_ms: 1.539064
  type: 'test'
  ...
# Subtest: an anchor amplitude of Infinity is refused before anything is computed
ok 17 - an anchor amplitude of Infinity is refused before anything is computed
  ---
  duration_ms: 2.024935
  type: 'test'
  ...
# Subtest: a response that lacks the fitted data or the component curve cannot vouch for an anchor
ok 18 - a response that lacks the fitted data or the component curve cannot vouch for an anchor
  ---
  duration_ms: 6.181833
  type: 'test'
  ...
# Subtest: an exact fit that needs the component is supported (chi-square with it is zero)
ok 19 - an exact fit that needs the component is supported (chi-square with it is zero)
  ---
  duration_ms: 2.800419
  type: 'test'
  ...
# Subtest: removing a component that costs nothing is the definition of unsupported
ok 20 - removing a component that costs nothing is the definition of unsupported
  ---
  duration_ms: 1.850237
  type: 'test'
  ...
# Subtest: the support check precedes every write of the charge-correction inputs
ok 21 - the support check precedes every write of the charge-correction inputs
  ---
  duration_ms: 0.827653
  type: 'test'
  ...
# Subtest: the fallback "first peak" anchor is held to the same rule
ok 22 - the fallback "first peak" anchor is held to the same rule
  ---
  duration_ms: 1.679109
  type: 'test'
  ...
# Subtest: rolling back to a Custom reference shows its target field again
ok 23 - rolling back to a Custom reference shows its target field again
  ---
  duration_ms: 1.351869
  type: 'test'
  ...
# Subtest: source ROI overwrites a different target ROI during propagation
ok 24 - source ROI overwrites a different target ROI during propagation
  ---
  duration_ms: 1.529667
  type: 'test'
  ...
# Subtest: blank source ROI leaves the target ROI unchanged (never wipes it)
ok 25 - blank source ROI leaves the target ROI unchanged (never wipes it)
  ---
  duration_ms: 0.344598
  type: 'test'
  ...
# Subtest: a blank source ROI bound (one side) falls back per-field
ok 26 - a blank source ROI bound (one side) falls back per-field
  ---
  duration_ms: 0.266911
  type: 'test'
  ...
# Subtest: background fields still propagate from source (no regression)
ok 27 - background fields still propagate from source (no regression)
  ---
  duration_ms: 0.237061
  type: 'test'
  ...
# Subtest: blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
ok 28 - blank source bgStart/bgEnd fall back to target (unchanged guard semantics)
  ---
  duration_ms: 0.351441
  type: 'test'
  ...
# Subtest: unrelated target UI fields are preserved untouched
ok 29 - unrelated target UI fields are preserved untouched
  ---
  duration_ms: 1.258872
  type: 'test'
  ...
# Subtest: legacy source without endpointAvg propagates 1, not the target default
ok 30 - legacy source without endpointAvg propagates 1, not the target default
  ---
  duration_ms: 1.984098
  type: 'test'
  ...
# Subtest: window at the ROI bounds covers every point, including the last one
ok 31 - window at the ROI bounds covers every point, including the last one
  ---
  duration_ms: 4.931029
  type: 'test'
  ...
# Subtest: off-grid bound inside the ROI never pulls in a point outside it
ok 32 - off-grid bound inside the ROI never pulls in a point outside it
  ---
  duration_ms: 0.380073
  type: 'test'
  ...
# Subtest: bound order does not matter
ok 33 - bound order does not matter
  ---
  duration_ms: 3.267431
  type: 'test'
  ...
# Subtest: ascending grid gives the same point set as descending
ok 34 - ascending grid gives the same point set as descending
  ---
  duration_ms: 0.331795
  type: 'test'
  ...
# Subtest: blank or NaN bound falls back to the full range
ok 35 - blank or NaN bound falls back to the full range
  ---
  duration_ms: 0.34398
  type: 'test'
  ...
# Subtest: fewer than two points in range falls back to the full range
ok 36 - fewer than two points in range falls back to the full range
  ---
  duration_ms: 0.338622
  type: 'test'
  ...
# Subtest: exactly two points in range is a usable window
ok 37 - exactly two points in range is a usable window
  ---
  duration_ms: 0.356858
  type: 'test'
  ...
# Subtest: computeBackgroundCore uses exactly the helper window
ok 38 - computeBackgroundCore uses exactly the helper window
  ---
  duration_ms: 1.441687
  type: 'test'
  ...
# Subtest: no request builder uses the old nearest-index idiom for the bg window
ok 39 - no request builder uses the old nearest-index idiom for the bg window
  ---
  duration_ms: 1.122039
  type: 'test'
  ...
# Subtest: both /api/fit request builders send the inclusive window as end_idx = i1 + 1
ok 40 - both /api/fit request builders send the inclusive window as end_idx = i1 + 1
  ---
  duration_ms: 1.892319
  type: 'test'
  ...
# Subtest: new tabs default to endpoint averaging 3, via one constant
ok 41 - new tabs default to endpoint averaging 3, via one constant
  ---
  duration_ms: 2.891203
  type: 'test'
  ...
# Subtest: legacy fallbacks resolve a saved ui without endpointAvg to 1
ok 42 - legacy fallbacks resolve a saved ui without endpointAvg to 1
  ---
  duration_ms: 1.138591
  type: 'test'
  ...
# Subtest: no bare endpointAvg || '1' fallback survives outside the constant
ok 43 - no bare endpointAvg || '1' fallback survives outside the constant
  ---
  duration_ms: 1.732631
  type: 'test'
  ...
# Subtest: Find Peaks records the averaging its engine used and applies it on apply
ok 44 - Find Peaks records the averaging its engine used and applies it on apply
  ---
  duration_ms: 1.06481
  type: 'test'
  ...
# Subtest: undo/redo carry the averaging recorded by the Find Peaks apply action
ok 45 - undo/redo carry the averaging recorded by the Find Peaks apply action
  ---
  duration_ms: 0.743879
  type: 'test'
  ...
# Subtest: averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
ok 46 - averaging snapshots live on the tab record: undo/redo read the ACTIVE tab only
  ---
  duration_ms: 0.499772
  type: 'test'
  ...
# Subtest: FP_TIER_META defines all three tiers with a color and short label
ok 47 - FP_TIER_META defines all three tiers with a color and short label
  ---
  duration_ms: 1.804527
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: empty query matches everything
ok 48 - _fpRegionMatchesFilter: empty query matches everything
  ---
  duration_ms: 0.431551
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by symbol (case-insensitive, prefix)
ok 49 - _fpRegionMatchesFilter: matches by symbol (case-insensitive, prefix)
  ---
  duration_ms: 0.254897
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by element name substring
ok 50 - _fpRegionMatchesFilter: matches by element name substring
  ---
  duration_ms: 1.810496
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches by level/subshell
ok 51 - _fpRegionMatchesFilter: matches by level/subshell
  ---
  duration_ms: 0.385907
  type: 'test'
  ...
# Subtest: _fpRegionMatchesFilter: matches the full region label
ok 52 - _fpRegionMatchesFilter: matches the full region label
  ---
  duration_ms: 0.20124
  type: 'test'
  ...
# Subtest: _fpRegionOptionLabel: includes the tier tag, region, and element name
ok 53 - _fpRegionOptionLabel: includes the tier tag, region, and element name
  ---
  duration_ms: 0.541479
  type: 'test'
  ...
# Subtest: _fpRegionOptionLabel: structure_only region is tagged distinctly from curated
ok 54 - _fpRegionOptionLabel: structure_only region is tagged distinctly from curated
  ---
  duration_ms: 0.32374
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: no query returns everything, sorted stably by input order
ok 55 - _fpBuildRegionOptions: no query returns everything, sorted stably by input order
  ---
  duration_ms: 1.441084
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: filters by query, each option carries its tier
ok 56 - _fpBuildRegionOptions: filters by query, each option carries its tier
  ---
  duration_ms: 0.647282
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: an unmatched query yields an empty list (never throws)
ok 57 - _fpBuildRegionOptions: an unmatched query yields an empty list (never throws)
  ---
  duration_ms: 0.284911
  type: 'test'
  ...
# Subtest: _fpBuildRegionOptions: tolerates a missing/empty coverage array
ok 58 - _fpBuildRegionOptions: tolerates a missing/empty coverage array
  ---
  duration_ms: 0.15878
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: single curated selection shows its own note
ok 59 - _fpTierNoteFor: single curated selection shows its own note
  ---
  duration_ms: 0.196678
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: single fallback (machine) selection is honestly labeled
ok 60 - _fpTierNoteFor: single fallback (machine) selection is honestly labeled
  ---
  duration_ms: 0.207645
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: structure_only selection says no reference position
ok 61 - _fpTierNoteFor: structure_only selection says no reference position
  ---
  duration_ms: 0.138361
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: no selection is an empty string (never throws)
ok 62 - _fpTierNoteFor: no selection is an empty string (never throws)
  ---
  duration_ms: 0.141486
  type: 'test'
  ...
# Subtest: _fpTierNoteFor: multi-region selection lists each region+tier
ok 63 - _fpTierNoteFor: multi-region selection lists each region+tier
  ---
  duration_ms: 0.180355
  type: 'test'
  ...
# Subtest: runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
ok 64 - runFindPeaks injects the panel value only for methods advertising endpoint_avg, JSON wins
  ---
  duration_ms: 2.40321
  type: 'test'
  ...
# Subtest: _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
ok 65 - _fpMethodChanged does not write endpoint_avg into the Advanced JSON view
  ---
  duration_ms: 0.553331
  type: 'test'
  ...
# Subtest: _fpBestTier: curated wins over machine and structure_only
ok 66 - _fpBestTier: curated wins over machine and structure_only
  ---
  duration_ms: 1.70704
  type: 'test'
  ...
# Subtest: _fpBestTier: machine wins over structure_only when no curated present
ok 67 - _fpBestTier: machine wins over structure_only when no curated present
  ---
  duration_ms: 0.304239
  type: 'test'
  ...
# Subtest: _fpBestTier: empty entries -> null (an element with zero practical coverage)
ok 68 - _fpBestTier: empty entries -> null (an element with zero practical coverage)
  ---
  duration_ms: 0.192893
  type: 'test'
  ...
# Subtest: FP_TIER_RANK: strictly orders curated > machine > structure_only
ok 69 - FP_TIER_RANK: strictly orders curated > machine > structure_only
  ---
  duration_ms: 0.194415
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click on a fresh region replaces an existing single selection
ok 70 - _fpNextSelection: plain click on a fresh region replaces an existing single selection
  ---
  duration_ms: 1.751004
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click replaces a multi-region selection with just the clicked one
ok 71 - _fpNextSelection: plain click replaces a multi-region selection with just the clicked one
  ---
  duration_ms: 1.38515
  type: 'test'
  ...
# Subtest: _fpNextSelection: plain click on the ONLY already-selected region is a no-op (stays selected)
ok 72 - _fpNextSelection: plain click on the ONLY already-selected region is a no-op (stays selected)
  ---
  duration_ms: 0.368992
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click ADDS a second region (ctrl-click co-fit)
ok 73 - _fpNextSelection: additive click ADDS a second region (ctrl-click co-fit)
  ---
  duration_ms: 0.368815
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click on an already-selected region REMOVES it
ok 74 - _fpNextSelection: additive click on an already-selected region REMOVES it
  ---
  duration_ms: 0.569237
  type: 'test'
  ...
# Subtest: _fpNextSelection: additive click on the last remaining region empties the selection
ok 75 - _fpNextSelection: additive click on the last remaining region empties the selection
  ---
  duration_ms: 0.657862
  type: 'test'
  ...
# Subtest: _fpNextSelection: never mutates the `current` Set passed in
ok 76 - _fpNextSelection: never mutates the `current` Set passed in
  ---
  duration_ms: 0.298342
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: translates role:param@max with no raw identifiers
ok 77 - _fpBoundaryHitLabel: translates role:param@max with no raw identifiers
  ---
  duration_ms: 3.449702
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: @min reads as lower limit
ok 78 - _fpBoundaryHitLabel: @min reads as lower limit
  ---
  duration_ms: 0.454231
  type: 'test'
  ...
# Subtest: _fpBoundaryHitLabel: unparseable input degrades honestly, never throws
ok 79 - _fpBoundaryHitLabel: unparseable input degrades honestly, never throws
  ---
  duration_ms: 0.214376
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: detection-family "absorbing a neighbor" variant
ok 80 - _fpWidthFlagLabel: detection-family "absorbing a neighbor" variant
  ---
  duration_ms: 0.549185
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: ordinary-cap "no known-broad justification" variant reads distinctly
ok 81 - _fpWidthFlagLabel: ordinary-cap "no known-broad justification" variant reads distinctly
  ---
  duration_ms: 0.319318
  type: 'test'
  ...
# Subtest: _fpWidthFlagLabel: DS+G and asym-GL variants still extract role + width cleanly
ok 82 - _fpWidthFlagLabel: DS+G and asym-GL variants still extract role + width cleanly
  ---
  duration_ms: 0.238802
  type: 'test'
  ...
# Subtest: _fpPlainMessage: structural_only stub (no cited or sourced data)
ok 83 - _fpPlainMessage: structural_only stub (no cited or sourced data)
  ---
  duration_ms: 0.630012
  type: 'test'
  ...
# Subtest: _fpPlainMessage: an EMPTY structural_only array must NOT trigger the stub (Codex-caught)
ok 84 - _fpPlainMessage: an EMPTY structural_only array must NOT trigger the stub (Codex-caught)
  ---
  duration_ms: 0.269968
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a MIXED request that succeeded must NOT trigger the stub either (Codex-caught, round 2)
ok 85 - _fpPlainMessage: a MIXED request that succeeded must NOT trigger the stub either (Codex-caught, round 2)
  ---
  duration_ms: 0.67899
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a MIXED request that failed for an unrelated reason must NOT trigger the stub
ok 86 - _fpPlainMessage: a MIXED request that failed for an unrelated reason must NOT trigger the stub
  ---
  duration_ms: 0.647619
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no survivors
ok 87 - _fpPlainMessage: no survivors
  ---
  duration_ms: 0.31355
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no survivors + truncated mentions the honest count
ok 88 - _fpPlainMessage: no survivors + truncated mentions the honest count
  ---
  duration_ms: 0.203673
  type: 'test'
  ...
# Subtest: _fpPlainMessage: clean winner with nothing flagged reads as clean
ok 89 - _fpPlainMessage: clean winner with nothing flagged reads as clean
  ---
  duration_ms: 0.165686
  type: 'test'
  ...
# Subtest: _fpPlainMessage: data-driven (region-unassigned) components need review
ok 90 - _fpPlainMessage: data-driven (region-unassigned) components need review
  ---
  duration_ms: 0.184289
  type: 'test'
  ...
# Subtest: _fpPlainMessage: decisive_override reads CONDITIONAL and names the fixed parameter
ok 91 - _fpPlainMessage: decisive_override reads CONDITIONAL and names the fixed parameter
  ---
  duration_ms: 0.419848
  type: 'test'
  ...
# Subtest: _fpPlainMessage: unstable_last_resort reads LOW CONFIDENCE, never hides the caveat
ok 92 - _fpPlainMessage: unstable_last_resort reads LOW CONFIDENCE, never hides the caveat
  ---
  duration_ms: 0.243534
  type: 'test'
  ...
# Subtest: _fpPlainMessage: no_clean_survivor names the boundary hit in plain words
ok 93 - _fpPlainMessage: no_clean_survivor names the boundary hit in plain words
  ---
  duration_ms: 0.232572
  type: 'test'
  ...
# Subtest: _fpPlainMessage: unphysical widths surface as LOW CONFIDENCE with no raw ceiling jargon
ok 94 - _fpPlainMessage: unphysical widths surface as LOW CONFIDENCE with no raw ceiling jargon
  ---
  duration_ms: 0.291432
  type: 'test'
  ...
# Subtest: _fpPlainMessage: filtered dominant alternative is mentioned honestly
ok 95 - _fpPlainMessage: filtered dominant alternative is mentioned honestly
  ---
  duration_ms: 1.389611
  type: 'test'
  ...
# Subtest: _fpPlainMessage: a CONDITIONAL result never reads as a clean pass
ok 96 - _fpPlainMessage: a CONDITIONAL result never reads as a clean pass
  ---
  duration_ms: 0.24521
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: sub-minute seconds
ok 97 - _fpFormatElapsed: sub-minute seconds
  ---
  duration_ms: 1.32976
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: minutes + seconds
ok 98 - _fpFormatElapsed: minutes + seconds
  ---
  duration_ms: 0.296354
  type: 'test'
  ...
# Subtest: _fpFormatElapsed: never negative, tolerates junk input
ok 99 - _fpFormatElapsed: never negative, tolerates junk input
  ---
  duration_ms: 0.213701
  type: 'test'
  ...
# Subtest: _fpProgressText: real candidate-sweep message
ok 100 - _fpProgressText: real candidate-sweep message
  ---
  duration_ms: 0.238456
  type: 'test'
  ...
# Subtest: _fpProgressText: starting phase before any candidate has run
ok 101 - _fpProgressText: starting phase before any candidate has run
  ---
  duration_ms: 0.329131
  type: 'test'
  ...
# Subtest: _fpProgressText: missing/malformed poll degrades to a generic message, never throws
ok 102 - _fpProgressText: missing/malformed poll degrades to a generic message, never throws
  ---
  duration_ms: 0.198013
  type: 'test'
  ...
# Subtest: A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
ok 103 - A08: a 200 response with success:false is a FAILED fit — nothing applied, no local fallback, message shown
  ---
  duration_ms: 17.914427
  type: 'test'
  ...
# Subtest: a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
ok 104 - a server validation error (HTTP 400 with error) surfaces its message and does NOT hand off to the local optimiser
  ---
  duration_ms: 11.213769
  type: 'test'
  ...
# Subtest: a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
ok 105 - a transport failure (fetch throws) still falls back to the local optimiser and shows the local-fit overlay
  ---
  duration_ms: 8.342126
  type: 'test'
  ...
# Subtest: a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
ok 106 - a transport failure whose local fallback does NOT converge shows no "local fit performed" overlay
  ---
  duration_ms: 14.226307
  type: 'test'
  ...
# Subtest: a converged backend result is applied (sanity)
ok 107 - a converged backend result is applied (sanity)
  ---
  duration_ms: 7.904122
  type: 'test'
  ...
# Subtest: the engine/objective labels of a fit result survive spectrum and project save/load
ok 108 - the engine/objective labels of a fit result survive spectrum and project save/load
  ---
  duration_ms: 0.95406
  type: 'test'
  ...
# Subtest: an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
ok 109 - an HTTP 502 with an HTML body on /api/fit is a server failure: message shown, no local fallback
  ---
  duration_ms: 19.49853
  type: 'test'
  ...
# Subtest: an HTTP 502 on the upload is a server failure, not a transport failure
ok 110 - an HTTP 502 on the upload is a server failure, not a transport failure
  ---
  duration_ms: 3.815872
  type: 'test'
  ...
# Subtest: uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
ok 111 - uploadToBackend itself classifies HTTP errors as server errors and rejects a reply without a session id
  ---
  duration_ms: 12.085277
  type: 'test'
  ...
# Subtest: every consumer that prints the goodness-of-fit statistic routes through the statistic identity
ok 112 - every consumer that prints the goodness-of-fit statistic routes through the statistic identity
  ---
  duration_ms: 2.032272
  type: 'test'
  ...
# Subtest: uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
ok 113 - uploadToBackend: an HTTP 200 whose body is JSON null (or not an object) is a server error, not a transport failure
  ---
  duration_ms: 1.250415
  type: 'test'
  ...
# Subtest: a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
ok 114 - a local (unweighted) result is labelled a STARTING POINT, not a reportable result, everywhere it is shown
  ---
  duration_ms: 2.101888
  type: 'test'
  ...
# Subtest: starting-point helpers: keyed on the persisted objective, weighted results untouched
ok 115 - starting-point helpers: keyed on the persisted objective, weighted results untouched
  ---
  duration_ms: 8.017473
  type: 'test'
  ...
# Subtest: Quantify shows the starting-point banner for a local result and not for a weighted one
ok 116 - Quantify shows the starting-point banner for a local result and not for a weighted one
  ---
  duration_ms: 8.398252
  type: 'test'
  ...
# Subtest: every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
ok 117 - every remaining site carries the designation: TSV export, saves, activation, status bar, history, chart labels
  ---
  duration_ms: 3.146474
  type: 'test'
  ...
# Subtest: project save derives the designation from the objective for an older local result lacking the new fields
ok 118 - project save derives the designation from the objective for an older local result lacking the new fields
  ---
  duration_ms: 16.472522
  type: 'test'
  ...
# Subtest: stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
ok 119 - stack envelope/legend, history preview and auto-fit caption carry the designation; CSV and XLSX warnings asserted separately
  ---
  duration_ms: 7.571211
  type: 'test'
  ...
# Subtest: _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
ok 120 - _applyStatDisplay keeps header, tooltip, caption and value consistent through local → weighted → none
  ---
  duration_ms: 6.250653
  type: 'test'
  ...
# Subtest: history preview glow is keyed on the dataset flag, not the label text
ok 121 - history preview glow is keyed on the dataset flag, not the label text
  ---
  duration_ms: 0.913545
  type: 'test'
  ...
# Subtest: spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
ok 122 - spectrum load renders the Results panel after restoring a saved result, and Save Fit carries the designation
  ---
  duration_ms: 0.709376
  type: 'test'
  ...
# Subtest: _applyStatDisplay clears header, tooltip, caption and value together on local → none
ok 123 - _applyStatDisplay clears header, tooltip, caption and value together on local → none
  ---
  duration_ms: 7.104122
  type: 'test'
  ...
# Subtest: _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
ok 124 - _isLocalModel: a model imported from a local .fit.json is a starting point even with no fit result
  ---
  duration_ms: 2.952154
  type: 'test'
  ...
# Subtest: fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
ok 125 - fit.json round trip: fromJSON keeps the provenance, Save Fit and the TSV export use it, saves and loads carry it, new fits clear it
  ---
  duration_ms: 1.724042
  type: 'test'
  ...
# Subtest: undo/redo snapshots carry and restore model provenance
ok 126 - undo/redo snapshots carry and restore model provenance
  ---
  duration_ms: 6.069428
  type: 'test'
  ...
# Subtest: round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
ok 127 - round-12 sites: undo/redo restore provenance, spectrum save/load carry it, import re-renders Results, figure/chart key on the model, Find Peaks clears it
  ---
  duration_ms: 1.442809
  type: 'test'
  ...
# Subtest: _provenanceOf derives a designation from a live local result, and undo snapshots use it
ok 128 - _provenanceOf derives a designation from a live local result, and undo snapshots use it
  ---
  duration_ms: 6.773319
  type: 'test'
  ...
# Subtest: batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
ok 129 - batch propagation copies the source model provenance onto each target (cleared again only by a successful fit)
  ---
  duration_ms: 1.025461
  type: 'test'
  ...
# Subtest: the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
ok 130 - the Peaks sidebar banner shows for a local result or a local-derived model and hides otherwise
  ---
  duration_ms: 6.635639
  type: 'test'
  ...
# Subtest: round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
ok 131 - round-14 sites: banner element and refresh hooks, undo/redo re-render Results, auto-fit snapshot/restore carry provenance
  ---
  duration_ms: 0.843598
  type: 'test'
  ...
# Subtest: the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
ok 132 - the sidebar banner sits outside the switchable tab panels and also shows for an active local history preview
  ---
  duration_ms: 5.673743
  type: 'test'
  ...
# Subtest: the sidebar banner is sticky at the top of the scrolling panel body
ok 133 - the sidebar banner is sticky at the top of the scrolling panel body
  ---
  duration_ms: 0.421879
  type: 'test'
  ...
# Subtest: the sidebar banner shows on a stack tab whose visible entries draw a local source fit
ok 134 - the sidebar banner shows on a stack tab whose visible entries draw a local source fit
  ---
  duration_ms: 4.703666
  type: 'test'
  ...
# Subtest: every stack chart repaint path refreshes the sidebar designation before any early return
ok 135 - every stack chart repaint path refreshes the sidebar designation before any early return
  ---
  duration_ms: 0.530182
  type: 'test'
  ...
# Subtest: closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
ok 136 - closeTab rebuilds the active stack chart when it prunes entries that referenced the closed tab
  ---
  duration_ms: 0.272277
  type: 'test'
  ...
# Subtest: W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
ok 137 - W1 helpers: weighted local results are chi-square but still designated; legacy unweighted keep Residual variance; server untouched
  ---
  duration_ms: 5.038851
  type: 'test'
  ...
# Subtest: TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
ok 138 - TSV export warning is objective-aware: legacy result, legacy imported model, weighted result, server result
  ---
  duration_ms: 11.061451
  type: 'test'
  ...
# Subtest: adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
ok 139 - adoption: the REQUEST starts from the alternative, asks for the starts check by ITS model, and the live model is untouched until success
  ---
  duration_ms: 10.244832
  type: 'test'
  ...
# Subtest: adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
ok 140 - adoption: a transport failure does NOT fall back to the local engine (it would start from the live model)
  ---
  duration_ms: 4.004973
  type: 'test'
  ...
# Subtest: adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
ok 141 - adoption: a tab switch during the re-fit discards it and leaves the originating model as it was
  ---
  duration_ms: 9.605604
  type: 'test'
  ...
# Subtest: adoption: success records the choice, the starts evidence and the key of the model it describes
ok 142 - adoption: success records the choice, the starts evidence and the key of the model it describes
  ---
  duration_ms: 6.887969
  type: 'test'
  ...
# Subtest: an ordinary Run Fit on one unlinked component does not ask for the starts check
ok 143 - an ordinary Run Fit on one unlinked component does not ask for the starts check
  ---
  duration_ms: 5.074396
  type: 'test'
  ...
# Subtest: a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
ok 144 - a model edited WHILE the fit runs does not receive the result (Codex round 2: a newly locked centre kept its edited value under the server's statistics, with a fresh evidence key)
  ---
  duration_ms: 4.059589
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice names it experimental and states the runtime range
ok 145 - FP_STRINGS.experimentalNotice names it experimental and states the runtime range
  ---
  duration_ms: 1.644776
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice says BOTH "starting point" and "not a final answer" -- either alone is not the safety claim
ok 146 - FP_STRINGS.experimentalNotice says BOTH "starting point" and "not a final answer" -- either alone is not the safety claim
  ---
  duration_ms: 0.451547
  type: 'test'
  ...
# Subtest: FP_STRINGS.experimentalNotice does not overclaim correctness and does not describe the app as broken/frozen
ok 147 - FP_STRINGS.experimentalNotice does not overclaim correctness and does not describe the app as broken/frozen
  ---
  duration_ms: 0.373651
  type: 'test'
  ...
# Subtest: the notice banner element and its dismiss button are wired to the actual dismiss function, not just present somewhere in the page
ok 148 - the notice banner element and its dismiss button are wired to the actual dismiss function, not just present somewhere in the page
  ---
  duration_ms: 0.912906
  type: 'test'
  ...
# Subtest: both notice functions read/write the SAME localStorage key -- a mismatched key would show the notice every time despite dismissal
ok 149 - both notice functions read/write the SAME localStorage key -- a mismatched key would show the notice every time despite dismissal
  ---
  duration_ms: 2.571069
  type: 'test'
  ...
# Subtest: the gate function early-returns (hides, does not show) when already dismissed, and only sets text+shows in the un-dismissed path
ok 150 - the gate function early-returns (hides, does not show) when already dismissed, and only sets text+shows in the un-dismissed path
  ---
  duration_ms: 7.93382
  type: 'test'
  ...
# Subtest: openFindPeaksModal calls the notice gate so it actually shows on open
ok 151 - openFindPeaksModal calls the notice gate so it actually shows on open
  ---
  duration_ms: 1.417168
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed has a clear, non-bare label
ok 152 - FP_STRINGS.materials.mixed has a clear, non-bare label
  ---
  duration_ms: 3.799769
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint is advisory, never claims correction
ok 153 - FP_STRINGS.materials.mixed hint is advisory, never claims correction
  ---
  duration_ms: 0.840388
  type: 'test'
  ...
# Subtest: FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
ok 154 - FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
  ---
  duration_ms: 1.992224
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
ok 155 - FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
  ---
  duration_ms: 0.401794
  type: 'test'
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Subtest: (A) frontend vs backend parity: Gaussian
not ok 156 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1614.346212
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
    startSubtestAfterBootstrap (node:internal/test_runner/harness:296:17)
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
not ok 157 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1402.529682
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: GL
not ok 158 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1352.549108
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: Voigt
not ok 159 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1334.446151
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DS
not ok 160 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1320.654365
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
not ok 161 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1337.585045
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)
not ok 162 - (A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization) # TODO unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)
  ---
  duration_ms: 1295.601115
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:171:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:176:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX at m=0 (no convolution)
not ok 163 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1276.87464
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:182:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:188:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
not ok 164 - (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
  ---
  duration_ms: 1264.000036
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:194:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:199:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
not ok 165 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1288.256546
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
not ok 166 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1230.050045
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
not ok 167 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1252.758407
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
not ok 168 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1293.7281
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
not ok 169 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1316.961275
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:235:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:242:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 170 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.380759
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 171 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.223265
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 172 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.168394
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 173 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.159041
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 174 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.217187
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 175 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.249079
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
not ok 176 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA # TODO evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)
  ---
  duration_ms: 3.695247
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA at x=393.3: evalPeak=7298.4050340345175, evalPeakArray[i]=8703.575517573383, rel diff=7.8969%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:272:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 177 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.217212
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7170.363795150584, rel diff=24.2055%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:272:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (C) evalPeak() has no direct callers outside evalPeakArray()
ok 178 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 3.264798
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
not ok 179 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1263.011612
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
not ok 180 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1255.758595
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Voigt
not ok 181 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1273.645763
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: GL
not ok 182 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1316.120997
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
not ok 183 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1336.556348
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DS
not ok 184 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1276.615025
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
not ok 185 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1277.04381
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
not ok 186 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1296.800827
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0)
not ok 187 - (D) sweep across the fitted range: DSG_LA (m > 0)
  ---
  duration_ms: 1267.026807
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP
not ok 188 - (D) sweep across the fitted range: LACX (m > 0) — KNOWN GAP # TODO convolved shapes: LACX kernel discretisation (unit 2 / caM clamp); DSG_LA page quadrature step ignores the Gaussian kernel width (own unit)
  ---
  duration_ms: 1251.012562
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:389:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:390:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
not ok 189 - (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
  ---
  duration_ms: 1280.681588
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
not ok 190 - (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
  ---
  duration_ms: 1320.871023
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
not ok 191 - (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
  ---
  duration_ms: 1290.996193
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
not ok 192 - (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
  ---
  duration_ms: 1280.82104
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
not ok 193 - (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
  ---
  duration_ms: 1282.337205
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
not ok 194 - (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
  ---
  duration_ms: 1293.971543
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
not ok 195 - (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
  ---
  duration_ms: 1277.152906
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
not ok 196 - (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
  ---
  duration_ms: 1273.893447
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 6-point irregular grid
not ok 197 - (D″) DS+G regression: a 6-point irregular grid
  ---
  duration_ms: 1255.417334
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
not ok 198 - (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
  ---
  duration_ms: 1236.936873
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
not ok 199 - (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
  ---
  duration_ms: 1239.676985
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
not ok 200 - (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
  ---
  duration_ms: 1201.944545
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
not ok 201 - (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
  ---
  duration_ms: 1200.414676
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
not ok 202 - (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
  ---
  duration_ms: 1229.059588
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
not ok 203 - (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
  ---
  duration_ms: 1178.583733
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 2-point grid
not ok 204 - (D″) DS+G regression: a 2-point grid
  ---
  duration_ms: 1163.025165
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 1-point grid
not ok 205 - (D″) DS+G regression: a 1-point grid
  ---
  duration_ms: 1171.69248
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
not ok 206 - (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1224.652493
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
not ok 207 - (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1134.330301
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
not ok 208 - (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1137.399555
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
not ok 209 - (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1223.541873
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
not ok 210 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1624.433798
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
not ok 211 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1430.801289
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
not ok 212 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1342.306584
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
not ok 213 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1328.153306
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
not ok 214 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1326.011694
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
not ok 215 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1348.109772
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 216 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
  ---
  duration_ms: 1297.02078
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
not ok 217 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX # TODO LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit
  ---
  duration_ms: 1275.936097
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:122:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:123:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
not ok 218 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1255.090646
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:131:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:138:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
not ok 219 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1291.242495
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:146:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:148:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
not ok 220 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1234.378328
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
not ok 221 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1256.410348
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
not ok 222 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1299.190587
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
not ok 223 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1319.19221
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
not ok 224 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1265.497941
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
not ok 225 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1250.273881
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
not ok 226 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1290.48043
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
not ok 227 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1320.833475
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
not ok 228 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1341.885204
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
not ok 229 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1272.602156
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
not ok 230 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1280.768696
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
not ok 231 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1297.981557
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
not ok 232 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1269.450846
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
not ok 233 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1252.372158
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
not ok 234 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1292.145608
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
not ok 235 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1317.366394
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
not ok 236 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1275.187422
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
not ok 237 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1275.529979
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
not ok 238 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
  ---
  duration_ms: 1291.307306
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
not ok 239 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
  ---
  duration_ms: 1289.685985
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
not ok 240 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
  ---
  duration_ms: 1277.39204
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
not ok 241 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked (request and hold only)
  ---
  duration_ms: 1277.510756
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:199:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:200:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
not ok 242 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1257.250347
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:213:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:109:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:214:33)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
not ok 243 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1237.682476
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:224:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:232:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
not ok 244 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1243.87004
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:242:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/lineshape_roundtrip.test.js:251:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 245 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1884.718236
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 246 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 335.530446
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 247 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 15.066106
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 248 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 10.241728
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 249 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 15.060851
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 250 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 9.795836
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 251 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 10.711304
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 252 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 11.118294
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 253 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 52.772125
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 254 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 28.187994
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 255 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 9.126056
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 256 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 15.738269
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 257 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 14.193539
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 258 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 11.823684
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 259 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 11.540863
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 260 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1847.777805
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 261 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 88.263293
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 262 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 25.947525
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 263 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 13.756295
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 264 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 92.061228
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 265 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1452.062194
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 266 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 28.766314
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 267 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 14.423931
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 268 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 9.524841
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 269 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1728.831816
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: reduced chi-square does not count the held caM as a varied parameter
ok 270 - reduced chi-square does not count the held caM as a varied parameter
  ---
  duration_ms: 20.754351
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 271 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 10.802894
  type: 'test'
  ...
# Subtest: plain, indented, multi-declarator, same-line, multiline, ASI declarations
ok 272 - plain, indented, multi-declarator, same-line, multiline, ASI declarations
  ---
  duration_ms: 12.163371
  type: 'test'
  ...
# Subtest: populated containers, ALL_CAPS containers, parenthesised and conditional initialisers
ok 273 - populated containers, ALL_CAPS containers, parenthesised and conditional initialisers
  ---
  duration_ms: 3.742494
  type: 'test'
  ...
# Subtest: destructuring, labelled, unbraced-if, top-level block and static class fields
ok 274 - destructuring, labelled, unbraced-if, top-level block and static class fields
  ---
  duration_ms: 4.320754
  type: 'test'
  ...
# Subtest: function-local declarations and primitive consts are not module state
ok 275 - function-local declarations and primitive consts are not module state
  ---
  duration_ms: 3.281085
  type: 'test'
  ...
# Subtest: comments, strings, regex and nested template literals cannot hide or fake a declaration
ok 276 - comments, strings, regex and nested template literals cannot hide or fake a declaration
  ---
  duration_ms: 2.316226
  type: 'test'
  ...
# Subtest: appending a forbidden declaration to each real inline script is found
ok 277 - appending a forbidden declaration to each real inline script is found
  ---
  duration_ms: 594.534801
  type: 'test'
  ...
# Subtest: destructuring defaults and rest create containers even when the right-hand side is primitive
ok 278 - destructuring defaults and rest create containers even when the right-hand side is primitive
  ---
  duration_ms: 0.438824
  type: 'test'
  ...
# Subtest: static fields with string or computed keys, class expressions and static blocks are reported
ok 279 - static fields with string or computed keys, class expressions and static blocks are reported
  ---
  duration_ms: 1.061537
  type: 'test'
  ...
# Subtest: a const whose initialiser is a class expression WITH static fields is not skipped
ok 280 - a const whose initialiser is a class expression WITH static fields is not skipped
  ---
  duration_ms: 0.639379
  type: 'test'
  ...
# Subtest: static fields on an anonymous superclass expression are attributed to the subclass
ok 281 - static fields on an anonymous superclass expression are attributed to the subclass
  ---
  duration_ms: 0.73885
  type: 'test'
  ...
# Subtest: a static block is reported as a whole, whatever it does
ok 282 - a static block is reported as a whole, whatever it does
  ---
  duration_ms: 0.413723
  type: 'test'
  ...
# Subtest: an unbound class expression with static state is reported under an un-allowlistable name
ok 283 - an unbound class expression with static state is reported under an un-allowlistable name
  ---
  duration_ms: 0.251329
  type: 'test'
  ...
# Subtest: computed class keys are evaluated in the enclosing scope: a class declared inside one is reported
ok 284 - computed class keys are evaluated in the enclosing scope: a class declared inside one is reported
  ---
  duration_ms: 0.76801
  type: 'test'
  ...
# Subtest: catch-clause bindings at module scope are enumerated
ok 285 - catch-clause bindings at module scope are enumerated
  ---
  duration_ms: 0.313128
  type: 'test'
  ...
# Subtest: a RegExp literal is a mutable object, not an immutable constant
ok 286 - a RegExp literal is a mutable object, not an immutable constant
  ---
  duration_ms: 0.141975
  type: 'test'
  ...
# Subtest: a class without static state reports nothing at all
ok 287 - a class without static state reports nothing at all
  ---
  duration_ms: 0.174742
  type: 'test'
  ...
# Subtest: every module-level mutable is allowlisted with a valid non-C class
ok 288 - every module-level mutable is allowlisted with a valid non-C class
  ---
  duration_ms: 321.808719
  type: 'test'
  ...
# Subtest: inherited property names and anonymous-class names cannot slip through the allowlist
ok 289 - inherited property names and anonymous-class names cannot slip through the allowlist
  ---
  duration_ms: 126.658467
  type: 'test'
  ...
# Subtest: the known class-C holders are gone from module scope
ok 290 - the known class-C holders are gone from module scope
  ---
  duration_ms: 8.445725
  type: 'test'
  ...
# Subtest: async operations capture their owning record before the first await
ok 291 - async operations capture their owning record before the first await
  ---
  duration_ms: 2.763758
  type: 'test'
  ...
# Subtest: undo/redo and Find Peaks apply read the ACTIVE tab record only
ok 292 - undo/redo and Find Peaks apply read the ACTIVE tab record only
  ---
  duration_ms: 0.758569
  type: 'test'
  ...
# Subtest: tolFromSlider clamps to [0.25, 5.0] and snaps to 0.25
ok 293 - tolFromSlider clamps to [0.25, 5.0] and snaps to 0.25
  ---
  duration_ms: 2.215197
  type: 'test'
  ...
# Subtest: coerceTolToEv maps legacy modes onto the base, passes numbers through
ok 294 - coerceTolToEv maps legacy modes onto the base, passes numbers through
  ---
  duration_ms: 0.442686
  type: 'test'
  ...
# Subtest: blendedSearch matches elements by symbol/name
ok 295 - blendedSearch matches elements by symbol/name
  ---
  duration_ms: 0.60549
  type: 'test'
  ...
# Subtest: blendedSearch matches compounds, tagged compound
ok 296 - blendedSearch matches compounds, tagged compound
  ---
  duration_ms: 0.375285
  type: 'test'
  ...
# Subtest: blendedSearch numeric query yields energy rows
ok 297 - blendedSearch numeric query yields energy rows
  ---
  duration_ms: 0.531928
  type: 'test'
  ...
# Subtest: blendedSearch caps results and empty query returns []
ok 298 - blendedSearch caps results and empty query returns []
  ---
  duration_ms: 1.153082
  type: 'test'
  ...
# Subtest: parseChemKey: exact spin-orbit key
ok 299 - parseChemKey: exact spin-orbit key
  ---
  duration_ms: 0.73828
  type: 'test'
  ...
# Subtest: parseChemKey: subshell-only p attaches to BOTH spin-orbit lines (Si 2p)
ok 300 - parseChemKey: subshell-only p attaches to BOTH spin-orbit lines (Si 2p)
  ---
  duration_ms: 0.332187
  type: 'test'
  ...
# Subtest: parseChemKey: 1s has no split
ok 301 - parseChemKey: 1s has no split
  ---
  duration_ms: 1.804522
  type: 'test'
  ...
# Subtest: compoundCandidatesFrom returns legacy candidates within tol, honest proximity
ok 302 - compoundCandidatesFrom returns legacy candidates within tol, honest proximity
  ---
  duration_ms: 0.886578
  type: 'test'
  ...
# Subtest: capConfidenceByTier: curated/machine keep candidate label + raw energyMatch
ok 303 - capConfidenceByTier: curated/machine keep candidate label + raw energyMatch
  ---
  duration_ms: 0.355159
  type: 'test'
  ...
# Subtest: capConfidenceByTier: legacy noun is "Legacy hint", energy annotated, never Strong
ok 304 - capConfidenceByTier: legacy noun is "Legacy hint", energy annotated, never Strong
  ---
  duration_ms: 0.180654
  type: 'test'
  ...
# Subtest: mergeAndRankCandidates: element-only golden order is Δ-primary
ok 305 - mergeAndRankCandidates: element-only golden order is Δ-primary
  ---
  duration_ms: 0.302278
  type: 'test'
  ...
# Subtest: adding compounds does not perturb the element subsequence
ok 306 - adding compounds does not perturb the element subsequence
  ---
  duration_ms: 0.208601
  type: 'test'
  ...
# Subtest: mergeAndRankCandidates: a clear Δ winner ranks first regardless of tier
ok 307 - mergeAndRankCandidates: a clear Δ winner ranks first regardless of tier
  ---
  duration_ms: 0.162313
  type: 'test'
  ...
# Subtest: augerApparentBE shifts with source; photoelectronBE is source-invariant
ok 308 - augerApparentBE shifts with source; photoelectronBE is source-invariant
  ---
  duration_ms: 0.233884
  type: 'test'
  ...
# Subtest: compound BE equals input be_ev (no ccShift, source-invariant)
ok 309 - compound BE equals input be_ev (no ccShift, source-invariant)
  ---
  duration_ms: 0.31955
  type: 'test'
  ...
# Subtest: elementOverlayVisible no longer depends on the palette being open
ok 310 - elementOverlayVisible no longer depends on the palette being open
  ---
  duration_ms: 0.215283
  type: 'test'
  ...
# Subtest: tierColor is a single source of truth for the three data tiers
ok 311 - tierColor is a single source of truth for the three data tiers
  ---
  duration_ms: 0.153011
  type: 'test'
  ...
# Subtest: tierColor falls back safely for unknown/missing tiers
ok 312 - tierColor falls back safely for unknown/missing tiers
  ---
  duration_ms: 0.142405
  type: 'test'
  ...
# Subtest: tierNote is the single source for tier wording; reviewed text is canonical
ok 313 - tierNote is the single source for tier wording; reviewed text is canonical
  ---
  duration_ms: 0.16829
  type: 'test'
  ...
# Subtest: nextColorIdx returns the first index whose palette residue is unused
ok 314 - nextColorIdx returns the first index whose palette residue is unused
  ---
  duration_ms: 0.247801
  type: 'test'
  ...
# Subtest: nextColorIdx falls back to max(used)+1 once every residue is taken
ok 315 - nextColorIdx falls back to max(used)+1 once every residue is taken
  ---
  duration_ms: 0.137265
  type: 'test'
  ...
# Subtest: nextColorIdx: a new pick shares no rendered residue with existing overlays (while residues remain)
ok 316 - nextColorIdx: a new pick shares no rendered residue with existing overlays (while residues remain)
  ---
  duration_ms: 0.165912
  type: 'test'
  ...
# Subtest: nextColorIdx ignores invalid entries (non-integer/negative) when computing the used set
ok 317 - nextColorIdx ignores invalid entries (non-integer/negative) when computing the used set
  ---
  duration_ms: 0.137311
  type: 'test'
  ...
# Subtest: clampToViewport: an in-bounds position passes through unchanged
ok 318 - clampToViewport: an in-bounds position passes through unchanged
  ---
  duration_ms: 0.222169
  type: 'test'
  ...
# Subtest: clampToViewport: negative / above-left position clamps to the margin
ok 319 - clampToViewport: negative / above-left position clamps to the margin
  ---
  duration_ms: 0.146282
  type: 'test'
  ...
# Subtest: clampToViewport: far off-screen (stale) position clamps inside the viewport
ok 320 - clampToViewport: far off-screen (stale) position clamps inside the viewport
  ---
  duration_ms: 0.135756
  type: 'test'
  ...
# Subtest: clampToViewport: non-finite (corrupt saved) coords fall back to the margin
ok 321 - clampToViewport: non-finite (corrupt saved) coords fall back to the margin
  ---
  duration_ms: 0.138109
  type: 'test'
  ...
# Subtest: overlays and compound markers have independent (decoupled) version constants
ok 322 - overlays and compound markers have independent (decoupled) version constants
  ---
  duration_ms: 0.120446
  type: 'test'
  ...
# Subtest: serializeRefOverlays is total: null for empty/nullish/malformed sel
ok 323 - serializeRefOverlays is total: null for empty/nullish/malformed sel
  ---
  duration_ms: 0.237764
  type: 'test'
  ...
# Subtest: serializeRefOverlays captures selection and never emits identify keys
ok 324 - serializeRefOverlays captures selection and never emits identify keys
  ---
  duration_ms: 0.217136
  type: 'test'
  ...
# Subtest: round-trip preserves a valid colorIdx verbatim
ok 325 - round-trip preserves a valid colorIdx verbatim
  ---
  duration_ms: 0.302609
  type: 'test'
  ...
# Subtest: deserialize: absent or envelope-malformed → clean empty (no throw)
ok 326 - deserialize: absent or envelope-malformed → clean empty (no throw)
  ---
  duration_ms: 0.249421
  type: 'test'
  ...
# Subtest: deserialize: newer internal version is ignored (no misread of a future shape)
ok 327 - deserialize: newer internal version is ignored (no misread of a future shape)
  ---
  duration_ms: 0.259516
  type: 'test'
  ...
# Subtest: deserialize entry repair: keep valid, skip no-sym, repair invalid colorIdx, keep unknown tier
ok 328 - deserialize entry repair: keep valid, skip no-sym, repair invalid colorIdx, keep unknown tier
  ---
  duration_ms: 0.27919
  type: 'test'
  ...
# Subtest: post-load next pick renders a color distinct from all restored while residues remain
ok 329 - post-load next pick renders a color distinct from all restored while residues remain
  ---
  duration_ms: 0.21033
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers is total: null for empty/nullish/non-array
ok 330 - serializeRefCompoundMarkers is total: null for empty/nullish/non-array
  ---
  duration_ms: 0.199947
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers is total for malformed ARRAY ENTRIES (no throw; all-invalid → null)
ok 331 - serializeRefCompoundMarkers is total for malformed ARRAY ENTRIES (no throw; all-invalid → null)
  ---
  duration_ms: 0.229096
  type: 'test'
  ...
# Subtest: serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept
ok 332 - serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept
  ---
  duration_ms: 0.327566
  type: 'test'
  ...
# Subtest: compound markers round-trip at global scope; absent/malformed/newer → empty
ok 333 - compound markers round-trip at global scope; absent/malformed/newer → empty
  ---
  duration_ms: 0.413972
  type: 'test'
  ...
# Subtest: compound markers: non-finite be dropped, absent sym tolerated (partial-invalid)
ok 334 - compound markers: non-finite be dropped, absent sym tolerated (partial-invalid)
  ---
  duration_ms: 0.238229
  type: 'test'
  ...
# Subtest: an ROI inside the data: no hint
ok 335 - an ROI inside the data: no hint
  ---
  duration_ms: 9.242623
  type: 'test'
  ...
# Subtest: an ROI past the data by more than one step: the quiet hint names the window actually used
ok 336 - an ROI past the data by more than one step: the quiet hint names the window actually used
  ---
  duration_ms: 5.1806
  type: 'test'
  ...
# Subtest: one side past the data is enough; the window named is the selected data
ok 337 - one side past the data is enough; the window named is the selected data
  ---
  duration_ms: 5.259329
  type: 'test'
  ...
# Subtest: a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
ok 338 - a sub-step overshoot (a toFixed(1) rounding of the data edge) is not "past the data"
  ---
  duration_ms: 9.90157
  type: 'test'
  ...
# Subtest: min above max: amber, no data selected (getROIData selects nothing)
ok 339 - min above max: amber, no data selected (getROIData selects nothing)
  ---
  duration_ms: 7.157063
  type: 'test'
  ...
# Subtest: an ROI that misses the data entirely: amber, names the data range
ok 340 - an ROI that misses the data entirely: amber, names the data range
  ---
  duration_ms: 5.367776
  type: 'test'
  ...
# Subtest: empty fields mean the full range (as getROIData): no hint
ok 341 - empty fields mean the full range (as getROIData): no hint
  ---
  duration_ms: 8.864246
  type: 'test'
  ...
# Subtest: the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
ok 342 - the window is in the CORRECTED frame (raw − ccShift), as the fit and Find Peaks use it
  ---
  duration_ms: 6.408013
  type: 'test'
  ...
# Subtest: a descending acquisition behaves the same
ok 343 - a descending acquisition behaves the same
  ---
  duration_ms: 6.207072
  type: 'test'
  ...
# Subtest: centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
ok 344 - centre outside the SELECTED data is flagged; inside, at the edges, or with no data selected is not
  ---
  duration_ms: 7.149349
  type: 'test'
  ...
# Subtest: the helpers write nothing: no assignment to a field value, a peak or the fit state
ok 345 - the helpers write nothing: no assignment to a field value, a peak or the fit state
  ---
  duration_ms: 5.931686
  type: 'test'
  ...
# Subtest: the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
ok 346 - the fit and Find Peaks still read the ROI exactly as before (getROIData / the two field values)
  ---
  duration_ms: 2.492389
  type: 'test'
  ...
# Subtest: an unsupported component: the badge warns without reporting its suppressed centre
ok 347 - an unsupported component: the badge warns without reporting its suppressed centre
  ---
  duration_ms: 3.526947
  type: 'test'
  ...
# Subtest: manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
ok 348 - manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge
  ---
  duration_ms: 18.247776
  type: 'test'
  ...
# Subtest: …and can differ by one edge point when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
ok 349 - …and can differ by one edge point when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)
  ---
  duration_ms: 12.441877
  type: 'test'
  ...
# Subtest: summary wording: counts of STARTS and of SOLUTIONS, never certification
ok 350 - summary wording: counts of STARTS and of SOLUTIONS, never certification
  ---
  duration_ms: 29.369635
  type: 'test'
  ...
# Subtest: no alternative: one line, no table
ok 351 - no alternative: one line, no table
  ---
  duration_ms: 35.731607
  type: 'test'
  ...
# Subtest: alternatives: "Your fit" first, own areas per component, the moved component named and coloured
ok 352 - alternatives: "Your fit" first, own areas per component, the moved component named and coloured
  ---
  duration_ms: 16.625249
  type: 'test'
  ...
# Subtest: RED band: applying asks first and NAMES the component and the distance
ok 353 - RED band: applying asks first and NAMES the component and the distance
  ---
  duration_ms: 20.089749
  type: 'test'
  ...
# Subtest: adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
ok 354 - adoption never writes the live model itself: the alternative is only the START of a fit, and the choice rides along
  ---
  duration_ms: 16.399784
  type: 'test'
  ...
# Subtest: below the red band there is no dialog
ok 355 - below the red band there is no dialog
  ---
  duration_ms: 44.767918
  type: 'test'
  ...
# Subtest: a locked parameter is never moved by an alternative
ok 356 - a locked parameter is never moved by an alternative
  ---
  duration_ms: 15.097027
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
ok 357 - evidence is bound to the fitted model — a peak deleted: the panel says so and nothing can be applied
  ---
  duration_ms: 12.421777
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
ok 358 - evidence is bound to the fitted model — a shape changed (GL -> DS) and the centre moved: the panel says so and nothing can be applied
  ---
  duration_ms: 10.924904
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
ok 359 - evidence is bound to the fitted model — a lock toggled: the panel says so and nothing can be applied
  ---
  duration_ms: 15.375966
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
ok 360 - evidence is bound to the fitted model — a link added: the panel says so and nothing can be applied
  ---
  duration_ms: 10.215364
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
ok 361 - evidence is bound to the fitted model — an undo that restored other values: the panel says so and nothing can be applied
  ---
  duration_ms: 11.273441
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
ok 362 - evidence is bound to the fitted model — an auto-fit asymmetry bound changed: the panel says so and nothing can be applied
  ---
  duration_ms: 8.69904
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
ok 363 - evidence is bound to the fitted model — the background type changed: the panel says so and nothing can be applied
  ---
  duration_ms: 12.036906
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
ok 364 - evidence is bound to the fitted model — the background window moved: the panel says so and nothing can be applied
  ---
  duration_ms: 14.31057
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
ok 365 - evidence is bound to the fitted model — endpoint averaging changed: the panel says so and nothing can be applied
  ---
  duration_ms: 10.079934
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
ok 366 - evidence is bound to the fitted model — the ROI changed: the panel says so and nothing can be applied
  ---
  duration_ms: 9.03089
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
ok 367 - evidence is bound to the fitted model — a manual anchor was added: the panel says so and nothing can be applied
  ---
  duration_ms: 10.507656
  type: 'test'
  ...
# Subtest: evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
ok 368 - evidence is bound to the fitted model — the charge correction changed: the panel says so and nothing can be applied
  ---
  duration_ms: 14.143083
  type: 'test'
  ...
# Subtest: a cosmetic edit (name, colour, visibility) does not invalidate the evidence
ok 369 - a cosmetic edit (name, colour, visibility) does not invalidate the evidence
  ---
  duration_ms: 15.844805
  type: 'test'
  ...
# Subtest: preview overlays a COPY and toggles off; the model is untouched
ok 370 - preview overlays a COPY and toggles off; the model is untouched
  ---
  duration_ms: 13.560426
  type: 'test'
  ...
# Subtest: a record is keyed like the live tab (project save of a non-active tab)
ok 371 - a record is keyed like the live tab (project save of a non-active tab)
  ---
  duration_ms: 14.812219
  type: 'test'
  ...
# Subtest: what is saved: the counts, never the alternatives' parameter sets
ok 372 - what is saved: the counts, never the alternatives' parameter sets
  ---
  duration_ms: 13.084377
  type: 'test'
  ...
# Subtest: a loaded summary (no parameter sets) still renders its line and offers nothing to apply
ok 373 - a loaded summary (no parameter sets) still renders its line and offers nothing to apply
  ---
  duration_ms: 11.259947
  type: 'test'
  ...
# Subtest: wiring: the trigger is decided with the other request inputs, BEFORE the first await
ok 374 - wiring: the trigger is decided with the other request inputs, BEFORE the first await
  ---
  duration_ms: 12.714055
  type: 'test'
  ...
# Subtest: persistence and export sites carry the summary
ok 375 - persistence and export sites carry the summary
  ---
  duration_ms: 3.110967
  type: 'test'
  ...
# Subtest: the tooltip reports what the starts found and claims nothing about the data
ok 376 - the tooltip reports what the starts found and claims nothing about the data
  ---
  duration_ms: 0.662279
  type: 'test'
  ...
# Subtest: the recorded adoption is worded once, for the exports
ok 377 - the recorded adoption is worded once, for the exports
  ---
  duration_ms: 9.304301
  type: 'test'
  ...
# Subtest: round-trip A -> B -> A restores every ACTIVE parameter (all shapes)
ok 378 - round-trip A -> B -> A restores every ACTIVE parameter (all shapes)
  ---
  duration_ms: 5.485327
  type: 'test'
  ...
# Subtest: DS+G -> GL -> DS+G leaves laAlpha/laBeta/laM and the curve unchanged
ok 379 - DS+G -> GL -> DS+G leaves laAlpha/laBeta/laM and the curve unchanged
  ---
  duration_ms: 21.249414
  type: 'test'
  ...
# Subtest: switching carries the effective eV width, both directions of laM<->fwhm
ok 380 - switching carries the effective eV width, both directions of laM<->fwhm
  ---
  duration_ms: 0.320896
  type: 'test'
  ...
# Subtest: a genuinely-new param is defaulted; a carried-over one is preserved
ok 381 - a genuinely-new param is defaulted; a carried-over one is preserved
  ---
  duration_ms: 0.214454
  type: 'test'
  ...
# Subtest: export columns read the ACTIVE shape, never a stale accumulated param
ok 382 - export columns read the ACTIVE shape, never a stale accumulated param
  ---
  duration_ms: 0.384992
  type: 'test'
  ...
# Subtest: multi-hop round-trip DS+G -> LACX -> GL -> DS+G restores active params
ok 383 - multi-hop round-trip DS+G -> LACX -> GL -> DS+G restores active params
  ---
  duration_ms: 4.915966
  type: 'test'
  ...
# Subtest: loss-kernel response peaks ~23.4 eV above a delta-like peak
ok 384 - loss-kernel response peaks ~23.4 eV above a delta-like peak
  ---
  duration_ms: 29.332943
  type: 'test'
  ...
# Subtest: ascending and descending BE input give the identical background
ok 385 - ascending and descending BE input give the identical background
  ---
  duration_ms: 1.359189
  type: 'test'
  ...
# Subtest: background meets the data at BOTH edges (high-BE anchor, low-BE C0)
ok 386 - background meets the data at BOTH edges (high-BE anchor, low-BE C0)
  ---
  duration_ms: 0.748222
  type: 'test'
  ...
# Subtest: flat window yields no phantom signal (F1 regression pin)
ok 387 - flat window yields no phantom signal (F1 regression pin)
  ---
  duration_ms: 6.999144
  type: 'test'
  ...
# Subtest: agrees with the backend implementation (fitting.py) on the same spectrum
ok 388 - agrees with the backend implementation (fitting.py) on the same spectrum
  ---
  duration_ms: 3.891584
  type: 'test'
  ...
# Subtest: computeBackgroundCore applies endpoint averaging for tougaard (both branches)
ok 389 - computeBackgroundCore applies endpoint averaging for tougaard (both branches)
  ---
  duration_ms: 1.507164
  type: 'test'
  ...
# Subtest: the twin reproduces the server verdict on real responses, and defers to the server field when present
ok 390 - the twin reproduces the server verdict on real responses, and defers to the server field when present
  ---
  duration_ms: 18.56766
  type: 'test'
  ...
# Subtest: _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
ok 391 - _applySupport writes every peak, follows ancestry to the root, stamps the fit key, and leaves null where the response says nothing
  ---
  duration_ms: 8.993069
  type: 'test'
  ...
# Subtest: the verdict applies only to the model and context it was computed for
ok 392 - the verdict applies only to the model and context it was computed for
  ---
  duration_ms: 8.932391
  type: 'test'
  ...
# Subtest: the local engine computes the same statistic from its own residuals
ok 393 - the local engine computes the same statistic from its own residuals
  ---
  duration_ms: 10.784435
  type: 'test'
  ...
# Subtest: sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
ok 394 - sidebar card: badge; centre and width shown as a dash; area % excluded and the others renormalised
  ---
  duration_ms: 17.895296
  type: 'test'
  ...
# Subtest: results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
ok 395 - results table: greyed row, no centre / width / sigma, area kept, percentage dash, and the note beneath
  ---
  duration_ms: 23.67054
  type: 'test'
  ...
# Subtest: uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
ok 396 - uncertainty panel: one rule-0 warning for the component, no per-parameter alarms and no "locked" note for it
  ---
  duration_ms: 20.044277
  type: 'test'
  ...
# Subtest: Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
ok 397 - Quantify: excluded from the body, listed beneath with the reason; total and percentages over the rest
  ---
  duration_ms: 12.995858
  type: 'test'
  ...
# Subtest: CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
ok 398 - CSV / XLSX export: Status column, suppressed cells, At% empty, WARNING line
  ---
  duration_ms: 12.286797
  type: 'test'
  ...
# Subtest: publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
ok 399 - publication figure: no label at the (zero) component, legend entry says so; chart and stack labels say so
  ---
  duration_ms: 4.575637
  type: 'test'
  ...
# Subtest: write-back: a server result sets support; the local engine and a propagated model reset it
ok 400 - write-back: a server result sets support; the local engine and a propagated model reset it
  ---
  duration_ms: 2.929449
  type: 'test'
  ...
# Subtest: persistence: support travels with the peak object through every save (the peak is spread whole)
ok 401 - persistence: support travels with the peak object through every save (the peak is spread whole)
  ---
  duration_ms: 1.903932
  type: 'test'
  ...
# Subtest: CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
ok 402 - CSV / XLSX: an unsupported DS+G component exports no width of any kind (beta, m)
  ---
  duration_ms: 9.763271
  type: 'test'
  ...
# Subtest: the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
ok 403 - the scattered-starts table: an unsupported component shows neither area % nor a move in "Your fit", and is not the largest move
  ---
  duration_ms: 11.296011
  type: 'test'
  ...
# Subtest: exports: a stale or keyless verdict is "not established", never "supported"
ok 404 - exports: a stale or keyless verdict is "not established", never "supported"
  ---
  duration_ms: 14.435007
  type: 'test'
  ...
# Subtest: Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
ok 405 - Auto-Fit finalisation (locks, charge shift) keeps its own verdicts: _restampSupport, called after the locks
  ---
  duration_ms: 7.055878
  type: 'test'
  ...
# Subtest: a .fit.json import onto this tab's data carries no verdict
ok 406 - a .fit.json import onto this tab's data carries no verdict
  ---
  duration_ms: 0.14107
  type: 'test'
  ...
# Subtest: _isUnsupported is never handed an array index as its key (Array.filter passes one)
ok 407 - _isUnsupported is never handed an array index as its key (Array.filter passes one)
  ---
  duration_ms: 3.438577
  type: 'test'
  ...
# Subtest: a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
ok 408 - a key change re-renders every consumer of the verdict — each compared with ITS OWN rendering
  ---
  duration_ms: 4.682998
  type: 'test'
  ...
# Subtest: stack tabs judge a source component against the SOURCE record's key
ok 409 - stack tabs judge a source component against the SOURCE record's key
  ---
  duration_ms: 7.355926
  type: 'test'
  ...
# Subtest: "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
ok 410 - "Your fit" percentages are over supported components; an empty Quantify shows no 100 %
  ---
  duration_ms: 19.317103
  type: 'test'
  ...
# Subtest: the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
ok 411 - the sidebar is patched in place (header, summary, badge) — the centre input's inline continuation respects the verdict
  ---
  duration_ms: 5.933317
  type: 'test'
  ...
1..411
# tests 411
# suites 0
# pass 328
# fail 78
# cancelled 0
# skipped 0
# todo 5
# duration_ms 57553.522799

exec
/bin/zsh -lc "sed -n '4690,4748p' templates/index.html
sed -n '9186,9225p' templates/index.html
sed -n '9263,9305p' templates/index.html
sed -n '11495,11585p' templates/index.html
sed -n '55,77p' docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md
rg -n 'p\\[.*\\]\\s*=|peak\\[.*\\]\\s*=|\\.center\\s*[-+*/]?=|setAttribute\\(.value|valueAsNumber\\s*=' templates/index.html static/js
rg -n 'function addPeak|function handleChartClick|function applyPreset|function _applyRightPanelMode' templates/index.html" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
function computeBackgroundCore(be, intensity, settings) {
  const type = settings.bgType;
  const iter = parseInt(settings.shirleyIter) || 5;
  const nAvg = parseInt(settings.endpointAvg) || 1;

  // Manual anchor background uses its own anchor points, not bg-start/end
  if (type === 'manual') return manualAnchorBackground(be, intensity);

  // The background window — the one definition shared with both /api/fit
  // request builders (see _bgWindowIndices). A blank bound or a window with
  // fewer than two points falls back to the full range inside the helper;
  // slicing the full range below is then a no-op.
  const { i0, i1 } = _bgWindowIndices(be, settings.bgStart, settings.bgEnd);

  // Slice data to background region
  const beSub = be.slice(i0, i1 + 1);
  const inSub = intensity.slice(i0, i1 + 1);

  // Compute background on the sliced region — apply endpoint averaging for Shirley types
  let bgSub;
  if (type === 'shirley') bgSub = shirleyBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart') bgSub = smartBackground(beSub, _applyEndpointAveraging(inSub, nAvg), iter);
  else if (type === 'smart_exp') bgSub = smartExperimentalBackground(beSub, inSub, iter, nAvg);
  else if (type === 'shirley_linear') bgSub = shirleyLinearBackground(beSub, inSub, iter, nAvg);
  else if (type === 'linear') bgSub = linearBackground(beSub, inSub);
  // Averaged for the same reason as Shirley types: the Tougaard amplitude
  // is anchored at the high-BE edge, so endpoint noise feeds the anchor
  // directly. Mirrors fitting.py's run_fit / compute_background_only.
  else if (type === 'tougaard') bgSub = tougaardBackground(beSub, _applyEndpointAveraging(inSub, nAvg));
  else return new Array(be.length).fill(0);

  // Extend background across full data range:
  // - Points before bg region: hold first bg value (flat)
  // - Points inside bg region: use computed bg
  // - Points after bg region: hold last bg value (flat)
  const full = new Array(be.length).fill(0);
  const bgLeft  = bgSub[0];
  const bgRight = bgSub[bgSub.length - 1];

  for (let i = 0; i < be.length; i++) {
    if (i < i0) full[i] = bgLeft;
    else if (i <= i1) full[i] = bgSub[i - i0];
    else full[i] = bgRight;
  }

  return full;
}

// Thin DOM-reading wrapper used by single-tab updatePlot. Stack render
// path calls computeBackgroundCore directly with source-tab settings.
function computeBackground(be, intensity) {
  return computeBackgroundCore(be, intensity, {
    bgType:      document.getElementById('bg-type').value,
    shirleyIter: document.getElementById('shirley-iter').value,
    endpointAvg: document.getElementById('bg-endpoint-avg').value,
    bgStart:     document.getElementById('bg-start').value,
    bgEnd:       document.getElementById('bg-end').value,
  });
}
function _renderStackChart(stackTab) {
  _updateLocalModelBanner();   // visibility / fit toggles repaint here; the designation must follow (unit A0)
  // Invalidate render-data caches. This is the only path that picks up
  // source-tab changes (peaks/fits/ccShift edited while user was on the
  // source tab), so it's also the right invalidation point.
  for (const e of stackTab.entries) e._renderDataCache = null;
  if (state.chart) { state.chart.destroy(); state.chart = null; }
  const canvas = document.getElementById('mainChart');
  const emptyEl = document.getElementById('stack-empty-state');
  const visible = _countVisibleStackEntries(stackTab);
  if (visible === 0) {
    if (canvas) canvas.style.display = 'none';
    if (emptyEl) emptyEl.style.display = 'flex';
    return;
  }
  if (canvas) canvas.style.display = '';
  if (emptyEl) emptyEl.style.display = 'none';
  const datasets = _buildStackDatasets(stackTab);
  const invert = document.getElementById('invert-be')?.checked ?? true;
  const offsetActive = (stackTab.verticalOffset || 0) > 0;
  const ctx = canvas.getContext('2d');
  state.chart = new Chart(ctx, {
    type: 'line',
    data: { datasets },
    options: {
      responsive: true, maintainAspectRatio: false, animation: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { type: 'linear', reverse: invert, title: { display: true, text: 'Binding Energy (eV)' } },
        y: {
          type: 'linear',
          ticks: { display: !offsetActive },
          title: {
            display: true,
            text: offsetActive ? 'Intensity (offset stacked)' : 'Intensity (counts/s)',
          }
        }
      },
      plugins: {
        legend: { display: false },
function _updateStackChart(stackTab, opts) {
  _updateLocalModelBanner();   // visibility / fit toggles repaint here; the designation must follow (unit A0)
  opts = opts || {};
  // Chart-type discriminator: the in-place path mutates datasets by
  // _stackKey, which is only valid when state.chart was built for THIS
  // stack tab. After loading a project, switching from a spectrum tab,
  // or switching between stacks, state.chart may be the wrong chart;
  // in-place lookups would miss silently and pill toggles would no-op.
  // Force a rebuild whenever the chart isn't tagged for this stack tab.
  const chartIsThisStack =
    state.chart &&
    state.chart._xpsStackTabId === stackTab.id &&
    state.chart.data.datasets.some(d => d._stackKey);
  if (opts.invalidate === 'datasets' || !chartIsThisStack) {
    _renderStackChart(stackTab);
    return;
  }
  const canvas = document.getElementById('mainChart');
  const emptyEl = document.getElementById('stack-empty-state');
  const visible = _countVisibleStackEntries(stackTab);
  if (visible === 0) {
    // No visible entries — show empty-state DOM but keep chart instance
    // alive so zoom etc. is preserved when user re-enables an entry.
    if (canvas) canvas.style.display = 'none';
    if (emptyEl) emptyEl.style.display = 'flex';
    return;
  }
  if (canvas) canvas.style.display = '';
  if (emptyEl) emptyEl.style.display = 'none';
  // Build key→index map once (O(N)) so per-entry lookups are O(1).
  // Chart.js v4 caches dataset.hidden into meta at construction; live
  // toggles mutate getDatasetMeta(i).hidden directly. The single
  // chart.update('none') at the end applies all changes in one pass.
  const dsByKey = new Map();
  state.chart.data.datasets.forEach((ds, i) => {
    if (ds._stackKey) dsByKey.set(ds._stackKey, i);
  });

  const lineWidth = stackTab.lineWidth ?? 1.5;
  const O = stackTab.verticalOffset || 0;
  const pills = _readStackPillState();
  let visIdx = 0;
  for (const e of stackTab.entries) {
  let timer = null;
  document.addEventListener('mouseenter', function (e) {
    const el = e.target instanceof Element ? e.target.closest('[data-xps-tip]') : null;
    if (!el) return;
    clearTimeout(timer);
    timer = setTimeout(() => {
      const tip = document.getElementById('xps-tooltip');
      if (!tip) return;
      tip.textContent = '';
      const lines = el.dataset.xpsTip.split('\n');
      lines.forEach((line, i) => {
        if (i > 0) tip.appendChild(document.createElement('br'));
        tip.appendChild(document.createTextNode(line));
      });
      tip.classList.remove('tip-above', 'visible');
      const rect = el.getBoundingClientRect();
      const tipH = 160;
      const spaceBelow = window.innerHeight - rect.bottom;
      if (spaceBelow < tipH && rect.top > tipH) {
        tip.classList.add('tip-above');
        tip.style.top = (rect.top - tipH - 6) + 'px';
      } else {
        tip.style.top = (rect.bottom + 6) + 'px';
      }
      tip.style.left = Math.max(8, Math.min(rect.left, window.innerWidth - 320)) + 'px';
      tip.classList.add('visible');
    }, DELAY);
  }, true);
  document.addEventListener('mouseleave', function (e) {
    if (!(e.target instanceof Element) || !e.target.closest('[data-xps-tip]')) return;
    clearTimeout(timer);
    const tip = document.getElementById('xps-tooltip');
    if (tip) tip.classList.remove('visible');
  }, true);
})();

// ═══════════════════════════════════════════════════
// UNCERTAINTY VALIDATION
// ═══════════════════════════════════════════════════
function _validateUncertainties() {
  if (!state.fitResult?.backendResult?.individual_peaks) return { warnings: [], info: [] };
  const warnings = [];
  const info = [];
  const stderrMap = _buildStderrMap(state.fitResult);
  const preFit = state.fitResult._preFit || {};
  // Map backend param names to pre-fit property names
  const nameMap = { center: 'center', fwhm: 'fwhm', fwhm_l: 'fwhm', amplitude: 'amplitude', gl_ratio: 'glMix' };

  for (const [rawId, params] of Object.entries(stderrMap)) {
    const p = getPeak(Number(rawId));
    if (!p) continue;
    // Rule 0: the fit did not determine this component at all. Reported once,
    // here, instead of the per-parameter alarms (or, after Auto-Fit's centre
    // lock, the neutral "locked" note) that would otherwise misdescribe it.
    if (_isUnsupported(p)) {
      warnings.push(`<li><b>${_escHtml(p.name)}:</b> ${_UNSUPPORTED_LABEL} — with the other components held as fitted, removing it does not make the fit significantly worse${p.support.f != null ? ' (F = ' + p.support.f.toFixed(1) + ', threshold 10)' : ''}. Its centre, width and uncertainties are not reported. Try another starting position or width, lock the centre where chemistry says it belongs, or drop the component.</li>`);
      continue;
    }
    const init = preFit[Number(rawId)] || {};

    for (const [pName, pData] of Object.entries(params)) {
      if (!['center','fwhm','fwhm_l','amplitude','gl_ratio'].includes(pName)) continue;
      const val = pData.value;

      // Locked or linked: skip the alarm-style movement/stderr checks.
      //   - linked satellite (expr set): tied to master via lmfit expr; intentional
      //     by construction → silent
      //   - genuinely locked (vary=false, no expr): user or auto-fit set this lock
      //     → neutral info note pointing at the padlock toggle, not an alarm
      if (pName === 'gl_ratio' && p.shape === 'Voigt') {
        // A03: a Voigt's mix is fixed by the SHAPE (η = 0.5), not by a padlock — there is none to unlock.
        info.push(`<li><b>${_escHtml(p.name)} / mix:</b> fixed at 50/50 by the Voigt shape — choose GL to fit the mix.</li>`);
        continue;
      }
      if (pData.vary === false) {
        const isLinked = pData.expr != null && pData.expr !== '';
        if (!isLinked) {
          info.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> locked — unlock the padlock to refine.</li>`);
        }
        continue;
      }

      // Rule 1: parameter sitting at its bound (within 1% of range from min or max)
      const lo = pData.min, hi = pData.max;
      if (lo != null && hi != null && isFinite(lo) && isFinite(hi)) {
        const range = hi - lo;
        if (range > 0) {
          if ((val - lo) <= range * 0.01) {
            warnings.push(`<li><b>${_escHtml(p.name)} / ${pName}:</b> at lower bound (${lo}). Widen bounds or lock this parameter.</li>`);
            continue;
          }
row 1, so the warning compares `p.center` with min/max of `getROIData().be`
— the grid the request carries.

## 3. "One fix covers both" — verified, with one exact qualification

Manual fit (row 2) and Find Peaks (row 4) apply the same inclusive
[min, max] filter to the same corrected energies, with one difference in
ORDER (Codex round 1): manual fit filters first and then uploads the
selection rounded to 4 dp (`uploadToBackend`), while Find Peaks uploads
the corrected energies rounded to 4 dp and the server filters those. The
selections are therefore identical except for an energy lying within
5e-5 eV of an ROI edge, which the rounding can move across it (Codex's
reproducer: 21 energies 280.00004 + 0.1 i, ROI 280.00002–282.1 — manual 21
points, Find Peaks 20). Real ROIs are typed to 0.1–0.5 eV and energies
rarely carry more than 4 decimals, so the one window the hint names is the
window both use for every ROI a user sets; both directions are pinned in
`tests/js/roi_clamp_centre_warning.test.js`. The edge divergence is
pre-existing and is not changed here (it would change Find Peaks'
request); logged with the empty-field divergence (row 4) for the
fail-open sweep.

## 4. The hint

templates/index.html:4288:  for (let i = 0; i < nTot; i++) xp[i] = lo + i * dxLin;
templates/index.html:4289:  xp[nTot - 1] = hi;                                   // np.linspace sets the endpoint exactly
templates/index.html:4291:  for (let i = 0; i < nTot; i++) { const v = laCasaXPSCore(xp[i] - center, a, b); ds[i] = Number.isFinite(v) ? v : 0; }
templates/index.html:5011:      p.center -= delta;
templates/index.html:5344:    if (Number.isFinite(w)) peak[newWF] = w;
templates/index.html:5346:    if (typeof lock === 'boolean') peak[_widthFixField(newShape)] = lock;
templates/index.html:5353:    if (!(k in peak)) peak[k] = v;
templates/index.html:5975:  p[key] = value;
templates/index.html:5985:      if (key === 'center') parent.center = p.center - p.linkOffset;
templates/index.html:5999:      if (key === 'center') child.center = parent.center + child.linkOffset;
templates/index.html:6012:  p[key] = !p[key];
templates/index.html:6041:    for (const k of LOCK_ALL_KEYS) p[k] = newVal;
templates/index.html:6224:          oninput="getPeak(${p.id}).linkOffset=parseFloat(this.value);getPeak(${p.id}).center=getPeak(${p.linked}).center+parseFloat(this.value);updatePeakParam(${p.id},'center',getPeak(${p.id}).center)">
templates/index.html:6508:  if (par.center    && !p.fixCenter)    p.center    = par.center.value;
templates/index.html:8221:      if (p) p[param] = clamp(param, params[i]);
templates/index.html:8230:      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
templates/index.html:8402:    active.forEach((a, k) => { dp[a] = dpA[k]; });
2547:function _applyRightPanelMode(activeTab) {
5724:function handleChartClick(event) {
5888:function addPeak(overrides) {

exec
/bin/zsh -lc "node <<'JS'
const fs = require('fs'), assert = require('assert');
const src = fs.readFileSync('templates/index.html','utf8').split('\\n');
function extract(name) {const i=src.findIndex(l => l.startsWith('function '+name+'(')); let d=0; for(let j=i;j<src.length;j++){ for(const c of src[j]) {if(c==='{')d++; if(c==='}')d--;} if(d===0)return src.slice(i,j+1).join('\\n');} throw Error(name);}
const names=['getCorrectedBE','getROIData','_roiWindowStatus','_roiHintFor','_refreshRoiHint','_centreOutsideData','_outsideDataBadge','_escAttr','_isUnsupported','_supportRootOf','_applySupportVerdicts'];
const dom={'roi-min':{value:'270'},'roi-max':{value:'320'},'roi-hint':{style:{display:''},textContent:'old hint'}};
const state={rawBE:[285],rawIntensity:[100],ccShift:0,peaks:[]};
let key='current'; const doc={getElementById:id=>dom[id]};
const f=new Function('document','state','_startsLiveKey',names.map(extract).join('\\n')+'\\nreturn {'+names.join(',')+'}')(doc,state,()=>key);
f._refreshRoiHint(f._roiWindowStatus());assert.equal(dom['roi-hint'].textContent,'ROI extends past your data — clipped to 285.00–285.00 eV.');
state.rawBE=[];f._refreshRoiHint(f._roiWindowStatus());assert.equal(dom['roi-hint'].style.display,'none');assert.equal(dom['roi-hint'].textContent,'');
const peaks=[{id:2,linked:1,center:310},{id:1,center:305}];f._applySupportVerdicts(peaks,()=>({supported:false}),key);
const st={n:20,sMin:280,sMax:295};
for(const p of peaks) {assert(f._isUnsupported(p)); assert("'!f._outsideDataBadge(p,st,f._isUnsupported(p)).includes(p.center.toFixed(2)));}
key='"'edited'; assert("'!f._isUnsupported(peaks[0])); assert(f._outsideDataBadge(peaks[0],st,f._isUnsupported(peaks[0])).includes('"'310.00'));
state.rawBE=Array.from({length:21},(_,i)=>+(280.1+i*.1).toFixed(4));state.rawIntensity=state.rawBE.map(()=>100);state.ccShift=.2;dom['roi-min'].value='279.9';dom['roi-max'].value='281.9';
const manual=f.getROIData().be; const fp=f.getCorrectedBE().map(v=>+v.toFixed(4)).filter(v=>v>=279.9&&v<=281.9);
console.log('Singleton, empty clear, linked-root suppression and stale-key checks: PASS');
console.log(JSON.stringify({rawRange:[state.rawBE[0],state.rawBE.at(-1)],ccShift:state.ccShift,roi:[279.9,281.9],manualPoints:manual.length,findPeaksPoints:fp.length,lastCorrected:f.getCorrectedBE().at(-1)}));
JS
nl -ba docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md | sed -n '63,75p'
nl -ba tests/js/roi_clamp_centre_warning.test.js | tail -22" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
zsh:1: can't create temp file for here document: operation not permitted
    63	selection rounded to 4 dp (`uploadToBackend`), while Find Peaks uploads
    64	the corrected energies rounded to 4 dp and the server filters those. The
    65	selections are therefore identical except for an energy lying within
    66	5e-5 eV of an ROI edge, which the rounding can move across it (Codex's
    67	reproducer: 21 energies 280.00004 + 0.1 i, ROI 280.00002–282.1 — manual 21
    68	points, Find Peaks 20). Real ROIs are typed to 0.1–0.5 eV and energies
    69	rarely carry more than 4 decimals, so the one window the hint names is the
    70	window both use for every ROI a user sets; both directions are pinned in
    71	`tests/js/roi_clamp_centre_warning.test.js`. The edge divergence is
    72	pre-existing and is not changed here (it would change Find Peaks'
    73	request); logged with the empty-field divergence (row 4) for the
    74	fail-open sweep.
    75	
   144	});
   145	
   146	// "One fix covers both" (plan §3): manual fit filters the corrected
   147	// energies, then uploads them rounded to 4 dp; Find Peaks uploads the
   148	// corrected energies rounded to 4 dp and the SERVER applies the same
   149	// inclusive mask. The two selections are identical except for an energy
   150	// within 5e-5 eV of an ROI edge, where rounding can move it across. Pinned
   151	// both ways so the qualification stays true.
   152	function serverMask(corr, lo, hi) { return corr.map(FP_UPLOAD_ROUND).filter(v => v >= lo && v <= hi); }
   153	test('manual fit and Find Peaks select the same points whenever no energy lies within 5e-5 eV of an ROI edge', () => {
   154	  for (const [lo, hi] of [[270, 320], [283.2, 300], [282, 293], [281.37, 291.83]]) {
   155	    const e = makeEnv({ rawBE: DATA, roiMin: lo, roiMax: hi });
   156	    const page = e.getROIData().be.map(FP_UPLOAD_ROUND);
   157	    assert.deepStrictEqual(serverMask(DATA, lo, hi), page, `ROI ${lo}–${hi}`);
   158	  }
   159	});
   160	test('…and can differ by one edge point when an energy lies within 5e-5 eV of an edge (pre-existing, logged, not changed)', () => {
   161	  const raw = Array.from({ length: 21 }, (_, i) => 280.00004 + 0.1 * i);   // Codex round 1 reproducer
   162	  const e = makeEnv({ rawBE: raw, roiMin: 280.00002, roiMax: 282.1 });
   163	  assert.equal(e.getROIData().be.length, 21);
   164	  assert.equal(serverMask(raw, 280.00002, 282.1).length, 20, 'rounding 280.00004 to 280.0 moves it below the edge');
   165	});

exec
/bin/zsh -lc "node -e '
const fs = require('\\''fs'\\''), assert = require('\\''assert'\\'');
const src = fs.readFileSync('\\''templates/index.html'\\'','\\''utf8'\\'').split('\\''\\n'\\'');
function extract(name) {const i=src.findIndex(l => l.startsWith('\\''function '\\''+name+'\\''('\\'')); let d=0; for(let j=i;j<src.length;j++){ for(const c of src[j]) {if(c==='\\''{'\\'')d++; if(c==='\\''}'\\'')d--;} if(d===0)return src.slice(i,j+1).join('\\''\\n'\\'');} throw Error(name);}
const names=['\\''getCorrectedBE'\\'','\\''getROIData'\\'','\\''_roiWindowStatus'\\'','\\''_roiHintFor'\\'','\\''_refreshRoiHint'\\'','\\''_centreOutsideData'\\'','\\''_outsideDataBadge'\\'','\\''_escAttr'\\'','\\''_isUnsupported'\\'','\\''_supportRootOf'\\'','\\''_applySupportVerdicts'\\''];
const dom={'\\''roi-min'\\'':{value:'\\''270'\\''},'\\''roi-max'\\'':{value:'\\''320'\\''},'\\''roi-hint'\\'':{style:{display:'\\'''\\''},textContent:'\\''old hint'\\''}};
const state={rawBE:[285],rawIntensity:[100],ccShift:0,peaks:[]};
let key='\\''current'\\''; const doc={getElementById:id=>dom[id]};
const f=new Function('\\''document'\\'','\\''state'\\'','\\''_startsLiveKey'\\'',names.map(extract).join('\\''\\n'\\'')+'\\''\\nreturn {'\\''+names.join('\\'','\\'')+'\\''}'\\'')(doc,state,()=>key);
f._refreshRoiHint(f._roiWindowStatus());assert.equal(dom['\\''roi-hint'\\''].textContent,'\\''ROI extends past your data — clipped to 285.00–285.00 eV.'\\'');
state.rawBE=[];f._refreshRoiHint(f._roiWindowStatus());assert.equal(dom['\\''roi-hint'\\''].style.display,'\\''none'\\'');assert.equal(dom['\\''roi-hint'\\''].textContent,'\\'''\\'');
const peaks=[{id:2,linked:1,center:310},{id:1,center:305}];f._applySupportVerdicts(peaks,()=>({supported:false}),key);
const st={n:20,sMin:280,sMax:295};
for(const p of peaks) {assert(f._isUnsupported(p)); assert("'!f._outsideDataBadge(p,st,f._isUnsupported(p)).includes(p.center.toFixed(2)));}
key='"'\\''edited'\\''; assert("'!f._isUnsupported(peaks[0])); assert(f._outsideDataBadge(peaks[0],st,f._isUnsupported(peaks[0])).includes('"'\\''310.00'\\''));
state.rawBE=Array.from({length:21},(_,i)=>+(280.1+i*.1).toFixed(4));state.rawIntensity=state.rawBE.map(()=>100);state.ccShift=.2;dom['\\''roi-min'\\''].value='\\''279.9'\\'';dom['\\''roi-max'\\''].value='\\''281.9'\\'';
const manual=f.getROIData().be; const fp=f.getCorrectedBE().map(v=>+v.toFixed(4)).filter(v=>v>=279.9&&v<=281.9);
console.log('\\''Singleton, empty clear, linked-root suppression and stale-key checks: PASS'\\'');
console.log(JSON.stringify({rawRange:[state.rawBE[0],state.rawBE.at(-1)],ccShift:state.ccShift,roi:[279.9,281.9],manualPoints:manual.length,findPeaksPoints:fp.length,lastCorrected:f.getCorrectedBE().at(-1)}));
'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp
 succeeded in 0ms:
Singleton, empty clear, linked-root suppression and stale-key checks: PASS
{"rawRange":[280.1,282.1],"ccShift":0.2,"roi":[279.9,281.9],"manualPoints":20,"findPeaksPoints":21,"lastCorrected":281.90000000000003}

codex
BLOCKER: none found. MAJOR: none found.

- **MINOR — equivalence documentation still overclaims, and reverse rounding is untested.** [Plan:68](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:68) claims ordinary user ROIs select identical points. Concrete counterexample: raw energies **280.1–282.1 by 0.1**, charge shift **0.2**, ROI **279.9–281.9** produce **20 manual points versus 21 Find Peaks points**. Subtraction yields `281.90000000000003`; upload rounding admits that endpoint. This remains within the documented, pre-existing exception, so it does not block this UI change. Remove the universal claim and add this reverse case; [test:160](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/roi_clamp_centre_warning.test.js:160) only tests rounding excluding a point.

Round-1 disposition:

- **Find Peaks refresh:** closed for the new hint and centre badges.
- **Rounding equivalence:** correctly qualified mathematically; the minor documentation/test issue above remains.
- **Unsupported tooltip:** closed. Linked children inherit suppression; stale fit keys do not suppress current values.
- **Last-tab hint:** closed. Empty stacks clear before their early return; singleton spectra recompute their own status.

The audited centre-write paths—Find Peaks, Auto-Fit, undo/history, alternative adoption, linked sync and Batch Fit—refresh cards or redraw. The ROI-writer inventory omits a **fourth `_restoreUI` caller**, Batch Fit’s already-active target branch: it refreshes cards immediately, with the hint following on successful fit redraw or subsequent activation.

Hint text uses `textContent`; tooltip attributes use `_escAttr`. I found no new writes to ROI fields, peak values, fit inputs, saves or evidence keys.

Validation: **37/37 focused tests passed**, plus direct singleton, empty-clear, linked-support and stale-key checks. Full-suite verification was limited by Python imports requiring a writable temporary directory; browser and 20-process results were not independently rerun.

**VERDICT: GO**
tokens used
72,244
BLOCKER: none found. MAJOR: none found.

- **MINOR — equivalence documentation still overclaims, and reverse rounding is untested.** [Plan:68](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/docs/superpowers/plans/2026-09-25-roi-clamp-and-centre-warning.md:68) claims ordinary user ROIs select identical points. Concrete counterexample: raw energies **280.1–282.1 by 0.1**, charge shift **0.2**, ROI **279.9–281.9** produce **20 manual points versus 21 Find Peaks points**. Subtraction yields `281.90000000000003`; upload rounding admits that endpoint. This remains within the documented, pre-existing exception, so it does not block this UI change. Remove the universal claim and add this reverse case; [test:160](/Users/skyefortier/xps-app/.claude/worktrees/fix-roi-clamp/tests/js/roi_clamp_centre_warning.test.js:160) only tests rounding excluding a point.

Round-1 disposition:

- **Find Peaks refresh:** closed for the new hint and centre badges.
- **Rounding equivalence:** correctly qualified mathematically; the minor documentation/test issue above remains.
- **Unsupported tooltip:** closed. Linked children inherit suppression; stale fit keys do not suppress current values.
- **Last-tab hint:** closed. Empty stacks clear before their early return; singleton spectra recompute their own status.

The audited centre-write paths—Find Peaks, Auto-Fit, undo/history, alternative adoption, linked sync and Batch Fit—refresh cards or redraw. The ROI-writer inventory omits a **fourth `_restoreUI` caller**, Batch Fit’s already-active target branch: it refreshes cards immediately, with the hint following on successful fit redraw or subsequent activation.

Hint text uses `textContent`; tooltip attributes use `_escAttr`. I found no new writes to ROI fields, peak values, fit inputs, saves or evidence keys.

Validation: **37/37 focused tests passed**, plus direct singleton, empty-clear, linked-support and stale-key checks. Full-suite verification was limited by Python imports requiring a writable temporary directory; browser and 20-process results were not independently rerun.

**VERDICT: GO**
