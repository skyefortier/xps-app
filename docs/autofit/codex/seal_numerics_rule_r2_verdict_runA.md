**NO-GO. The central server rule is fixed, but the open-page cache still has MAJOR correctness gaps. No BLOCKER found.**

1. **Round-1 findings, both runs**

| Finding | Status |
|---|---|
| Unreadable request always becomes `mismatch` | **Resolved for otherwise valid records.** Other numerics now produce `unconfirmed/numerics`. [app.py:1411](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1411) |
| Schema failures described as differing recomputations | **Partially resolved.** A reached `schema` failure stays `mismatch`, but earlier failures can hide malformed structure; see item 2. [fitting.py:3378](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3378) |
| Informational software fields untyped or missing | **Resolved.** Presence and types are checked, including rejecting integer checkout flags. [fitting.py:129](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:129) |
| Missing machine, OS, BLAS and asteval identity | **Addressed with a stated limit.** Added fields and backward compatibility are implemented; this explicitly remains a declared compatibility identity, not identical arithmetic. [fitting.py:53](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:53) |
| `_parse_int` escapes the digest | **Resolved.** The normaliser’s function closure includes it. [numerics_digest.py:100](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:100) |
| Wording/refactors force numerical version bumps | **Partially resolved.** Tested logging/raise wording is ignored; other wording still changes the digest. Equivalence entries avoid a mandatory bump. See item 3. |
| Verifier arithmetic escapes the digest — run B | **Still present, explicitly excluded.** This is a stated scope limit, not a numerical fix. [numerics_digest.py:38](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:38) |
| History can be rewritten | **Addressed conditionally.** Existing `main` entries must remain a prefix. Bootstrap and unavailable-`main` cases remain unenforced; the test skipped here because `main` has no manifest. [test_numerics_version.py:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:49) |
| Ineffective digest mutation tests | **Specific defects resolved.** Production digest, included docstrings, real statistics arithmetic and `_parse_int` are exercised. [test_numerics_version.py:61](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:61) |
| Open page retains verdicts across numerics changes | **Partially resolved; MAJOR gaps remain.** Ordinary completed verdicts invalidate correctly, but unreachable and multi-check cases do not. |

2. **Does the whole path implement the owner’s rule?**

For ordinary valid records, the server does: valid commit/checkout/environment differences do not gate confirmation; matching recomputation confirms under either identity; differing recomputation becomes `mismatch` under the same numerics and `unconfirmed/numerics` under other numerics. Existing impossible-check exceptions remain explicit. [fitting.py:3359](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3359)

The whole path does **not** yet satisfy it:

- **MAJOR — Auto-Fit can cache a mixed-numerics confirmation as current.** Its two checks are aggregated without requiring matching verifier identities. I reproduced the final-fit check replying under old numerics, followed by the anchor check under new numerics. The aggregate took the anchor’s `consistent` verdict and new software identity; `_cachedVerdict` accepted it. A subsequent background trigger issued no replacement check for the old-numerics result. Thus one required check can remain unconfirmed under the new numerics while the aggregate reads current. Preserve and validate the identity of **every** constituent check before caching confirmation. [index.html:9107](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9107), [index.html:9183](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9183)

- **MAJOR — a previous unreachable result suppresses the deployment recheck.** `_noteServerSoftware` calls `_ensureVerified` without retry; `_sealUnreachable` makes that return immediately. I reproduced **zero requests** after declaring new numerics, with the old verdict invalidated and the seal left unconfirmed/unreachable. Clear or version the unreachable marker when numerics change. [index.html:9081](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9081), [index.html:9196](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9196)

- **MINOR — schema precedence remains incomplete.** I reproduced `unconfirmed/numerics` for both an unreadable request paired with an `O` containing only valid software, and a record with malformed `individual_peaks` plus an earlier background difference. Neither becomes falsely confirmed, but both violate “a record not of a response’s form is mismatch whatever made it.” Structural validation must precede numerical classification. [app.py:1414](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:1414), [fitting.py:3478](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3478), [fitting.py:3497](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3497)

The page also discovers deployment changes only through a subsequent fit/check reply; an idle page has no independent discovery mechanism. That limitation is described in the implementation. [index.html:9068](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/templates/index.html:9068)

3. **Does the digest capture exactly fitting math; is equivalence sound?**

**No: it is a syntactic guard with explicit exclusions and manual equivalence decisions.**

A recomputed number can still change without changing the digest. In memory, doubling the verifier’s weights left the digest unchanged and made an honest seal return `mismatch/statistics` under unchanged numerics. The exclusion is deliberate and documented, but it prevents claiming coverage of all recomputation arithmetic. Shared numerical operations should be covered even when called by the verifier. [fitting.py:3483](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3483), [test_numerics_version.py:69](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:69)

**MINOR — wording exclusion remains incomplete.** Changing only the empty-peaks error text or the background’s nonfinite explanation changes the digest. These edits now require an equivalence entry rather than necessarily forcing a bump. Also, normalization blanks arguments to *all* `warnings` methods, including the behavioral `simplefilter("ignore")`, not just message text. [app.py:102](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/app.py:102), [fitting.py:1157](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:1157), [numerics_digest.py:87](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:87)

The equivalence mechanism is reasonable **as a reviewed exception supported by evidence**. Its automated enforcement establishes only a changed digest, unchanged version and nonempty explanation; it cannot establish numerical equivalence. A number-moving change accompanied by an incorrect equivalence explanation passes those rules. That assurance limit should remain explicit. [numerics_digest.py:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/scripts/numerics_digest.py:158), [test_numerics_version.py:36](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:36)

4. **Do the tests fail on the defects they name?**

The specific server and repaired digest cases are effective. I restored the old whole-software gate in memory: the deployment regression test failed. Disabling docstring stripping and omitting the helper closure likewise caused the corresponding mutation tests to fail. [test_seal_1a_verify.py:225](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_seal_1a_verify.py:225), [test_numerics_version.py:61](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_numerics_version.py:61)

**MINOR — the browser deployment test overstates its integration coverage.** It injects `_noteServerSoftware` directly, so it does not prove that real fit/check replies invoke the notification. It also covers neither unreachable markers nor mixed-numerics Auto-Fit replies. The schema test covers one early schema error, not schema precedence across combined failures. [test_browser_seal_step4.py:574](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_browser_seal_step4.py:574), [test_seal_1a_verify.py:289](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/test_seal_1a_verify.py:289)

5. **Other regressions and validation**

I found no change to fitted arithmetic in this diff. Under the new digest definition, `seal-1a-server`, `seal-1c-page` and HEAD all produce the manifest’s digest. The LA evaluation exception remains intact; I did not rerun the historical 1b population. [numerics_manifest.json:3](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/tests/fixtures/numerics_manifest.json:3), [fitting.py:3574](/Users/skyefortier/xps-app/.claude/worktrees/seal-numerics/fitting.py:3574)

Read-only validation: **18 pytest cases passed, one skipped; all 24 new server cases and 44 existing mutations passed through the real verification endpoint using an in-memory fit; all 100 tests in the changed JavaScript suites passed.** The cache counterexamples used the actual page functions. Full browser integration tests were inspected, not run. Checkout unchanged.

**VERDICT: NO-GO.**
