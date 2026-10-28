Reviewed **`ce16e21`**. All locations below refer to that commit; external uncommitted edits appeared during review and are excluded from this verdict. I changed nothing.

**Verification:** all 12 tests pass. Regenerating all 275 files reproduced the committed JSON and text exactly in 18.9 seconds. An independent dictionary walk agrees with the decoder and Microsoft’s [DictionaryEntry specification](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-oleps/333959a3-a999-4eca-8627-48a224e63e77). Another 600 exact interval comparisons and 750 forced-deferral cases found no false exclusions or false admissible results.

No BLOCKER found. The numerical exclusion results hold, but these reporting issues remain:

1. **MAJOR — The claimed chance expectation is unsupported.**  
   [counting-time.md:167](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:167), also line 19; [noise_counting_time.py:285](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:285); `counting_time.txt:10`.

   Bonferroni provides an upper bound on false-positive probability; it does not make each file’s rejection probability exactly 1%. Moreover, only **156,024** candidates were evaluated. Even treating the approximate p-values as calibrated, the union-bound expectation is at most:
   ```
   156024 × 0.01 / 1024 = 1.523671875
   ```
   It is not 2.75. The document also acknowledges that the null is uncalibrated for these spectra, so “what chance gives” is not established.

   The global calculation itself is correct: the smallest untruncated adjusted value is **1.4695654**, hence **1 after clipping**. Report that no candidate survives the global correction; do not claim that chance explains the two per-file flags.

2. **MAJOR — Differing corrections are still incorrectly presented as necessary.**  
   [README.md:317](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:317); [counting-time.md:206](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:206).

   The corrected equation `k·d·s = a/f` is right, but the README still says counting noise is consistent with the measurement “only if the corrections differ.” The document likewise says equal corrections predict a factor of 10, without requiring equal `f`.

   Counterexample to that inference:
   ```
   a_high = a_survey = 0.26
   f_high = 2; f_survey = 13
   k_high   = 0.26 / (2 × 0.2)   = 0.65
   k_survey = 0.26 / (13 × 0.02) = 1.00
   ```
   This gives the observed approximate k ratio and exactly the 6.5 ratio in `k·d·s`, with **identical corrections**. Differences in `a`, `f`, or estimator bias remain possible.

3. **MAJOR — Correction metadata is promoted into a demonstrated cause.**  
   [counting-time.md:176](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:176), also lines 20 and 186; [README.md:120](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:120).

   “The files record why” the conversion fails, with “each” correction’s coefficients present, exceeds the evidence. §1 correctly labels the coefficient-block identities as hypotheses, and the signature path points to an uncommitted external file. Later prose silently upgrades those interpretations.

   Correction flags alone also do not prove destruction of a lattice: a constant correction preserves one at a rescaled time:
   ```
   y = a·N/T = N/(T/a)
   ```
   Keep the flags and unnamed numerical blocks as observations; label their identities, transformations, and causal role as hypotheses.

4. **MAJOR — The README still makes an unrestricted no-common-time claim.**  
   [README.md:8](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:8).

   “No common counting time makes the stored values whole counts” drops the ranges and error model.

   Reproduction on `1 UCl4-graphite …DATA/C1s Scan.VGD`: taking
   ```
   T = max(Fraction(float(v)).denominator for v in y)
   ```
   gives **T = 2⁴¹ seconds**, and every exact rational `Fraction(float(v))*T` is an integer. This enormous time has no established acquisition meaning, but it disproves the unrestricted mathematical statement. Preserve the bounded result and its exposure-model qualification in summaries.

5. **MINOR — The generator’s introductory documentation retains superseded guarantees.**  
   [noise_counting_time.py:8](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:8).

   It still says every constraint is applied, a nonempty set lists admissible times, and the elapsed-time cap holds “whatever the detector does in parallel.” These contradict the repaired status logic and conditional exposure model. The implementation handles these correctly; update its introductory description.

6. **MINOR — The VERIFIED channel-count statement exceeds its check.**  
   [counting-time.md:88](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:88).

   Finding no numeric property equal to 128 does not establish that no property contains “any other channel count.” State that no channel-count property was identified and no numeric property equals 128.

The remaining reported dispositions checked out: dictionary names and recorded values, exclusion-gap ranks, negative/subnormal handling, packed vectors and signed I1, alignment controls and candidate coverage, neighbouring-c values, sidecar counts, decimal energy-axis comparison, and the 166/46/120 project census. No new numerical defect was found in the revised solver or alignment implementation. README §1a and §8 were excluded.

VERDICT: NO-GO
