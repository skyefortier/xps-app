The bounded exclusion result reproduces, but the finding needs revision. I reproduced `counting_time.json` exactly and `counting_time.txt` byte-for-byte; all eight tests pass. No files were changed.

1. **MAJOR — The reader discards a dictionary that establishes property names and records correction information.** [vgd_properties.py:113](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/vgd_properties.py:113), [counting-time.md:30](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:30), [counting-time.md:44](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:44).

   Property 0 is replaced with `("DICTIONARY", None)`. Decoding it reveals these names consistently across all 275 files:

   | ID | Recorded name |
   |---|---|
   | 305 | `DwellTime` |
   | 306 | `Scans` |
   | 328 | `Current Scan` |
   | 303 / 304 | `AcquisitionStart` / `AcquisitionEnd` |
   | 404 | `PassEnergy` |
   | 105 | `SourceEnergy` |
   | 406 | `ChamberWorkFunction` |
   | 331 | `DetectorSignatureCorrectionPath` |
   | 981 | `Calibration Energy Scale` |

   Thus these names are recorded evidence, not merely hypotheses; 328 is not named “number of scans (second copy).”

   More consequentially, **all 275 files contain `SignatureCorrected` (313) = True and `Acq_TXFN_Correction` (415) = True**, plus `Acq_TXFN_CCorrectionType` = 3, `NumberOfTXFNCoeffs` = 4, and `NumberOfPSFCoeffs` = 8. This contradicts the statements that the files do not record whether corrections occurred and that nothing in them settles the proposed correction explanation. The exact correction algorithm remains unestablished.

   Reproduction: in the first committed `C1s Scan.VGD`, the main stream’s dictionary starts at byte 684 and contains 58 entries. Read its entry count, then each `(uint32 property_id, uint32 character_count, padded UTF-16LE name)`. This is the documented [MS-OLEPS DictionaryEntry format](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-oleps/333959a3-a999-4eca-8627-48a224e63e77). Across the corpus, 254 dictionaries contain 58 entries and 21 contain 57.

2. **MAJOR — Deferred results are not complete admissible sets, but the API and reporting describe them that way.** [noise_counting_time.py:105](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:105), [noise_counting_time.py:221](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:221), [counting-time.md:60](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:60).

   With the default cap:

   ```python
   admissible_times(
       [1.0, math.sqrt(2)],
       [(Fraction(1), Fraction(1_000_000))]
   )
   # ([(Fraction(1), Fraction(1000000))], 0, 3)
   ```

   The returned interval includes `T = 1`, which plainly fails the value constraint for `sqrt(2)`. All three constraints were deferred. The reporter nevertheless counts any non-empty interval set as “admissible.”

   Return an explicit unresolved status and prevent unresolved intervals from being reported as admissible, or complete the constraints. Add a regression test for this case.

   **This does not invalidate the committed exclusions:** instrumentation found zero actual deferrals in either corpus search. Generally, however, returned `deferred: 0` means no unresolved constraints remain—not that every constraint was applied.

3. **MAJOR — The noise-scale derivation incorrectly cancels an arbitrary smooth correction.** [counting-time.md:113](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:113).

   For Poisson counts and a deterministic multiplicative correction,

   \[
   y=\frac{aN}{f\,d\,s}
   \quad\Longrightarrow\quad
   \operatorname{Var}(y)=\frac{a}{f\,d\,s}E[y],
   \qquad kds=\frac{a}{f}.
   \]

   The document asserts `kds = 1/f` while allowing “any smooth correction factor.” Even a constant correction disproves that assertion. With the same detector factor, `a_high-resolution = 1` and `a_survey = 0.15` predict a survey/high-resolution noise-scale ratio of **1.5**, despite the tenfold dwell×scans difference.

   The factors **10** and **25** are correct only under additional assumptions about equal correction factors and comparable estimator bias. Correlation and noise-floor caveats do not repair the missing factor. The measured table is reproducible; the claimed model rejection needs narrowing.

4. **MAJOR — The headline claims an approximate exclusion over a continuous range that was never tested.** [counting-time.md:7](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:7), [counting-time.md:101](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:101), [noise_counting_time.py:168](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:168).

   The exact search covers range (a); Rayleigh testing only samples the decoded candidates in (b). It cannot establish “none … admits any T up to its own acquisition time, exactly or approximately.”

   Reproduction using the existing statistic: at `T = 1e-9`, **all 275 files have R ≥ 0.9999999912**; even multiplying their nominal p-values by 1024 leaves every result below `2.53e-76`. This is trivial phase concentration near zero, not evidence of meaningful counting times, but directly demonstrates why the continuous approximate claim is unjustified.

   Also, only **113 files** have all 1024 Rayleigh candidates evaluated; the others lose candidates at the minimum-point cutoff, with as few as 58 evaluated.

   State separately: exact exclusions within the specified ranges and error model; no significant Rayleigh result among eligible decoded candidates. Preserve the physical-cap assumptions in the conclusion.

5. **MINOR — The document identifies the wrong constraints as excluding 117 files.** [counting-time.md:86](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:86).

   Instrumenting `_apply` shows:

   - Range (a): 158 files are excluded by the first gap constraint; 117 by the second.
   - Range (b): every file is excluded by the first gap constraint.
   - **No value constraint is reached in either corpus search.**

   Replace “the value constraints exclude the remaining 117” with the actual second-gap intersection result.

6. **MINOR — The explanation of olefile’s failure is incorrect, and the reader overstates its general format support.** [vgd_properties.py:3](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/vgd_properties.py:3), [vgd_properties.py:49](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/vgd_properties.py:49), [counting-time.md:24](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:24).

   A raw type-header census found **zero vector properties** across every property stream in the 275 files. The reported corrupt `Nexsa_G2…` string is reproducible, but the installed olefile implementation reads the LPWSTR length from `offset + 4`, the start of the characters, instead of `offset`.

   The custom reader correctly handles the scalar types present, but its generic vector branch incorrectly pads each small scalar. For example:

   ```python
   _value(struct.pack("<HHIhh", 0x1002, 0, 2, 1, 2), 0)
   # struct.error
   ```

   This is a valid two-element I2 vector: [MS-OLEPS](https://learn.microsoft.com/en-us/openspecs/windows_protocols/MS-OLEPS/f122b9d7-e5cf-4484-8466-83f6fd94b3cc) pads the sequence, not each element. Scalar I1 also decodes `-1` as `255`. Neither defect affects this corpus; narrow the support claim or fix and test these branches.

7. **MINOR — “Stepped point by point” is stronger than the timing regression establishes.** [counting-time.md:37](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:37), [counting-time.md:83](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:83).

   Independently unpacking the numeric properties reproduces:

   ```
   slope       1.00498659335
   intercept  20.9535781308 s
   residuals  -3.34406656876 … +2.69068740972 s
   ```

   This supports a stepping-time budget. It does not distinguish single-energy acquisition from stepping an analyser while multiple channels collect simultaneously, nor establish each output bin’s accumulated exposure.

   The elapsed-time cap is sound **conditional on the asserted single-channel-per-output-energy exposure model**. Dispersiveness alone does not establish that mapping or the normalization. Retain that condition explicitly; the dictionary establishes the timestamp names, not the entire detector model.

8. **MINOR — CPS units are not established by every sidecar in the expanded corpus.** [noise_counting_time.py:1](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:1), [counting-time.md:101](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:101).

   XML parsing gives **268 `AxisY` titles of `Counts / s` and seven of `Counts`**. For example, [9 A to G.DATA/C1s Scan.xml:34](</Users/skyefortier/xps-app/.claude/worktrees/noise/docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan.xml:34>).

   These seven charts may contain default/stale display settings; this does **not** establish that their intensities are raw counts. It does require qualifying the extension of the earlier 230-file unit evidence to all 275 files. The mathematical lattice exclusions are unaffected.

9. **MINOR — Blanket negative rejection exceeds the stated inequality model.** [noise_counting_time.py:85](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:85).

   For `y = -math.ulp(0.0)`, nonnegative count `N = 0` satisfies `|y − N/T| ≤ 2 ulp(y)` at every positive T. The function returns an empty set. Either make nonnegative observations an explicit additional input restriction or handle negatives within tolerance. No committed spectrum is affected.

10. **MINOR — The exact sidecar identity uses the decimal nominal source energy, not the stored property value.** [counting-time.md:148](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:148).

    Property 105 is `1486.6800537109375`, whereas the exact endpoint identity uses `1486.68`. Their difference is `0.0000537109375 eV`. Say “the decimal nominal value represented by property 105.” The **4.58 eV app/sidecar offset itself is correct**.

Other checks passed: the scalar property boundaries and padding match throughout; all code pages are 1200, supporting UTF-16 BSTR decoding; all acquisition timestamps have whole-second ticks; the 72/73-property census and absence of numeric 128 reproduce. Ordinary consistent whole-second rounding/truncation justifies the additional one-second duration allowance.

For positive observations and positive ranges without unresolved deferrals, the gap constraints are implied by the value constraints, their `n_min = 1` is justified when `gap > δ₁ + δ₂`, and the ceil/floor bounds are correct. Skipping nonnegative values `≤ δ` is valid because `N = 0` works. An independent 2,000-case point-membership check found no discrepancies. Both requested mutations—dropping value constraints and setting δ to zero—are caught by existing tests.

Range (b)’s rational bands correctly contain both dwell representations. The Rayleigh formula is the correct large-sample expression under independent uniform phases, rather than a calibrated null for arbitrary correlated spectra; [Astropy’s implementation](https://docs.astropy.org/en/stable/_modules/astropy/stats/circstats.html#rayleightest) also applies small-sample corrections. Bonferroni over 1024 is conservative when candidates are skipped. A minimum adjusted p of 0.01436 across 275 files is not compelling evidence against chance, but “about what chance gives” is not a demonstrated calibration. The `yT ≤ 1e5` cutoff limits the nominal/float32 time discrepancy to approximately **0.00224 cycles**, so that numerical rationale is sound.

All 275 sidecar energy endpoints match the decimal identity. Both upload paths send only the file, so the app defaults apply. The project census also reproduces: **167 saved tabs, 46 at zero, and 121 nonzero shifts spanning −6.00 to −4.65 eV**. Which physical energy convention is correct remains a separate interpretation.

VERDICT: NO-GO
