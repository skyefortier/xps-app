# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 6, RUN A (2026-09-09, reviewed at dc97555 / code db6566a; page unchanged since 3fdba3c)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 71,616.
Prompt: docs/autofit/codex/per_tab_state_r6_review_prompt.txt
Round 6: NO-GO x2 — superclass-expression and static-block rules CLOSED (both). OPEN, scanner only: MAJOR computed class keys are evaluated in the enclosing scope but the whole ClassBody was treated as a function boundary (both); MAJOR catch-clause bindings not enumerated (B); MAJOR RegExp literals exempted as immutable though they are mutable objects (A); MINOR '[anonymous class].x' is allowlistable in principle (A); MINOR the stateless-class negative assertion should check an exactly empty result (B).

**Findings**

1. **MAJOR — Computed class keys still hide static declarations.** [module_state_scan.js:119](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:119) disables module scope for the entire `ClassBody`, including computed keys evaluated during class definition:
   ```js
   class K {
     [register(class { static store = [] })]() {}
   }
   ```
   The scanner returns `[]`. A runtime probe confirmed that `register` can retain the class and its mutable `store`. This is an **in-scope declaration**, with no function boundary crossed. Walk computed keys in their enclosing scope while excluding method bodies.

2. **MAJOR — RegExp literals are incorrectly exempted as immutable.** [module_state_scan.js:53](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:53) exempts every `Literal`, including mutable RegExp objects:
   ```js
   const stash = /x/g;
   stash.lastIndex = [{ center: 285 }];
   ```
   This also returns `[]`; runtime verification confirms the array remains accessible. `lastIndex` is an **existing writable own property**, so this requires neither property additions nor closures. The container declaration belongs in scope. Both this mutation and finding 1 added zero reported names when appended to either real inline script.

3. **MINOR — Anonymous-class names are not inherently unallowlistable.** [per_tab_state.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/per_tab_state.test.js:60) accepts any own key with a valid classification, including `"[anonymous class].s"`. These names fail the current allowlist, but the stronger round-6 claim requires an explicit rejection or narrower wording.

The supplied superclass and assignment-only static-block cases are fixed and pass. No additional application regression was identified: actual HEAD `dc97555` adds only the review prompt after `db6566a`, and the page matches `3fdba3c`. Archived verdicts were not read.

Validation: all **23 focused tests passed**. The full Node run produced **169 pass / 12 fail / 3 TODO**; the 12 failures arise from Python imports requiring a writable temporary directory unavailable in this sandbox. Browser/full-pytest results remain author-reported.

VERDICT: NO-GO — Computed class keys and RegExp-literal declarations still allow module-lifetime mutable containers to escape the ownership guard.
