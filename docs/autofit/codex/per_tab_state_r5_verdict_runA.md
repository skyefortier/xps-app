# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 5, RUN A (2026-09-09, reviewed at 57de357 / code 49fc345)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 52,045.
Prompt: docs/autofit/codex/per_tab_state_r5_review_prompt.txt
Evidence: node 178 pass; seven browser files passed together; round-4 full suite on the parent: 829 passed / 7 skipped.
Round 5: NO-GO x2 — destructuring, own-property allowlist, count, window.K / IIFE class holders all CLOSED (both). OPEN: MAJOR a class EXPRESSION in a superclass position carrying static fields is not reported (class K extends class { static store = [] } {}); MAJOR a static block that only ASSIGNS (this.store = []) leaves the class unclassified (const K = class { static { this.store = [] } }). Disposition in round 6: conservative rule — every class with static fields or a static block reachable in module scope is reported under its best name (subclass for a superclass expression, '[anonymous class]' otherwise), and a static block is reported as a whole.

**Findings**

Reviewed `49fc345`; current HEAD `57de357` adds only the round-5 prompt. No archived verdicts read.

Destructuring defaults/rest, own-property allowlist validation, and the 61-binding count are verified. Both requested class-expression examples are caught through their outer holders (`window.K` or the IIFE-result binding). The 14 focused tests pass. The full Node run encountered sandbox temporary-directory failures in Python-backed tests.

1. **MAJOR — Inherited static fields bypass the guard.** [module_state_scan.js:95](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:95) never reports a class expression used as a superclass. Both `class K extends class { static store = []; } {}` and its `const K = class …` equivalent return **zero names**, including when appended to either real script. Runtime execution confirms mutable `K.store` exists. These are declared static fields outside the documented manual-review boundary. Cover superclass expressions and inherited static state in the immutable exemption; add mutation tests.

2. **MAJOR — Static-block property initialization leaves its owning class unclassified.** [module_state_scan.js:64](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:64) finds declarations inside static blocks but misses `class K { static { this.store = []; } }`. The `const K = class …` variant also reports **zero names**, despite correctly recognizing the initializer as potentially mutable. Both bypass the guard in either real script and create persistent arrays. The documented exception concerns additions to **already allowlisted objects**; here `K` never receives classification. Report the owner/static block conservatively or detect these stores, with mutation coverage.

VERDICT: NO-GO — Class inheritance and static-block initialization still introduce unclassified module-lifetime mutable storage without failing the guard.
