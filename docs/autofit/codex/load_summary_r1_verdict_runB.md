Review scoped to **`05591b9`**. The working tree changed during review; those later edits are excluded.

1. **MAJOR — A mixed-reason summary can put its dismiss button outside the viewport.** [templates/index.html:821](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:821)  
   The fixed, bottom-anchored panel has no maximum height or scrolling region. At phone width, enough reason groups push its header and only dismiss button above the viewport. Page scrolling cannot recover the top of this fixed element. Separately, the flex title lacks `min-width: 0` and word breaking, so a long unbroken project/spectrum name can push the button horizontally offscreen.

   Reproduction: at 320×568, call `showLoadSummary` with one tab in each project-reachable group—earlier, rawdata, background, unmatched, damaged, unreadable, unconfirmed, bgchanged and voigt. Add `voigtAlso` for the unconfirmed tab. Bound the panel’s height, scroll its body, keep dismissal visible, and allow title wrapping.

2. **MAJOR — Stack pruning loses information instead of moving it into per-tab detail.** [templates/index.html:14354](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:14354)  
   Only aggregate entry/stack counts survive. The affected stack identities and individual removal counts are discarded, and no stack-specific notice is installed.

   Reproduction: load two stacks with respectively one and three missing-source entries. Previously their names and individual counts were reported; now only “4 stack entries … from 2 stacks” remains. Opening either stack cannot explain what happened. Keep the grouped summary, but preserve the details on each affected stack.

3. **MINOR — “In N of those” has an ambiguous, potentially impossible antecedent.** [templates/index.html:15470](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:15470)  
   I reproduced this output from the committed functions:

   - Three unconfirmed tabs, all also Voigt-stale.
   - One background-changed tab.
   - One Voigt-only tab.
   - Then: **“In 3 of those…”**, immediately after the one-tab Voigt-only sentence.

   The stored counts are correct, including repeated tab names. The prose is not unambiguous. Name the background-related population explicitly, or attach separate “also” counts to its respective groups.

4. **MINOR — Some grouped sentences overstate what the restore established.** [templates/index.html:15429](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:15429), [templates/index.html:15464](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:15464)  
   Specific mismatches:

   - Missing envelope ⇒ “saved by an earlier version,” although that failure establishes missing data, not its cause.
   - Arithmetic overflow or exceeding the grid checker’s supported point count ⇒ points “can’t be matched,” although matching was refused or could not be verified.
   - A spectrum saved after **settings alone** changed ⇒ “model was edited.”
   - Folder FileReader/network failures ⇒ the file “holds no spectrum the app can read,” although its contents may be valid.

   All failure strings reach a group; none disappear. More neutral wording would preserve the actual distinction between absent, invalid, ambiguous and uncheckable data.

5. **MINOR — The next successful load does not always replace the summary.** [templates/index.html:5500](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:5500), [templates/index.html:13952](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:13952)  
   Load an older project, then load a CSV/XLSX/VGD or apply a `.fit.json`/v1 setup. Those paths issue their usual success notice without dismissing or replacing the previous summary. The earlier project’s refit instructions remain over the newly active content. Project, saved-spectrum and completed folder loads do replace it correctly.

6. **MINOR — The audit incorrectly treats all validation notices as short.** [templates/index.html:14194](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:14194), [templates/index.html:17832](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/templates/index.html:17832)  
   `_peakLoadError` embeds unrestricted invalid IDs, link targets and colors. I reproduced a **2,109-character prominent notice**, still dismissed after three seconds, using a project peak ID containing 2,048 `x` characters. The same helper reaches spectrum and fit/setup loads.

   Generic session/parse errors also interpolate exception text into the four-second, non-wrapping `#notify`. These paths need bounded summary text with persistent detail, or explicit treatment in the audit; the plan’s blanket “short” classification is inaccurate.

7. **MINOR — The refit proposal misstates failure/edit behavior and needs clearer red-band semantics.** [2026-10-28-load-summary.md:64](/Users/skyefortier/xps-app/.claude/worktrees/load-notices/docs/superpowers/plans/2026-10-28-load-summary.md:64)  
   An edit during ordinary Run Fit is retained; the tab is not restored “exactly as loaded.” Transport failure can also trigger a successful local fallback that changes the tab. The red-band confirmation belongs to **adopting an alternative solution**; ordinary fit certificate displacement is a notice, not a confirmation. Clarify these outcomes before implementation.

   The proposal correctly identifies `_serverFitJob`, per-tab method/background/ROI, and Batch Fit’s local-only behavior. No refit action was built.

The remaining audit results:

| Path | Assessment at `05591b9` |
|---|---|
| Project JSON/ZIP legacy restore | Concatenated dropped/stale notices replaced correctly. |
| Saved-spectrum load | Long dropped/stale/unreadable notices moved correctly. |
| ZIP missing files | Count retained in the persistent summary. |
| Folder load | Counts successful reads; `_loadOneFile` has one caller, updated correctly. FileReader errors resolve `false`. |
| Fit file / v1 setup | Ordinary notices are short; validation and summary replacement exceptions noted above. |
| History/snapshot/undo restore | No concatenated per-tab notification found; snapshot notices are short. |
| Seal installation | Unreadable seals retain their Results explanation. Verification uses panel state rather than concatenated notifications. |
| Stack pruning | Aggregation works; identifying detail is lost. |

I found **no change to which legacy fits are restored, marked stale or dropped**, or to stack-pruning decisions. Dropped-fit groups retain their full reason through `_droppedLegacyFitOf`; stale groups retain the Results banner; unreadable seals retain the record-failure explanation. The exception is stack-specific detail.

The markup supplies `role="status"`, polite announcements and a native, keyboard-focusable dismiss button with an accessible name. Ordinary prose wraps. The viewport/overflow problem above prevents calling the layout complete.

The browser tests meaningfully reject the old concatenated/expiring behavior and wrong folder count. However, the “restored in full” fixture contains **no fitted result**, so it does not verify successful fit restoration. Per-tab checks sample only three IDs per group; empty report arrays make those loops vacuous. There are no committed checks for mixed stale populations, phone overflow, replacement by other load types, or actual FileReader errors.

I reran the two updated JS files against the **committed sources: 56 passed**, and separately exercised successful, unparseable and FileReader-error folder branches. I did not rerun browser tests in this read-only environment or assume the full pytest suite passed.

VERDICT: NO-GO
