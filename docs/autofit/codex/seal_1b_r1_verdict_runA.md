The headline counts reproduce, but the corpus does **not** satisfy its stated “current page’s request” contract. **One MAJOR finding prevents approval; no BLOCKER found.** Review was read-only.

1. **MAJOR — Historical Voigt specs materially change 90 measured models.**  
   `page_request()` copies `t["specs"]` from an absolute path into an older investigation’s targets; it never rebuilds them using today’s page converter ([seal_1b_measure.py:35](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:35), [line 65](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:65)). In the retained raw records, the 180 frontend-labelled Voigt components across 90 targets all start at `gl_ratio=0.3`: 171 free, nine fixed. Today’s page sends **0.5, fixed** ([index.html:7044](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:7044)).

   Example: target `a82157575b35`, indexed at [records_index.jsonl:20](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/records_index.jsonl:20), has two free-0.3 satellite components in [raw records:20](/private/tmp/claude-501/-Users-skyefortier-xps-app/892cab71-a3bf-4f7b-8318-f3125bb6ba72/scratchpad/seal1b/final/records.jsonl:20). All 865 committed-target specs also omit today’s `frontend_shape` field ([index.html:7026](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:7026)).

   Consequently, the replay fraction and LA mixed-model results describe historical requests, not precisely what Run Fit now sends. Regenerate the targets through the current converter and rerun the affected measurements.

2. **MINOR — The size estimate measures only part of the designed seal.**  
   The generator measures `{request, energies, counts}` plus O ([seal_1b_measure.py:84](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:84), [line 176](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:176)). The design additionally requires `idx`, `ccShift`, `roi`, `pageModel`, `context0`, `producer`, and D ([design:723](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:723)). “A 30-tab project gains about 2 MB” should be labelled a partial-record estimate. Separate gzip sizes also do not directly measure incremental `.proj.zip` size.

3. **MINOR — Some evidence and scope are overstated.**  
   “Every background method” omits `shirley_linear`, which saved projects can still restore and fit ([generator:91](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:91), [page:2021](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:2021)). Existing parity tests cover it, but these 328 records do not ([background_parity.test.js:82](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/tests/js/background_parity.test.js:82)). Likewise, “no honest fit is ever called stale” exceeds the measured statement: **zero mismatches in these 1,312 checks**.

4. **MINOR — Replay wording needs qualification.**  
   The nine starts-only classifications are correct, but one includes `n_converged: 3 → 2`, and DS+G’s largest reported not-better objective difference is approximately **2.12×10⁻⁵ relative**, not merely a few 10⁻⁷ ([replay.jsonl:236](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/replay.jsonl:236), [line 280](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/replay.jsonl:280)). “Byte-identical” means sorted JSON equality **after restoring the original `seed_source`**, not identical verbatim responses ([generator:166](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:166)).

The answers to the requested checks are:

**1. Generator fidelity and execution conditions**

- **Real route/full precision: yes.** Recording uploads float representations through `/api/upload`, then calls the actual `/api/fit` route. All 328 retained records have R’s arrays exactly equal to O’s energy/count arrays. This matches the page’s full-precision numerical upload, though not necessarily identical CSV text ([generator:78](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:78), [page:6995](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:6995)).
- **Exact page request: no**, because of finding 1. Synthetic requests also omit fields the page explicitly sends, including window indices, most endpoint averages, and explicit peak flags. Their defaults are numerically meaningful, but they are handcrafted API requests.
- **Fresh/shaken/HTTP processes: supported.** The retained [run script:6](/private/tmp/claude-501/-Users-skyefortier-xps-app/892cab71-a3bf-4f7b-8318-f3125bb6ba72/scratchpad/seal1b/run_final.sh:6) launches separate recording and verification commands. Fresh verifier PIDs are 73705/73778; shaken is 73808. Shaking really allocates and retains random-sized arrays between checks ([generator:129](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:129)); it does not establish particular alignment coverage.
- **Four-worker gunicorn: supported by retained logs.** [gunicorn.log:4](/private/tmp/claude-501/-Users-skyefortier-xps-app/892cab71-a3bf-4f7b-8318-f3125bb6ba72/scratchpad/seal1b/final/gunicorn.log:4) records four workers. HTTP verification therefore used a different process from production. The JSONL’s PID 73948 is the **HTTP client’s** PID, not the serving worker; it does not prove every worker handled checks.
- **Clean commit: supported for this run.** All 328 raw O records identify `db50327…`, `git_dirty=false`, and one environment. Verification compares the complete software identity before numerical checks ([fitting.py:3305](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:3305)). However, the committed index omits that identity, and the resumable generators do not enforce a clean, single-commit run. Preserve the run manifest/log evidence with the findings.
- **Replay standard and seed: correct.** It calls `tests/fit_equality.py`, supplies O’s recorded seed, and removes only the expected `seed_source` distinction before comparison ([generator:152](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:152)). The comparator’s uncertainty/history exclusions are the repository’s existing standard.

**2. Numbers against the JSONL**

I ran the summariser with the repository virtualenv’s Python. Every file has 328 unique IDs, and all ID sets agree. The index reports 328 HTTP 200/successful fits.

Verification totals match exactly; entries below are **consistent / unconfirmed**:

| Setting | Committed | Synthetic |
|---|---:|---:|
| Fresh 1 | 175 / 27 | 126 / 0 |
| Fresh 2 | 177 / 25 | 126 / 0 |
| Shaken | 179 / 23 | 126 / 0 |
| Gunicorn | 168 / 34 | 119 / 7 |

Normalizing frontend labels to backend evaluators gives these **record-level** counts:

| Lineshape present | Fresh 1 | Fresh 2 | Shaken | Gunicorn |
|---|---:|---:|---:|---:|
| Gaussian | 43/0 | 43/0 | 43/0 | 43/0 |
| Lorentzian | 18/0 | 18/0 | 18/0 | 18/0 |
| Pseudo-Voigt/GL | 174/27 | 176/25 | 178/23 | 167/34 |
| Asymmetric GL | 126/0 | 126/0 | 126/0 | 125/1 |
| DS | 18/0 | 18/0 | 18/0 | 18/0 |
| DS+G | 18/0 | 18/0 | 18/0 | 18/0 |
| LA | 80/27 | 82/25 | 84/23 | 66/41 |

The GL/asymmetric-GL unconfirmed rows contain LA; their failure reasons identify LA. For example, [verify_gunicorn.jsonl:61](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/verify_gunicorn.jsonl:61). Thus “every other lineshape verifies consistent” should distinguish evaluator success from the enclosing record’s verdict.

I reran the background twin against the retained raw records: **all 328 output rows exactly match the committed JSONL**, including convergence and window recovery. Totals are Shirley 90, Smart 130, smart_exp 24, and Tougaard/linear/none/manual 21 each.

Size totals also reproduce exactly:

| Bytes | R | O |
|---|---:|---:|
| Raw total | 2,245,548 | 11,180,628 |
| Gzip total | 759,379 | 5,055,760 |
| Raw maximum | 15,375 | 76,740 |

The README’s rounded medians agree. Technically, [summariser:47](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_summarise.py:47) selects the upper middle observation; conventional medians are R/O raw **9,458.5/52,704.5** and gzip **3,198.5/23,817.5** bytes.

Replay totals are exactly **196/202** committed and **121/126** synthetic reproduced; normalized JSON-identical counts are **134/86**. All 11 diagnostic strings are shorter than the generator’s 400-character truncation limit. They support **nine starts-only differences**, one objective difference of **3.31×10⁻⁷ relative**, and one amplitude difference of **0.716%** ([replay.jsonl:60](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/replay.jsonl:60), [line 62](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/replay.jsonl:62)).

**3. Conclusions**

- **Q7:** `{la_casaxps}` is supported as the **observed unstable set**. All seven backend evaluators are exercised ([fitting.py:1471](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:1471)). DS+G’s 18 fits genuinely exercise FFT broadening; their fitted `m_gauss` values exceed the no-convolution threshold. Their 72 successful verifications support the bounded claim, not universal stability across parameters/platforms. Replay optimizer differences do not contradict evaluator stability.
- **No mismatch:** exactly true for this corpus.
- **Exact background binding:** supported on the tested records. The twin correctly converts end-exclusive indices to edge text, uses blank bounds for whole-window requests, and converts manual anchor pairs into the page’s `{x,y}` representation ([twin:36](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_background_twin.js:36)). This is a valid numerical adapter; it does not recover the original form text.
- **1d recommendation:** supported. Judge fit reproduction separately from search evidence, while still reporting convergence-count and alternative-solution changes. Regenerate current-page models before treating this corpus’s reproduction fraction as the current application’s measured rate.

The supplementary Python-backed parity tests could not initialize under the read-only sandbox because a dependency requires a writable temporary directory. The summariser, raw-record audits, and complete 328-record JavaScript background rerun succeeded.

**VERDICT: NO-GO.**
