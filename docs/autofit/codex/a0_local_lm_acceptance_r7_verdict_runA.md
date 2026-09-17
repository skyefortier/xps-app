# Codex adversarial CODE review — unit A0 — round 7 (delta: starting-point labelling), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck6_prompt.txt
Outcome: NO-GO x2 — designation missing at Quantify, TSV export, saves, activation/status bar, history, chart labels; structural test too broad. Dispositioned in a0_local_lm_acceptance_recheck7_prompt.txt (round 8).

1. **MAJOR — Quantify remains unlabelled.** [renderQuantify](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7753) displays local areas and atomic percentages with only the generic “Semi-quantitative” warning. Quantify hides the Results tab containing the new banner, so these numbers appear without the required starting-point restriction. Confirmed by executing both renderers.

2. **MAJOR — Export coverage is incomplete.** [exportResults](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9868) writes `xps_fit_result.tsv` containing model, residual, and component curves without any local provenance or reportability warning. [Spectrum saves](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9244) and [project saves](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9323) preserve engine/objective/status, but carry no explicit starting-point or non-reportable designation. Add that designation to exported local results.

3. **MAJOR — Other visible fit presentations remain unlabelled.** [History rows](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:12885) still show “Fit #…” and residual variance without the restriction. [Tab activation](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:3218) restores the statistic without starting-point wording; the status bar retains its static χ²ᵣ heading. Main-chart and stack envelopes likewise remain labelled “Fit” or “(fit)”. These are gaps against the new acceptance requirement, rather than newly introduced numerical regressions.

4. **MINOR — The structural test overstates coverage.** [The new test](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/fit_acceptance.test.js:185) searches broad source slices, omits the sites above, and does not exercise conditional rendering. Its combined CSV/XLSX assertion would pass if either warning disappeared. Add behavioral checks for local, weighted, and reloaded results.

The banner predicate itself is correct: persisted `objective` determines the label, even without `engine`. Spectrum/project persistence preserves that field, so reloaded local results receive the banner when `renderResults()` runs.

All 12 acceptance tests passed. Independent probes confirmed the omissions, escaped peak-name rendering, and the CSV warning with its unchanged 16-column table header. No delta-induced HTML injection or obvious results-panel layout defect was identified; layout was inspected in source, not browser-rendered.

VERDICT: NO-GO — Local results still appear and export without the required starting-point designation across several reachable paths.
