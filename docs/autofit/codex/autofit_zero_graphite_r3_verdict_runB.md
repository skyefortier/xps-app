Reviewed HEAD `0eb9517`, read-only. **Two MAJOR findings remain. No BLOCKER found.**

1. **MAJOR — Constant uploaded data still anchors charge correction with background None.** [templates/index.html:6857](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6857)

   Reproduction: 280–290 eV, 0.05 eV spacing, intensity `10 + 0.004 × exp(-4 ln(2) × ((E−284.5)/3)²)`. Detection selects 284.5, but upload rounds **every count to 10.00**. With background None, `counts − background_y` remains constant **10**, so the “flat” check passes.

   `leastsq`, `n_perturb: 3`, perturb seed 2 returns success: amplitude **5.76639**, stderr **null**, centre **284.200267**. The extracted application function writes **`cc-obs = 284.200`** and calls charge correction—approximately **0.300 eV derived from constant data**. Also reproduced unseeded. A narrower 283.5–285.5 eV version reproduces with default `least_squares`.

2. **MAJOR — A single-channel spike is accepted as a resolved Graphite anchor.** [templates/index.html:6857](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6857)

   Reproduction: 280–295 eV, 0.05 eV spacing, baseline **1,000**, with just the **284.7 eV channel raised to 1,100**; linear background, `least_squares`, `n_perturb: 3`.

   Detection selects the spike. Successful fitting returns amplitude **14.5898**, FWHM at its **0.400 eV lower bound**, centre **284.49987**, and missing stderr. Amplitude exceeds the **5-count** threshold. Application writes **`cc-obs = 284.700`** and calls charge correction, deriving a **0.200 eV shift from one anomalous channel**.

   Reproduced repeatedly, including perturb seeds 1–3. A spike at 284.5 also passed with finite uncertainty, **14.5894 ± 2.92265**, so requiring stderr alone would not close this gap.

3. **MINOR — Known undo/redo loss remains unchanged.** [templates/index.html:7013](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:7013)

   Undo an edit, then run an Auto-Fit that rejects: `pushUndo()` clears Redo, and rollback does not restore it. This is the documented limitation.

The original round-2 linear-background cases now pass their intended checks: rounded-flat data is rejected; steep-ramp anchors, including the 100-scan noisy example, are accepted.

**Response contract confirmed:** `counts` and `background_y` are present, equal-length, and cover the fitted uploaded ROI for all eight background choices, including narrowed background windows and legacy Shirley + Linear. They are returned unconditionally at [fitting.py:1440](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/fitting.py:1440).

All **18 Node tests pass**. Reproductions used extracted frontend functions, actual upload rounding/parser, and the real Flask `/api/fit`, with session storage supplied in memory. No browser run; workspace unchanged.

**VERDICT: NO-GO.**
