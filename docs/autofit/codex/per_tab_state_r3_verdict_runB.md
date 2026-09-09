# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 3, RUN B (2026-09-09, reviewed at 2ccad17 / code 015512e)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 84,910.
Prompt: docs/autofit/codex/per_tab_state_r3_review_prompt.txt
Round 3: NO-GO x2 — auto-fit owner-before-confirmation, fit inputs before upload, generic-JSON guard, batch target identity, stored-result recovery, debounce ordering, wording: all CLOSED (both). OPEN: MAJOR batch reads sourceTab.peaks/ui/ccShift inside the loop (both); MAJOR an already-active target is not refreshed into live state because activateTab no-ops (B); MAJOR the tokenizer scanner still misses valid forms — destructuring, ASI, labelled/unbraced-if declarations, top-level blocks, static class fields, IIFE initialisers (both). MINOR: recovered results do not display their stored settings (both). Disposition in round 4: batch source snapshot before the loop + explicit already-active refresh; scanner replaced by a real parser (AST), not a longer regex list.

**Findings**

Reviewed `015512e` and `main...HEAD`; current HEAD `2ccad17` only adds documentation. No archived verdicts read.

Dispositions **1, 2, 3, 6, and 8 are verified**. Stored-result recovery works: `_fpRenderResults()` explicitly sets `fp-results` to `display: block`. Batch target identity is fixed, but batch ownership remains incomplete.

1. **MAJOR — Batch source inputs are still read inside the loop.** [index.html:10720](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:10720) reads `sourceTab.peaks`; subsequent lines read `sourceTab.ui` and `sourceTab.ccShift` on every iteration, contrary to disposition 4. An in-memory probe of the production function edited and synchronized A during the inter-iteration yield: B received center/averaging/shift `285/3/0`, while C received `289/9/2`, without cancellation. Deep-copy the source model/settings and capture its shift before the first await.

2. **MAJOR — Activating the next target during the 10 ms yield bypasses propagation.** [index.html:10743](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:10743) assumes `activateTab(tid)` populates live state. It returns immediately when that target is already active. The preceding writes update the record, leaving live peaks and controls unchanged; the identity check passes, and the subsequent synchronization overwrites the propagated record. A production-function probe switching to C during B’s final yield fitted C’s original center/averaging `287/5`, instead of A’s `285/3`, while reporting success. Revalidate after the inter-iteration yield or explicitly handle an already-active target.

3. **MAJOR — The scanner still silently misses ordinary module state.** [module_state_scan.js:75](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:75) does not handle automatic semicolon insertion, and declaration matching excludes destructuring. Appending each of these valid mutations to **both real inline scripts** failed to report the forbidden holder: `const [ROUND3_FORBIDDEN] = [[]];`, `let harmless = []\nlet ROUND3_FORBIDDEN = [];`, and `{ var ROUND3_FORBIDDEN = []; }`. Standalone probes also missed labelled `var`, top-level block `let`, static class fields, and container-returning IIFE initializers. A regex after an unbraced `if` can still desynchronize depth and hide subsequent declarations. These gaps exceed the documented closure boundary; disposition 7 remains open.

4. **MINOR — Recovered results lack visible original settings.** [index.html:13863](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/templates/index.html:13863) resets method and region controls before displaying the saved result. The “last result” status is helpful, and Apply correctly uses retained provenance/averaging, but the original settings are not displayed alongside the result. Showing them would reduce ambiguity after ROI or peak edits.

Validation: **18/18 targeted ownership, scanner, and averaging tests passed**. The full Node run reported 164 passed, 12 failed, and 3 TODOs; Python-backed parity tests encountered the sandbox’s unavailable temporary directory. Browser tests were reviewed but not rerun.

VERDICT: NO-GO — Batch propagation still consumes changing source inputs and mishandles an already-active target, while the scanner fails to enforce the declared module-state boundary.
