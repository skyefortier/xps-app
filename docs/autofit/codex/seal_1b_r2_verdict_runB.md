**No BLOCKER or MAJOR findings remain in the v2 measurement. Four MINOR issues remain.** Review was read-only.

I located the verbatim records and verified their manifest hash. Regenerated tabs, targets and index match exactly; all eight JSONL files contain the same 328 unique IDs. Every committed file digest matches. Recomputed sizes and all 328 background-twin rows also match.

1. **Round-1 findings: resolved or explicitly bounded, except the stale generator fallback.**

   | Finding from either round-1 review | Round-2 status |
   |---|---|
   | Obsolete Voigt parameters; missing `frontend_shape` | **Resolved.** All 180 Voigt components request 0.5 fixed; all 865 committed-target specs carry `frontend_shape`. Example: [records_index.jsonl:20](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/records_index.jsonl:20). |
   | Synthetic requests differ from the page, particularly fixed LA m | **Explicit limit.** Handwritten requests, omitted indices/flags/averaging, and all 36 synthetic LA components holding m=6 are disclosed. [README:19](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:19) |
   | “LA is never current”; universal “no honest fit is stale” | **Resolved.** Conclusions are corpus-bounded; LA can verify consistent. [README:43](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:43) |
   | Mixed-record verdicts confused with evaluator failures | **Resolved.** The distinction is explicit. [README:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:49) |
   | Insufficient preserved provenance; client/worker PID ambiguity; unproven alignment coverage | **Resolved/documented limits.** Manifest, index and logs preserve provenance; worker distribution and actual alignment coverage are expressly unmeasured. [MANIFEST:8](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/MANIFEST.md:8), [README:29](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:29) |
   | Partial size called complete seal/project growth | **Resolved.** Missing fields, separate compression and extrapolation are clearly identified. [README:81](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:81) |
   | Upper-middle values called medians | **Resolved.** Conventional medians are implemented and independently agree. [summariser:27](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_summarise.py:27) |
   | Missing `shirley_linear` coverage | **Explicit limit**, with separate parity-test coverage cited. [README:72](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:72) |
   | Replay differences understated; normalized JSON called verbatim bytes | **Resolved.** Current differences and normalization are accurately described. [README:114](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:114) |
   | DS+G evidence generalized beyond tested parameters/platform | **Explicit limit.** [README:51](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:51) |
   | Generator silently falls back to obsolete targets | **Still present—MINOR for this reviewed run.** See item 5. |

2. **The 202 committed targets measure today’s numerical page requests; the 126 synthetic records deliberately do not.**

   Regenerated targets match the manifest hash and every committed raw request’s peaks, background and data arrays. The page’s Voigt conversion, window indices, averaging and starts rule match the generator. All uploaded arrays equal the response arrays. Trust-Region is the disclosed default-method assumption. [page:7044](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:7044), [page:9137](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:9137), [generator:71](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:71)

   The four settings are supported by their JSONL flags/PIDs, separate process invocations and gunicorn log:

   | Setting | Committed consistent / unconfirmed | Synthetic consistent / unconfirmed |
   |---|---:|---:|
   | Fresh 1 | 199 / 3 | 126 / 0 |
   | Fresh 2 | 190 / 12 | 126 / 0 |
   | Shaken | 199 / 3 | 126 / 0 |
   | Gunicorn | 164 / 38 | 118 / 8 |

   Shaking retains allocations during verification; it does not measure alignment. Gunicorn genuinely started four workers, but serving-worker distribution is unknown. [generator:129](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:129), [run.sh:9](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/run.sh:9), [gunicorn.log:4](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/gunicorn.log:4)

3. **The summary reproduces numerically, but not reliably byte-for-byte.**

   All reported measurement totals, size tables and replay magnitudes agree with the JSONL. Independently calculated committed medians are **9,607.5 / 52,704.5 B raw**, **3,222 / 23,819 B gzip**; paired R+O medians are **62,323 / 27,035 B**. These are true medians.

   All seven replay diagnostics are complete—84–129 characters, below the 400-character cap—and contain only `starts.*` differences. The comparator accumulates all detected differences and still compares `certificate.certified`. Thus **321/328 pass the complete comparator; 328/328 reproduce the fit when starts evidence is separated**. [comparator:233](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/tests/fit_equality.py:233), [summary:53](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/summary.txt:53)

   The changed classification really is 3→2 “same,” 0→1 “not better,” with no convergence-count difference. The largest reported relative objective difference is approximately **6.87×10⁻⁴**. [replay.jsonl:238](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:238), [replay.jsonl:322](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:322)

   Literally “every README number” is not correct: the background-method count and the placement of the starts count need correction below.

4. **The principal conclusions are supported within the stated scope.**

   - **Q7:** `{la_casaxps}` is the observed unstable set. All 64 unconfirmed checks identify LA components; all 884 checks without LA are consistent. Stable components are checked before returning an LA-related unconfirmed result. [summary:38](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/summary.txt:38), [verifier:3526](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:3526)
   - **Zero mismatches in 1,312 verifications:** correct.
   - **Background twin 328/328:** independently reproduced exactly. `shirley_linear` is separately covered by exact-equality parity assertions. [parity test:82](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/tests/js/background_parity.test.js:82)
   - **Size:** appropriately labelled partial.
   - **1d recommendation:** supported—compare fit values, success and certification while visibly reporting starts changes separately. This fits the approved replay role in [V6.22:1324](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1324).

   I could not independently reproduce the claimed 22/22 parity-test execution: the command fails during dependency initialization because this read-only sandbox provides no writable temporary directory. The assertions were inspected; the complete record-based background rerun succeeded.

5. **Remaining MINOR findings:**

   - **Summary output order is nondeterministic.** Set iteration controls dictionary ordering at [summariser:106](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_summarise.py:106). `PYTHONHASHSEED=1` changes summary line 40; seeds 0, 2 and 3 matched exactly. Sort these counts.
   - **The obsolete-target fallback remains.** Without `SEAL_1B_TARGETS`, [generator:44](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:44) still selects the historical investigation’s targets. The preserved v2 command overrides it correctly. Require an explicit path or fail clearly.
   - **Two corpus-count wording errors.** [README:136](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:136) says six methods; the combined corpus contains **seven**, including `smart_exp`. At [README:14](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:14), **304** starts-enabled records is the whole-corpus count under a committed-target bullet; the committed count is **178**, plus 24 disabled.
   - **DS+G causation is stated too strongly.** [README:125](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:125) concludes the replay differences “come from somewhere else.” Verification tested evaluations at recorded fitted parameters, not every intermediate optimizer evaluation. Say no DS+G instability was observed at the tested parameters and the replay cause was not isolated.

VERDICT: GO
