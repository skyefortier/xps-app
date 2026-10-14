**GO for this measurement unit, with MINOR corrections. No BLOCKER or MAJOR finding remains.** Reviewed HEAD `a11c8d0`, read-only.

I checked all eight v2 JSONL files: each contains the same 328 unique IDs. The retained raw records match the manifest, their index regenerates exactly, all recorded sizes reproduce, regenerated tabs/targets match their hashes, and rerunning the background twin reproduces its committed output byte-for-byte.

1. **Round-1 findings are resolved or explicitly bounded, with one residual generator issue.**

| Round-1 finding, combining both reviews | Round-2 status |
|---|---|
| Obsolete Voigt 0.3/free and missing `frontend_shape` | **Resolved for v2.** All 180 committed Voigt components are 0.5/fixed; all 865 committed specs carry `frontend_shape`. See [summary.txt:5](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/summary.txt:5). |
| Synthetic requests differ from the page, especially fixed LA m | **Explicit limit.** Missing indices, averaging defaults, numeric IDs, absent flags, free-0.3 pseudo-Voigt and held LA m are disclosed. See [README.md:19](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:19). |
| “LA fits are never current” | **Resolved.** The README correctly makes `unconfirmed` conditional on that verification’s evaluation difference; 54 LA records were consistent in all four settings. See [README.md:45](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:45). |
| Missing committed provenance | **Resolved.** Manifest, software digest, clean commit, run script and worker log are retained and agree with raw records. See [MANIFEST.md:8](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/MANIFEST.md:8). |
| Shaking does not prove alignment coverage; HTTP PID is client PID | **Explicit limits.** Both are stated accurately. See [README.md:29](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:29). |
| Partial size presented as complete seal/project increment | **Resolved by qualification.** Missing fields, separate compression and the arithmetic 30-fit extrapolation are explicit. See [README.md:81](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:81). |
| `shirley_linear` omitted from “every background” | **Explicit limit**, with separate parity-test coverage. See [README.md:72](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:72). |
| Universal “no honest fit is stale” claim | **Resolved.** Restricted to 1,312 observations. See [README.md:43](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:43). |
| Mixed-record verdict confused with evaluator failure | **Resolved.** The distinction and stable-component checks are explained. See [README.md:49](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:49). |
| Upper-middle values called medians | **Resolved.** Even-length samples average the two middle values. See [seal_1b_summarise.py:27](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_summarise.py:27). |
| Replay differences understated; “byte-identical” misleading | **Resolved for v2.** Actual starts changes and relative differences are reported, and sorted-JSON equality is qualified. See [README.md:114](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:114). |
| Generator can silently reuse historical targets | **Still present, MINOR for this reviewed run.** The documented v2 invocation overrides it correctly; see finding below. |

2. **The 202 committed records measure today’s page-built requests. The 126 synthetic records deliberately do not.**

I regenerated the targets from the committed projects and compared their complete requests and arrays with the raw records. They agree. The page’s converter supplies fixed-0.5 Voigt and `frontend_shape`; the measurement sends explicit background indices, endpoint averaging, Trust-Region, `n_perturb=3`, and the correct starts rule. The relevant page construction is at [index.html:7024](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:7024) and [index.html:9137](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/templates/index.html:9137); the measurement counterpart is [seal_1b_measure.py:71](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:71).

All raw R arrays equal O’s energy/count arrays exactly. Among committed records, **178 use three starts and 24 use zero**. Including synthetics gives 304/24.

The four verification settings are supported by the separate commands, JSONL settings/PIDs and four-worker log. They produce:

| Setting | Committed: consistent / unconfirmed | Synthetic: consistent / unconfirmed |
|---|---:|---:|
| Fresh 1 | 199 / 3 | 126 / 0 |
| Fresh 2 | 190 / 12 | 126 / 0 |
| Shaken | 199 / 3 | 126 / 0 |
| Gunicorn | 164 / 38 | 118 / 8 |

See [run.sh:9](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/run.sh:9), [gunicorn.log:4](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/gunicorn.log:4) and [summary.txt:14](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/summary.txt:14). Neither actual alignment coverage nor distribution across all workers is established, as disclosed.

3. **The summariser reproduces the numbers; exact text reproduction has a minor ordering defect.**

My initial invocation reproduced `summary.txt` byte-for-byte. Independent calculations confirm the true committed medians:

| Bytes | R | O |
|---|---:|---:|
| JSON | 9,607.5 | 52,704.5 |
| Gzip | 3,222 | 23,819 |

The combined-record medians and 30-fit arithmetic also agree with [summary.txt:41](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/summary.txt:41).

Replay classification is correct under the repository comparator: **200/202 committed and 121/126 synthetic pass its complete comparison; the remaining seven fail only within `starts.*`.** Their diagnostics are 84–129 characters, below the 400-character truncation boundary. The comparator accumulates differences across the response rather than stopping at the first failure ([fit_equality.py:262](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/tests/fit_equality.py:262)).

The seven are:

- Committed objective differences: [replay.jsonl:23](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:23), [replay.jsonl:158](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:158).
- Synthetic classification/count change, without a reported `n_converged` change: [replay.jsonl:238](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:238).
- Four synthetic objective differences: lines [276](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:276), [278](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:278), [280](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:280), [322](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/replay.jsonl:322).

The README’s numerical measurement claims are traceable and correct apart from the count wording below. I could inspect the separate parity coverage, but could not independently repeat its claimed **22/22** pass: the read-only environment prevents `dill` from finding a writable temporary directory during import.

4. **The substantive conclusions are supported within the stated limits.**

- **Q7 `{la_casaxps}`:** supported as the observed unstable evaluator set. All 64 unconfirmed results identify LA/components; all 884 verifications without LA are consistent. Stable components are checked before deferred LA failure ([fitting.py:3515](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/fitting.py:3515)). DS+G’s 72 consistent checks exercise nonzero FFT broadening, with appropriate platform/parameter limits.
- **Zero mismatch in 1,312:** exact; 1,248 consistent plus 64 unconfirmed ([summary.txt:38](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/v2/summary.txt:38)).
- **Background twin 328/328:** independently reproduced exactly, including window recovery and convergence. `shirley_linear` is separately included in the exact-zero parity assertion ([background_parity.test.js:82](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/tests/js/background_parity.test.js:82)).
- **Size:** accurately labelled partial.
- **1d recommendation:** supported. Fit reproduction includes success/certification and the comparator’s numerical standard, while starts evidence remains visibly reported ([README.md:129](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:129)). This is consistent with the approved measurement/replay scope ([design:1322](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md:1322)).

5. **Remaining findings—all MINOR:**

- **Summary text is nondeterministic.** With `PYTHONHASHSEED=1`, the two category dictionaries on summary line 40 reverse order. Counts remain identical, but the output no longer matches the recorded SHA. Sort categories before formatting the set-derived counters at [seal_1b_summarise.py:106](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_summarise.py:106).
- **Two README count descriptions need correction.** “Over six methods” should be **seven**: the combined corpus includes `smart_exp` as well as the six synthetic methods ([README.md:136](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:136)). The 304 three-start records are the **whole corpus**, although stated beneath the 202-committed-target bullet; that subset has 178 ([README.md:14](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/docs/findings/seal-1b/README.md:14)).
- **Generator defaults still permit the original mistake.** An unset `SEAL_1B_TARGETS` silently selects historical targets ([seal_1b_measure.py:42](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:42)). Require an explicit target path or validate its provenance. Also qualify the docstring’s assertion that shaking produces other alignments; only changed allocation history is demonstrated ([seal_1b_measure.py:14](/Users/skyefortier/xps-app/.claude/worktrees/seal-1b/scripts/seal_1b_measure.py:14)). Neither issue invalidates the documented v2 execution.

VERDICT: GO
