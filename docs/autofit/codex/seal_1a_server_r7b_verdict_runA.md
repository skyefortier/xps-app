Reviewed HEAD `39d4688`. **Two MAJOR findings; no BLOCKER found.** No files changed.

1. **MAJOR — non-finite request handling can return `mismatch` before reaching the promised `unconfirmed` check.**  
   Starting with an honest Gaussian request/response, change only `R.request.peaks[0].center` to `Infinity`, leaving its default bounds. Verification returns:
   ```json
   {"state":"mismatch","check":"request","reason":"the request is not one a fit accepts: Parameter 'p1_center' has min == max"}
   ```
   Parameter construction/deep-copy runs first and converts its exception to `mismatch` at [fitting.py:3339](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3339). The non-finite check comes afterward at [fitting.py:3353](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3353). This contradicts the explicit round-6 contract at [plan:133](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/superpowers/plans/2026-10-13-seal-1a-server.md:133). Check non-finite request values before constructing parameters. This is a verdict-classification defect, not an honest finite fit falsely marked stale.

2. **MAJOR — the docs overstate LA’s exemption from `mismatch`.**  
   [README:53](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/findings/seal-1a/README.md:53) says a curve-derived failure on an LA request reads `unconfirmed`, “never `mismatch`.” [CLAUDE.md:58](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/CLAUDE.md:58) and [plan:61](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/docs/superpowers/plans/2026-10-13-seal-1a-server.md:61) retain the same broad description.

   Reproduced: an honest LA response verifies `consistent`; changing only `statistics.rmse` by `+1` returns `mismatch`, check `statistics`. That behavior is correct: recorded-array relationships remain exact at [fitting.py:3523](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3523). Only the component and composite **evaluation identities** receive the exemption at [fitting.py:3478](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3478). Update those descriptions to match the round-2 fix notes.

Answers to the five questions:

1. **Honest responses falsely stale:** none found. The verifier suite covers all seven shapes, all background methods, all five optimisers, links, held values, bounds, starts, required-component checks and caller seeds ([tests:62](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/tests/test_seal_1a_verify.py:62)). Additional finite-bound and held-parameter cases across all five methods also verified consistently.
2. **False `consistent`:** none found within the numerical checks’ scope. Acceptance and uncertainty changes remaining consistent are expressly permitted by option (b), documented at [fitting.py:3278](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3278).
3. **HTTP 500:** no input-triggered example found. Internal verifier exceptions become `unconfirmed` at [fitting.py:3302](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:3302); the route nevertheless retains a final 500 fallback at [app.py:1417](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/app.py:1417).
4. **Docs:** inaccurate in the two ways above.
5. **Tolerance/second reading:** no new comparison tolerance or divergent numerical reading found. Equality is exact; shared helpers construct the request/model/background. The statistics’ existing floor is reproduced identically, not used as an acceptance tolerance ([fitting.py:2997](/Users/skyefortier/xps-app/.claude/worktrees/seal-1a-r3/fitting.py:2997)).

Validation: **123 tests passed** using an in-memory upload/session harness to preserve read-only operation; 25 additional honest fit/verification cases passed. The checked-in full-suite report still names `a71661e`, so it does not establish a full-suite pass at HEAD.

**VERDICT: NO-GO.**
