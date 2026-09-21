Validation: **five non-upload tests passed**. An equivalent page request using an in-memory session succeeded on HEAD and returned 422 using parent code. Parent GL and DS+G calls both reproduced the original open-bound failure. The upload fixture was not run because this review is read-only. Missing coverage includes the three findings, nonfinite inputs, and actual linked-peak optimization; the DS+G test also never asserts convergence.

VERDICT: NO-GO.
tokens used
79,735
The site table misses the separate `runAutoFitC1sGraphite` request path and asynchronous `/api/analyze/start` worker. Both can reach DE. Also, item 6’s assumption is false: `_validateUncertainties()` reads response bounds.

1. **MAJOR — The amplitude cap excludes valid solutions.** [fitting.py:978](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:978)

   Reproduced with ROI 284–294 eV, Gaussian centre fixed at 283, FWHM fixed at 1, true amplitude 10,000, starting amplitude 100, background `none`. The largest observed intensity is 625, so the generated ceiling is 6,250.

   Least-squares recovers 10,000 exactly. DE returns **HTTP 200, `success=true`, amplitude 6,250**, and an area **37.5% too small**. This represents fitting a neighbouring peak’s tail after narrowing the ROI. Including twice the start does not protect an underestimated start.

2. **MAJOR — Valid one-sided bounds can become zero-width intervals.** [fitting.py:984](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:984)

   Reproduced with ROI 284–294, free `ds_g`, `center=294`, `center_min=294`, no `center_max`. The helper creates `[294, 294]`. lmfit rejects it with `Parameter 'p1_center' has min == max`; `/api/fit` returns **422**.

   The symmetric upper-only case also fails. Widening only to include the current value guarantees neither positive interval width nor a valid search domain.

3. **MINOR — Generated ceilings introduce false “at lower bound” warnings.** [fitting.py:978](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/fitting.py:978), [templates/index.html:10732](/Users/skyefortier/xps-app/.claude/worktrees/fix-de-finite-bounds/templates/index.html:10732)

   With maximum intensity 10,000, every ordinary amplitude gets ceiling 100,000. A well-determined satellite amplitude of 500, even with stderr 5, now triggers “at lower bound (0). Widen bounds or lock this parameter.” Reproduced by executing the actual validator. Its 1%-of-range threshold becomes 1,000 solely because of the artificial ceiling.

The seven-shape normalization premise does **not** hold:

| Shape | Actual normalization |
|---|---|
| Gaussian | Height at mathematical centre; sampled maximum can be much smaller |
| Lorentzian | Same |
| Pseudo-Voigt GL | Same |
| Asymmetric GL | Same |
| Doniach–Šunjić | Value at centre; asymmetric maximum can exceed amplitude |
| DS+G | Convolved value at centre on padded grid; without convolution, interpolated centre value on input grid |
| CasaXPS LA | With convolution, nearest-to-centre sample; without convolution, mathematical centre |

Thus convolved DS+G also lacks the claimed ROI-maximum guarantee. Convolved LA has a sampled normalization point, but its unconvolved branch does not.

Other checks:

- **Expressions/fixed parameters:** Safe to skip. Installed lmfit 1.3.4 checks finite bounds only for varying parameters and forces expression parameters non-varying. An actual linked-doublet DE fit succeeded with the linked amplitude still unbounded.
- **Negative/zero data:** Absolute intensity avoids a negative ceiling; the `1.0` floor handles zero data. With nonnegative components, entirely nonpositive data does not itself require a large positive amplitude.
- **NaN/Inf:** The helper does not guarantee finite boxes: an infinite intensity produces an infinite ceiling; all-NaN intensities produce NaN; NaN energy contaminates centre bounds. `nan_policy="omit"` runs later. Upload parsing filters nonfinite samples, limiting ordinary-page exposure.
- **Refits/results:** Bounds persist through perturb-and-refit and are serialized. Changed fitted values affect areas and any available uncertainty propagation. DE’s retries sample the same box afresh.
- **Other callers:** `/api/analyze` and its asynchronous variant accept DE through `LeastSquaresMethod.options.fit_method`; `bg_window_worked_example.py` accepts it through its CLI argument. The core autofit engine uses its own fitting path.
- **Expectations/documentation:** Existing ±2 eV centre windows remain. Starts influence the inferred amplitude ceiling despite DE not using them as its initial solution. CLAUDE’s formula omits absolute values and the floor of 1; “centre within the fitted energy range” also excludes preserved bounds and out-of-ROI starts. The reported timings and target-specific nonconvergence were not independently verified.

Validation: **five non-upload tests passed**. An equivalent page request using an in-memory session succeeded on HEAD and returned 422 using parent code. Parent GL and DS+G calls both reproduced the original open-bound failure. The upload fixture was not run because this review is read-only. Missing coverage includes the three findings, nonfinite inputs, and actual linked-peak optimization; the DS+G test also never asserts convergence.

VERDICT: NO-GO.
