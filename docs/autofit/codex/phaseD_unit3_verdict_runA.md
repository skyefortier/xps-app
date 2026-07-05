# Codex review — Phase D unit 3 (structural fallback, commit 2ef5b2c + swept-in structural_provenance) — RUN A (2026-07-05)

codex exec, read-only sandbox, model_reasoning_effort=high, gtimeout rails. Tokens: 224,673.
Prompt: docs/autofit/codex/phaseD_unit3_fallback_prompt.txt

1. **BLOCKER** [autofit/grammar.py](/Users/skyefortier/xps-app/autofit/grammar.py:383), [autofit/fit_physics.py](/Users/skyefortier/xps-app/autofit/fit_physics.py:123), [app.py](/Users/skyefortier/xps-app/app.py:731): structural fallback imports fit-physics DB records that contain empirical, fit-enabling numbers.  
   Failure scenario: `resolve([Phase(..., regions=("Cu 2p",))], "Cu 2p", allow_structural_fallback=True)` returns `candidates == []`, but provenance includes `nominal_be_ev`, `be_window_ev`, and `spin_orbit.splitting_ev` for `Cu-2p1/2` and `Cu-2p3/2`. Fe/Mg/Rh/Au/Zn also expose nominal BEs and BE windows. `/api/analyze` returns these in `structure_report` and mixed-method payloads under `analysis.constants_provenance`. This violates the rail that fallback must never create a BE window, splitting, or other fit-enabling number.

2. **MAJOR** [tests/autofit/test_structural_fallback.py](/Users/skyefortier/xps-app/tests/autofit/test_structural_fallback.py:73): the fallback test suite does not guard against the blocker above and partly pins it by asserting a `fit_physics` record exists.  
   Failure scenario: a structural-only Fe 2p response containing `be_window_ev: [706.5, 711]` and `nominal_be_ev: 706.86` passes the current tests. The test should instead assert structural fallback provenance has no fit-enabling DB values unless they came through the D2 cited-value loader contract and still do not create windows/candidates.

Checks that passed in direct probes: meV/keV string guard catches the requested forms and the old pattern would fail; legal bookkeeping strings do not match; cited filtering is element+subshell only including component rows for the same subshell; fallback default remains off; ambiguity/duplicate checks run before fallback; structural-only and structural+deep candidates remain empty/intact as expected; least_squares does not reach the structural degradation path.

VERDICT: NO-GO
