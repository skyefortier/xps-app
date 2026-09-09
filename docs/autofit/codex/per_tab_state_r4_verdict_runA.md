# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 4, RUN A (2026-09-09, reviewed at 9088543 / code 3fdba3c)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 74,375.
Prompt: docs/autofit/codex/per_tab_state_r4_review_prompt.txt
Evidence at review time: node 174 pass / 0 fail / 3 known-gap todo; seven browser files (per_tab_state 18) passed together, exit-code gated; round-3 full suite on the parent: 827 passed / 7 skipped; round-4 full suite recorded in the round-5 header.
Round 4: NO-GO x2 — both batch items CLOSED (source snapshot before the first yield; already-active target loaded into live state), recovered-result settings CLOSED, acorn confirmed test-only (both). OPEN, all scanner/allowlist: MAJOR destructuring with a primitive RHS hides container defaults/rest (const {stash = []} = 0; const [...stash] = ''); MAJOR static fields with string/computed keys, class EXPRESSIONS, static blocks not reported; MAJOR the allowlist check used 'in', so inherited names (constructor, toString, __proto__) passed unclassified. MINOR: memo must name property additions, eval/Function and prototype getters as the manual-review boundary; binding count 61, not 64.

**Findings**

The scanner disposition remains open. Both batch fixes check out: source inputs are captured before yielding, and the active-target refresh supplies the fit’s dependencies. `runFitLocal` replaces `fitResult` without reading its previous value; chart state is not a fit input. Recovered results show the stored settings and caution. Acorn remains test-only.

1. **MAJOR — Destructuring can bypass the scanner.** [module_state_scan.js:55](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:55) skips declarations based on the RHS before examining the binding pattern. Both `const {stash = []} = 0;` and `const [...stash] = "";` create mutable arrays but produce no reported names. Reproduced standalone and appended to **each real inline script**. Restrict the primitive-initializer exemption to simple identifiers, or analyze destructuring defaults/rest explicitly.

2. **MAJOR — Static-class coverage remains incomplete.** [module_state_scan.js:59](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:59) misses `class K { static "store" = []; }`, `class K { static ["store"] = []; }`, and `const K = class { static store = []; };`. Each reports nothing, including when appended to either real script. The blanket `ClassBody` boundary also skips declarations in static blocks. These are within the advertised declaration/static-field coverage, not the function-closure exception.

3. **MAJOR — Inherited properties count as allowlist entries.** [per_tab_state.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/per_tab_state.test.js:60) uses `n in ALLOWLIST`. Consequently, `let constructor = [];`, `let toString = [];`, and `const __proto__ = [];` are detected but pass without an explicit classification. Reproduced against both real scripts and the actual allowlist. Use an own-property check and validate the permitted classification values.

4. **MINOR — Document the broader manual-review boundary accurately.** Property additions such as `state.x = []`, dynamic `eval`/`Function` code, and prototype getters can retain content outside this declaration guard. These belong to manual ownership review; the memo currently names only closures explicitly. They do not justify the declaration omissions above. Also, the current scanner enumerates **61 bindings**, not the reported 64.

Validation: 17 focused tests passed. The full Node run returned 162 passed, 12 failed, and 3 TODO; Python-backed checks encountered sandbox temporary-directory failures. Browser/pytest evidence was not independently rerun. Actual HEAD `9088543` differs from `3fdba3c` only by the round-4 prompt. No archived verdicts were read.

VERDICT: NO-GO — The ownership guard still silently permits unclassified module-lifetime containers through destructuring, static-class forms, and inherited allowlist properties.
