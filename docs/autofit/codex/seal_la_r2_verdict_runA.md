The round-1 MAJOR is resolved. I found **no BLOCKER or MAJOR implementation defect**. One documentation MINOR remains.

- **MINOR — The cross-machine explanation is incorrect.** The README says confirmation requires the original software identity and attributes cross-machine differences exclusively to optimizer arithmetic. Neither follows from the implementation or evidence. The verifier returns CONSISTENT whenever recomputation matches; differing numerics turn a failed recomputation into UNCONFIRMED. In this review, **53/107 xps2 records confirmed on the i9**, while 54 returned UNCONFIRMED. **55/214 xps2 LA component curves** differed when evaluated here from their recorded parameters. Correct the identity explanation and remove the claim excluding LA evaluation as a contributor to cross-machine fit differences. This does not invalidate repeatability within either tested environment. [README.md:77](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/README.md:77), [README.md:90](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/README.md:90), [fitting.py:3639](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/fitting.py:3639), [seal_la_matrix.py:146](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/scripts/seal_la_matrix.py:146).

1. **Acceptance matrix: satisfied. Original MINORs: addressed.**

   I audited the retained raw records against seal 1b: all four datasets contain exactly its **107 LA requests—89 committed, 18 synthetic—with only session IDs changed**. Every R/O hash matches committed provenance; every fit returned HTTP 200 and success true. Each setting contains all 107 unique IDs. The verification procedure matches seal 1b’s harness. [seal_la_matrix.py:66](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/scripts/seal_la_matrix.py:66), [seal_la_matrix.py:81](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/scripts/seal_la_matrix.py:81).

   Independently recounted results:

   | Dataset | Consistent | Unconfirmed |
   |---|---:|---:|
   | Before, i9 | 307/428 | 121, affecting 70 records |
   | After, i9 | 428/428 | 0 |
   | Final LA code, i9 | 428/428 | 0 |
   | Final LA code, xps2 | 428/428 | 0 |

   The before/after experiment uses the same i9 setup. xps2 supplies the additional **after-side** experiment requested by the owner, with its documented two-worker configuration. It is not a before/after experiment on both machines. [run.sh:14](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/matrix/run.sh:14), [run_xps2.sh:13](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/matrix/xps2/run_xps2.sh:13).

   The stale LA allowance, documentation, even-kernel coverage, held-m coverage, and hardcoded numerics assertion are corrected. Browser provenance limits are disclosed; the replacement timing script checks every response. [envelope_identity.py:62](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/envelope_identity.py:62), [CLAUDE.md:58](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/CLAUDE.md:58), [test_la_deterministic.py:46](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/test_la_deterministic.py:46), [test_seal_1a_server.py:124](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/test_seal_1a_server.py:124), [README.md:107](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/README.md:107), [seal_la_fit_time.py:35](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/scripts/seal_la_fit_time.py:35).

2. **Tap-range equivalence: correct for every positive grid/kernel length.**

   Tap `t` touches indices `[t, t+N−1]`; the returned window is `[off, off+N−1]`. Their intersection is nonempty exactly when `off−N+1 ≤ t ≤ off+N−1`, clipped to `[0,K−1]`. Those are the implemented bounds. Every returned element therefore receives exactly the original products, in the original order, starting from the same zero. Both parity cases and kernels longer than the grid retain the old offset. The equivalence entry correctly avoids another numerics bump. [fitting.py:1642](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/fitting.py:1642), [numerics_manifest.json:19](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/fixtures/numerics_manifest.json:19).

3. **Repeatability: supported within each tested environment, with bounded scope.**

   I found no remaining demonstrated process-dependent evaluation in the reviewed path. Fixed association removes the observed convolution instability; it does not make `power`, `exp`, reductions, backgrounds, or other evaluators universally platform-independent. Verification recomputes arrays and derived quantities, not optimization. The README’s bounded-evidence qualification is appropriate. [README.md:16](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/README.md:16), [fitting.py:3603](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/fitting.py:3603).

   xps2’s provenance records the requested Python 3.12.3, pinned libraries, Linux/OpenBLAS environment, clean commit, and local refitting. That meets the owner’s request. Cross-machine confirmation is conditional on exact recomputation, as explained in the MINOR above. [xps2/provenance.json:2](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/matrix/xps2/provenance.json:2).

4. **Tests: meaningful and mutation-sensitive.**

   The exact length/offset, 4,000-case byte-equivalence, alignment, and process tests passed. Restoring only `np.convolve` produced **four digests across five processes**, versus one with the fix. Both inward off-by-one tap-bound mutations failed the equivalence test. All seven free/held-m cases passed four fresh verifications each, including held `m=499`. [test_la_deterministic.py:66](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/test_la_deterministic.py:66), [test_la_deterministic.py:112](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/test_la_deterministic.py:112), [test_la_deterministic.py:128](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/test_la_deterministic.py:128).

Read-only validation: **24 focused tests passed, one skipped**, plus the 28 fresh-process verifications using stdin in place of temporary files. All 107 final i9 records also verified under current HEAD. Temporary-directory fixtures were blocked by the sandbox; I did not rerun the full suite or remote servers.

**VERDICT: GO**
