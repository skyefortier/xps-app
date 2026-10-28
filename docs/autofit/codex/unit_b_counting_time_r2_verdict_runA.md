The exact exclusions reproduce and withstand independent checks. Remaining problems are in the interpretation and documentation; I found no BLOCKER.

1. **MAJOR — The README still states an unrestricted exclusion.** [README.md:8](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:8) says “no common counting time makes the stored values whole counts,” omitting the tested ranges and error model.

   Concrete counterexample: for `1 UCl4-graphite …10spot.DATA/C1s Scan.VGD`, all 191 stored values satisfy `Fraction(y) * 2199023255552 ∈ integers` exactly. Reproduce by taking `T = max(Fraction(y).denominator for y in values)` and checking every product’s denominator. This enormous time has no established acquisition meaning, but demonstrates why the bounded qualification is essential. State that no common time **in the tested ranges, under the stated model** works.

2. **MAJOR — The correction-factor fix remains incomplete in the interpretation.** [README.md:317](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:317) still says counting noise is consistent “only if the corrections differ.” [counting-time.md:207](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:207) likewise says equal corrections predict a factor of ten without requiring equal `f`.

   The corrected equation constrains **`a/f`**, not `a` alone. Counterexample: use the same correction `a = 0.26`, with `f_high-resolution = 2` and `f_survey = 13`. Then:
   ```
   k_high-resolution = 0.26 / (2 × 0.2)  = 0.65
   k_survey          = 0.26 / (13 × 0.02) = 1.00
   ```
   This reproduces the approximate measured contrast with equal corrections. A correction ratio of approximately 0.15 requires an additional assumption of equal detector factors; estimator bias supplies another unresolved possibility.

3. **MAJOR — “Expected by chance: 2.75” is not established.** [noise_counting_time.py:285](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:285), [counting_time.txt:10](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting_time.txt:10), and [counting-time.md:167](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:167) treat a nominal Bonferroni limit as an expected rejection count. The headline at line 19 then concludes that the observed count “is what chance gives.”

   Bonferroni does not make each family’s rejection probability exactly 1%. There are **156,024 evaluated candidates**, so even granting calibrated candidate p-values for these tested families, the summed union-bound limit is:
   ```
   156024 × 0.01 / 1024 = 1.523671875
   ```
   That is an upper bound, not an expectation. Moreover, the document correctly acknowledges that the phase null is uncalibrated for these spectra, so neither number establishes their actual chance expectation.

   The across-file adjusted minimum **does correctly reproduce as 1**. Report that no candidate survives the stated global adjustment; remove the unsupported chance-count conclusion.

4. **MINOR — Hypothesized coefficient identities become established causes later.** [counting-time.md:176](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:176) says the files “record why” conversion fails and that both corrections have coefficients carried in the files. Section 1 correctly labels the unnamed blocks’ identities as hypotheses and identifies an external detector-signature file.

   The flags establish recorded correction settings; they do not establish the transformation responsible for the failed lattice test or identify embedded signature coefficients. A constant multiplicative correction, for example, preserves a lattice at a rescaled time. Keep this explanation hypothetical, including the similar wording at README line 120.

5. **MINOR — The channel-count VERIFIED assertion exceeds its check.** [counting-time.md:88](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:88) says no property holds “128 or any other channel count,” supported by finding no numeric property equal to 128. That check cannot establish the absence of another count or an encoded count. Narrow this to the actual observation and the absence of an identified channel-count property.

6. **MINOR — The generator’s introductory contract retains superseded claims.** [noise_counting_time.py:8](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:8) says every constraint is applied and any nonempty result lists admissible times. Its own deferred-constraint counterexamples contradict that description. Lines 12–14 also retain the unconditional exposure cap “whatever the detector does in parallel.” Update this introduction to match the corrected function contract and conditional physical interpretation.

Verification completed read-only:

- HEAD is `78b71ed`; its only difference from `ce16e21` is the review prompt.
- **12 tests passed** using `pytest -s -q -p no:cacheprovider`.
- Regenerated JSON matched structurally; regenerated TXT matched byte for byte.
- Independently verified both exclusion certificates for all **275 files**, including the **158/117** first/second-gap split.
- Checked the solver against **2,000 independent singleton-time oracle cases**, including negative values and rounding perturbations, and exercised deferred-constraint retry. No false exclusion or admissible result with outstanding constraints was found.
- Independently decoded every dictionary; all matched. Their code page is 1200, consistent with the implemented [MS-OLEPS DictionaryEntry layout](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-oleps/333959a3-a999-4eca-8627-48a224e63e77).
- Confirmed alignment arithmetic, coverage, controls, neighboring-c values, correction-property values, vector/I1 fixes, the olefile explanation, sidecar counts and energy-axis identity, and the **166 spectrum / 46 zero-shift / 120 nonzero-shift** census.

VERDICT: NO-GO
