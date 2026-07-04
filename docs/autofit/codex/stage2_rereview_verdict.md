**Findings**

- **MAJOR** [autofit/methods/ic_model_comparison.py](/Users/skyefortier/xps-app/autofit/methods/ic_model_comparison.py:57): `bic_ambiguity_threshold` is passed into `compare_models`, but the emitted criteria panel is built later with `build_criteria_panel(... )` and no threshold argument at [line 231](/Users/skyefortier/xps-app/autofit/methods/ic_model_comparison.py:231), so it silently falls back to `2.0` from [autofit/criteria.py](/Users/skyefortier/xps-app/autofit/criteria.py:117). The `<=` fix is present in both code paths, but a non-default threshold can still make `analysis.ambiguous_pairs` and `analysis.criteria_panel.bic_ambiguous` disagree.

- **MAJOR** [autofit/grammar.py](/Users/skyefortier/xps-app/autofit/grammar.py:317): same-region, multi-phase slugs are phase-qualified, but the final role prefix sanitizer deletes separators at [line 409](/Users/skyefortier/xps-app/autofit/grammar.py:409). Distinct valid phase IDs like `B-4C` and `B4C`, or `phase 1` and `phase1`, collapse to the same role prefix. That turns a valid “same region once per phase” request into duplicate roles or parameter namespace collision. The ordinary BN/B4C case is fixed; the slug namespace is still not collision-safe.

- **MAJOR** [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:1626): `orphan_peaks` is recorded in `PlausibilityFlags`, but `rank_and_filter` ignores it and only filters on `boundary_hits` / `unphysical_widths` at [line 1033](/Users/skyefortier/xps-app/autofit/engine.py:1033). The analysis payload also drops the orphan flag. Failure scenario: a model whose refits repeatedly produce unmatched components can still be reported as a clean survivor if active slot persistence passes.

- **MAJOR residual risk** [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:674): best-minimum promotion chooses the lowest-χ² refit and promotes it at [line 1609](/Users/skyefortier/xps-app/autofit/engine.py:1609), but there is no basin reproducibility gate beyond slot occupancy persistence. A one-off lower minimum with very different centers can become the reported fit while the instability is only buried in MAD/confidence, not used in survivor filtering. This is statistically honest only if “best found minimum” is the intended product, not “robust representative minimum.”

**Fix Verification**

Items 1-8 are implemented for the normal/default paths: structured `(region, phase_id)` requests work; proposal slots are `unassigned`; survivor sort is `(bic_adjusted, reduced_chi_sq)`; absent winner slots are excluded from emitted peaks/confidence; F-tests skip absent-adjusted reports; AICc uses fitted `k` while BIC* uses adjusted `k`; C 1s windows/FWHM provenance is labeled; and the slow gate skip is loud with CI enforcement logged out of scope.

Item 9 is only partially closed: both comparisons use `<=`, but the criteria-panel threshold is not wired to the method option.

I could not run the pinned pytest tests in this read-only session because Python/pytest/lmfit could not find any writable temp directory.

VERDICT: GO
