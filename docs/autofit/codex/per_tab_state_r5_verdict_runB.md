# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 5, RUN B (2026-09-09, reviewed at 57de357 / code 49fc345)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 59,974.
Prompt: docs/autofit/codex/per_tab_state_r5_review_prompt.txt
Evidence: node 178 pass; seven browser files passed together; round-4 full suite on the parent: 829 passed / 7 skipped.
Round 5: NO-GO x2 — destructuring, own-property allowlist, count, window.K / IIFE class holders all CLOSED (both). OPEN: MAJOR a class EXPRESSION in a superclass position carrying static fields is not reported (class K extends class { static store = [] } {}); MAJOR a static block that only ASSIGNS (this.store = []) leaves the class unclassified (const K = class { static { this.store = [] } }). Disposition in round 6: conservative rule — every class with static fields or a static block reachable in module scope is reported under its best name (subclass for a superclass expression, '[anonymous class]' otherwise), and a static block is reported as a whole.

**Findings**

Verified the destructuring fixes, own-property allowlist validation, and 61-binding count. The requested `window.K = class …` and IIFE-returned-class examples are caught through their outer holders. No archived verdicts were read.

Focused tests: **14 passed**. The full Node run returned 166 passed, 12 failed, 3 TODO, with Python temporary-directory errors under this read-only sandbox; I could not independently confirm the reported full-suite result.

1. **MAJOR — Anonymous superclass static fields escape detection.** In [module_state_scan.js](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:95), class expressions receive static-state reporting only through a direct variable initializer. Consequently, `class K extends class { static store = []; } {}` reports **nothing**, although `K.store` is a persistent array. The `const K = class extends class …` equivalent also escapes. Both add zero findings when appended to either real script. No function boundary, runtime property addition, or prototype getter is involved; the documented exclusions do not cover this. Report static state in superclass expressions and add mutation coverage.

2. **MAJOR — Static-block stores can disappear along with their class binding.** In [module_state_scan.js](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:88), `const K = class { static { this.store = []; } };` reports **nothing**: `reportClass` finds no declaration, and the unconditional `const` continuation suppresses `K`. Runtime execution confirms `K.store` is an array; appending this to either real script leaves the guard passing. The memo’s exception concerns additions to an **allowlisted** object, but `K` never requires classification. Retain a reportable class binding or static-block marker when its state cannot be enumerated, and add this mutation test.

VERDICT: NO-GO — Static state in anonymous superclasses and assignment-only static blocks still bypasses the ownership allowlist without falling within the documented manual-review boundary.
