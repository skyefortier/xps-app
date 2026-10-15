Step 5 is **not ready**: four MAJOR findings affect stack rendering, history, and `.fit.json` designation. No BLOCKER found. Persistence and producer switching were treated as deferred work.

1. **Switch OFF — no shipped-page regression found, but the strict gate requirement fails.**

   **MINOR:** `_componentArea` and `_shownPeak` evaluate `state.fitResult` before entering `_sealedDisplay`. Both throw `ReferenceError: state is not defined` in an isolated switch-OFF harness. Existing page callers already require `state`, so this is not evidence of a normal-page crash, but it contradicts “every reader returns at its gate before needing page state.” See [index.html:9303](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9303) and [index.html:9321](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9321).

2. **Switch ON — migration is substantial, but incomplete.**

   **MAJOR: the stack’s in-place update reconstructs the net envelope.** Initial construction uses `rd.fittedSub`, but `_updateStackChart` still uses `rd.fittedY - rd.bg`. Therefore a slider, pill toggle, or verification repaint changes the arithmetic used to display the same seal. A harness using `background = 1e16`, `fittedSub = 1`, and `fittedY = 1e16` displayed **1 initially, then 0 after repaint**. Use the recorded `fittedSub` in both paths. See [initial construction:11896](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11896) and [in-place update:12070](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12070).

   **MAJOR: a server `.fit.json` is subsequently classified as local.** The exporter now writes the view’s server objective, `poisson_weighted_chi_square`, but `_isLocalProvenance` treats that objective as sufficient evidence of a local fit—even with `engine: 'server'`. The existing importer consequently installs local provenance and displays the local-engine caveats. I reproduced this using the exporter and provenance reader. This is compatibility of the newly changed export, not a request to implement step 6. See [export:12947](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12947), [classification:10009](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10009), and [import:3510](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:3510).

   Results, sidebar areas/percentages, Quantify, uncertainties, and the main fit curves generally use the view correctly. Quantify calculates percentages from the supplied recorded areas; I found no independent live-area denominator there ([index.html:11002](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11002)).

   **MINOR remaining omissions:** `.fit.json` still takes `chosenAlternative` and server `reportable` from legacy fields; a fresh sealed server export writes `reportable: null` instead of the view’s `true` ([index.html:12954](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12954)). Batch summary still reads `outcome.chiReduced`, although currently it equals the value placed in local O ([index.html:15147](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:15147)).

3. **Presentation — correct in the main panels, incomplete in history and exports.**

   **MAJOR: history bypasses state entirely.** History rows call `_sealView` directly and show χ²/R as “as recorded”; preview likewise draws the seal’s envelope without checking its verdict. A seal rejected by verification can therefore remain displayed in history without its failure state or reason. The snapshot needs evaluation against its own model/context and owning spectrum, not the active model. See [history rows:16963](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:16963) and [preview:12339](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12339).

   **MINOR: STALE exports lose the actual diagnosis.** TSV always says “model has changed,” including verification failures, and uses the legacy record. PNG also says “Model changed” and omits `sealState` from its metadata precisely when `_figSeal` is null for STALE. Preserve the failed check/reason in these exports. See [TSV:13801](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:13801), [PNG annotation:14083](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14083), and [PNG metadata:14218](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14218).

   The main Results/header state text, suppression of R-level wording, disabled alternatives, and handler enforcement are implemented correctly. See [Results:10725](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:10725), [R panel:14455](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:14455), and [Use handler:9748](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9748).

4. **Owners — normal active/inactive handling is sound; history is the exception.**

   `_ownerOfFit` distinguishes the active live result from inactive tab records, and an unowned result is classified stale. Stack construction explicitly supplies the source tab. See [owner resolution:9252](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9252) and [stack source:11686](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11686).

   History avoids owner resolution altogether rather than supplying a snapshot-specific owner/context; that is the MAJOR history finding above.

5. **Repaint — not every visible consumer follows the verdict.**

   **MAJOR: stack support labels survive invalidation.** `_repaintForSeal` drops cached arrays and calls `_updateStackChart`, but that function updates data/styles without updating component labels. After PENDING → STALE invalidates an unsupported verdict, the dataset still says “not supported by the data.” The extracted-function harness reproduced this. See [verdict repaint:9195](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9195), [label construction:11850](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:11850), and [component update:12092](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:12092).

   The history list is also never refreshed by this verdict path. Main Results, header, R and Quantify do follow `_sealSig` changes ([index.html:9386](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/templates/index.html:9386)).

6. **Tests — useful coverage, insufficient to establish the claimed contract.**

   Specific blind spots:

   - “Switch off is today’s chart” only asserts `_sealedDisplay(...) === null`; it never compares charts ([test:152](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:152)).
   - The stack test checks cached render data, not actual datasets after an in-place update or verdict ([test:141](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:141)).
   - History checks recorded values but never a failed/unconfirmed verdict ([test:299](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:299)).
   - `sidebarPct` is collected but never asserted ([test:180](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:180)).
   - Export coverage lacks XLSX behavior, PNG drawing verification, and server/local `.fit.json` import round trips ([test:344](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/tests/test_browser_seal_step5.py:344)).

   Add discriminating cases where legacy copies differ from O, plus verdict transitions without manually calling render functions.

   The selected JavaScript suites passed except the Python-backed parity test, blocked by the sandbox’s unavailable writable temporary directory. Browser tests were not executed. Read-only harnesses reproduced the stack, history, gate, and export-designation findings.

7. **Design rules — two concrete violations of consistent readings.**

   Stack construction and updating read the same envelope differently; the exporter and importer interpret the same objective differently. Both violate [“Two readings of one field”](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/CLAUDE.md:186).

   No new data-scaled tolerance was introduced. Fix the stack by selecting `fittedSub`, not by adding an epsilon or intensity cutoff; that follows [the threshold rule](/Users/skyefortier/xps-app/.claude/worktrees/seal-1c-fix/CLAUDE.md:169).

VERDICT: NO-GO.
