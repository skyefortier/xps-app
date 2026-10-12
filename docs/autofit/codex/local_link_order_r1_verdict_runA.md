# Local link order (Q10 0b) — Codex round 1, run A (commit 086378d)

**MAJOR — the extra final χ² evaluation changes cyclic models without freezing the committed state.** At [index.html:9567](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9567), `chiSq(params)` applies links, the next `applyParams(params)` applies them again before commit, and `rawResiduals(params)` applies them once more afterward. The unresolved-graph fallback at [index.html:9337](/Users/skyefortier/xps-app/.claude/worktrees/local-links/templates/index.html:9337) is not idempotent.

Concrete reproducer: one Gaussian, `id:1, linked:1`, center 285, amplitude 100, FWHM 1, offset 1, ratio 0.5; 401 points spanning 280–300, counts 10, background zero.

- Main commits center **287**, amplitude **25**.
- HEAD commits center **288**, amplitude **12.5**.
- HEAD reports χ² **3886.397790**, while its committed peaks give **3712.982693**.
- HEAD reports RMSE **9.738075**, while its committed peaks give **9.622530**.

**Requires non-physical inputs: yes—an inconsistent self-link**, although all numerical values are finite and ordinary. Project loading preserves this graph. The underlying cyclic inconsistency predates the branch; **the extra propagation and changed committed result are introduced here**. Deferring graph validation does not make that behavior unchanged. For this narrowly scoped unit, remove the redundant recomputation and qualify the guarantee to acyclic graphs; broader graph handling belongs in the deferred unit.

The remaining checks support the intended chain fix:

- **Dependency order:** correct for acyclic graphs with unique IDs, arbitrary depth/order, and multiple children. Missing parents retain existing behavior. Mixed string/number IDs retain strict matching. I also checked 500 shuffled forests with mixed ID types: one-pass resolution and idempotence passed. Cycles and their dependent descendants have no such guarantee.
- **Other consumers:** for those acyclic graphs, I found no remaining half-propagated read in the Jacobian, certificate, support calculation, record, Batch Fit, or fallback. For cyclic graphs, repeated propagation still contaminates downstream statistics.
- **Identity measurement:** reproduced **121/121 successful, identical fits** against `8cc3750`, with zero skips; confirmed **57 linked tabs and zero multi-level chains**. A second comparison using deep strict equality also passed. The script’s JSON comparison alone is weaker than literal bit identity, and its corpus evidence is not a universal proof. Its shared background implementation/manual-anchor omission does not affect this corpus or diff.
- **Tests:** all three additions pass. Restoring peak-order propagation leaves the first two passing but **fails the four-level test**, so that regression test is meaningful. Removing only the final recomputation leaves all three passing—as expected for idempotent acyclic propagation. The “not separately testable” claim needs that qualification.
- **Scope:** no unrelated production changes found beyond the cyclic behavior above. The documentation, measurement, extraction adjustment, and CI count change support this unit.

Validation: **90 tests passed; one backend-parity test failed because the read-only sandbox provides no writable temporary directory.** Workspace unchanged.

**VERDICT: NO-GO.**
