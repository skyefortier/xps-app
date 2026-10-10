# Fit recording — Codex round 4, run B (commit 2732fda)

Reviewed `52e5b4a..2732fda`, focusing on `bcb006e..2732fda`. No BLOCKER or MAJOR findings remain.

- **Round 3, centre movements: resolved.** All-locked fits now record every component’s zero displacement, including linked children. The local engine has one successful return; every successful path with free parameters passes through `certify()`. No other successful exit skips the snapshot.
- **Round 3, averaging: resolved.** `_bgEffect` now matches the helpers’ double parse and clamp. Checks covered empty, decimal, exponent, signed, huge and non-numeric values: **7,900 curve comparisons and 1,975 edge-helper comparisons passed**, with recorded `k` matching the computation.
- **Rounds 1 and 2 remain intact.** No regression found in producer records, saves/loaders, imported provenance, lossless exports, software identity, background certificates, or movement over all parameters and components.

**MINOR — documentation overgeneralizes huge averaging values.** [PROGRESS.md:42](/Users/skyefortier/xps-app/.claude/worktrees/fit-recording/docs/autofit/PROGRESS.md:42) says “1e21 or more acts as 1”; entering `2000000000000000000000` actually acts as **2**, correctly recorded by the implementation. The plan repeats this wording. Category: documentation concerning an atypical/non-physical averaging setting; no numerical fix required.

The underlying page/server discrepancy is correctly identified as **pre-existing and outside this recording unit**. Correcting it would change the background. The all-locked finding, by contrast, concerned ordinary supported inputs.

Validation: **130 JS tests and 11 Python tests passed**. One additional Python-backed JS test was blocked by temporary-directory restrictions; browser/HTTP suites were not rerun. Thirty local fits across six shapes, locks and linkage had identical existing outputs against `main`. Workspace unchanged.

VERDICT: GO
