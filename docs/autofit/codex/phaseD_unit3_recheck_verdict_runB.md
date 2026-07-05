# Codex re-check — Phase D unit 3 (argued DB-exposure disposition) — RUN B (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 85,225.
Prompt: docs/autofit/codex/phaseD_unit3_recheck_prompt.txt

**Disposition**

- Argued KEPT disposition: **CLOSED**. I do not read the Phase D rail as requiring fit-physics DB values to be stripped from structural no-candidate responses. The rail bans invented fallback values and candidate/window construction; these records are sourced provenance overlays, non-VERIFIED, and `resolve()` states they are reference-only. The D3 goal text also explicitly says the fit-physics DB exposure rides along.
- Boundary guard: **CLOSED in behavior**. Direct probes: `Cu 2p` and `Fe 2p` return `0` candidates, `{}` diagnostic windows, `structural_only == (region,)`, and the new reference-only note.
- Semantics note: **CLOSED** at [autofit/grammar.py](/Users/skyefortier/xps-app/autofit/grammar.py:387).
- Phase ambiguity pin: **CLOSED**. Direct probe and pytest pass; the test would fail if fallback ran before ambiguity resolution.
- API pins: **PARTIAL**. Static path is correct: mixed non-`least_squares` resolves fallback, deep candidates run, and method analysis deep-copies `grammar.provenance`; `least_squares` keeps `grammar=None`. I could not execute Flask API tests because the read-only sandbox has no usable temp dir and app import hits `dill/tempfile`.

**New Findings**

- **MINOR** [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:183): the DB-boundary test does not assert `diagnostic_windows == {}`. Failure scenario: a future refactor exposes DB `be_window_ev` through `grammar.diagnostic_windows` while leaving `candidates == []`; this test still passes, despite the “never windows” claim.
- **MINOR** [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:321): the mixed API pin asserts only that `"Fe 2p"` exists in `analysis.constants_provenance`, not that derived structural records are present. Failure scenario: API/method returns `"Fe 2p": []` or fit-physics-only records; the test still passes.

No BLOCKER/MAJOR findings. Redacting DB values or gating them behind an explicit flag is not required by my reading; it would be a product/UI policy change, not a Phase D correctness blocker.

VERDICT: GO
