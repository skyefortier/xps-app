The implementation looks correct, and I reproduced the cross-process improvement. **NO-GO for acceptance coverage:** the required 107-case, four-setting validation has been replaced with a narrower measurement.

Findings, ranked:

- **MAJOR — Required acceptance coverage is incomplete.** [PROGRESS.md:48](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/autofit/PROGRESS.md:48) requires the 107 seal-1b LA cases in all four settings. The submitted measurement covers 54 LA browser fits ([README.md:30](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/README.md:30)). Changing arithmetic justifies producing fresh records; it does not require dropping the original requests or settings. Regenerate those 107 cases and verify them in both fresh processes, shaken memory, and four-worker gunicorn.
- **MINOR — Measurement provenance is insufficiently recorded.** The output records tab names and states, but no server software identity, request/response digest, or server configuration ([measurement script:40](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/scripts/seal_la_confirm_measure.py:40)). The counts are independently checkable; the claimed identical server setup rests on the README.
- **MINOR — Current documentation still identifies LA as unstable.** [CLAUDE.md:58](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/CLAUDE.md:58) explicitly identifies LA in `NOT_BIT_STABLE_SHAPES`. Update that description and qualify the historical `np.convolve` account at [CLAUDE.md:518](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/CLAUDE.md:518).

No BLOCKER implementation defect found.

1. **Cause: yes, `np.convolve` is convincingly isolated. Exclusivity: bounded evidence, not a universal proof.**

   The diagnosis hashes base and kernel separately from convolution output ([isolation script:27](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/scripts/seal_la_isolate.py:27)). Independently, the new test workload produced **one digest across five fresh processes**; replacing only the helper with old `np.convolve` plus trim produced **five different digests**. NumPy’s [float64 dot implementation](https://raw.githubusercontent.com/numpy/numpy/v2.4.4/numpy/_core/src/multiarray/arraytypes.c.src) supports the BLAS attribution.

   I found no second demonstrated source in verification. However, LA still uses `power`, `exp`, and kernel summation ([fitting.py:1683](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/fitting.py:1683)); verification also recomputes backgrounds, areas, statistics, support, and other shapes, including DS+G’s FFT. The evidence does not prove all these operations stable across every platform. Optimizer reproducibility is separate: verification does not rerun optimization ([fitting.py:3548](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/fitting.py:3548)).

2. **Length and offset: correct for all positive grid/kernel lengths, including even/odd and kernel-longer-than-grid.**

   For `K ≤ N`, the offset is `floor((K−1)/2)`. Otherwise, NumPy’s initial offset is `floor((N−1)/2)`, followed by the old trim’s `floor((K−N)/2)`. The implementation matches this exactly ([fitting.py:1614](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/fitting.py:1614)). I additionally checked all **4,096 pairs with N,K = 1…64**, using integer-valued float64 inputs to make equality exact.

   Each output accumulates taps in increasing order, with separately materialized multiplication and addition ([fitting.py:1611](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/fitting.py:1611)). Alignment cannot change that order.

   **“Any machine state” is too strong.** Changing the hardware rounding mode changed this helper’s output bits in an isolated probe. The valid claim is reproducibility under the same normal floating-point environment, not immunity to altered rounding modes. I found no application code changing that environment.

3. **Emptying the set and bumping the version are technically appropriate, subject to completing acceptance.**

   The verifier retains the generic instability mechanism ([fitting.py:3805](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/fitting.py:3805)); the tests explicitly monkeypatch LA into it. I found no executable page logic hardcoding LA as unstable.

   The convolution changes fitting arithmetic, so `2026-10-15` is justified. The manifest matches, and the numerical-version tests passed. `NOT_BIT_STABLE_SHAPES` and verification code are excluded from the fitting-math digest ([numerics_digest.py:42](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/scripts/numerics_digest.py:42)).

4. **The reported counts are correct; the tests detect the old failure; the fixture changes are legitimate.**

   I independently counted both JSON files: identical 121 tab identities, no recorded errors or unsealed results, five re-checks each.

   | Metric | Before | After |
   |---|---:|---:|
   | LA current after Run Fit | 37/54 | 54/54 |
   | LA current re-checks | 190/270 | 270/270 |
   | Non-LA current after Run Fit | 67/67 | 67/67 |
   | Non-LA current re-checks | 335/335 | 335/335 |

   Thus **17 initially unconfirmed fits and 80 unconfirmed re-check outcomes disappear in this measurement**. This does not establish conversion of all original seal-1b records.

   The mutation check above confirms the cross-process regression detects old arithmetic on this machine. All 12 fresh-process verifications of three newly generated fits passed.

   Both fixture changes preserve a real one-ulp component mutation while selecting a point where the **summed model remains unchanged**. They retain exact component-level assertions, including identifying the later stable Gaussian mismatch ([test:467](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/test_seal_1a_verify.py:467), [test:582](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/tests/test_seal_1a_verify.py:582)). They are not weakened.

5. **Speed: acceptable on the measured workloads, with limited whole-fit evidence.**

   My convolution timings at 450 points were approximately **0.30 ms at 119 taps** and **2.18 ms at the actual maximum, 1,167 taps**. The reported whole-fit median increase, 1.16 → 1.38 seconds, is reasonable ([README.md:48](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/docs/findings/seal-la/README.md:48)).

   That 12-fit benchmark is limited: its script neither checks response success nor preserves timings and identities in this unit ([timing script:18](/Users/skyefortier/xps-app/.claude/worktrees/seal-la/scripts/seal_la_fit_time.py:18)). It does not establish worst-case fit latency.

Read-only validation completed: **23 focused tests passed, one skipped**, plus the independent process, mutation, parity, and timing probes. Browser measurements were audited from committed artifacts, not rerun.

**VERDICT: NO-GO.**
