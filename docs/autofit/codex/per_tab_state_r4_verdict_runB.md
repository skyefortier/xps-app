# Codex adversarial review — per-tab state ownership (feature-per-tab-state) — round 4, RUN B (2026-09-09, reviewed at 9088543 / code 3fdba3c)

codex exec 0.153.4 (model gpt-6-astra), read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 69,713.
Prompt: docs/autofit/codex/per_tab_state_r4_review_prompt.txt
Evidence at review time: node 174 pass / 0 fail / 3 known-gap todo; seven browser files (per_tab_state 18) passed together, exit-code gated; round-3 full suite on the parent: 827 passed / 7 skipped; round-4 full suite recorded in the round-5 header.
Round 4: NO-GO x2 — both batch items CLOSED (source snapshot before the first yield; already-active target loaded into live state), recovered-result settings CLOSED, acorn confirmed test-only (both). OPEN, all scanner/allowlist: MAJOR destructuring with a primitive RHS hides container defaults/rest (const {stash = []} = 0; const [...stash] = ''); MAJOR static fields with string/computed keys, class EXPRESSIONS, static blocks not reported; MAJOR the allowlist check used 'in', so inherited names (constructor, toString, __proto__) passed unclassified. MINOR: memo must name property additions, eval/Function and prototype getters as the manual-review boundary; binding count 61, not 64.

**Findings**

1. **MAJOR — Destructuring can still hide mutable bindings.** At [module_state_scan.js:55](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:55), the initializer check skips the entire declaration before expanding its pattern. Both `const {stash = []} = 0;` and `const [...stash] = "";` create mutable arrays but return no scanner names. Both pass when appended to **each real inline script**. Restrict primitive skipping to identifier bindings or analyze defaults/rest explicitly.

2. **MAJOR — Static-field coverage remains incomplete.** At [module_state_scan.js:59](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/lib/module_state_scan.js:59), only class declarations with identifier field keys are reported. Both `class K { static "store" = []; }` and `const K = class { static store = []; };` return no names and pass in each real script. These are direct module-lifetime stores within the promised coverage, outside the closure exception.

3. **MAJOR — Inherited properties bypass the allowlist.** [per_tab_state.test.js:60](/Users/skyefortier/xps-app/.claude/worktrees/feature-per-tab-state/tests/js/per_tab_state.test.js:60) uses `n in ALLOWLIST`. Consequently, `let constructor = [];` is detected but accepted without any classification. Reproduced against both real scripts. Use an own-property check and validate the permitted class values.

4. **MINOR — Document the broader manual-review boundary accurately.** Properties added to `state`/`tabManager`, generated code through `eval`/`Function`, and storage exposed through prototype getters require semantic/manual ownership review. The memo explicitly documents closures, but these additional mechanisms need explicit boundary wording. They need not expand this unit into whole-program analysis; findings 1–3 remain ordinary declaration/allowlist defects within this unit.

The two batch dispositions are closed on inspection: source peaks, UI scalars, shift and intensity reference are captured before yielding; subsequent model inputs come from those snapshots or the target. The explicit active-target load supplies the fit dependencies. `activateTab` itself restores rather than clears `fitResult`; `runFitLocal` replaces it before rendering results, and chart state does not drive the fit. Recovered Find Peaks results display the stored method, regions, averaging and requested caution. Acorn is test-only.

Validation: **17 focused Node tests passed**; the adversarial reproductions above nevertheless bypass the guard. The full Node run encountered Python temporary-directory failures under the read-only sandbox; browser/pytest evidence was not independently rerun. The scanner enumerates **61 bindings**, with **64 allowlist entries**. Actual HEAD is `9088543`, a documentation-only successor to `3fdba3c`. No archived verdict files were read.

VERDICT: NO-GO — Direct module-lifetime container declarations and inherited allowlist names still bypass the ownership guard.
