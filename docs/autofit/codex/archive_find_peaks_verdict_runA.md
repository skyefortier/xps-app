# Archive Find Peaks round 1 — run A (commit 9dc28a3; codex exec, reasoning high)

- **MAJOR — Find Peaks JavaScript tests do not run in CI.** [.github/workflows/autofit-gates.yml:39](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/.github/workflows/autofit-gates.yml:39) runs pytest; neither job invokes Node, and no pytest wrapper runs the JS suite. Consequently, the new archive guard and existing Find Peaks polling/rendering tests are never executed on a push. A regression caught only by those tests would escape CI. This pre-existing gap violates the unit’s explicit “all Find Peaks tests … running in CI” requirement. Add a required JavaScript test step.

- **MINOR — Unit B’s parking rationale misstates its supporting record.** [docs/autofit/PROGRESS.md:23](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/docs/autofit/PROGRESS.md:23) cites a file absent from this branch without identifying its commit. Reading that record at `08a51d9`, §2 supports dispersion **0.4–1.2**, but does not supply the stated **k = 0.43–0.75** or **1.3–2.3×** calibration range. It also explicitly says constant noise scaling leaves the F test invariant. Concrete scenario: calibrating variance by a constant changes displayed chi2r, but the factor cancels from the support F ratio; the note incorrectly groups that verdict with affected quantities. Qualify the citation and correct the dependency statement.

No reachable launch path or cached-result/provenance display path emerged from tracing the page. Runtime HTML is identical to `main` after removing comments and the menu button; backend, autofit engine, shared fitting infrastructure, and existing tests are unchanged.

Validation: **66 Find Peaks JS tests passed**; the new static suite correctly fails against `main`, with valid block boundaries. The browser helper performs real analysis, but I did **not** rerun browser or Python suites in this read-only review.

**VERDICT: NO-GO.**
