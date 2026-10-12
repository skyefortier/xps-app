No BLOCKER, MAJOR or MINOR findings in `8cc3750..a4ae517`, including this round’s `d37cdd9..a4ae517`. Non-physical-input classification: not applicable; no defect found.

- **Graph handling:** The [guard and ordering](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9332) match the fitter’s strict-equality lookup. Duplicate IDs—including `0`/`-0`—and singleton `NaN` IDs fall back to main’s order. Truthy missing parents, self-links and cycles do likewise, including disconnected malformed components. Numeric `1` and string `'1'` remain distinct. Falsy `linked` values correctly mean no link under the stated field semantics.
- **Adversarial checks:** 18,001 graph cases passed: 3,797 valid graphs matched an independent recursive propagation oracle after one application and remained identical after another; 14,204 malformed graphs retained main’s effective order and matched repeated legacy applications. Coverage included mixed IDs, falsy links and a 1,000-peak reversed chain.
- **Consumers:** No remaining half-propagated read found for well-formed graphs in the Jacobian, certificate, support calculation, record, Batch Fit copy or fallback. Residual evaluations apply the complete dependency pass; final applications are idempotent. Malformed graphs retain main’s existing behavior.
- **Identity:** Reproduced **121/121 exact matches, zero differences or skips**, suppressing artifact writes in memory. The script compares numbers using `Object.is`, including signed zero. Its shared background helpers are unchanged in this unit. This establishes identity for the measured corpus; ordinary models without multilevel dependencies also retain the same effective pass by inspection.
- **Tests:** The comparison executes actual `8cc3750` fitter code. In-memory substitution caught the round 2 duplicate-child defect at `39d04d6`, the missing-root defect at `b6d0f2c`, and the NaN-ID defect at `d37cdd9`. Substituting main failed the chain regressions. These are meaningful regression tests.
- **Scope:** Production changes are confined to selecting the link traversal order. Other changes support documentation, measurement and testing.

Validation: **93 tests passed**. One backend-parity test could not execute because the read-only sandbox provides no writable temporary directory. No files changed.

VERDICT: GO
