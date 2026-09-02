# Codex adversarial review — DSG_LA m->0 delta-kernel fix (fix-dsgla-m0-collapse, 7e7767e) — RUN B (2026-09-02, overnight session)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 79,457.
Prompt: docs/autofit/codex/dsgla_m0_collapse_review_prompt.txt
Run A on the identical prompt/repo state returned NO-GO rating the shared
normalization finding MAJOR; stricter verdict governs -> unit NO-GO, stopped.

**Findings**

1. MINOR: `templates/index.html:3892` matches backend branch choice for numeric negative `laM`: JS treats `-1 < 0.001` as delta, backend clamps to `0.0` then treats it as delta. `NaN`/`undefined` do not take the JS delta branch; backend direct calls would error or propagate `NaN`, while `peakToBackendSpec()` sanitizes non-finite `p.laM` to `0.4`, so frontend rendering can still diverge on malformed state. That is pre-existing input hygiene, not a regression from this fix.

2. MINOR: Normalization is not fully backend-identical off-grid. Backend normalizes by interpolating sampled `ds_core` at `center` on the data grid (`fitting.py:219-226`); JS normalizes analytically by `laCasaXPSCore(0, ...)` (`templates/index.html:3893-3895`). With a typical 0.05 eV grid and center halfway between samples, this can be about `9.7e-4` of amplitude, well above the asserted `1e-6`. Descending grids are handled by backend reversal, so descending alone is not the issue. The current test grid is ascending and center-on-grid, so it hides this.

3. MINOR: There is a hard visual jump at the branch boundary if state is driven through `0.001`: at `m=0.0009`, the new branch returns the normalized DS core; at `m=0.0011`, the old quadrature can still collapse to zero because its sampled epsilon grid misses the extremely narrow Gaussian. Around the peak this is roughly a full-amplitude jump. Normal UI and local/free backend fitting clamp `laM` to `0.05`, so this is mostly programmatic/imported-state behavior. Pre-fix behavior was worse physically because both sides near zero collapsed, but the fix does expose the discontinuity.

4. MINOR: I do not see a caller relying on collapse-to-zero as a supported “disable peak” path. DSG_LA uses `evalPeakArray()` via the common fallback (`templates/index.html:4015-4023`), chart/render/export/save/results paths also route through `evalPeakArray()`, linked sync copies `laM`, and local LM clamps `laM >= 0.05` (`templates/index.html:6945`). The app already has amplitude/visibility controls for disabling a peak.

5. MINOR: The two new tests pin the basic below-threshold fix, and would catch an unnormalized core or obviously wrong peak normalization for the chosen parameters. They do not pin exact threshold semantics (`m=0.001` vs `<=`), just-above-threshold behavior, off-grid centers, descending grids, or malformed `laM`. So the test is useful but narrower than the “mirrors backend” claim.

VERDICT: GO
