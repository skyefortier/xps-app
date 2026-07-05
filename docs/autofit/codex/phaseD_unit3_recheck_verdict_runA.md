# Codex re-check — Phase D unit 3 (argued DB-exposure disposition) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 82,604.
Prompt: docs/autofit/codex/phaseD_unit3_recheck_prompt.txt

**Disposition**

Central argued disposition: **CLOSED.** I read the Phase D rail as banning invented or estimated empirical values from the structural fallback, not banning relay of the already-wired tiered DB records when they remain sourced, status-limited, and non-operative. Current code at [autofit/grammar.py](/Users/skyefortier/xps-app/autofit/grammar.py:383) attaches DB provenance after structural records and passes `slot_facts=None`; it does not create candidates/windows. Direct probes for `Cu 2p` and `Fe 2p` showed `candidates == []`, `diagnostic_windows == {}`, DB records under `fit_physics:*`, non-`VERIFIED` status, and the explicit “not used to build candidates or windows” note.

Middle grounds: value redaction or key-only exposure is not required for Phase D as written, and would hide useful curation hints. A separate explicit UI flag/filter for “show reference DB values” could be reasonable later, but I would not make it a GO condition.

Run B minor 1: **CLOSED.** The new test at [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:212) would fail if fallback ran before ambiguity checking; direct probe raises `PhaseAmbiguityError`.

Run B minor 2: **CLOSED.** The API pins at [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:306) and [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:325) would fail for the guarded regressions: missing mixed `structural_only`, wiped deep fit, missing structural provenance in `analysis.constants_provenance`, or `least_squares` entering structural degradation.

**New Finding**

MINOR [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:170): the DB-boundary test claims “no windows” but does not assert `g.diagnostic_windows == {}`. Current code is correct; failure scenario is a future refactor populating structural diagnostic windows from `be_window_ev` while leaving candidates empty and provenance sourced, which this test would not catch.

I could not run pytest/API tests because this sandbox lacks `pytest`, `flask`, and `lmfit`; I used static review plus direct `resolve()` probes.

VERDICT: GO
