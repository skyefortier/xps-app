- **MINOR — The “exactness” cutoff still rejects a resolved anchor at extreme dynamic range.** [fitting.py:1398](/Users/skyefortier/xps-app/.claude/worktrees/feature-autofit-required-refit/fitting.py:1398). Reproduced using the existing fixture’s grid, bounds and `KW`, with two-decimal synthetic data: Graphite `(amplitude=1, center=284.5, width=0.7)`, GL components `(3e9, 285.1, 1.9)` and `(2300, 286.4, 1.4)`, background `1000`. Both fits converge:
  - χ² with anchor: **1.946e−10**; without: **1.439e−9**.
  - **F = 943.79**, support F = **10,499.67**, yet `required:false` because the cutoff is **3.347e−9**.
  - Fitted center: **284.49945 ± 0.00278 eV**. Maximum reduced-fit residual: **0.268 counts**, well above two-decimal rounding or floating-point resolution.

  Thus, `1e-10` relative residual does not establish floating-point exactness. The exception still needs a numerical justification that preserves this significant removal. This counterexample is synthetic; I did not establish a failure on ordinary Poisson data.

The expression-order fix passes both reverse-chain cases. All generated cross-peak expressions use `constrain_to`, so I found no page-produced reference escaping the removal closure. Unrounded identical-half-component removal correctly returns “not required” under both local methods.

Validation: **8 Python tests and 23 JavaScript tests passed**; one filesystem-writing API test excluded. No files changed. No BLOCKER or MAJOR findings.

**VERDICT: NO-GO.**
