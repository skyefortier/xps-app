# Archive Find Peaks round 1 — run B (commit 9dc28a3; codex exec, reasoning high)

- **MAJOR — JavaScript Find Peaks tests are not running in CI.** [CLAUDE.md:232](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/CLAUDE.md:232) claims every test runs, but the only workflow invokes pytest and Python gates ([autofit-gates.yml:42](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/.github/workflows/autofit-gates.yml:42)). No pytest wrapper invokes `tests/js`. Concrete failure: a failing assertion in `find_peaks_archived.test.js` or the polling-liveness test never reaches CI. This inherited gap violates the owner’s explicit acceptance criterion. Add a required JavaScript-suite step.

- **MINOR — Unit B’s quantitative justification exceeds its cited evidence.** [PROGRESS.md:23](/Users/skyefortier/xps-app/.claude/worktrees/archive-find-peaks/docs/autofit/PROGRESS.md:23) asserts `k = 0.43–0.75` and a `1.3–2.3×` χ²ᵣ correction. The cited record, retrieved from commit `08a51d9`, reports variance/mean of `0.4–1.2`, without that narrower estimate. For variance/mean `1.2`, correction would *lower* χ²ᵣ to about `0.83×`. It also explicitly says constant noise rescaling leaves the F test unchanged. Cite the additional measurement or remove the unsupported numbers and clarify the F-test invariance.

Verification: **78 focused JavaScript tests passed**. The archive static test rejects main’s template, and its block boundaries are valid. The browser helper genuinely runs analysis and applies its results. Inspection found no additional UI launch or cached-provenance display path; backend, engine, shared fitting code, and serialization remain unchanged.

Python verification was blocked during collection by the read-only temporary-directory restriction; browser tests were not rerun.

**VERDICT: NO-GO**
