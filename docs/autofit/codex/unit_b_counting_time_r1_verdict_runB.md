tokens used
96,657
The numerical exclusions reproduce, but the finding needs substantive corrections. I reviewed **`81f9f8c`**, including loading its scripts directly after the working files changed during review. I made no changes.

All eight committed tests pass. Regenerated JSON and text match the committed outputs exactly.

1. **MAJOR — The reader discards the dictionary that establishes the property names and records corrections.**  
   [scripts/vgd_properties.py:113](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/vgd_properties.py:113), [counting-time.md:30](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:30), [counting-time.md:44](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:44).

   Property 0 is replaced with `("DICTIONARY", None)`. Decoding its entries in the main property stream produces these names **in all 275 files**:

   | IDs | Recorded names |
   |---|---|
   | 305, 306, 328 | `DwellTime`, `Scans`, `Current Scan` |
   | 303, 304 | `AcquisitionStart`, `AcquisitionEnd` |
   | 404, 406, 105 | `PassEnergy`, `ChamberWorkFunction`, `SourceEnergy` |
   | 331, 981 | `DetectorSignatureCorrectionPath`, `Calibration Energy Scale` |
   | 313, 415 | `SignatureCorrected`, `Acq_TXFN_Correction` |

   Both correction flags are `True` in every file. Additional named fields include correction type, coefficient counts, and detector-efficiency calibration.

   **Reproduction:** read property 0 from `\x05Q5nw4m3lIjudbfwyAayojlptCa`; decode its entry count followed by `(property ID, character count, padded UTF-16LE name)` entries. This follows Microsoft’s [DictionaryEntry specification](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-oleps/333959a3-a999-4eca-8627-48a224e63e77).

   Consequently, the names are recorded evidence, 328 is not simply a second copy of the scan-count field, and 406 is identified. Statements that the files do not record **whether** corrections occurred are contradicted. Their formulas and invertibility remain unestablished.

2. **MAJOR — Deferred constraints invalidate the unconditional “exact and complete” return contract.**  
   [scripts/noise_counting_time.py:105](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:105), [counting-time.md:60](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:60).

   Using the committed implementation:

   ```python
   admissible_times([1e8, 2e8 + 1], [(Fraction(1), Fraction(2))])
   # ([(Fraction(1), Fraction(2))], 0, 3)
   ```

   The returned interval includes `T=1.5`, where the second value gives a half-integer: residual `0.5` counts versus allowed error `8.94e-8` counts. The intervals are therefore an **unresolved superset**, not the admissible set. The report also counts nonempty unresolved intervals as “admissible,” although it separately prints deferrals.

   Require an explicit unresolved status, or complete the constraints before claiming admissibility. Add this counterexample to the tests.

   **The committed negative results are unaffected:** all are empty, and I independently excluded range (a) for every file using only two gap constraints. `deferred: 0` means no unresolved constraints remain relevant to the result; it does not mean every value constraint was evaluated.

3. **MAJOR — §3’s prediction is mathematically incorrect when allowing “any smooth correction factor.”**  
   [counting-time.md:113](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:113), [counting-time.md:140](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:140).

   For Poisson counts with stored intensity
   \[
   Y=a(E)N/T,\qquad T=f\,dwell\,scans,
   \]
   the variance-to-mean ratio is
   \[
   k=\frac{\operatorname{Var}(Y)}{\operatorname{E}(Y)}
     =\frac{a(E)}{T},
   \qquad k\,dwell\,scans=\frac{a(E)}{f},
   \]
   **not `1/f`**. Smoothness does not cancel the correction amplitude.

   Factors **10** and **25** are correctly derived only with an appropriate common correction amplitude: the latter is `10 × [(50/0.1)/(200/1)]`. Different correction amplitudes can change either prediction without correlation or a noise floor. The existing caveats do not repair this omitted factor, especially given the recorded correction flags.

4. **MAJOR — The approximate test does not support the headline exclusion over all acquisition-bounded times.**  
   [counting-time.md:7](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:7), [scripts/noise_counting_time.py:167](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:167).

   Rayleigh is evaluated only at nominal discrete candidates in range (b), not continuously over range (a), nor throughout the candidate bands. Only **58–1024 candidates per file** actually have enough retained points.

   Moreover, failure to reject uniform phases is not proof of absence of approximate integer structure. Two reproduced limitations:

   - Ten perfect integer phases give `R=1`, but family p is `1024·exp(-10)=0.04649`; this is reported as not significant at 1%.
   - A half-integer offset lattice also gives `R=1`; the statistic does not check phase alignment with zero.

   `exp(-mR²)` is the appropriate asymptotic tail under independent uniform phases, not merely unspecified “no structure.” The [Rayleigh literature](https://pmc.ncbi.nlm.nih.gov/articles/PMC10964323/) supports that asymptotic formulation. Bonferroni over 1024 is conservative when fewer candidates are evaluated; dependence between candidates does not itself invalidate Bonferroni.

   The minimum family p, `0.0143593`, is not persuasive evidence against chance across 275 files. Report **no significant phase concentration at evaluated candidates**, rather than approximate exclusion everywhere.

5. **MINOR — The serial-acquisition inference is stronger than the regression establishes.**  
   [counting-time.md:37](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:37), [counting-time.md:83](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:83).

   Independent reproduction gives slope `1.0049865933`, intercept `20.95357813 s`, residuals `−3.34406657…+2.69068741 s`.

   This supports acquisition duration proportional to the number of dwell settings and scans. A detector collecting multiple energies simultaneously while stepping through those settings produces the same relationship. It does not establish that each energy receives only `dwell × scans`.

   The elapsed-time cap is sound **conditional on the stated nonoverlapping-channel/live-time premise**. A dispersive analyser alone does not establish every detail of that premise. `elapsed + 1 s` is appropriate conservative slack for consistently rounded or truncated whole-second endpoints. Preserve these conditions in the conclusion; the dictionary establishes the timestamp names more directly than the regression does.

6. **MINOR — CPS provenance is not verified uniformly for the expanded 275-file corpus.**  
   [scripts/noise_counting_time.py:1](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/noise_counting_time.py:1), [counting-time.md:101](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:101).

   An XML census gives **268 `Counts / s` sidecars and seven `Counts` sidecars**. For example, [9 A to G.DATA/C1s Scan.xml:34](</Users/skyefortier/xps-app/.claude/worktrees/noise/docs/autofit/test_data/9 UCl4-graphite 4%, no kapton 1eV, 180 eV, 200 um/9 A to G.DATA/C1s Scan.xml:34>) says `Title="Counts"`; its enabled secondary axis agrees.

   These may be placeholder chart settings, so they do not establish that the values are raw counts. They do prevent extending the original 230-file sidecar-based CPS verification to all 275 without qualification. The numerical lattice exclusions remain valid; their interpretation in seconds needs verified units.

7. **MINOR — The stated reason for excluding 117 files is wrong.**  
   [counting-time.md:86](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:86).

   Instrumenting the committed solver and independently intersecting the first two gap constraints gives:

   ```text
   Excluded by first gap:   158 files
   Excluded by second gap:  117 files
   Value constraints used:   0 files
   ```

   Replace “the value constraints exclude the remaining 117” with “a second gap constraint excludes the remaining 117.” The eight tests do catch dropping value constraints and setting δ to zero, but the corpus itself does not exercise the value-constraint path.

8. **MINOR — The olefile failure is real, but its explanation and the reader’s generality are overstated.**  
   [counting-time.md:23](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:23), [scripts/vgd_properties.py:49](/Users/skyefortier/xps-app/.claude/worktrees/noise/scripts/vgd_properties.py:49).

   The committed property streams contain **no vector properties**. Installed olefile 0.47 does reproduce the corrupted `Nexsa_G2…` string: its LPWSTR branch reads the length from `offset+4` instead of `offset`.

   The custom reader correctly handles the types encountered here, including character-counted LPWSTR, UTF-16 BSTR under code page 1200, and FILETIME. A synthetic variant vector also decodes correctly. However:

   ```python
   _value(struct.pack("<II4B", 0x1011, 4, 1, 2, 3, 4), 0)
   # IndexError: packed UI1 vector elements are incorrectly padded individually

   _value(struct.pack("<IB3x", 16, 255), 0)
   # I1 = 255; should be -1
   ```

   Microsoft specifies packed small scalar vector elements with padding after the sequence, and signed `VT_I1` in [TypedPropertyValue](https://learn.microsoft.com/en-us/openspecs/windows_protocols/MS-OLEPS/f122b9d7-e5cf-4484-8466-83f6fd94b3cc). These defects do not affect this corpus.

Other requested checks passed: 21 files have 72 main properties and 254 have 73; no decoded numeric property equals 128. The positive-value gap implications, integer endpoint bounds, and Fraction arithmetic are sound. Values within δ of zero can correctly use `N=0`; blanket rejection of negative subnormal values needs an explicit nonnegative-input restriction to match the mathematical contract.

Range (b) covers the stated integer candidates and both dwell representations. The `yT≤1e5` cutoff bounds nominal-versus-float32 dwell phase displacement to approximately `0.00224` cycles or less.

The **4.58 eV axis discrepancy is reproduced for all 275 files**, as are the file-only upload paths and default parameters. The project census is also correct: 166 tabs, including 46 at zero, with nonzero shifts from −6.00 to −4.65 eV. One precision correction: property 105 is `1486.6800537109375`, whereas the sidecar identity uses nominal `1486.68`. Which physical energy convention is correct remains unestablished by that identity.

VERDICT: NO-GO
