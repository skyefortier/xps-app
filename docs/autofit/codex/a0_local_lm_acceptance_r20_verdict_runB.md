# Codex adversarial CODE review — unit A0 — round 20 (delta: labelling, fourteenth pass), RUN B (2026-09-16)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck19_prompt.txt
Outcome: GO x2 — no remaining in-scope designation gap; MINOR (both): stack close/toggle coverage is structural (shipped handlers executed by both runs). Unit passes review: optimiser/acceptance rule GO x2 at round 6, starting-point designation GO x2 at round 20. Final suites on the owner machine: JS 241 pass / 3 known TODO; Python 727 pass / 7 skips (rerun on the final tree before deploy); browser 114 pass; :5151 browser check (batch, banners on Results/Quantify/sidebar incl. after scroll, status caption, server fit, success:false, HTTP 400, transport abort, save labels) pass.

1. **MINOR — Stack regression coverage remains structural.** The [close-tab test](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/tests/js/fit_acceptance.test.js:505) checks for the rebuild call without asserting dataset removal. Add behavioral coverage for closing the last local source and retaining another local source. Independent execution of the shipped handlers passed those cases, mixed/hidden survivors, and both checkbox toggles; this is nonblocking.

No remaining in-scope designation gap or functional regression identified in `c790c03..HEAD`. The round-19 fix removes the closed source’s curves and updates the banner correctly.

Validation: 63 targeted tests passed; full JavaScript suite reported 229 passes, 3 TODOs, and 12 Python parity failures associated with the sandbox’s unavailable writable temporary directory. Browser layout was not exercised.

VERDICT: GO
