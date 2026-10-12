No new BLOCKER, MAJOR, or MINOR findings in the combination at `272cd06`. No lost or incorrectly interleaved production change found.

- **Merge fidelity:** Compared against all three source branches. [runFitLocal](/Users/skyefortier/xps-app/.claude/worktrees/q10/templates/index.html:9272) is exactly 0b’s version plus 0c′’s early refusal. `_applyBackendParams` and `_altPeaks` match 0c; the builder, graph validator, family switch, and fit-entry guards match 0c′. Production files reproduce the union of the reviewed edits.
- **Tests and CI:** Both branches’ retained tests survive. The two superseded malformed-graph tests become one refusal test. The CI floor correctly accounts for this: `610 + 6 + 6 + 8 − 1 = 629`.
- **Graph interaction:** No malformed graph handled by 0b’s fallback escapes 0c′’s guard. Both use strict parent lookup and truthy links; self-lookup failures, missing parents, self-links, and cycles are covered. **287,496 adversarial cases** confirmed this, including **262,884 fallback cases**, all refused. 0c′ deliberately also rejects server-ID collisions such as `1` versus `"1"` and cross-shape links; those never reach propagation.
- **Replacement proof:** The [replacement test](/Users/skyefortier/xps-app/.claude/worktrees/q10/tests/js/local_lm_descent.test.js:731) executes the shipped engine, requires a graph-specific refusal, and checks unchanged peaks. Removing the guard makes it fail. Additional probes confirmed all nine fixtures preserve frozen peaks and an existing non-null fit result. The finite fixtures plus the guard/fallback comparison support the replacement; no unproved reachable fallback remains.
- **Shape and write-back interaction:** Cross-shape refusal precedes fitting, so expression-based write-back does not bypass that policy. Six family-switch probes—using reversed three-level chains and locked, stale children—passed real backend fitting and page write-back, including DSG_LA width transitions, LACX, and Voigt. Displayed component curves matched backend curves.
- **Measurements:** Reproduced **121/121 bit-identical results against `8cc3750`**, zero differences or skips; census reproduced **121 tabs, 530 peaks, 67 links, zero refusals**. These establish corpus compatibility; the separate chain probes cover the new dependency behavior.
- **Other merge changes:** Outside the reviewed edits, executable changes are confined to the documented test replacement, CI floor, and identity-script helper extraction.

Validation: **171 targeted JavaScript tests passed**, using an in-memory bootstrap for Python dependency initialization under read-only restrictions. Full repository and browser suites were not rerun. No files changed.

Non-physical inputs were included in adversarial probes, notably NaN IDs; no finding requiring an input classification remains. Previously accepted unit-level MINORs are unchanged.

VERDICT: GO
