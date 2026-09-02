# Codex adversarial DESIGN review — background architecture (v4) — round 4, RUN B (2026-09-02)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 59,603.
Prompt: docs/autofit/codex/bg_design_r4_review_prompt.txt
Design under review: docs/superpowers/plans/2026-09-02-background-architecture-sealed-fit-record.md (this file records the round-4 state; the committed memo is the final v4+amendments)
Round 4: GO x2 — sealed-record class rules approved; amendments (precise shift transform, non-dirty hydration writer, allowlist structural guard, legacy adapter, local-LM seal contract) folded into the memo as part of the approved design.

**Findings**

1. MAJOR: The auto-fit rigid-shift rule is sound, but must cover every coordinate-bearing field: `be`, peak center values, center bounds, `roiRange`, `settingsSnapshot.bgStart/bgEnd`, and manual-anchor x values if manual background can be used. Counts, background arrays, bg-subtracted arrays, fitted/per-peak y arrays, widths, sigma/stderr, chi2, and R-factor are invariant under the relabeling. Do not expose an unshifted raw `backendResult` as a consumer escape hatch.

2. MAJOR: The dirty funnel is acceptable as the class rule only if the structural test owns the field names, not just obvious `.value =` assignments. A generic helper like `set(id, v)` can evade a weak grep. The design should require all bg/cc DOM writes through `_setBgInput(field, value, { dirty })`, with `dirty:false` allowed only for load/undo/history restore paths.

3. MINOR: Load/restore must be explicitly non-dirty. Restoring a saved seal and its matching UI fields should preserve the seal as clean; user/programmatic bg edits after restore should dirty through the same funnel.

4. MINOR: Local-LM sealing is coherent with parity semantics if the seal identifies/stores the JS-produced background it actually fit, includes local per-peak `y`, and leaves stderr absent/null. The parity suite should not expect a local-LM seal to match Python background output.

5. MAJOR: Migration needs a legacy adapter for old `fitResult` shapes. Existing save/load/history/stack paths currently consume top-level `fitResult.be/bgIntensity/fittedY` and sometimes live `state.peaks`; consumers can move to `fitResult.sealed`, but project load, `.spec.json` load, undo, `_autoSnapshot`, and stack Path B need explicit wrapping/fallback behavior for old saves.

6. MINOR: Ship order is reasonable: 1a-1d should land as one branch because producers, consumers, dirty semantics, and compatibility are coupled. 1c is separable and can ship first if its byte-stability/parity fixtures are updated deliberately.

VERDICT: GO
