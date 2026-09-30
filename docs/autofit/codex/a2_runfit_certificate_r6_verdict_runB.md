# A2 round 6 — run B (commit 2157625; codex exec, reasoning high)

1. **MAJOR — Alternatives lose bounded-parameter scales, rejecting equivalent certified solutions.** [tests/fit_equality.py:204](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:204), [line 213](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:213).

   Bounds are recovered only from `{value, min, max}` dictionaries. Alternative parameters are scalar values, so they fall back to relative comparison.

   Reproduced with two complete responses to the same request, seed **123**, controlling only scattered-start initialization; fitting, certification and reporting remained real. Construction: 1,001 points over −10…10, a held height-50/FWHM-1e9 Gaussian, and two true LA lines at ±1 with heights 10/8, FWHM 0.2, α=β=1. Fit one LA component starting at +1; scatter it to −1 with free `m` initialized at **0.3 versus 0.001**.

   Both alternatives certify at centre **−0.9998344627**, with **identical curves, areas and χ²ᵣ = 0.00900083851426**. The returned fits also compare equal. Nevertheless, the complete comparison rejects only:
   `starts.alternatives.0.components.0.params.m`.

   The difference **0.299** is inside the documented `[0,499]` span allowance **0.499**, but the alternative receives an allowance of **0.0003**. Resolve alternative parameter scales using the corresponding component’s metadata, including linked bounds.

2. **MINOR — Link lookup does not recognize all valid parameter identifiers.** [tests/fit_equality.py:114](/Users/skyefortier/xps-app/.claude/worktrees/fix-runfit-certificate/tests/fit_equality.py:114).

   The regex cannot resolve names such as `proot_1_m`, although these are valid lmfit names accepted by `run_fit`.

   Reproduced with real three-component LA fits linked **`grandchild → child_2 → root_1`**, including amplitude factors **0.75** and centre offsets **10.9 eV**. Changing the root’s starting `m` from **0.3 to 0.001**, with seed pinned, produces **identical component curves and χ² = 2.486270895138508**, both certified. The root passes against `[0,499]`; both linked copies fail because their master lookup fails. Parse complete identifiers instead of this restricted pattern.

The accepted finite-resolution ruling stands. The round-5 DS+G regression and numeric-ID chain checks passed, as did all **398 eligible recorded parameter/curve replays**, the **59-test parity battery**, and **122 focused JavaScript tests**. Broader Python sweeps were stopped for the review budget after 46 and 14 passes. Certificate exits, cancellation, V3 ordering and displacement checks passed; recorded notices remain **0/202** for each method. No files changed.

**VERDICT: NO-GO**
