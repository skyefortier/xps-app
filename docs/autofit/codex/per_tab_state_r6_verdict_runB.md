# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 6, RUN B (2026-09-09, reviewed at dc97555 / code db6566a; page unchanged since 3fdba3c)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 59,561.
Prompt: docs/autofit/codex/per_tab_state_r6_review_prompt.txt
Round 6: NO-GO x2 — superclass-expression and static-block rules CLOSED (both). OPEN, scanner only: MAJOR computed class keys are evaluated in the enclosing scope but the whole ClassBody was treated as a function boundary (both); MAJOR catch-clause bindings not enumerated (B); MAJOR RegExp literals exempted as immutable though they are mutable objects (A); MINOR '[anonymous class].x' is allowlistable in principle (A); MINOR the stateless-class negative assertion should check an exactly empty result (B).

**Findings**

The specified superclass and static-block fixes work, but two declaration gaps remain. Both reproductions return `[]` and add no reported names when appended to either real inline script. Runtime probes confirmed that registration can retain their containers.

1. **MAJOR — Computed class keys hide static declarations.** [module_state_scan.js:119](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:119) disables module scope for the entire `ClassBody`, including computed keys:
   ```js
   class K {
     [register(class { static store = [] })]() {}
   }
   ```
   The key executes during class definition without crossing a function boundary, yet the nested static field is unreported. Computed instance-field keys also reproduce this. This is an **in-scope declaration gap**, outside the documented manual-review boundary. Preserve module scope for computed keys while excluding method bodies and instance initializers.

2. **MAJOR — Module-scope catch bindings are never enumerated.** [module_state_scan.js:97](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:97) handles `VariableDeclaration` bindings but omits `CatchClause.param`:
   ```js
   try { throw {} }
   catch ({ stash = [] }) { register(stash); }
   ```
   Plain `catch (stash)` receiving an array also escapes detection. These bindings are introduced without crossing a function boundary; registration can retain their containers. Under the memo’s “every binding” rule, this is an **in-scope binding-declaration gap**. Expand catch parameters through `bindingNames`.

3. **MINOR — The new stateless-class negative assertion cannot detect erroneous member reports.** [module_state_scan.test.js:105](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/module_state_scan.test.js:105) checks absence of the exact name `[anonymous class]`, whereas reports include a member suffix. Assert that the complete scan result equals `[]`.

Validation: scanner, ownership and endpoint-default tests passed **23/23**. The full JS run returned **169 pass / 12 fail / 3 TODO**, with Python backend failures encountering the sandbox’s unavailable writable temporary directory. Browser/pytest evidence remains author-reported. The page is unchanged since `3fdba3c`; archived verdicts were not read.

VERDICT: NO-GO — Computed class keys and catch bindings still permit unreported container declarations within the scanner’s stated scope.
