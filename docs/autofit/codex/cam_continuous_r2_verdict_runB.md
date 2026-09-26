OpenAI Codex v0.153.4
--------
workdir: /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
model: gpt-6-astra
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 01a0dbe0-6e47-7853-937d-8b12de257e30
--------
user
RECHECK, round 2, of the caM unit: branch fix-cam-continuous, git diff main..HEAD. Read-only. Be adversarial. Findings ranked BLOCKER / MAJOR / MINOR with file:line and a concrete failing scenario, then VERDICT: GO or VERDICT: NO-GO. Budget your time: a verdict is required within the run.

Round 1 (docs/autofit/codex/cam_continuous_verdict_runA.md / runB.md, both NO-GO) found one MAJOR, the same in both: LA's curve jumps where the kernel half-width max(1, ceil(3.5 m/3)) changes (m = 6k/7); with m now free in the local engine, a central difference straddling a jump stalled fits that converge with m held (run A: 201 pts at 0.03 eV, m 48, noise 5 sin(1.77 i), start amplitude 4900, amplitude and m free; run B: 61 pts at 0.05 eV, m 18/7 - 0.001, noise 0.1 sin(3 i), start amplitude 4000 / m 2.6, all free).

What changed (plan §7; commit "fix(caM): Codex round 1"): templates/index.html gained _laKernelHalf(m) (0 below the 1e-3 threshold, else max(1, ceil(3.5*(m/3))), m clamped to [0, 499]), used by laTrueCasaXPS_array AND by runFitLocal's Jacobian: for caM the difference keeps each side inside the current piece - one-sided when one side crosses, the step halved (up to 40 times) when both would, a zero column if none fits. The mirror itself is unchanged. Both reproducers are regression tests in tests/js/local_lm_descent.test.js (they fail on df388ce, pass now; the free fit must not end worse than the held one). scripts/cam_transition_sweep.js (docs/findings/cam/transition_sweep.json): 210 local LA fits around 7 transitions x 5 offsets x 3 grid steps x 2 starts - 0 fail free, 0 held, 0 worse free than held. The local-vs-server re-measurement (plan §4) is unchanged. JS suite 420 tests, 418 pass, 2 todo.

Verify round 1 is closed, then try to break: the piece logic (m exactly on a transition; the 1e-3 threshold piece; the clamps at 0 and 499 interacting with one-sided steps; a zero column - does the certificate or the sensitivity check (SENS_MIN) then fail a fit whose m is legitimately at a transition?); the certificate's own coordinate probes for m (step 1e-3 scaled) crossing transitions - a spurious "descent" found across a jump, a certify-restart loop, MAX_CERTIFY exhaustion; the LM step crossing a jump (the objective is genuinely discontinuous: can damping exhaustion follow a step that lands just across a jump?); linked LA children (m synced) during the Jacobian; anything else in the unit's diff still open, and docs vs code.

Finish with VERDICT: GO or VERDICT: NO-GO.

codex
I’ll check the round-1 fix, then probe the transition boundaries, certification, and linked-child behavior. I’ll keep the review read-only and return a verdict within this run.

exec
/bin/zsh -lc "pwd; git status --short; git diff --stat main..HEAD; rg --files -g AGENTS.md -g '*cam*' -g '*local_lm*' -g '*verdict*'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HfFNgZ1E' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YLIX9XHP' (errno=Operation not permitted)
?? docs/autofit/codex/cam_continuous_r2_verdict_runA.md
?? docs/autofit/codex/cam_continuous_r2_verdict_runB.md
?? docs/autofit/codex/cam_continuous_recheck_prompt.txt
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-5GrS3iFg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HVfV7LmL' (errno=Operation not permitted)
 CLAUDE.md                                          |    45 +-
 .../autofit/codex/cam_continuous_review_prompt.txt |    33 +
 docs/autofit/codex/cam_continuous_verdict_runA.md  | 11123 ++++++++++++++++++
 docs/autofit/codex/cam_continuous_verdict_runB.md  | 11767 +++++++++++++++++++
 docs/findings/cam/lacx_page_vs_server_after.json   |   991 ++
 docs/findings/cam/lacx_page_vs_server_before.json  |   991 ++
 docs/findings/cam/local_server_gap_after_cam.json  |  3375 ++++++
 docs/findings/cam/local_server_gap_after_cam.log   |    18 +
 docs/findings/cam/transition_sweep.json            |     1 +
 .../superpowers/plans/2026-09-25-cam-continuous.md |   125 +
 scripts/cam_transition_sweep.js                    |    24 +
 scripts/lacx_page_vs_server.js                     |    40 +
 scripts/local_server_gap.js                        |     2 +-
 scripts/voigt_saved_vs_refit.js                    |     2 +-
 templates/index.html                               |   144 +-
 tests/js/fit_acceptance.test.js                    |     2 +-
 tests/js/lineshape_parity.test.js                  |    32 +-
 tests/js/lineshape_roundtrip.test.js               |    17 +-
 tests/js/local_lm_descent.test.js                  |    63 +-
 19 files changed, 28693 insertions(+), 102 deletions(-)
scripts/cam_transition_sweep.js
docs/superpowers/plans/2026-09-25-cam-continuous.md
docs/findings/cam/local_server_gap_after_cam.log
docs/findings/cam/local_server_gap_after_cam.json
tests/js/local_lm_descent.test.js
tests/js/local_lm_server_parity_backend.py
docs/autofit/codex/de_finite_bounds_r5_verdict_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round5_runB.md
docs/autofit/codex/autofit_zero_graphite_r6_verdict_runB.md
docs/autofit/codex/dsg_page_evaluator_r3_verdict_runA.md
docs/autofit/codex/unsupported_components_r2_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r14_verdict_runB.md
docs/autofit/codex/self_citation_removal_verdict_round4_runA.md
docs/autofit/codex/refpop_unit2_recheck2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck10_prompt.txt
docs/autofit/codex/phaseD_unit1_recheck2_verdict_runB.md
docs/autofit/codex/dsgla_m0_collapse_verdict_runA.md
docs/autofit/codex/tougaard_bg_fixes_unit2_verdict_runB.md
docs/autofit/codex/seed_perturbation_r4_verdict_runA.md
docs/autofit/codex/plain_english_pass_verdict_round2_runB.md
docs/autofit/codex/phaseD_unit2_recheck4_verdict_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round2_runA.md
docs/autofit/codex/shape_switch_recheck_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck6_prompt.txt
docs/autofit/codex/a03_voigt_eta_verdict_runB.md
docs/autofit/codex/adjudication_unit_verdict.md
docs/autofit/codex/phaseD_unit3_verdict_runA.md
docs/autofit/codex/per_tab_state_verdict_runB.md
docs/autofit/codex/stage6_element_db_verdict.md
docs/autofit/codex/autofit_zero_graphite_r3_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_verdict_runA.md
docs/autofit/codex/autofit_required_r3_verdict_runA.md
docs/autofit/codex/per_tab_state_r4_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r5_verdict_runA.md
docs/autofit/codex/refpop_unit1_recheck_verdict_runA.md
docs/autofit/codex/self_citation_removal_verdict_round1_runB.md
docs/autofit/codex/dsg_page_evaluator_verdict_runA.md
docs/autofit/codex/bg_design_r3_verdict_runA.md
docs/autofit/codex/endpoint_avg_default_unit_r3_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r11_verdict_runA.md
docs/autofit/codex/anchor_cc_r2_verdict_runB.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runB.md
docs/autofit/codex/cofit_gate_r2_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r5_verdict_runB.md
docs/autofit/codex/autofit_zero_graphite_verdict_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round2_runA.md
docs/autofit/codex/roi_clamp_verdict_runA.md
docs/autofit/codex/tougaard_fix_verdict_runA.md
docs/autofit/codex/endpoint_avg_default_unit_r3_verdict_runA.md
docs/autofit/codex/cofit_gate_r2_verdict_runB.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round1_runA.md
docs/autofit/codex/self_citation_removal_verdict_round1_runA.md
docs/autofit/codex/bg_design_r3_verdict_runB.md
docs/autofit/codex/cam_continuous_review_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r11_verdict_runB.md
docs/autofit/codex/anchor_cc_r2_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck8_prompt.txt
docs/autofit/codex/stress_suite_verdicts.md
docs/autofit/codex/a0_local_lm_acceptance_r5_verdict_runB.md
docs/autofit/codex/refpop_unit1_recheck_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_verdict_runB.md
docs/autofit/codex/autofit_zero_graphite_r3_verdict_runB.md
docs/autofit/codex/phaseD_unit2_recheck_verdict_runA.md
docs/autofit/codex/per_tab_state_verdict_runA.md
docs/autofit/codex/shape_switch_recheck_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck13_prompt.txt
docs/autofit/codex/tougaard_bg_fixes_unit2_verdict_runA.md
docs/autofit/codex/dsgla_m0_collapse_verdict_runB.md
docs/autofit/codex/per_tab_state_r4_verdict_runB.md
docs/autofit/codex/autofit_required_r3_verdict_runB.md
docs/autofit/codex/phaseD_unit2_recheck4_verdict_runB.md
docs/autofit/codex/plain_english_pass_verdict_round2_runA.md
docs/autofit/codex/seed_perturbation_r4_verdict_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round2_runB.md
docs/autofit/codex/de_finite_bounds_r5_verdict_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round5_runA.md
docs/autofit/codex/phaseD_unit3_verdict_runB.md
docs/autofit/codex/autofit_zero_graphite_r6_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_r3_verdict_runB.md
docs/autofit/codex/phaseD_unit1_recheck2_verdict_runA.md
docs/autofit/codex/self_citation_removal_verdict_round4_runB.md
docs/autofit/codex/refpop_unit2_recheck2_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck5_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r14_verdict_runA.md
docs/autofit/codex/unsupported_components_r2_verdict_runA.md
docs/autofit/codex/unsupported_components_r5_verdict_runA.md
docs/autofit/codex/w1_local_weighting_r2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r13_verdict_runA.md
docs/autofit/codex/refpop_unit2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r7_verdict_runA.md
docs/autofit/codex/stage8_mcr_verdict.md
docs/autofit/codex/de_finite_bounds_verdict_runB.md
docs/autofit/codex/plain_english_pass_verdict_round3_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck16_prompt.txt
docs/autofit/codex/candpool_recheck2_verdict_runA.md
docs/autofit/codex/find_peaks_endpoint_avg_verdict_runB.md
docs/autofit/codex/c1s_multienv_fix_verdict_runB.md
docs/autofit/codex/de_finite_bounds_r2_verdict_runA.md
docs/autofit/codex/seed_perturbation_r3_verdict_runB.md
docs/autofit/codex/roi_clamp_r2_verdict_runA.md
docs/autofit/codex/dsgla_m0_collapse_r2_verdict_runA.md
docs/autofit/codex/phaseD_unit2_recheck3_verdict_runB.md
docs/autofit/codex/autofit_required_r4_verdict_runB.md
docs/autofit/codex/per_tab_state_r3_verdict_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round4_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round3_runB.md
docs/autofit/codex/reference_bridge_mechanism_verdict_runA.md
docs/autofit/codex/de_finite_bounds_r8_verdict_runB.md
docs/autofit/codex/candpool_review_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r19_verdict_runB.md
docs/autofit/codex/mixed_material_class_unitB_verdict_runB.md
docs/autofit/codex/scattered_starts_a_r2_verdict_runA.md
docs/autofit/codex/autofit_required_verdict_runA.md
docs/autofit/codex/find_peaks_endpoint_avg_r2_verdict_runB.md
docs/autofit/codex/method_tooltips_verdict_runA.md
docs/autofit/codex/de_finite_bounds_r7_verdict_runB.md
docs/autofit/codex/phaseD_unit1_verdict_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round1_runB.md
docs/autofit/codex/autofit_zero_graphite_r4_verdict_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round3_runA.md
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r2_verdict_runB.md
docs/autofit/codex/region_provenance_honesty_verdict_round2_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r16_verdict_runB.md
docs/autofit/codex/stage5_recheck4_verdict.md
docs/autofit/codex/c1s_multienv_fix_recheck2_verdict_runA.md
docs/autofit/codex/bg_design_r4_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r8_verdict_runA.md
docs/autofit/codex/endpoint_avg_default_unit_r4_verdict_runA.md
docs/autofit/codex/fit_full_window_verdict_round1_runB.md
docs/autofit/codex/per_tab_state_r6_verdict_runA.md
docs/autofit/codex/stage2cal_review_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_r2_verdict_runB.md
docs/autofit/codex/plain_english_pass_verdict_round1_runA.md
docs/autofit/codex/tougaard_fix_recheck_verdict_runB.md
docs/autofit/codex/scattered_starts_a_verdict_runA.md
docs/autofit/codex/de_finite_bounds_r3_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r12_verdict_runA.md
docs/autofit/codex/unsupported_components_r4_verdict_runA.md
docs/autofit/codex/refpop_unit3_verdict_runA.md
docs/autofit/codex/anchor_cc_verdict_runB.md
docs/autofit/codex/stage3_u4f_verdict.md
docs/autofit/codex/cam_continuous_verdict_runA.md
docs/autofit/codex/stage5_recheck3_verdict.md
docs/autofit/codex/a0_local_lm_acceptance_r6_verdict_runA.md
docs/autofit/codex/area_sign_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r18_verdict_runB.md
docs/autofit/codex/endpoint_avg_default_unit_verdict_runB.md
docs/autofit/codex/scattered_starts_a_r3_verdict_runA.md
docs/autofit/codex/bg_window_1c_verdict_runA.md
docs/autofit/codex/find_peaks_endpoint_avg_r3_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_r6_verdict_runA.md
docs/autofit/codex/seed_perturbation_r2_verdict_runB.md
docs/autofit/codex/per_tab_state_r2_verdict_runB.md
docs/autofit/codex/stage8_recheck_verdict.md
docs/autofit/codex/phaseD_unit2_recheck2_verdict_runB.md
docs/autofit/codex/stage2_rereview_verdict.md
docs/autofit/codex/c1s_badge_fix_verdict_round6_runA.md
docs/autofit/codex/asym_gl_mismatch_verdict_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round1_runB.md
docs/autofit/codex/de_finite_bounds_r9_verdict_runB.md
docs/autofit/codex/phaseD_unit3_recheck_verdict_runB.md
docs/autofit/codex/stage5_recheck_verdict.md
docs/autofit/codex/a0_local_lm_acceptance_r3_verdict_runB.md
docs/autofit/codex/self_citation_removal_verdict_round2_runA.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runA.md
docs/autofit/codex/noise_model_verdicts.md
docs/autofit/codex/findpeaks_unit2_verdict.md
docs/autofit/codex/a0_local_lm_acceptance_r17_verdict_runB.md
docs/autofit/codex/de_finite_bounds_r6_verdict_runB.md
docs/autofit/codex/stage4_cookbook_verdict2.md
docs/autofit/codex/a0_local_lm_acceptance_recheck7_prompt.txt
docs/autofit/codex/autofit_zero_graphite_r5_verdict_runB.md
docs/autofit/codex/cofit_gate_verdict_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round1_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round3_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round4_runA.md
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runB.md
docs/autofit/codex/fit_full_window_verdict_round3_runB.md
docs/autofit/codex/candpool_recheck_verdict_runA.md
docs/autofit/codex/fwhm_cap_recheck_verdict_runA.md
docs/autofit/codex/per_tab_state_r7_verdict_runA.md
docs/autofit/codex/analyze_ui_verdicts.md
docs/autofit/codex/a03_voigt_eta_r3_verdict_runB.md
docs/autofit/codex/broad_justification_refactor_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck11_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r9_verdict_runA.md
docs/autofit/codex/stage4_cookbook_verdict.md
docs/autofit/codex/a0_local_lm_acceptance_r20_verdict_runA.md
docs/autofit/codex/shape_switch_verdict_runA.md
docs/autofit/codex/fwhm_cap_verdict_runB.md
docs/autofit/codex/endpoint_avg_default_unit_r5_verdict_runA.md
docs/autofit/codex/endpoint_avg_default_unit_r2_verdict_runA.md
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runB.md
docs/autofit/codex/cofit_gate_r3_verdict_runB.md
docs/autofit/codex/region_provenance_honesty_verdict_round1_runA.md
docs/autofit/codex/bg_design_r2_verdict_runB.md
docs/autofit/codex/phaseD_unit1_recheck_verdict_runA.md
docs/autofit/codex/self_citation_removal_verdict_round3_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck2_prompt.txt
docs/autofit/codex/unsupported_components_verdict_runA.md
docs/autofit/codex/broad_justification_recheck_verdict_runB.md
docs/autofit/codex/a03_voigt_eta_r4_verdict_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round2_runB.md
docs/autofit/codex/w1_local_weighting_verdict_runA.md
docs/autofit/codex/mixed_material_class_verdict_runA.md
docs/autofit/codex/c1s_multienv_fix_recheck_verdict_runB.md
docs/autofit/codex/autofit_zero_graphite_r2_verdict_runB.md
docs/autofit/codex/fit_full_window_verdict_round2_runB.md
docs/autofit/codex/seed_perturbation_verdict_runA.md
docs/autofit/codex/unsupported_components_r6_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r10_verdict_runB.md
docs/autofit/codex/anchor_cc_r3_verdict_runA.md
docs/autofit/codex/refpop_unit1_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck14_prompt.txt
docs/autofit/codex/a0_local_lm_acceptance_r4_verdict_runB.md
docs/autofit/codex/cam_continuous_recheck_prompt.txt
docs/autofit/codex/stage9_maxent_verdict.md
docs/autofit/codex/fp_experimental_notice_verdict_runB.md
docs/autofit/codex/per_tab_state_r5_verdict_runB.md
docs/autofit/codex/autofit_required_r2_verdict_runB.md
docs/autofit/codex/seed_perturbation_r5_verdict_runB.md
docs/autofit/codex/de_finite_bounds_r10_verdict_runB.md
docs/autofit/codex/find_peaks_endpoint_avg_r4_verdict_runB.md
docs/autofit/codex/bg_design_verdict_runB.md
docs/autofit/codex/stage2cal_recheck_verdict_runB.md
docs/autofit/codex/stage6_recheck_verdict.md
docs/autofit/codex/fe2p_roi_widen_verdict_runB.md
docs/autofit/codex/cam_continuous_r2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck19_prompt.txt
docs/autofit/codex/dsg_page_evaluator_r2_verdict_runB.md
docs/autofit/codex/refpop_unit2_recheck_verdict_runB.md
docs/autofit/codex/bg_window_1c_r2_verdict_runB.md
docs/autofit/codex/unsupported_components_r3_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r15_verdict_runA.md
docs/autofit/codex/stage5_bayesian_verdict.md
docs/autofit/codex/de_finite_bounds_r4_verdict_runA.md
docs/autofit/codex/phaseD_unit2_verdict_runB.md
docs/autofit/codex/shirley_linear_delist_verdict_runB.md
docs/autofit/codex/findpeaks_unit3_verdict_round2.md
docs/autofit/codex/cofit_gate_r3_verdict_runA.md
docs/autofit/codex/region_provenance_honesty_verdict_round1_runB.md
docs/autofit/codex/tougaard_bg_fixes_unit1_recheck_verdict_runA.md
docs/autofit/codex/endpoint_avg_default_unit_r2_verdict_runB.md
docs/autofit/codex/self_citation_removal_verdict_round3_runB.md
docs/autofit/codex/unsupported_components_verdict_runB.md
docs/autofit/codex/phaseD_unit1_recheck_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck17_prompt.txt
docs/autofit/codex/bg_design_r2_verdict_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round2_runA.md
docs/autofit/codex/a03_voigt_eta_r4_verdict_runA.md
docs/autofit/codex/broad_justification_recheck_verdict_runA.md
docs/autofit/codex/w1_local_weighting_verdict_runB.md
docs/autofit/codex/mixed_material_class_verdict_runB.md
docs/autofit/codex/c1s_multienv_fix_recheck_verdict_runA.md
docs/autofit/codex/autofit_zero_graphite_r2_verdict_runA.md
docs/autofit/codex/seed_perturbation_verdict_runB.md
docs/autofit/codex/fit_full_window_verdict_round2_runA.md
docs/autofit/codex/refpop_unit1_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r10_verdict_runA.md
docs/autofit/codex/anchor_cc_r3_verdict_runB.md
docs/autofit/codex/unsupported_components_r6_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r4_verdict_runA.md
docs/autofit/codex/fp_experimental_notice_verdict_runA.md
docs/autofit/codex/de_finite_bounds_r10_verdict_runA.md
docs/autofit/codex/seed_perturbation_r5_verdict_runA.md
docs/autofit/codex/per_tab_state_r5_verdict_runA.md
docs/autofit/codex/autofit_required_r2_verdict_runA.md
docs/autofit/codex/fe2p_roi_widen_verdict_runA.md
docs/autofit/codex/find_peaks_endpoint_avg_r4_verdict_runA.md
docs/autofit/codex/bg_design_verdict_runA.md
docs/autofit/codex/stage2cal_recheck_verdict_runA.md
docs/autofit/codex/stage9_recheck2_verdict.md
docs/autofit/codex/cam_continuous_r2_verdict_runB.md
docs/autofit/codex/bg_window_1c_r2_verdict_runA.md
docs/autofit/codex/refpop_unit2_recheck_verdict_runA.md
docs/autofit/codex/dsg_page_evaluator_r2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r15_verdict_runB.md
docs/autofit/codex/unsupported_components_r3_verdict_runB.md
docs/autofit/codex/phaseD_unit2_verdict_runA.md
docs/autofit/codex/stage7_recheck_verdict.md
docs/autofit/codex/de_finite_bounds_r4_verdict_runB.md
docs/autofit/codex/findpeaks_unit3_verdict_round1.md
docs/autofit/codex/shirley_linear_delist_verdict_runA.md
docs/autofit/codex/plain_english_pass_verdict_round1_runB.md
docs/autofit/codex/scattered_starts_a_verdict_runB.md
docs/autofit/codex/de_finite_bounds_r3_verdict_runB.md
docs/autofit/codex/tougaard_fix_recheck_verdict_runA.md
docs/autofit/codex/cam_continuous_verdict_runB.md
docs/autofit/codex/refpop_unit3_verdict_runB.md
docs/autofit/codex/anchor_cc_verdict_runA.md
docs/autofit/codex/stage9_recheck_verdict.md
docs/autofit/codex/unsupported_components_r4_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r12_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r6_verdict_runB.md
docs/autofit/codex/area_sign_verdict_runB.md
docs/autofit/codex/scattered_starts_a_r3_verdict_runB.md
docs/autofit/codex/endpoint_avg_default_unit_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r18_verdict_runA.md
docs/autofit/codex/find_peaks_endpoint_avg_r3_verdict_runA.md
docs/autofit/codex/bg_window_1c_verdict_runB.md
docs/autofit/codex/phaseD_unit2_recheck2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck9_prompt.txt
docs/autofit/codex/per_tab_state_r2_verdict_runA.md
docs/autofit/codex/seed_perturbation_r2_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r6_verdict_runB.md
docs/autofit/codex/phaseD_unit3_recheck_verdict_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round6_runB.md
docs/autofit/codex/asym_gl_mismatch_verdict_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round1_runA.md
docs/autofit/codex/de_finite_bounds_r9_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r3_verdict_runA.md
docs/autofit/codex/self_citation_removal_verdict_round2_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r17_verdict_runA.md
docs/autofit/codex/fp_periodic_table_picker_verdict_round2_runB.md
docs/autofit/codex/de_finite_bounds_r6_verdict_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round3_runA.md
docs/autofit/codex/full_window_crop_fix_verdict_round4_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round1_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck12_prompt.txt
docs/autofit/codex/autofit_zero_graphite_r5_verdict_runA.md
docs/autofit/codex/cofit_gate_verdict_runA.md
docs/autofit/codex/candpool_recheck_verdict_runB.md
docs/autofit/codex/fwhm_cap_recheck_verdict_runB.md
docs/autofit/codex/fit_full_window_verdict_round3_runA.md
docs/autofit/codex/tougaard_bg_fixes_unit1_verdict_runA.md
docs/autofit/codex/broad_justification_refactor_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck4_prompt.txt
docs/autofit/codex/a03_voigt_eta_r3_verdict_runA.md
docs/autofit/codex/per_tab_state_r7_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r9_verdict_runB.md
docs/autofit/codex/endpoint_avg_default_unit_r5_verdict_runB.md
docs/autofit/codex/stage2_review1_verdict.md
docs/autofit/codex/fwhm_cap_verdict_runA.md
docs/autofit/codex/findpeaks_unit1_verdict.md
docs/autofit/codex/a0_local_lm_acceptance_r20_verdict_runB.md
docs/autofit/codex/shape_switch_verdict_runB.md
docs/autofit/codex/refpop_unit2_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r13_verdict_runB.md
docs/autofit/codex/unsupported_components_r5_verdict_runB.md
docs/autofit/codex/w1_local_weighting_r2_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r7_verdict_runB.md
docs/autofit/codex/plain_english_pass_verdict_round3_runB.md
docs/autofit/codex/a0_local_lm_acceptance_review_prompt.txt
docs/autofit/codex/de_finite_bounds_verdict_runA.md
docs/autofit/codex/c1s_multienv_fix_verdict_runA.md
docs/autofit/codex/de_finite_bounds_r2_verdict_runB.md
docs/autofit/codex/candpool_recheck2_verdict_runB.md
docs/autofit/codex/find_peaks_endpoint_avg_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck3_prompt.txt
docs/autofit/codex/autofit_required_r4_verdict_runA.md
docs/autofit/codex/per_tab_state_r3_verdict_runA.md
docs/autofit/codex/dsgla_m0_collapse_r2_verdict_runB.md
docs/autofit/codex/phaseD_unit2_recheck3_verdict_runA.md
docs/autofit/codex/roi_clamp_r2_verdict_runB.md
docs/autofit/codex/seed_perturbation_r3_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck15_prompt.txt
docs/autofit/codex/de_finite_bounds_r8_verdict_runA.md
docs/autofit/codex/reference_bridge_mechanism_verdict_runB.md
docs/autofit/codex/c1s_badge_fix_verdict_round4_runB.md
docs/autofit/codex/full_window_crop_fix_verdict_round3_runA.md
docs/autofit/codex/scattered_starts_a_r2_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r19_verdict_runA.md
docs/autofit/codex/mixed_material_class_unitB_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_recheck_prompt.txt
docs/autofit/codex/candpool_review_verdict_runA.md
docs/autofit/codex/method_tooltips_verdict_runB.md
docs/autofit/codex/find_peaks_endpoint_avg_r2_verdict_runA.md
docs/autofit/codex/autofit_required_verdict_runB.md
docs/autofit/codex/phaseD_unit1_verdict_runB.md
docs/autofit/codex/de_finite_bounds_r7_verdict_runA.md
docs/autofit/codex/tooltip_markup_leak_verdict_round3_runB.md
docs/autofit/codex/autofit_zero_graphite_r4_verdict_runA.md
docs/autofit/codex/c1s_badge_fix_verdict_round1_runA.md
docs/autofit/codex/tougaard_bg_fixes_unit2_recheck2_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r2_verdict_runA.md
docs/autofit/codex/a0_local_lm_acceptance_r16_verdict_runA.md
docs/autofit/codex/region_provenance_honesty_verdict_round2_runB.md
docs/autofit/codex/a0_local_lm_acceptance_r8_verdict_runB.md
docs/autofit/codex/bg_design_r4_verdict_runA.md
docs/autofit/codex/c1s_multienv_fix_recheck2_verdict_runB.md
docs/autofit/codex/endpoint_avg_default_unit_r4_verdict_runB.md
docs/autofit/codex/a0_local_lm_acceptance_recheck18_prompt.txt
docs/autofit/codex/stage7_sparse_map_verdict.md
docs/autofit/codex/fit_full_window_verdict_round1_runA.md
docs/autofit/codex/stage2cal_review_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r2_verdict_runA.md
docs/autofit/codex/per_tab_state_r6_verdict_runB.md
docs/autofit/codex/tooltip_markup_leak_verdict_round2_runB.md
docs/autofit/codex/roi_clamp_verdict_runB.md
docs/autofit/codex/autofit_zero_graphite_verdict_runA.md
docs/autofit/codex/a03_voigt_eta_r5_verdict_runA.md
docs/autofit/codex/stage5_recheck2_verdict.md
docs/autofit/codex/tougaard_fix_verdict_runB.md

exec
/bin/zsh -lc 'for p in /AGENTS.md /Users/AGENTS.md /Users/skyefortier/AGENTS.md /Users/skyefortier/xps-app/AGENTS.md /Users/skyefortier/xps-app/.claude/AGENTS.md /Users/skyefortier/xps-app/.claude/worktrees/AGENTS.md AGENTS.md; do if [ -f "$p" ]; then cat "$p"; fi; done; git diff main..HEAD -- templates/index.html tests/js/local_lm_descent.test.js scripts/cam_transition_sweep.js; cat package.json; cat docs/superpowers/plans/2026-09-25-cam-continuous.md' in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-s4TciZo7' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-DrKvJ80u' (errno=Operation not permitted)
diff --git a/scripts/cam_transition_sweep.js b/scripts/cam_transition_sweep.js
new file mode 100644
index 0000000..f18f24f
--- /dev/null
+++ b/scripts/cam_transition_sweep.js
@@ -0,0 +1,24 @@
+const path = require('path'); process.chdir(path.join(__dirname, '..'));   // caM unit, Codex round 1: local LA fits with m free around kernel-width transitions (m = 6k/7) vs m held
+const fs = require('fs'); const html = fs.readFileSync('templates/index.html', 'utf8'); const lines = html.split('\n');
+function extractFn(name) { const re = new RegExp('^(async )?function ' + name + '\\('); const start = lines.findIndex(l => re.test(l)); let depth = 0, seen = false;
+  for (let i = start; i < lines.length; i++) { for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; } if (seen && depth === 0) return lines.slice(start, i + 1).join('\n'); } }
+const NAMES = ['_arrMin','_arrMax','gaussian','lorentzian','pseudoVoigt','asymmGL','doniachSunjic','laCasaXPSCore','laCasaXPS','laTrueCasaXPS','_laKernelHalf','laTrueCasaXPS_array','evalPeak','_dsgAlpha','dsgDeltaKernel_array','_fftRadix2','_circularConvolve','dsgConvolved_array','evalPeakArray','evalAllPeaks','getPeak','runFitLocal','solveLinear','_computeRFactor','_fitStatLabel','_isUnweightedLocal','_isLocalProvenance','_localFitDetail','_isLocalFit','_isLocalModel','_governingProvenance','_localFitCaveat','_fitStatusText','_applyStatCaption','_applyStatDisplay','_updateLocalModelBanner','_componentSupportCore','_supportRootOf','_applySupportVerdicts'];
+const CAV = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');
+function env() { const dom = {}; const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {}, classList: { add() {}, remove() {}, contains: () => false } });
+  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 }; const noop = () => {};
+  const f = new Function('document','state','notify','_CHISQ_TOOLTIP','_LOCALFIT_TOOLTIP','_activeTab','_escHtml','_historyPreview','tabManager','_updateRFactorUI','_updateROIDisplay','renderPeakList','updatePlot','renderResults','_hideFitSpinner','_autoSnapshot','manualAnchorBackground',
+    CAV + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "K";\n' + NAMES.map(extractFn).join('\n\n') + '\nreturn { runFitLocal, evalAllPeaks };');
+  return { ...f({ getElementById: el, querySelectorAll: () => [] }, state, noop, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop, be => be.map(() => 0)), state }; }
+const grid = (lo, hi, st) => Array.from({ length: Math.round((hi - lo) / st) + 1 }, (_, i) => lo + st * i);
+let freeFail = 0, heldFail = 0, worse = 0, n = 0; const fails = [];
+for (const st of [0.03, 0.05, 0.1]) for (const k of [2, 3, 5, 9, 17, 33, 56]) for (const off of [-0.003, -0.0005, 0, 0.0005, 0.003]) for (const startDelta of [-0.4, 0.3]) {
+  const mT = 6 * k / 7 + off; const be = grid(280, 280 + 150 * st, st);
+  const truth = { id: 1, name: 'la', shape: 'LACX', center: 280 + 75 * st + 0.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: mT, glMix: 50, asymmetry: 0 };
+  const run = fixCaM => { const e = env(); e.state.peaks = [{ ...truth }]; const d = e.evalAllPeaks(be, e.state.peaks).map((v, i) => v + 5 * Math.sin(1.77 * i));
+    e.state.peaks = [{ ...truth, amplitude: 4600, caM: Math.max(0.01, mT + startDelta), fixCenter: true, fixFwhm: true, fixCaM }]; const o = e.runFitLocal(be, d, be.map(() => 0)); return { o, chi: e.state.fitResult && e.state.fitResult.chi }; };
+  const fr = run(false), hd = run(true); n++;
+  if (!fr.o.success) { freeFail++; fails.push({ st, k, off, startDelta, msg: fr.o.message }); }
+  if (!hd.o.success) heldFail++;
+  if (fr.o.success && hd.o.success && fr.chi > hd.chi * (1 + 1e-9)) worse++;
+}
+console.log(JSON.stringify({ cases: n, free_failed: freeFail, held_failed: heldFail, free_ended_worse_than_held: worse, first_fails: fails.slice(0, 5) }));
diff --git a/templates/index.html b/templates/index.html
index be8edd2..7a51bf3 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -4061,10 +4061,11 @@ function laCasaXPS(x, center, alpha, beta, mGauss) {
   return laCasaXPSCore(x - center, alpha, beta) / peakVal;
 }
 
-// True LA(α, β, m) [CasaXPS] — piecewise-asymmetric Lorentzian + integer-kernel Gauss conv.
-// Mirrors fitting.py:_la_casaxps_true. BE axis: high-BE side (eps ≥ 0)
-// gets exponent α; low-BE side (eps < 0) gets β. m is integer 0–499 in
-// data-points; σ_pts = m/3.
+// True LA(α, β, m) [CasaXPS] — piecewise-asymmetric Lorentzian + Gauss conv.
+// BE axis: high-BE side (eps ≥ 0) gets exponent α; low-BE side (eps < 0)
+// gets β. Per-point: the base curve only, m IGNORED — the convolution is a
+// grid operation (laTrueCasaXPS_array, via evalPeakArray; parity guard (C)
+// proves no shipped caller reaches the scalar path).
 function laTrueCasaXPS(x, center, fwhm, alpha, beta, m) {
   const F = Math.max(fwhm, 1e-9);
   const A = Math.max(alpha, 1e-3);
@@ -4076,49 +4077,67 @@ function laTrueCasaXPS(x, center, fwhm, alpha, beta, m) {
   return eps >= 0 ? Math.pow(L, A) : Math.pow(L, B);
 }
 
+// LA(α, β, m) on a grid — a literal mirror of fitting._la_casaxps_true
+// (caM unit, 2026-09-25). m is CONTINUOUS in data points (the server fits it
+// continuously so its derivative exists; the page used to round it and
+// build an integer 2m+1 kernel, drawing a curve up to 0.97 % of amplitude
+// and an area up to 1.2 % away from the fitted one on the lab's U 4f
+// components): σ = m/3 points, half-width max(1, ⌈3.5σ⌉), kernel
+// normalised to unit sum, np.convolve(base, kernel, 'same') with the
+// server's trim when the kernel is longer than the grid, normalisation at
+// the grid point nearest the centre (np.argmin |ε|; fallback max), m < 1e-3
+// = the bare base curve (no normalisation), m clamped to [0, 499].
+// Returns the curve for unit amplitude; the caller applies the amplitude.
+// The LA kernel's half-width in points for a given m — the server's
+// `max(1, ceil(3.5·σ))`, σ = m/3, and 0 below the 1e-3 no-convolution
+// threshold. The curve is smooth in m BETWEEN changes of this integer and
+// jumps where it changes (m = 6k/7); the local engine's derivative for m
+// uses it to stay inside one piece (Codex round 1 of the caM unit).
+function _laKernelHalf(m) {
+  const mc = Math.max(0, Math.min(499, Number.isFinite(m) ? m : 0));
+  if (mc < 1e-3) return 0;
+  return Math.max(1, Math.ceil(3.5 * (mc / 3.0)));
+}
+
 function laTrueCasaXPS_array(xArr, center, fwhm, alpha, beta, m) {
   const N = xArr.length;
   const F = Math.max(fwhm, 1e-9);
   const A = Math.max(alpha, 1e-3);
   const B = Math.max(beta,  1e-3);
-  const mInt = Math.max(0, Math.min(499, Math.round(m || 0)));
+  const mc = Math.max(0, Math.min(499, Number.isFinite(m) ? m : 0));
   const base = new Float64Array(N);
   for (let i = 0; i < N; i++) {
     const eps = xArr[i] - center;
     const L = 1.0 / (1.0 + 4.0 * (eps / F) * (eps / F));
     base[i] = eps >= 0 ? Math.pow(L, A) : Math.pow(L, B);
   }
-  if (mInt === 0) return base;
-  const sigma = mInt / 3.0;
-  const klen = 2 * mInt + 1;
-  const kern = new Float64Array(klen);
+  if (mc < 1e-3) return Array.from(base);
+  const sigma = mc / 3.0;
+  const half = _laKernelHalf(mc);
+  const K = 2 * half + 1;
+  const kern = new Float64Array(K);
   let ksum = 0;
-  for (let k = 0; k < klen; k++) {
-    const dk = k - mInt;
-    kern[k] = Math.exp(-(dk * dk) / (2.0 * sigma * sigma));
-    ksum += kern[k];
-  }
-  for (let k = 0; k < klen; k++) kern[k] /= ksum;
-  const out = new Float64Array(N);
+  for (let t = 0; t < K; t++) { const k = t - half; kern[t] = Math.exp(-(k * k) / (2.0 * sigma * sigma)); ksum += kern[t]; }
+  for (let t = 0; t < K; t++) kern[t] /= ksum;
+  // np.convolve(base, kern, 'same'), then the server's trim to len(base):
+  // out[i] = full[off + i], full[j] = Σ_t base[j − t]·kern[t],
+  // off = (K−1)/2 when K ≤ N, else ⌊(N−1)/2⌋ + ⌊(K−N)/2⌋ (pinned against
+  // numpy on 3,000 random (N, K) — plan §2)
+  const off = K <= N ? (K - 1) / 2 : Math.floor((N - 1) / 2) + Math.floor((K - N) / 2);
+  const out = new Array(N);
   for (let i = 0; i < N; i++) {
-    let s = 0;
-    for (let k = 0; k < klen; k++) {
-      const j = i + (k - mInt);
-      if (j >= 0 && j < N) s += base[j] * kern[k];
-    }
-    out[i] = s;
-  }
-  let pkIdx = 0;
-  for (let i = 1; i < N; i++) {
-    if (Math.abs(xArr[i] - center) < Math.abs(xArr[pkIdx] - center)) pkIdx = i;
-  }
-  let pkVal = out[pkIdx];
-  if (pkVal <= 0) {
-    let mx = 0; for (let i = 0; i < N; i++) if (out[i] > mx) mx = out[i];
-    pkVal = mx;
-  }
-  if (pkVal <= 0) return out;
-  for (let i = 0; i < N; i++) out[i] = out[i] / pkVal;
+    const j = off + i;
+    let acc = 0;
+    const t0 = Math.max(0, j - (N - 1)), t1 = Math.min(K - 1, j);
+    for (let t = t0; t <= t1; t++) acc += base[j - t] * kern[t];
+    out[i] = acc;
+  }
+  let pk = 0;
+  for (let i = 1; i < N; i++) if (Math.abs(xArr[i] - center) < Math.abs(xArr[pk] - center)) pk = i;   // np.argmin: first minimum
+  let pv = N ? out[pk] : 0;
+  if (!(pv > 0)) { let mx = -Infinity; for (let i = 0; i < N; i++) if (out[i] > mx) mx = out[i]; pv = mx; }
+  if (!(pv > 0)) return new Array(N).fill(0);
+  for (let i = 0; i < N; i++) out[i] = out[i] / pv;
   return out;
 }
 
@@ -4348,7 +4367,9 @@ function dsgConvolved_array(beArr, center, alpha, beta, mGauss) {
 // DSG_LA (every m: the delta branch below 0.001, the convolution above) so
 // the padding, kernel and normalisation see the whole grid.
 function evalPeakArray(beArr, p) {
-  if (p.shape === 'LACX' && Math.round(p.caM || 0) > 0) {
+  if (p.shape === 'LACX') {
+    // every m, continuous, as the server (caM unit 2026-09-25; it was
+    // Math.round(p.caM) > 0 → integer kernel)
     const yArr = laTrueCasaXPS_array(beArr, p.center, p.fwhm, p.caAlpha, p.caBeta, p.caM);
     const out = new Array(beArr.length);
     const amp = p.amplitude;
@@ -6334,10 +6355,10 @@ function renderShapeControls(p) {
         </div>
       </div>
       <div class="field">
-        <label data-xps-tip="Gaussian convolution kernel width in DATA POINTS (not eV). Integer 0–499. m=0 = no convolution. Effective eV width ≈ (m/3) × dx where dx is the data step size.">m (Gauss kernel pts)
+        <label data-xps-tip="Gaussian convolution kernel width in DATA POINTS (not eV), 0–499. Continuous: the fit returns a fractional value and the curve is drawn with it. m=0 = no convolution. Effective eV width ≈ (m/3) × dx where dx is the data step size.">m (Gauss kernel pts)
           ${!isLinked ? `<button class="lock-btn${p.fixCaM ? ' locked' : ''}" onclick="event.stopPropagation();toggleLock(${p.id},'fixCaM',this)" title="${p.fixCaM ? 'Unlock' : 'Lock'} during fitting">${p.fixCaM ? '&#x1f512;' : '&#x1f513;'}</button>` : ''}
         </label>
-        <input type="number" value="${Math.round(p.caM ?? 50)}" step="1" min="0" max="499"
+        <input type="number" value="${Number.isFinite(p.caM) ? +p.caM.toFixed(2) : 50}" step="0.1" min="0" max="499"
           oninput="updatePeakParam(${p.id},'caM',parseFloat(this.value))">
       </div>
     `;
@@ -8013,12 +8034,11 @@ function _fitStatLabel(fr) {
 // (2026-09-22: Voigt = fixed eta 0.5 on BOTH sides), on Voigt components
 // wherever the two engines reach the same minimum (5 of 9 committed U 4f
 // targets: every component within 4.3 meV, 2.6 % FWHM, 2 % area, 0.12 pp);
-// it still differs on the other 4 U 4f targets (satellite areas up to
-// 8.9 %, 0.77 pp): on one because the LA m is held at its start locally
-// (the gap closes when the server holds m too), on three because the local
-// descent stops at a higher chi2r than the server from the same start
-// (+5 to +13 %, with m held as well) - several minima - and it gives no
-// uncertainties. Unweighted A0-era results differed by more than 100 %.
+// since the caM unit (2026-09-25: LA m continuous and optimised locally) the
+// remaining U 4f differences are all a different minimum, in both
+// directions (docs/findings/cam/local_server_gap_after_cam.json): the local
+// engine above the server by 4.9-13 % chi2r on three targets, below it by
+// 5.7 % on one - and it gives no uncertainties. Unweighted A0-era results differed by more than 100 %.
 // Every site that shows, exports or saves a fit result carries the
 // designation, keyed on persisted identity so reloaded results are labelled.
 const _LOCAL_FIT_CAVEAT = 'Local fit (Poisson-weighted like the server, no uncertainties): a starting point, not a reportable result. Run Fit before reporting.';
@@ -8037,7 +8057,7 @@ function _governingProvenance() {
 function _localFitDetail(fr) {
   return _isUnweightedLocal(fr)
     ? 'Its areas can differ from the server fit by more than 100&nbsp;%.'
-    : 'It can differ from the server fit for LA components (the page holds the smoothing parameter m at its start; the server fits it) or where the model has several minima.';
+    : 'It can differ from the server fit where the model has several minima (either engine can stop in the worse one).';
 }
 // The designation follows the MODEL, not only a live fit result: parameters
 // imported from a .fit.json that was saved from a local fit are a starting
@@ -8208,7 +8228,7 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
     if (param === 'caAlpha')      return Math.max(0.1, Math.min(5.0, v));
     if (param === 'caBeta')       return Math.max(0.1, Math.min(5.0, v));
-    if (param === 'caM')          return Math.max(0,   Math.min(499, Math.round(v)));
+    if (param === 'caM')          return Math.max(0,   Math.min(499, v));   // continuous, as the server (caM unit 2026-09-25)
     return v;
   }
   const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
@@ -8296,10 +8316,10 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     }
     return Math.max(1, Math.abs(vec[j]));
   };
-  // caM is rounded to an integer by its clamp, so a finite difference cannot
-  // see it: it is carried at its starting value (inherited behaviour; see the
-  // A0 follow-up list) and excluded from the stationarity test.
-  const isDiscrete = j => paramMap[j].param === 'caM';
+  // No parameter is discrete: caM was rounded by its clamp and carried at
+  // its start until the caM unit (2026-09-25); it is now continuous, as the
+  // server fits it, and is optimised and tested like any other.
+  const isDiscrete = () => false;
   // MINPACK-style termination: (ftol) actual AND predicted relative
   // reductions both below FTOL, with the linearised model agreeing with
   // the actual reduction; (xtol) relative step below XTOL; (gtol) the
@@ -8340,6 +8360,22 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
       const pPlus = [...params], pMinus = [...params];
       pPlus[j] = clamp(param, params[j] + step);
       pMinus[j] = clamp(param, params[j] - step);
+      if (param === 'caM') {
+        // LA's curve jumps where its kernel half-width changes (m = 6k/7):
+        // a difference straddling a jump is not a derivative and stalled
+        // fits that converge with m held (Codex round 1, caM unit). Keep
+        // each side inside the current piece — one-sided when one side
+        // crosses, the step halved when both would.
+        const piece = _laKernelHalf(params[j]);
+        let hh = step;
+        for (let t = 0; t < 40; t++) {
+          const up = clamp(param, params[j] + hh), dn = clamp(param, params[j] - hh);
+          const upOk = _laKernelHalf(up) === piece, dnOk = _laKernelHalf(dn) === piece;
+          if (upOk || dnOk) { pPlus[j] = upOk ? up : params[j]; pMinus[j] = dnOk ? dn : params[j]; break; }
+          hh /= 2;
+          if (t === 39) { pPlus[j] = params[j]; pMinus[j] = params[j]; }
+        }
+      }
       const span = pPlus[j] - pMinus[j];
       if (span === 0) { J.push(r.map(() => 0)); continue; }
       const rPlus = pPlus[j] === params[j] ? r : residuals(pPlus);
@@ -8444,9 +8480,9 @@ function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
     delete live._backendParams;
   }
 
-  // Degrees of freedom count the parameters this engine actually varies: the
-  // integer-clamped caM is carried at its start value and is not one of them
-  // (continuous parameters temporarily blocked at a wall still count).
+  // Degrees of freedom count the parameters this engine varies (every free
+  // one, since caM became continuous; parameters temporarily blocked at a
+  // wall still count).
   const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
   const dof = Math.max(1, be.length - nVaried);
   const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
@@ -11486,7 +11522,7 @@ function _updateROIDisplay(roiRange) {
   el.textContent = `ROI: ${roiRange.min}\u2013${roiRange.max} eV`;
 }
 
-const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
+const _LOCALFIT_TOOLTIP = "Statistic of the local (in-page) fit. Since unit W1 (2026-09) the local engine is Poisson-weighted like the server, so its \u03c7\u00b2\u1d63 is comparable with the server's, but it gives no parameter uncertainties and can differ from the server fit where the model has several minima. Local results saved earlier were unweighted and are labelled 'Residual variance'. Run Fit with the server available for a reportable result.";
 const _CHISQ_TOOLTIP = "Reduced chi-squared (\u03c7\u00b2\u1d63) measures the goodness of fit weighted by data uncertainty. Computed within the ROI range.\n\n\u2022 \u03c7\u00b2 \u2248 1.0 = ideal fit (residuals match expected noise)\n\u2022 \u03c7\u00b2 >> 1 = poor fit or underestimated uncertainties\n\u2022 \u03c7\u00b2 << 1 = possible overfitting or overestimated uncertainties\n\nNote: a low \u03c7\u00b2 does not guarantee a correct model \u2014 always check the R-factor and visually inspect residuals.";
 
 // Wire up custom tooltip for data-xps-tip elements (R-factor, chi-squared, etc.)
@@ -14529,7 +14565,7 @@ document.addEventListener('mousedown', function(e) {
 <div id="localfit-warn-overlay" class="xps-modal-overlay" onclick="if(event.target===this)this.classList.remove('open')">
   <div class="xps-modal" style="max-width:460px;border-color:var(--amber,#f59e0b)">
     <h3 style="color:var(--amber,#f59e0b)">&#9888; Local fit used (server unreachable) <button class="btn btn-sm" onclick="document.getElementById('localfit-warn-overlay').classList.remove('open')">&#x2715;</button></h3>
-    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit for LA components (m held at its start locally) or where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
+    <p style="font-size:12px;color:var(--text);line-height:1.6;margin:0 0 10px">The server fitting engine (lmfit) could not be reached, so the page's built-in optimiser fitted this spectrum instead. It converged and is Poisson-weighted like the server, but it gives <strong>no parameter uncertainties</strong> and can differ from the server fit where the model has several minima. Treat it as a <strong>starting point, not a reportable result</strong>. Run Fit again when the server is available before quantifying, exporting or reporting.</p>
     <p style="font-size:11px;color:var(--text2);line-height:1.6;margin:0 0 12px"><strong style="color:var(--text)">Possible causes:</strong><br>
     &bull; The server may be offline or restarting<br>
     &bull; The fit request may have timed out<br>
diff --git a/tests/js/local_lm_descent.test.js b/tests/js/local_lm_descent.test.js
index 024ca96..cbe16c8 100644
--- a/tests/js/local_lm_descent.test.js
+++ b/tests/js/local_lm_descent.test.js
@@ -35,7 +35,7 @@ function extractFn(name) {
 }
 
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
   'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
   'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
@@ -477,25 +477,62 @@ test('server parity on GL-type models: weighted local Batch Fit matches lmfit fr
   }
 });
 
-// ── W1 Codex round 1: a never-optimised parameter (integer-clamped caM) is not a degree of freedom ──
-test('reduced chi-square does not count the held caM as a varied parameter', () => {
-  const run = (fixCaM) => {
+// ── caM unit (2026-09-25): m is continuous and OPTIMISED by the local engine, as by the server ──
+// Until this unit the local clamp rounded caM, the finite difference could
+// not see it, and it was carried at its start and left out of the degrees
+// of freedom (W1 Codex round 1 pinned that). Now it moves and counts.
+test('the local engine optimises a free LA m continuously and counts it as a degree of freedom', () => {
+  const be = grid(280, 283, 0.05);
+  const truth = { id: 1, name: 'la', shape: 'LACX', center: 281.5, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 8.66, glMix: 50, asymmetry: 0 };
+  const fitFrom = (fixCaM) => {
     const env = makeEnv();
-    const be = grid(280, 282, 0.1);
-    const truth = { id: 1, name: 'la', shape: 'LACX', center: 281.0, fwhm: 1.0, amplitude: 50, caAlpha: 1.2, caBeta: 1.5, caM: 6, glMix: 50, asymmetry: 0 };
     env.state.peaks = [{ ...truth }];
-    const data = env.evalAllPeaks(be, env.state.peaks).map((v, i) => v * (1 + 0.05 * Math.sin(3 * i)) + 20);
-    env.state.peaks = [{ ...truth, amplitude: 40, fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true, fixCaM }];
-    const out = env.runFitLocal(be, data.map(v => v - 20), new Array(be.length).fill(20));
+    const data = env.evalAllPeaks(be, env.state.peaks);          // noise-free truth at a FRACTIONAL m
+    env.state.peaks = [{ ...truth, caM: 5, amplitude: 4000, fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true, fixCaM }];
+    const out = env.runFitLocal(be, data, new Array(be.length).fill(0));
     assert.equal(out.success, true, JSON.stringify(out));
-    return { chi: env.state.fitResult.chi, chiReduced: out.chiReduced, amp: env.state.peaks[0].amplitude };
+    return { out, p: env.state.peaks[0], fr: env.state.fitResult };
   };
-  const a = run(true), b = run(false);
-  assert.ok(Math.abs(a.amp - b.amp) < 1e-9 && Math.abs(a.chi - b.chi) < 1e-9, 'identical fit either way');
-  assert.ok(Math.abs(a.chiReduced - b.chiReduced) < 1e-12, `same fit, same reduced chi-square: ${a.chiReduced} vs ${b.chiReduced}`);
+  const free = fitFrom(false);
+  assert.ok(Math.abs(free.p.caM - 8.66) < 1e-3, `m recovered continuously: ${free.p.caM}`);
+  assert.ok(!Number.isInteger(free.p.caM), 'not rounded');
+  assert.ok(Math.abs(free.p.amplitude - 5000) < 1e-2, `amplitude ${free.p.amplitude}`);
+  const held = fitFrom(true);
+  assert.equal(held.p.caM, 5, 'a locked m stays where it was locked');
+  // the free fit varies two parameters (amplitude, m), the held one one: dof differ by exactly one
+  assert.equal(Math.round(held.fr.chi / held.out.chiReduced) - Math.round(free.fr.chi / free.out.chiReduced), 1, 'm counts as a degree of freedom when free');
 });
 
 
+// caM unit, Codex round 1: LA's curve JUMPS where the kernel half-width
+// max(1, ceil(3.5 m/3)) changes (m = 6k/7). A central difference straddling
+// a jump stalled fits that converge with m held. The derivative for m now
+// stays inside one piece; both reviewers' reproducers must converge.
+for (const c of [
+  { label: 'run A: 201 pts at 0.03 eV, m 48 (a transition), noisy', be: grid(280, 286, 0.03),
+    truth: { center: 283.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 48 }, noise: i => 5 * Math.sin(1.77 * i),
+    start: { amplitude: 4900 }, lock: { fixCenter: true, fixFwhm: true, fixCaAlpha: true, fixCaBeta: true } },
+  { label: 'run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free', be: grid(280, 283, 0.05),
+    truth: { center: 281.538, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: 18 / 7 - 0.001 }, noise: i => 0.1 * Math.sin(3 * i),
+    start: { amplitude: 4000, caM: 2.6 }, lock: {} },
+]) {
+  test(`an LA fit with m free converges across a kernel-width transition — ${c.label}`, () => {
+    const run = (fixCaM) => {
+      const env = makeEnv();
+      const truth = { id: 1, name: 'la', shape: 'LACX', glMix: 50, asymmetry: 0, ...c.truth };
+      env.state.peaks = [{ ...truth }];
+      const data = env.evalAllPeaks(c.be, env.state.peaks).map((v, i) => v + c.noise(i));
+      env.state.peaks = [{ ...truth, ...c.start, ...c.lock, fixCaM }];
+      const out = env.runFitLocal(c.be, data, new Array(c.be.length).fill(0));
+      return { out, chi: env.state.fitResult && env.state.fitResult.chi };
+    };
+    const free = run(false), held = run(true);
+    assert.equal(held.out.success, true, 'held: ' + JSON.stringify(held.out));
+    assert.equal(free.out.success, true, 'free: ' + JSON.stringify(free.out));
+    assert.ok(free.chi <= held.chi * (1 + 1e-9), `freeing m cannot end worse than holding it: ${free.chi} vs ${held.chi}`);
+  });
+}
+
 test('recovery from an amplitude of exactly zero (the new floor is not a trap)', () => {
   const env = makeEnv();
   const be = grid(280, 290, 0.05);
cat: package.json: No such file or directory
# The `caM` unit — LA's m continuous on the page and in the local engine (2026-09-25)

Branch `fix-cam-continuous` off main `3ea3b8b`. Queued by the owner after
A03 and the fail-open sweep ("Then the caM clamp"). The record defined the
unit as two halves (A03 plan §5/§6; CLAUDE.md): the page draws LA with m
ROUNDED to an integer 2m+1 kernel while the server fits m continuously, and
the local engine rounds m in its clamp and carries it at its start.

## 1. Contract

The server's continuous m is deliberate (`_la_casaxps_true`: "m flows
through continuously so lmfit's finite-difference Jacobian in m is
non-singular" — rounding made the function locally constant in m and
poisoned the covariance of every other parameter). So, as for DS+G
(2026-09-22), the PAGE MIRRORS THE SERVER; nothing on the server changes.

## 2. Measured before (`scripts/lacx_page_vs_server.js`)

All 108 LA components in the seven committed projects, at their saved
parameters on their tab's ROI grid (106 carry a fractional, server-fitted
m; 107 are unlocked):

| | before | after |
|---|---:|---:|
| max page − server, of amplitude | median 0.29 %, max 0.97 % | max 7.4e-16 |
| area, page vs server | median 0.33 %, max 1.18 % | max 5.6e-14 % |

`docs/findings/cam/lacx_page_vs_server_{before,after}.json`. The "before"
column is also what a student sees change on opening a saved U 4f project:
the page's LA areas move by 0.33 % at the median, 1.2 % at most, to the
curve the server actually fitted.

## 3. Sites

| # | site | before | after |
|---|---|---|---|
| 1 | `laTrueCasaXPS_array` | integer m = round(caM), kernel 2m+1, σ = m/3, own convolution and peak search | literal mirror of `_la_casaxps_true`: m clamped to [0, 499], continuous σ = m/3, half-width max(1, ⌈3.5σ⌉), unit-sum kernel, `np.convolve(base, k, 'same')` + the server's trim when the kernel is longer than the grid (index formula pinned against numpy on 3,000 random (N, K)), normalisation at `argmin |ε|` (first minimum), fallback max, m < 1e-3 = bare base curve |
| 2 | `evalPeakArray` LA gate | array path only when `Math.round(caM) > 0` | every LA through the array path (it handles m < 1e-3 itself) |
| 3 | `laTrueCasaXPS` (scalar) | base curve, m ignored | unchanged; comment corrected; parity guard (C) proves no shipped caller |
| 4 | m input (`renderPeakForm`) | `Math.round(caM)`, step 1, "Integer 0–499" | the value to 2 dp, step 0.1, "continuous" |
| 5 | `runFitLocal` clamp | `Math.round(v)` | continuous clamp to [0, 499] |
| 6 | `runFitLocal` `isDiscrete` (Jacobian skip, sensitivity, certificate, dof, per-component support p) | `caM` discrete → never moved, not a dof | nothing discrete: m is optimised, certified and counted |
| 7 | local-fit caveat (`_localFitDetail`, `_LOCALFIT_TOOLTIP`, fallback banner) | "differ … for LA components (m held at its start locally)" | "differ … where the model has several minima" (§4) |
| 8 | `peakToBackendSpec` (`m`, `fix_m`), `_applyBackendParams` (writes `par.m`), exports (`p.caM`), Find Peaks mapping (`o.caM = p.m`), `syncKeys` / `LINK_SYNC_KEYS`, `_STARTS_MODEL_FIELDS`, Python twins | carry the value as is | unchanged (they already carried the fractional server value) |
| 9 | defaults (`caM: 50`, `fixCaM: true`; server `fix_m` default true) | — | unchanged |

## 4. The re-measurement (`scripts/local_server_gap.js` → `docs/findings/cam/local_server_gap_after_cam.json`)

W1's 18 targets, local engine vs server from the same scaled start.

| U 4f target | local χ²ᵣ vs server, A03 | after this unit | max Δarea, A03 → after |
|---|---:|---:|---:|
| Scan_0, 2, 3, 7 (same minimum) | −0.2 to +0.5 % | +0.1 to +0.8 % | ≤ 1.74 % → ≤ 0.34 % |
| Scan_1 | +1.3 % | +1.6 % | 1.95 % → 1.57 % |
| Scan_4 | +9.6 % | +4.9 % | 8.32 % → 4.30 % |
| Scan_5 | +10.1 % | +9.2 % | 6.65 % → 5.25 % |
| Scan_6 | −5.0 % | −5.7 % | 8.88 % → 11.25 % |
| Scan_8 | +12.7 % | +13.0 % | 8.31 % → 7.91 % |

C 1s unchanged (8 of 9 within 3.8 meV / 0.5 % / 1.4 % / 0.32 pp; Scan_4 is
findings §2). On the four U 4f targets where both engines reach the same
minimum every component now agrees within 3.0 meV, 0.49 % FWHM, 0.34 %
area, 0.02 pp.

Reading: the `caM` half of the gap is closed — on Scan_6, the one target
A03's control arm attributed to the clamp, the local engine now MOVES m and
lands 5.7 % BELOW the server (the server, m free, stops in a worse
minimum; with m held it reaches 2.629, the local 2.639). Everything left is
a different minimum, in BOTH directions: the local engine above the server
on Scan_4/5/8 (+4.9 to +13 %), below it on Scan_6. That is the
worse-minimum finding A03 recorded, not a model difference.

**The "starting point" label.** The owner's condition was a re-measurement
after the `caM` clamp and the worse-minimum work. The first is done; the
second is not, and three of nine U 4f targets still land in a worse local
minimum. Recommendation: the label STAYS; its wording now names only
"several minima" and the absent uncertainties. Owner's call.

## 5. Verification

- `tests/js/lineshape_parity.test.js`: (A) LACX m > 0 and (D) LACX m > 0
  (fractional m, the 1e-3 threshold, 499) are hard assertions; new (D‴)
  sweeps the LA box on six more grids incl. 9- and 2-point grids (kernel
  longer than the grid). `tests/js/lineshape_roundtrip.test.js`: no shape
  has a known gap; LA m locked at 499 and at a fractional 8.66 round-trip
  with the curve compared. `tests/js/local_lm_descent.test.js`: the
  W1-round-1 test pinning "held caM is not a dof" replaced by one pinning
  continuous recovery of m (8.66 from 5), a locked m unmoved, and one more
  dof when free. JS suite (after round 1): 420 tests, 418 pass, 2 todo
  (the scalar evaluators of the two convolved shapes, by design).
- Browser check (`browser_check_cam.py`, dev :5151): committed
  UCl4-graphite U4f Scan loads with m 8.2 shown as "8.2"; Run Fit → LA
  drawn vs fitted 1.1e-13 of amplitude (was 5.6e-3), Results area equal to
  the server curve's (was −0.66 %); Batch Fit onto U4f Scan_1 converges and
  moves m (6.49 → 7.66); no page errors.
- Python suite: 993 passed, 7 skipped (on the round-0 commit df388ce; the
  round-1 change is page-only).

## 6. Release-note line

LA(α, β, m) components are now drawn, integrated and exported with the same
continuous m the server fits (the page rounded it to a whole number of
points): opening a saved U 4f project moves an LA component's area by
0.33 % at the median and 1.2 % at most, to the curve that was actually
fitted. Batch Fit now fits m instead of holding it. m is shown to 0.01.

## 7. Codex rounds

**Round 1 (`docs/autofit/codex/cam_continuous_verdict_run{A,B}.md`):
NO-GO ×2, one finding, the same in both.** MAJOR — LA's curve JUMPS where
the kernel half-width max(1, ⌈3.5 m/3⌉) changes (m = 6k/7), so a
central-difference step for m that straddles a jump is not a derivative;
with m now free, local fits that converge with m held stalled and failed
(run A: 201 points at 0.03 eV, m 48; run B: 61 points at 0.05 eV,
m 18/7 − 0.001). lmfit escapes it only because its step is ~1e-8. Fixed
in the local engine's Jacobian, not in the mirror: one shared
`_laKernelHalf(m)` (used by the evaluator and the Jacobian, so they cannot
disagree) and a difference that stays inside the current piece —
one-sided when one side crosses, the step halved when both would. Both
reproducers are regression tests (they fail on df388ce, pass now; freeing
m never ends worse than holding it). `scripts/cam_transition_sweep.js`
(→ `docs/findings/cam/transition_sweep.json`): 210 local LA fits started
around 7 transitions × 5 offsets × 3 grid steps × 2 starts — 0 fail with m
free, 0 with m held, 0 end worse free than held. The §4 re-measurement,
re-run on the fixed engine, is unchanged to the digits quoted.

exec
/bin/zsh -lc "sed -n '8100,8495p' templates/index.html; sed -n '1,120p' tests/js/local_lm_descent.test.js; rg --files -g AGENTS.md -g '*package*' -g '*pytest*' -g '*requirements*'; git diff main..HEAD -- CLAUDE.md tests/js/lineshape_parity.test.js tests/js/lineshape_roundtrip.test.js scripts/lacx_page_vs_server.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
function _provenanceOf(tab) {
  if (!tab) return null;
  if (tab.modelProvenance) return JSON.parse(JSON.stringify(tab.modelProvenance));
  const fr = tab.fitResult;
  if (!_isLocalFit(fr)) return null;
  return { objective: fr.objective || null, engine: fr.engine || 'local', status: fr.status || null,
           weighting: fr.weighting || null, chiReduced: fr.chiReduced ?? null,
           reportable: false, caveat: _localFitCaveat(fr), derivedFrom: 'local_fit' };
}
function _localFitCaveat(fr) {
  if (!_isLocalFit(fr)) return '';
  return _isUnweightedLocal(fr) ? _LOCAL_FIT_CAVEAT_UNWEIGHTED : _LOCAL_FIT_CAVEAT;
}
function _fitStatusText(fr) {
  const tag = !_isLocalFit(fr) ? '' : (_isUnweightedLocal(fr) ? ' (starting point)' : ' (local, starting point)');
  return _fitStatLabel(fr) + ' = ' + fr.chiReduced.toFixed(2) + tag;
}
function _applyStatCaption(fr) {
  const cap = document.getElementById('sb-chi-caption');
  if (!cap) return;
  cap.innerHTML = !_isLocalFit(fr) ? '&#967;&#178;&#7523;:'
    : (_isUnweightedLocal(fr) ? 'Residual variance (starting point):' : '&#967;&#178;&#7523; (local, starting point):');
}
// The statistic is displayed as ONE unit — header text + tooltip, status-bar
// caption + value — from the same fit result, or all cleared. Refreshing
// any one of them alone can pair a local value with a chi-square caption
// (Codex round 9).
function _applyStatDisplay(fr) {
  const fq = document.getElementById('fit-quality');
  const sb = document.getElementById('sb-chi');
  if (fr && Number.isFinite(fr.chiReduced)) {
    if (fq) { fq.textContent = _fitStatusText(fr); fq.setAttribute('data-xps-tip', _isLocalFit(fr) ? _LOCALFIT_TOOLTIP : _CHISQ_TOOLTIP); }
    if (sb) sb.textContent = fr.chiReduced.toFixed(3);
  } else {
    if (fq) { fq.innerHTML = '&#967;&#178; &mdash;'; fq.removeAttribute('data-xps-tip'); }
    if (sb) sb.textContent = '\u2014';
  }
  _applyStatCaption(fr);
  _updateLocalModelBanner();
}

// Local Levenberg-Marquardt: the fallback engine, and the ONLY engine Batch
// Fit uses.
//
// ACCEPTANCE RULE (unit A0, 2026-09-15): this function never writes to
// state.peaks or state.fitResult unless the optimiser converged. It works on
// a copy of the peak list and commits the copy on success; on
// non-convergence the previous peaks and the previous fit result are left
// exactly as they were and the caller receives { success: false }.
//
// History: from the initial commit (f20d71b) until this unit the update
// step solved JtJ.dp = +Jt.r with r = data - model, i.e. an ASCENT step, so
// every step was rejected, lambda inflated past 1e8 and the loop returned
// the STARTING model announced as "Fit complete (local LM)". The
// convergence test also compared chi-square with itself after acceptance.
// Both are pinned by tests/js/local_lm_descent.test.js, which replays the
// committed lab project; the proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md.
function runFitLocal(be, bgSubtracted, bgIntensity, options = {}) {
  const maxIter = Number.isFinite(options.maxIterations) ? options.maxIterations : 3000;
  const fail = (message, iterations) => {
    _hideFitSpinner();
    document.getElementById('sb-msg').textContent = 'Local fit failed';
    notify('Local fit did not converge: ' + message + ' Previous peaks and result kept.', 'red', true);
    return { success: false, engine: 'local', message, iterations: iterations || 0 };
  };
  if (!Array.isArray(be) || be.length < 2 ||
      !Array.isArray(bgSubtracted) || bgSubtracted.length !== be.length ||
      !Array.isArray(bgIntensity) || bgIntensity.length !== be.length ||
      !be.every(Number.isFinite) || !bgSubtracted.every(Number.isFinite) || !bgIntensity.every(Number.isFinite)) {
    return fail('invalid or non-finite data in the fitting region.');
  }
  // POISSON WEIGHTS (unit W1): the same weighting fitting.run_fit applies on
  // the server — sigma = sqrt(raw counts), floored at 1, where the raw
  // counts are the background-subtracted signal plus the background.
  const _w = be.map((_, i) => 1 / Math.sqrt(Math.max(bgSubtracted[i] + bgIntensity[i], 1)));
  // Work on copies: live peaks are touched only on success.
  const work = state.peaks.map(p => ({ ...p }));
  if (!work.length) return fail('no peaks to fit.');
  const workPeak = id => work.find(q => q.id === id);

  const freeParams = [];
  const paramMap = [];
  for (const p of work) {
    if (!p.linked) {
      if (!p.fixCenter)    { freeParams.push(p.center);    paramMap.push({id: p.id, param: 'center'}); }
      if (!p.fixFwhm && p.shape !== 'DSG_LA') { freeParams.push(p.fwhm); paramMap.push({id: p.id, param: 'fwhm'}); }
      if (!p.fixAmplitude) { freeParams.push(p.amplitude); paramMap.push({id: p.id, param: 'amplitude'}); }
      if ((p.shape === 'GL' || p.shape === 'asym-GL') && !p.fixGlMix) {
        freeParams.push(p.glMix); paramMap.push({id: p.id, param: 'glMix'});
      }
      if (p.shape === 'asym-GL' && !p.fixAsymmetry) {
        freeParams.push(p.asymmetry); paramMap.push({id: p.id, param: 'asymmetry'});
      }
      if (p.shape === 'DS' && !p.fixDsAlpha) {
        freeParams.push(p.dsAlpha); paramMap.push({id: p.id, param: 'dsAlpha'});
      }
      if (p.shape === 'DS' && !p.fixDsGamma) {
        freeParams.push(p.dsGamma); paramMap.push({id: p.id, param: 'dsGamma'});
      }
      if (p.shape === 'DSG_LA') {
        if (!p.fixLaAlpha) { freeParams.push(Number.isFinite(p.laAlpha) ? p.laAlpha : 0.10); paramMap.push({id: p.id, param: 'laAlpha'}); }
        if (!p.fixLaBeta)  { freeParams.push(Number.isFinite(p.laBeta)  ? p.laBeta  : 0.3);  paramMap.push({id: p.id, param: 'laBeta'}); }
        if (!p.fixLaM)     { freeParams.push(Number.isFinite(p.laM)     ? p.laM     : 0.4);  paramMap.push({id: p.id, param: 'laM'}); }
      }
      if (p.shape === 'LACX') {
        if (!p.fixCaAlpha) { freeParams.push(Number.isFinite(p.caAlpha) ? p.caAlpha : 1.0); paramMap.push({id: p.id, param: 'caAlpha'}); }
        if (!p.fixCaBeta)  { freeParams.push(Number.isFinite(p.caBeta)  ? p.caBeta  : 1.0); paramMap.push({id: p.id, param: 'caBeta'}); }
        if (!p.fixCaM)     { freeParams.push(Number.isFinite(p.caM)     ? p.caM     : 50);  paramMap.push({id: p.id, param: 'caM'}); }
      }
    }
  }
  if (!freeParams.every(Number.isFinite)) return fail('a free parameter is not a finite number.');

  // Parameter box. The amplitude floor is 0, the server's, since unit step (b)
  // (owner decision 2026-09-18: zero allowed in both engines; a component at
  // its floor is an explicit outcome). The active-set step holds a parameter
  // pushed into the wall, and paramScale is floored at 1, so a zero amplitude
  // is a valid, stationary point rather than a division by zero.
  function clamp(param, v) {
    if (param === 'fwhm')         return Math.max(0.1, Math.min(15, v));
    if (param === 'amplitude')    return Math.max(0, v);
    if (param === 'glMix')        return Math.max(0, Math.min(100, v));
    if (param === 'asymmetry')    return Math.max(0, Math.min(1, v));
    if (param === 'dsAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'dsGamma')      return Math.max(0, Math.min(5.0, v));
    if (param === 'laAlpha')      return Math.max(0, Math.min(0.49, v));
    if (param === 'laBeta')       return Math.max(0.05, Math.min(2.0, v));
    if (param === 'laM')          return Math.max(0.05, Math.min(4.0, v));
    if (param === 'caAlpha')      return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caBeta')       return Math.max(0.1, Math.min(5.0, v));
    if (param === 'caM')          return Math.max(0,   Math.min(499, v));   // continuous, as the server (caM unit 2026-09-25)
    return v;
  }
  const LINK_SYNC_KEYS = ['glMix', 'asymmetry', 'dsAlpha', 'dsGamma',
    'laAlpha', 'laBeta', 'laM', 'caAlpha', 'caBeta', 'caM'];

  function applyParams(params) {
    for (let i = 0; i < params.length; i++) {
      const { id, param } = paramMap[i];
      const p = workPeak(id);
      if (p) p[param] = clamp(param, params[i]);
    }
    // Linked peaks follow their parent: centre + offset, amplitude x ratio,
    // and every lineshape parameter (the same constraint set the backend
    // enforces through lmfit expressions).
    for (const q of work) {
      if (!q.linked) continue;
      const parent = workPeak(q.linked);
      if (!parent) continue;
      if (Number.isFinite(q.linkOffset)) q.center = parent.center + q.linkOffset;
      if (Number.isFinite(q.linkRatio))  q.amplitude = parent.amplitude * q.linkRatio;
      q.fwhm = parent.fwhm;
      for (const k of LINK_SYNC_KEYS) if (parent[k] !== undefined) q[k] = parent[k];
    }
  }

  function rawResiduals(params) {
    applyParams(params);
    const model = evalAllPeaks(be, work);
    return be.map((_, i) => bgSubtracted[i] - model[i]);
  }
  // weighted residual: what the optimiser minimises (chi = sum of squares)
  function residuals(params) {
    return rawResiduals(params).map((v, i) => v * _w[i]);
  }

  function chiSq(params) {
    const r = residuals(params);
    return r.reduce((s, v) => s + v * v, 0);
  }

  let params = freeParams.map((v, i) => clamp(paramMap[i].param, v));
  let chi = chiSq(params);
  if (!Number.isFinite(chi)) return fail('the model is not finite at the starting parameters.');
  let lambda = 0.001;
  // Feasible-descent certificate (see PROBE_REL below). Returns true when
  // no single-parameter feasible move improves the residual by more than
  // FTOL; otherwise moves to the best such point and returns false.
  function certify() {
    applyParams(params);                     // working copy = current point
    let bestChi = chi, bestParams = null;
    for (let j = 0; j < params.length; j++) {
      if (isDiscrete(j)) continue;
      for (const sgn of [-1, 1]) {
        const trial = [...params];
        trial[j] = clamp(paramMap[j].param, params[j] + sgn * PROBE_REL * paramScale(j, params));
        if (trial[j] === params[j]) continue;
        const c = chiSq(trial);
        if (Number.isFinite(c) && c < bestChi) { bestChi = c; bestParams = trial; }
      }
    }
    applyParams(params);
    if (bestParams && bestChi < chi * (1 - FTOL)) {
      params = bestParams; chi = bestChi; certifyRestarts++;
      lambda = Math.max(lambda, 1e-3);
      return false;
    }
    return true;
  }
  // Finite-difference step per parameter. A centre's natural scale is the
  // peak WIDTH, not its binding energy: h*|285 eV| = 0.03 eV is wider than
  // a narrow peak and gave misleading derivatives (Codex round 1).
  const H_REL = 1e-4;
  // Scale of parameter j at the parameter VECTOR `vec` — a pure function of
  // the vector, never of the mutable working copy (which the Jacobian loop
  // leaves at its last perturbation — Codex round 5). A centre's scale is
  // its peak's width: from the vector when the width is free, from the
  // (never perturbed) fixed value otherwise.
  const fwhmIndex = {};
  paramMap.forEach((d, k) => { if (d.param === 'fwhm') fwhmIndex[d.id] = k; });
  const paramScale = (j, vec) => {
    const { id, param } = paramMap[j];
    if (param === 'center') {
      const w = fwhmIndex[id] !== undefined ? vec[fwhmIndex[id]] : (workPeak(id) || {}).fwhm;
      return Math.max(0.05, Number.isFinite(w) ? w : 1);
    }
    return Math.max(1, Math.abs(vec[j]));
  };
  // No parameter is discrete: caM was rounded by its clamp and carried at
  // its start until the caM unit (2026-09-25); it is now continuous, as the
  // server fits it, and is optimised and tested like any other.
  const isDiscrete = () => false;
  // MINPACK-style termination: (ftol) actual AND predicted relative
  // reductions both below FTOL, with the linearised model agreeing with
  // the actual reduction; (xtol) relative step below XTOL; (gtol) the
  // largest cosine between the residual and any Jacobian column below
  // GTOL. Tiny steps alone never count. FTOL = 1e-6 (relative chi-square):
  // on real 6-component C1s data with a vanished component the optimiser
  // otherwise crawls a flat valley for thousands of iterations changing
  // chi-square in its 7th digit and no parameter in its 5th.
  const FTOL = 1e-6, XTOL = 1e-8, GTOL = 1e-6, SENS_MIN = 1e-12;
  // CERTIFICATE: a tentative convergence (gtol / ftol / xtol) is accepted
  // only if no feasible move of PROBE_REL (scaled) in any single free
  // parameter reduces the residual by more than FTOL of its value. If one
  // does, that point is taken and iteration continues (Codex round 3: the
  // linearised model is not a stationarity certificate; a column-norm
  // cutoff froze determined parameters).
  const PROBE_REL = 1e-3, MAX_CERTIFY = 200;
  // No exit is exempt from the certificate: a tiny absolute residual is
  // still probed relatively (Codex round 4). The certificate is a
  // single-parameter (coordinate) feasible-descent check, not a proof of a
  // local minimum along coupled directions; the LM step handles coupling
  // during optimisation.
  let converged = params.length === 0 || (chi === 0 && certify());
  let iterations = 0;
  let acceptedSteps = 0;
  let certifyRestarts = 0;

  for (let iter = 0; iter < maxIter && !converged; iter++) {
    iterations++;
    if (certifyRestarts > MAX_CERTIFY) return fail('could not certify a stationary point after ' + iterations + ' iterations.', iterations);
    const r = residuals(params);
    const n = params.length;
    // Central-difference Jacobian d r / d p, stepping inside the parameter
    // box (one-sided at a wall).
    const J = [];
    for (let j = 0; j < n; j++) {
      const { param } = paramMap[j];
      const step = H_REL * paramScale(j, params);
      const pPlus = [...params], pMinus = [...params];
      pPlus[j] = clamp(param, params[j] + step);
      pMinus[j] = clamp(param, params[j] - step);
      if (param === 'caM') {
        // LA's curve jumps where its kernel half-width changes (m = 6k/7):
        // a difference straddling a jump is not a derivative and stalled
        // fits that converge with m held (Codex round 1, caM unit). Keep
        // each side inside the current piece — one-sided when one side
        // crosses, the step halved when both would.
        const piece = _laKernelHalf(params[j]);
        let hh = step;
        for (let t = 0; t < 40; t++) {
          const up = clamp(param, params[j] + hh), dn = clamp(param, params[j] - hh);
          const upOk = _laKernelHalf(up) === piece, dnOk = _laKernelHalf(dn) === piece;
          if (upOk || dnOk) { pPlus[j] = upOk ? up : params[j]; pMinus[j] = dnOk ? dn : params[j]; break; }
          hh /= 2;
          if (t === 39) { pPlus[j] = params[j]; pMinus[j] = params[j]; }
        }
      }
      const span = pPlus[j] - pMinus[j];
      if (span === 0) { J.push(r.map(() => 0)); continue; }
      const rPlus = pPlus[j] === params[j] ? r : residuals(pPlus);
      const rMinus = pMinus[j] === params[j] ? r : residuals(pMinus);
      J.push(rPlus.map((v, i) => (v - rMinus[i]) / span));
    }
    const JtJ = Array.from({length: n}, () => new Array(n).fill(0));
    const Jtr = new Array(n).fill(0);
    for (let a = 0; a < n; a++) {
      for (let b = 0; b < n; b++) {
        for (let i = 0; i < r.length; i++) JtJ[a][b] += J[a][i] * J[b][i];
      }
      for (let i = 0; i < r.length; i++) Jtr[a] += J[a][i] * r[i];
    }
    if (!Jtr.every(Number.isFinite) || !JtJ.every(row => row.every(Number.isFinite))) {
      return fail('the model derivative is not finite.', iterations);
    }
    // Sensitivity: a model that does not respond to any free parameter here
    // (e.g. a peak far outside the window) cannot be optimised — that is a
    // failure, not a stationary point.
    let sens = 0;
    for (let j = 0; j < n; j++) if (!isDiscrete(j)) sens = Math.max(sens, JtJ[j][j] * paramScale(j, params) ** 2);
    if (n > 0 && sens / Math.max(chi, 1e-300) < SENS_MIN) {
      return fail('the model has no measurable sensitivity to its free parameters in this region.', iterations);
    }
    // ACTIVE SET: a parameter whose descent direction points into a wall of
    // the parameter box (or that has no sensitivity, or is discrete) is held
    // FIXED for this step. Solving the joint system with such a parameter
    // and then clipping it would leave the other components of the step
    // meaningless and let a tiny "agreed" step pass the ftol test at a
    // non-stationary point (Codex round 2). With r = data - model,
    // d(chi)/dp_j = +2 * (J_j . r), so the descent direction is -sign(J_j . r).
    const active = [];
    let gradCos = 0;
    const rNorm = Math.sqrt(chi);
    for (let j = 0; j < n; j++) {
      if (isDiscrete(j) || !(JtJ[j][j] > 0)) continue;
      if (Jtr[j] !== 0) {
        const probe = clamp(paramMap[j].param, params[j] - Math.sign(Jtr[j]) * 1e-6 * paramScale(j, params));
        if (probe === params[j]) continue;          // blocked by the box
      }
      active.push(j);
      if (rNorm > 0) gradCos = Math.max(gradCos, Math.abs(Jtr[j]) / (Math.sqrt(JtJ[j][j]) * rNorm));
    }
    // Projected gradient test (gtol) over the active set only. A failed
    // certificate has moved the point: restart the iteration so the
    // derivatives and active set are rebuilt there.
    if (gradCos < GTOL) { if (certify()) { converged = true; break; } continue; }
    // Linear model of the residual, for the predicted reduction (ftol test).
    const JtJ0 = JtJ.map(row => row.slice());

    // Marquardt damping, then the DESCENT step on the active set:
    // JtJ_aa . dp_a = -Jt.r_a, dp = 0 for held parameters.
    const m = active.length;
    const A = active.map(a => active.map(b => (a === b ? JtJ[a][a] * (1 + lambda) + 1e-300 : JtJ[a][b])));
    const rhs = active.map(a => -Jtr[a]);
    const dpA = solveLinear(A, rhs, m);
    if (!dpA.every(Number.isFinite)) return fail('the normal equations are singular.', iterations);
    const dp = new Array(n).fill(0);
    active.forEach((a, k) => { dp[a] = dpA[k]; });
    const newParams = params.map((v, i) => clamp(paramMap[i].param, v + dp[i]));
    const step = newParams.map((v, i) => v - params[i]);
    const newChi = chiSq(newParams);

    if (Number.isFinite(newChi) && newChi < chi) {
      const actred = (chi - newChi) / Math.max(chi, 1e-300);
      // predicted reduction of the linearised problem: (2 Jt.r . (-dp) - dp.JtJ.dp) / chi
      let lin = 0, quad = 0;
      for (let a = 0; a < n; a++) {
        lin += Jtr[a] * step[a];
        for (let b = 0; b < n; b++) quad += step[a] * JtJ0[a][b] * step[b];
      }
      const prered = (-2 * lin - quad) / Math.max(chi, 1e-300);
      const relStep = Math.max(0, ...step.map((d, i) => Math.abs(d) / paramScale(i, params)));
      params = newParams;
      chi = newChi;
      acceptedSteps++;
      lambda *= 0.7;
      if (chi === 0 || (prered > 0 && actred <= FTOL && prered <= FTOL && actred / prered <= 2) || relStep <= XTOL) {
        if (certify()) { converged = true; break; }
      }
    } else {
      lambda *= 3;
      if (lambda > 1e8) {
        // Even a tiny steepest-descent step no longer reduces the residual,
        // yet the projected gradient is not small: stalled, not converged.
        return fail('the optimiser stalled (no step reduces the residual) after ' + iterations + ' iterations.', iterations);
      }
    }
  }
  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);

  // ── Converged: commit the working copy to the live peaks ──────────────────
  applyParams(params);
  for (const p of work) {
    const live = getPeak(p.id);
    if (!live) continue;
    Object.assign(live, p);
    // A local fit has no backend covariance; any _backendParams on the peak
    // belong to an earlier server fit (or, in Batch Fit, to the SOURCE
    // spectrum's fit) and must not travel with this result.
    delete live._backendParams;
  }

  // Degrees of freedom count the parameters this engine varies (every free
  // one, since caM became continuous; parameters temporarily blocked at a
  // wall still count).
  const nVaried = params.filter((_, j) => !isDiscrete(j)).length;
  const dof = Math.max(1, be.length - nVaried);
  const chiReduced = chi / dof;                       // weighted reduced chi-square, as lmfit's redchi
  const _raw = rawResiduals(params);
  const rmse = Math.sqrt(_raw.reduce((a, v) => a + v * v, 0) / be.length);   // unweighted RMS, as the server path reports
  // "Not supported by the data": the same removal statistic the server
  // computes, from this engine's own residuals and weights (a component driven
  // to the zero floor is an outcome here too, not something to hide).
  {
    const model = evalAllPeaks(be, work);
// Local Levenberg–Marquardt: it must DESCEND and it must never present a
// non-converged attempt as a result (unit A0, 2026-09-15).
//
// Background: from the initial commit (f20d71b) until this unit, runFitLocal
// solved JᵀJ·dp = +Jᵀr with r = data − model, so every step was an ascent
// step, no step was ever accepted, and after 24 rejections λ passed 1e8 and
// the loop exited with the STARTING parameters, announced as "Fit complete
// (local LM)". Every Batch Fit called that path. The empirical proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md; this file is
// that proof turned into a regression test on the SHIPPED functions.
//
// Everything under test is extracted verbatim from templates/index.html by
// function name (brace-matched) — the same functions the browser runs.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found in templates/index.html`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
  return { be, bgSub, bg, initial: JSON.parse(JSON.stringify(cloned)) };
}

// The objective the local engine minimises since unit W1: the Poisson-weighted
// sum of squares, w = 1/sqrt(max(raw counts, 1)), raw = bgSub + bg.
function residualSS(env, be, bgSub, bg) {
  const m = env.evalAllPeaks(be, env.state.peaks);
  return be.reduce((s, _, i) => { const raw = bgSub[i] + (bg ? bg[i] : 0); return s + (bgSub[i] - m[i]) ** 2 / Math.max(raw, 1); }, 0);
}

test('A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters', () => {
  const tabs = loadProjectTabs();
  for (const target of ['C1s Scan_0', 'C1s Scan_4', 'C1s Scan_8']) {
    const env = makeEnv();
    const { be, bgSub, bg, initial } = batchTarget(env, tabs, 'C1s Scan', target);
    const chi0 = residualSS(env, be, bgSub, bg);
    const out = env.runFitLocal(be, bgSub, bg);
    assert.ok(out && out.success === true, `${target}: runFitLocal must report success, got ${JSON.stringify(out)}`);
    const chi1 = residualSS(env, be, bgSub, bg);
    assert.ok(chi1 < 0.5 * chi0, `${target}: residual must drop substantially (before ${chi0.toExponential(3)}, after ${chi1.toExponential(3)})`);
    const moved = env.state.peaks.some((p, i) => Math.abs(p.center - initial[i].center) > 1e-3 || Math.abs(p.fwhm / initial[i].fwhm - 1) > 1e-3);
    assert.ok(moved, `${target}: at least one free centre/width must move — the shipped code returned the starting model on 18/18 targets`);
    assert.ok(env.state.fitResult && env.state.fitResult.status === 'converged', 'a converged local fit records status: converged');
  }
});

test('A01 replay: the linked U 4f pair also descends', () => {
  const tabs = loadProjectTabs();
  const env = makeEnv();
  const { be, bgSub, bg } = batchTarget(env, tabs, 'U4f Scan', 'U4f Scan_3');
requirements-dev.txt
requirements.txt
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-WbZriqlw' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-sI2ep4sp' (errno=Operation not permitted)
diff --git a/CLAUDE.md b/CLAUDE.md
index 7e8b8bd..c0abebb 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -115,7 +115,7 @@ tab reordering exists.
 | `asym-GL` | GL with asymmetric FWHM broadening on high-BE side |
 | `DS` | Doniach-Šunjić, `dsAlpha` (0–0.5) + `dsGamma` |
 | `DSG_LA` | DS+G — DS asymmetric core convolved with Gaussian. Frontend params `laAlpha`/`laBeta`/`laM`; backend id `ds_g`. |
-| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + integer-kernel Gauss conv. Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |
+| `LACX` | True CasaXPS LA(α,β,m) — asymmetric Lorentzian + Gauss conv with a CONTINUOUS m (data points; σ = m/3, half-width ⌈3.5σ⌉) on both sides since the caM unit (2026-09-25). Frontend params `caAlpha`/`caBeta`/`caM`; backend id `la_casaxps`. |
 
 **What the page draws must be what the server fitted.** Two harnesses pin
 it: `tests/js/lineshape_roundtrip.test.js` builds the request with the
@@ -132,9 +132,16 @@ to the optimiser's bounds (a DS+G m locked at 0 fitted at 0.05 —
 `_make_peak_params._set` now widens a limit to a held value), and the
 server clipping DS+G α to 0.495 where the page did not (`_dsgAlpha`). A
 held parameter is held at its value; what the page draws is what the
-server fitted. Tracked gap, `todo` in both files: LACX with m > 0 (the page draws
-a rounded integer kernel; the server fits m continuously — the `caM` clamp
-unit). DS+G was the other gap until 2026-09-22 (the page's quadrature
+server fitted. No shape carries a tracked gap any more. LACX with m > 0 was
+the last (the page drew m rounded to an integer 2m+1 kernel while the
+server fits it continuously: up to 0.97 % of amplitude and 1.2 % of area on
+the lab's U 4f components) until the `caM` unit, 2026-09-25:
+`laTrueCasaXPS_array` now mirrors `_la_casaxps_true` (continuous σ = m/3,
+half-width max(1, ⌈3.5σ⌉), `np.convolve` 'same' with the server's trim,
+normalisation at the grid point nearest the centre) — ≤ 7e-16 of amplitude
+on all 108 committed LA components, pinned across the α/β/m box on seven
+grids incl. grids shorter than the kernel
+(`docs/superpowers/plans/2026-09-25-cam-continuous.md`). DS+G was the other gap until 2026-09-22 (the page's quadrature
 `laCasaXPS` sized its step to the Lorentzian core, not the Gaussian kernel,
 and was wrong by up to 1e52 × amplitude at β = 2, m = 0.05 and 5–21 % low
 in area on the very box Find Peaks emits for a graphitic C 1s line);
@@ -228,7 +235,7 @@ names `caAlpha` / `caBeta` / `caM` so users do not confuse them with DS+G's
 |-----------|---------|
 | α (`caAlpha`) | High-BE-side exponent on the unit-amplitude Lorentzian; dimensionless, default 1.0, bounds 0.1–5.0 |
 | β (`caBeta`) | Low-BE-side exponent; dimensionless, default 1.0, bounds 0.1–5.0 |
-| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); integer, default 50, bounds 0–499 |
+| m (`caM`) | Gaussian convolution kernel width in DATA POINTS (not eV); continuous (the server fits it continuously so its derivative exists; the page draws and the local engine optimises the same continuous value since 2026-09-25 — it was rounded to an integer kernel on the page and held at its start by the local engine), default 50, bounds 0–499 |
 
 α=β=1, m=0 reduces exactly to a pure Lorentzian. Increasing α
 **suppresses** the high-BE tail; decreasing α extends it (BE-axis
@@ -488,8 +495,9 @@ Damping exhaustion is a FAILURE. Poisson-weighted since unit W1
 (2026-09-18): it minimises Σ(w·r)² with w = 1/√max(raw counts, 1), the
 server's weighting, so its statistic is a real χ²ᵣ (objective
 `poisson_weighted_chi_square`); results saved by unit A0 were unweighted
-and stay labelled "Residual variance". It produces no uncertainties, and
-the integer-clamped `caM` is not optimised (carried at its start value).
+and stay labelled "Residual variance". It produces no uncertainties. Since
+the `caM` unit (2026-09-25) it optimises LA's m continuously, as the server
+does (it was rounded by the clamp and carried at its start).
 
 **A local result is a STARTING POINT, not a reportable result** (keyed on
 `engine: 'local'`, helpers `_isLocalFit` / `_isLocalModel` /
@@ -500,22 +508,21 @@ GL-type models (≤ 4 meV, ≤ 1.4 % area on the lab's C1s scans) and on Voigt
 components (fixed η = 0.5 on both sides since A03: on the 5 of 9 committed
 U 4f targets where both engines reach the same minimum every component
 agrees within 4.3 meV, 2.6 % FWHM, 2.0 % area, 0.12 pp — W1 had measured up
-to 20.8 % area on the Voigt satellites); it still differs on the other 4
-U 4f targets (satellite areas up to 8.9 %, 0.77 pp) for two reasons,
-separated by a control arm (the server with every LA m held at its start):
-on one target the `caM` clamp (`caM` held at its start locally while the
-server fits m continuously; holding m on the server closes the gap), on
-three the local descent stopping at a χ²ᵣ 5–13 % above the server's from
-the same start with the same free parameters — a worse minimum, the
-"several minima" case (both engines' amplitude floor is 0 since unit
+to 20.8 % area on the Voigt satellites) and, since the `caM` unit
+(2026-09-25, LA m continuous and optimised locally), on LA components
+wherever the engines reach the same minimum (4 of 9 U 4f targets within
+3.0 meV / 0.49 % / 0.34 % / 0.02 pp). What remains is a different minimum,
+in BOTH directions (`docs/findings/cam/local_server_gap_after_cam.json`):
+the local engine 4.9–13 % above the server on three U 4f targets and
+5.7 % below it on one (both engines' amplitude floor is 0 since unit
 step (b)). Both engines weight by
 √intensity whether the data are counts or CPS (a convention, not a
 calibrated uncertainty for rates); the formula is the same but the inputs
 are not bit-identical, because `uploadToBackend` rounds intensities to
-2 dp before the server weights them. A03 is done and the designation
-STAYS on both grounds; the `caM` clamp is the next unit, the worse-minimum
-outcome is recorded for the local-engine work after it, and the label is
-reconsidered only on a re-measurement after both. (The amplitude-bound change
+2 dp before the server weights them. A03 and the `caM` unit are done and
+the designation STAYS: the worse-minimum outcome (three of nine U 4f
+targets) is the remaining ground, and the label is reconsidered only on a
+re-measurement after that work. (The amplitude-bound change
 DECIDED 2026-09-18 — `docs/findings/2026-09-fit-determinacy.md` §3 — is
 implemented: unit step (b), 2026-09-22, below.) The same file records that a
 converged server fit is not ground truth: on a committed C 1s scan the
diff --git a/scripts/lacx_page_vs_server.js b/scripts/lacx_page_vs_server.js
new file mode 100644
index 0000000..603b030
--- /dev/null
+++ b/scripts/lacx_page_vs_server.js
@@ -0,0 +1,40 @@
+#!/usr/bin/env node
+// caM unit (2026-09-25): the page's LA (LACX) curve vs the server's, for every
+// LA component in the committed projects, at its SAVED parameters on its tab's
+// ROI grid (the page's getROIData semantics: corrected BE inside the ROI).
+// Reports the max |page − server| as a fraction of amplitude and the area
+// difference, per component. Run before and after the unit: before = the
+// defect; after = what a student sees change when a saved project is opened.
+// Usage: node scripts/lacx_page_vs_server.js [out.json]
+const fs = require('fs'); const path = require('path'); const { execFileSync } = require('child_process');
+const ROOT = path.join(__dirname, '..');
+const html = fs.readFileSync(path.join(ROOT, 'templates/index.html'), 'utf8');
+const m = html.match(/function gaussian\(x, center, fwhm\) \{[\s\S]*?\nfunction evalPeakArray\(beArr, p\) \{[\s\S]*?\n\}/);
+const { evalPeakArray } = eval('(function(){\n' + m[0] + '\nreturn { evalPeak, evalPeakArray };})()');
+const PY = [path.join(ROOT, 'venv/bin/python3'), '/Users/skyefortier/xps-app/venv/bin/python3'].find(p => fs.existsSync(p));
+const DATA = path.join(ROOT, 'docs/autofit/test_data');
+const rows = [];
+const specs = [];
+for (const zp of fs.readdirSync(DATA).filter(f => f.endsWith('.proj.zip')).sort()) {
+  const tabs = JSON.parse(execFileSync(PY, ['-c', 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))', ROOT, path.join(DATA, zp)], { encoding: 'utf8', maxBuffer: 1 << 26 }));
+  for (const t of tabs) {
+    const ui = t.ui || {}; const lo = parseFloat(ui.roiMin), hi = parseFloat(ui.roiMax);
+    const be = t.rawBE.map(b => b - (t.ccShift || 0)).filter(c => (!(lo <= Infinity) || c >= lo) && (!(hi <= Infinity) || c <= hi));
+    for (const p of t.peaks || []) {
+      if (p.shape !== 'LACX') continue;
+      rows.push({ project: zp, tab: t.name, peak: p.name, caM: p.caM, fixCaM: !!p.fixCaM, be, p });
+      specs.push({ shape: 'la_casaxps', params: { amplitude: p.amplitude, center: p.center, fwhm: p.fwhm, alpha: p.caAlpha, beta: p.caBeta, m: p.caM }, x: be });
+    }
+  }
+}
+const srv = JSON.parse(execFileSync(PY, [path.join(ROOT, 'tests/js/lineshape_parity_backend.py')], { input: JSON.stringify(specs), encoding: 'utf8', maxBuffer: 1 << 28 }));
+const out = rows.map((r, i) => {
+  const pg = evalPeakArray(r.be, r.p); let mx = 0, aP = 0, aS = 0;
+  for (let j = 0; j < r.be.length; j++) { mx = Math.max(mx, Math.abs(pg[j] - srv[i][j])); aP += pg[j]; aS += srv[i][j]; }
+  return { project: r.project, tab: r.tab, peak: r.peak, caM: r.caM, fixCaM: r.fixCaM, maxDiffRel: mx / Math.abs(r.p.amplitude || 1), dAreaPct: aS ? 100 * (aP / aS - 1) : null };
+});
+const q = v => { v = [...v].sort((a, b) => a - b); const n = v.length; return { n, median: n % 2 ? v[(n - 1) / 2] : 0.5 * (v[n / 2 - 1] + v[n / 2]), max: v[n - 1] }; };
+const summary = { components: out.length, integer_caM: out.filter(r => Number.isInteger(r.caM)).length, locked: out.filter(r => r.fixCaM).length,
+  maxDiffRel: q(out.map(r => r.maxDiffRel)), absDAreaPct: q(out.map(r => Math.abs(r.dAreaPct))) };
+console.log(JSON.stringify(summary));
+if (process.argv[2]) fs.writeFileSync(process.argv[2], JSON.stringify({ summary, rows: out }, null, 1));
diff --git a/tests/js/lineshape_parity.test.js b/tests/js/lineshape_parity.test.js
index 9e7b849..98e23b5 100644
--- a/tests/js/lineshape_parity.test.js
+++ b/tests/js/lineshape_parity.test.js
@@ -168,7 +168,7 @@ for (const shape of ['Gaussian', 'Lorentzian', 'GL', 'Voigt', 'DS', 'asym-GL'])
 //   the fitted box, every grid step, orientation and off-grid centre tested
 //   below).
 //
-test('(A) frontend vs backend parity: LACX (m>0) — KNOWN GAP, unit 2 (kernel discretization)', { todo: 'unit 2 fast-follow: LACX Gaussian-conv kernel mismatch vs backend, grows with m (~0.15% at m=50, measured 2026-08-30)' }, () => {
+test('(A) frontend vs backend parity: LACX (m>0) (FIXED 2026-09-25, caM unit: continuous-m kernel mirrored)', () => {
   const p = basePeak('LACX');
   const x = grid(p.center);
   const jsY = evalPeakArray(x, p);
@@ -347,10 +347,10 @@ const SWEEP = {
   // the full β/m box the optimiser can reach, incl. the corner that made the
   // old quadrature 1e52 × amplitude (β 2, m 0.05) and the delta threshold
   'DSG_LA (m > 0)': { laAlpha: [0, 0.25, 0.49], laBeta: [0.05, 0.7, 2], laM: [0.001, 0.05, 0.4, 2, 4] },
+  // continuous m (caM unit, 2026-09-25): fractional values, the 1e-3 threshold, and the 499 ceiling
+  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [0.001, 0.5, 1, 5, 8.66, 50, 123.4, 499], fwhm: FWHM_RANGE },
 };
-const SWEEP_KNOWN_GAP = {
-  'LACX (m > 0)':   { caAlpha: [0.1, 1, 5], caBeta: [0.1, 1, 5], caM: [1, 5, 50, 499], fwhm: FWHM_RANGE },
-};
+const SWEEP_KNOWN_GAP = {};
 function sweepShape(label) { return label.split(' ')[0]; }
 // The backend parameters of the sweep come from the PAGE's request builder,
 // not from a mapping of this file's own (Codex round 1: a mapping written
@@ -480,3 +480,27 @@ for (const laM of [0.001, 0.002, 0.02, 0.05]) {
     else assert.ok(serverMax > 0.9, `m = ${laM}: a real curve`);
   });
 }
+
+// ── (D‴) LA convergence beyond the base grid (caM unit, 2026-09-25) ──────────
+// The kernel is built in DATA POINTS, so the grid decides it: steps, a
+// descending grid, an off-grid centre, and grids SHORTER than the kernel
+// (np.convolve 'same' then the server's trim — the branch the old integer
+// kernel never exercised).
+const LA_BOX = { caAlpha: [0.1, 1.4, 5], caBeta: [0.1, 0.8, 5], caM: [0.001, 2.5, 8.66, 50, 499] };
+const LA_GRIDS = [
+  { label: 'step 0.1 eV, 120 pts', step: 0.1, n: 120 },
+  { label: 'step 0.02 eV, 500 pts', step: 0.02, n: 500 },
+  { label: 'step 0.05 eV, descending', step: 0.05, n: 200, descending: true },
+  { label: 'step 0.05 eV, centre 0.013 eV off-grid', step: 0.05, n: 200, offset: 0.013 },
+  { label: '9 points (kernel longer than the grid for m ≥ 3)', step: 0.1, n: 9 },
+  { label: '2 points', step: 0.1, n: 2 },
+];
+for (const g of LA_GRIDS) {
+  test(`(D‴) LA continuous-m convolution matches the server on another grid: ${g.label}`, () => {
+    const cases = combos(LA_BOX).map(c => ({ c, p: { ...basePeak('LACX'), ...c } }));
+    const specs = cases.map(k => { const b = backendParamsFromRequest(k.p); return { ...b, x: gridOf(k.p.center, g.step, g.n, g) }; });
+    const beYs = backendEvalMany(specs);
+    const worst = cases.map((k, i) => ({ c: k.c, rel: maxRelDiff(evalPeakArray(specs[i].x, k.p), beYs[i], k.p.amplitude) })).sort((a, b) => b.rel - a.rel);
+    assert.ok(worst[0].rel < TIGHT_TOL, `${g.label}: ${worst.filter(r => r.rel >= TIGHT_TOL).length} of ${worst.length} diverge; worst ${(worst[0].rel * 100).toExponential(3)} % of amplitude at ${JSON.stringify(worst[0].c)}`);
+  });
+}
diff --git a/tests/js/lineshape_roundtrip.test.js b/tests/js/lineshape_roundtrip.test.js
index 4103c52..4204428 100644
--- a/tests/js/lineshape_roundtrip.test.js
+++ b/tests/js/lineshape_roundtrip.test.js
@@ -15,10 +15,10 @@
 // page then DRAWS (evalPeakArray on the fitted grid) to be the curve the
 // server FITTED (individual_peaks[].y).
 //
-// One shape carries a known drawn-vs-fitted gap and is marked todo with the
-// unit that owns it: LACX (the page sends m free and draws it ROUNDED — the
-// caM clamp unit). DSG_LA was the other until 2026-09-22 (the page's
-// quadrature; now dsgConvolved_array mirrors the server).
+// No shape carries a known drawn-vs-fitted gap any more. DSG_LA did until
+// 2026-09-22 (the page's quadrature; now dsgConvolved_array mirrors the
+// server) and LACX until 2026-09-25 (the page drew m rounded to an integer
+// kernel; now laTrueCasaXPS_array mirrors the server's continuous-m one).
 const { test } = require('node:test');
 const assert = require('node:assert');
 const { execFileSync } = require('node:child_process');
@@ -41,7 +41,7 @@ function extractFn(name) {
   assert.fail(`unbalanced braces extracting ${name}`);
 }
 const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
-  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
+  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
   'evalPeakArray', 'getPeak', 'peakToBackendSpec', '_applyBackendParams'];
 const state = { peaks: [] };
 const env = new Function('state', NAMES.map(extractFn).join('\n\n') + '\nreturn { evalPeakArray, peakToBackendSpec, _applyBackendParams };')(state);
@@ -91,9 +91,7 @@ const CASES = {
   'LACX':       { truth: { shape: 'LACX', caAlpha: 1.6, caBeta: 0.7, caM: 20 }, start: { caAlpha: 1.0, caBeta: 1.0, caM: 30 } },
 };
 const TIGHT_TOL = 1e-6;      // of amplitude; both curves are the same closed form on the same grid
-const KNOWN_GAP = {
-  'LACX':   'LACX: the page sends m FREE and draws it rounded to an integer kernel (laTrueCasaXPS_array) — the caM clamp unit',
-};
+const KNOWN_GAP = {};   // LACX was the last (the page drew m rounded to an integer kernel) — closed by the caM unit, 2026-09-25
 
 function roundTrip(shape, { truth, start, extraPeaks = [] }) {
   const truthPeaks = [fullPeak(truth), ...extraPeaks.map(e => fullPeak(e.truth))];
@@ -193,7 +191,8 @@ const LOCKED_AT_BOUNDS = [
   // comparison sits under the caM evaluator gap marked todo above (curve: false)
   { label: 'DS+G m 0.05 locked', truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 0.05, fixLaM: true }, held: { m_gauss: 0.05 } },
   { label: 'DS+G m 4 locked',    truth: { shape: 'DSG_LA', laAlpha: 0.15, laBeta: 0.5, laM: 4, fixLaM: true }, held: { m_gauss: 4 } },
-  { label: 'LA m 499 locked (request and hold only)',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 }, curve: false },
+  { label: 'LA m 499 locked',    truth: { shape: 'LACX', caAlpha: 1, caBeta: 1, caM: 499, fixCaM: true }, held: { m: 499 } },
+  { label: 'LA m 8.66 locked (a fractional m, as a fit returns it)', truth: { shape: 'LACX', caAlpha: 1.3, caBeta: 0.9, caM: 8.66, fixCaM: true }, held: { m: 8.66 } },
 ];
 for (const c of LOCKED_AT_BOUNDS) {
   test(`locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — ${c.label}`, () => {

codex
The Jacobian now keeps its differences inside the current kernel piece. Certification and proposed LM steps can still cross a jump, so I’m testing those paths separately. I’m also checking whether a flat m column causes a legitimate boundary fit to fail.

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 node --test tests/js/local_lm_descent.test.js tests/js/lineshape_parity.test.js tests/js/lineshape_roundtrip.test.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
exec
/bin/zsh -lc 'node scripts/cam_transition_sweep.js' in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 3529ms:
{"cases":210,"free_failed":0,"held_failed":0,"free_ended_worse_than_held":0,"first_fails":[]}

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/cam_transition_sweep.js'\\'','\\''utf8'\\'').split('\\''let freeFail'\\'')[0];
new Function('\\''require'\\'','\\''__dirname'\\'',src+\"\\nlet count=0, bad=[];\\nfor (const m of [0,0.000999,0.001,0.001001,0.01,0.1,0.5,6/7,12/7,18/7,48,498,499]) for (const all of [false,true]) for(const amp of [4900,5000]) {\\nconst be=grid(280,286,0.03),truth={id:1,name:'\\''la'\\'',shape:'\\''LACX'\\'',center:283.013,fwhm:.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:m,glMix:50,asymmetry:0};\\nconst run=fixCaM=>{const e=env();const d=e.evalAllPeaks(be,[truth]).map((v,i)=>v+5*Math.sin(1.77*i));e.state.peaks=[{...truth,amplitude:amp,fixCenter:"'!all,fixFwhm:!all,fixCaAlpha:!all,fixCaBeta:!all,fixCaM}];let o=e.runFitLocal(be,d,be.map(()=>0));return {o,chi:e.state.fitResult?.chi,m:e.state.peaks[0].caM};};'"\\nconst fr=run(false),hd=run(true);count++;if("'!fr.o.success&&hd.o.success || fr.chi>hd.chi*1.000001)bad.push({m,all,amp,fr,hd});'"\\n}console.log(JSON.stringify({count,bad}));\\n\")(require,process.cwd()+'\\''/scripts'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 1004ms:
{"count":52,"bad":[{"m":0.5,"all":false,"amp":5000,"fr":{"o":{"success":true,"engine":"local","iterations":18,"acceptedSteps":1,"chiReduced":0.19711020062032922,"certifyRestarts":0},"chi":39.224929923445515,"m":0.1734714223390038},"hd":{"o":{"success":true,"engine":"local","iterations":2,"acceptedSteps":2,"chiReduced":0.1960854206186589,"certifyRestarts":0},"chi":39.21708412373178,"m":0.5}}]}

exec
/bin/zsh -lc "sed -n '1,90p' tests/js/local_lm_descent.test.js; rg -n 'function evalAllPeaks|_la_casaxps_true|caM|round\\(' fitting.py | head -40; git log -3 --oneline" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
// Local Levenberg–Marquardt: it must DESCEND and it must never present a
// non-converged attempt as a result (unit A0, 2026-09-15).
//
// Background: from the initial commit (f20d71b) until this unit, runFitLocal
// solved JᵀJ·dp = +Jᵀr with r = data − model, so every step was an ascent
// step, no step was ever accepted, and after 24 rejections λ passed 1e8 and
// the loop exited with the STARTING parameters, announced as "Fit complete
// (local LM)". Every Batch Fit called that path. The empirical proof is in
// docs/superpowers/plans/2026-09-15-a01-local-lm-proof.md; this file is
// that proof turned into a regression test on the SHIPPED functions.
//
// Everything under test is extracted verbatim from templates/index.html by
// function name (brace-matched) — the same functions the browser runs.

const { test } = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');

const REPO_ROOT = path.join(__dirname, '../..');
const html = fs.readFileSync(path.join(REPO_ROOT, 'templates/index.html'), 'utf8');
const lines = html.split('\n');

function extractFn(name) {
  const re = new RegExp('^(async )?function ' + name.replace(/\$/g, '\\$') + '\\(');
  const start = lines.findIndex(l => re.test(l));
  assert.ok(start >= 0, `function ${name} not found in templates/index.html`);
  let depth = 0, seen = false;
  for (let i = start; i < lines.length; i++) {
    for (const ch of lines[i]) { if (ch === '{') { depth++; seen = true; } else if (ch === '}') depth--; }
    if (seen && depth === 0) return lines.slice(start, i + 1).join('\n');
  }
  assert.fail(`unbalanced braces extracting ${name}`);
}

const NAMES = ['_arrMin', '_arrMax', 'gaussian', 'lorentzian', 'pseudoVoigt', 'asymmGL', 'doniachSunjic',
  'laCasaXPSCore', 'laCasaXPS', 'laTrueCasaXPS', '_laKernelHalf', 'laTrueCasaXPS_array', 'evalPeak', '_dsgAlpha', 'dsgDeltaKernel_array', '_fftRadix2', '_circularConvolve', 'dsgConvolved_array',
  'evalPeakArray', 'evalAllPeaks', 'shirleyBackground', 'smartBackground', 'linearBackground',
  'tougaardBackground', '_applyEndpointAveraging', '_bgWindowIndices', 'computeBackgroundCore',
  'smartExperimentalBackground', 'shirleyLinearBackground', 'getPeak', 'runFitLocal', 'solveLinear',
  '_computeRFactor', '_fitStatLabel', '_isUnweightedLocal', '_isLocalProvenance', '_localFitDetail', '_isLocalFit', '_isLocalModel', '_governingProvenance', '_localFitCaveat', '_fitStatusText', '_applyStatCaption', '_applyStatDisplay', '_updateLocalModelBanner',
  '_componentSupportCore', '_supportRootOf', '_applySupportVerdicts'];
const CAVEAT_CONST = (html.match(/^const _LOCAL_FIT_CAVEAT\w* = .*$/mg) || []).join('\n');

// One isolated environment per test: a fresh `state`, a stub DOM, and the
// extracted functions bound to them.
function makeEnv() {
  const dom = {};
  const el = id => (dom[id] ||= { value: '', textContent: '', innerHTML: '', style: {}, setAttribute() {}, removeAttribute() {},
    classList: { add() {}, remove() {}, contains: () => false } });
  const document = { getElementById: el, querySelectorAll: () => [] };
  const state = { peaks: [], fitResult: null, rawBE: [], rawIntensity: [], ccShift: 0 };
  const calls = { notify: [] };
  const notify = (msg, kind) => calls.notify.push({ msg, kind });
  const noop = () => {};
  const src = CAVEAT_CONST + '\nconst _SUPPORT_MIN_F = 10; const _startsLiveKey = () => "KEY";\n' + NAMES.map(extractFn).join('\n\n');
  const factory = new Function('document', 'state', 'notify', '_CHISQ_TOOLTIP', '_LOCALFIT_TOOLTIP', '_activeTab', '_escHtml', '_historyPreview', 'tabManager', '_updateRFactorUI', '_updateROIDisplay',
    'renderPeakList', 'updatePlot', 'renderResults', '_hideFitSpinner', '_autoSnapshot', 'manualAnchorBackground',
    src + '\nreturn { runFitLocal, computeBackgroundCore, evalAllPeaks, evalPeakArray, gaussian };');
  const fns = factory(document, state, notify, '', '', () => null, x => String(x), null, null, noop, noop, noop, noop, noop, noop, noop,
    be => new Array(be.length).fill(0));
  return { ...fns, state, dom, calls };
}

// ── Committed lab project, replayed exactly as runPropagation does ──────────
const PROJECT = path.join(REPO_ROOT, 'docs/autofit/test_data/1-GTA UCl4-graphite one set of U doublets.proj.zip');
const BatchPropagation = require(path.join(REPO_ROOT, 'static/js/batch_propagation.js'));

function loadProjectTabs() {
  const py = fs.existsSync(path.join(REPO_ROOT, 'venv/bin/python3')) ? path.join(REPO_ROOT, 'venv/bin/python3')
    : (fs.existsSync('/Users/skyefortier/xps-app/venv/bin/python3') ? '/Users/skyefortier/xps-app/venv/bin/python3' : 'python3');
  const script = 'import sys, json; sys.path.insert(0, sys.argv[1]); from autofit.reference import load_project_tabs; ' +
    'print(json.dumps([t for t in load_project_tabs(sys.argv[2]) if not t.get("isStack") and t.get("rawBE")]))';
  return JSON.parse(execFileSync(py, ['-c', script, REPO_ROOT, PROJECT], { encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 }));
}

function batchTarget(env, tabs, sourceName, targetName) {
  const src = tabs.find(t => t.name === sourceName), tgt = tabs.find(t => t.name === targetName);
  assert.ok(src && tgt, 'source/target tabs present in committed project');
  const scale = Math.max(...tgt.rawIntensity) / Math.max(...src.rawIntensity);
  const cloned = JSON.parse(JSON.stringify(src.peaks)).map(p => ({ ...p, amplitude: p.linked ? p.amplitude : p.amplitude * scale }));
  const ui = BatchPropagation.propagateFitUi({ ...src.ui }, { ...tgt.ui });
  const roiMin = parseFloat(ui.roiMin), roiMax = parseFloat(ui.roiMax);
  const be = [], inten = [];
  tgt.rawBE.forEach((b, i) => { const c = b - (src.ccShift || 0); if (c >= roiMin && c <= roiMax) { be.push(c); inten.push(tgt.rawIntensity[i]); } });
  const bg = env.computeBackgroundCore(be, inten, ui);
  const bgSub = inten.map((v, i) => v - bg[i]);
  env.state.peaks = cloned;
  env.state.fitResult = null;
164:    LA shape (see _la_casaxps_true), which uses a piecewise-asymmetric
336:def shirley_background(
400:def smart_background(
416:    shir = shirley_background(x, y, n_iter, tol, n_avg=n_avg)
420:def linear_background(x: np.ndarray, y: np.ndarray) -> np.ndarray:
426:def smart_experimental_background(
482:def shirley_linear_background(
544:def tougaard_background(
670:def _la_casaxps_true(
723:    # int(round(m)), making the function locally constant in m and
786:    "la_casaxps": _la_casaxps_true,
1555:            bg = linear_background(x, y)
1557:        bg_inner = shirley_background(x_bg, y_bg, n_avg=endpoint_avg)
1559:        bg_inner = smart_background(x_bg, y_bg, n_avg=endpoint_avg)
1561:        bg_inner = smart_experimental_background(x_bg, y_bg, n_avg=endpoint_avg)
1563:        bg_inner = shirley_linear_background(x_bg, y_bg, n_avg=endpoint_avg)
1565:        bg_inner = tougaard_background(x_bg, y_bg, n_avg=endpoint_avg)
1950:        bg = shirley_background(x, y, n_avg=endpoint_avg)
1952:        bg = smart_background(x, y, n_avg=endpoint_avg)
1954:        bg = smart_experimental_background(x, y, n_avg=endpoint_avg)
1956:        bg = shirley_linear_background(x, y, n_avg=endpoint_avg)
1958:        bg = tougaard_background(x, y, n_avg=endpoint_avg)
1960:        bg = linear_background(x, y)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BV9VRNgd' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Mps8PLJs' (errno=Operation not permitted)
c875490 fix(caM): Codex round 1 (NO-GO x2) - the local engine's derivative for m stays inside one kernel-width piece
df388ce fix(caM): LA's m is continuous on the page and in the local engine, as the server fits it
3ea3b8b docs(roi): owner decisions at deploy - the edge difference filed under audit item 8 / R6-1; review the quiet hint's 18 % later; deploy-log entry

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/cam_transition_sweep.js'\\'','\\''utf8'\\'').split('\\''let freeFail'\\'')[0];new Function('\\''require'\\'','\\''__dirname'\\'',src+\"\\nlet count=0,bad=[],maxRestarts=0;\\nfor(const st of [.03,.05,.1])for(const k of [2,3,9,17,56])for(const off of [-1e-8,0,1e-8])for(const freq of [.1,.5,1,2.5,3])for(const phase of [0,2]){\\nconst m=6*k/7+off,be=grid(280,280+100*st,st),truth={id:1,name:'\\''la'\\'',shape:'\\''LACX'\\'',center:280+50*st+.013,fwhm:.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:m,glMix:50,asymmetry:0};\\nconst run=fixCaM=>{const e=env();const d=e.evalAllPeaks(be,[truth]).map((v,i)=>v+5*Math.sin(freq*i+phase));e.state.peaks=[{...truth,amplitude:4900,fixCenter:true,fixFwhm:true,fixCaAlpha:true,fixCaBeta:true,fixCaM}];const o=e.runFitLocal(be,d,be.map(()=>0));maxRestarts=Math.max(maxRestarts,o.certifyRestarts||0);return {o,chi:e.state.fitResult?.chi,m:e.state.peaks[0].caM};};\\nconst fr=run(false);count++;if("'!fr.o.success){const hd=run(true);bad.push({st,k,off,freq,phase,fr,hd});if(bad.length<=6)console.log(JSON.stringify(bad.at(-1)));}'"\\n}console.log(JSON.stringify({count,fails:bad.length,maxRestarts}));\\n\")(require,process.cwd()+'\\''/scripts'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
exec
/bin/zsh -lc "node --test --test-name-pattern='local engine optimises a free LA|an LA fit with m free' tests/js/local_lm_descent.test.js" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 149ms:
# Subtest: the local engine optimises a free LA m continuously and counts it as a degree of freedom
ok 1 - the local engine optimises a free LA m continuously and counts it as a degree of freedom
  ---
  duration_ms: 42.144278
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 2 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 28.362907
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 3 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 23.092147
  type: 'test'
  ...
1..3
# tests 3
# suites 0
# pass 3
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 204.430255

 succeeded in 3796ms:
{"count":450,"fails":0,"maxRestarts":1}

 exited 1 in 60354ms:
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
#     from fitting import _SHAPE_FUNCS  \# noqa: E402
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Subtest: (A) frontend vs backend parity: Gaussian
not ok 1 - (A) frontend vs backend parity: Gaussian
  ---
  duration_ms: 1217.169745
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
    startSubtestAfterBootstrap (node:internal/test_runner/harness:296:17)
  ...
# Subtest: (A) frontend vs backend parity: Lorentzian
not ok 2 - (A) frontend vs backend parity: Lorentzian
  ---
  duration_ms: 1204.437556
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: GL
not ok 3 - (A) frontend vs backend parity: GL
  ---
  duration_ms: 1222.257763
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: Voigt
not ok 4 - (A) frontend vs backend parity: Voigt
  ---
  duration_ms: 1124.894036
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DS
not ok 5 - (A) frontend vs backend parity: DS
  ---
  duration_ms: 1126.240651
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: asym-GL
not ok 6 - (A) frontend vs backend parity: asym-GL
  ---
  duration_ms: 1166.2515
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:134:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:139:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX (m>0) (FIXED 2026-09-25, caM unit: continuous-m kernel mirrored)
not ok 7 - (A) frontend vs backend parity: LACX (m>0) (FIXED 2026-09-25, caM unit: continuous-m kernel mirrored)
  ---
  duration_ms: 1176.627645
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:171:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:176:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: LACX at m=0 (no convolution)
not ok 8 - (A) frontend vs backend parity: LACX at m=0 (no convolution)
  ---
  duration_ms: 1088.042984
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:182:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:188:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
not ok 9 - (A) frontend vs backend parity: DSG_LA at moderate m (FIXED 2026-09-22: grid-aware convolution, dsgConvolved_array)
  ---
  duration_ms: 1132.780443
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:194:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:199:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
not ok 10 - (A) frontend vs backend parity: DSG_LA at m=0, center on-grid (delta kernel)
  ---
  duration_ms: 1111.497621
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
not ok 11 - (A) frontend vs backend parity: DSG_LA at m=0, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1130.948153
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
not ok 12 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center on-grid (delta kernel)
  ---
  duration_ms: 1110.610429
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
not ok 13 - (A) frontend vs backend parity: DSG_LA at m=0.0009, center half-step off-grid (delta kernel)
  ---
  duration_ms: 1113.873237
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:218:5'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:225:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
not ok 14 - (A) frontend vs backend parity: DSG_LA at m=0, descending grid, off-grid center
  ---
  duration_ms: 1108.548079
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:235:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:242:15)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
ok 15 - (B) evalPeak vs evalPeakArray agree pointwise: Gaussian
  ---
  duration_ms: 0.398232
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
ok 16 - (B) evalPeak vs evalPeakArray agree pointwise: Lorentzian
  ---
  duration_ms: 0.173611
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: Voigt
ok 17 - (B) evalPeak vs evalPeakArray agree pointwise: Voigt
  ---
  duration_ms: 0.177035
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: GL
ok 18 - (B) evalPeak vs evalPeakArray agree pointwise: GL
  ---
  duration_ms: 0.178252
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
ok 19 - (B) evalPeak vs evalPeakArray agree pointwise: asym-GL
  ---
  duration_ms: 0.23917
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DS
ok 20 - (B) evalPeak vs evalPeakArray agree pointwise: DS
  ---
  duration_ms: 0.290645
  type: 'test'
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA
not ok 21 - (B) evalPeak vs evalPeakArray agree pointwise: DSG_LA # TODO evalPeak() DSG_LA branch is the normalised DS core with m IGNORED (the convolution is a grid operation, dsgConvolved_array via evalPeakArray); no shipped caller reaches it — guard (C)
  ---
  duration_ms: 4.145922
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'DSG_LA at x=393.3: evalPeak=7298.4050340345175, evalPeakArray[i]=8703.575517573383, rel diff=7.8969%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:272:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (B) evalPeak vs evalPeakArray agree pointwise: LACX
not ok 22 - (B) evalPeak vs evalPeakArray agree pointwise: LACX # TODO evalPeak() LACX branch ignores m; only its call sites are rerouted in unit-1 commit 2, not evalPeak() itself — see file header
  ---
  duration_ms: 1.333723
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:265:3'
  failureType: 'testCodeFailure'
  error: 'LACX at x=393.3: evalPeak=2863.2353955224326, evalPeakArray[i]=7181.067813111589, rel diff=24.2657%'
  code: 'ERR_ASSERTION'
  name: 'AssertionError'
  expected: true
  actual: false
  operator: '=='
  stack: |-
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:272:12)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
    async Test.processPendingSubtests (node:internal/test_runner/test:744:7)
  ...
# Subtest: (C) evalPeak() has no direct callers outside evalPeakArray()
ok 23 - (C) evalPeak() has no direct callers outside evalPeakArray()
  ---
  duration_ms: 3.537512
  type: 'test'
  ...
# Subtest: (D) sweep across the fitted range: Gaussian
not ok 24 - (D) sweep across the fitted range: Gaussian
  ---
  duration_ms: 1142.770319
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Lorentzian
not ok 25 - (D) sweep across the fitted range: Lorentzian
  ---
  duration_ms: 1263.794764
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: Voigt
not ok 26 - (D) sweep across the fitted range: Voigt
  ---
  duration_ms: 1146.758711
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: GL
not ok 27 - (D) sweep across the fitted range: GL
  ---
  duration_ms: 1118.931389
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: asym-GL
not ok 28 - (D) sweep across the fitted range: asym-GL
  ---
  duration_ms: 1103.746233
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DS
not ok 29 - (D) sweep across the fitted range: DS
  ---
  duration_ms: 1156.123212
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (delta kernel)
not ok 30 - (D) sweep across the fitted range: DSG_LA (delta kernel)
  ---
  duration_ms: 1131.328559
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m = 0)
not ok 31 - (D) sweep across the fitted range: LACX (m = 0)
  ---
  duration_ms: 1134.174437
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: (D) sweep across the fitted range: DSG_LA (m > 0)
not ok 32 - (D) sweep across the fitted range: DSG_LA (m > 0)
  ---
  duration_ms: 1244.153599
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D) sweep across the fitted range: LACX (m > 0)
not ok 33 - (D) sweep across the fitted range: LACX (m > 0)
  ---
  duration_ms: 1152.208929
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:381:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    runSweep (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:373:16)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:382:19)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
not ok 34 - (D′) DS+G convolution converges on another grid: step 0.1 eV, 120 pts
  ---
  duration_ms: 1111.337374
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
not ok 35 - (D′) DS+G convolution converges on another grid: step 0.02 eV, 500 pts
  ---
  duration_ms: 1113.963749
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
not ok 36 - (D′) DS+G convolution converges on another grid: step 0.05 eV, descending
  ---
  duration_ms: 1108.780618
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
not ok 37 - (D′) DS+G convolution converges on another grid: step 0.05 eV, centre half a step off-grid
  ---
  duration_ms: 1106.57977
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
not ok 38 - (D′) DS+G convolution converges on another grid: step 0.1 eV, descending, centre 0.03 eV off-grid
  ---
  duration_ms: 1178.576046
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
not ok 39 - (D′) DS+G convolution converges on another grid: short window: 30 pts at 0.1 eV (narrower than the pad)
  ---
  duration_ms: 1100.564736
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
not ok 40 - (D′) DS+G convolution converges on another grid: irregular-ish step 0.0503 eV (median step), 181 pts
  ---
  duration_ms: 1107.021222
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:419:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:422:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
not ok 41 - (D″) DS+G regression: centre 10 eV outside a [−5, 5] window (a free DS+G centre has no window on the server)
  ---
  duration_ms: 1137.743213
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 6-point irregular grid
not ok 42 - (D″) DS+G regression: a 6-point irregular grid
  ---
  duration_ms: 1284.442692
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
not ok 43 - (D″) DS+G regression: genuinely irregular steps (0.05 / 0.06 alternating; median ≠ mean)
  ---
  duration_ms: 1268.514467
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
not ok 44 - (D″) DS+G regression: a 0.001 eV grid over 10 eV at the box corner β 2, m 4, α 0.49 (13 s per curve in the first cut)
  ---
  duration_ms: 1290.354891
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
not ok 45 - (D″) DS+G regression: centre 10 eV outside [−5, 5] on a 0.5 eV grid, β 0.05, m 0.05 (Codex round 2 reproducer: was 5e16 × amplitude)
  ---
  duration_ms: 1276.894824
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
not ok 46 - (D″) DS+G regression: centre −10 eV on the low-BE side, 201 points at 0.05 eV, m 0.001
  ---
  duration_ms: 1264.070137
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
not ok 47 - (D″) DS+G regression: centre just outside the padded grid (6.5 eV, pad 1 eV)
  ---
  duration_ms: 1240.905044
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
not ok 48 - (D″) DS+G regression: centre just inside the padded grid (5.999 eV, pad 1 eV)
  ---
  duration_ms: 1192.627439
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 2-point grid
not ok 49 - (D″) DS+G regression: a 2-point grid
  ---
  duration_ms: 1203.768504
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G regression: a 1-point grid
not ok 50 - (D″) DS+G regression: a 1-point grid
  ---
  duration_ms: 1239.067557
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:449:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:452:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
not ok 51 - (D″) DS+G at m = 0.001 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1189.930572
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
not ok 52 - (D″) DS+G at m = 0.002 on a 0.1 eV grid: page equals server (both an all-zero curve — the server kernel underflows; known server limit)
  ---
  duration_ms: 1180.452382
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
not ok 53 - (D″) DS+G at m = 0.02 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1193.015779
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
not ok 54 - (D″) DS+G at m = 0.05 on a 0.1 eV grid: page equals server
  ---
  duration_ms: 1217.550356
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:471:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEval (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:80:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:475:17)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: step 0.1 eV, 120 pts
not ok 55 - (D‴) LA continuous-m convolution matches the server on another grid: step 0.1 eV, 120 pts
  ---
  duration_ms: 1207.77134
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: step 0.02 eV, 500 pts
not ok 56 - (D‴) LA continuous-m convolution matches the server on another grid: step 0.02 eV, 500 pts
  ---
  duration_ms: 1315.872164
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: step 0.05 eV, descending
not ok 57 - (D‴) LA continuous-m convolution matches the server on another grid: step 0.05 eV, descending
  ---
  duration_ms: 1257.09232
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: step 0.05 eV, centre 0.013 eV off-grid
not ok 58 - (D‴) LA continuous-m convolution matches the server on another grid: step 0.05 eV, centre 0.013 eV off-grid
  ---
  duration_ms: 1284.232415
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: 'spawnSync /Users/skyefortier/xps-app/venv/bin/python3 EPIPE'
  code: 'EPIPE'
  stack: |-
    Object.spawnSync (node:internal/child_process:1120:20)
    spawnSync (node:child_process:902:24)
    execFileSync (node:child_process:945:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: 9 points (kernel longer than the grid for m ≥ 3)
not ok 59 - (D‴) LA continuous-m convolution matches the server on another grid: 9 points (kernel longer than the grid for m ≥ 3)
  ---
  duration_ms: 1280.518581
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: (D‴) LA continuous-m convolution matches the server on another grid: 2 points
not ok 60 - (D‴) LA continuous-m convolution matches the server on another grid: 2 points
  ---
  duration_ms: 1236.544285
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:499:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity_backend.py", line 20, in <module>
        from fitting import _SHAPE_FUNCS  # noqa: E402
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    backendEvalMany (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:329:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_parity.test.js:502:18)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
not ok 61 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Gaussian
  ---
  duration_ms: 1209.825286
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.start (node:internal/test_runner/test:944:17)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
not ok 62 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Lorentzian
  ---
  duration_ms: 1211.946839
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
not ok 63 - page → server → page: what the page draws after applying the result IS the curve the server fitted — Voigt
  ---
  duration_ms: 1215.15811
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
not ok 64 - page → server → page: what the page draws after applying the result IS the curve the server fitted — GL
  ---
  duration_ms: 1123.274689
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
not ok 65 - page → server → page: what the page draws after applying the result IS the curve the server fitted — asym-GL
  ---
  duration_ms: 1129.908877
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
not ok 66 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DS
  ---
  duration_ms: 1163.872263
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
not ok 67 - page → server → page: what the page draws after applying the result IS the curve the server fitted — DSG_LA
  ---
  duration_ms: 1175.430252
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
not ok 68 - page → server → page: what the page draws after applying the result IS the curve the server fitted — LACX
  ---
  duration_ms: 1095.359688
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:120:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:121:28)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
not ok 69 - Voigt is the fixed 50/50 mix on both sides (A03): request, server parameter, page write-back, drawn curve
  ---
  duration_ms: 1129.074494
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:129:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:136:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
not ok 70 - a linked Voigt follows its parent and both are drawn as fitted (η follows the parent: fixed 0.5)
  ---
  duration_ms: 1108.929235
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:144:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:146:26)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
not ok 71 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 0 locked
  ---
  duration_ms: 1133.712978
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
not ok 72 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — GL mix 100 locked
  ---
  duration_ms: 1114.682102
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
not ok 73 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 0 locked
  ---
  duration_ms: 1110.894666
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
not ok 74 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL mix 100 locked
  ---
  duration_ms: 1107.302383
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
not ok 75 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 0 locked
  ---
  duration_ms: 1153.703295
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
not ok 76 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — asym-GL asymmetry 1 locked
  ---
  duration_ms: 1263.449638
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
not ok 77 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0 locked
  ---
  duration_ms: 1150.785781
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
not ok 78 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS alpha 0.5 locked
  ---
  duration_ms: 1116.282159
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
not ok 79 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 0 locked
  ---
  duration_ms: 1105.223242
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
not ok 80 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS gamma 5 locked
  ---
  duration_ms: 1156.710979
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
not ok 81 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0 locked (delta kernel)
  ---
  duration_ms: 1128.121056
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
not ok 82 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.49 locked (delta kernel)
  ---
  duration_ms: 1137.804648
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
not ok 83 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 0.05 locked (delta kernel)
  ---
  duration_ms: 1240.417094
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
not ok 84 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G beta 2 locked (delta kernel)
  ---
  duration_ms: 1141.053417
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
not ok 85 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 0.1 locked (m = 0)
  ---
  duration_ms: 1116.853004
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
not ok 86 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA alpha 5 locked (m = 0)
  ---
  duration_ms: 1115.002567
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
not ok 87 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 0.1 locked (m = 0)
  ---
  duration_ms: 1114.550773
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
not ok 88 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA beta 5 locked (m = 0)
  ---
  duration_ms: 1105.425159
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
not ok 89 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G alpha 0.5 locked (delta kernel; both evaluators clip to 0.495)
  ---
  duration_ms: 1184.37001
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
not ok 90 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 0.05 locked
  ---
  duration_ms: 1097.979658
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
not ok 91 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — DS+G m 4 locked
  ---
  duration_ms: 1100.069167
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked
not ok 92 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 499 locked
  ---
  duration_ms: 1141.571216
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 8.66 locked (a fractional m, as a fit returns it)
not ok 93 - locked at a bound, the request carries the value the page draws, the server holds it, and the fit is drawn as fitted — LA m 8.66 locked (a fractional m, as a fit returns it)
  ---
  duration_ms: 1295.790869
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:198:3'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:199:35)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: a locked GL mix is sent locked, held by the server and drawn at the locked value
not ok 94 - a locked GL mix is sent locked, held by the server and drawn at the locked value
  ---
  duration_ms: 1265.784585
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:212:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    roundTrip (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:107:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:213:33)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
not ok 95 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1281.798582
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:223:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:231:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
not ok 96 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1280.191457
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:241:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip_backend.py", line 22, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    bridge (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:58:21)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/lineshape_roundtrip.test.js:250:14)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
  ...
# Traceback (most recent call last):
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
#     import fitting  \# noqa: E402
#     ^^^^^^^^^^^^^^
#   File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
#     from lmfit import Model, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
#     from .confidence import conf_interval, conf_interval2d
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
#     from .minimizer import MinimizerException
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
#     from .parameter import Parameter, Parameters
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
#     from .jsonutils import decode4js, encode4js
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
#     import dill
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
#     from .session import (
#   File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
#     TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
#                                ^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
#     return _os.fsdecode(_gettempdir())
#                         ^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
#     tempdir = _get_default_tempdir()
#               ^^^^^^^^^^^^^^^^^^^^^^
#   File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
#     raise FileNotFoundError(_errno.ENOENT,
# FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
# Subtest: A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
ok 97 - A01 replay: Batch Fit on the committed UCl4-graphite C1s scans actually moves the parameters
  ---
  duration_ms: 1334.106664
  type: 'test'
  ...
# Subtest: A01 replay: the linked U 4f pair also descends
ok 98 - A01 replay: the linked U 4f pair also descends
  ---
  duration_ms: 283.050736
  type: 'test'
  ...
# Subtest: noiseless Gaussian: amplitude 10 started at 5 is recovered
ok 99 - noiseless Gaussian: amplitude 10 started at 5 is recovered
  ---
  duration_ms: 13.007315
  type: 'test'
  ...
# Subtest: acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
ok 100 - acceptance rule: a non-converged attempt refuses to overwrite peaks or the previous fit result
  ---
  duration_ms: 9.218127
  type: 'test'
  ...
# Subtest: a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
ok 101 - a local fit result is Poisson-weighted: objective, weighting and the designated statistic text
  ---
  duration_ms: 12.261898
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
ok 102 - bound stationarity: amplitude at its lower wall with the optimum inside the box must move off the wall
  ---
  duration_ms: 9.032986
  type: 'test'
  ...
# Subtest: bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
ok 103 - bound stationarity: amplitude at its lower wall with the optimum OUTSIDE the box is a legitimate converged fit
  ---
  duration_ms: 8.587313
  type: 'test'
  ...
# Subtest: a weak component the data DO hold is no longer forced up to an amplitude of 1
ok 104 - a weak component the data DO hold is no longer forced up to an amplitude of 1
  ---
  duration_ms: 8.661267
  type: 'test'
  ...
# Subtest: derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
ok 105 - derivative accuracy: a free centre on a narrow peak lands on the true centre from either side (fixed wrong width)
  ---
  duration_ms: 42.541677
  type: 'test'
  ...
# Subtest: derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
ok 106 - derivative accuracy: centre-only fit on a 0.005 eV grid with a mis-scaled amplitude reaches the least-squares optimum
  ---
  duration_ms: 24.874475
  type: 'test'
  ...
# Subtest: a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
ok 107 - a genuinely stalled start (no sensitivity: peak far outside the data window) is reported as a failure, not convergence
  ---
  duration_ms: 7.943323
  type: 'test'
  ...
# Subtest: linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
ok 108 - linked child follows its parent even when the parent width is locked (behaviour documented in unit A0)
  ---
  duration_ms: 13.153812
  type: 'test'
  ...
# Subtest: round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
ok 109 - round-2 replay A: a peak that can only shrink at a wall is left at a constrained stationary point
  ---
  duration_ms: 12.36491
  type: 'test'
  ...
# Subtest: round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
ok 110 - round-2 replay B: amplitude pinned at its wall must not stop the width from reaching its constrained optimum
  ---
  duration_ms: 10.600772
  type: 'test'
  ...
# Subtest: round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
ok 111 - round-2: predicted reduction <= 0 never counts as convergence (start at FWHM 0.5 on replay A data)
  ---
  duration_ms: 10.478849
  type: 'test'
  ...
# Subtest: A01 replay targets converge to constrained stationary points (C1s and U 4f)
ok 112 - A01 replay targets converge to constrained stationary points (C1s and U 4f)
  ---
  duration_ms: 1559.575304
  type: 'test'
  ...
# Subtest: round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
ok 113 - round-3 A1: a weak satellite next to a 100x stronger line is determined and must be fitted, not frozen
  ---
  duration_ms: 93.188941
  type: 'test'
  ...
# Subtest: round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
ok 114 - round-3 B1: a 10-count satellite beside a 100000-count line (centres/widths locked) recovers its amplitude
  ---
  duration_ms: 20.007325
  type: 'test'
  ...
# Subtest: round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
ok 115 - round-3 A2: (285.3, 1, 8) fitted to (285, 1.5, 0.1) ends at a constrained stationary point
  ---
  duration_ms: 14.528939
  type: 'test'
  ...
# Subtest: round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
ok 116 - round-3 B2: (286, 0.3 locked, 20) fitted to (285, 1.5, 5) ends at a constrained stationary point
  ---
  duration_ms: 82.408951
  type: 'test'
  ...
# Subtest: round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
ok 117 - round-4: near-zero residual with no data still passes the feasible-descent certificate (centre free, zero data)
  ---
  duration_ms: 1230.566591
  type: 'test'
  ...
# Subtest: round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
ok 118 - round-4: near-zero residual on the accepted-step exit is certified (amplitude free, peak mostly outside the window)
  ---
  duration_ms: 22.728828
  type: 'test'
  ...
# Subtest: round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
ok 119 - round-5: a single Gaussian between two symmetric peaks is certified with the CURRENT width, not a Jacobian-perturbed one
  ---
  duration_ms: 10.016413
  type: 'test'
  ...
# Subtest: weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
ok 120 - weighted least squares: a locked-shape amplitude lands on the closed-form WEIGHTED solution, not the unweighted one
  ---
  duration_ms: 8.617865
  type: 'test'
  ...
# Subtest: server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
not ok 121 - server parity on GL-type models: weighted local Batch Fit matches lmfit from the same start (committed C1s targets)
  ---
  duration_ms: 1427.207394
  type: 'test'
  location: '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_descent.test.js:455:1'
  failureType: 'testCodeFailure'
  error: |-
    Command failed: /Users/skyefortier/xps-app/venv/bin/python3 /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_server_parity_backend.py /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
    Traceback (most recent call last):
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_server_parity_backend.py", line 12, in <module>
        import fitting  # noqa: E402
        ^^^^^^^^^^^^^^
      File "/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/fitting.py", line 33, in <module>
        from lmfit import Model, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/__init__.py", line 38, in <module>
        from .confidence import conf_interval, conf_interval2d
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/confidence.py", line 10, in <module>
        from .minimizer import MinimizerException
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/minimizer.py", line 41, in <module>
        from .parameter import Parameter, Parameters
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/parameter.py", line 14, in <module>
        from .jsonutils import decode4js, encode4js
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/lmfit/jsonutils.py", line 8, in <module>
        import dill
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/__init__.py", line 33, in <module>
        from .session import (
      File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/dill/session.py", line 25, in <module>
        TEMPDIR = pathlib.PurePath(tempfile.gettempdir())
                                   ^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
        return _os.fsdecode(_gettempdir())
                            ^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
        tempdir = _get_default_tempdir()
                  ^^^^^^^^^^^^^^^^^^^^^^
      File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
        raise FileNotFoundError(_errno.ENOENT,
    FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous']
    
  code: 'ERR_TEST_FAILURE'
  stack: |-
    genericNodeError (node:internal/errors:983:15)
    wrappedFn (node:internal/errors:537:14)
    checkExecSyncError (node:child_process:916:11)
    execFileSync (node:child_process:952:15)
    TestContext.<anonymous> (/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/tests/js/local_lm_descent.test.js:468:31)
    Test.runInAsyncScope (node:async_hooks:214:14)
    Test.run (node:internal/test_runner/test:1047:25)
    Test.processPendingSubtests (node:internal/test_runner/test:744:18)
    Test.postRun (node:internal/test_runner/test:1173:19)
    Test.run (node:internal/test_runner/test:1101:12)
  ...
# Subtest: the local engine optimises a free LA m continuously and counts it as a degree of freedom
ok 122 - the local engine optimises a free LA m continuously and counts it as a degree of freedom
  ---
  duration_ms: 23.874564
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
ok 123 - an LA fit with m free converges across a kernel-width transition — run A: 201 pts at 0.03 eV, m 48 (a transition), noisy
  ---
  duration_ms: 25.79086
  type: 'test'
  ...
# Subtest: an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
ok 124 - an LA fit with m free converges across a kernel-width transition — run B: 61 pts at 0.05 eV, m 18/7 − 0.001, all free
  ---
  duration_ms: 19.399289
  type: 'test'
  ...
# Subtest: recovery from an amplitude of exactly zero (the new floor is not a trap)
ok 125 - recovery from an amplitude of exactly zero (the new floor is not a trap)
  ---
  duration_ms: 9.529397
  type: 'test'
  ...
1..125
# tests 125
# suites 0
# pass 35
# fail 88
# cancelled 0
# skipped 0
# todo 2
# duration_ms 60376.174133

codex
Both round-1 regressions pass, and the committed sweep reproduces its 210/210 result. I’m extending the sweep to starts exactly at—and extremely close to—the transitions. The broader tests hit a sandbox issue: Python’s import checks for a writable temporary directory. I’m checking whether they can run with an in-memory workaround.

exec
/bin/zsh -lc "node -e 'const cp=require('\\''child_process'\\''), orig=cp.execFileSync;
cp.execFileSync=function(file,args,opts){if(file.includes('\\''python'\\'')){if(args[0]==='\\''-c'\\''){args=[...args];args[1]=\"import tempfile; tempfile.tempdir='\\''/tmp'\\''; \"+args[1];}else{args=['\\''-c'\\'',\"import tempfile,runpy,sys; tempfile.tempdir='\\''/tmp'\\''; sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='\\''__main__'\\'')\",...args];}opts={...opts,env:{...process.env,PYTHONDONTWRITEBYTECODE:'\\''1'\\''}};}return orig.call(this,file,args,opts);};
require('\\''./tests/js/local_lm_descent.test.js'\\'');require('\\''./tests/js/lineshape_parity.test.js'\\'');require('\\''./tests/js/lineshape_roundtrip.test.js'\\'');' 2>&1 | tail -n 25" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/cam_transition_sweep.js'\\'','\\''utf8'\\'').split('\\''let freeFail'\\'')[0];new Function('\\''require'\\'','\\''__dirname'\\'',src+\"\\nlet count=0,bad=[];\\nfor(const k of [2,3,9,17,56])for(const off of [-1e-8,0,1e-8])for(const freq of [.1,.5,1,1.77,2.5,3])for(const noise of [.01,.1,1,5]) {\\nconst st=.05,m=6*k/7+off,be=grid(280,285,st),truth={id:1,name:'\\''la'\\'',shape:'\\''LACX'\\'',center:282.513,fwhm:.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:m,glMix:50,asymmetry:0};\\nconst run=fixCaM=>{const e=env();const d=e.evalAllPeaks(be,[truth]).map((v,i)=>v+noise*Math.sin(freq*i));e.state.peaks=[{...truth,fixCenter:true,fixFwhm:true,fixAmplitude:true,fixCaAlpha:true,fixCaBeta:true,fixCaM}];const o=e.runFitLocal(be,d,be.map(()=>0));return {o,chi:e.state.fitResult?.chi,m:e.state.peaks[0].caM};};\\nconst fr=run(false);count++;if("'!fr.o.success){bad.push({k,off,freq,noise,fr,hd:run(true)});if(bad.length<=8)console.log(JSON.stringify(bad.at(-1)));}'"\\n}console.log(JSON.stringify({count,fails:bad.length}));\\n\")(require,process.cwd()+'\\''/scripts'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '8358,8388p'; nl -ba templates/index.html | sed -n '8395,8475p'; sed -n '704,765p' fitting.py" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
  8358	      const { param } = paramMap[j];
  8359	      const step = H_REL * paramScale(j, params);
  8360	      const pPlus = [...params], pMinus = [...params];
  8361	      pPlus[j] = clamp(param, params[j] + step);
  8362	      pMinus[j] = clamp(param, params[j] - step);
  8363	      if (param === 'caM') {
  8364	        // LA's curve jumps where its kernel half-width changes (m = 6k/7):
  8365	        // a difference straddling a jump is not a derivative and stalled
  8366	        // fits that converge with m held (Codex round 1, caM unit). Keep
  8367	        // each side inside the current piece — one-sided when one side
  8368	        // crosses, the step halved when both would.
  8369	        const piece = _laKernelHalf(params[j]);
  8370	        let hh = step;
  8371	        for (let t = 0; t < 40; t++) {
  8372	          const up = clamp(param, params[j] + hh), dn = clamp(param, params[j] - hh);
  8373	          const upOk = _laKernelHalf(up) === piece, dnOk = _laKernelHalf(dn) === piece;
  8374	          if (upOk || dnOk) { pPlus[j] = upOk ? up : params[j]; pMinus[j] = dnOk ? dn : params[j]; break; }
  8375	          hh /= 2;
  8376	          if (t === 39) { pPlus[j] = params[j]; pMinus[j] = params[j]; }
  8377	        }
  8378	      }
  8379	      const span = pPlus[j] - pMinus[j];
  8380	      if (span === 0) { J.push(r.map(() => 0)); continue; }
  8381	      const rPlus = pPlus[j] === params[j] ? r : residuals(pPlus);
  8382	      const rMinus = pMinus[j] === params[j] ? r : residuals(pMinus);
  8383	      J.push(rPlus.map((v, i) => (v - rMinus[i]) / span));
  8384	    }
  8385	    const JtJ = Array.from({length: n}, () => new Array(n).fill(0));
  8386	    const Jtr = new Array(n).fill(0);
  8387	    for (let a = 0; a < n; a++) {
  8388	      for (let b = 0; b < n; b++) {
  8395	    }
  8396	    // Sensitivity: a model that does not respond to any free parameter here
  8397	    // (e.g. a peak far outside the window) cannot be optimised — that is a
  8398	    // failure, not a stationary point.
  8399	    let sens = 0;
  8400	    for (let j = 0; j < n; j++) if (!isDiscrete(j)) sens = Math.max(sens, JtJ[j][j] * paramScale(j, params) ** 2);
  8401	    if (n > 0 && sens / Math.max(chi, 1e-300) < SENS_MIN) {
  8402	      return fail('the model has no measurable sensitivity to its free parameters in this region.', iterations);
  8403	    }
  8404	    // ACTIVE SET: a parameter whose descent direction points into a wall of
  8405	    // the parameter box (or that has no sensitivity, or is discrete) is held
  8406	    // FIXED for this step. Solving the joint system with such a parameter
  8407	    // and then clipping it would leave the other components of the step
  8408	    // meaningless and let a tiny "agreed" step pass the ftol test at a
  8409	    // non-stationary point (Codex round 2). With r = data - model,
  8410	    // d(chi)/dp_j = +2 * (J_j . r), so the descent direction is -sign(J_j . r).
  8411	    const active = [];
  8412	    let gradCos = 0;
  8413	    const rNorm = Math.sqrt(chi);
  8414	    for (let j = 0; j < n; j++) {
  8415	      if (isDiscrete(j) || !(JtJ[j][j] > 0)) continue;
  8416	      if (Jtr[j] !== 0) {
  8417	        const probe = clamp(paramMap[j].param, params[j] - Math.sign(Jtr[j]) * 1e-6 * paramScale(j, params));
  8418	        if (probe === params[j]) continue;          // blocked by the box
  8419	      }
  8420	      active.push(j);
  8421	      if (rNorm > 0) gradCos = Math.max(gradCos, Math.abs(Jtr[j]) / (Math.sqrt(JtJ[j][j]) * rNorm));
  8422	    }
  8423	    // Projected gradient test (gtol) over the active set only. A failed
  8424	    // certificate has moved the point: restart the iteration so the
  8425	    // derivatives and active set are rebuilt there.
  8426	    if (gradCos < GTOL) { if (certify()) { converged = true; break; } continue; }
  8427	    // Linear model of the residual, for the predicted reduction (ftol test).
  8428	    const JtJ0 = JtJ.map(row => row.slice());
  8429	
  8430	    // Marquardt damping, then the DESCENT step on the active set:
  8431	    // JtJ_aa . dp_a = -Jt.r_a, dp = 0 for held parameters.
  8432	    const m = active.length;
  8433	    const A = active.map(a => active.map(b => (a === b ? JtJ[a][a] * (1 + lambda) + 1e-300 : JtJ[a][b])));
  8434	    const rhs = active.map(a => -Jtr[a]);
  8435	    const dpA = solveLinear(A, rhs, m);
  8436	    if (!dpA.every(Number.isFinite)) return fail('the normal equations are singular.', iterations);
  8437	    const dp = new Array(n).fill(0);
  8438	    active.forEach((a, k) => { dp[a] = dpA[k]; });
  8439	    const newParams = params.map((v, i) => clamp(paramMap[i].param, v + dp[i]));
  8440	    const step = newParams.map((v, i) => v - params[i]);
  8441	    const newChi = chiSq(newParams);
  8442	
  8443	    if (Number.isFinite(newChi) && newChi < chi) {
  8444	      const actred = (chi - newChi) / Math.max(chi, 1e-300);
  8445	      // predicted reduction of the linearised problem: (2 Jt.r . (-dp) - dp.JtJ.dp) / chi
  8446	      let lin = 0, quad = 0;
  8447	      for (let a = 0; a < n; a++) {
  8448	        lin += Jtr[a] * step[a];
  8449	        for (let b = 0; b < n; b++) quad += step[a] * JtJ0[a][b] * step[b];
  8450	      }
  8451	      const prered = (-2 * lin - quad) / Math.max(chi, 1e-300);
  8452	      const relStep = Math.max(0, ...step.map((d, i) => Math.abs(d) / paramScale(i, params)));
  8453	      params = newParams;
  8454	      chi = newChi;
  8455	      acceptedSteps++;
  8456	      lambda *= 0.7;
  8457	      if (chi === 0 || (prered > 0 && actred <= FTOL && prered <= FTOL && actred / prered <= 2) || relStep <= XTOL) {
  8458	        if (certify()) { converged = true; break; }
  8459	      }
  8460	    } else {
  8461	      lambda *= 3;
  8462	      if (lambda > 1e8) {
  8463	        // Even a tiny steepest-descent step no longer reduces the residual,
  8464	        // yet the projected gradient is not small: stalled, not converged.
  8465	        return fail('the optimiser stalled (no step reduces the residual) after ' + iterations + ' iterations.', iterations);
  8466	      }
  8467	    }
  8468	  }
  8469	  if (!converged) return fail('iteration limit (' + maxIter + ') reached.', iterations);
  8470	
  8471	  // ── Converged: commit the working copy to the live peaks ──────────────────
  8472	  applyParams(params);
  8473	  for (const p of work) {
  8474	    const live = getPeak(p.id);
  8475	    if (!live) continue;
        non-singular.

    With α=β=1 and m=0, this reduces exactly to amplitude × L(x) (a pure
    Lorentzian of peak height = amplitude, FWHM = `fwhm`).

    Parameters
    ----------
    fwhm  : Lorentzian FWHM in eV (must be > 0)
    alpha : high-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    beta  : low-BE-side exponent, dimensionless, default 1.0, bounds (0.1, 5.0)
    m     : Gaussian convolution kernel width in DATA POINTS (not eV);
            0–499, used CONTINUOUSLY (no rounding — see kernel note above).
    """
    fwhm = max(float(fwhm), 1e-9)
    alpha = max(float(alpha), 1e-3)
    beta = max(float(beta), 1e-3)
    # Continuous-σ kernel: m flows through to the kernel weights as a real
    # number, so the Jacobian column for m is well-defined under lmfit's
    # finite-difference perturbation. Previously m was rounded with
    # int(round(m)), making the function locally constant in m and
    # producing a singular Hessian whenever m varied — that poisoned
    # covariance estimation for every other free param too.
    # Defensive guard preserves the prior [0, 499] cap in case a saved
    # spec or caller bypasses the lmfit bound.
    m_cont = max(0.0, min(499.0, float(m)))

    eps = x - center
    # Base unit-amplitude Lorentzian
    L = 1.0 / (1.0 + 4.0 * (eps / fwhm) ** 2)
    # Piecewise exponentiation. BE-axis: high-BE side is eps ≥ 0.
    high = eps >= 0
    base = np.where(high, np.power(L, alpha), np.power(L, beta))

    # Below ε, treat as un-convolved Lorentzian so an optimizer that lands
    # exactly at m=0 returns the bare base curve rather than degenerating.
    if m_cont < 1e-3:
        return amplitude * base

    sigma_pts = m_cont / 3.0
    # Kernel half-width: ±3.5σ captures > 99.95% of the Gaussian. Use 3.5
    # rather than 3 specifically so the kernel-length quantization step
    # `ceil(3.5σ)` doesn't coincide with integer m — that would put a
    # discrete jump in the output exactly at integer m and re-break
    # backwards compat with previously-saved (integer-m) fits. With 3.5
    # the next jump from m=N is at m = 6(N+1)/7 ≠ integer.
    half = max(1, int(np.ceil(3.5 * sigma_pts)))
    k = np.arange(-half, half + 1, dtype=float)
    kern = np.exp(-(k ** 2) / (2.0 * sigma_pts ** 2))
    kern = kern / kern.sum()

    convolved = np.convolve(base, kern, mode='same')
    # np.convolve mode='same' returns max(len(base), len(kern)) — not
    # len(base). When the input grid is shorter than the kernel, trim
    # back to len(base) so the function's len(output) == len(x) contract
    # holds. lmfit's composite-fit residual path will broadcast the
    # per-peak arrays against the data grid, so a kernel-length return
    # surfaces as a cryptic shape mismatch downstream.
    if len(convolved) > len(base):
        excess = len(convolved) - len(base)
        start = excess // 2
        convolved = convolved[start:start + len(base)]


 succeeded in 2851ms:
{"k":3,"off":0,"freq":0.1,"noise":0.01,"fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":3.7901272913299625e-7,"certifyRestarts":0},"chi":0.00003828028564243262,"m":2.5714285714285716}}
{"k":3,"off":0,"freq":0.5,"noise":0.01,"fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.526860861825571e-7,"certifyRestarts":0},"chi":0.00004572129470443827,"m":2.5714285714285716}}
{"k":3,"off":0,"freq":0.5,"noise":0.1,"fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.00004524312212277895,"certifyRestarts":0},"chi":0.004569555334400674,"m":2.5714285714285716}}
{"k":3,"off":0,"freq":1,"noise":0.01,"fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.5600750827723656e-7,"certifyRestarts":0},"chi":0.000046056758336000895,"m":2.5714285714285716}}
{"k":3,"off":0,"freq":1,"noise":0.1,"fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.00004558704026395199,"certifyRestarts":0},"chi":0.004604291066659151,"m":2.5714285714285716}}
{"k":3,"off":0,"freq":2.5,"noise":0.01,"fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.5956698564794945e-7,"certifyRestarts":0},"chi":0.00004641626555044289,"m":2.5714285714285716}}
{"k":3,"off":0,"freq":2.5,"noise":0.1,"fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.00004596113198318792,"certifyRestarts":0},"chi":0.00464207433030198,"m":2.5714285714285716}}
{"k":3,"off":0,"freq":3,"noise":0.01,"fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.5124232330638036e-7,"certifyRestarts":0},"chi":0.000045575474653944414,"m":2.5714285714285716}}
{"count":360,"fails":32}

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/cam_transition_sweep.js'\\'','\\''utf8'\\'').split('\\''let freeFail'\\'')[0];new Function('\\''require'\\'','\\''__dirname'\\'',src+\"\\nlet bad=[],count=0,maxCert=0;\\nfor(const m of [0,.000999,.001,.001001,6/7,12/7,18/7,54/7,48,499])for(const noise of [.01,.1,1])for(const mode of ['\\''m'\\'','\\''amp_m'\\'','\\''all'\\'','\\''linked'\\'']) {\\nconst be=grid(280,285,.05),truth={id:1,name:'\\''la'\\'',shape:'\\''LACX'\\'',center:282.513,fwhm:.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:m,glMix:50,asymmetry:0};\\nconst peaks=[truth];if(mode==='\\''linked'\\'')peaks.push({...truth,id:2,center:283.713,amplitude:2500,linked:1,linkOffset:1.2,linkRatio:.5});\\nconst run=fixCaM=>{const e=env();const d=e.evalAllPeaks(be,peaks).map((v,i)=>v+noise*Math.sin(.5*i));e.state.peaks=peaks.map(p=>({...p,fixCenter:mode"'!=='"'\\''all'\\'',fixFwhm:mode"'!=='"'\\''all'\\'',fixAmplitude:mode==='\\''m'\\'',fixCaAlpha:mode"'!=='"'\\''all'\\'',fixCaBeta:mode"'!=='"'\\''all'\\'',fixCaM}));const o=e.runFitLocal(be,d,be.map(()=>0));maxCert=Math.max(maxCert,o.certifyRestarts||0);return {o,chi:e.state.fitResult?.chi,m:e.state.peaks[0].caM};};\\nconst fr=run(false),hd=run(true);count++;if("'!fr.o.success&&hd.o.success){bad.push({m,noise,mode,fr,hd});console.log(JSON.stringify(bad.at(-1)));}'"\\n}console.log(JSON.stringify({count,fails:bad.length,maxCert}));\")(require,process.cwd()+'\\''/scripts'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 1843ms:
{"m":0,"noise":0.1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.00004605361463481252,"certifyRestarts":0},"chi":0.004651415078116065,"m":0}}
{"m":0,"noise":1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.0045812538875899655,"certifyRestarts":0},"chi":0.4627066426465865,"m":0}}
{"m":0.000999,"noise":0.01,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.000999},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.6080005139038036e-7,"certifyRestarts":0},"chi":0.000046540805190428416,"m":0.000999}}
{"m":0.000999,"noise":0.1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.000999},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.00004605361463481252,"certifyRestarts":0},"chi":0.004651415078116065,"m":0.000999}}
{"m":0.000999,"noise":1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.000999},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.0045812538875899655,"certifyRestarts":0},"chi":0.4627066426465865,"m":0.000999}}
{"m":0.001,"noise":0.01,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.001},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.600709807521253e-7,"certifyRestarts":0},"chi":0.000046467169055964656,"m":0.001}}
{"m":0.001,"noise":0.1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.001},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.00004598079061167411,"certifyRestarts":0},"chi":0.004644059851779085,"m":0.001}}
{"m":0.001,"noise":1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.001},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.004574043788002667,"certifyRestarts":0},"chi":0.46197842258826943,"m":0.001}}
{"m":0.001001,"noise":0.01,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.001001},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.600709807521253e-7,"certifyRestarts":0},"chi":0.000046467169055964656,"m":0.001001}}
{"m":0.001001,"noise":0.1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.001001},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.00004598079061167411,"certifyRestarts":0},"chi":0.004644059851779085,"m":0.001001}}
{"m":0.001001,"noise":1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.001001},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.004574043788002667,"certifyRestarts":0},"chi":0.46197842258826943,"m":0.001001}}
{"m":2.5714285714285716,"noise":0.01,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.526860861825571e-7,"certifyRestarts":0},"chi":0.00004572129470443827,"m":2.5714285714285716}}
{"m":2.5714285714285716,"noise":0.01,"mode":"amp_m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":4.5721289634494895e-7,"certifyRestarts":0},"chi":0.00004572128963449489,"m":2.5714285714285716}}
{"m":2.5714285714285716,"noise":0.01,"mode":"all","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":2,"acceptedSteps":2,"chiReduced":4.7136979218912213e-7,"certifyRestarts":0},"chi":0.000045251500050155726,"m":2.5714285714285716}}
{"m":2.5714285714285716,"noise":0.01,"mode":"linked","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":3.23110506481093e-7,"certifyRestarts":0},"chi":0.0000323110506481093,"m":2.5714285714285716}}
{"m":2.5714285714285716,"noise":0.1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.00004524312212277895,"certifyRestarts":0},"chi":0.004569555334400674,"m":2.5714285714285716}}
{"m":2.5714285714285716,"noise":0.1,"mode":"linked","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":2.5714285714285716},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":0.00003228956088438629,"certifyRestarts":0},"chi":0.003228956088438629,"m":2.5714285714285716}}
{"m":7.714285714285714,"noise":0.01,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":4.171502272337418e-7,"certifyRestarts":0},"chi":0.00004213217295060792,"m":7.714285714285714}}
{"m":7.714285714285714,"noise":0.01,"mode":"amp_m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":4.213216839531223e-7,"certifyRestarts":0},"chi":0.00004213216839531223,"m":7.714285714285714}}
{"m":7.714285714285714,"noise":0.01,"mode":"linked","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":2.966920169913881e-7,"certifyRestarts":0},"chi":0.00002966920169913881,"m":7.714285714285714}}
{"m":7.714285714285714,"noise":0.1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.000041689624747732924,"certifyRestarts":0},"chi":0.004210652099521026,"m":7.714285714285714}}
{"m":7.714285714285714,"noise":0.1,"mode":"amp_m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":0.00004210650980575871,"certifyRestarts":0},"chi":0.004210650980575871,"m":7.714285714285714}}
{"m":7.714285714285714,"noise":0.1,"mode":"linked","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":0.000029647293604718604,"certifyRestarts":0},"chi":0.0029647293604718604,"m":7.714285714285714}}
{"m":7.714285714285714,"noise":1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.004145423897697565,"certifyRestarts":0},"chi":0.41868781366745406,"m":7.714285714285714}}
{"m":7.714285714285714,"noise":1,"mode":"amp_m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":2,"acceptedSteps":2,"chiReduced":0.004186854490302356,"certifyRestarts":0},"chi":0.41868544903023563,"m":7.714285714285714}}
{"m":7.714285714285714,"noise":1,"mode":"linked","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":7.714285714285714},"hd":{"o":{"success":true,"engine":"local","iterations":2,"acceptedSteps":2,"chiReduced":0.0029440242115843945,"certifyRestarts":0},"chi":0.29440242115843945,"m":7.714285714285714}}
{"m":48,"noise":0.01,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":48},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":5.461963273431825e-8,"certifyRestarts":0},"chi":0.000005516582906166143,"m":48}}
{"m":48,"noise":0.01,"mode":"amp_m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":48},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":5.5165811970568264e-8,"certifyRestarts":0},"chi":0.000005516581197056827,"m":48}}
{"m":48,"noise":0.01,"mode":"linked","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":48},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":3.8567292253162416e-8,"certifyRestarts":0},"chi":0.000003856729225316242,"m":48}}
{"m":48,"noise":0.1,"mode":"m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":48},"hd":{"o":{"success":true,"engine":"local","iterations":0,"acceptedSteps":0,"chiReduced":0.000005461650072986563,"certifyRestarts":0},"chi":0.0005516266573716428,"m":48}}
{"m":48,"noise":0.1,"mode":"amp_m","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":48},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":0.000005516264585254427,"certifyRestarts":0},"chi":0.0005516264585254427,"m":48}}
{"m":48,"noise":0.1,"mode":"linked","fr":{"o":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"m":48},"hd":{"o":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":0.000003856319025719706,"certifyRestarts":0},"chi":0.0003856319025719706,"m":48}}
{"count":120,"fails":33,"maxCert":0}

codex
I found a remaining transition failure. Starting exactly at m = 18/7, a noisy LA fit with amplitude and m free stalls after 24 iterations; holding m lets it converge. The one-sided Jacobian keeps proposing positive m steps across the jump, and damping cannot eliminate that jump. I’m checking the objective probes to confirm the cause.

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/cam_transition_sweep.js'\\'','\\''utf8'\\'').split('\\''let freeFail'\\'')[0];src=src.replace('\\''NAMES.map(extractFn)'\\'','\\''NAMES.map(n => instrument(extractFn(n)))'\\'');new Function('\\''require'\\'','\\''__dirname'\\'',src+\"\\nfunction instrument(s){return s.replace('\\''const newChi = chiSq(newParams);'\\'','\\''const newChi = chiSq(newParams); if(iterations===1||iterations===24) console.log(JSON.stringify({trace:true,iterations,params,newParams,chi,newChi,Jtr,lambda,certifyRestarts}));'\\'');}\\nconst be=grid(280,285,.05),truth={id:1,name:'\\''la'\\'',shape:'\\''LACX'\\'',center:282.513,fwhm:.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:18/7,glMix:50,asymmetry:0};\\nconst e=env(),d=e.evalAllPeaks(be,[truth]).map((v,i)=>v+.01*Math.sin(.5*i));\\nfunction chi(p){return e.evalAllPeaks(be,[p]).reduce((s,v,i)=>s+(d[i]-v)**2/Math.max(d[i],1),0);}\\nconsole.log(JSON.stringify({probes:[0,-1e-8,1e-8,-.001*truth.caM,.001*truth.caM].map(delta=>({delta,chi:chi({...truth,caM:truth.caM+delta})})),ampProbes:[4995,5005].map(amplitude=>({amplitude,chi:chi({...truth,amplitude})}))}));\\nfor(const fixCaM of [false,true]){e.state.peaks=[{...truth,fixCenter:true,fixFwhm:true,fixCaAlpha:true,fixCaBeta:true,fixCaM}];console.log(JSON.stringify({fixCaM,out:e.runFitLocal(be,d,be.map(()=>0)),p:e.state.peaks[0]}));}\\n\")(require,process.cwd()+'\\''/scripts'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
{"probes":[{"delta":0,"chi":0.00004572129470443826},{"delta":-1e-8,"chi":0.00004572130462079283},{"delta":1e-8,"chi":0.000048032778992732445},{"delta":-0.0025714285714285717,"chi":0.0001600917451951687},{"delta":0.0025714285714285717,"chi":0.00019049245033585422}],"ampProbes":[{"amplitude":4995,"chi":0.08900238233057775},{"amplitude":5005,"chi":0.08900506862981859}]}
{"trace":true,"iterations":1,"params":[5000,2.5714285714285716],"newParams":[4999.9947000298425,2.571521170337288],"chi":0.00004572129470443827,"newChi":0.000048340100495948,"Jtr":[1.3431496183936718e-7,-0.0004957481031656443],"lambda":0.001,"certifyRestarts":0}
{"trace":true,"iterations":24,"params":[5000,2.5714285714285716],"newParams":[5000,2.571428571428883],"chi":0.00004572129470443827,"newChi":0.00004803266316431328,"Jtr":[1.3431496183936718e-7,-0.0004957481031656443],"lambda":94143178.82699998,"certifyRestarts":0}
{"fixCaM":false,"out":{"success":false,"engine":"local","message":"the optimiser stalled (no step reduces the residual) after 24 iterations.","iterations":24},"p":{"id":1,"name":"la","shape":"LACX","center":282.513,"fwhm":0.8,"amplitude":5000,"caAlpha":1.2,"caBeta":1.5,"caM":2.5714285714285716,"glMix":50,"asymmetry":0,"fixCenter":true,"fixFwhm":true,"fixCaAlpha":true,"fixCaBeta":true,"fixCaM":false}}
{"trace":true,"iterations":1,"params":[5000],"newParams":[4999.999962290975],"chi":0.00004572129470443827,"newChi":0.00004572128963449489,"Jtr":[1.3431496183936718e-7],"lambda":0.001,"certifyRestarts":0}
{"fixCaM":true,"out":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":4.5721289634494895e-7,"certifyRestarts":0},"p":{"id":1,"name":"la","shape":"LACX","center":282.513,"fwhm":0.8,"amplitude":4999.999962290975,"caAlpha":1.2,"caBeta":1.5,"caM":2.5714285714285716,"glMix":50,"asymmetry":0,"fixCenter":true,"fixFwhm":true,"fixCaAlpha":true,"fixCaBeta":true,"fixCaM":true,"support":{"f":194565821641.2768,"delta_chi2":88958.00284234289,"supported":true,"fitKey":"K"}}}

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/cam_transition_sweep.js'\\'','\\''utf8'\\'').split('\\''let freeFail'\\'')[0];new Function('\\''require'\\'','\\''__dirname'\\'',src+\"\\nconst be=grid(280,285,.05),truth={id:1,name:'\\''la'\\'',shape:'\\''LACX'\\'',center:282.513,fwhm:.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:0,glMix:50,asymmetry:0};\\nconst e=env(),d=e.evalAllPeaks(be,[truth]);\\nconst p={...truth,caM:.001,fixCenter:true,fixFwhm:true,fixAmplitude:true,fixCaAlpha:true,fixCaBeta:true,fixCaM:false};\\nconst objective=m=>e.evalAllPeaks(be,[{...p,caM:m}]).reduce((s,v,i)=>s+(d[i]-v)**2/Math.max(d[i],1),0);\\nconsole.log(JSON.stringify({chiAtStart:objective(.001),chiAtMinusProbe:objective(0),out:(e.state.peaks=[p],e.runFitLocal(be,d,be.map(()=>0)))}));\")(require,process.cwd()+'\\''/scripts'\\'');'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
{"chiAtStart":0.21969684554889973,"chiAtMinusProbe":0,"out":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1}}

exec
/bin/zsh -lc "node -e 'const fs=require('\\''fs'\\'');let src=fs.readFileSync('\\''scripts/cam_transition_sweep.js'\\'','\\''utf8'\\'').split('\\''let freeFail'\\'')[0];for(const ref of ['\\''main'\\'','\\''df388ce'\\'','\\''HEAD'\\'']){console.log(ref);let s=src;if(ref"'!=='"'\\''HEAD'\\'')s=s.replace(\"fs.readFileSync('\\''templates/index.html'\\'', '\\''utf8'\\'')\",\"require('\\''child_process'\\'').execFileSync('\\''git'\\'',['\\''show'\\'','\\''\"+ref+\":templates/index.html'\\''],{encoding:'\\''utf8'\\''})\").replace(\"'\\''_laKernelHalf'\\'',\",'\\'''\\'');new Function('\\''require'\\'','\\''__dirname'\\'',s+\"\\nconst be=grid(280,285,.05),truth={id:1,name:'\\''la'\\'',shape:'\\''LACX'\\'',center:282.513,fwhm:.8,amplitude:5000,caAlpha:1.2,caBeta:1.5,caM:0,glMix:50,asymmetry:0};\\nconst e=env(),d=e.evalAllPeaks(be,[truth]);e.state.peaks=[{...truth,caM:.001,fixCenter:true,fixFwhm:true,fixAmplitude:true,fixCaAlpha:true,fixCaBeta:true,fixCaM:false}];console.log(JSON.stringify({out:e.runFitLocal(be,d,be.map(()=>0)),m:e.state.peaks[0].caM}));\")(require,process.cwd()+'\\''/scripts'\\'');}'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 42ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-jBTV0X51' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0cJ4jJI0' (errno=Operation not permitted)
{"out":{"success":true,"engine":"local","iterations":1,"acceptedSteps":1,"chiReduced":0,"certifyRestarts":0},"m":0.0008001998001998}
HEAD
{"out":{"success":false,"engine":"local","message":"the model has no measurable sensitivity to its free parameters in this region.","iterations":1},"m":0.001}

 succeeded in 149348ms:
  ---
  duration_ms: 1538.58565
  type: 'test'
  ...
# Subtest: autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
ok 124 - autofit.reference.peak_to_backend_spec is the page’s peakToBackendSpec, shape by shape
  ---
  duration_ms: 1553.203462
  type: 'test'
  ...
# Subtest: autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
ok 125 - autofit.reference.apply_backend_params is the page’s _applyBackendParams, shape by shape and lock by lock
  ---
  duration_ms: 1547.881664
  type: 'test'
  ...
1..125
# tests 125
# suites 0
# pass 123
# fail 0
# cancelled 0
# skipped 0
# todo 2
# duration_ms 149391.034531

codex
A second regression is confirmed at the 1e-3 threshold: with only m free, a noiseless m = 0 spectrum started at m = 0.001 fails the sensitivity check before certification can probe m = 0, which has zero error. This case succeeds on both main and df388ce. The remaining transition stall also reproduces with all parameters free and with a linked LA child.

exec
/bin/zsh -lc "git status --short; nl -ba templates/index.html | sed -n '8270,8304p'; nl -ba scripts/cam_transition_sweep.js | sed -n '13,24p'" in /Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4mq4DS2Z' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-6lCJKJ2x' (errno=Operation not permitted)
?? docs/autofit/codex/cam_continuous_r2_verdict_runA.md
?? docs/autofit/codex/cam_continuous_r2_verdict_runB.md
?? docs/autofit/codex/cam_continuous_recheck_prompt.txt
  8270	  }
  8271	
  8272	  let params = freeParams.map((v, i) => clamp(paramMap[i].param, v));
  8273	  let chi = chiSq(params);
  8274	  if (!Number.isFinite(chi)) return fail('the model is not finite at the starting parameters.');
  8275	  let lambda = 0.001;
  8276	  // Feasible-descent certificate (see PROBE_REL below). Returns true when
  8277	  // no single-parameter feasible move improves the residual by more than
  8278	  // FTOL; otherwise moves to the best such point and returns false.
  8279	  function certify() {
  8280	    applyParams(params);                     // working copy = current point
  8281	    let bestChi = chi, bestParams = null;
  8282	    for (let j = 0; j < params.length; j++) {
  8283	      if (isDiscrete(j)) continue;
  8284	      for (const sgn of [-1, 1]) {
  8285	        const trial = [...params];
  8286	        trial[j] = clamp(paramMap[j].param, params[j] + sgn * PROBE_REL * paramScale(j, params));
  8287	        if (trial[j] === params[j]) continue;
  8288	        const c = chiSq(trial);
  8289	        if (Number.isFinite(c) && c < bestChi) { bestChi = c; bestParams = trial; }
  8290	      }
  8291	    }
  8292	    applyParams(params);
  8293	    if (bestParams && bestChi < chi * (1 - FTOL)) {
  8294	      params = bestParams; chi = bestChi; certifyRestarts++;
  8295	      lambda = Math.max(lambda, 1e-3);
  8296	      return false;
  8297	    }
  8298	    return true;
  8299	  }
  8300	  // Finite-difference step per parameter. A centre's natural scale is the
  8301	  // peak WIDTH, not its binding energy: h*|285 eV| = 0.03 eV is wider than
  8302	  // a narrow peak and gave misleading derivatives (Codex round 1).
  8303	  const H_REL = 1e-4;
  8304	  // Scale of parameter j at the parameter VECTOR `vec` — a pure function of
    13	let freeFail = 0, heldFail = 0, worse = 0, n = 0; const fails = [];
    14	for (const st of [0.03, 0.05, 0.1]) for (const k of [2, 3, 5, 9, 17, 33, 56]) for (const off of [-0.003, -0.0005, 0, 0.0005, 0.003]) for (const startDelta of [-0.4, 0.3]) {
    15	  const mT = 6 * k / 7 + off; const be = grid(280, 280 + 150 * st, st);
    16	  const truth = { id: 1, name: 'la', shape: 'LACX', center: 280 + 75 * st + 0.013, fwhm: 0.8, amplitude: 5000, caAlpha: 1.2, caBeta: 1.5, caM: mT, glMix: 50, asymmetry: 0 };
    17	  const run = fixCaM => { const e = env(); e.state.peaks = [{ ...truth }]; const d = e.evalAllPeaks(be, e.state.peaks).map((v, i) => v + 5 * Math.sin(1.77 * i));
    18	    e.state.peaks = [{ ...truth, amplitude: 4600, caM: Math.max(0.01, mT + startDelta), fixCenter: true, fixFwhm: true, fixCaM }]; const o = e.runFitLocal(be, d, be.map(() => 0)); return { o, chi: e.state.fitResult && e.state.fitResult.chi }; };
    19	  const fr = run(false), hd = run(true); n++;
    20	  if (!fr.o.success) { freeFail++; fails.push({ st, k, off, startDelta, msg: fr.o.message }); }
    21	  if (!hd.o.success) heldFail++;
    22	  if (fr.o.success && hd.o.success && fr.chi > hd.chi * (1 + 1e-9)) worse++;
    23	}
    24	console.log(JSON.stringify({ cases: n, free_failed: freeFail, held_failed: heldFail, free_ended_worse_than_held: worse, first_fails: fails.slice(0, 5) }));

codex
The two round-1 reproducers pass, but the underlying transition problem is not fully closed.

1. **MAJOR — Exact-transition starts still exhaust damping.** [templates/index.html:8374](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/templates/index.html:8374), with unrestricted LM steps at line 8439.

   Reproducer: 101 points, `BE[i] = 280 + 0.05*i`; LA center `282.513`, FWHM `0.8`, amplitude `5000`, α `1.2`, β `1.5`, m `18/7`. Generate data from that peak plus `0.01*sin(0.5*i)`. Start at those parameters, with only amplitude and m free.

   **Result:** free m fails after 24 iterations; held m converges in one. The within-piece derivative proposes increasing m, but every positive step crosses the jump. Even the final proposed increase of approximately `3.1e-13` raises χ² from `4.572129e-5` to `4.803266e-5`. Certification is never reached. This also reproduces with all parameters free and with a linked LA child.

   The step/active-set logic needs to handle a piece boundary; constraining only the Jacobian is insufficient.

2. **MAJOR — Threshold protection creates a zero derivative that prevents an exact recovery.** [templates/index.html:8374](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/templates/index.html:8374), followed by the sensitivity rejection at [line 8401](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/templates/index.html:8401).

   Use the same grid and peak parameters, generate **noiseless data at m = 0**, and start at **m = 0.001**, with only m free.

   **Result:** HEAD fails immediately with “no measurable sensitivity.” The permitted within-piece difference is numerically zero. Yet the certificate’s negative probe would reach m = 0 and reduce χ² from `0.2196968455` to exactly zero.

   This case succeeds on **main and df388ce**, so it is a regression introduced by the round-1 fix. A zero m column must not prevent checking the reachable threshold branch.

Validation: the committed 210-case sweep passes. The three relevant test files yield **123 passes, 2 todo**, using an in-memory Python temporary-directory initialization workaround for the read-only sandbox. Additional probes found no certificate-restart exhaustion. No files changed.

**VERDICT: NO-GO.**
tokens used
74,273
The two round-1 reproducers pass, but the underlying transition problem is not fully closed.

1. **MAJOR — Exact-transition starts still exhaust damping.** [templates/index.html:8374](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/templates/index.html:8374), with unrestricted LM steps at line 8439.

   Reproducer: 101 points, `BE[i] = 280 + 0.05*i`; LA center `282.513`, FWHM `0.8`, amplitude `5000`, α `1.2`, β `1.5`, m `18/7`. Generate data from that peak plus `0.01*sin(0.5*i)`. Start at those parameters, with only amplitude and m free.

   **Result:** free m fails after 24 iterations; held m converges in one. The within-piece derivative proposes increasing m, but every positive step crosses the jump. Even the final proposed increase of approximately `3.1e-13` raises χ² from `4.572129e-5` to `4.803266e-5`. Certification is never reached. This also reproduces with all parameters free and with a linked LA child.

   The step/active-set logic needs to handle a piece boundary; constraining only the Jacobian is insufficient.

2. **MAJOR — Threshold protection creates a zero derivative that prevents an exact recovery.** [templates/index.html:8374](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/templates/index.html:8374), followed by the sensitivity rejection at [line 8401](/Users/skyefortier/xps-app/.claude/worktrees/fix-cam-continuous/templates/index.html:8401).

   Use the same grid and peak parameters, generate **noiseless data at m = 0**, and start at **m = 0.001**, with only m free.

   **Result:** HEAD fails immediately with “no measurable sensitivity.” The permitted within-piece difference is numerically zero. Yet the certificate’s negative probe would reach m = 0 and reduce χ² from `0.2196968455` to exactly zero.

   This case succeeds on **main and df388ce**, so it is a regression introduced by the round-1 fix. A zero m column must not prevent checking the reachable threshold branch.

Validation: the committed 210-case sweep passes. The three relevant test files yield **123 passes, 2 todo**, using an in-memory Python temporary-directory initialization workaround for the read-only sandbox. Additional probes found no certificate-restart exhaustion. No files changed.

**VERDICT: NO-GO.**
