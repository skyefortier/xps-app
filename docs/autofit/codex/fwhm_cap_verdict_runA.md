# FWHM-cap unit review — run A

Date: 2026-07-08. Commit: 1beec0d. VERDICT: NO-GO.
Prompt: docs/autofit/codex/fwhm_cap_review_prompt.txt

```
1. MAJOR, [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:577): Proposed-slot shape pegs are not rejected despite the commit/docs saying every non-`fwhm@max` peg still rejects. Concrete failing scenario: an isolated out-of-grammar residual peak shaped like an endpoint pseudo-Voigt case drives `proposed_peak_0:gl_ratio` to `0` or `1`, with center/amplitude/FWHM inside bounds and FWHM below `2.0`; `_detect_boundary_hits` suppresses `gl_ratio`, so `_attempt_proposal` sees `pr.boundary_hits == []`, accepts the proposal, and it can survive cleanly. Fix: for proposal slots, detect finite-bound hits without `_BOUNDARY_EXCLUDED`, then allow only exactly `{spec.role}:fwhm@max`.

2. MINOR, [autofit/engine.py](/Users/skyefortier/xps-app/autofit/engine.py:2101): Bound-fixed promoted proposal reports lose proposal lineage. Concrete failing scenario: a width-capped `P1+prop` beats a clean residual-flagged base strongly enough for decisive override; `_bound_fixed_refit` emits `P1+prop+bfix` with `winner_unphysical_widths` and low-confidence text, but `proposed_peaks` is reset to `[]`, so `width_capped=True` is no longer attached to the winner row. Fix: copy `report.proposed_peaks` and `augmented_from` into the bound-fixed `ModelReport`.

VERDICT: NO-GO
```
