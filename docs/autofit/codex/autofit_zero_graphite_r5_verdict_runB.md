Reviewed HEAD `2f8420b`, read-only. **Two in-scope MAJOR findings remain.**

Reproductions used shipped detection, `buildAutoFitModel`, `uploadToBackend` serialization/parser, `/api/fit` with `least_squares`, `n_perturb: 3`, and extracted result-application functions. Session storage was replaced with memory; no browser run or file changes.

Both scenarios use Graphite asymmetric GL at **284.5 eV**, FWHM **0.7**, mixing **0.3**, asymmetry **0.25**, plus four symmetric GL components with **20%** of Graphite’s amplitude, mixing **0.3**, at center/FWHM **285.3/0.8, 286.2/0.8, 287.8/0.8, 291/1.0**.

1. **MAJOR — Numerical residue on exactly zero server signal passes.** [templates/index.html:6848](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6848)

   Scan **295→280 eV**, spacing **0.02**; constant background **10,000,000**, Graphite amplitude **0.0001**. Set manual background anchors to **10,000,000** at both endpoints.

   Detection selects **284.52**, but every uploaded intensity becomes **10000000.00**. Server `counts − background_y` is **exactly zero everywhere**.

   Nevertheless, the successful fit returns amplitude **0.02958562 ± 0.00916598**, center **284.256015**. Both checks pass. Result application writes **`cc-obs = 284.276`** and calls charge correction, permitting approximately **+0.224 eV** from numerical residue.

   Reproduced with perturbation seeds **1 and 2**; seed 3 rejects. This is an in-scope residue failure: zero amplitudes would fit the server’s signal exactly.

2. **MAJOR — The 0.01 cutoff rejects a resolved small-unit anchor retained after upload.** [templates/index.html:6848](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6848)

   Scan **295→280 eV**, spacing **0.002**; background **`0.1 + 0.04 × (BE − 280)`**, represented by manual endpoint anchors. Graphite amplitude **0.009**. Uploaded intensities remain between **0.10 and 0.70**.

   Detection selects **284.512**. The successful server fit returns amplitude **0.00886999 ± 0.00173491**—**5.11σ**—FWHM **0.689876**, and recovered raw center **284.498743 eV**. The gate rejects solely because amplitude is below **0.01**. Reproduced with seeds **1 and 2**.

   Removing Graphite changes **428 uploaded samples**. Thus the server retains information about this line: **sample quantization is not a lower bound on resolvable fitted amplitude**. The rule does not track exactly what the server can see.

All **21 Node tests pass**. The round-4 **50-on-1,000,000** reproduction now passes. Near-unit-scale data passes; a **0.004** line uploaded as all zeros rejects appropriately. No additional BLOCKER, MINOR, placement, or rollback finding.

**OUT-OF-SCOPE**

- Previously documented non-zero anchors on featureless data with background None, and single-channel spikes, remain feature-authenticity issues.
- Previously documented undo/redo loss on rejection remains unchanged.

**VERDICT: NO-GO.**
