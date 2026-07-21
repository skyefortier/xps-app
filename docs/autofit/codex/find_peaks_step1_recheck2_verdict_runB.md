# Find Peaks math-first architecture — Step 1 SECOND RECHECK, Run B

Focused recheck of commit f183a7e (fixes the 2 findings from the first
recheck's Run A NO-GO). See `find_peaks_step1_recheck_verdict_runA.md` for
the findings being verified here.

1. The MAJOR is fixed. The test now tracks `per_kind_fp` and `per_kind_total` separately at [tests/autofit/test_cwt_width_ceiling.py](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:251), keeps the aggregate `<= 0.08` assertion at line 276, and adds an independent per-kind `<= 0.05` assertion at line 287.

Arithmetic check: each kind has 5 ROI sizes x 40 draws = 200 trials. If flat stays clean and slope/sigmoid regress to 10%, then slope = 20/200 = 10% and sigmoid = 20/200 = 10%; each fails the new <=5% bound. At 12%, each is 24/200 = 12%; also fails. The old aggregate would have allowed 10% (40/600 = 6.67%) and even 12% exactly (48/600 = 8.0%, inclusive), so this closes the prior loophole.

The per-kind tolerance is justified in the test docstring by an explicit measurement using the exact test seeds: flat 0.5%, slope 0%, sigmoid 0% across 200 trials/kind. With 200 trials/kind, the 5% bound allows 10 FPs per kind versus a measured worst observed 1 FP, giving the stated headroom while still catching double-digit regressions.

2. The MINOR is fixed. The module docstring no longer says the stale phrase; it now explicitly says `fwhm_init` reaches diagnostics only and is NOT the optimizer starting guess for grammar-augmented preseed slots.

Repo grep found no live standing overclaim. Active code hits in autofit/candidates.py and autofit/engine.py are corrective "NOT the optimizer's starting guess" comments. The top-level architecture doc keeps the phrase only as struck-through/corrected text. PROGRESS.md hits are narrative history of what was wrong and what was fixed.

Final sanity check: `git show --stat f183a7e` shows exactly `tests/autofit/test_cwt_width_ceiling.py`, `docs/autofit/PROGRESS.md`, and three new files under `docs/autofit/codex/`. `git diff --name-only f183a7e^ f183a7e -- 'autofit/*.py'` returned no files, confirming zero production code changes.

Findings: none.

VERDICT: GO
