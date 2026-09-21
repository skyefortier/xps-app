**Validation:** Five non-upload tests passed. A read-only API check using an injected in-memory session returned **200/success=true** on HEAD and **422** on the parent. Parent GL and DS+G calls both failed on open bounds. The unchanged-method test appropriately passes before the fix. Missing coverage includes the three findings above, degenerate/nonfinite boxes, and an actual linked fit; the DS+G regression test also never asserts `success`.

VERDICT: NO-GO.
tokens used
92,844
The site table misses **saved fit/project data**: `applyBackendResult` stores returned bounds in `_backendParams` (`templates/index.html:6283`), which peak serialization preserves (`:9336`, `:9494`). Also distinguish the browser’s Auto-fit C1s request (`:7024`) from Run Fit; both select DE. Item 6 is false: `_validateUncertainties` reads response bounds at `:10732`.

1. **MAJOR — The amplitude cap excludes valid solutions and still reports success.** [fitting.py:978](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:978)

   Reproduced with `x = linspace(286,290,81)`, background `none`, and a Gaussian of true amplitude **10,000**, centre **285**, FWHM **1**. Fix centre/width; start amplitude at **1,000**. This represents fitting a neighbouring peak’s tail after narrowing the ROI.

   `max(y_sub)=625`, so DE caps amplitude at **6,250**. It returns **success=true**, amplitude **6,250**, and ROI area **62.096**. Least-squares recovers amplitude **10,000** and area **99.353**. The new restriction causes **37.5% area underestimation**. Perturbation cannot escape the inherited cap.

   The normalization premise at `:966` does not justify this bound. Account for the component’s visibility on the evaluation grid, or detect and expand an active artificial cap.

2. **MAJOR — Valid one-sided centre bounds can become `min == max`.** [fitting.py:984](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:984)

   Reproduced with ROI **280–290**, free `ds_g`, `center=300`, `center_min=300`, and no upper bound. The helper creates **[300,300]**. lmfit then raises `Parameter 'p1_center' has min == max`; `run_fit` wraps it as `RuntimeError`, producing **HTTP 422**.

   The symmetric case, `center=270, center_max=270`, also fails. Widening to include the start guarantees neither positive width nor finite bounds. Preserve a nonzero search interval when filling an open side.

3. **MINOR — Artificial caps trigger misleading “at lower bound” warnings.** [fitting.py:978](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:978), [templates/index.html:10732](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/templates/index.html:10732)

   With a strongest peak of **1,000**, the generated amplitude range is **[0,10,000]**. A well-determined satellite at **80 ± 1** is consequently classified as “at lower bound (0)” because the frontend uses **1% of the entire range**, i.e. **100**. I reproduced that warning using the actual frontend function. Distinguish artificial search limits or revise this diagnostic.

The seven normalization implementations are:

| Shape | Actual amplitude convention |
|---|---|
| Gaussian | Value at mathematical centre; sampled maximum can be much smaller. |
| Lorentzian | Same. |
| Pseudo-Voigt GL | Same. |
| Asymmetric GL | Same, with different widths on either side. |
| Doniach–Sunjic | Value at centre; asymmetry can move the maximum. |
| DS+G | Convolved branch normalizes at centre on the **padded grid**, potentially outside the ROI. Unconvolved branch interpolates on the supplied grid. |
| CasaXPS LA | Unconvolved branch uses mathematical centre height; convolved branch normalizes at the sample nearest the centre, not necessarily the maximum. |

Thus none supports the blanket “peak height on the evaluation grid” claim across all allowed inputs.

Other checks:

- **Expressions/fixed parameters:** Safe to skip for DE’s finite-bound check. Installed lmfit **1.3.4** checks only `vary=True` and disables variation for expressions. An actual linked-doublet DE fit succeeded with the slave amplitude bounds still open.
- **Perturbations/results:** Closed bounds carry through. DE performs fresh global searches over those same bounds; changing starts does not expand them. Bounds are echoed at `fitting.py:1259`; area and uncertainty formulas are unchanged, but their inputs can change materially.
- **NaN/inf:** Partial NaNs in `y_sub` are ignored by `nanmax`; all-NaN data produces a NaN upper bound, and infinity produces an infinite bound. NaN/inf in `x` similarly poisons centre limits. This happens **before** `nan_policy="omit"`. CSV upload filters nonfinite rows, but direct callers are not protected. Zero and entirely negative finite data both fitted successfully with amplitude zero in my checks.
- **Search expectations/docs:** Existing ±2 eV centre windows remain. Starts influence the generated bounds despite DE not using them as its population seed. [CLAUDE.md:247](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/CLAUDE.md:247) omits the absolute values and floor of 1; “centre within the fitted energy range” also ignores preserved bounds and outside starts. I did not independently verify the 3–47 s or six/seven-component benchmark claims.
- **Other callers:** `/api/analyze` and `/api/analyze/start` can reach DE through `LeastSquaresMethod.options.fit_method`. The parity refitter defaults to leastsq; the other inspected scripts do not currently select DE.

**Validation:** Five non-upload tests passed. A read-only API check using an injected in-memory session returned **200/success=true** on HEAD and **422** on the parent. Parent GL and DS+G calls both failed on open bounds. The unchanged-method test appropriately passes before the fix. Missing coverage includes the three findings above, degenerate/nonfinite boxes, and an actual linked fit; the DS+G regression test also never asserts `success`.

VERDICT: NO-GO.
