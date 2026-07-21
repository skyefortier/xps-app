# Find Peaks math-first architecture — Step 1 RECHECK, Run A

Recheck of commit 47bf77b ("fix(autofit): apply Skye's dispositions on
step-1 Codex review findings"), against the original NO-GO/NO-GO review of
854c40a (see `find_peaks_step1_verdict_run{A,B}.md`).

## Recheck Judgments

1. **Run A finding 1 / D0 bound leak: verified as ruled acceptable.** No guard was added: `PoolFeature.fwhm_est` still comes straight from detected feature width at [autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:878), and `build_detection_candidate` still sizes `hi_w` as `2.5 * width` at [autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:543) and [autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:560). The architecture step-6 obligation is substantive: it names the direct D0 path, the `~2.5x` bound scaling, the ceiling-chasing exposure, neighbor absorption, and the k+1/model-comparison remedy at [docs/autofit/find-peaks-math-first-architecture.md](/Users/skyefortier/xps-verify/docs/autofit/find-peaks-math-first-architecture.md:87). The rewritten stress-test docstring is not laundered; it gives Skye's architectural rationale, not just tie mechanics, at [tests/autofit/test_stress_honesty.py](/Users/skyefortier/xps-verify/tests/autofit/test_stress_honesty.py:145).

2. **Run B finding 1 / `fwhm_init` optimizer-start claim: mostly verified, but one stale active docstring remains.** `_preseed_augmented` still does not read `spec.fwhm_init`; it constructs slots from `center_init` plus fixed `PROPOSAL_FWHM_MIN/MAX` at [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:1891). The only actual `spec.fwhm_init` optimizer initialization remains the proposal path at [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:2150). The three requested correction sites now state the true behavior: [autofit/candidates.py](/Users/skyefortier/xps-verify/autofit/candidates.py:679), [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:2633), and [docs/autofit/find-peaks-math-first-architecture.md](/Users/skyefortier/xps-verify/docs/autofit/find-peaks-math-first-architecture.md:79).

3. **False-positive guard widening: not verified.** The arithmetic claim is not inflated: `8% / 0.67% ~= 11.9x`, and the test now covers 5 ROI sizes. Hard-step omission is now explicit and reasoned at [tests/autofit/test_cwt_width_ceiling.py](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:212). But the assertion is still aggregate-only, so it can pass a double-digit regression in the named sloped/sigmoid risk classes.

4. **Two minor fixes: verified.** The real main-peak test now has a meaningful ceiling-chase guard, `0.3 < fwhm_est < 0.9 * ceiling`; if this feature started chasing the ROI ceiling, it would fail. The `cwt_scale_range_ev` direction is correct: the public ceiling is the same `hi` used to generate scales, and later `ceil()`/margin filtering can only remove usable top-rung cases, not create a detector-resolvable scale above the reported ceiling.

5. **Regression/scope check: verified except findings below.** `git show --stat 47bf77b` shows exactly the six requested files. `autofit/candidates.py` and `autofit/engine.py` diffs are comments/docstrings only; no guards, clipping, branches, or functional code were added.

## Findings

1. **MAJOR** [tests/autofit/test_cwt_width_ceiling.py](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:258): the false-positive guard can still miss the named regression because it asserts only aggregate FP rate across flat+slope+sigmoid. Concrete scenario: 5 sizes * 40 draws * 2 risky backgrounds = 400 sloped/sigmoid trials. If slope and sigmoid both regress to 10% FP across all sizes, aggregate is `40/600 = 6.67%`, passing the `<=8%` assertion. Even 12% in slope+sigmoid gives `48/600 = 8.0%` and passes because the check is inclusive. This does not actually catch the example risk in the prompt.

2. **MINOR** [tests/autofit/test_cwt_width_ceiling.py](/Users/skyefortier/xps-verify/tests/autofit/test_cwt_width_ceiling.py:12): the module docstring still says the `build_candidate_pool` `fwhm_init` clip is "the starting estimate handed to the optimizer." That is the same false claim the comment-only fix was meant to retire for the preseed path.

VERDICT: NO-GO

## Claude's disposition (2026-07-21)

Both findings fixed in the next commit:
- MAJOR: added per-background-kind assertions (5% each) alongside the
  existing 8% aggregate, grounded in a fresh per-kind measurement using
  the test's own exact seeds (flat 0.5%, slope 0%, sigmoid 0% across 200
  trials/kind) -- this directly catches the exact "slope+sigmoid regress,
  flat stays clean" scenario Run A constructed.
- MINOR: fixed the stale module docstring occurrence; confirmed via
  repo-wide grep that no other ACTIVE (non-historical-record) occurrence
  of the overclaim remains.
