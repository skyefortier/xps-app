**NO-GO. Two MAJOR gaps remain: mixed-numerics staged transactions can commit, and heterogeneous workers can cause an endless recheck cycle. No BLOCKER found.**

**1. Round-2 findings, both runs**

| Finding | Round-3 status |
|---|---|
| Auto-Fit combines different numerics into one confirmation | **Resolved for confirmation:** `_verdictEntry` returns unconfirmed for mixed answers. **Staged commit remains incorrect**, detailed below. [index.html:9112](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9112) |
| Previous unreachable result suppresses deployment recheck | **Resolved:** unreachable marks are epoch-specific, and deployment discovery forces replacement checks. [index.html:9102](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9102) |
| Delayed old-deployment reply restores old numerics/confirmation | **Resolved for requests sent before the epoch change:** their differing replies cannot move the identity back; installed attempts are superseded. [index.html:9096](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9096) |
| Structural failures hidden by request/numerics failures | **Partially resolved; MINOR remains:** the new precheck runs early, but misses independently checkable structure. See answer 3. |
| Message wording counted; `warnings.simplefilter` blanked | **Partially resolved:** `_err` wording is ignored and `simplefilter` behavior counts. Helper-generated error wording still counts. Record-contained reason text now deliberately counts. [numerics_digest.py:93](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:93) |
| Deployment test directly calls `_noteServerSoftware` | **Resolved:** discovery now goes through check and fit replies. Mixed-transaction coverage remains insufficient. [test_browser_seal_step4.py:587](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:587), [test_browser_seal_step4.py:657](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:657) |
| Recording test compares asteval/BLAS values with themselves | **Unchanged coverage limitation:** presence/nonempty strings are tested, accurate collection is not. [test_fit_recording.py:59](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_fit_recording.py:59) |

The inherited verifier-arithmetic exclusion and conditional history protection also remain explicit limitations, discussed below.

**2. End-to-end deployment behavior**

**MAJOR — mixed-numerics staged transactions still commit.** I reproduced sequential staged checks answered under A and B, followed by `_commitStaged` returning:

```json
{"committed":true,"verdict":{"state":"unconfirmed","check":"numerics"}}
```

The mixed-answer entry receives the **current** numerics key, so checking that aggregate key against current numerics cannot reject the mixture. Additionally, an outdated answer paired with an unreachable outcome commits because `agg.unreachable` bypasses validation altogether. The guard must inspect every constituent outcome before consuming the transaction; unreachable outcomes also need epoch provenance. This reproducer does **not** falsely confirm, but violates the required commit boundary. [index.html:9116](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9116), [index.html:9185](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9185)

**MAJOR — different workers can cause unbounded rechecking.** Each current-epoch reply declaring different numerics immediately starts replacement checks for every installed seal. If successive requests alternate between workers A and B, every replacement becomes another “deployment.” My bounded probe reached **13 requests and 12 epoch changes, with no cached answer**, before deliberately withholding further replies. There is no retry bound or stable unconfirmed state for this condition. [index.html:9091](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9091)

For a deployment that settles on B, the ordinary installed-seal path now works: old caches stop applying, unreachable seals retry, replacement attempts supersede old attempts, and delayed A replies cannot restore A. I reproduced these cases using the actual page functions. Detached staged checks preserve their snapshots and transaction ownership, but their mixed/outdated outcomes encounter the commit defect above. [index.html:9173](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9173), [index.html:9205](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9205)

An idle page still discovers deployment only through a subsequent fit/check reply.

**3. Server form and ordering**

**MINOR — form validation remains incomplete.** These malformed records pass `response_form_failure`:

- Component `id` is an object.
- Component `shape` is a number.
- Component parameters omit `area`.
- Background verdict’s `converged` is text.

With another numerics identity and an earlier background disagreement, all four returned `unconfirmed/numerics` in my endpoint probes. The checker validates parameter entries only when present, omits component ID/shape types, and checks the background verdict only as a dictionary. [fitting.py:174](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:174), [fitting.py:183](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:183)

Ordering is correct before request normalization and numerics classification, but not universally: nonfinite request data return before response-form validation. A malformed statistic paired with infinite request counts returned `unconfirmed/non_finite`. [app.py:1405](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1405), [app.py:1413](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1413)

I found no new rejection of an honest record in the exercised cases.

**4. Digest and equivalence**

The repaired message-call handling matches the narrower definition: `warnings.simplefilter` counts, `_err` wording does not, and background reason text counts. All three revisions produce the manifest digest.

It remains a syntactic guard with deliberate exclusions:

- Verifier arithmetic can change without changing the digest; a test explicitly requires this. [test_numerics_version.py:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:69)
- The app closure follows functions, not module-level data. Changing `MAX_N_PERTURB` remains invisible. [numerics_digest.py:109](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:109)
- **MINOR, retained wording limitation:** changing only `_precision_words` wording changes the digest. An equivalence entry avoids a version bump, but the wording exclusion is not complete. [fitting.py:750](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:750)

Equivalence is sound as a **reviewed assertion supported by evidence**; automation checks only a nonempty explanation. History protection remains conditional on `main` having a manifest. [test_numerics_version.py:36](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:36)

**5. Tests and regressions**

**MINOR — the mixed-answer test does not test a mixed staged commit.** It tests `_verdictEntry` directly, then changes the key of one single-fit answer. Both assertions pass despite the two-answer commit defect. Add a real staged A/B pair and outdated-plus-unreachable case. [test_browser_seal_step4.py:676](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:676)

Read-only validation completed:

- **14 digest tests passed; one history test skipped.**
- **113 JavaScript tests passed.**
- **84 server cases and 24 honest-record cases passed**, using in-memory fits through the real verification endpoint.
- All **three new form-precedence cases failed** when the precheck was removed in memory.
- Targeted page-function probes reproduced both MAJOR findings and verified the ordinary epoch fixes.

Full browser integration tests and the historical 1b corpus were not run. Checkout unchanged.

**VERDICT: NO-GO.**
