# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 3, RUN A (2026-09-09, reviewed at 2ccad17 / code 015512e)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 80,810.
Prompt: docs/autofit/codex/per_tab_state_r3_review_prompt.txt
Round 3: NO-GO x2 — auto-fit owner-before-confirmation, fit inputs before upload, generic-JSON guard, batch target identity, stored-result recovery, debounce ordering, wording: all CLOSED (both). OPEN: MAJOR batch reads sourceTab.peaks/ui/ccShift inside the loop (both); MAJOR an already-active target is not refreshed into live state because activateTab no-ops (B); MAJOR the tokenizer scanner still misses valid forms — destructuring, ASI, labelled/unbraced-if declarations, top-level blocks, static class fields, IIFE initialisers (both). MINOR: recovered results do not display their stored settings (both). Disposition in round 4: batch source snapshot before the loop + explicit already-active refresh; scanner replaced by a real parser (AST), not a longer regex list.

**Findings**

Reviewed `015512e`; checkout HEAD `2ccad17` adds only the review prompt. No archived verdicts read.

Dispositions 1–3, 6 and 8 check out. Target identity in 4 is fixed. Find Peaks recovery works: `_fpRenderResults` explicitly shows the container, and Apply uses the stored metadata.

1. **MAJOR — Batch source inputs are still read inside the loop.** [index.html:10720](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:10720) reads `sourceTab.peaks`; subsequent lines read `sourceTab.ui` and `sourceTab.ccShift`. Contrary to disposition 4’s premise, these are not captured before the loop. An asynchronous rollback on the source can therefore change the model between targets. A deterministic harness executing the shipped function reproduced B receiving center/averaging/shift `285 / 3 / 0`, then C receiving `289 / 7 / 4`. Capture independent source snapshots before the first yield and test mutation between targets.

2. **MAJOR — The scanner still silently misses module-level mutable stores.** [module_state_scan.js:97](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:97) requires declarations at the statement’s beginning, while initializer classification uses an overly broad prefix match. Each following valid form escaped detection, including when appended to **each real inline script**:

   ```js
   outer: var hidden = [];
   if (true) var hidden = [];
   const N = 1
   let hidden = [];
   const {hidden} = {hidden: []};
   const hidden = true ? [] : [];
   ```

   These include actual global bindings, outside the documented closure limitation. The simple appended-declaration test does not establish the promised coverage. Extend scope/declaration handling and classify complete initializers conservatively.

3. **MINOR — Reopened results lack visible run provenance.** [index.html:13869](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:13869) restores the old results after resetting method and region controls. The “last result” status appropriately identifies historical output, but does not show its stored method, regions or averaging, or flag changed ROI/peaks. Display the stored run settings alongside recovered results; this does not reopen the ownership blocker.

Validation: the 12 focused ownership/scanner tests pass. The full Node run produced 164 passes, 12 failures and 3 TODOs; Python-backed checks failed because the read-only sandbox provides no usable temporary directory. Browser tests were inspected, not rerun.

VERDICT: NO-GO — Batch source inputs remain mutable across yields, and the scanner still permits unallowlisted module-level state.
