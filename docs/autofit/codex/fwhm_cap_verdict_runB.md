# FWHM-cap unit review — run B

Date: 2026-07-08. Commit: 1beec0d. VERDICT: NO-GO.
Prompt: docs/autofit/codex/fwhm_cap_review_prompt.txt

```
1. BLOCKER, `autofit/engine.py:1944`: after `run_stability_analysis()` promotes `stability.best_outcome`, `_attempt_proposal()` updates `primary` and the proposal’s fitted center/FWHM/amplitude, but never recomputes `pr.boundary_hits`, never reapplies the “only `{role}:fwhm@max` is allowed” split, and never refreshes `width_capped`. Concrete failing scenario: initial augmented fit for `proposed_peak_0` is clean and passes SNR/BIC; stability finds a lower-chi-square best outcome with `primary.boundary_hits == ["proposed_peak_0:center@min"]`, persistence `0.8`, and ΔBIC* `< -2`. The function accepts it at lines `1989-1996`, producing an accepted proposal with a spurious center wall that should still reject. The opposite stale-report case also exists: initial fit has no cap hit, stability best outcome moves `proposed_peak_0:fwhm@max`, and the final report is conditional via `boundary_hits`/`unphysical_widths` but `analysis.candidates[].proposed_peaks[].width_capped` remains false. Fix: immediately after the `best_outcome` promotion block, recompute `pr.boundary_hits` from the final `primary.boundary_hits`, rerun the spurious-hit rejection against the final outcome, and set `pr.width_capped = (pr.boundary_hits == [f"{spec.role}:fwhm@max"])`; add a unit test that monkeypatches stability to return a better proposed-slot `center@min` and expects rejection, plus one for a stability-only `fwhm@max` expecting `width_capped=True`.

VERDICT: NO-GO
```
