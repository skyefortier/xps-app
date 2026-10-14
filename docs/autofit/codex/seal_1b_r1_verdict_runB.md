**NO-GO: the reported counts are reproducible, but the corpus does not consistently represent the current page’s requests.**

I reran the summariser with `python3`, checked all JSONL files, located the uncommitted raw records, and reran the background twin: **328/328 passed**. No files were changed by this review.

The review began at `4328e75`. During it, HEAD advanced to `a46cd3f`, adding target rebuilding support. The findings JSONL remained unchanged, so that commit does not resolve the measurement problem below.

1. **MAJOR — the committed-target measurements use obsolete Voigt models.**

   The recording generator copies `t["specs"]` directly into the request. In the actual raw records, the 90 targets labelled Voigt contain 180 pseudo-Voigt components starting at `gl_ratio: 0.3`: **171 free and nine fixed**. Today’s page sends **0.5, fixed**, for Voigt. This changes the fitted model, parameter count, optimisation and replay behaviour—not merely request metadata. See [request construction](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:64), [current Voigt builder](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:7044), and [raw record 20](/private/tmp/claude-501/-Users-skyefortier-xps-app/892cab71-a3bf-4f7b-8318-f3125bb6ba72/scratchpad/seal1b/final/records.jsonl:20).

   Consequently, the README’s “page’s request” claim and its page-facing replay fraction need corrected measurements. The new environment-variable override still falls back to the obsolete targets when unset. [Source](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:35)

   The synthetic requests also bypass the page builder. They omit explicit background indices/default averaging, use numeric peak IDs, omit `frontend_shape` and lock fields, and notably omit `fix_m`: the backend therefore **holds synthetic LA’s m fixed**, whereas an unlocked page peak explicitly sends `fix_m: false`. All 36 synthetic LA components have fixed m in the raw responses. See [synthetic specs](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:110), [page LA mapping](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:7087), and [backend default](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:1701).

2. **MAJOR — “an LA fit is … never current” contradicts the measured behaviour.**

   The verifier returns `unconfirmed` for LA **when an evaluation identity fails**, not whenever LA is present. For example, the first LA/Voigt record is `consistent` in fresh process 1. Across that setting, 62 committed LA fits and all 18 synthetic LA fits are consistent. The README must distinguish the unstable-shape set from the verdict on a particular verification. See [README claim](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:34), [JSONL counterexample](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/verify_fresh_1.jsonl:20), and [conditional verifier behaviour](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:3526).

3. **MINOR — run provenance is real locally, but insufficiently preserved in the committed evidence.**

   The raw records all report the same software identity: clean `db50327`, Python 3.12.13, NumPy 2.4.4, SciPy 1.17.1 and lmfit 1.3.4. Software includes commit and cleanliness, and verification requires equality of the whole identity before checking components. Thus the clean-commit condition is supported by the recovered records and the verification results. [Identity implementation](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:84), [verification gate](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:3305)

   The two local verification runs have distinct PIDs, 73705 and 73778; shake uses 73808 and genuinely allocates random-sized arrays between checks. This perturbs allocation history, although it does not measure actual evaluator-buffer alignment. [Generator](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:122)

   The recovered gunicorn log shows four workers, 73875–73878, serving port 5153. HTTP verification therefore uses a separate server process. However, JSONL’s `pid: 73948` is the **HTTP client’s PID**, not the verifying worker’s; it cannot establish worker distribution. Neither that log nor the software identity is retained in the committed index. Preserve a small run manifest and distinguish client/verifier PID. [Logged PID](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:139), [worker log](/private/tmp/claude-501/-Users-skyefortier-xps-app/892cab71-a3bf-4f7b-8318-f3125bb6ba72/scratchpad/seal1b/final/gunicorn.log:4)

**The numerical audit passes, with these qualifications.**

Every JSONL contains 328 unique IDs, and all eight files contain the same ID set. The index reports 328 HTTP-200, successful fits. The verification counts exactly match the README:

| Setting | Committed: consistent / unconfirmed | Synthetic: consistent / unconfirmed |
|---|---:|---:|
| Fresh 1 | 175 / 27 | 126 / 0 |
| Fresh 2 | 177 / 25 | 126 / 0 |
| Shake | 179 / 23 | 126 / 0 |
| Gunicorn | 168 / 34 | 119 / 7 |

There are **zero mismatches in 1,312 recorded checks**. Every unconfirmed reason identifies LA and `components`. “No honest fit is ever called stale” should be restricted to these observations; it is not a universal guarantee. [README table and conclusion](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:22)

All seven registered backend evaluators are represented:

| Evaluator | Committed fits containing it | Synthetic |
|---|---:|---:|
| Gaussian | 25 | 18 |
| Lorentzian | 0 | 18 |
| Pseudo-Voigt | 183 | 18 |
| Asymmetric GL | 108 | 18 |
| DS | 0 | 18 |
| DS+G | 0 | 18 |
| LA | 89 | 18 |

These are overlapping fit-presence counts. Mixed LA/Voigt fits can be unconfirmed even though their pseudo-Voigt evaluations passed. The summariser reports frontend labels and backend identifiers separately. [Summariser](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_summarise.py:35), [registered evaluators](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:1471)

**Q7:** `{la_casaxps}` is supported as the **observed unstable set in this experiment**. DS+G contributes 72 successful verifications, and its fitted Gaussian widths are approximately 0.63–1.30 eV, so these genuinely exercise the FFT branch. That is useful bounded evidence, not proof across every grid, parameter regime or environment. No backend lineshape is wholly untested; the current page’s fixed-0.5 Voigt configuration is not represented correctly.

**Background:** the corrected twin uses the page’s actual functions, reconstructs explicit windows from round-trip edge text, handles omitted windows with blank fields, and converts manual anchors correctly. I reproduced all 328 successful, exact comparisons:

- Shirley 90; Smart 130; smart_exp 24.
- Tougaard, linear, none and manual: 21 each.

The adapter is numerically faithful for these records, including whole-window and manual cases. The page itself always sends explicit indices and averaging, so the synthetic requests are equivalent defaults rather than literal page requests. [Twin adapter](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_background_twin.js:33), [page payload](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:9149)

**MINOR:** “every background method” overstates this corpus: legacy `shirley_linear` remains fit-capable but has no row. Existing parity tests cover it; cite those separately or add measurement cases before claiming complete coverage. [Legacy method](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:2018), [existing parity coverage](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/tests/js/background_parity.test.js:82)

**Sizes:** the raw records reproduce every stored size. The summariser outputs:

| Bytes | Reported median | Maximum | Total |
|---|---:|---:|---:|
| R JSON | 9,459 | 15,375 | 2,245,548 |
| O JSON | 52,707 | 76,740 | 11,180,628 |
| R gzip | 3,199 | 5,126 | 759,379 |
| O gzip | 23,838 | 35,131 | 5,055,760 |

The README’s rounded figures agree. **MINOR:** the summariser selects the upper middle item instead of averaging the two middle values; true medians are 9,458.5, 52,704.5, 3,198.5 and 23,817.5. The 30-tab estimate is an extrapolation from these R/O records, not a measured complete seal/project archive. [Size calculation](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_summarise.py:43)

**Replay:** the generator correctly reuploads full-precision arrays, supplies `O.random_seed`, and invokes the repository’s `assert_same_fit`, removing only the expected `seed_source` difference beforehand. The seed drives the same random streams. [Replay implementation](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:144), [seed streams](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:2648)

The counts are exactly **196/202 committed**, **121/126 synthetic**, and **317/328 overall**. The 134 and 86 “byte-identical” counts actually mean equal sorted JSON after normalising `seed_source`, not identical original response bytes.

The **9 + 1 + 1 classification is supported**: all eleven diagnostic strings are shorter than the generator’s truncation limit. Nine contain only starts-evidence differences; Scan_1 has approximately 3.31×10⁻⁷ relative objective disagreement; Scan_3 has approximately 0.716% amplitude disagreement. [Objective case](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/replay.jsonl:60), [amplitude case](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/replay.jsonl:62)

**MINOR:** the nine are described too narrowly. One DS+G case changes converged-start count from three to two, and another not-better objective differs by about 2.12×10⁻⁵ relatively—not merely a few 10⁻⁷. [Convergence difference](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/replay.jsonl:236), [larger difference](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/replay.jsonl:280)

Separating reproduced fit values from search evidence is a sound recommendation for 1d, provided success/certification remain checked and changed search evidence remains visible. The page-facing reproduction fraction must first be remeasured with current requests.

**VERDICT: NO-GO.**
