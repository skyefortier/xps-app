**Findings**

1. [autofit/grammar.py:186](/Users/skyefortier/xps-app/autofit/grammar.py:186), [autofit/grammar.py:223](/Users/skyefortier/xps-app/autofit/grammar.py:223), [autofit/grammar.py:337](/Users/skyefortier/xps-app/autofit/grammar.py:337)  
**BLOCKER**: `target_phases` is keyed only by region, so the resolver cannot express two phase-scoped grammars for the same region in one co-fit window. A BN/B4C sample with both phases contributing `B 1s` can only select BN or B4C, not both; trying duplicate `"B 1s"` requests would also collide because joint role prefixes use only the region slug.  
**Fix**: accept structured region requests such as `{region, phase_id}` or return all phase-scoped slot families for ambiguous regions, and prefix composed roles by both region and phase.

2. [autofit/engine.py:1092](/Users/skyefortier/xps-app/autofit/engine.py:1092)  
**BLOCKER**: residual-proposal slots copy `region` and `phase_id` from `base.slots[0]`. In a U 4f + N 1s co-fit, a residual peak in the N 1s overlap can be tagged as the U phase if U is first, causing phase leakage and wrong downstream interpretation.  
**Fix**: infer the proposal’s region/phase from the diagnostic/proposal window, or mark proposals as phase-unassigned until explicitly adjudicated.

3. [autofit/engine.py:934](/Users/skyefortier/xps-app/autofit/engine.py:934), [autofit/methods/ic_model_comparison.py:81](/Users/skyefortier/xps-app/autofit/methods/ic_model_comparison.py:81)  
**MAJOR**: survivors are ranked by `(reduced_chi_sq, bic_adjusted)`, so the returned winner is not BIC* ranked even though the spec says BIC* is the ranking default. A larger model with a tiny χ² improvement but worse BIC* can become the emitted fit.  
**Fix**: sort by `bic_adjusted` first, with χ² only as a diagnostic/tie-breaker.

4. [autofit/methods/ic_model_comparison.py:110](/Users/skyefortier/xps-app/autofit/methods/ic_model_comparison.py:110), [autofit/methods/ic_model_comparison.py:114](/Users/skyefortier/xps-app/autofit/methods/ic_model_comparison.py:114)  
**MAJOR**: absent slots are subtracted from BIC*/persistence, but `_peaks_from_report()` still emits every slot as an output peak. A candidate can win because a contaminant was deemed absent, then still write that absent contaminant as a fitted peak.  
**Fix**: omit absent-slot roles from returned peaks/confidence, or emit them only as explicitly inactive diagnostics.

5. [autofit/criteria.py:60](/Users/skyefortier/xps-app/autofit/criteria.py:60), [autofit/criteria.py:148](/Users/skyefortier/xps-app/autofit/criteria.py:148)  
**MAJOR**: F-tests do not exclude reports with `absent_slots`, even though the spec says absent-slot-adjusted models are outside F-test validity. The panel can report an F-test on a larger model whose BIC* parameter count was arithmetically reduced.  
**Fix**: skip F-tests when either report has absent slots, or run true reduced-model refits before testing.

6. [autofit/criteria.py:115](/Users/skyefortier/xps-app/autofit/criteria.py:115)  
**MAJOR**: AICc is computed with `adjusted_n_params`, effectively making it an unlabelled AICc* and suppressing the intended BIC*/AICc disagreement signal.  
**Fix**: compute AICc from actual fitted `k`, or explicitly label/use a reduced-refit AICc* convention.

7. [autofit/regions/c1s.py:38](/Users/skyefortier/xps-app/autofit/regions/c1s.py:38), [autofit/regions/c1s.py:51](/Users/skyefortier/xps-app/autofit/regions/c1s.py:51)  
**MAJOR**: several physical C 1s BE/FWHM constants are not lit-cited or explicitly marked UNVERIFIED: `C1S_WINDOWS` and `FWHM_RANGE_GRAPHITIC` in particular. These constants gate candidate admissibility.  
**Fix**: cite each physical window/range or mark it `UNVERIFIED`/calibration-only inline.

8. [tests/autofit/test_c1s_parity_gate.py:38](/Users/skyefortier/xps-app/tests/autofit/test_c1s_parity_gate.py:38), [tests/autofit/test_browser_schema_roundtrip.py:31](/Users/skyefortier/xps-app/tests/autofit/test_browser_schema_roundtrip.py:31)  
**MAJOR**: required Stage 2 gates can silently skip. The C 1s parity gate requires `RUN_AUTOFIT_GATE=1`, and schema round-trip skips when browser tooling is unavailable. A default CI run can pass without enforcing the two mandatory gates.  
**Fix**: make these required in CI or add non-skipping CI markers/jobs for Stage 2.

9. [autofit/criteria.py:142](/Users/skyefortier/xps-app/autofit/criteria.py:142), [autofit/engine.py:940](/Users/skyefortier/xps-app/autofit/engine.py:940)  
**MINOR**: BIC ambiguity threshold semantics differ: criteria panel uses `< τ`, engine ambiguous pairs use `<= τ`. Exact-threshold cases disagree.  
**Fix**: use one convention.

Manual-fit path check: `app.py` and `fitting.py` are unchanged vs `main`; I did not find a silent `/api/fit` or `fitting.run_fit` code change. Template diff is confined to the intended `analysis` save/load additions and keeps v3.

VERDICT: NO-GO (blockers: same-region multi-phase resolver cannot co-fit both phase contributions; residual proposals leak the first slot’s phase/region in joint fits)