# Codex adversarial CODE review — unit A0 — round 3 (second recheck), RUN B (2026-09-15)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. tokens used.
Prompt: docs/autofit/codex/a0_local_lm_acceptance_recheck2_prompt.txt
Branch state reviewed: b105606. Outcome: NO-GO x2 — the 1e-4 column-norm cutoff froze determined satellites; the undamped-Newton ftol gate still passed points where a 1e-3 scaled move gained > 1e-6. Dispositioned in a0_local_lm_acceptance_recheck3_prompt.txt (round 4): both mechanisms removed, replaced by an explicit feasible-descent certificate.

Reviewed `origin/main..b105606` in full, including tests. No files changed.

1. **BLOCKER — The new cutoff freezes a determined satellite and certifies the unchanged model.** At [index.html:7439](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7439), small scaled columns are excluded from both optimization and convergence checks.

   Reproduction using the unmodified extracted functions: grid **280–295 eV, spacing 0.01**; two Gaussians with centers/FWHMs locked at **285/1** and **290/1**. Data amplitudes are **100,000 and 10**; starting amplitudes are **100,000 and 5**, both free.

   The fitter returns **success, one iteration, zero accepted steps**, with `undetermined: ["satellite.amplitude"]`. Moving that amplitude from **5 to 5.005**, exactly the oracle’s scaled `1e-3` move, reduces SS from **1881.729619 to 1877.968042**: a relative reduction of **0.001999**, far exceeding `1e-6`.

   Locking only the already-correct main amplitude makes the satellite recover **10 in four iterations**. These separated amplitude columns are independently identifiable; their relative scaled magnitudes do not establish finite-difference failure or statistical indeterminacy. The `1e-4` cutoff is therefore **not defensible as implemented**. Reporting the exclusion does not make the resulting convergence claim valid.

2. **MAJOR — The Newton-prediction gate still fails the requested stationarity oracle without any held parameters.** At [index.html:7480](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:7480), the additional prediction remains an approximation rather than a bound on available true reduction.

   Reproduction: grid **283–287 eV, spacing 0.01**; Gaussian data `(center, FWHM, amplitude) = (285, 1.5, 5)`; starting model **(286, 0.3, 20)**, with only FWHM locked.

   It succeeds after **78 iterations**, at center **285.001882614**, amplitude **6.933718280**, with no undetermined parameters. Moving center by **−0.0003** reduces SS from **1736.966234 to 1736.963560**, a relative reduction of **1.53969e-6**. The committed oracle fails at the requested `1e-6` tolerance.

   Instrumentation identifies the `ftol` exit: `actred=9.11338e-7`, `prered=4.73895e-7`, `predGN=4.73896e-7`, while gradient cosine is **6.88400e-4**. This is much smaller than finding 1’s failure, but independently disproves the stated acceptance criterion. Add both reproductions and require convergence checks that cover every feasible free direction.

3. **MINOR — The new held-parameter qualification disappears on save/reload.** Both [spectrum serialization](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9211) and [project serialization](/Users/skyefortier/xps-app/.claude/worktrees/fix-local-lm-acceptance/templates/index.html:9290) preserve `status: "converged"` but omit `undetermined`. The current result consequently loses the record of which free parameters were excluded. Persist that qualification and expose it beyond the transient notification.

The other dispositions are supported: upload null-body rejection, scanner wording/missing-path handling/unconditional caveat, updated maintainer documentation, and revised student wording. The scope ruling remains defensible.

**Validation:** all **54 focused and structural JS tests passed**. All **18 committed targets converged in 5–532 iterations** and passed the supplied oracle at `1e-6`. Scan_1 and Scan_4 actually report **both amplitude and width** held. The scanner reproduced two suspected repository tabs and exit **2** for a nonexistent path. Python/browser suites were not independently run.

VERDICT: NO-GO — The optimizer still certifies non-stationary fits, including an unchanged, independently determined satellite excluded by the new sensitivity cutoff.
