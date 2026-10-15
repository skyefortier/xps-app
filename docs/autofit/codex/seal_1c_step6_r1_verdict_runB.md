**NO-GO.** I found four MAJOR correctness defects and two MINOR gaps. No files were changed.

1. **Save/load dispatch: mostly correct, but malformed seals are not handled reliably.**

   Projects save `{seal}`; spectrum files save the seal plus view-derived convenience fields. Both loaders use `_installSavedSeal`, and ZIP and drag-and-drop route through those loaders. `.fit.json` imports parameters and explicitly clears the fit. See [project serialization:13403](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13403), [spectrum dispatch:13665](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13665), [ZIP:14056](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14056), [drag-and-drop routing:5380](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:5380), and [parameter import:3504](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:3504).

   **MAJOR — schema rejection still installs values that readers cannot handle.** `_installSavedSeal(rec, true)` installs frozen `{seal:true}` and returns `"not a record"`. Subsequent `_sealSig` throws `Invalid value used as weak map key`. I reproduced this with the extracted production functions. Also, both dispatches test truthiness: explicitly present `seal:false`, `0`, or `""` enter legacy restoration instead of schema rejection. The invalid-record representation and dispatch need to support all schema failures safely. See [installer:11858](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11858), [reader:9456](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9456), and [project dispatch:13902](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13902).

   History/contextual undo still reinstall shallow, unfrozen wrappers without this installer ([2426](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:2426), [17390](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:17390)); that is the explicitly deferred step-7 work. Batch produces a local seal rather than invoking legacy restoration ([15453](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:15453)).

2. **The schema is neither complete nor compatible with every honest response.**

   **MAJOR — valid “starts did not run” responses are rejected.** The schema requires `fit` and `alternatives` whenever `O.starts` is non-null. The server legitimately returns `{ran:false, reason:"method"}` for global methods, and analogous records for unsuccessful/skipped starts. Thus a global-method fit with multiple independent peaks becomes PEAKS-ONLY even when its fit is valid. The extracted schema reproduces the rejection. Validate the `ran:false` and `ran:true` variants separately. See [schema:7200](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7200), [request starts count:7080](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7080), and [server variants:2868](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/fitting.py:2868).

   **MAJOR — unchecked nested fields reach readers before verification.** On an otherwise valid record:

   - `starts.n_not_better_elsewhere = 1` and `starts.not_better_chi2r = ["bad"]` pass schema validation, then `_startsSummaryText` throws `c.toFixed is not a function`.
   - `starts.alternatives[0].n_starts = "<b>FILE MARKUP</b>"` passes validation and is interpolated unescaped into the starts table.

   Both were reproduced using extracted production functions. Verification cannot protect the initial PENDING rendering. Validate every consumed nested field, including counts and numeric lists, and escape textual interpolation. See [schema:7201](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7201), [summary reader:9640](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9640), and [table interpolation:9857](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9857).

   Model IDs/colours receive the existing loader checks, and the inspected name renderers escape names; I found no additional injection through those specific fields. That does not make the overall schema safe.

3. **Round trips: not every honest seal survives as CURRENT.**

   The skipped-starts defect above disproves that claim. Otherwise, the two serializers preserve the complete seal independently of legacy fields, and retain the edited workspace, so their structure supports seal-only re-saving and STALE round trips. See [spectrum serializer:13321](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13321) and [project serializer:13396](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:13396).

   The tests cover selected server, local and Auto-Fit cases, but not Batch or “Use this solution” persistence, nor a loaded-seal → save → second-load cycle. Consequently, the full producer matrix is unproven. CURRENT also remains conditional on matching verification; UNCONFIRMED remains legitimate under the owner’s recomputation rule.

4. **Provenance: normal persistence works, but validation and presentation have gaps.**

   **MAJOR — newly loaded legacy provenance can abort Results rendering.** `_loadedTabProvenance` accepts `{record:{engine:"server",software:{role:7}}}` because `_isFitRecord` checks only the engine. The new no-fit Results branch passes it into `_fitRecordRows`, which throws `sw.role.replace is not a function`. I reproduced acceptance followed by that exception. Validate nested fields or make the record renderer total. See [provenance loader:11864](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:11864), [new rendering path:10887](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:10887), and [failing reader:9749](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:9749).

   The ATTESTED/INCOMPLETE calculation uses the intended server/local software source and producing-page digests, without gating statistics ([7234](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:7234)).

   **MINOR — provenance disappears in required presentations.** Results and CSV/XLSX require `_sealedDisplay`, which excludes STALE; the stale TSV branch also omits provenance. PNG metadata adds `sealState` but never `view.provenance` or the producing-page digest evidence. See [Results:10951](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:10951), [CSV/XLSX:14651](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14651), [stale TSV:14110](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14110), and [PNG:14529](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:14529).

5. **Mutators: no additional in-scope write into a frozen loaded result found.**

   The four named mutators are guarded: [cache invalidators:5039](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:5039), [support restamp:8140](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:8140), and [lazy R-factor:3325](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/templates/index.html:3325). The serializers no longer require legacy fields on their sealed paths. History’s unfrozen reinstall remains the deferred exception described above.

6. **Switch OFF: no normal-workflow behavioral regression found relative to step 5.**

   Persistence, provenance rendering and legacy refusal are gated. `_isInstalledSeal` itself is not switch-gated, but normal switch-off producers/loaders do not create frozen sealed wrappers. This conclusion is from code inspection, not an exhaustive browser comparison.

7. **No: several tests would not fail on the defect their names claim to cover.**

   **MINOR — acceptance tests mask or omit their named behavior.**

   - The five-tab test’s `SETTLE` calls `_ensureVerified` for every tab itself. Removing the loader’s inactive-tab verification loop can still pass ([helper:27](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:27), [test:113](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:113)).
   - Auto-Fit’s “both checks” test collects requests but never asserts them; CURRENT alone does not prove the anchor was checked ([178](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:178)).
   - “Switch off saves and loads” never loads and checks only three serialization properties ([306](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:306)).
   - Provenance tests accept either state without controlled missing-field cases; an implementation always returning INCOMPLETE with a nonempty list could pass ([296](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-s6/tests/test_browser_seal_step6.py:296)).

   The remaining tests directly assert useful parts of their named behavior, but do not cover the defects above or the complete §11 matrix.

Validation: extracted-function probes confirmed the reported rejection, exceptions and markup rendering. The targeted JavaScript run had 100 passes and three failures involving Python’s unavailable writable temporary directory. Browser pytest could not start for the same sandbox limitation.

**VERDICT: NO-GO.**
