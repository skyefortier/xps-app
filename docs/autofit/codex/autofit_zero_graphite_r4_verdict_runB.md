Reviewed HEAD `4dcabb7`, read-only.

**In-scope findings**

1. **MAJOR — The `1e-4` rule rejects a resolved, non-zero anchor solely because of its background level.** [templates/index.html:6852](/Users/skyefortier/xps-app/.claude/worktrees/fix-autofit-zero-graphite-cc/templates/index.html:6852)

   Concrete synthetic reproduction: 295→280 eV, 0.02 eV spacing; constant manual background **1,000,000**. Add Graphite asymmetric GL: amplitude **50**, center **284.5**, FWHM **0.7**, asymmetry **0.25**, mixing **0.3**. Add four symmetric GL components, amplitude **10**, mixing **0.3**, at center/FWHM **285.3/0.8, 286.2/0.8, 287.8/0.8, 291/1.0**.

   Shipped detection selects **284.52**. Using `buildAutoFitModel`, actual upload rounding/parser, and `/api/fit` with `least_squares`, `n_perturb: 3`, the successful fit returns:
   
   - Graphite amplitude **49.9978 ± 0.02646**.
   - Corrected center **284.479995 ± 0.0000511 eV**, recovering raw center **284.5000**.
   - FWHM **0.69998 eV**.

   The gate nevertheless requires amplitude **100.0051** and rejects. The identical signal on background **1,000** passes. Reproduced in both energy orders and across three perturbation seeds. This is requested case **(b)**: rejection of a resolved anchor, not a feature-authenticity objection.

No BLOCKER or additional in-scope MINOR found.

All **20 Node tests pass**. Endpoint reproductions confirm round-3 manual-background residue now rejects and the 300,000-count spike case now accepts its resolved anchor. Full-handler harness checks pass for rollback and Custom-field visibility, including tab switching. The gate precedes the **fitted-center** correction; provisional inputs are changed earlier and restored on rejection. No browser run; endpoint sessions were supplied in memory.

**OUT-OF-SCOPE**

- Previously documented non-zero anchors on featureless data/background None and single-channel spikes remain separate feature-test issues.
- Documented undo/redo loss on rejected Auto-Fit remains unchanged.

**VERDICT: NO-GO.**
