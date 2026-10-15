**The fresh verifier is substantially improved, but the open-page recheck remains incorrect across deployment races. Two MAJOR findings prevent GO. No BLOCKER found.**

1. **Round-1 findings: mostly resolved, with remaining cache and digest limitations.**

| Round-1 finding, combining both runs | Round-2 status |
|---|---|
| Unreadable request always becomes `mismatch` | **Resolved for request normalization failures:** other numerics now yields `unconfirmed/numerics`. [app.py:1411](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1411) |
| Schema failures described as differing recomputation | **Resolved in the exception handler**, but schema validation can still be bypassed by an earlier failure; see below. [fitting.py:3378](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3378) |
| Informational software fields missing or mistyped | **Resolved:** presence and types are checked; valid values do not gate confirmation. [fitting.py:130](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:130) |
| Missing machine, OS, BLAS and asteval identity | **Resolved as a declared compatibility identity.** It explicitly does not prove identical arithmetic; older records remain supported. [fitting.py:51](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:51) |
| `_parse_int` omitted from digest | **Resolved:** the app function closure includes it. [numerics_digest.py:100](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:100) |
| Wording and equivalent refactors force version changes | **Partially resolved:** tested inline messages are ignored; equivalence entries permit refactors without bumps. Other wording still changes the digest. |
| Historical entries can be rewritten | **Resolved conditionally:** history must preserve `main`’s prefix once its manifest exists. Bootstrap limitation is explicit; this check currently skips. [test_numerics_version.py:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:49) |
| Ineffective docstring/statistics tests and duplicate digest implementation | **Resolved:** included docstrings and real arithmetic mutations exercise production `math_digest`. [test_numerics_version.py:61](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:61) |
| Open page retains answers across numerics changes | **Partially resolved:** ordinary completed checks invalidate correctly, but deployment races and unreachable attempts remain incorrect. |
| Verifier arithmetic excluded from digest | **Retained as an explicit limit**, now pinned by a test changing recomputation weights without changing the digest. [test_numerics_version.py:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:69) |

2. **The whole path does not yet implement the owner’s rule.**

Fresh, readable verification correctly ignores commit/checkout/environment differences, recomputes before confirmation, and distinguishes numerical disagreement by declared numerics. I found no new server path confirming a differing required recomputation. [fitting.py:3359](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3359)

**MAJOR — a delayed reply can restore an obsolete server identity and its cached confirmation.** Every response unconditionally updates `_serverNumerics`. Meanwhile, a numerics-change notification calls `_ensureVerified`, which skips an existing attempt. I reproduced: start an old-numerics check; observe new numerics; receive the old check’s delayed reply. The page resets its identity to old numerics and accepts that old confirmation. No replacement check starts. The same trigger issues **zero requests** for a seal marked unreachable. Track deployment changes across attempts, and invalidate/retry affected attempts and unreachable markers. [index.html:9081](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9081), [index.html:9196](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9196)

**MAJOR — Auto-Fit’s aggregate cache does not establish that both checks used current numerics.** `_aggregateVerdicts` selects one response, and the cache stores only that response’s software. I reproduced two consistent answers from different numerics: the cache first becomes unusable with no attempt outstanding; a subsequent notification matching the selected answer makes it usable again **without rechecking the other fit**. Both required checks must carry compatible current identities before the aggregate can confirm. This also affects staged commits. [index.html:9107](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9107), [index.html:9155](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9155), [index.html:9183](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9183)

**MINOR — unconditional schema precedence is still overstated.** With other numerics, an unreadable request and string-valued `statistics.rmse`, the endpoint returns `unconfirmed/numerics`; it never validates the statistic. Thus “a malformed record is mismatch whatever numerics made it” is not universally implemented. Validate independently checkable response structure before request-dependent early exits, or document that precedence limit. [app.py:1416](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1416)

The page also discovers redeployment only upon another fit/check reply; an otherwise idle page has no detection mechanism. [index.html:9068](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9068)

3. **The digest is a useful syntactic guard, not exactly “changes to fitting math.”**

**MINOR — message normalization both misses wording and removes behavior.** In-memory mutations established:

- Changing only the empty-peaks `_err(...)` message changes the digest. So does `_precision_words(...)` wording. [app.py:102](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:102), [fitting.py:700](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:700)
- Changing `warnings.simplefilter("ignore")` to `"error"` leaves the digest unchanged. The transformer treats every `warnings.*` call like message text. I reproduced a lineshape evaluation returning `[0.0]` before that mutation and raising `RuntimeWarning` afterward. This changes execution behavior without detection. [numerics_digest.py:87](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:87), [fitting.py:261](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:261)

Number-changing **recomputation** edits can explicitly escape through the excluded verifier. The app closure also follows function definitions, not referenced module-level data, so it is not a general dependency closure.

Equivalence entries are reasonable **reviewed assertions**, but the tests establish only a nonempty reason, not equivalence or evidence. An incorrect equivalence claim can conceal a numerical change. Wording therefore need not force a version bump, but currently may require an unnecessary equivalence entry. [test_numerics_version.py:36](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:36)

4. **The tests are stronger, but not every claimed defect is covered.**

The deployment regression test is effective: I restored the old whole-software gate in memory and its assertions failed. The repaired digest mutations genuinely exercise their named behavior.

**MINOR — the open-page deployment test bypasses deployment discovery.** It calls `_noteServerSoftware` directly. Removing the notification calls from fit/check response handling would therefore escape this test. It also covers neither delayed replies, mixed-numerics Auto-Fit checks, nor previously unreachable seals. Drive discovery through an actual reply and add those cases. [test_browser_seal_step4.py:582](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:582)

The recording test checks presence/nonempty strings for asteval and BLAS, but compares their values with themselves; it does not verify accurate identity collection. [test_fit_recording.py:59](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_fit_recording.py:59)

5. **Regression assessment and validation.**

The cache failures above are the material remaining regressions. I confirmed identical production math digests at `seal-1a-server`, `seal-1c-page`, and HEAD. That supports unchanged covered fitting arithmetic; I did not rerun the 1b corpus or independently reproduce its historical counts.

Read-only validation completed: **11 digest tests passed, one skipped; 113 JavaScript tests passed; 25 server-test cases, 44 existing tamper cases, and five recording cases passed using in-memory execution.** Targeted JavaScript probes reproduced the cache failures. Full browser integration tests were inspected, not run. The checkout remains unchanged.

**VERDICT: NO-GO.**
