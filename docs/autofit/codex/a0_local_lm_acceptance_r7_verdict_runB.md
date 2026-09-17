# Codex adversarial CODE review — unit A0 — round 7 (delta: starting-point labelling), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck6_prompt.txt
Outcome: NO-GO x2 — designation missing at Quantify, TSV export, saves, activation/status bar, history, chart labels; structural test too broad. Dispositioned in a0_local_lm_acceptance_recheck7_prompt.txt (round 8).

1. **MAJOR — Quantify remains unlabelled.** [renderQuantify](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7753) displays local areas and atomic percentages with only the existing “semi-quantitative” caveat. Opening Quantify hides the Results banner. The Peaks sidebar and chart’s “Fit” label also lack the starting-point qualification.

2. **MAJOR — Export coverage is incomplete.** [exportResults](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9868) exports model/component curves as `xps_fit_result.tsv` without engine identity or warning. [.spec.json](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9244) and [project saves](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9323) preserve `engine`, `objective`, and `status: converged`, but contain no explicit starting-point/non-reportable designation. Persist that designation alongside the numerical output.

3. **MAJOR — Status and history remain unqualified.** [Tab activation](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:3218) restores the statistic without a starting-point label; the bottom status bar still has a fixed χ²ᵣ caption. [History rows](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:12886) show “Fit #…” and residual variance without the qualification—even when the current Results banner describes a different, server-fitted result.

4. **MINOR — The new test overstates its coverage.** [The structural test](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/fit_acceptance.test.js:185) searches selected source slices for wording. It omits the sites above and never exercises the objective-dependent banner condition.

**Reload logic is correct:** the persisted objective controls `_statIsChi`; reloaded local results receive the banner when Results renders. Runtime probes confirmed this and the missing labels above.

**No identified delta regression** in HTML escaping, Results markup, or CSV headers: the banner is static HTML, the CSV warning follows the existing comment convention, and the 16-column header is unchanged. Layout was inspected in source, not browser-tested. Targeted tests: **19/19 passed**.

VERDICT: NO-GO — The new starting-point requirement remains unenforced across quantitative displays, history/status, and several export/save paths.
