# Find Peaks math-first architecture — Step 1 SECOND RECHECK, Run A

Focused recheck of commit f183a7e (fixes the 2 findings from the first
recheck's Run A NO-GO). See `find_peaks_step1_recheck_verdict_runA.md` for
the findings being verified here.

(1) Fixed. The test now tracks `per_kind_fp` and `per_kind_total` separately at [test_cwt_width_ceiling.py](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:252), keeps the aggregate `<= 0.08` check at [line 276](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:276), and adds independent per-kind `<= 0.05` assertions at [line 285](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:285).

Arithmetic check: 200 trials/kind. If flat stays clean and slope/sigmoid regress to 10%, that is `20/200 = 10%` for each risky kind, so both fail the new `5%` per-kind bound even though aggregate is `40/600 = 6.67%`. At 12%, each risky kind is `24/200 = 12%`, also failing per-kind; aggregate is `48/600 = 8.0%`, which would still pass the old inclusive aggregate check. The new assertion catches the prior failure scenario. The tolerance is justified in the docstring by measured baseline from the exact seeds: flat 0.5%, slope 0%, sigmoid 0% across 200 trials/kind. A 5% bound is 10 observed false positives out of 200, giving headroom while still catching double-digit regressions.

(2) Fixed. The stale module docstring now says the value reaches diagnostics only and is not `_preseed_augmented`'s optimizer starting guess. Repo-wide grep found no live surviving overclaim. Active-code hits in autofit/candidates.py and autofit/engine.py are explicit corrections. The architecture doc hit is a struck-through correction plus explanatory ruling. PROGRESS and codex verdict hits are historical records, not live executable-context claims.

Final sanity check passed: `git show --stat f183a7e` shows only `tests/autofit/test_cwt_width_ceiling.py`, `docs/autofit/PROGRESS.md`, and three files under `docs/autofit/codex/`. No `autofit/*.py` production code changed.

Findings: None.

VERDICT: GO
