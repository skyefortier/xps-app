Reviewed HEAD `0eb9517`, read-only. **Two MAJOR findings remain.** No BLOCKER found.

1. **MAJOR — Upload-rounded flat data still anchors charge correction with a manual background.** [templates/index.html:6857](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6857)

   Reproduction: 280–295 eV, 0.02 eV spacing; baseline **10.009999**, plus a Gaussian of height **0.0001**, FWHM **0.4**, centred at **284.5**. Place manual anchors at both endpoints.

   Detection selects 284.5, but upload rounds every count to **10.01**. The unrounded manual background leaves a **constant 1e-6 residual**, exceeding the guard’s approximately **1e-8** flatness threshold.

   With `least_squares`, `n_perturb: 3`, the server returns Graphite amplitude **3.1649e-5 ± 7.2876e-6**, centre **284.203953**. Both gates pass. The application writes `cc-obs = 284.204` and invokes charge correction, permitting approximately **+0.296 eV from numerical residue**. Reproduced identically three times.

   The maximum residual distinguishes zero from positive intensity; it does not establish that a feature exists.

2. **MAJOR — One spike rejects an otherwise resolved Graphite anchor solely through the maximum-intensity threshold.** [templates/index.html:6857](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6857)

   Reproduction: 280–295 eV, 0.01 eV spacing, baseline **1,000**. Graphite: asymmetric GL, amplitude **10,000**, centre **284.5**, FWHM **0.5**, mixing **0.3**, asymmetry **0.25**. Add four symmetric GL components of amplitude **2,000**, mixing **0.3**, at centres/FWHMs **285.3/0.8, 286.2/0.8, 287.8/0.8, 291/1.0**. Use linear background; add **300,000 counts to the single sample at 284.5**.

   Detection still selects 284.5. The backend recovers amplitude **10,342 ± 1,432**, centre **284.500625 ± 0.017096 eV**—comfortably above 3σ. However, the spike makes the maximum residual **310,234**, requiring amplitude **15,512**. The guard rejects solely on the 5% rule.

   Reproduced three times. The same spectrum without the spike passes.

3. **MINOR — Documented undo/redo loss remains unchanged.** [templates/index.html:7013](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:7013)

   Undo an edit, then run an Auto-Fit that rejects: `pushUndo()` clears Redo, and rollback does not restore it. Acknowledged pre-existing limitation.

The response-contract check passes: `counts` and `background_y` are returned unconditionally and cover the full fitted ROI. Successful endpoint checks confirmed equal lengths and uploaded-data identity for **linear, Shirley, Smart, Smart experimental, legacy Shirley+Linear, Tougaard, none, and manual**, including interior background windows. See [fitting.py:1167](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/fitting.py:1167) and [fitting.py:1436](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/fitting.py:1436).

All **18 Node tests pass**. The round-2 linear-background flat case now rejects; clean and 100-scan-averaged noisy steep-ramp cases pass. Reproductions used extracted frontend functions, actual upload formatting/parser, and `/api/fit`, substituting in-memory session loading to preserve read-only operation. No browser run; workspace unchanged.

**VERDICT: NO-GO.**
