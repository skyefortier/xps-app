# Codex adversarial CODE review — unit A0 — round 20 (delta: labelling, fourteenth pass), RUN A (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck19_prompt.txt
Outcome: GO x2 — no remaining in-scope designation gap; MINOR (both): stack close/toggle coverage is structural (shipped handlers executed by both runs). Unit passes review: optimiser/acceptance rule GO x2 at round 6, starting-point designation GO x2 at round 20. Final suites on the owner machine: JS 241 pass / 3 known TODO; Python 727 pass / 7 skips (rerun on the final tree before deploy); browser 114 pass; :5151 browser check (batch, banners on Results/Quantify/sidebar incl. after scroll, status caption, server fit, success:false, HTTP 400, transport abort, save labels) pass.

1. **MINOR — Stack regression coverage remains structural.** The [tests](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/fit_acceptance.test.js:494) check source text rather than resulting chart/banner state. Independent execution of the shipped close and toggle handlers passed, including surviving local sources, weighted-only stacks, empty stacks, and chart rebuilds. Nonblocking.

No remaining in-scope designation gap or functional regression identified in `c790c03..HEAD`. Round 19’s source-close defect is resolved.

Validation: 229 passed, 3 TODO; 12 Python parity tests failed because the read-only sandbox lacks a writable temporary directory. Browser layout was not exercised.

VERDICT: GO
