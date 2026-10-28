No BLOCKER or MAJOR findings. Three MINOR documentation issues remain.

1. **MINOR — Coefficient identities remain overstated in §3.** [counting-time.md:200](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:200) says the files record “corrections whose coefficients differ.” The evidence establishes that the unnamed eight-value block differs between settings; its identity remains a HYPOTHESIS in §1 and the repaired §2. Preserve that qualification here. This residual wording does not invalidate the corrected `a/f` interpretation.

2. **MINOR — Stage-position count conflates XY with XYZ.** [README.md:332](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/README.md:332) reports 66 distinct positions using properties 203–205. Across all 275 files, there are **67 distinct `(StageX, StageY, StageZ)` triples**, versus **66 `(StageX, StageY)` pairs**.

   Reproduction using the committed readers:
   ```python
   props = [vp.main_properties(f) for f in nct._files()]
   len({tuple(p[k][1] for k in (203, 204, 205)) for p in props})  # 67
   len({tuple(p[k][1] for k in (203, 204)) for p in props})       # 66
   ```
   State 67 triples, or explicitly describe 66 XY positions.

3. **MINOR — Intercept percentile lacks its region qualification.** [counting-time.md:229](/Users/skyefortier/xps-app/.claude/worktrees/noise/docs/findings/noise-estimator/counting-time.md:229) quotes a 90th percentile of `0.105` without identifying B1s. In `real_spectra.txt`, that number belongs specifically to B1s; the regional percentiles range from `0.036` to `0.404`. Qualify the example or report the regional range.

Verification completed read-only:

- Reviewed `git show c8cfabf`; HEAD is `bc8c6ff`, whose additional prompt commit leaves every scoped file unchanged.
- Regenerated all 275 measurements in memory: **TXT and JSON both matched byte for byte**.
- **12 tests passed**, with bytecode, pytest cache, and capture disabled.
- Independently reproduced both exact exclusion certificates, including the **158/117** first/second-gap split.
- Verified the bounded headline and exact **T = 2⁴¹ s** counterexample; corrected `a/f` interpretation; global adjusted minimum **1**; conditional union-bound calculation **1.523671875**; generator’s three statuses and conditional exposure model; and narrowed channel-count claim.
- Independently decoded the dictionaries and checked correction settings, coefficient blocks, alignment coverage and neighboring candidates. The correction-causality disposition is repaired except for the minor §3 wording above.

README §1a and §8 were excluded. No files were changed.

VERDICT: GO
