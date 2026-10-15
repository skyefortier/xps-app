**NO-GO. Two MAJOR page issues remain, plus MINOR schema and test gaps. No BLOCKER found.**

The round-2 findings, combining both runs, resolve as follows:

| Finding | Round-3 status |
|---|---|
| Mixed-numerics Auto-Fit checks become one confirmation | **Partially resolved.** `_verdictEntry` prevents mixed confirmation, but staged commits still accept mixed answers. [index.html:9112](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9112) |
| Earlier unreachable result suppresses deployment recheck | **Resolved for installed seals.** Unreachable marks are epoch-specific, and deployment discovery forces replacement attempts. [index.html:9102](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9102) |
| Delayed old-deployment reply restores old numerics | **Resolved for requests sent before the epoch changed.** A separate multiple-worker issue remains below. [index.html:9096](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9096) |
| Schema failures hidden by earlier request/numerical failures | **Partially resolved.** Validation moved earlier, but its coverage and precedence remain incomplete. [fitting.py:150](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:150) |
| Message normalization blanks `warnings.simplefilter` behavior | **Resolved.** Only `warnings.warn` receives message normalization. [numerics_digest.py:96](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:96) |
| Message wording still counts | **Partially resolved.** `_err` wording is excluded; recorded background reasons deliberately count. Helper-generated exception wording still counts, as discussed below. |
| Deployment test bypasses response discovery | **Resolved.** Tests now discover changes through check and fit replies. [test_browser_seal_step4.py:587](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:587), [657](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:657) |
| Recording test validates asteval/BLAS values against themselves | **Unchanged MINOR coverage limitation.** [test_fit_recording.py:59](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_fit_recording.py:59) |

**The page does not yet satisfy the complete deployment rule.**

- **MAJOR — mixed-numerics staged transactions commit.** `_verdictEntry` converts mixed answers into an `unconfirmed/numerics` entry tagged with the **current** numerics. `_commitStaged` checks that aggregate tag, rather than requiring every answer to have the current identity. I reproduced sequential staged checks answered under A and B: `_commitStaged` returned `committed: true`. It does not falsely confirm, but violates the explicit “never committing” requirement and caches an unconfirmed aggregate that suppresses ordinary background retries. Validate the constituent answers before aggregation. [index.html:9116](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9116), [index.html:9188](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9188), [index.html:9235](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9235)

- **MAJOR — multiple workers can revive an earlier epoch’s confirmation.** I reproduced: cache a consistent A answer; discover B; let the resulting recheck reach an A worker. Because that request was sent during the current epoch, A is accepted as another deployment. While its replacement check remains pending, the original cached A confirmation becomes readable again. Cached verdicts contain a numerics key but no epoch; old answers are therefore invalidated only temporarily. Alternating workers can also repeatedly supersede each other’s checks. Epoch-tagging cached answers would prevent resurrection; the implementation still needs an explicit treatment of concurrent differing worker identities. [index.html:9095](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9095), [index.html:9123](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9123)

For a single A → B transition, installed-seal attempts are correctly superseded, old unreachable marks cease applying, and delayed A replies cannot move the page backward. Staged checks retain their detached input snapshots and transaction ownership checks. However, deployment enumeration covers installed tab seals, not detached history records; those need verification upon installation. [index.html:9102](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9102), [index.html:9173](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9173)

This remains the step-4 manager, whose consumers are explicitly unwired in this checkout; it is not evidence of completed UI integration. Idle-page deployment discovery also still requires another reply. [test_browser_seal_step4.py:1](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:1)

**The server’s form check is improved but incomplete.**

**MINOR — independently malformed response structure still escapes schema precedence.** `response_form_failure` accepts:

- A component whose `params.area` is missing.
- A component whose `shape` is an object or whose `id` is an array.
- A background verdict whose `converged` value is `"yes"`.

I reproduced each returning `unconfirmed/numerics` when paired with an unreadable request and other numerics. The function validates existing parameter entries without requiring area, omits component identity/shape types, and checks only that the background verdict is a dictionary. [fitting.py:174](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:174), [fitting.py:183](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:183)

**MINOR — route ordering is still not unconditional.** The saved-data nonfinite return precedes response-form validation. A malformed `O.statistics.rmse` paired with an infinite saved energy returns `unconfirmed/non_finite`, not `mismatch/schema`. [app.py:1405](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1405)

Within `fitting.verify_fit`, form validation correctly precedes numerics classification. I found no honest-record rejection introduced by it: 21 honest-record cases covering lineshapes, backgrounds, local methods, links and held parameters passed. Valid informational software differences still do not gate confirmation. [fitting.py:3413](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3413)

**The digest implements a declared syntax boundary, not exact semantic detection of mathematical changes.**

The specific `_err` and warning-filter defects are repaired, and counting background-verdict reasons agrees with the revised definition. I confirmed identical digests at `seal-1a-server`, `seal-1c-page` and HEAD.

The previous limits remain:

- Verifier arithmetic is deliberately excluded; the test explicitly permits changing recomputation weights without changing the digest. [test_numerics_version.py:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:69)
- The app closure follows function definitions, not arbitrary referenced module data. [numerics_digest.py:109](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:109)
- Changing `_precision_words` wording still changes the digest. This fits the narrowed call-site definition but leaves the broader wording-only complaint unresolved. Equivalence can avoid a version bump. [fitting.py:750](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:750)
- Equivalence is a reviewed assertion: tests require a nonempty explanation, not proof that no number moves. History protection remains conditional on `main` having a manifest. [test_numerics_version.py:36](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:36)

**The tests catch their narrow cases, but not all claimed guarantees.**

The three new form-precedence cases all failed when I disabled `response_form_failure` in memory. The digest mutations exercise production code and distinguish the specified wording, behavior and recorded-text edits.

**MINOR — the “mixed answers never committing” coverage is insufficient.** Its commit test uses one check with a modified identity, not Auto-Fit’s two answers under different identities. It therefore passes despite the reproduced mixed-commit defect. The mixed-confirmation portion tests `_verdictEntry` directly rather than the complete asynchronous aggregation path. No test covers A → B → A cache resurrection. [test_browser_seal_step4.py:676](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:676)

Read-only validation: **100 JavaScript tests passed; 14 digest tests passed, one skipped; 78 server cases passed through the real verification endpoint with an in-memory fit; 21 additional honest-record cases passed.** Full browser integration tests were inspected, not executed. No fitted-arithmetic regression was found; the historical 1b corpus was not rerun. Checkout unchanged.

VERDICT: NO-GO
