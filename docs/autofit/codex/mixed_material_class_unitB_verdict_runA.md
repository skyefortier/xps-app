2026-07-20T19:22:43.294103Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 86 column 5
OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f80fb-0c01-7941-b1a4-52f2cb3dd1cd
--------
user
You are an adversarial reviewer for a follow-up fix in this repo (XPS
peak-fitting web app), branch feature-autofit-stage2. Review commit
bdc909a ("fix(mixed): rebase MIXED's own 2 accepted Codex findings onto
the corrected engine") -- `git show bdc909a` gives the full diff. This is
the third round in a review chain: MIXED material class (77bf3a8) -> both
Codex reviews NO-GO x2 (frontend copy overstated scope; a shared-width
degeneracy risk flagged; a weak provenance guard test) -> a separate
engine-level refactor (5070662 broad_justification, then ad7e668 fixing a
_retag_slot regression the refactor introduced) closed the underlying
mechanism -> this commit rebases MIXED's own two remaining findings onto
that corrected engine and adds new coverage. Your job is to verify this
round's specific claims, not to re-litigate whether MIXED itself should
exist.

WHAT THIS COMMIT CHANGES (templates/index.html, tests/autofit/
test_c1s_mixed_material_class.py, tests/js/fp_material_mixed.test.js):

1. Frontend copy fix (Codex run B's original MAJOR on 77bf3a8):
   FP_STRINGS.materials.mixed.hint used to say "Peak width limits are
   relaxed accordingly" with no region named -- read as global. Now says
   "For C 1s, contamination/adventitious peak width limits are relaxed
   accordingly -- other regions are unaffected."

2. Provenance guard test fix (both runs' original MINOR on 77bf3a8):
   test_mixed_provenance_relaxation_record_asserts_no_new_value used to
   only assert the relaxation record's `value` field `isinstance(...,
   str)` -- so a lab-derived number smuggled into prose (e.g. "relax to
   3.5 eV based on our spectra") would still have passed, missing the
   exact provenance-audit trap this feature exists to avoid. Now also
   asserts `not any(ch.isdigit() for ch in rec["value"])`.

3. THE ACTUAL FINDING, encoded directly: a MIXED contamination slot
   fitting at ~6-10 eV must now be flagged unphysical and route to
   CONDITIONAL -- the exact scenario both Codex reviews of the
   broad_justification refactor (5070662) used to demonstrate that bug,
   now pinned as a permanent regression test:
   test_mixed_wide_contamination_is_flagged_unphysical (direct
   _unphysical_width_flags call) and
   test_mixed_wide_contamination_routes_to_conditional (a real ModelReport
   from an actual fast MIXED C 1s fit, with its plausibility flags
   replaced by the ACTUAL flag _unphysical_width_flags produces for the
   8 eV scenario, run through rank_and_filter and confirmed to land in
   the CONDITIONAL tier, not survive clean).

4. A new test, test_mixed_shared_width_contamination_all_flagged_
   independently, addressing a risk 77bf3a8's OWN commit message flagged
   as KNOWN and unresolved at the time: C 1s's "_linked" candidate
   families (A1_linked/A2_linked/A3_linked/AG*_linked/MG*_linked) share
   ONE lmfit width parameter (_SHARED_CONTAM_FWHM) across all 3
   contaminant slots. Under MIXED that shared parameter's range ALSO
   widens to (0.8, 15.0) -- so in principle a single fat shared-width
   component could absorb signal across the whole ~280-292 eV
   contaminant span (the same overlap-degeneracy class c1s.py's own
   MG-family comments document for a free position, reachable here
   through width instead). The commit claims this is ALREADY closed by
   the broad_justification mechanism: sharing one lmfit parameter across
   3 slots does not create one shared EXEMPTION, because
   _unphysical_width_flags evaluates each FittedComponent independently
   against its OWN slot's fwhm_range/broad_justification -- so a wide
   shared value flags every slot built on it, not just some.

ADVERSARIAL QUESTIONS -- ATTACK THESE SPECIFICALLY:

(a) RED-GREEN ON THE REGRESSION TEST (item 3). Verify
    test_mixed_wide_contamination_is_flagged_unphysical and
    test_mixed_wide_contamination_routes_to_conditional actually exercise
    the fix, not pass incidentally -- this codebase has a documented prior
    instance of exactly this failure mode (a "laundered" regression test
    in the earlier Tougaard background work this session, where a test's
    own fixture collapsed the quantity under test to near-zero so the
    assertion passed regardless of whether the fix was present). If your
    sandbox can run Python (even without pytest -- direct import and
    exec), simulate reverting autofit/engine.py's _unphysical_width_flags
    to the OLD numeric rule (`vouched = declared_hi > FWHM_MAX_ORDINARY_EV`
    instead of `slot.broad_justification is not None`, and the DS_G/
    ASYM_GL branches' `declared_hi <= FWHM_MAX_ORDINARY_EV` instead of
    `not vouched`) and confirm both tests would fail against that
    reverted logic. If your sandbox cannot execute Python, verify by
    close reading: trace exactly what `_unphysical_width_flags` would
    return for an 8.0 eV component in a MIXED contamination slot
    (fwhm_range=(0.8,15.0)) under BOTH the old rule (declared_hi=15.0 > 2.0
    -> exempt -> no flag) and the new rule (broad_justification=None ->
    not vouched -> flagged) and confirm the test's own assertions would
    only pass under the new rule.

(b) THE SHARED-WIDTH DEGENERACY (item 4) -- INDEPENDENTLY VERIFY, DON'T
    JUST TRUST THE CLAIM. Construct your own scenario (or trace the code
    precisely) confirming or refuting: does a wide SHARED contamination
    width (all 3 linked slots reporting the same fitted fwhm, e.g. via
    resolve()'s A3_linked candidate and its shared_fwhm_params) actually
    get flagged for EVERY slot built on it, or is there any path where a
    shared-width component can go wide while looking acceptable (e.g. if
    only 1 or 2 of the 3 contaminant slots are present in a given
    candidate, if the offset-linked family behaves differently, or if
    some other candidate family's shared-width construction differs from
    A3_linked's). If you find a gap the test doesn't cover, that is a real
    finding, not a hypothetical -- say so plainly.

(c) THE PROVENANCE DIGIT-CHECK (item 2). Take the exact string "relax to
    3.5 eV based on our spectra" and confirm it fails the updated
    assertion (`not any(ch.isdigit() for ch in value)` -- "3.5" contains
    digits, so this should correctly reject it). Also check the OPPOSITE
    direction: does the ACTUAL current value of the
    mixed_material_class_width_relaxation record (read it directly from
    autofit/regions/c1s.py's provenance()) still pass the digit check --
    i.e. does the real record's prose contain any digit that would now
    make this stricter test fail spuriously (e.g. a DOI number, a year, or
    an eV figure accidentally left in the value field rather than the
    source field)?

(d) FRONTEND COPY ACCURACY (item 1). Read FP_STRINGS.materials.mixed.hint
    in templates/index.html literally, as a chemist with no other context
    would. Does it now accurately scope the relaxation to C 1s
    contamination without implying (i) other regions changed, or (ii)
    charge correction changed or was corrected for? Is "other regions are
    unaffected" actually true given everything else in this review chain
    (broad_justification only applies to C 1s's own slots; MIXED is
    read nowhere else in the codebase)?

(e) CHARGE-CORRECTION ISOLATION, RE-CONFIRM. Verify
    test_material_class_does_not_affect_charge_correction in
    tests/test_api_analyze.py still passes and still genuinely proves
    isolation (app.py's `corrected = energy - cc_shift` has zero reference
    to material_class) -- this is unchanged by bdc909a, but re-confirm
    nothing in this round's changes reaches it.

(f) SCOPE. Confirm bdc909a's diff touches only templates/index.html,
    tests/autofit/test_c1s_mixed_material_class.py, and
    tests/js/fp_material_mixed.test.js -- no diff in autofit/engine.py,
    autofit/grammar.py, autofit/regions/c1s.py, or app.py.

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll review the target commit in code-review mode and verify the specific regression claims against the current branch. I’m going to inspect the diff, the relevant engine and C 1s code paths, and run targeted tests or direct Python checks where the read-only sandbox allows it.
exec
/bin/zsh -lc 'rg -n "mixed|mixed_material_class_width_relaxation|_unphysical_width_flags|FWHM_MAX_ORDINARY_EV|broad_justification|corrected = energy - cc_shift|material_class" autofit tests templates app.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:243:    mc_raw = body.get("material_class", "")
app.py:247:        raise _AnalyzeError(f"Unknown material_class '{mc_raw}'")
app.py:253:    corrected = energy - cc_shift   # frontend getCorrectedBE convention
app.py:289:                      material_class=mclass,
app.py:881:            "material_classes": [m.value for m in MaterialClass],
app.py:897:          "material_class": "conductor" | "insulator" | "semiconductor" | "mixed",
autofit/candidates.py:73:# 2.4 eV (just above FWHM_MAX_ORDINARY_EV = 2.0, the engine's ordinary-
tests/test_api_analyze_progress.py:60:    "session_id": sid, "material_class": "insulator",
tests/test_api_analyze_progress.py:164:    """Cheap, request-shape validation (session/region/roi/material_class)
tests/test_api_analyze_progress.py:168:        "session_id": "not-a-uuid", "material_class": "insulator",
templates/index.html:10652:// legacy via t._legacy), so an element can hold mixed tiers (e.g. Si: machine
templates/index.html:13023:  // Only "mixed" gets an entry — conductor/semiconductor/insulator render
templates/index.html:13026:    mixed: {
templates/index.html:13027:      label: 'mixed (analyte in matrix)',
templates/index.html:13324:  // failure, mixed regions or not). That is what distinguishes it from
templates/index.html:13326:  // array — e.g. a mixed curated+structural request that still
templates/index.html:13430:  mat.innerHTML = _fpMeta.material_classes
templates/index.html:13899:      material_class: document.getElementById('fp-material').value,
tests/test_api_analyze_coverage.py:81:        "session_id": sid, "material_class": "conductor",
tests/test_api_analyze_coverage.py:102:        "session_id": sid, "material_class": "insulator",
tests/test_mixed_ds_lacx_e2e.py:89:print("OK — mixed DS + LACX recovered:")
tests/test_api_analyze.py:53:    assert set(meta["material_classes"]) == {"conductor", "insulator",
tests/test_api_analyze.py:54:                                             "semiconductor", "mixed"}
tests/test_api_analyze.py:65:        "session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:96:        "session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:116:    ({"material_class": "plasma"}, "material_class"),
tests/test_api_analyze.py:126:    base = {"session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:137:        "session_id": "0" * 32, "material_class": "insulator",
tests/test_api_analyze.py:150:    base = {"session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:168:            "session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:175:def test_analyze_material_class_mixed_accepted(client):
tests/test_api_analyze.py:180:    tests/autofit/test_c1s_mixed_material_class.py, against C 1s)."""
tests/test_api_analyze.py:183:        "session_id": sid, "material_class": "mixed",
tests/test_api_analyze.py:192:def test_analyze_start_material_class_mixed_accepted(client):
tests/test_api_analyze.py:199:        "session_id": sid, "material_class": "mixed",
tests/test_api_analyze.py:208:def test_material_class_does_not_affect_charge_correction(client):
tests/test_api_analyze.py:214:    must be byte-identical regardless of material_class. material_class
tests/test_api_analyze.py:215:    only ever reaches Phase.material_class, consumed by grammar
tests/test_api_analyze.py:228:        {**base, "material_class": "conductor"}, upload_folder)
tests/test_api_analyze.py:229:    ctx_mixed = _validate_analyze_request(
tests/test_api_analyze.py:230:        {**base, "material_class": "mixed"}, upload_folder)
tests/test_api_analyze.py:231:    assert np.array_equal(ctx_conductor.x, ctx_mixed.x)
tests/test_api_analyze.py:232:    assert np.array_equal(ctx_conductor.y, ctx_mixed.y)
autofit/confidence.py:7:  unavailable}``; kinds are NEVER mixed in one numeric field.  ``covariance``
tests/autofit/test_methods_seam.py:9:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
autofit/engine.py:116:FWHM_MAX_ORDINARY_EV = 2.0
autofit/engine.py:120:PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV
autofit/engine.py:753:def _unphysical_width_flags(
autofit/engine.py:757:    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.
autofit/engine.py:761:    only if it carries an explicit ``ComponentSlot.broad_justification``
autofit/engine.py:771:    ``broad_justification`` is INDEPENDENT of ``fwhm_range``'s own magnitude
autofit/engine.py:774:    FWHM_MAX_ORDINARY_EV`` alone, which conflated "the optimizer may search
autofit/engine.py:791:        vouched = slot.broad_justification is not None
autofit/engine.py:803:            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
autofit/engine.py:806:                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
autofit/engine.py:817:            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
autofit/engine.py:820:                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
autofit/engine.py:828:        # signature in transferable units. Unaffected by broad_justification
autofit/engine.py:845:        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
autofit/engine.py:847:                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
autofit/engine.py:2318:            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
autofit/engine.py:2457:            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
autofit/engine.py:2598:        # A future mixed-background grammar only affects DETECTION here —
autofit/engine.py:2830:                unphysical_widths=_unphysical_width_flags(primary.components, model),
autofit/coverage.py:124:    "user-overridable: the declared Phase.material_class wins."
autofit/coverage.py:405:                   "Phase.material_class wins)"},
tests/autofit/test_b1s_cl2p_parity_gates.py:36:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_b1s_cl2p_parity_gates.py:38:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
autofit/grammar.py:16:``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
autofit/grammar.py:88:    # tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction).
autofit/grammar.py:91:    MIXED = "mixed"
autofit/grammar.py:102:    material_class: MaterialClass
autofit/grammar.py:172:    # autofit.engine._unphysical_width_flags must not exempt it, REGARDLESS
autofit/grammar.py:176:    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
autofit/grammar.py:181:    broad_justification: Optional[str] = None
autofit/grammar.py:402:                f"{chosen.material_class.value}) — derived structure only")
autofit/grammar.py:436:            f"{slug}: phase {chosen.id!r} ({chosen.material_class.value}"
autofit/grammar.py:595:    reconstruction this replaced was exactly how broad_justification got
autofit/grammar.py:599:    tests/autofit/test_broad_justification.py's
tests/autofit/test_stage2_rereview_findings.py:94:    pa = Phase(id="B-4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:96:    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:103:    pa = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_stage2_rereview_findings.py:105:    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:124:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
autofit/regions/u4f.py:222:            broad_justification=_main_justification,
autofit/regions/u4f.py:231:            broad_justification=_main_justification,
autofit/regions/u4f.py:239:            broad_justification=_sat_justification,
autofit/regions/u4f.py:249:            broad_justification=_sat_justification,
autofit/regions/u4f.py:260:            broad_justification=_sat_justification,
autofit/regions/u4f.py:270:            broad_justification=_sat_justification,
autofit/regions/u4f.py:277:            broad_justification=_sat_justification,
tests/autofit/test_fit_full_window_option.py:147:def test_full_window_mixed_model_branches_per_slot_not_per_region():
tests/test_api_fit_full_window_option.py:60:        "session_id": sid, "material_class": "insulator",
tests/test_api_fit_full_window_option.py:75:        "session_id": sid, "material_class": "insulator",
tests/fixtures/curated_records_snapshot.json:1904:              "state": "U₃O₈ (mixed)",
autofit/regions/b1s.py:96:                broad_justification=(
tests/autofit/test_structural_fallback.py:34:    return Phase(id="sample", material_class=MaterialClass(mc),
tests/autofit/test_structural_fallback.py:227:    p1 = Phase(id="a", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:229:    p2 = Phase(id="b", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:280:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:304:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:322:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:346:def test_api_mixed_deep_plus_structural_runs_and_flags(client):
tests/autofit/test_structural_fallback.py:351:        "session_id": sid, "material_class": "insulator",
tests/autofit/test_structural_fallback.py:374:        "session_id": sid, "material_class": "conductor",
autofit/regions/n1s.py:80:            broad_justification=_justification,
autofit/regions/n1s.py:87:            broad_justification=_justification,
tests/fixtures/xps_legacy_snapshot.json:491:    "state": "U₃O₈ (mixed)",
tests/autofit/test_u4f_parity_gate.py:30:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_u4f_parity_gate.py:32:BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
autofit/regions/cl2p.py:147:                broad_justification=_empirical_justification,
autofit/regions/cl2p.py:164:                    broad_justification=_coster_kronig_justification,
autofit/regions/cl2p.py:175:                broad_justification=_empirical_justification,
autofit/regions/c1s.py:95:# cap derived from THIS LAB'S OWN mixed-phase spectra would be exactly
autofit/regions/c1s.py:125:def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
autofit/regions/c1s.py:128:    if material_class is MaterialClass.MIXED:
autofit/regions/c1s.py:243:            {"constant": "mixed_material_class_width_relaxation",
autofit/regions/c1s.py:268:            {"constant": "mixed_fwhm_ceiling_numeric_guard",
autofit/regions/c1s.py:293:        - M0–M3:  mixed graphitic (DS+G) + aliphatic (PV) two-main models
autofit/regions/c1s.py:306:        contam_fwhm = _contamination_fwhm_range(phase.material_class)
autofit/regions/c1s.py:337:            broad_justification=(
autofit/regions/c1s.py:404:        # --- M family: mixed graphitic (DS+G) + aliphatic (PV) two mains ---
tests/js/ref_core.test.js:286:test('serializeRefCompoundMarkers: mixed valid+invalid → invalid be dropped, valid kept', () => {
tests/autofit/test_cl2p_freewidth.py:41:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_cl2p_freewidth.py:183:def test_excess_area_link_rejects_mixed_shapes():
tests/autofit/test_stage2_completeness.py:301:    flags = eng._unphysical_width_flags([fat], m)
tests/autofit/test_stage2_completeness.py:306:    assert eng._unphysical_width_flags([thin], m) == []
tests/autofit/test_stage2_completeness.py:327:    assert eng._unphysical_width_flags([comp(4.0)], m), "4.0 ≥ 0.7×5.0"
tests/autofit/test_stage2_completeness.py:328:    assert eng._unphysical_width_flags([comp(3.0)], m) == []
tests/autofit/test_stage2_completeness.py:377:    flags = eng._unphysical_width_flags([fat], m)   # eff = 1.7×1.25 = 2.13
tests/autofit/test_stage2_completeness.py:382:    assert eng._unphysical_width_flags([ok], m) == []   # eff = 1.65
tests/autofit/test_reference_bridge.py:271:    phase = Phase(id="s", material_class=MaterialClass("conductor"),
tests/autofit/test_reference_bridge.py:289:    phase2 = Phase(id="s", material_class=MaterialClass("conductor"),
autofit/methods/bayesian_exchange_mc.py:42:  mixed with 'covariance'/'stability_mad' numerics (spec §5 discipline).
autofit/methods/bayesian_exchange_mc.py:559:                # typed posterior kind — NEVER mixed with covariance /
tests/js/fp_material_mixed.test.js:2:// clear label ("mixed (analyte in matrix)" reads better than bare "mixed")
tests/js/fp_material_mixed.test.js:27:test('FP_STRINGS.materials.mixed has a clear, non-bare label', () => {
tests/js/fp_material_mixed.test.js:28:  assert.ok(FP_STRINGS.materials && FP_STRINGS.materials.mixed,
tests/js/fp_material_mixed.test.js:29:    'FP_STRINGS.materials.mixed must exist');
tests/js/fp_material_mixed.test.js:30:  const label = FP_STRINGS.materials.mixed.label;
tests/js/fp_material_mixed.test.js:31:  assert.match(label, /mixed/i);
tests/js/fp_material_mixed.test.js:33:  assert.notStrictEqual(label, 'mixed');
tests/js/fp_material_mixed.test.js:36:test('FP_STRINGS.materials.mixed hint is advisory, never claims correction', () => {
tests/js/fp_material_mixed.test.js:37:  const hint = FP_STRINGS.materials.mixed.hint;
tests/js/fp_material_mixed.test.js:56:test('FP_STRINGS.materials.mixed hint names C 1s specifically and does not '
tests/js/fp_material_mixed.test.js:62:  const hint = FP_STRINGS.materials.mixed.hint;
tests/autofit/test_broad_justification.py:10:``autofit/engine.py``'s ``_unphysical_width_flags`` used to infer (2) from
tests/autofit/test_broad_justification.py:11:(1) via a bare numeric test (``declared_hi > FWHM_MAX_ORDINARY_EV``). The
tests/autofit/test_broad_justification.py:18:mixed_material_class_verdict_run{A,B}.md).
tests/autofit/test_broad_justification.py:20:The fix: ``ComponentSlot.broad_justification`` makes meaning (2) an
tests/autofit/test_broad_justification.py:21:explicit, independent field. ``_unphysical_width_flags`` keys its
tests/autofit/test_broad_justification.py:22:exemption off ``broad_justification is not None``, never off the bound's
tests/autofit/test_broad_justification.py:33:from autofit.engine import FittedComponent, _unphysical_width_flags
tests/autofit/test_broad_justification.py:37:# (declared_hi > FWHM_MAX_ORDINARY_EV == 2.0 eV, the pre-refactor rule),
tests/autofit/test_broad_justification.py:42:_CONDUCTOR_C1S = Phase(id="s", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_broad_justification.py:44:_INSULATOR_B1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:46:_INSULATOR_CL2P = Phase(id="s", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:48:_INSULATOR_N1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:50:_INSULATOR_U4F = Phase(id="s", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:98:# by manually re-listing every field -- broad_justification wasn't in that
tests/autofit/test_broad_justification.py:104:_U4F_PHASE = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:106:_N1S_PHASE = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:130:def test_composed_candidate_preserves_broad_justification(
tests/autofit/test_broad_justification.py:137:        assert slot.broad_justification is not None, (
tests/autofit/test_broad_justification.py:138:            f"{candidate_name}/{role} lost its broad_justification during "
tests/autofit/test_broad_justification.py:142:        assert slot.broad_justification is None
tests/autofit/test_broad_justification.py:174:        "broad_justification": "sentinel justification text",
tests/autofit/test_broad_justification.py:200:def test_exemption_fixture_matches_broad_justification(
tests/autofit/test_broad_justification.py:202:    """Each currently-exempt slot must carry a real broad_justification;
tests/autofit/test_broad_justification.py:208:        assert slot.broad_justification is not None, (
tests/autofit/test_broad_justification.py:219:        assert slot.broad_justification is None, (
tests/autofit/test_broad_justification.py:233:    """Minimal stand-in for CandidateModel -- _unphysical_width_flags only
tests/autofit/test_broad_justification.py:243:    """The actual OUTPUT of _unphysical_width_flags for a component fitted
tests/autofit/test_broad_justification.py:253:    flags = _unphysical_width_flags([comp], cand)
tests/autofit/test_broad_justification.py:270:    been auto-exempt under the old numeric rule) but broad_justification
tests/autofit/test_broad_justification.py:279:        fwhm_range=(0.8, 15.0), broad_justification=None,
tests/autofit/test_broad_justification.py:284:    flags = _unphysical_width_flags([comp], model)
tests/autofit/test_broad_justification.py:286:        "a slot with a wide bound but NO broad_justification must still "
tests/autofit/test_broad_justification.py:293:    """Mirror case: an explicit broad_justification grants exemption even
tests/autofit/test_broad_justification.py:302:        fwhm_range=(0.5, 2.0), broad_justification="synthetic test justification",
tests/autofit/test_broad_justification.py:307:    flags = _unphysical_width_flags([comp], model)
tests/autofit/test_broad_justification.py:309:        "an explicit broad_justification must exempt a slot even when its "
tests/autofit/test_broad_justification.py:314:def test_component_slot_broad_justification_defaults_to_none():
tests/autofit/test_broad_justification.py:320:    assert s.broad_justification is None
tests/autofit/test_resolver.py:18:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_resolver.py:20:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_resolver.py:22:BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_resolver.py:36:    # families present: DS+G asymmetric, expert-parity asym-GL, mixed, symmetric
tests/autofit/test_resolver.py:84:        xe = Phase(id="x", material_class=MaterialClass.CONDUCTOR, regions=("Xe 3d",))
tests/autofit/test_resolver.py:131:    both = Phase(id="mix", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_resolver.py:158:    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
tests/autofit/test_resolver.py:159:    p2 = Phase(id="ph2", material_class=MaterialClass.SEMICONDUCTOR, regions=("Fk 2p",))
tests/autofit/test_resolver.py:183:    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
tests/autofit/test_candidate_pool_real_gate.py:86:    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
tests/autofit/test_candidate_pool_real_gate.py:226:    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
tests/autofit/test_preseed_dominants.py:154:        assert p["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6, \
tests/autofit/test_preseed_dominants.py:160:def test_unphysical_width_flags_helper():
tests/autofit/test_preseed_dominants.py:163:    ``broad_justification``, e.g. a satellite) are NOT.
tests/autofit/test_preseed_dominants.py:165:    2026-07-20 (Unit A, broad_justification refactor): the exemption used
tests/autofit/test_preseed_dominants.py:172:    Updated to set broad_justification explicitly, matching how every real
tests/autofit/test_preseed_dominants.py:178:    def slot(role, lo, hi, broad_justification=None):
tests/autofit/test_preseed_dominants.py:182:                             broad_justification=broad_justification)
tests/autofit/test_preseed_dominants.py:191:             broad_justification="synthetic: pi->pi* shake-up, physically broad"),
tests/autofit/test_preseed_dominants.py:193:    flags = eng._unphysical_width_flags(
tests/autofit/test_preseed_dominants.py:203:    assert eng._unphysical_width_flags([comp("contamination_CO", 1.5)], m) == []
tests/autofit/test_preseed_dominants.py:206:def test_unphysical_width_flags_wide_range_alone_no_longer_exempts():
tests/autofit/test_preseed_dominants.py:208:    declared fwhm_range but NO broad_justification must be flagged when it
tests/autofit/test_preseed_dominants.py:222:    flags = eng._unphysical_width_flags([comp], m)
tests/autofit/test_preseed_dominants.py:236:    assert seeded.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
tests/autofit/test_preseed_dominants.py:243:    assert aug.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
tests/autofit/test_preseed_dominants.py:269:    assert p["fitted_fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6   # NOT 3 eV
tests/autofit/test_preseed_dominants.py:278:            assert pk["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6
tests/autofit/test_c1s_parity_gate.py:95:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/js/find_peaks_plain_message.test.js:117:  // Regression: a mixed curated+structural request (e.g. regions
tests/js/find_peaks_plain_message.test.js:121:  // test_api_mixed_deep_plus_structural_runs_and_flags) — a bare
tests/js/find_peaks_plain_message.test.js:139:  // it could be an ordinary no-survivors failure in a mixed request.
tests/autofit/test_c1s_mixed_material_class.py:49:def _resolve(material_class):
tests/autofit/test_c1s_mixed_material_class.py:50:    phase = Phase(id="sample", material_class=material_class, regions=("C 1s",))
tests/autofit/test_c1s_mixed_material_class.py:66:@pytest.mark.parametrize("material_class", NON_MIXED)
tests/autofit/test_c1s_mixed_material_class.py:67:def test_non_mixed_candidate_pool_unchanged(material_class):
tests/autofit/test_c1s_mixed_material_class.py:71:    g = _resolve(material_class)
tests/autofit/test_c1s_mixed_material_class.py:77:            f"material_class {material_class}"
tests/autofit/test_c1s_mixed_material_class.py:81:@pytest.mark.parametrize("material_class", NON_MIXED)
tests/autofit/test_c1s_mixed_material_class.py:82:def test_non_mixed_candidate_names_unchanged(material_class):
tests/autofit/test_c1s_mixed_material_class.py:85:    non-MIXED material class (it always was -- material_class was
tests/autofit/test_c1s_mixed_material_class.py:88:    names_other = {c.name for c in _resolve(material_class).candidates}
tests/autofit/test_c1s_mixed_material_class.py:92:def test_mixed_relaxes_contamination_fwhm_ceiling():
tests/autofit/test_c1s_mixed_material_class.py:110:def test_mixed_does_not_touch_position_windows_or_offsets():
tests/autofit/test_c1s_mixed_material_class.py:118:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:122:    assert windows(g_conductor) == windows(g_mixed), (
tests/autofit/test_c1s_mixed_material_class.py:128:    assert offsets(g_conductor) == offsets(g_mixed), (
tests/autofit/test_c1s_mixed_material_class.py:133:def test_mixed_does_not_touch_unrelated_fwhm_families():
tests/autofit/test_c1s_mixed_material_class.py:139:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:146:    assert other_family_ranges(g_conductor) == other_family_ranges(g_mixed)
tests/autofit/test_c1s_mixed_material_class.py:149:def test_mixed_provenance_relaxation_record_asserts_no_new_value():
tests/autofit/test_c1s_mixed_material_class.py:158:    rec = _by_constant(records, "mixed_material_class_width_relaxation")
tests/autofit/test_c1s_mixed_material_class.py:179:def test_mixed_provenance_numeric_guard_record_is_honestly_labeled():
tests/autofit/test_c1s_mixed_material_class.py:186:    rec = _by_constant(records, "mixed_fwhm_ceiling_numeric_guard")
tests/autofit/test_c1s_mixed_material_class.py:202:# in autofit.engine._unphysical_width_flags, so a MIXED contaminant fitting
tests/autofit/test_c1s_mixed_material_class.py:205:# so the app must not vouch for it). Fixed by Unit A (broad_justification):
tests/autofit/test_c1s_mixed_material_class.py:209:def test_mixed_wide_contamination_is_flagged_unphysical():
tests/autofit/test_c1s_mixed_material_class.py:214:    from autofit.engine import FittedComponent, _unphysical_width_flags
tests/autofit/test_c1s_mixed_material_class.py:219:    assert slot.broad_justification is None, (
tests/autofit/test_c1s_mixed_material_class.py:225:    flags = _unphysical_width_flags([comp], cand)
tests/autofit/test_c1s_mixed_material_class.py:233:def test_mixed_shared_width_contamination_all_flagged_independently():
tests/autofit/test_c1s_mixed_material_class.py:245:    linked slots keeps its OWN fwhm_range/broad_justification, and
tests/autofit/test_c1s_mixed_material_class.py:246:    _unphysical_width_flags checks each FittedComponent independently --
tests/autofit/test_c1s_mixed_material_class.py:249:    from autofit.engine import FittedComponent, _unphysical_width_flags
tests/autofit/test_c1s_mixed_material_class.py:260:        assert slot.broad_justification is None, (
tests/autofit/test_c1s_mixed_material_class.py:273:    flags = _unphysical_width_flags(comps, cand)
tests/autofit/test_c1s_mixed_material_class.py:282:def test_mixed_wide_contamination_routes_to_conditional():
tests/autofit/test_c1s_mixed_material_class.py:288:    autofit.engine._unphysical_width_flags produces for the 8 eV scenario
tests/autofit/test_c1s_mixed_material_class.py:297:                                _unphysical_width_flags)
tests/autofit/test_c1s_mixed_material_class.py:317:    injected_flags = _unphysical_width_flags([fake_comp], report.model)
tests/autofit/test_multivariate_mcr.py:163:def test_build_matrix_interpolates_mixed_grids():
tests/autofit/test_fit_physics_wiring.py:15:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_fit_physics_wiring.py:17:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_bayesian_real_gate.py:37:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_bayesian_u4f_unresolved_gate.py:37:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,

exec
/bin/zsh -lc 'git status --short --branch' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fTzHdHY8' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mJ5twOzs' (errno=Operation not permitted)
## feature-autofit-stage2...origin/feature-autofit-stage2
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json

exec
/bin/zsh -lc 'git show --stat --oneline --decorate --no-renames bdc909a && git show --name-only --format=fuller --no-renames bdc909a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ccTbEiRF' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iUZi9ZEf' (errno=Operation not permitted)
bdc909a fix(mixed): rebase MIXED's own 2 accepted Codex findings onto the corrected engine
 templates/index.html                           |  13 ++-
 tests/autofit/test_c1s_mixed_material_class.py | 147 +++++++++++++++++++++++++
 tests/js/fp_material_mixed.test.js             |  11 ++
 3 files changed, 165 insertions(+), 6 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ziDXFVNy' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-uvbN9eDJ' (errno=Operation not permitted)
commit bdc909a271f64bf59097a8cc734a71e5728cd436
Author:     Skye Fortier <skyefortier@gmail.com>
AuthorDate: Mon Jul 20 13:21:20 2026 -0600
Commit:     Skye Fortier <skyefortier@gmail.com>
CommitDate: Mon Jul 20 13:21:20 2026 -0600

    fix(mixed): rebase MIXED's own 2 accepted Codex findings onto the corrected engine
    
    MIXED (77bf3a8) shipped with two open findings from its own Codex review,
    now fixed here, rebased onto the corrected broad_justification refactor
    (5070662 + ad7e668):
    
    1. Run B's MAJOR: the frontend copy ("Peak width limits are relaxed
       accordingly") read as global -- a chemist selecting MIXED for U 4f,
       Cl 2p, B 1s, or N 1s would wrongly believe peak widths changed there
       too, when only C 1s contamination/adventitious widths actually relax.
       FP_STRINGS.materials.mixed.hint now names C 1s contamination
       specifically and states other regions are unaffected.
    
    2. Both runs' MINOR: the provenance relaxation-record test only asserted
       `value` was a string, so a lab-derived number smuggled into prose
       (e.g. "relax to 3.5 eV based on our spectra") would still have passed
       -- exactly the provenance-audit trap this whole feature exists to
       avoid, missed by its own guard test. Now asserts the string contains
       no digit at all.
    
    The finding itself -- a MIXED contamination slot fitting at ~6-10 eV must
    now be flagged unphysical and route to CONDITIONAL, the actual gap both
    Codex reviews of the broad_justification refactor (5070662) and its
    _retag_slot fix (ad7e668) exist to close -- is encoded directly as
    test_mixed_wide_contamination_is_flagged_unphysical and
    test_mixed_wide_contamination_routes_to_conditional. Explicitly red-green
    verified rather than trusted: temporarily reverted autofit/engine.py's
    _unphysical_width_flags to the pre-Unit-A numeric rule
    (declared_hi > FWHM_MAX_ORDINARY_EV) and confirmed both tests fail there
    (not a laundered pin -- the same failure mode caught once already in this
    session's Tougaard background work), then confirmed green on restore.
    
    Also formalizes an empirical finding requested directly: 77bf3a8's own
    commit message flagged the "_linked" candidate families' shared
    contamination width as a KNOWN RISK (all 3 contaminant slots share ONE
    lmfit parameter, so a single fat shared value could in principle absorb
    signal across the whole ~280-292 eV contaminant span -- the same
    overlap-degeneracy class c1s.py's own MG-family comments document for a
    free position, reachable here through width instead). Verified directly
    (not left as a theoretical concern) that this is already closed: sharing
    one lmfit parameter does not create one shared exemption --
    _unphysical_width_flags checks each FittedComponent independently
    against its OWN slot's individually-unvouched broad_justification, so a
    wide shared value flags every slot built on it, not just some. Pinned as
    test_mixed_shared_width_contamination_all_flagged_independently.
    
    Re-confirmed test_material_class_does_not_affect_charge_correction still
    passes unchanged (charge correction remains provably untouched by any of
    this).
    
    Full suite: 748 passed, 6 skipped, 0 failed.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

templates/index.html
tests/autofit/test_c1s_mixed_material_class.py
tests/js/fp_material_mixed.test.js

codex
The commit scope matches the claimed three files from `git show --name-only`. I’m now reading the exact tests and implementation paths so the review can distinguish a real red-green pin from a fixture that happens to pass.
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '730,875p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba autofit/regions/c1s.py | sed -n '80,460p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   730	        hits.append(f"{role or '?'}:{short}@{'min' if at_min else 'max'}")
   731	    return hits
   732	
   733	
   734	def _proposed_slot_pegs(outcome: FitOutcome, role: str) -> list[str]:
   735	    """Boundary pegs for one proposed slot, using the SAME detector (and the
   736	    same ``_BOUNDARY_EXCLUDED`` shape-endpoint policy) as every grammar slot.
   737	
   738	    Shape endpoints (a pure-Gaussian ``gl_ratio``=0, a pure-Lorentzian
   739	    ``gl_ratio``=1) are LEGITIMATE physics, not constraint violations — the
   740	    grammar excludes them from boundary hits, and treating a proposal that
   741	    reaches one as spurious would drop real pure-Gaussian/Lorentzian peaks
   742	    (measured: the two-narrow-peak F2 case regressed to zero accepted
   743	    proposals when shape pegs were rejected).  So the caller tolerates
   744	    ``{role}:fwhm@max`` (the physical-width ceiling doing its job) and any
   745	    shape endpoint, and rejects on a SUBSTANTIVE peg — ``center`` at a window
   746	    edge, ``amplitude`` at a wall, or ``fwhm@min`` (an implausibly narrow
   747	    spike) (Codex fwhm-cap review, run A: the accurate statement of "which
   748	    pegs reject").
   749	    """
   750	    return [h for h in outcome.boundary_hits if h.startswith(f"{role}:")]
   751	
   752	
   753	def _unphysical_width_flags(
   754	    components: "list[FittedComponent]", model: CandidateModel
   755	) -> list[str]:
   756	    """Fitted components whose width reaches the ordinary physical FWHM
   757	    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.
   758	
   759	    A slot is grammar-sanctioned-broad — EXEMPT, because its width is region
   760	    physics cited in the region module, not an unphysical stretch — if and
   761	    only if it carries an explicit ``ComponentSlot.broad_justification``
   762	    (C 1s π→π* satellite, U 4f mains, B 1s, …; see each region module for its
   763	    citation or honest UNVERIFIED-empirical disclosure). Any other slot —
   764	    contamination, the aliphatic main, and the region-``unassigned`` F1
   765	    pre-seed / F2-F3 proposal slots — that fits at/above the ordinary
   766	    ceiling is flagged: the optimizer wanted a wider (fatter) peak than an
   767	    ordinary component physically has, the cap held it at the limit, and the
   768	    decomposition must be reported low-confidence (routes to the CONDITIONAL
   769	    tier via rank_and_filter) rather than silently accepted.
   770	
   771	    ``broad_justification`` is INDEPENDENT of ``fwhm_range``'s own magnitude
   772	    (2026-07-20 refactor, Codex-caught in the MIXED material-class review):
   773	    the exemption used to be inferred from ``declared_hi >
   774	    FWHM_MAX_ORDINARY_EV`` alone, which conflated "the optimizer may search
   775	    this wide" with "this region module vouches the width is real physics".
   776	    Widening a bound for an unrelated reason (numerical-stability headroom,
   777	    a wider calibration envelope, MIXED material class's relaxed
   778	    contamination ceiling) used to silently grant the vouching exemption as
   779	    a side effect. Region-agnostic: the exemption is driven entirely by
   780	    each slot's own declared field, so no region's cited widths are ever
   781	    mis-flagged, and no bound can ever again disable this safety net merely
   782	    by being wide.
   783	    """
   784	    slots_by_role = {s.role: s for s in model.slots}
   785	    flags: list[str] = []
   786	    for c in components:
   787	        slot = slots_by_role.get(c.slot_role)
   788	        if slot is None:
   789	            continue
   790	        declared_lo, declared_hi = slot.fwhm_range
   791	        vouched = slot.broad_justification is not None
   792	        # EFFECTIVE width (Stage-2 PHYSICAL bar): DS+G's width lives in TWO
   793	        # params — beta (Lorentzian HWHM, eV) and m_gauss (Gaussian FWHM;
   794	        # what comp.fwhm carries) — so the checks below must see the
   795	        # convolved width, not the Gaussian part alone (a component could
   796	        # otherwise be ~3+ eV wide while every width check reads 1.0:
   797	        # exactly the 'neighbor broadened to hide a missed peak' channel).
   798	        # Olivero & Longbothum 1977 Voigt-FWHM approximation (0.02%).
   799	        eff_fwhm = c.fwhm
   800	        if c.line_shape is LineShape.DS_G:
   801	            f_l = 2.0 * float(c.shape_params.get("beta", 0.0))
   802	            eff_fwhm = 0.5346 * f_l + np.sqrt(0.2166 * f_l ** 2 + c.fwhm ** 2)
   803	            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
   804	                flags.append(
   805	                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
   806	                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
   807	                    f"β={c.shape_params.get('beta', 0.0):.2f} + "
   808	                    f"m={c.fwhm:.2f}; no known-broad justification)")
   809	                continue
   810	        elif c.line_shape is LineShape.ASYM_GL:
   811	            # asym-GL broadens its high-BE side to fwhm×(1+asymmetry)
   812	            # (fitting.py convention) — the MEAN effective width
   813	            # fwhm×(1+asym/2) closes the remaining papering-over channel
   814	            # (Codex Stage-2 review, run A MAJOR).
   815	            asym = float(c.shape_params.get("asymmetry", 0.0))
   816	            eff_fwhm = c.fwhm * (1.0 + 0.5 * asym)
   817	            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
   818	                flags.append(
   819	                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
   820	                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
   821	                    f"fwhm={c.fwhm:.2f}×(1+{asym:.2f}/2); no known-broad "
   822	                    "justification)")
   823	                continue
   824	        # detection-family slots (scale-relative ceilings, usually > the
   825	        # ordinary cap): a component at ≥ DETECTION_WIDTH_ABSORB_FRACTION
   826	        # of its own ceiling (= 1.75× the DETECTED width via the 2.5×
   827	        # ceiling) is absorbing neighboring intensity — the papering-over
   828	        # signature in transferable units. Unaffected by broad_justification
   829	        # (these are engine-constructed proposal/pre-seed slots, not
   830	        # region-module-authored grammar; their ceiling is scale-relative,
   831	        # not a physics vouch).
   832	        if c.slot_role.startswith("detected_peak_"):
   833	            if eff_fwhm >= DETECTION_WIDTH_ABSORB_FRACTION * declared_hi:
   834	                flags.append(
   835	                    f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥"
   836	                    f"{DETECTION_WIDTH_ABSORB_FRACTION:.2f}×ceiling "
   837	                    f"({declared_hi:.2f}eV) — ~1.75× its detected width; "
   838	                    "likely absorbing a neighbor")
   839	            continue
   840	        if vouched:
   841	            continue                       # grammar-sanctioned-broad slot
   842	        # pegging the ordinary ceiling — same 1%-of-range tol as boundary
   843	        # detection, so a component held AT the 2.0 cap is caught
   844	        tol = 0.01 * (declared_hi - declared_lo) if declared_hi > declared_lo else 0.0
   845	        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
   846	            flags.append(
   847	                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
   848	                "ordinary cap (no known-broad justification)")
   849	    return flags
   850	
   851	
   852	def fit_candidate(
   853	    x: np.ndarray,
   854	    y: np.ndarray,
   855	    weights: np.ndarray,
   856	    model: CandidateModel,
   857	    initial_params: Optional[Parameters] = None,
   858	    max_nfev: int = FIT_CANDIDATE_MAX_NFEV,
   859	    fit_full_window: bool = False,
   860	) -> FitOutcome:
   861	    """One fit of ``model`` to (x, y, weights); background subtracted first.
   862	
   863	    ``max_nfev`` bounds leastsq's own effort per call. lmfit's default
   864	    (200000*(nvars+1), see lmfit.Minimizer) is effectively unbounded: a
   865	    candidate whose params wander to a valid-but-degenerate corner (e.g.
   866	    DS+G's alpha/beta pinned at their bounds — a shape preference, not a
   867	    param error; see _BOUNDARY_EXCLUDED) produces a landscape leastsq can't
   868	    descend, and it spins for tens of thousands of evaluations without
   869	    terminating. Diagnostic run (2026-07-05, Suggest-peaks hang
   870	    investigation) showed a clean bimodal split: converged fits topped out
   871	    at nfev=14890; non-convergent ones started at nfev=21604. This cap sits
   872	    between the two so lmfit's own AbortFitException (caught internally by
   873	    leastsq(), surfacing as result.success=False) cuts off the latter
   874	    deterministically, without clipping legitimate slow-but-converging fits.
   875	    """

 succeeded in 0ms:
    80	# adjudicated cap, exact width parity with the broadest expert components
    81	# is not expressible by construction — the cap is the ruling.
    82	FWHM_RANGE_CONTAMINATION = (0.8, 2.0)
    83	
    84	# MIXED material class (2026-07-20): FWHM_RANGE_CONTAMINATION's ceiling is
    85	# justified by a single, well-referenced HOMOGENEOUS surface. That
    86	# condition is not met for an analyte embedded in a different matrix —
    87	# analyte and matrix can charge differently under X-ray illumination
    88	# (differential charging), and a non-uniform spatial distribution of
    89	# charging potentials broadens the observed peak (inhomogeneous
    90	# broadening; see provenance() for the citations). Withdrawing that
    91	# homogeneity assumption needs no citation — it is the removal of a
    92	# claim, not a new one — so this widens the ceiling toward
    93	# "unconstrained" rather than asserting a second, chemistry-flavored
    94	# magic number (the provenance-audit trap this unit exists to avoid: a
    95	# cap derived from THIS LAB'S OWN mixed-phase spectra would be exactly
    96	# the self-reference the audit removed, wearing a feature label instead
    97	# of a tier badge). The floor is untouched: differential charging only
    98	# broadens a peak, it never narrows one.
    99	#
   100	# A fully unconstrained (infinite) ceiling is not viable with the current
   101	# engine: autofit/engine.py seeds the initial FWHM guess at the MIDPOINT
   102	# of fwhm_range, so an infinite upper bound would seed an infinite
   103	# initial value and break the optimizer outright. Some finite ceiling is
   104	# therefore unavoidable for numerical stability — so this reuses
   105	# fitting.py's OWN existing fwhm_max default (15.0 eV), the ceiling the
   106	# manual /api/fit path already applies to literally every peak, everywhere
   107	# in this app, rather than inventing a new number. Purely a numeric guard
   108	# for optimizer stability, not a chemistry or physics claim (same footing
   109	# as DSG_ALPHA_RANGE_GRAPHITIC's "fitalg numeric guard" below) — if a
   110	# fitted component pegs this ceiling under MIXED, that is the numerical
   111	# guard doing its job, not a measurement.
   112	#
   113	# KNOWN RISK (flag for review, do not silently paper over): the "_linked"
   114	# candidate families share ONE width parameter across all 3 contaminant
   115	# slots (see shared_decl below) — under MIXED that shared width relaxes
   116	# to this same wide ceiling, so a single fat shared-width component could
   117	# in principle absorb signal across the whole ~280-292 eV C 1s contaminant
   118	# span. c1s.py's own MG-family comments already document an analogous
   119	# overlap-degeneracy failure mode (see aliphatic_main_offset below); this
   120	# is the same class of risk, now reachable through a wider ceiling instead
   121	# of a free position. Should be adversarially fit-tested, not just read.
   122	FWHM_MIXED_CEILING_NUMERIC_GUARD_EV = 15.0
   123	
   124	
   125	def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
   126	    """FWHM_RANGE_CONTAMINATION, widened under MIXED. See the constant
   127	    comment above — this relaxes a constraint, it never asserts a new one."""
   128	    if material_class is MaterialClass.MIXED:
   129	        return (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
   130	    return FWHM_RANGE_CONTAMINATION
   131	
   132	
   133	# DS+G Lorentzian HWHM fixed at the C 1s core-hole lifetime:
   134	# Campbell & Papp, At. Data Nucl. Data Tables 77 (2001) 1–56
   135	# (DOI 10.1006/adnd.2000.0848): Γ_K(C) ≈ 0.10 eV FWHM → 0.05 eV HWHM.
   136	# VERIFIED (spec §9). Breaks the α/β/m_gauss broadening degeneracy.
   137	DSG_LORENTZIAN_HWHM_C1S = 0.05
   138	
   139	# Graphitic asymmetry-index cap ≤ 0.3 — UNVERIFIED numeric guard (fitalg;
   140	# keeps the optimizer away from the α→0.5 singularity).
   141	DSG_ALPHA_RANGE_GRAPHITIC = (0.0, 0.3)
   142	
   143	# asym-GL graphitic parameter windows — UNVERIFIED-empirical: chosen to
   144	# bracket the expert reference fits (asymmetry ≈ 0.10, glMix ≈ 0.08–0.5)
   145	# rather than derived from literature. The AG family exists so the engine
   146	# can express the analysts' asym-GL practice; treat its constants as
   147	# calibration targets, not physics.
   148	ASYMGL_ASYMMETRY_RANGE = (0.0, 0.5)
   149	
   150	# Adventitious-carbon chemical shifts from the C-C/C-H reference — soft
   151	# priors/windows per Biesinger (2022): C-O +1.5±0.3, C=O +3.0±0.3,
   152	# O-C=O +4.0±0.4 (CONDITIONAL per spec §9 — convention, not universal).
   153	CONTAM_OFFSETS = {"CO": (1.5, 0.3), "C=O": (3.0, 0.3), "OC=O": (4.0, 0.4)}
   154	
   155	# π→π* satellite offset window from the graphitic main (fitalg; UNVERIFIED
   156	# tunable).
   157	SATELLITE_OFFSET_RANGE = (5.5, 7.0)
   158	
   159	_MAIN_FWHM_BY_MATERIAL = {
   160	    "graphite": FWHM_RANGE_GRAPHITIC,
   161	    None: FWHM_RANGE_GRAPHITIC,          # default material for a conductor
   162	    "polymer": FWHM_RANGE_AROMATIC_POLYMER,
   163	}
   164	
   165	_SHARED_CONTAM_FWHM = "shared_contamination_fwhm"
   166	
   167	
   168	class C1sModule:
   169	    region = REGION
   170	
   171	    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
   172	        return dict(C1S_WINDOWS)
   173	
   174	    def provenance(self) -> list[dict]:
   175	        return [
   176	            {"constant": "graphite_reference_ev", "value": 284.4,
   177	             "status": "VERIFIED",
   178	             "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS "
   179	                       "10.1116/1.1247695 (window anchor)"},
   180	            {"constant": "adventitious_reference_ev", "value": 284.8,
   181	             "status": "CONDITIONAL",
   182	             "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; "
   183	                       "Greczynski 10.1002/anie.201916000 — convention"},
   184	            {"constant": "dsg_core_hole_beta_ev", "value": DSG_LORENTZIAN_HWHM_C1S,
   185	             "status": "VERIFIED",
   186	             "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 "
   187	                       "(Γ_K(C) ≈ 0.10 eV FWHM → 0.05 HWHM)"},
   188	            {"constant": "contamination_offsets_ev",
   189	             "value": {k: list(v) for k, v in CONTAM_OFFSETS.items()},
   190	             "status": "CONDITIONAL",
   191	             "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"},
   192	            {"constant": "window_widths", "value": {k: list(v) for k, v in C1S_WINDOWS.items()},
   193	             "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"},
   194	            {"constant": "fwhm_graphitic_ev", "value": list(FWHM_RANGE_GRAPHITIC),
   195	             "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"},
   196	            {"constant": "fwhm_contamination_floor_ev",
   197	             "value": FWHM_RANGE_CONTAMINATION[0],
   198	             "status": "CONDITIONAL",
   199	             "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; "
   200	                       "Greczynski & Hultman (2020) — published lower "
   201	                       "bound for adventitious/aliphatic carbon FWHM"},
   202	            {"constant": "fwhm_contamination_ceiling_ev",
   203	             "value": FWHM_RANGE_CONTAMINATION[1],
   204	             "status": "UNVERIFIED",
   205	             "source": "lab-adjudicated cap, not a literature value — "
   206	                       "expert adjudication 2026-07-03 "
   207	                       "(docs/autofit/adjudication-decisions.md #5); a "
   208	                       "literature-reasonable upper bound but a cap, not "
   209	                       "a target; replaces the prior split 1.6/3.5 caps"},
   210	            {"constant": "fwhm_satellite_ev", "value": list(FWHM_RANGE_SATELLITE),
   211	             "status": "UNVERIFIED",
   212	             "source": "labeled-set calibration (44 fits, 1.9–5.0 eV)"},
   213	            {"constant": "dsg_alpha_cap", "value": list(DSG_ALPHA_RANGE_GRAPHITIC),
   214	             "status": "UNVERIFIED", "source": "fitalg numeric guard"},
   215	            {"constant": "asymgl_family", "value": "empirical asymmetric envelope",
   216	             "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"},
   217	            {"constant": "asymgl_asymmetry_range", "value": list(ASYMGL_ASYMMETRY_RANGE),
   218	             "status": "UNVERIFIED",
   219	             "source": "UNVERIFIED-empirical: chosen to bracket the expert "
   220	                       "reference fits (asymmetry ≈ 0.10, glMix ≈ "
   221	                       "0.08–0.5) rather than derived from literature; "
   222	                       "treat as a calibration target, not physics"},
   223	            {"constant": "satellite_offset_range_ev", "value": list(SATELLITE_OFFSET_RANGE),
   224	             "status": "UNVERIFIED",
   225	             "source": "fitalg tunable — the π→π* satellite "
   226	                       "offset window from the graphitic main"},
   227	            {"constant": "aromatic_polymer_fwhm_ev",
   228	             "value": list(FWHM_RANGE_AROMATIC_POLYMER),
   229	             "status": "CONDITIONAL",
   230	             "source": "Beamson & Briggs, High Resolution XPS of Organic "
   231	                       "Polymers — The Scienta ESCA300 Database, Wiley "
   232	                       "(1992): aromatic C 1s 0.9–1.5 eV; widened to "
   233	                       "0.8–1.8 as the generous cross-instrument envelope "
   234	                       "(the widening beyond the cited range is editorial, "
   235	                       "not itself literature-derived)"},
   236	            {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6],
   237	             "status": "UNVERIFIED",
   238	             "source": "UNVERIFIED-empirical (labeled-set + convention): "
   239	                       "brackets both expert practice (+0.30: graphitic "
   240	                       "284.5 vs aliphatic 284.8) and Biesinger's "
   241	                       "adventitious C-C/C-H convention (284.8 vs "
   242	                       "graphite 284.4, +0.4)"},
   243	            {"constant": "mixed_material_class_width_relaxation",
   244	             "value": "under MaterialClass.MIXED (analyte embedded in a "
   245	                      "different matrix), the contamination/adventitious "
   246	                      "FWHM ceiling's single-species-homogeneity "
   247	                      "assumption is withdrawn and the ceiling is relaxed "
   248	                      "toward unconstrained; no new position or width "
   249	                      "value is asserted — position windows and every "
   250	                      "other FWHM family are unchanged",
   251	             "status": "CONDITIONAL",
   252	             "source": "differential charging between analyte and matrix "
   253	                       "causes inhomogeneous broadening (Baer, "
   254	                       "Artyushkova, Cohen, Easton, Engelhard, Gengenbach, "
   255	                       "Greczynski, Mack, Morgan, Roberts, \"XPS Guide: "
   256	                       "Charge neutralization and binding energy "
   257	                       "referencing for insulating samples,\" J. Vac. Sci. "
   258	                       "Technol. A 38, 031204 (2020), DOI "
   259	                       "10.1116/6.0000057 — differential charging "
   260	                       "broadens peaks, and a single charge correction is "
   261	                       "insufficient once it is present; internal "
   262	                       "referencing has \"limited accuracy ... often "
   263	                       "including multiphase and other complex samples\"; "
   264	                       "Greczynski & Hultman, \"X-ray photoelectron "
   265	                       "spectroscopy: Towards reliable binding energy "
   266	                       "referencing,\" Prog. Mater. Sci. 107 (2020) "
   267	                       "100591, DOI 10.1016/j.pmatsci.2019.100591)"},
   268	            {"constant": "mixed_fwhm_ceiling_numeric_guard",
   269	             "value": FWHM_MIXED_CEILING_NUMERIC_GUARD_EV,
   270	             "status": "UNVERIFIED",
   271	             "source": "a fully unconstrained (infinite) ceiling breaks "
   272	                       "the engine's initial-value seeding (the FWHM "
   273	                       "guess is the fwhm_range midpoint); this reuses "
   274	                       "fitting.py's own existing fwhm_max default, the "
   275	                       "ceiling the manual /api/fit path already applies "
   276	                       "to every peak in this app — a numeric guard for "
   277	                       "optimizer stability, not a chemistry or physics "
   278	                       "claim (same footing as dsg_alpha_cap above)"},
   279	        ]
   280	
   281	    def build_candidates(
   282	        self, phase: Phase, oxidation_state: Optional[str] = None
   283	    ) -> list[CandidateModel]:
   284	        """
   285	        Model families (admissibility encoded structurally, fitalg §):
   286	
   287	        - A0–A3:  DS+G asymmetric graphitic main + π→π* satellite
   288	                  + 0–3 contaminants (absolute windows)
   289	        - A1–A3_linked:         shared contamination FWHM (Biesinger 2022)
   290	        - A1–A3_linked_offset:  + contaminant centers as bounded offsets
   291	        - AG0–AG3_linked:       asym-GL graphitic main variants (expert-fit
   292	                                parity family; UNVERIFIED-empirical shape)
   293	        - M0–M3:  mixed graphitic (DS+G) + aliphatic (PV) two-main models
   294	        - B2/B3 (+_linked):     symmetric adventitious-carbon models
   295	        - shake-up satellite only with an asymmetric main (admissibility)
   296	
   297	        ``oxidation_state`` is accepted for the Layer-C seam; C 1s defines
   298	        no oxidation-state overrides.
   299	        """
   300	        if oxidation_state is not None:
   301	            raise KeyError(
   302	                f"C 1s defines no oxidation-state override {oxidation_state!r}"
   303	            )
   304	        pid = phase.id
   305	        main_fwhm = _MAIN_FWHM_BY_MATERIAL.get(phase.material, FWHM_RANGE_GRAPHITIC)
   306	        contam_fwhm = _contamination_fwhm_range(phase.material_class)
   307	
   308	        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
   309	            return ComponentSlot(
   310	                role=role, region=REGION, phase_id=pid,
   311	                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
   312	            )
   313	
   314	        def graphitic_main_dsg() -> ComponentSlot:
   315	            return slot(
   316	                "main_graphitic", C1S_WINDOWS["graphitic"], LineShape.DS_G,
   317	                main_fwhm,
   318	                fixed_params=(("beta", DSG_LORENTZIAN_HWHM_C1S),),
   319	                param_ranges=(("alpha", DSG_ALPHA_RANGE_GRAPHITIC),),
   320	            )
   321	
   322	        def graphitic_main_asymgl() -> ComponentSlot:
   323	            return slot(
   324	                "main_graphitic", C1S_WINDOWS["graphitic"], LineShape.ASYM_GL,
   325	                main_fwhm,
   326	                param_ranges=(("asymmetry", ASYMGL_ASYMMETRY_RANGE),),
   327	            )
   328	
   329	        def aliphatic_main() -> ComponentSlot:
   330	            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
   331	                        LineShape.PSEUDO_VOIGT, contam_fwhm)
   332	
   333	        shake_up = slot(
   334	            "satellite_pi", C1S_WINDOWS["shake_up_pi"], LineShape.PSEUDO_VOIGT,
   335	            FWHM_RANGE_SATELLITE,
   336	            linked_to="main_graphitic", linked_offset_range=SATELLITE_OFFSET_RANGE,
   337	            broad_justification=(
   338	                "pi->pi* shake-up satellite: physically broad due to "
   339	                "multi-electron excitation (a genuine broadening "
   340	                "mechanism, not merely calibration); the specific range "
   341	                "is further calibrated to the labeled expert set (44 "
   342	                "fits, 1.9-5.0 eV, CALIBRATED 2026-07-03)"
   343	            ),
   344	        )
   345	
   346	        def contam(key, linked_fwhm=None, offset=None,
   347	                   fwhm_range=None) -> ComponentSlot:
   348	            kw = {}
   349	            if linked_fwhm:
   350	                kw["fwhm_linked_to"] = linked_fwhm
   351	            if offset:
   352	                mid, hw = offset
   353	                kw["linked_to"] = "main_graphitic"
   354	                kw["linked_offset_range"] = (mid - hw, mid + hw)
   355	            return slot(f"contamination_{key}", C1S_WINDOWS[key],
   356	                        LineShape.PSEUDO_VOIGT,
   357	                        fwhm_range if fwhm_range is not None else contam_fwhm, **kw)
   358	
   359	        shared_decl = ((_SHARED_CONTAM_FWHM, contam_fwhm[0], contam_fwhm[1]),)
   360	        keys = ["CO", "C=O", "OC=O"]
   361	
   362	        candidates: list[CandidateModel] = []
   363	
   364	        def add(name, slots, shared=()):
   365	            candidates.append(CandidateModel(
   366	                name=name, background=BackgroundType.SHIRLEY,
   367	                slots=tuple(slots), shared_fwhm_params=tuple(shared),
   368	            ))
   369	
   370	        # --- A family: DS+G asymmetric main + satellite + contaminants ---
   371	        base_a = [graphitic_main_dsg(), shake_up]
   372	        plain = [contam(k) for k in keys]
   373	        add("A0_graphite_asym_satellite", base_a)
   374	        for n in (1, 2, 3):
   375	            add(f"A{n}_graphite_asym_sat_plus_{'_'.join(keys[:n])}",
   376	                base_a + plain[:n])
   377	
   378	        # --- A_linked: shared contamination width (Biesinger 2022) ---
   379	        linked = [contam(k, linked_fwhm=_SHARED_CONTAM_FWHM) for k in keys]
   380	        for n in (1, 2, 3):
   381	            add(f"A{n}_linked", base_a + linked[:n], shared_decl)
   382	
   383	        # --- A_linked_offset: + offset-parameterized contaminant centers ---
   384	        offset_linked = [
   385	            contam(k, linked_fwhm=_SHARED_CONTAM_FWHM, offset=CONTAM_OFFSETS[k])
   386	            for k in keys
   387	        ]
   388	        for n in (1, 2, 3):
   389	            add(f"A{n}_linked_offset", base_a + offset_linked[:n], shared_decl)
   390	
   391	        # --- AG family: asym-GL graphitic main (expert-fit parity family).
   392	        #     Contamination widths use the UNIFORM adjudicated cap — the
   393	        #     former split lab-practice (0.8, 3.5) convention was replaced
   394	        #     per adjudication #5; AG/MG now differ from A/M only in the
   395	        #     graphitic main lineshape. ---
   396	        base_ag = [graphitic_main_asymgl(), shake_up]
   397	        add("AG0_graphite_asymGL_satellite", base_ag)
   398	        for n in (1, 2, 3):
   399	            add(f"AG{n}_graphite_asymGL_sat_plus_{'_'.join(keys[:n])}",
   400	                base_ag + plain[:n])
   401	        for n in (1, 2, 3):
   402	            add(f"AG{n}_linked", base_ag + linked[:n], shared_decl)
   403	
   404	        # --- M family: mixed graphitic (DS+G) + aliphatic (PV) two mains ---
   405	        base_m = [graphitic_main_dsg(), aliphatic_main(), shake_up]
   406	        add("M0_graph_asym_aliph_sym_satellite", base_m)
   407	        for n in (1, 2, 3):
   408	            add(f"M{n}_graph_asym_aliph_sym_sat_{'_'.join(keys[:n])}",
   409	                base_m + plain[:n])
   410	
   411	        # --- MG family: the expert-practice STRUCTURE — asym-GL graphitic +
   412	        #     aliphatic + satellite + contaminants (uniform adjudicated
   413	        #     contamination cap).  The
   414	        #     reference C 1s fits are exactly MG2-shaped (graphitic asym-GL
   415	        #     284.5 + adventitious 284.8/285.9/287.6 + π→π* ~290.9).
   416	        #     The aliphatic center is OFFSET-LINKED to the graphitic main
   417	        #     (+0.2…+0.6 eV): with a free center the optimizer slides the
   418	        #     aliphatic into the graphitic flank and pegs the window floor
   419	        #     (overlap degeneracy, fitalg LIMITATIONS §9).  The offset window
   420	        #     brackets both the expert practice (+0.30: 284.8 vs 284.5) and
   421	        #     Biesinger's adventitious C-C/C-H at 284.8 vs graphite 284.4
   422	        #     (+0.4).  UNVERIFIED-empirical (labeled-set + convention). ---
   423	        def aliphatic_main_offset() -> ComponentSlot:
   424	            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
   425	                        LineShape.PSEUDO_VOIGT, contam_fwhm,
   426	                        linked_to="main_graphitic",
   427	                        linked_offset_range=(0.2, 0.6))
   428	
   429	        base_mg = [graphitic_main_asymgl(), aliphatic_main_offset(), shake_up]
   430	        add("MG0_graphAsymGL_aliph_satellite", base_mg)
   431	        for n in (1, 2, 3):
   432	            add(f"MG{n}_graphAsymGL_aliph_sat_{'_'.join(keys[:n])}",
   433	                base_mg + plain[:n])
   434	
   435	        # --- B family: symmetric adventitious-carbon models (no satellite —
   436	        #     admissibility: shake-up requires an asymmetric sp² main) ---
   437	        aliph = aliphatic_main()
   438	        aliph_fwhm_param = "s_main_aliphatic_fwhm"
   439	        blinked = [contam(k, linked_fwhm=aliph_fwhm_param) for k in keys]
   440	        add("B2_linked", [aliph] + blinked[:2])
   441	        add("B3_linked", [aliph] + blinked[:3])
   442	        # plain-window symmetric variants (low-priority but admissible)
   443	        graph_sym = slot("main_graphitic", C1S_WINDOWS["graphitic"],
   444	                         LineShape.PSEUDO_VOIGT, main_fwhm)
   445	        add("B2_graphite_sym_CO_C=O", [graph_sym] + plain[:2])
   446	        add("B3_graphite_sym_CO_C=O_OC=O", [graph_sym] + plain[:3])
   447	
   448	        return candidates
   449	
   450	
   451	register_region(C1sModule())

exec
/bin/zsh -lc "nl -ba tests/autofit/test_c1s_mixed_material_class.py | sed -n '1,380p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""MIXED material class (2026-07-20 unit): analyte-in-matrix samples can
     2	show DIFFERENTIAL CHARGING between phases -- the sample charges
     3	non-uniformly under X-ray illumination, so a distribution of local surface
     4	potentials broadens observed peaks (inhomogeneous broadening). That
     5	broadening voids the single-species-homogeneity assumption behind the C 1s
     6	adventitious/contamination FWHM ceiling, so MIXED relaxes it.
     7	
     8	The provenance-audit trap this unit must NOT fall into: asserting a new
     9	numeric position/width value derived from this lab's own spectra (e.g.
    10	"MIXED widens the cap to 3.5 eV because that's what our UCl4-in-graphite
    11	samples do") would reintroduce exactly the self-reference the provenance
    12	audit removed -- wearing a feature label instead of a tier badge.
    13	Withdrawing an assumption needs no citation; asserting a new numeric
    14	window does, and this feature has none. So MIXED only RELAXES an existing
    15	constraint (widens toward the engine's own pre-existing numeric-stability
    16	ceiling) -- it never asserts a new position or width VALUE.
    17	
    18	Citations for the physical rationale (see also C1sModule.provenance()):
    19	Baer, Artyushkova, Cohen, Easton, Engelhard, Gengenbach, Greczynski, Mack,
    20	Morgan, Roberts, "XPS Guide: Charge neutralization and binding energy
    21	referencing for insulating samples," J. Vac. Sci. Technol. A 38, 031204
    22	(2020), DOI 10.1116/6.0000057 -- differential charging broadens peaks
    23	(examining the leading edge across analysis points/time "identif[ies]
    24	peak broadening as a result of differential charging"), and a single
    25	charge correction is insufficient once differential charging is present:
    26	internal referencing has "limited accuracy... often including multiphase
    27	and other complex samples." Greczynski & Hultman, "X-ray photoelectron
    28	spectroscopy: Towards reliable binding energy referencing," Prog. Mater.
    29	Sci. 107 (2020) 100591, DOI 10.1016/j.pmatsci.2019.100591 (referencing
    30	reliability, general).
    31	"""
    32	from __future__ import annotations
    33	
    34	import pytest
    35	
    36	from autofit.grammar import MaterialClass, Phase, resolve
    37	from autofit.regions.c1s import C1sModule, FWHM_RANGE_CONTAMINATION
    38	
    39	NON_MIXED = [MaterialClass.CONDUCTOR, MaterialClass.SEMICONDUCTOR,
    40	             MaterialClass.INSULATOR]
    41	
    42	
    43	def _by_constant(records, name):
    44	    hits = [r for r in records if r["constant"] == name]
    45	    assert len(hits) == 1, f"expected exactly one {name!r} record, got {len(hits)}"
    46	    return hits[0]
    47	
    48	
    49	def _resolve(material_class):
    50	    phase = Phase(id="sample", material_class=material_class, regions=("C 1s",))
    51	    return resolve([phase], "C 1s")
    52	
    53	
    54	def _contamination_slots(grammar):
    55	    """Every slot governed by FWHM_RANGE_CONTAMINATION under the DEFAULT
    56	    (non-MIXED) convention -- identified by its FLOOR, which MIXED never
    57	    changes, so this selector is stable across material classes."""
    58	    out = []
    59	    for c in grammar.candidates:
    60	        for s in c.slots:
    61	            if s.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0]:
    62	                out.append((c.name, s))
    63	    return out
    64	
    65	
    66	@pytest.mark.parametrize("material_class", NON_MIXED)
    67	def test_non_mixed_candidate_pool_unchanged(material_class):
    68	    """Non-regression, structural pin: conductor/semiconductor/insulator
    69	    must build EXACTLY the pre-MIXED contamination fwhm_range -- byte
    70	    (tuple) identical, not just close."""
    71	    g = _resolve(material_class)
    72	    slots = _contamination_slots(g)
    73	    assert slots, "fixture assumption: at least one contamination-governed slot"
    74	    for name, slot in slots:
    75	        assert slot.fwhm_range == FWHM_RANGE_CONTAMINATION, (
    76	            f"{name}/{slot.role}: fwhm_range changed for non-MIXED "
    77	            f"material_class {material_class}"
    78	        )
    79	
    80	
    81	@pytest.mark.parametrize("material_class", NON_MIXED)
    82	def test_non_mixed_candidate_names_unchanged(material_class):
    83	    """Non-regression at the coarsest level: the SET of candidate model
    84	    names build_candidates() produces must be identical across every
    85	    non-MIXED material class (it always was -- material_class was
    86	    previously read nowhere in this module)."""
    87	    names_conductor = {c.name for c in _resolve(MaterialClass.CONDUCTOR).candidates}
    88	    names_other = {c.name for c in _resolve(material_class).candidates}
    89	    assert names_conductor == names_other
    90	
    91	
    92	def test_mixed_relaxes_contamination_fwhm_ceiling():
    93	    """The one concrete, falsifiable claim: MIXED must actually widen the
    94	    contamination FWHM ceiling in the generated candidates -- otherwise
    95	    the feature is decorative. The FLOOR must NOT move: differential
    96	    charging only broadens a peak, it never narrows one, so there is no
    97	    physical basis to touch 0.8 eV."""
    98	    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
    99	    assert slots, "fixture assumption: at least one contamination-governed slot"
   100	    for name, slot in slots:
   101	        assert slot.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0], (
   102	            f"{name}/{slot.role}: MIXED changed the FLOOR -- no physical "
   103	            "justification for narrowing under differential charging"
   104	        )
   105	        assert slot.fwhm_range[1] > FWHM_RANGE_CONTAMINATION[1], (
   106	            f"{name}/{slot.role}: MIXED did not widen the ceiling -- decorative"
   107	        )
   108	
   109	
   110	def test_mixed_does_not_touch_position_windows_or_offsets():
   111	    """The provenance-audit trap, enforced structurally: MIXED relaxes
   112	    WIDTH only. Every BE window and every linked-offset (contaminant
   113	    center position, expressed relative to the graphitic main) must be
   114	    byte-identical to the conductor default -- tempting as it is to widen
   115	    a position window to admit an uncited differential-charging shift,
   116	    doing so would convert a known-unknown into a silently-permitted fit."""
   117	    g_conductor = _resolve(MaterialClass.CONDUCTOR)
   118	    g_mixed = _resolve(MaterialClass.MIXED)
   119	
   120	    windows = lambda g: {(c.name, s.role): s.be_window
   121	                         for c in g.candidates for s in c.slots}
   122	    assert windows(g_conductor) == windows(g_mixed), (
   123	        "MIXED must not alter any component's BE window"
   124	    )
   125	
   126	    offsets = lambda g: {(c.name, s.role): s.linked_offset_range
   127	                         for c in g.candidates for s in c.slots}
   128	    assert offsets(g_conductor) == offsets(g_mixed), (
   129	        "MIXED must not alter any linked-offset (contaminant center) range"
   130	    )
   131	
   132	
   133	def test_mixed_does_not_touch_unrelated_fwhm_families():
   134	    """Scope discipline: only the contamination/adventitious FWHM family
   135	    relaxes. The graphitic main, aromatic-polymer main, and satellite FWHM
   136	    ranges are untouched -- this unit's own instructions name the
   137	    adventitious cap as the one clear, in-scope case."""
   138	    g_conductor = _resolve(MaterialClass.CONDUCTOR)
   139	    g_mixed = _resolve(MaterialClass.MIXED)
   140	
   141	    def other_family_ranges(g):
   142	        return {(c.name, s.role): s.fwhm_range
   143	                for c in g.candidates for s in c.slots
   144	                if s.fwhm_range[0] != FWHM_RANGE_CONTAMINATION[0]}
   145	
   146	    assert other_family_ranges(g_conductor) == other_family_ranges(g_mixed)
   147	
   148	
   149	def test_mixed_provenance_relaxation_record_asserts_no_new_value():
   150	    """provenance() must document the relaxation itself: CONDITIONAL,
   151	    citing the differential-charging literature, and its `value` must
   152	    read as an ACTION (relax/remove a constraint) -- never a specific new
   153	    BE or width number. This is the literal test of the provenance-audit
   154	    design constraint: withdrawing an assumption needs no citation,
   155	    asserting a new numeric window does, and this record must not smuggle
   156	    one in under CONDITIONAL cover."""
   157	    records = C1sModule().provenance()
   158	    rec = _by_constant(records, "mixed_material_class_width_relaxation")
   159	    assert rec["status"] == "CONDITIONAL"
   160	    assert isinstance(rec["value"], str), (
   161	        "the relaxation record's value must be a descriptive action, not "
   162	        "a bare number that could read as a newly-asserted window"
   163	    )
   164	    # Both Codex reviews of 77bf3a8 flagged this exact gap: "is a string"
   165	    # alone would pass `value = "relax to 3.5 eV based on our spectra"` --
   166	    # a lab-derived number smuggled in as prose. No digit may appear at all.
   167	    assert not any(ch.isdigit() for ch in rec["value"]), (
   168	        f"the relaxation record's value contains a digit -- it must "
   169	        f"describe an action only, never a specific number: {rec['value']!r}"
   170	    )
   171	    assert "10.1116/6.0000057" in rec["source"], "Baer et al. 2020 DOI"
   172	    assert "baer" in rec["source"].lower()
   173	    assert "10.1016/j.pmatsci.2019.100591" in rec["source"], \
   174	        "Greczynski & Hultman 2020 DOI"
   175	    assert "greczynski" in rec["source"].lower()
   176	    assert "hultman" in rec["source"].lower()
   177	
   178	
   179	def test_mixed_provenance_numeric_guard_record_is_honestly_labeled():
   180	    """The residual finite ceiling (unavoidable -- the optimizer needs a
   181	    finite initial-value midpoint) must be labeled UNVERIFIED and
   182	    described as a numeric guard for fit stability, not a chemistry or
   183	    physics claim -- the same footing as dsg_alpha_cap's 'fitalg numeric
   184	    guard' language."""
   185	    records = C1sModule().provenance()
   186	    rec = _by_constant(records, "mixed_fwhm_ceiling_numeric_guard")
   187	    assert rec["status"] == "UNVERIFIED"
   188	    assert "numeric guard" in rec["source"].lower()
   189	    assert ("not a chemistry" in rec["source"].lower()
   190	            or "not a physical" in rec["source"].lower()
   191	            or "not a physics" in rec["source"].lower())
   192	    # the guard's own value must equal whatever ceiling build_candidates()
   193	    # actually uses under MIXED -- no drift between the doc and the code
   194	    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
   195	    actual_ceiling = slots[0][1].fwhm_range[1]
   196	    assert rec["value"] == actual_ceiling
   197	
   198	
   199	# ── Unit A dependency: the finding itself, encoded (2026-07-20) ───────────
   200	# Both Codex reviews of 77bf3a8 independently caught the same MAJOR: the
   201	# 15.0 eV numeric guard made contamination slots "grammar-sanctioned-broad"
   202	# in autofit.engine._unphysical_width_flags, so a MIXED contaminant fitting
   203	# at 6-10 eV sailed through unflagged -- the exact opposite of MIXED's own
   204	# premise (we do NOT know how broad differential charging makes the peak,
   205	# so the app must not vouch for it). Fixed by Unit A (broad_justification):
   206	# MIXED contamination slots get a wide bound but NO justification, so they
   207	# are no longer exempt. These two tests are that finding, encoded directly.
   208	
   209	def test_mixed_wide_contamination_is_flagged_unphysical():
   210	    """A C 1s contamination component fit at 8 eV under MIXED (well within
   211	    the relaxed 0.8-15.0 eV bound, well above the ordinary 2.0 eV cap) must
   212	    be flagged unphysical -- the bound's width must never itself grant
   213	    exemption (that would be the finding recurring)."""
   214	    from autofit.engine import FittedComponent, _unphysical_width_flags
   215	
   216	    g = _resolve(MaterialClass.MIXED)
   217	    cand = next(c for c in g.candidates if c.name == "A1_linked")
   218	    slot = cand.slot_by_role("contamination_CO")
   219	    assert slot.broad_justification is None, (
   220	        "fixture assumption: MIXED contamination must NOT be vouched-broad"
   221	    )
   222	    comp = FittedComponent(slot_role="contamination_CO", position=286.0,
   223	                           fwhm=8.0, amplitude=1e4, shape_params={},
   224	                           line_shape=slot.line_shape)
   225	    flags = _unphysical_width_flags([comp], cand)
   226	    assert flags, (
   227	        "an 8 eV MIXED contaminant must be flagged unphysical -- the "
   228	        "relaxed bound must not silently exempt it"
   229	    )
   230	    assert any("contamination_CO" in f for f in flags)
   231	
   232	
   233	def test_mixed_shared_width_contamination_all_flagged_independently():
   234	    """The degeneracy risk 77bf3a8's own commit message flagged as KNOWN
   235	    RISK, not yet closed at the time: the "_linked" families share ONE
   236	    width parameter (_SHARED_CONTAM_FWHM) across all 3 contaminant slots,
   237	    so under MIXED that shared width also relaxes to the wide ceiling -- a
   238	    single fat shared-width component could in principle absorb signal
   239	    across the whole ~280-292 eV contaminant span (the same overlap-
   240	    degeneracy class c1s.py's own MG-family comments document for a free
   241	    position, now reachable through width instead).
   242	
   243	    Verified here rather than left as a theoretical concern: sharing one
   244	    lmfit parameter does not create one shared exemption. Each of the 3
   245	    linked slots keeps its OWN fwhm_range/broad_justification, and
   246	    _unphysical_width_flags checks each FittedComponent independently --
   247	    so a shared width ballooning wide flags EVERY slot built on it, not
   248	    just some, and none can hide behind another's exemption."""
   249	    from autofit.engine import FittedComponent, _unphysical_width_flags
   250	
   251	    g = _resolve(MaterialClass.MIXED)
   252	    cand = next(c for c in g.candidates if c.name == "A3_linked")
   253	    assert cand.shared_fwhm_params, (
   254	        "fixture assumption: A3_linked really does share one width "
   255	        "parameter across its contaminants"
   256	    )
   257	    contam_roles = ("contamination_CO", "contamination_C=O", "contamination_OC=O")
   258	    for role in contam_roles:
   259	        slot = cand.slot_by_role(role)
   260	        assert slot.broad_justification is None, (
   261	            f"fixture assumption: {role} must not be individually vouched"
   262	        )
   263	
   264	    # All three report the SAME shared fitted width (as they would after a
   265	    # real fit, since they're constrained equal via one lmfit expression).
   266	    shared_wide_fwhm = 8.0
   267	    comps = [
   268	        FittedComponent(slot_role=role, position=0.0, fwhm=shared_wide_fwhm,
   269	                        amplitude=1e4, shape_params={},
   270	                        line_shape=cand.slot_by_role(role).line_shape)
   271	        for role in contam_roles
   272	    ]
   273	    flags = _unphysical_width_flags(comps, cand)
   274	    flagged_roles = {f.split(":")[0] for f in flags}
   275	    assert flagged_roles == set(contam_roles), (
   276	        "a wide SHARED contamination width must flag every slot built on "
   277	        f"it, not just some -- got {flagged_roles}, expected all of "
   278	        f"{set(contam_roles)}"
   279	    )
   280	
   281	
   282	def test_mixed_wide_contamination_routes_to_conditional():
   283	    """The tiering consequence: a report carrying that exact unphysical-
   284	    widths flag must be excluded from clean survivors and, as the sole
   285	    report, land in the CONDITIONAL tier -- not silently accepted as a
   286	    clean winner. Uses a REAL ModelReport (from an actual, fast MIXED
   287	    C 1s fit) with its plausibility flags replaced by the ACTUAL flag
   288	    autofit.engine._unphysical_width_flags produces for the 8 eV scenario
   289	    above -- not a hand-written string -- so this test would break if the
   290	    flag's own wording or the tiering logic ever drifted apart."""
   291	    import dataclasses
   292	
   293	    import numpy as np
   294	
   295	    from autofit.engine import (FittedComponent, PlausibilityFlags,
   296	                                compare_models, rank_and_filter,
   297	                                _unphysical_width_flags)
   298	    from autofit.methods.base import poisson_like_weights
   299	
   300	    x = np.linspace(295.0, 280.0, 300)
   301	    y = (4000.0
   302	         + 6000.0 * np.exp(-0.5 * ((x - 284.6) / 0.9) ** 2)
   303	         + 1500.0 * np.exp(-0.5 * ((x - 286.8) / 1.0) ** 2))
   304	    weights = poisson_like_weights(y)
   305	    g = _resolve(MaterialClass.MIXED)
   306	
   307	    res = compare_models(x, y, weights, g, n_refits=1, rng_seed=0,
   308	                         enable_proposal_pass=False, enable_preseed=False,
   309	                         candidate_filter=["A1_linked"])
   310	    assert res.reports, "fixture assumption: A1_linked produced a report"
   311	    report = res.reports[0]
   312	
   313	    slot = report.model.slot_by_role("contamination_CO")
   314	    fake_comp = FittedComponent(slot_role="contamination_CO", position=286.0,
   315	                                fwhm=8.0, amplitude=1e4, shape_params={},
   316	                                line_shape=slot.line_shape)
   317	    injected_flags = _unphysical_width_flags([fake_comp], report.model)
   318	    assert injected_flags, "fixture assumption: the flag must fire"
   319	
   320	    conditional_report = dataclasses.replace(
   321	        report,
   322	        plausibility=PlausibilityFlags(boundary_hits=[],
   323	                                       unphysical_widths=injected_flags,
   324	                                       orphan_peaks=False),
   325	    )
   326	    result = rank_and_filter([conditional_report], allow_conditional=True)
   327	    # rank_and_filter's `survivors` holds the final ranked winner regardless
   328	    # of tier (matches test_stage2_completeness.py's last-resort precedent);
   329	    # the CLEAN-vs-CONDITIONAL distinction is `result.conditional` +
   330	    # `result.filtered_out`, not whether `survivors` is populated.
   331	    assert result.conditional is True, (
   332	        "a report with an unphysical-widths flag must route through the "
   333	        "CONDITIONAL tier, never win as a clean survivor"
   334	    )
   335	    assert result.conditional_reason == "no_clean_survivor"
   336	    assert conditional_report in [r for r, _ in result.filtered_out]

exec
/bin/zsh -lc 'git show --no-ext-diff --unified=80 --no-renames bdc909a -- templates/index.html tests/autofit/test_c1s_mixed_material_class.py tests/js/fp_material_mixed.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-xfxQcMY1' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ezSW1bwy' (errno=Operation not permitted)
commit bdc909a271f64bf59097a8cc734a71e5728cd436
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Mon Jul 20 13:21:20 2026 -0600

    fix(mixed): rebase MIXED's own 2 accepted Codex findings onto the corrected engine
    
    MIXED (77bf3a8) shipped with two open findings from its own Codex review,
    now fixed here, rebased onto the corrected broad_justification refactor
    (5070662 + ad7e668):
    
    1. Run B's MAJOR: the frontend copy ("Peak width limits are relaxed
       accordingly") read as global -- a chemist selecting MIXED for U 4f,
       Cl 2p, B 1s, or N 1s would wrongly believe peak widths changed there
       too, when only C 1s contamination/adventitious widths actually relax.
       FP_STRINGS.materials.mixed.hint now names C 1s contamination
       specifically and states other regions are unaffected.
    
    2. Both runs' MINOR: the provenance relaxation-record test only asserted
       `value` was a string, so a lab-derived number smuggled into prose
       (e.g. "relax to 3.5 eV based on our spectra") would still have passed
       -- exactly the provenance-audit trap this whole feature exists to
       avoid, missed by its own guard test. Now asserts the string contains
       no digit at all.
    
    The finding itself -- a MIXED contamination slot fitting at ~6-10 eV must
    now be flagged unphysical and route to CONDITIONAL, the actual gap both
    Codex reviews of the broad_justification refactor (5070662) and its
    _retag_slot fix (ad7e668) exist to close -- is encoded directly as
    test_mixed_wide_contamination_is_flagged_unphysical and
    test_mixed_wide_contamination_routes_to_conditional. Explicitly red-green
    verified rather than trusted: temporarily reverted autofit/engine.py's
    _unphysical_width_flags to the pre-Unit-A numeric rule
    (declared_hi > FWHM_MAX_ORDINARY_EV) and confirmed both tests fail there
    (not a laundered pin -- the same failure mode caught once already in this
    session's Tougaard background work), then confirmed green on restore.
    
    Also formalizes an empirical finding requested directly: 77bf3a8's own
    commit message flagged the "_linked" candidate families' shared
    contamination width as a KNOWN RISK (all 3 contaminant slots share ONE
    lmfit parameter, so a single fat shared value could in principle absorb
    signal across the whole ~280-292 eV contaminant span -- the same
    overlap-degeneracy class c1s.py's own MG-family comments document for a
    free position, reachable here through width instead). Verified directly
    (not left as a theoretical concern) that this is already closed: sharing
    one lmfit parameter does not create one shared exemption --
    _unphysical_width_flags checks each FittedComponent independently
    against its OWN slot's individually-unvouched broad_justification, so a
    wide shared value flags every slot built on it, not just some. Pinned as
    test_mixed_shared_width_contamination_all_flagged_independently.
    
    Re-confirmed test_material_class_does_not_affect_charge_correction still
    passes unchanged (charge correction remains provably untouched by any of
    this).
    
    Full suite: 748 passed, 6 skipped, 0 failed.
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

diff --git a/templates/index.html b/templates/index.html
index 2b2d3fa..818ec26 100644
--- a/templates/index.html
+++ b/templates/index.html
@@ -12950,166 +12950,167 @@ let _fpLast = null;        // last analysis result (for apply)
 // tierColor/tierNote (curated/machine/legacy), which grades a REFERENCE
 // ENERGY VALUE's provenance for the separate Reference/Identify palette —
 // see autofit/coverage_index.py's module docstring for why the same word
 // ("curated") means something different in each system, and why that's
 // intentional rather than an inconsistency to fix.
 const FP_TIER_META = {
   curated:        { color: '#3ddc84', tag: '[cited]',
                     label: 'Cited fit recipe' },
   machine:        { color: '#b48eff', tag: '[sourced]',
                     label: 'Sourced reference position' },
   structure_only: { color: '#8a9ab8', tag: '[structure only]',
                     label: 'No reference position' },
 };
 
 // One coverage entry + a search query -> does it match? Case-insensitive
 // substring match against the region label, element symbol, element name,
 // and level/subshell — matches how a chemist would actually search
 // ("Fe", "iron", "2p", "Fe 2p" all find the same entry).
 function _fpRegionMatchesFilter(entry, query) {
   const q = String(query == null ? '' : query).trim().toLowerCase();
   if (!q) return true;
   const hay = [entry.region, entry.symbol, entry.name, entry.level]
     .map(v => String(v || '').toLowerCase());
   return hay.some(h => h.includes(q));
 }
 
 // One coverage entry -> its <option> display text: tier tag + region +
 // element name, so the tier is legible even where <option> styling is
 // ignored (some browsers/screen readers) — color is a second, not the
 // only, channel.
 function _fpRegionOptionLabel(entry) {
   const meta = FP_TIER_META[entry.tier] || FP_TIER_META.structure_only;
   return meta.tag + ' ' + entry.region + ' — ' + entry.name;
 }
 
 // The full coverage array + a search query -> the option list to render
 // (value/label/tier per entry). Pure — used by both the initial modal
 // population and the live filter-input handler. Total: a missing/empty
 // coverage array or an unmatched query both degrade to [], never throw.
 function _fpBuildRegionOptions(coverage, query) {
   return (coverage || [])
     .filter(e => _fpRegionMatchesFilter(e, query))
     .map(e => ({ value: e.region, label: _fpRegionOptionLabel(e), tier: e.tier }));
 }
 
 // The currently-selected coverage entries -> the honesty note shown below
 // the selector (goal: "never shown as if it had cited grammar"). Total:
 // no selection -> ''.
 function _fpTierNoteFor(entries) {
   const list = entries || [];
   if (!list.length) return '';
   if (list.length === 1) {
     const meta = FP_TIER_META[list[0].tier] || FP_TIER_META.structure_only;
     return meta.label + ': ' + list[0].note;
   }
   return list.map(e => {
     const meta = FP_TIER_META[e.tier] || FP_TIER_META.structure_only;
     return e.region + ' (' + meta.label + ')';
   }).join(' · ');
 }
 
 // ═══ ALL user-facing wording lives HERE (one place, easy to iterate). ═══
 // Audience: bench chemists/spectroscopists. Engine jargon (grammar,
 // candidate-model, decisive_override, +bfix, role slugs) must never reach
 // the screen — the honest CONTENT stays, said plainly.
 const FP_STRINGS = {
   blurb: 'Suggests a set of peaks for the region(s) you select and shows ' +
          'how confident it is. These are <b>starting suggestions to ' +
          'review — not final answers</b>. Nothing changes your manual fit ' +
          'unless you add them.',
   applyNote: 'Adding replaces this tab’s current peak list with the ' +
              'suggested peaks. You can undo this (Ctrl+Z).',
   // Label/hint override for one material-class dropdown option (2026-07-20).
   // Only "mixed" gets an entry — conductor/semiconductor/insulator render
   // exactly as before (bare backend value, no title attribute).
   materials: {
     mixed: {
       label: 'mixed (analyte in matrix)',
       hint: 'Your sample is an analyte embedded in a different matrix, ' +
             'which can charge differently under x-rays than the matrix ' +
-            'does (differential charging). Peak width limits are relaxed ' +
-            'accordingly. The charge reference calibrates the MATRIX’s ' +
-            'potential — it may not apply to the analyte, so reported ' +
-            'positions carry additional, unquantified uncertainty. This ' +
-            'does not correct for that uncertainty; it only stops ' +
-            'assuming there isn’t any.',
+            'does (differential charging). For C 1s, contamination/' +
+            'adventitious peak width limits are relaxed accordingly — ' +
+            'other regions are unaffected. The charge reference ' +
+            'calibrates the MATRIX’s potential — it may not apply to the ' +
+            'analyte, so reported positions carry additional, ' +
+            'unquantified uncertainty. This does not correct for that ' +
+            'uncertainty; it only stops assuming there isn’t any.',
     },
   },
   tips: {
     material: 'Conducting samples charge-correct differently from ' +
               'insulating ones, and the suggested peak shapes differ too. ' +
               'Pick what best describes YOUR sample.',
     method: 'How the suggestions are generated. Hover (or select) an ' +
             'option below to see what it does and when to use it — ' +
             '“Compare peak models” fits most regions; the others trade ' +
             'speed for confidence ranges, a quick estimate, or refitting ' +
             'peaks you already placed.',
     regions: 'Which core-level region(s) to model. Pick the region this ' +
              'scan covers; ctrl-click two if one scan genuinely contains ' +
              'both (e.g. N 1s inside a U 4f window).',
     chi2r: 'Goodness of fit: about 1 means the model matches the data ' +
            'within noise; higher means the model is missing structure.',
     bic: 'Ranking score used to compare models — lower is better. Extra ' +
          'peaks are only rewarded when the data genuinely supports them.',
     sigmaCenter: 'Statistical uncertainty in the fitted peak position (eV).',
     position: 'Fitted peak position, binding energy (eV).',
     width: 'Fitted peak width, FWHM (eV).',
     height: 'Fitted peak height (counts).',
     shape: 'Line shape used for this peak.',
     status: 'How this model fared: the best-supported one wins; others ' +
             'are kept for comparison or rejected with the reason shown.',
   },
   methods: {
     ic_model_comparison: {
       label: 'Compare peak models (recommended)',
       hint: 'Tries several physically sensible peak models for the ' +
             'region, checks each for stability and plausibility, and ' +
             'reports the best-supported one. Use this first for most ' +
             'regions. Usually seconds to a minute.',
     },
     bayesian_exchange_mc: {
       label: 'Compare peak models + confidence ranges (slower)',
       hint: 'Does the same comparison, but samples many fits to attach ' +
             'confidence ranges to the result. Use this when you need an ' +
             'uncertainty estimate, not just a single best answer. Can ' +
             'take several minutes.',
     },
     sparse_map: {
       label: 'Quick peak count (approximate)',
       hint: 'A fast first look that estimates how many peaks are ' +
             'present. Positions are approximate — use this to get ' +
             'oriented, then follow up with “Compare peak models”.',
     },
     least_squares: {
       label: 'Refit my current peaks',
       hint: 'Refits the peaks already on this tab, using their current ' +
             'shapes and positions as the starting point. Use this to ' +
             'polish a fit you’ve already built manually — add peaks first.',
     },
   },
   // friendly controls per method — each writes into the Advanced JSON so
   // the request itself is unchanged (values only, no new behavior)
   controls: {
     ic_model_comparison: [
       { key: 'n_refits', type: 'number', min: 1, max: 32, step: 1,
         label: 'Stability re-fits',
         tip: 'How many times each model is re-fitted from different ' +
              'starting points to check the answer is stable. More is ' +
              'slower but more reliable.' },
       { key: 'enable_proposal_pass', type: 'checkbox',
         label: 'Look for unexpected extra peaks',
         tip: 'After fitting, scan the leftover signal for a clear peak ' +
              'the model missed and suggest it.' },
       { key: 'fit_full_window', type: 'checkbox',
         label: 'Fit the entire window',
         tip: 'By default, Find Peaks focuses on the region around the ' +
              'peaks. Check this to fit the full window you selected — ' +
              'best when your background is clean across the whole range.' },
     ],
     bayesian_exchange_mc: [
       { key: 'n_replicas', type: 'number', min: 4, max: 32, step: 1,
         label: 'Samplers',
         tip: 'Parallel samplers exploring the fit. More handles hard, ' +
              'overlapping regions better — and takes longer.' },
       { key: 'n_sweeps', type: 'number', min: 100, max: 20000, step: 100,
         label: 'Sampling length',
diff --git a/tests/autofit/test_c1s_mixed_material_class.py b/tests/autofit/test_c1s_mixed_material_class.py
index c827e62..a2dbfd9 100644
--- a/tests/autofit/test_c1s_mixed_material_class.py
+++ b/tests/autofit/test_c1s_mixed_material_class.py
@@ -84,106 +84,253 @@ def test_non_mixed_candidate_names_unchanged(material_class):
     names build_candidates() produces must be identical across every
     non-MIXED material class (it always was -- material_class was
     previously read nowhere in this module)."""
     names_conductor = {c.name for c in _resolve(MaterialClass.CONDUCTOR).candidates}
     names_other = {c.name for c in _resolve(material_class).candidates}
     assert names_conductor == names_other
 
 
 def test_mixed_relaxes_contamination_fwhm_ceiling():
     """The one concrete, falsifiable claim: MIXED must actually widen the
     contamination FWHM ceiling in the generated candidates -- otherwise
     the feature is decorative. The FLOOR must NOT move: differential
     charging only broadens a peak, it never narrows one, so there is no
     physical basis to touch 0.8 eV."""
     slots = _contamination_slots(_resolve(MaterialClass.MIXED))
     assert slots, "fixture assumption: at least one contamination-governed slot"
     for name, slot in slots:
         assert slot.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0], (
             f"{name}/{slot.role}: MIXED changed the FLOOR -- no physical "
             "justification for narrowing under differential charging"
         )
         assert slot.fwhm_range[1] > FWHM_RANGE_CONTAMINATION[1], (
             f"{name}/{slot.role}: MIXED did not widen the ceiling -- decorative"
         )
 
 
 def test_mixed_does_not_touch_position_windows_or_offsets():
     """The provenance-audit trap, enforced structurally: MIXED relaxes
     WIDTH only. Every BE window and every linked-offset (contaminant
     center position, expressed relative to the graphitic main) must be
     byte-identical to the conductor default -- tempting as it is to widen
     a position window to admit an uncited differential-charging shift,
     doing so would convert a known-unknown into a silently-permitted fit."""
     g_conductor = _resolve(MaterialClass.CONDUCTOR)
     g_mixed = _resolve(MaterialClass.MIXED)
 
     windows = lambda g: {(c.name, s.role): s.be_window
                          for c in g.candidates for s in c.slots}
     assert windows(g_conductor) == windows(g_mixed), (
         "MIXED must not alter any component's BE window"
     )
 
     offsets = lambda g: {(c.name, s.role): s.linked_offset_range
                          for c in g.candidates for s in c.slots}
     assert offsets(g_conductor) == offsets(g_mixed), (
         "MIXED must not alter any linked-offset (contaminant center) range"
     )
 
 
 def test_mixed_does_not_touch_unrelated_fwhm_families():
     """Scope discipline: only the contamination/adventitious FWHM family
     relaxes. The graphitic main, aromatic-polymer main, and satellite FWHM
     ranges are untouched -- this unit's own instructions name the
     adventitious cap as the one clear, in-scope case."""
     g_conductor = _resolve(MaterialClass.CONDUCTOR)
     g_mixed = _resolve(MaterialClass.MIXED)
 
     def other_family_ranges(g):
         return {(c.name, s.role): s.fwhm_range
                 for c in g.candidates for s in c.slots
                 if s.fwhm_range[0] != FWHM_RANGE_CONTAMINATION[0]}
 
     assert other_family_ranges(g_conductor) == other_family_ranges(g_mixed)
 
 
 def test_mixed_provenance_relaxation_record_asserts_no_new_value():
     """provenance() must document the relaxation itself: CONDITIONAL,
     citing the differential-charging literature, and its `value` must
     read as an ACTION (relax/remove a constraint) -- never a specific new
     BE or width number. This is the literal test of the provenance-audit
     design constraint: withdrawing an assumption needs no citation,
     asserting a new numeric window does, and this record must not smuggle
     one in under CONDITIONAL cover."""
     records = C1sModule().provenance()
     rec = _by_constant(records, "mixed_material_class_width_relaxation")
     assert rec["status"] == "CONDITIONAL"
     assert isinstance(rec["value"], str), (
         "the relaxation record's value must be a descriptive action, not "
         "a bare number that could read as a newly-asserted window"
     )
+    # Both Codex reviews of 77bf3a8 flagged this exact gap: "is a string"
+    # alone would pass `value = "relax to 3.5 eV based on our spectra"` --
+    # a lab-derived number smuggled in as prose. No digit may appear at all.
+    assert not any(ch.isdigit() for ch in rec["value"]), (
+        f"the relaxation record's value contains a digit -- it must "
+        f"describe an action only, never a specific number: {rec['value']!r}"
+    )
     assert "10.1116/6.0000057" in rec["source"], "Baer et al. 2020 DOI"
     assert "baer" in rec["source"].lower()
     assert "10.1016/j.pmatsci.2019.100591" in rec["source"], \
         "Greczynski & Hultman 2020 DOI"
     assert "greczynski" in rec["source"].lower()
     assert "hultman" in rec["source"].lower()
 
 
 def test_mixed_provenance_numeric_guard_record_is_honestly_labeled():
     """The residual finite ceiling (unavoidable -- the optimizer needs a
     finite initial-value midpoint) must be labeled UNVERIFIED and
     described as a numeric guard for fit stability, not a chemistry or
     physics claim -- the same footing as dsg_alpha_cap's 'fitalg numeric
     guard' language."""
     records = C1sModule().provenance()
     rec = _by_constant(records, "mixed_fwhm_ceiling_numeric_guard")
     assert rec["status"] == "UNVERIFIED"
     assert "numeric guard" in rec["source"].lower()
     assert ("not a chemistry" in rec["source"].lower()
             or "not a physical" in rec["source"].lower()
             or "not a physics" in rec["source"].lower())
     # the guard's own value must equal whatever ceiling build_candidates()
     # actually uses under MIXED -- no drift between the doc and the code
     slots = _contamination_slots(_resolve(MaterialClass.MIXED))
     actual_ceiling = slots[0][1].fwhm_range[1]
     assert rec["value"] == actual_ceiling
+
+
+# ── Unit A dependency: the finding itself, encoded (2026-07-20) ───────────
+# Both Codex reviews of 77bf3a8 independently caught the same MAJOR: the
+# 15.0 eV numeric guard made contamination slots "grammar-sanctioned-broad"
+# in autofit.engine._unphysical_width_flags, so a MIXED contaminant fitting
+# at 6-10 eV sailed through unflagged -- the exact opposite of MIXED's own
+# premise (we do NOT know how broad differential charging makes the peak,
+# so the app must not vouch for it). Fixed by Unit A (broad_justification):
+# MIXED contamination slots get a wide bound but NO justification, so they
+# are no longer exempt. These two tests are that finding, encoded directly.
+
+def test_mixed_wide_contamination_is_flagged_unphysical():
+    """A C 1s contamination component fit at 8 eV under MIXED (well within
+    the relaxed 0.8-15.0 eV bound, well above the ordinary 2.0 eV cap) must
+    be flagged unphysical -- the bound's width must never itself grant
+    exemption (that would be the finding recurring)."""
+    from autofit.engine import FittedComponent, _unphysical_width_flags
+
+    g = _resolve(MaterialClass.MIXED)
+    cand = next(c for c in g.candidates if c.name == "A1_linked")
+    slot = cand.slot_by_role("contamination_CO")
+    assert slot.broad_justification is None, (
+        "fixture assumption: MIXED contamination must NOT be vouched-broad"
+    )
+    comp = FittedComponent(slot_role="contamination_CO", position=286.0,
+                           fwhm=8.0, amplitude=1e4, shape_params={},
+                           line_shape=slot.line_shape)
+    flags = _unphysical_width_flags([comp], cand)
+    assert flags, (
+        "an 8 eV MIXED contaminant must be flagged unphysical -- the "
+        "relaxed bound must not silently exempt it"
+    )
+    assert any("contamination_CO" in f for f in flags)
+
+
+def test_mixed_shared_width_contamination_all_flagged_independently():
+    """The degeneracy risk 77bf3a8's own commit message flagged as KNOWN
+    RISK, not yet closed at the time: the "_linked" families share ONE
+    width parameter (_SHARED_CONTAM_FWHM) across all 3 contaminant slots,
+    so under MIXED that shared width also relaxes to the wide ceiling -- a
+    single fat shared-width component could in principle absorb signal
+    across the whole ~280-292 eV contaminant span (the same overlap-
+    degeneracy class c1s.py's own MG-family comments document for a free
+    position, now reachable through width instead).
+
+    Verified here rather than left as a theoretical concern: sharing one
+    lmfit parameter does not create one shared exemption. Each of the 3
+    linked slots keeps its OWN fwhm_range/broad_justification, and
+    _unphysical_width_flags checks each FittedComponent independently --
+    so a shared width ballooning wide flags EVERY slot built on it, not
+    just some, and none can hide behind another's exemption."""
+    from autofit.engine import FittedComponent, _unphysical_width_flags
+
+    g = _resolve(MaterialClass.MIXED)
+    cand = next(c for c in g.candidates if c.name == "A3_linked")
+    assert cand.shared_fwhm_params, (
+        "fixture assumption: A3_linked really does share one width "
+        "parameter across its contaminants"
+    )
+    contam_roles = ("contamination_CO", "contamination_C=O", "contamination_OC=O")
+    for role in contam_roles:
+        slot = cand.slot_by_role(role)
+        assert slot.broad_justification is None, (
+            f"fixture assumption: {role} must not be individually vouched"
+        )
+
+    # All three report the SAME shared fitted width (as they would after a
+    # real fit, since they're constrained equal via one lmfit expression).
+    shared_wide_fwhm = 8.0
+    comps = [
+        FittedComponent(slot_role=role, position=0.0, fwhm=shared_wide_fwhm,
+                        amplitude=1e4, shape_params={},
+                        line_shape=cand.slot_by_role(role).line_shape)
+        for role in contam_roles
+    ]
+    flags = _unphysical_width_flags(comps, cand)
+    flagged_roles = {f.split(":")[0] for f in flags}
+    assert flagged_roles == set(contam_roles), (
+        "a wide SHARED contamination width must flag every slot built on "
+        f"it, not just some -- got {flagged_roles}, expected all of "
+        f"{set(contam_roles)}"
+    )
+
+
+def test_mixed_wide_contamination_routes_to_conditional():
+    """The tiering consequence: a report carrying that exact unphysical-
+    widths flag must be excluded from clean survivors and, as the sole
+    report, land in the CONDITIONAL tier -- not silently accepted as a
+    clean winner. Uses a REAL ModelReport (from an actual, fast MIXED
+    C 1s fit) with its plausibility flags replaced by the ACTUAL flag
+    autofit.engine._unphysical_width_flags produces for the 8 eV scenario
+    above -- not a hand-written string -- so this test would break if the
+    flag's own wording or the tiering logic ever drifted apart."""
+    import dataclasses
+
+    import numpy as np
+
+    from autofit.engine import (FittedComponent, PlausibilityFlags,
+                                compare_models, rank_and_filter,
+                                _unphysical_width_flags)
+    from autofit.methods.base import poisson_like_weights
+
+    x = np.linspace(295.0, 280.0, 300)
+    y = (4000.0
+         + 6000.0 * np.exp(-0.5 * ((x - 284.6) / 0.9) ** 2)
+         + 1500.0 * np.exp(-0.5 * ((x - 286.8) / 1.0) ** 2))
+    weights = poisson_like_weights(y)
+    g = _resolve(MaterialClass.MIXED)
+
+    res = compare_models(x, y, weights, g, n_refits=1, rng_seed=0,
+                         enable_proposal_pass=False, enable_preseed=False,
+                         candidate_filter=["A1_linked"])
+    assert res.reports, "fixture assumption: A1_linked produced a report"
+    report = res.reports[0]
+
+    slot = report.model.slot_by_role("contamination_CO")
+    fake_comp = FittedComponent(slot_role="contamination_CO", position=286.0,
+                                fwhm=8.0, amplitude=1e4, shape_params={},
+                                line_shape=slot.line_shape)
+    injected_flags = _unphysical_width_flags([fake_comp], report.model)
+    assert injected_flags, "fixture assumption: the flag must fire"
+
+    conditional_report = dataclasses.replace(
+        report,
+        plausibility=PlausibilityFlags(boundary_hits=[],
+                                       unphysical_widths=injected_flags,
+                                       orphan_peaks=False),
+    )
+    result = rank_and_filter([conditional_report], allow_conditional=True)
+    # rank_and_filter's `survivors` holds the final ranked winner regardless
+    # of tier (matches test_stage2_completeness.py's last-resort precedent);
+    # the CLEAN-vs-CONDITIONAL distinction is `result.conditional` +
+    # `result.filtered_out`, not whether `survivors` is populated.
+    assert result.conditional is True, (
+        "a report with an unphysical-widths flag must route through the "
+        "CONDITIONAL tier, never win as a clean survivor"
+    )
+    assert result.conditional_reason == "no_clean_survivor"
+    assert conditional_report in [r for r, _ in result.filtered_out]
diff --git a/tests/js/fp_material_mixed.test.js b/tests/js/fp_material_mixed.test.js
index 4397981..2d80cc9 100644
--- a/tests/js/fp_material_mixed.test.js
+++ b/tests/js/fp_material_mixed.test.js
@@ -1,54 +1,65 @@
 // MIXED material class (2026-07-20 unit) -- Find Peaks modal must offer a
 // clear label ("mixed (analyte in matrix)" reads better than bare "mixed")
 // and an advisory note: MIXED does not correct for differential charging,
 // it only stops ASSUMING there isn't any. Per the DECIDED scope
 // (Skye, 2026-07-17), the note must describe the charge reference as not
 // necessarily transferring to the analyte -- it must never imply the app
 // has corrected for anything.
 
 const { test } = require('node:test');
 const assert = require('node:assert');
 const fs = require('node:fs');
 const path = require('node:path');
 
 const html = fs.readFileSync(
   path.join(__dirname, '../../templates/index.html'), 'utf8');
 
 function extract(re, name) {
   const m = html.match(re);
   assert.ok(m, name + ' not found in templates/index.html');
   return m[0];
 }
 
 const FP_STRINGS = eval(
   '(' + extract(/const FP_STRINGS = \{[\s\S]*?\n\};/, 'FP_STRINGS')
     .replace(/^const FP_STRINGS = /, '').replace(/;$/, '') + ')');
 
 test('FP_STRINGS.materials.mixed has a clear, non-bare label', () => {
   assert.ok(FP_STRINGS.materials && FP_STRINGS.materials.mixed,
     'FP_STRINGS.materials.mixed must exist');
   const label = FP_STRINGS.materials.mixed.label;
   assert.match(label, /mixed/i);
   assert.match(label, /analyte/i);
   assert.notStrictEqual(label, 'mixed');
 });
 
 test('FP_STRINGS.materials.mixed hint is advisory, never claims correction', () => {
   const hint = FP_STRINGS.materials.mixed.hint;
   assert.match(hint, /charge reference/i);
   assert.match(hint, /uncertain|not.*apply|may not/i);
   // must not imply the app corrected for differential charging
   assert.doesNotMatch(hint, /has been corrected/i);
   assert.doesNotMatch(hint, /automatically adjust/i);
   assert.doesNotMatch(hint, /we (have )?correct/i);
 });
 
 test('FP_STRINGS has no override entries for the other 3 material classes '
      + '(dropdown rendering must stay byte-identical for them)', () => {
   const materials = FP_STRINGS.materials || {};
   for (const v of ['conductor', 'semiconductor', 'insulator']) {
     assert.strictEqual(materials[v], undefined,
       `${v} must not get an FP_STRINGS override -- non-MIXED rendering `
       + 'must be unchanged');
   }
 });
+
+test('FP_STRINGS.materials.mixed hint names C 1s specifically and does not '
+     + 'overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)', () => {
+  // "Peak width limits are relaxed accordingly" (no region named) reads as
+  // global -- a chemist picking MIXED for U 4f/Cl 2p/B 1s/N 1s would wrongly
+  // believe peak widths changed there too. Only C 1s contamination/
+  // adventitious widths actually relax.
+  const hint = FP_STRINGS.materials.mixed.hint;
+  assert.match(hint, /C ?1s/);
+  assert.match(hint, /other regions are unaffected|only C ?1s|no effect on other regions/i);
+});

codex
The regression tests are structurally aimed at the old failure: the synthetic 8 eV contaminant sits inside MIXED’s widened `(0.8, 15.0)` slot, and the current engine’s exemption key is `slot.broad_justification`, not the upper bound. I’m checking the shared-width construction across all linked families now, including offset-linked and B-linked variants, because that is where a narrow test could miss a real path.
exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '130,230p;540,630p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   130	    linked_to: Optional[str] = None
   131	    linked_offset_range: Optional[tuple[float, float]] = None
   132	
   133	    # Amplitude-linkage (spin-orbit doublets):  amplitude = parent × ratio.
   134	    # `area_ratio_range` bounds a *relaxed* ratio parameter around the
   135	    # theoretical default (e.g. U 4f 0.75 with bounded relaxation, spec §3.2).
   136	    area_ratio: Optional[float] = None
   137	    area_ratio_range: Optional[tuple[float, float]] = None
   138	
   139	    # Generic per-shape-parameter constraints, e.g. (("beta", 0.05),) to fix
   140	    # the DS+G Lorentzian HWHM at the C 1s core-hole lifetime.
   141	    fixed_params: tuple[tuple[str, float], ...] = ()
   142	    param_ranges: tuple[tuple[str, tuple[float, float]], ...] = ()
   143	
   144	    # Width-linkage: this slot's fwhm becomes an lmfit expression referencing
   145	    # another parameter name (Biesinger-style shared contamination width).
   146	    fwhm_linked_to: Optional[str] = None
   147	
   148	    # Width-INEQUALITY linkage (spin-orbit doublets whose deeper j-hole is
   149	    # Coster-Kronig broadened, e.g. Cl 2p1/2 — adjudication 2026-07-03,
   150	    # docs/autofit/adjudication-decisions.md #7): this slot's width parameter
   151	    # becomes parent_width + a FREE non-negative excess bounded by this
   152	    # range, enforcing width(child) >= width(parent).  Requires
   153	    # ``linked_to``; mutually exclusive with fixing/sharing/expression-
   154	    # linking the width.  An excess pegged at 0 surfaces as a boundary hit,
   155	    # correctly steering selection toward the nested shared-width candidate.
   156	    fwhm_excess_range: Optional[tuple[float, float]] = None
   157	
   158	    # Names of shape parameters tied to the PARENT slot's same-named
   159	    # parameters via lmfit expressions (requires ``linked_to``).  The width
   160	    # parameter name ('fwhm' / DS+G 'm_gauss') is allowed here too.  This is
   161	    # how a spin-orbit partner shares its sibling's lineshape (e.g. LACX
   162	    # alpha/beta/m across a U 4f doublet), mirroring the manual path's
   163	    # linked-peak sync.
   164	    share_parent_params: tuple[str, ...] = ()
   165	
   166	    # Explicit semantic claim, independent of fwhm_range's magnitude
   167	    # (2026-07-20 refactor): the region module VOUCHES that a component
   168	    # this wide is legitimate physics for this slot specifically — e.g. the
   169	    # C 1s π→π* shake-up satellite's intrinsic multi-electron-excitation
   170	    # breadth, or U 4f's unresolved 5f² multiplet manifold. None means the
   171	    # slot's width is ordinary — no known-broad justification exists, so
   172	    # autofit.engine._unphysical_width_flags must not exempt it, REGARDLESS
   173	    # of how wide fwhm_range happens to be. Before this field existed,
   174	    # fwhm_range's upper bound alone served double duty as both the
   175	    # optimizer's search bound AND this semantic claim (declared_hi >
   176	    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
   177	    # bound for an UNRELATED reason (numerical-stability headroom, a wider
   178	    # calibration envelope) silently asserted "this is vouched-for physics"
   179	    # as a side effect. A region module that just needs search headroom
   180	    # without vouching for width MUST leave this None.
   181	    broad_justification: Optional[str] = None
   182	
   183	    def contains(self, be: float, fwhm: float, amplitude: float,
   184	                 noise_floor: float) -> bool:
   185	        return (
   186	            self.be_window[0] <= be <= self.be_window[1]
   187	            and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
   188	            and amplitude > noise_floor
   189	        )
   190	
   191	
   192	@dataclass(frozen=True)
   193	class CandidateModel:
   194	    """A candidate model M = (background, slots) with admissibility built in."""
   195	    name: str
   196	    background: BackgroundType
   197	    slots: tuple[ComponentSlot, ...]
   198	    # (name, min, max) free params referenced by fwhm_linked_to expressions
   199	    shared_fwhm_params: tuple[tuple[str, float, float], ...] = ()
   200	
   201	    @property
   202	    def n_components(self) -> int:
   203	        return len(self.slots)
   204	
   205	    def slot_by_role(self, role: str) -> Optional[ComponentSlot]:
   206	        for s in self.slots:
   207	            if s.role == role:
   208	                return s
   209	        return None
   210	
   211	
   212	@dataclass
   213	class CandidateGrammar:
   214	    """resolve() output: the composed, admissible candidate set."""
   215	    regions: tuple[str, ...]
   216	    phase_ids: tuple[str, ...]
   217	    candidates: list[CandidateModel]
   218	    diagnostic_windows: dict[str, tuple[float, float]]
   219	    # Human-readable resolution trace (which phase supplied which region,
   220	    # Layer-A decisions, oxidation-state overrides applied).
   221	    notes: list[str] = field(default_factory=list)
   222	    # {region-slug: [{constant, value, status, source}, ...]} — every
   223	    # physical constant the resolved grammar consumes, with its verification
   224	    # status.  Travels into the analysis namespace (never comments-only).
   225	    provenance: dict[str, list[dict]] = field(default_factory=dict)
   226	    # Phase D structural fallback: regions resolved WITHOUT a registered
   227	    # module — derived structure only (see autofit.coverage), zero fit
   228	    # candidates contributed.  Empty for every pre-Phase-D caller.
   229	    structural_only: tuple[str, ...] = ()
   230	
   540	                raise ValueError(
   541	                    f"candidate {cand.name!r}: slot {slot.role!r} region "
   542	                    f"{slot.region!r} is not contributed by phase {phase.id!r}"
   543	                )
   544	
   545	
   546	def _compose_joint_candidates(
   547	    slugs: list[str],
   548	    per_request: list[list[CandidateModel]],
   549	) -> list[CandidateModel]:
   550	    """
   551	    Cartesian composition of per-request candidate sets into joint models for
   552	    one shared spectral window.  Slot roles are prefixed with the request's
   553	    slug (region name, phase-qualified when the same region appears for
   554	    multiple phases) to stay unique; the shared window uses ONE background
   555	    (co-fit means one physical loss continuum).
   556	    """
   557	    composed: list[CandidateModel] = []
   558	    for combo in itertools.product(*per_request):
   559	        backgrounds = {c.background for c in combo}
   560	        if len(backgrounds) != 1:
   561	            raise ValueError(
   562	                f"joint candidates must share one background, got {backgrounds} "
   563	                f"for {[c.name for c in combo]}"
   564	            )
   565	        slots: list[ComponentSlot] = []
   566	        shared: list[tuple[str, float, float]] = []
   567	        for slug, cand in zip(slugs, combo):
   568	            slug = re.sub(r"[^A-Za-z0-9_]", "", slug.replace(" ", ""))
   569	            rename = {s.role: f"{slug}__{s.role}" for s in cand.slots}
   570	            shared_rename = {name: f"{slug}__{name}" for name, _, _ in cand.shared_fwhm_params}
   571	            for s in cand.slots:
   572	                slots.append(_retag_slot(s, rename, shared_rename))
   573	            for name, lo, hi in cand.shared_fwhm_params:
   574	                shared.append((shared_rename[name], lo, hi))
   575	        composed.append(CandidateModel(
   576	            name="+".join(c.name for c in combo),
   577	            background=combo[0].background,
   578	            slots=tuple(slots),
   579	            shared_fwhm_params=tuple(shared),
   580	        ))
   581	    return composed
   582	
   583	
   584	def _retag_slot(
   585	    s: ComponentSlot,
   586	    rename: dict[str, str],
   587	    shared_rename: dict[str, str],
   588	) -> ComponentSlot:
   589	    """Rewrite role / linked_to / fwhm_linked_to under the region prefix.
   590	
   591	    Uses dataclasses.replace (ComponentSlot is frozen) rather than
   592	    reconstructing the slot field-by-field: replace() carries every field
   593	    NOT explicitly overridden forward unchanged, including any field added
   594	    to ComponentSlot after this function was written. The manual
   595	    reconstruction this replaced was exactly how broad_justification got
   596	    silently dropped for every multi-region composed candidate (Codex-caught
   597	    regression, 2026-07-20): a new field simply wasn't in the list, so it
   598	    defaulted back to None for every slot passing through here — see
   599	    tests/autofit/test_broad_justification.py's
   600	    test_retag_slot_preserves_all_fields_except_the_three_rewritten, which
   601	    guards against this exact class of bug recurring for whatever field
   602	    comes next.
   603	    """
   604	    fwhm_link = s.fwhm_linked_to
   605	    if fwhm_link is not None:
   606	        # fwhm_linked_to may reference either a shared param or another
   607	        # slot's parameter name (prefix-based); rewrite whichever matches.
   608	        if fwhm_link in shared_rename:
   609	            fwhm_link = shared_rename[fwhm_link]
   610	        else:
   611	            for old, new in rename.items():
   612	                old_prefix = _slot_param_prefix(old)
   613	                if fwhm_link.startswith(old_prefix):
   614	                    fwhm_link = _slot_param_prefix(new) + fwhm_link[len(old_prefix):]
   615	                    break
   616	    return replace(
   617	        s,
   618	        role=rename[s.role],
   619	        linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None,
   620	        fwhm_linked_to=fwhm_link,
   621	    )
   622	
   623	
   624	def _slot_param_prefix(role: str) -> str:
   625	    """Must match engine._slot_prefix — kept here to rewrite fwhm links."""
   626	    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"

exec
/bin/zsh -lc "rg -n \"shared_fwhm_params|fwhm_linked_to|FittedComponent\\(|slot_by_role|components=\" autofit/engine.py autofit/grammar.py autofit/fitting.py autofit -g '*.py'" in /Users/skyefortier/xps-verify
 exited 2 in 0ms:
rg: autofit/fitting.py: No such file or directory (os error 2)
autofit/grammar.py:146:    fwhm_linked_to: Optional[str] = None
autofit/grammar.py:198:    # (name, min, max) free params referenced by fwhm_linked_to expressions
autofit/grammar.py:199:    shared_fwhm_params: tuple[tuple[str, float, float], ...] = ()
autofit/grammar.py:205:    def slot_by_role(self, role: str) -> Optional[ComponentSlot]:
autofit/grammar.py:570:            shared_rename = {name: f"{slug}__{name}" for name, _, _ in cand.shared_fwhm_params}
autofit/grammar.py:573:            for name, lo, hi in cand.shared_fwhm_params:
autofit/grammar.py:579:            shared_fwhm_params=tuple(shared),
autofit/grammar.py:589:    """Rewrite role / linked_to / fwhm_linked_to under the region prefix.
autofit/grammar.py:604:    fwhm_link = s.fwhm_linked_to
autofit/grammar.py:606:        # fwhm_linked_to may reference either a shared param or another
autofit/grammar.py:620:        fwhm_linked_to=fwhm_link,
autofit/engine.py:392:        if wname in shared or wname in fixed or slot.fwhm_linked_to is not None:
autofit/engine.py:410:    elif slot.fwhm_linked_to is not None:
autofit/engine.py:412:              expr=slot.fwhm_linked_to)
autofit/engine.py:494:    for name, lo_b, hi_b in model.shared_fwhm_params:
autofit/engine.py:546:        parent = model.slot_by_role(slot.linked_to)
autofit/engine.py:675:        out.append(FittedComponent(
autofit/engine.py:913:            converged=False, components=[], residual_sum_sq=float("inf"),
autofit/engine.py:922:        components=_extract_fitted_components(result, model),
autofit/engine.py:1076:            orphans.append(FittedComponent(
autofit/engine.py:1094:        claimed = FittedComponent(
autofit/engine.py:1915:        shared_fwhm_params=base.shared_fwhm_params,
autofit/engine.py:2122:        shared_fwhm_params=base.shared_fwhm_params,
autofit/engine.py:2861:                    fitted_components=current.primary_fit.components,
autofit/engine.py:392:        if wname in shared or wname in fixed or slot.fwhm_linked_to is not None:
autofit/engine.py:410:    elif slot.fwhm_linked_to is not None:
autofit/engine.py:412:              expr=slot.fwhm_linked_to)
autofit/engine.py:494:    for name, lo_b, hi_b in model.shared_fwhm_params:
autofit/engine.py:546:        parent = model.slot_by_role(slot.linked_to)
autofit/engine.py:675:        out.append(FittedComponent(
autofit/engine.py:913:            converged=False, components=[], residual_sum_sq=float("inf"),
autofit/engine.py:922:        components=_extract_fitted_components(result, model),
autofit/engine.py:1076:            orphans.append(FittedComponent(
autofit/engine.py:1094:        claimed = FittedComponent(
autofit/engine.py:1915:        shared_fwhm_params=base.shared_fwhm_params,
autofit/engine.py:2122:        shared_fwhm_params=base.shared_fwhm_params,
autofit/engine.py:2861:                    fitted_components=current.primary_fit.components,
autofit/grammar.py:146:    fwhm_linked_to: Optional[str] = None
autofit/grammar.py:198:    # (name, min, max) free params referenced by fwhm_linked_to expressions
autofit/grammar.py:199:    shared_fwhm_params: tuple[tuple[str, float, float], ...] = ()
autofit/grammar.py:205:    def slot_by_role(self, role: str) -> Optional[ComponentSlot]:
autofit/grammar.py:570:            shared_rename = {name: f"{slug}__{name}" for name, _, _ in cand.shared_fwhm_params}
autofit/grammar.py:573:            for name, lo, hi in cand.shared_fwhm_params:
autofit/grammar.py:579:            shared_fwhm_params=tuple(shared),
autofit/grammar.py:589:    """Rewrite role / linked_to / fwhm_linked_to under the region prefix.
autofit/grammar.py:604:    fwhm_link = s.fwhm_linked_to
autofit/grammar.py:606:        # fwhm_linked_to may reference either a shared param or another
autofit/grammar.py:620:        fwhm_linked_to=fwhm_link,
autofit/confidence.py:38:    slot = report.model.slot_by_role(role)
autofit/regions/c1s.py:350:                kw["fwhm_linked_to"] = linked_fwhm
autofit/regions/c1s.py:367:                slots=tuple(slots), shared_fwhm_params=tuple(shared),

exec
/bin/zsh -lc "nl -ba tests/test_api_analyze.py | sed -n '200,240p' && nl -ba app.py | sed -n '232,294p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   200	        "regions": ["Cl 2p"], "method": "ic_model_comparison",
   201	        "roi": {"be_min": 192.0, "be_max": 205.0},
   202	        "options": {"n_refits": 2, "enable_proposal_pass": False},
   203	    })
   204	    assert resp.status_code == 202, resp.get_json()
   205	    assert "job_id" in resp.get_json()
   206	
   207	
   208	def test_material_class_does_not_affect_charge_correction(client):
   209	    """DECIDED (Skye, 2026-07-17): MIXED must not alter the charge-
   210	    correction step in any way -- not suppressed, not adjusted, not
   211	    conditionally applied. Verified at the mechanism, not just by reading
   212	    the diff: _validate_analyze_request's corrected/ROI-masked (x, y)
   213	    arrays -- the actual output of the cc_shift charge-correction step --
   214	    must be byte-identical regardless of material_class. material_class
   215	    only ever reaches Phase.material_class, consumed by grammar
   216	    resolution/candidate building, which happens strictly AFTER x/y are
   217	    already fixed."""
   218	    from app import _validate_analyze_request
   219	
   220	    sid = _upload_doublet(client)
   221	    upload_folder = client.application.config["UPLOAD_FOLDER"]
   222	    base = {
   223	        "session_id": sid, "regions": ["Cl 2p"],
   224	        "method": "ic_model_comparison", "cc_shift": 1.23,
   225	        "roi": {"be_min": 192.0, "be_max": 205.0},
   226	    }
   227	    ctx_conductor = _validate_analyze_request(
   228	        {**base, "material_class": "conductor"}, upload_folder)
   229	    ctx_mixed = _validate_analyze_request(
   230	        {**base, "material_class": "mixed"}, upload_folder)
   231	    assert np.array_equal(ctx_conductor.x, ctx_mixed.x)
   232	    assert np.array_equal(ctx_conductor.y, ctx_mixed.y)
   233	
   234	
   235	def test_json_sanitize_non_finite():
   236	    """inf/NaN (degenerate-fit BIC values) must become null, not invalid
   237	    JSON tokens browsers refuse to parse."""
   238	    from app import _json_sanitize
   239	    out = _json_sanitize({"a": float("inf"), "b": float("nan"),
   240	                          "c": [1.0, float("-inf")],
   232	
   233	    method_id = body.get("method", "ic_model_comparison")
   234	    if method_id not in _ANALYZE_METHODS:
   235	        raise _AnalyzeError(f"Unknown analyze method '{method_id}' "
   236	                            f"(available: {sorted(_ANALYZE_METHODS)})")
   237	
   238	    regions = body.get("regions") or []
   239	    if (not isinstance(regions, list) or not regions
   240	            or not all(isinstance(r, str) for r in regions)):
   241	        raise _AnalyzeError("'regions' must be a non-empty list of region names")
   242	
   243	    mc_raw = body.get("material_class", "")
   244	    try:
   245	        mclass = MaterialClass(mc_raw)
   246	    except ValueError:
   247	        raise _AnalyzeError(f"Unknown material_class '{mc_raw}'")
   248	
   249	    try:
   250	        cc_shift = float(body.get("cc_shift", 0.0))
   251	    except (TypeError, ValueError):
   252	        raise _AnalyzeError("cc_shift must be a number")
   253	    corrected = energy - cc_shift   # frontend getCorrectedBE convention
   254	
   255	    # present-but-falsy non-objects ([], "", false) must be clean 400s,
   256	    # not silently treated as omitted (Codex re-check)
   257	    roi = body.get("roi")
   258	    roi = {} if roi is None else roi
   259	    if not isinstance(roi, dict):
   260	        raise _AnalyzeError("'roi' must be an object")
   261	    try:
   262	        be_min = float(roi.get("be_min", float(corrected.min())))
   263	        be_max = float(roi.get("be_max", float(corrected.max())))
   264	    except (TypeError, ValueError):
   265	        raise _AnalyzeError("roi.be_min/be_max must be numbers")
   266	    mask = (corrected >= be_min) & (corrected <= be_max)
   267	    if int(mask.sum()) < 20:
   268	        raise _AnalyzeError("ROI selects fewer than 20 points")
   269	    x, y = corrected[mask], counts[mask]
   270	
   271	    options = body.get("options")
   272	    options = {} if options is None else options
   273	    if not isinstance(options, dict):
   274	        raise _AnalyzeError("'options' must be an object")
   275	    opts = {**_ANALYZE_METHODS[method_id], **options}
   276	
   277	    peak_specs = body.get("peak_specs") or None
   278	    if method_id == "least_squares" and not peak_specs:
   279	        raise _AnalyzeError("least_squares is the manual-model baseline — "
   280	                            "provide 'peak_specs'")
   281	
   282	    phase_kwargs = body.get("phase")
   283	    phase_kwargs = {} if phase_kwargs is None else phase_kwargs
   284	    if not isinstance(phase_kwargs, dict):
   285	        raise _AnalyzeError("'phase' must be an object")
   286	    grammar = None
   287	    if method_id != "least_squares":
   288	        phase = Phase(id=str(phase_kwargs.get("id", "sample")),
   289	                      material_class=mclass,
   290	                      regions=tuple(regions),
   291	                      material=phase_kwargs.get("material"))
   292	        try:
   293	            # Phase D: regions without a deep module degrade to derived
   294	            # structure instead of erroring (unparseable labels still 400)

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13018,13038p' && nl -ba tests/js/fp_material_mixed.test.js | sed -n '34,68p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 13018	         'review — not final answers</b>. Nothing changes your manual fit ' +
 13019	         'unless you add them.',
 13020	  applyNote: 'Adding replaces this tab’s current peak list with the ' +
 13021	             'suggested peaks. You can undo this (Ctrl+Z).',
 13022	  // Label/hint override for one material-class dropdown option (2026-07-20).
 13023	  // Only "mixed" gets an entry — conductor/semiconductor/insulator render
 13024	  // exactly as before (bare backend value, no title attribute).
 13025	  materials: {
 13026	    mixed: {
 13027	      label: 'mixed (analyte in matrix)',
 13028	      hint: 'Your sample is an analyte embedded in a different matrix, ' +
 13029	            'which can charge differently under x-rays than the matrix ' +
 13030	            'does (differential charging). For C 1s, contamination/' +
 13031	            'adventitious peak width limits are relaxed accordingly — ' +
 13032	            'other regions are unaffected. The charge reference ' +
 13033	            'calibrates the MATRIX’s potential — it may not apply to the ' +
 13034	            'analyte, so reported positions carry additional, ' +
 13035	            'unquantified uncertainty. This does not correct for that ' +
 13036	            'uncertainty; it only stops assuming there isn’t any.',
 13037	    },
 13038	  },
    34	});
    35	
    36	test('FP_STRINGS.materials.mixed hint is advisory, never claims correction', () => {
    37	  const hint = FP_STRINGS.materials.mixed.hint;
    38	  assert.match(hint, /charge reference/i);
    39	  assert.match(hint, /uncertain|not.*apply|may not/i);
    40	  // must not imply the app corrected for differential charging
    41	  assert.doesNotMatch(hint, /has been corrected/i);
    42	  assert.doesNotMatch(hint, /automatically adjust/i);
    43	  assert.doesNotMatch(hint, /we (have )?correct/i);
    44	});
    45	
    46	test('FP_STRINGS has no override entries for the other 3 material classes '
    47	     + '(dropdown rendering must stay byte-identical for them)', () => {
    48	  const materials = FP_STRINGS.materials || {};
    49	  for (const v of ['conductor', 'semiconductor', 'insulator']) {
    50	    assert.strictEqual(materials[v], undefined,
    51	      `${v} must not get an FP_STRINGS override -- non-MIXED rendering `
    52	      + 'must be unchanged');
    53	  }
    54	});
    55	
    56	test('FP_STRINGS.materials.mixed hint names C 1s specifically and does not '
    57	     + 'overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)', () => {
    58	  // "Peak width limits are relaxed accordingly" (no region named) reads as
    59	  // global -- a chemist picking MIXED for U 4f/Cl 2p/B 1s/N 1s would wrongly
    60	  // believe peak widths changed there too. Only C 1s contamination/
    61	  // adventitious widths actually relax.
    62	  const hint = FP_STRINGS.materials.mixed.hint;
    63	  assert.match(hint, /C ?1s/);
    64	  assert.match(hint, /other regions are unaffected|only C ?1s|no effect on other regions/i);
    65	});

codex
One additional linked path exists beyond the test’s named `A3_linked`: the `B2/B3_linked` family links contaminant widths to the aliphatic main’s FWHM parameter rather than `_SHARED_CONTAM_FWHM`. I’m going to enumerate the candidates directly and check whether any MIXED slot with a widened C 1s contamination/adventitious width can reach 8 eV without producing an unphysical-width flag.
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '360,425p;485,505p;650,690p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   360	}
   361	
   362	# Which parameter carries the slot's fwhm_range for each shape.
   363	def _width_param(shape: LineShape) -> str:
   364	    return "m_gauss" if shape is LineShape.DS_G else "fwhm"
   365	
   366	
   367	def _add_shape_params(
   368	    p: Parameters, prefix: str, slot: ComponentSlot, fwhm_init: float,
   369	    parent_prefix: Optional[str] = None,
   370	) -> None:
   371	    """Width + shape-specific parameters for one slot, with bounds/overrides."""
   372	    flo, fhi = slot.fwhm_range
   373	    fixed = dict(slot.fixed_params)
   374	    ranges = dict(slot.param_ranges)
   375	    shared = set(slot.share_parent_params)
   376	    if shared and parent_prefix is None:
   377	        raise ValueError(
   378	            f"slot {slot.role!r} declares share_parent_params but has no "
   379	            "linked parent"
   380	        )
   381	
   382	    # Width parameter (fwhm, or m_gauss for DS+G)
   383	    wname = _width_param(slot.line_shape)
   384	    if slot.fwhm_excess_range is not None:
   385	        # width-inequality linkage: width = parent width + free excess >= 0
   386	        # (Coster-Kronig doublet broadening — grammar.ComponentSlot docs)
   387	        if parent_prefix is None:
   388	            raise ValueError(
   389	                f"slot {slot.role!r} declares fwhm_excess_range but has no "
   390	                "linked parent"
   391	            )
   392	        if wname in shared or wname in fixed or slot.fwhm_linked_to is not None:
   393	            raise ValueError(
   394	                f"slot {slot.role!r}: fwhm_excess_range is mutually exclusive "
   395	                "with sharing/fixing/expression-linking the width"
   396	            )
   397	        elo, ehi = slot.fwhm_excess_range
   398	        if not (0.0 <= elo < ehi):
   399	            raise ValueError(
   400	                f"slot {slot.role!r}: fwhm_excess_range must be a "
   401	                f"non-negative interval, got {slot.fwhm_excess_range}"
   402	            )
   403	        p.add(f"{prefix}fwhm_excess", value=0.5 * (elo + ehi), min=elo, max=ehi)
   404	        p.add(f"{prefix}{wname}", value=0.0,
   405	              expr=f"{parent_prefix}{wname} + {prefix}fwhm_excess")
   406	    elif wname in shared:
   407	        p.add(f"{prefix}{wname}", value=0.0, expr=f"{parent_prefix}{wname}")
   408	    elif wname in fixed:
   409	        p.add(f"{prefix}{wname}", value=float(fixed[wname]), vary=False)
   410	    elif slot.fwhm_linked_to is not None:
   411	        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, flo, fhi)),
   412	              expr=slot.fwhm_linked_to)
   413	    else:
   414	        wlo, whi = ranges.get(wname, (flo, fhi))
   415	        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, wlo, whi)),
   416	              min=wlo, max=whi)
   417	
   418	    for name, init, lo, hi in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
   419	        if name in shared:
   420	            p.add(f"{prefix}{name}", value=0.0, expr=f"{parent_prefix}{name}")
   421	            continue
   422	        if name in fixed:
   423	            p.add(f"{prefix}{name}", value=float(fixed[name]), vary=False)
   424	            continue
   425	        plo, phi = ranges.get(name, (lo, hi))
   485	    ``fit_full_window`` (default False — every existing caller's behavior
   486	    is unchanged unless it opts in) relaxes the primary-slot CENTER bound
   487	    per ``_full_window_bound_overrides``; the starting guess and the
   488	    amplitude-estimate window always stay anchored to the slot's own
   489	    ``be_window``, so relaxing the bound never changes where the search
   490	    starts, only how far it may wander.
   491	    """
   492	    p = Parameters()
   493	
   494	    for name, lo_b, hi_b in model.shared_fwhm_params:
   495	        p.add(name, value=0.5 * (lo_b + hi_b), min=lo_b, max=hi_b)
   496	
   497	    if y_net is not None and len(y_net) > 0:
   498	        y_peak = max(float(np.max(y_net)), 1.0)
   499	    else:
   500	        y_peak = 1.0e5
   501	
   502	    def _amp_bounds(window: tuple[float, float]) -> tuple[float, float]:
   503	        if x is not None and y_net is not None:
   504	            init = _peak_estimate_in_window(x, y_net, window)
   505	            return init, max(2.0 * y_peak, 10.0 * init, 1.0)
   650	    lmfit_result: Optional[ModelResult] = None
   651	    background: Optional[np.ndarray] = None
   652	    boundary_hits: list[str] = field(default_factory=list)
   653	
   654	
   655	def _extract_fitted_components(
   656	    result: ModelResult, model: CandidateModel
   657	) -> list[FittedComponent]:
   658	    out: list[FittedComponent] = []
   659	    for slot in model.slots:
   660	        prefix = _slot_prefix(slot.role)
   661	        pars = result.params
   662	        try:
   663	            center = float(pars[f"{prefix}center"].value)
   664	            amplitude = float(pars[f"{prefix}amplitude"].value)
   665	            fwhm = float(pars[f"{prefix}{_width_param(slot.line_shape)}"].value)
   666	        except KeyError:
   667	            continue
   668	        shape_params = {}
   669	        for name, _, _, _ in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
   670	            par = pars.get(f"{prefix}{name}")
   671	            if par is not None:
   672	                shape_params[name] = float(par.value)
   673	        if slot.line_shape is LineShape.DS_G:
   674	            shape_params["m_gauss"] = fwhm
   675	        out.append(FittedComponent(
   676	            slot_role=slot.role, position=center, fwhm=fwhm,
   677	            amplitude=amplitude, shape_params=shape_params,
   678	            line_shape=slot.line_shape,
   679	        ))
   680	    return out
   681	
   682	
   683	# Shape-parameter names allowed to saturate at bounds per lineshape (shape
   684	# preference, not pathology).  Width-like params are NOT excluded.
   685	_BOUNDARY_EXCLUDED: dict[LineShape, frozenset[str]] = {
   686	    LineShape.GAUSSIAN: frozenset(),
   687	    LineShape.LORENTZIAN: frozenset(),
   688	    LineShape.PSEUDO_VOIGT: frozenset({"gl_ratio"}),
   689	    LineShape.ASYM_GL: frozenset({"gl_ratio", "asymmetry"}),
   690	    LineShape.DS: frozenset({"alpha", "gamma_asym"}),

2026-07-20T19:23:43.623953Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The shell cannot create here-doc temp files in this read-only profile, so I’m switching to `python -c` for the direct checks. That still lets me import the repo and evaluate the live logic without modifying files.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python -c '
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.engine import FittedComponent, _unphysical_width_flags, FWHM_MAX_ORDINARY_EV
from autofit.regions.c1s import FWHM_RANGE_CONTAMINATION, FWHM_MIXED_CEILING_NUMERIC_GUARD_EV, C1sModule
phase = Phase(id=\"sample\", material_class=MaterialClass.MIXED, regions=(\"C 1s\",))
g = resolve([phase], \"C 1s\")
rec = next(r for r in C1sModule().provenance() if r[\"constant\"] == \"mixed_material_class_width_relaxation\")
print(\"ordinary cap\", FWHM_MAX_ORDINARY_EV)
print(\"mixed ceiling\", FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
print(\"actual relaxation value has digit?\", any(ch.isdigit() for ch in rec[\"value\"]))
print(\"bad string has digit?\", any(ch.isdigit() for ch in \"relax to 3.5 eV based on our spectra\"))
misses = []
checks = []
for cand in g.candidates:
    comps = []
    roles = []
    for slot in cand.slots:
        if slot.fwhm_range == (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV) and slot.broad_justification is None:
            comps.append(FittedComponent(slot_role=slot.role, position=0.0, fwhm=8.0, amplitude=1e4, shape_params={}, line_shape=slot.line_shape))
            roles.append(slot.role)
    if not comps:
        continue
    flags = _unphysical_width_flags(comps, cand)
    flagged = {f.split(\":\", 1)[0] for f in flags}
    checks.append((cand.name, tuple(roles), tuple(sorted(flagged))))
    missing = set(roles) - flagged
    if missing:
        misses.append((cand.name, sorted(missing), flags))
print(\"wide-slot candidates checked\", len(checks))
print(\"misses\", misses)
for name, roles, flagged in checks:
    if \"linked\" in name:
        print(name, \"roles=\", roles, \"flagged=\", flagged)
'" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

2026-07-20T19:23:58.163176Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c '
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.engine import FittedComponent, _unphysical_width_flags, FWHM_MAX_ORDINARY_EV
from autofit.regions.c1s import FWHM_RANGE_CONTAMINATION, FWHM_MIXED_CEILING_NUMERIC_GUARD_EV, C1sModule
phase = Phase(id=\"sample\", material_class=MaterialClass.MIXED, regions=(\"C 1s\",))
g = resolve([phase], \"C 1s\")
rec = next(r for r in C1sModule().provenance() if r[\"constant\"] == \"mixed_material_class_width_relaxation\")
print(\"ordinary cap\", FWHM_MAX_ORDINARY_EV)
print(\"mixed ceiling\", FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
print(\"actual relaxation value has digit?\", any(ch.isdigit() for ch in rec[\"value\"]))
print(\"bad string has digit?\", any(ch.isdigit() for ch in \"relax to 3.5 eV based on our spectra\"))
misses = []
checks = []
for cand in g.candidates:
    comps = []
    roles = []
    for slot in cand.slots:
        if slot.fwhm_range == (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV) and slot.broad_justification is None:
            comps.append(FittedComponent(slot_role=slot.role, position=0.0, fwhm=8.0, amplitude=1e4, shape_params={}, line_shape=slot.line_shape))
            roles.append(slot.role)
    if not comps:
        continue
    flags = _unphysical_width_flags(comps, cand)
    flagged = {f.split(\":\", 1)[0] for f in flags}
    checks.append((cand.name, tuple(roles), tuple(sorted(flagged))))
    missing = set(roles) - flagged
    if missing:
        misses.append((cand.name, sorted(missing), flags))
print(\"wide-slot candidates checked\", len(checks))
print(\"misses\", misses)
for name, roles, flagged in checks:
    if \"linked\" in name:
        print(name, \"roles=\", roles, \"flagged=\", flagged)
'" in /Users/skyefortier/xps-verify
 exited 1 in 173ms:
Traceback (most recent call last):
  File "<string>", line 3, in <module>
  File "/Users/skyefortier/xps-verify/autofit/engine.py", line 38, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

2026-07-20T19:24:11.368470Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
System `python3` lacks the app dependencies (`lmfit`), so direct engine imports fail there. I’m checking for a local virtualenv or project runner before falling back to close-reading plus dependency-free imports.
exec
/bin/zsh -lc "rg --files -g 'pyproject.toml' -g 'requirements*.txt' -g 'Pipfile' -g 'poetry.lock' -g 'uv.lock' -g '.venv/**' -g 'venv/**'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
requirements-dev.txt
requirements.txt

exec
/bin/zsh -lc "find . -maxdepth 3 \\( -name python -o -name pytest \\) -type f" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
exec
/bin/zsh -lc 'ls -la' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
total 560
drwxr-xr-x   29 skyefortier  staff    928 Jul 20 00:14 .
drwxr-xr-x+  74 skyefortier  staff   2368 Jul 20 13:20 ..
-rw-r--r--    1 skyefortier  staff     61 Jul 10 15:28 .git
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 .github
-rw-r--r--    1 skyefortier  staff    111 Jul 10 15:28 .gitignore
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 .impeccable
drwxr-xr-x    6 skyefortier  staff    192 Jul 10 19:53 .pytest_cache
drwxr-xr-x   27 skyefortier  staff    864 Jul 16 12:39 .stage9
-rw-r--r--    1 skyefortier  staff  20250 Jul 10 15:28 CLAUDE.md
-rw-r--r--    1 skyefortier  staff   2656 Jul 10 15:28 DEPLOY.md
-rw-r--r--    1 skyefortier  staff   8758 Jul 10 15:28 DESIGN.md
-rw-r--r--    1 skyefortier  staff   2735 Jul 10 15:28 PRODUCT.md
drwxr-xr-x    7 skyefortier  staff    224 Jul 20 00:14 __pycache__
-rw-r--r--    1 skyefortier  staff  52624 Jul 20 00:14 app.py
drwxr-xr-x   20 skyefortier  staff    640 Jul 20 12:32 autofit
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 data
drwxr-xr-x    6 skyefortier  staff    192 Jul 10 15:28 docs
-rw-r--r--    1 skyefortier  staff  56830 Jul 17 16:38 fitting.py
-rw-r--r--    1 skyefortier  staff  19994 Jul 10 15:28 parser.py
-rw-r--r--    1 skyefortier  staff    319 Jul 10 15:28 requirements-dev.txt
-rw-r--r--    1 skyefortier  staff    446 Jul 10 15:28 requirements.txt
drwxr-xr-x   22 skyefortier  staff    704 Jul 10 21:01 scripts
drwxr-xr-x    3 skyefortier  staff     96 Jul 10 15:28 static
drwxr-xr-x    4 skyefortier  staff    128 Jul 20 11:31 templates
drwxr-xr-x   39 skyefortier  staff   1248 Jul 20 00:13 tests
drwxr-xr-x  141 skyefortier  staff   4512 Jul 20 13:19 uploads
-rw-r--r--    1 skyefortier  staff   6062 Jul 10 15:28 vgd_parser.py
-rw-r--r--    1 skyefortier  staff  68252 Jul 10 15:28 xps-fitting-tool.html
-rw-r--r--    1 skyefortier  staff  18124 Jul 10 15:28 xps_reference.py

2026-07-20T19:24:18.990222Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
I can import the grammar/C 1s module without `lmfit`, so I’ll still do an executable enumeration of the candidate slots and implement the old/new width-rule predicates locally. That won’t exercise `rank_and_filter`, but it directly verifies the shared-width slot coverage and the old-rule failure condition.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c '
from autofit.grammar import MaterialClass, Phase, resolve
from autofit.regions.c1s import FWHM_RANGE_CONTAMINATION, FWHM_MIXED_CEILING_NUMERIC_GUARD_EV, C1sModule
FWHM_MAX_ORDINARY_EV = 2.0
phase = Phase(id=\"sample\", material_class=MaterialClass.MIXED, regions=(\"C 1s\",))
g = resolve([phase], \"C 1s\")
rec = next(r for r in C1sModule().provenance() if r[\"constant\"] == \"mixed_material_class_width_relaxation\")
print(\"actual relaxation value:\", rec[\"value\"])
print(\"actual relaxation value has digit?\", any(ch.isdigit() for ch in rec[\"value\"]))
print(\"bad string has digit?\", any(ch.isdigit() for ch in \"relax to 3.5 eV based on our spectra\"))
misses_new = []
old_exemptions = []
linked = []
for cand in g.candidates:
    roles = []
    for slot in cand.slots:
        if slot.fwhm_range == (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV) and slot.broad_justification is None:
            roles.append(slot.role)
            declared_hi = slot.fwhm_range[1]
            old_vouched = declared_hi > FWHM_MAX_ORDINARY_EV
            new_vouched = slot.broad_justification is not None
            old_flags = (not old_vouched) and (8.0 >= FWHM_MAX_ORDINARY_EV - 0.01 * (declared_hi - slot.fwhm_range[0]))
            new_flags = (not new_vouched) and (8.0 >= FWHM_MAX_ORDINARY_EV - 0.01 * (declared_hi - slot.fwhm_range[0]))
            if not new_flags:
                misses_new.append((cand.name, slot.role))
            if not old_flags:
                old_exemptions.append((cand.name, slot.role, slot.fwhm_range, slot.broad_justification))
    if roles and \"linked\" in cand.name:
        linked.append((cand.name, cand.shared_fwhm_params, tuple(roles), tuple((s.role, s.fwhm_linked_to) for s in cand.slots if s.role in roles)))
print(\"new-rule misses for 8eV widened unvouched slots\", misses_new)
print(\"old-rule exemptions count\", len(old_exemptions))
print(\"old-rule A1 contamination_CO exempt?\", any(n == \"A1_linked\" and r == \"contamination_CO\" for n, r, *_ in old_exemptions))
for item in linked:
    print(\"linked\", item)
'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-CH2aHgkm' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-SHsSLw2M' (errno=Operation not permitted)
actual relaxation value: under MaterialClass.MIXED (analyte embedded in a different matrix), the contamination/adventitious FWHM ceiling's single-species-homogeneity assumption is withdrawn and the ceiling is relaxed toward unconstrained; no new position or width value is asserted — position windows and every other FWHM family are unchanged
actual relaxation value has digit? False
bad string has digit? True
new-rule misses for 8eV widened unvouched slots []
old-rule exemptions count 62
old-rule A1 contamination_CO exempt? True
linked ('A1_linked', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO',), (('contamination_CO', 'shared_contamination_fwhm'),))
linked ('A2_linked', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO', 'contamination_C=O'), (('contamination_CO', 'shared_contamination_fwhm'), ('contamination_C=O', 'shared_contamination_fwhm')))
linked ('A3_linked', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO', 'contamination_C=O', 'contamination_OC=O'), (('contamination_CO', 'shared_contamination_fwhm'), ('contamination_C=O', 'shared_contamination_fwhm'), ('contamination_OC=O', 'shared_contamination_fwhm')))
linked ('A1_linked_offset', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO',), (('contamination_CO', 'shared_contamination_fwhm'),))
linked ('A2_linked_offset', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO', 'contamination_C=O'), (('contamination_CO', 'shared_contamination_fwhm'), ('contamination_C=O', 'shared_contamination_fwhm')))
linked ('A3_linked_offset', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO', 'contamination_C=O', 'contamination_OC=O'), (('contamination_CO', 'shared_contamination_fwhm'), ('contamination_C=O', 'shared_contamination_fwhm'), ('contamination_OC=O', 'shared_contamination_fwhm')))
linked ('AG1_linked', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO',), (('contamination_CO', 'shared_contamination_fwhm'),))
linked ('AG2_linked', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO', 'contamination_C=O'), (('contamination_CO', 'shared_contamination_fwhm'), ('contamination_C=O', 'shared_contamination_fwhm')))
linked ('AG3_linked', (('shared_contamination_fwhm', 0.8, 15.0),), ('contamination_CO', 'contamination_C=O', 'contamination_OC=O'), (('contamination_CO', 'shared_contamination_fwhm'), ('contamination_C=O', 'shared_contamination_fwhm'), ('contamination_OC=O', 'shared_contamination_fwhm')))
linked ('B2_linked', (), ('main_aliphatic', 'contamination_CO', 'contamination_C=O'), (('main_aliphatic', None), ('contamination_CO', 's_main_aliphatic_fwhm'), ('contamination_C=O', 's_main_aliphatic_fwhm')))
linked ('B3_linked', (), ('main_aliphatic', 'contamination_CO', 'contamination_C=O', 'contamination_OC=O'), (('main_aliphatic', None), ('contamination_CO', 's_main_aliphatic_fwhm'), ('contamination_C=O', 's_main_aliphatic_fwhm'), ('contamination_OC=O', 's_main_aliphatic_fwhm')))

2026-07-20T19:24:41.162960Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The executable enumeration found no current-rule misses: every MIXED C 1s slot with the widened `(0.8, 15.0)` unvouched width would flag at 8 eV. Under the old numeric-vouch rule, the same slots are all exempted, including the exact `A1_linked/contamination_CO` regression case.
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '1150,1275p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
  1150	    # understating them against the full nominal n_refits.
  1151	    n_attempted: int = 0
  1152	    timed_out: bool = False
  1153	
  1154	    @property
  1155	    def min_persistence(self) -> float:
  1156	        if not self.per_slot:
  1157	            return 0.0
  1158	        return min(s.persistence for s in self.per_slot.values())
  1159	
  1160	
  1161	def run_stability_analysis(
  1162	    x: np.ndarray,
  1163	    y: np.ndarray,
  1164	    weights: np.ndarray,
  1165	    model: CandidateModel,
  1166	    primary_fit: FitOutcome,
  1167	    noise_floor: float,
  1168	    n_refits: int = 20,
  1169	    rng_seed: int = 0,
  1170	    fixed_param_values: Optional[dict[str, float]] = None,
  1171	    deadline: Optional[float] = None,
  1172	    fit_full_window: bool = False,
  1173	) -> ModelStability:
  1174	    """
  1175	    ``deadline`` is an absolute ``time.perf_counter()`` timestamp (set by
  1176	    the caller from CANDIDATE_TIMEOUT_SEC) shared across this candidate's
  1177	    primary fit + all its refits. Once passed, remaining refits are
  1178	    skipped — not run and not counted as failures — so one candidate stuck
  1179	    in a slow-but-nfev-capped region can't consume the rest of the request.
  1180	    """
  1181	    rng = np.random.default_rng(rng_seed)
  1182	    pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
  1183	    fw: dict[str, list[float]] = {s.role: [] for s in model.slots}
  1184	    am: dict[str, list[float]] = {s.role: [] for s in model.slots}
  1185	    occupied: dict[str, int] = {s.role: 0 for s in model.slots}
  1186	    n_converged = 0
  1187	    n_with_orphans = 0
  1188	    # Same widened bounds every refit was actually built with (constant
  1189	    # across this candidate's whole stability pass) — identity-matching
  1190	    # must agree with the bound the fit was allowed to search, or a
  1191	    # component correctly placed outside its ORIGINAL window becomes an
  1192	    # orphan here, tanking persistence for the very slot this option
  1193	    # exists to rescue (Codex-caught, see _effective_be_window).
  1194	    bound_overrides = _full_window_bound_overrides(model, x) if fit_full_window else None
  1195	
  1196	    # Data-informed perturbation seeds (see perturb_initial_params): reuse
  1197	    # the primary fit's background rather than recomputing per refit.
  1198	    bg = primary_fit.background
  1199	    y_net = y - bg if bg is not None else None
  1200	
  1201	    best_outcome: Optional[FitOutcome] = None
  1202	    refit_chis: list[float] = [float(primary_fit.weighted_chi_sq)]
  1203	    n_attempted = 0
  1204	    timed_out = False
  1205	    for _ in range(n_refits):
  1206	        if deadline is not None and time.perf_counter() >= deadline:
  1207	            timed_out = True
  1208	            log.warning(
  1209	                "run_stability_analysis: candidate %s hit its %.0fs budget "
  1210	                "after %d/%d refits — remaining refits skipped",
  1211	                model.name, CANDIDATE_TIMEOUT_SEC, n_attempted, n_refits,
  1212	            )
  1213	            break
  1214	        n_attempted += 1
  1215	        seed = int(rng.integers(0, 2**31 - 1))
  1216	        init = perturb_initial_params(model, seed=seed, x=x, y_net=y_net,
  1217	                                      fit_full_window=fit_full_window)
  1218	        if fixed_param_values:
  1219	            # bound-fixed refit stability: the constrained parameters stay
  1220	            # fixed at their bounds in every multi-start refit
  1221	            for pname, val in fixed_param_values.items():
  1222	                if pname in init:
  1223	                    init[pname].set(value=float(val), vary=False)
  1224	        outcome = fit_candidate(x, y, weights, model, initial_params=init)
  1225	        if not outcome.converged:
  1226	            continue
  1227	        n_converged += 1
  1228	        refit_chis.append(float(outcome.weighted_chi_sq))
  1229	        if best_outcome is None or outcome.weighted_chi_sq < best_outcome.weighted_chi_sq:
  1230	            best_outcome = outcome
  1231	        slot_map = match_components_to_slots(outcome.components, model, noise_floor,
  1232	                                            bound_overrides=bound_overrides)
  1233	        if slot_map.pop("__orphans__", []):
  1234	            n_with_orphans += 1
  1235	        for role, comp in slot_map.items():
  1236	            if comp is None:
  1237	                continue
  1238	            occupied[role] += 1
  1239	            pos[role].append(comp.position)
  1240	            fw[role].append(comp.fwhm)
  1241	            am[role].append(comp.amplitude)
  1242	
  1243	    def _med(v):  # median or None
  1244	        return float(np.median(v)) if v else None
  1245	
  1246	    def _mad(v):
  1247	        if not v:
  1248	            return None
  1249	        arr = np.asarray(v)
  1250	        return float(np.median(np.abs(arr - np.median(arr))))
  1251	
  1252	    per_slot = {
  1253	        role: SlotStability(
  1254	            role=role,
  1255	            persistence=occupied[role] / max(n_attempted, 1),
  1256	            position_median=_med(pos[role]), position_mad=_mad(pos[role]),
  1257	            fwhm_median=_med(fw[role]), fwhm_mad=_mad(fw[role]),
  1258	            amplitude_median=_med(am[role]), amplitude_mad=_mad(am[role]),
  1259	        )
  1260	        for role in occupied
  1261	    }
  1262	    best_chi = min(refit_chis)
  1263	    basin_support = sum(1 for c in refit_chis
  1264	                        if c <= best_chi * (1.0 + BASIN_SUPPORT_RTOL))
  1265	    return ModelStability(
  1266	        per_slot=per_slot,
  1267	        orphan_rate=n_with_orphans / max(n_attempted, 1),
  1268	        convergence_rate=n_converged / max(n_attempted, 1),
  1269	        best_outcome=best_outcome,
  1270	        best_basin_support=basin_support,
  1271	        n_attempted=n_attempted,
  1272	        timed_out=timed_out,
  1273	    )
  1274	
  1275	

exec
/bin/zsh -lc 'node --test tests/js/fp_material_mixed.test.js' in /Users/skyefortier/xps-verify
 succeeded in 136ms:
# Subtest: FP_STRINGS.materials.mixed has a clear, non-bare label
ok 1 - FP_STRINGS.materials.mixed has a clear, non-bare label
  ---
  duration_ms: 0.962796
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint is advisory, never claims correction
ok 2 - FP_STRINGS.materials.mixed hint is advisory, never claims correction
  ---
  duration_ms: 0.29028
  type: 'test'
  ...
# Subtest: FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
ok 3 - FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
  ---
  duration_ms: 0.191151
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
ok 4 - FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
  ---
  duration_ms: 0.203324
  type: 'test'
  ...
1..4
# tests 4
# suites 0
# pass 4
# fail 0
# cancelled 0
# skipped 0
# todo 0
# duration_ms 90.35447

2026-07-20T19:24:50.530418Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc 'rg -n "def rank_and_filter|conditional_reason|unphysical_widths|no_clean_survivor|filtered_out" autofit/engine.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
83:# candidate; the result carries conditional_reason='decisive_override'.
112:# the physical limit and the result is flagged (unphysical_widths →
1437:    unphysical_widths: list[str] = field(default_factory=list)
1586:    filtered_out: list[tuple[ModelReport, str]]
1592:    #   'no_clean_survivor'  — nothing passed plausibility cleanly; the
1601:    conditional_reason: Optional[str] = None
1642:def rank_and_filter(
1660:    filtered_out: list[tuple[ModelReport, str]] = []
1667:        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
1672:            filtered_out.append((r, f"plausibility: {r.plausibility}"))
1679:            filtered_out.append((r, f"stability: active min persistence "
1685:    conditional_reason = None
1689:        conditional_reason = "no_clean_survivor"
1712:            conditional_reason = "unstable_last_resort"
1737:        filtered_out=filtered_out, ambiguous_pairs=ambiguous,
1738:        conditional=conditional, conditional_reason=conditional_reason,
2217:    # (unphysical_widths + the fwhm@max boundary hit → CONDITIONAL) rather
2318:            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
2457:            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
2490:    pool = [r for r, why in result.filtered_out
2513:        result.conditional_reason = "decisive_override"
2830:                unphysical_widths=_unphysical_width_flags(primary.components, model),
2984:        # filtered_out — flagging the original as "buried" would name the
2994:        for rep, why in result.filtered_out:

2026-07-20T19:24:54.694381Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '1428,1445p;1578,1742p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
  1428	
  1429	
  1430	# ─────────────────────────────────────────────────────────────────────────────
  1431	# Reports, BIC*, ranking
  1432	# ─────────────────────────────────────────────────────────────────────────────
  1433	
  1434	@dataclass
  1435	class PlausibilityFlags:
  1436	    boundary_hits: list[str] = field(default_factory=list)
  1437	    unphysical_widths: list[str] = field(default_factory=list)
  1438	    orphan_peaks: bool = False
  1439	
  1440	
  1441	@dataclass
  1442	class ProposedPeakReport:
  1443	    role: str
  1444	    detection_windows: list[str]
  1445	    detection_energy: float
  1578	        return float("inf")
  1579	    return n * np.log(rss / n) + fit.n_params * np.log(n)
  1580	
  1581	
  1582	@dataclass
  1583	class ComparisonResult:
  1584	    reports: list[ModelReport]
  1585	    survivors: list[ModelReport]
  1586	    filtered_out: list[tuple[ModelReport, str]]
  1587	    ambiguous_pairs: list[tuple[str, str, str]]
  1588	    non_converged: list[tuple[CandidateModel, FitOutcome]] = field(default_factory=list)
  1589	    cross_candidate_coincidences: list[CoincidenceReport] = field(default_factory=list)
  1590	    proposal_pass_timings: list[ProposalPassTiming] = field(default_factory=list)
  1591	    # True when the leading survivor is constraint-limited.  Reason:
  1592	    #   'no_clean_survivor'  — nothing passed plausibility cleanly; the
  1593	    #                          stable-but-boundary-limited tier is ranked.
  1594	    #   'decisive_override'  — clean survivors exist but a bound-fixed refit
  1595	    #                          of a boundary-limited candidate dominates them
  1596	    #                          (see CONDITIONAL_OVERRIDE_DELTA_BIC); clean
  1597	    #                          survivors remain as ranked alternatives.
  1598	    # Never silent (spec stance: best-evidenced proposal + honest
  1599	    # uncertainty, not a dead end).
  1600	    conditional: bool = False
  1601	    conditional_reason: Optional[str] = None
  1602	    # The ambiguity threshold ACTUALLY used for ambiguous_pairs — consumers
  1603	    # (criteria panel) must reuse it so the payload can never disagree with
  1604	    # the ranking (Codex Stage-2 re-review finding #1).
  1605	    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY
  1606	    # A filtered candidate whose BIC* beats the winner's by more than the
  1607	    # decisive threshold — {name, bic_star, delta_bic_vs_winner,
  1608	    # filter_reason} or None.  Stress-suite finding 0: evidence burial must
  1609	    # be machine-visible at the result level.
  1610	    filtered_dominant_alternative: Optional[dict] = None
  1611	    # The weighted-χ² criterion (consistent with the fit weights) prefers a
  1612	    # DIFFERENT survivor than the ranking's RSS-form BIC* — {rss_bic_top,
  1613	    # weighted_bic_top, note} or None (BIC/IC math review blocker:
  1614	    # selection must not silently rest on a likelihood the fits reject).
  1615	    weighted_ic_disagreement: Optional[dict] = None
  1616	    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
  1617	    # evaluating every candidate in the grammar. The candidates evaluated so
  1618	    # far are still ranked/reported normally (best-so-far) — this only flags
  1619	    # that the comparison is partial, so a slow/pathological spectrum
  1620	    # returns an honest incomplete result instead of a request timeout.
  1621	    analysis_truncated: bool = False
  1622	    n_candidates_evaluated: int = 0
  1623	    n_candidates_total: int = 0
  1624	    # Pre-fit out-of-grammar dominant seeding (unit F1): the detected
  1625	    # features every candidate was augmented with, incl. the gate values
  1626	    # (UNVERIFIED tunables) — empty when detection found nothing, in which
  1627	    # case the candidate set ran unmodified.
  1628	    preseeded_features: list[dict] = field(default_factory=list)
  1629	    # Two-phase sweep record (unit F3) — None when the classic single-phase
  1630	    # path ran (candidate set ≤ SCREEN_TOP_K).  Otherwise every candidate's
  1631	    # screen outcome: {name, converged, bic, selected} — screened-out
  1632	    # candidates are visible here and can never be survivors.
  1633	    screen: Optional[list[dict]] = None
  1634	    # Candidate-generation layer (autofit.candidates): the OVERCOMPLETE,
  1635	    # provenance-tagged detection pool payload — every feature any source
  1636	    # (local_max / curvature_shoulder / residual_gap / grammar) proposed,
  1637	    # with per-feature gate outcomes and seeding decisions.  None when the
  1638	    # layer did not run (enable_preseed=False or no candidates).
  1639	    candidate_pool: Optional[dict] = None
  1640	
  1641	
  1642	def rank_and_filter(
  1643	    reports: list[ModelReport],
  1644	    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
  1645	    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY,
  1646	    allow_conditional: bool = True,
  1647	    allow_last_resort: bool = False,
  1648	) -> ComparisonResult:
  1649	    """
  1650	    Filter (plausibility, active persistence) then rank (χ²ᵣ, BIC*).
  1651	
  1652	    Two-tier semantics (departure from fitalg, which returned zero survivors
  1653	    whenever every candidate had any boundary hit — routine on real composite
  1654	    samples): when NO candidate passes plausibility cleanly but some are
  1655	    otherwise stable, those are ranked as a CONDITIONAL tier with
  1656	    ``result.conditional = True`` and every violation preserved.  Stability
  1657	    failures are never promoted — an unstable fit is pathology, not a
  1658	    constraint conflict.
  1659	    """
  1660	    filtered_out: list[tuple[ModelReport, str]] = []
  1661	    survivors: list[ModelReport] = []
  1662	    conditional_pool: list[ModelReport] = []
  1663	
  1664	    for r in reports:
  1665	        active_min = r.active_min_persistence
  1666	        stable = active_min >= persistence_threshold
  1667	        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
  1668	                or r.plausibility.orphan_peaks:
  1669	            # orphan_peaks included (Codex Stage-2 re-review finding #3):
  1670	            # refits repeatedly producing unmatched components is a
  1671	            # plausibility violation, not clean-survivor material.
  1672	            filtered_out.append((r, f"plausibility: {r.plausibility}"))
  1673	            if stable:
  1674	                conditional_pool.append(r)
  1675	            continue
  1676	        if not stable:
  1677	            absent_roles = [a.role for a in r.absent_slots]
  1678	            extra = f"  (absent slots excluded: {absent_roles})" if absent_roles else ""
  1679	            filtered_out.append((r, f"stability: active min persistence "
  1680	                                    f"{active_min:.2f} < {persistence_threshold}{extra}"))
  1681	            continue
  1682	        survivors.append(r)
  1683	
  1684	    conditional = False
  1685	    conditional_reason = None
  1686	    if allow_conditional and conditional_pool and not survivors:
  1687	        survivors = conditional_pool
  1688	        conditional = True
  1689	        conditional_reason = "no_clean_survivor"
  1690	    elif allow_conditional and allow_last_resort and not survivors and reports:
  1691	        # LAST-RESORT tier (Stage-2, 2026-07-10; measured on real low-res
  1692	        # Fe 2p): fires ONLY when the caller says detection found real
  1693	        # structure (allow_last_resort = detection seeds exist) — its job
  1694	        # is rescuing DETECTED structure from selection instability, never
  1695	        # forcing an answer on featureless data (a flat-noise grammar fit
  1696	        # can converge; the honest result there stays no-survivor).
  1697	        # Every candidate failed BOTH tiers — typically cross-refit
  1698	        # label instability (orphan_peaks) on heavily-overlapped low-res
  1699	        # structure.  For a suggest-a-profile tool an EMPTY answer is the
  1700	        # worst answer: emit the single best CONVERGED model, loudly
  1701	        # flagged unstable.  This tier exists only when clean and
  1702	        # conditional are BOTH empty — stability failures are still never
  1703	        # preferred over anything (the original design rule stands).
  1704	        viable = [r for r in reports
  1705	                  if r.primary_fit.converged
  1706	                  and np.isfinite(r.bic_adjusted)]
  1707	        if viable:
  1708	            best = min(viable,
  1709	                       key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))
  1710	            survivors = [best]
  1711	            conditional = True
  1712	            conditional_reason = "unstable_last_resort"
  1713	    # NOTE: the decisive-override path (clean survivors exist but a
  1714	    # bound-fixed refit of a conditional candidate dominates) lives in
  1715	    # compare_models — it needs the spectrum to refit; rank_and_filter is
  1716	    # pure ranking.
  1717	
  1718	    # BIC* is the ranking default (spec §6); χ²ᵣ breaks ties only.  fitalg
  1719	    # ranked (χ²ᵣ, BIC*) — spec-noncompliant, changed per Codex finding #3.
  1720	    survivors.sort(key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))
  1721	
  1722	    ambiguous: list[tuple[str, str, str]] = []
  1723	    for i in range(len(survivors)):
  1724	        for j in range(i + 1, len(survivors)):
  1725	            a, b = survivors[i], survivors[j]
  1726	            if abs(a.bic_adjusted - b.bic_adjusted) <= bic_ambiguity_threshold \
  1727	               and a.model.n_components != b.model.n_components:
  1728	                diff = {s.role for s in a.model.slots} ^ {s.role for s in b.model.slots}
  1729	                ambiguous.append((
  1730	                    a.model.name, b.model.name,
  1731	                    f"Indistinguishable on fit quality and BIC* "
  1732	                    f"(ΔBIC*={abs(a.bic_adjusted - b.bic_adjusted):.2f}); "
  1733	                    f"structural difference: {diff}",
  1734	                ))
  1735	    return ComparisonResult(
  1736	        reports=reports, survivors=survivors,
  1737	        filtered_out=filtered_out, ambiguous_pairs=ambiguous,
  1738	        conditional=conditional, conditional_reason=conditional_reason,
  1739	        bic_ambiguity_threshold=bic_ambiguity_threshold,
  1740	    )
  1741	
  1742	

2026-07-20T19:24:58.231198Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The UI test passes under Node. Python test execution itself is blocked by the environment, not by test failures: the available `python3` has neither `pytest` nor `lmfit`, so I’m treating the Python portions as close-read plus lightweight grammar execution where possible.
exec
/bin/zsh -lc "rg -n \"material_class|MaterialClass\\.MIXED|phase\\.material_class|_contamination_fwhm_range\" autofit app.py templates tests -g '*.py' -g '*.html' -g '*.js'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:243:    mc_raw = body.get("material_class", "")
app.py:247:        raise _AnalyzeError(f"Unknown material_class '{mc_raw}'")
app.py:289:                      material_class=mclass,
app.py:881:            "material_classes": [m.value for m in MaterialClass],
app.py:897:          "material_class": "conductor" | "insulator" | "semiconductor" | "mixed",
tests/test_api_analyze_progress.py:60:    "session_id": sid, "material_class": "insulator",
tests/test_api_analyze_progress.py:164:    """Cheap, request-shape validation (session/region/roi/material_class)
tests/test_api_analyze_progress.py:168:        "session_id": "not-a-uuid", "material_class": "insulator",
templates/index.html:13430:  mat.innerHTML = _fpMeta.material_classes
templates/index.html:13899:      material_class: document.getElementById('fp-material').value,
tests/test_api_analyze.py:53:    assert set(meta["material_classes"]) == {"conductor", "insulator",
tests/test_api_analyze.py:65:        "session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:96:        "session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:116:    ({"material_class": "plasma"}, "material_class"),
tests/test_api_analyze.py:126:    base = {"session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:137:        "session_id": "0" * 32, "material_class": "insulator",
tests/test_api_analyze.py:150:    base = {"session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:168:            "session_id": sid, "material_class": "insulator",
tests/test_api_analyze.py:175:def test_analyze_material_class_mixed_accepted(client):
tests/test_api_analyze.py:176:    """MaterialClass.MIXED (2026-07-20 unit) round-trips through the
tests/test_api_analyze.py:180:    tests/autofit/test_c1s_mixed_material_class.py, against C 1s)."""
tests/test_api_analyze.py:183:        "session_id": sid, "material_class": "mixed",
tests/test_api_analyze.py:192:def test_analyze_start_material_class_mixed_accepted(client):
tests/test_api_analyze.py:199:        "session_id": sid, "material_class": "mixed",
tests/test_api_analyze.py:208:def test_material_class_does_not_affect_charge_correction(client):
tests/test_api_analyze.py:214:    must be byte-identical regardless of material_class. material_class
tests/test_api_analyze.py:215:    only ever reaches Phase.material_class, consumed by grammar
tests/test_api_analyze.py:228:        {**base, "material_class": "conductor"}, upload_folder)
tests/test_api_analyze.py:230:        {**base, "material_class": "mixed"}, upload_folder)
autofit/grammar.py:88:    # tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction).
autofit/grammar.py:102:    material_class: MaterialClass
autofit/grammar.py:402:                f"{chosen.material_class.value}) — derived structure only")
autofit/grammar.py:436:            f"{slug}: phase {chosen.id!r} ({chosen.material_class.value}"
autofit/coverage.py:124:    "user-overridable: the declared Phase.material_class wins."
autofit/coverage.py:405:                   "Phase.material_class wins)"},
tests/test_api_analyze_coverage.py:81:        "session_id": sid, "material_class": "conductor",
tests/test_api_analyze_coverage.py:102:        "session_id": sid, "material_class": "insulator",
tests/test_api_fit_full_window_option.py:60:        "session_id": sid, "material_class": "insulator",
tests/test_api_fit_full_window_option.py:75:        "session_id": sid, "material_class": "insulator",
tests/autofit/test_b1s_cl2p_parity_gates.py:36:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_b1s_cl2p_parity_gates.py:38:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_structural_fallback.py:34:    return Phase(id="sample", material_class=MaterialClass(mc),
tests/autofit/test_structural_fallback.py:227:    p1 = Phase(id="a", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:229:    p2 = Phase(id="b", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:280:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:304:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:322:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:351:        "session_id": sid, "material_class": "insulator",
tests/autofit/test_structural_fallback.py:374:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_bayesian_u4f_unresolved_gate.py:37:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_stage2_rereview_findings.py:94:    pa = Phase(id="B-4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:96:    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:103:    pa = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_stage2_rereview_findings.py:105:    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:124:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_broad_justification.py:18:mixed_material_class_verdict_run{A,B}.md).
tests/autofit/test_broad_justification.py:42:_CONDUCTOR_C1S = Phase(id="s", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_broad_justification.py:44:_INSULATOR_B1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:46:_INSULATOR_CL2P = Phase(id="s", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:48:_INSULATOR_N1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:50:_INSULATOR_U4F = Phase(id="s", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:104:_U4F_PHASE = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_broad_justification.py:106:_N1S_PHASE = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_bayesian_real_gate.py:37:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_reference_bridge.py:271:    phase = Phase(id="s", material_class=MaterialClass("conductor"),
tests/autofit/test_reference_bridge.py:289:    phase2 = Phase(id="s", material_class=MaterialClass("conductor"),
autofit/regions/c1s.py:125:def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
autofit/regions/c1s.py:128:    if material_class is MaterialClass.MIXED:
autofit/regions/c1s.py:243:            {"constant": "mixed_material_class_width_relaxation",
autofit/regions/c1s.py:244:             "value": "under MaterialClass.MIXED (analyte embedded in a "
autofit/regions/c1s.py:306:        contam_fwhm = _contamination_fwhm_range(phase.material_class)
tests/autofit/test_methods_seam.py:9:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_u4f_parity_gate.py:30:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_u4f_parity_gate.py:32:BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_cl2p_freewidth.py:41:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_c1s_parity_gate.py:95:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_fit_physics_wiring.py:15:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_fit_physics_wiring.py:17:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_c1s_mixed_material_class.py:49:def _resolve(material_class):
tests/autofit/test_c1s_mixed_material_class.py:50:    phase = Phase(id="sample", material_class=material_class, regions=("C 1s",))
tests/autofit/test_c1s_mixed_material_class.py:66:@pytest.mark.parametrize("material_class", NON_MIXED)
tests/autofit/test_c1s_mixed_material_class.py:67:def test_non_mixed_candidate_pool_unchanged(material_class):
tests/autofit/test_c1s_mixed_material_class.py:71:    g = _resolve(material_class)
tests/autofit/test_c1s_mixed_material_class.py:77:            f"material_class {material_class}"
tests/autofit/test_c1s_mixed_material_class.py:81:@pytest.mark.parametrize("material_class", NON_MIXED)
tests/autofit/test_c1s_mixed_material_class.py:82:def test_non_mixed_candidate_names_unchanged(material_class):
tests/autofit/test_c1s_mixed_material_class.py:85:    non-MIXED material class (it always was -- material_class was
tests/autofit/test_c1s_mixed_material_class.py:88:    names_other = {c.name for c in _resolve(material_class).candidates}
tests/autofit/test_c1s_mixed_material_class.py:98:    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
tests/autofit/test_c1s_mixed_material_class.py:118:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:139:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:158:    rec = _by_constant(records, "mixed_material_class_width_relaxation")
tests/autofit/test_c1s_mixed_material_class.py:194:    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
tests/autofit/test_c1s_mixed_material_class.py:216:    g = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:251:    g = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:305:    g = _resolve(MaterialClass.MIXED)
tests/autofit/test_resolver.py:18:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_resolver.py:20:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_resolver.py:22:BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_resolver.py:84:        xe = Phase(id="x", material_class=MaterialClass.CONDUCTOR, regions=("Xe 3d",))
tests/autofit/test_resolver.py:131:    both = Phase(id="mix", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_resolver.py:158:    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
tests/autofit/test_resolver.py:159:    p2 = Phase(id="ph2", material_class=MaterialClass.SEMICONDUCTOR, regions=("Fk 2p",))
tests/autofit/test_resolver.py:183:    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
tests/autofit/test_candidate_pool_real_gate.py:86:    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
tests/autofit/test_candidate_pool_real_gate.py:226:    phase = Phase(id="sample", material_class=MaterialClass("conductor"),

exec
/bin/zsh -lc 'git diff --name-only bdc909a''^ bdc909a && git diff --name-only bdc909a''^ bdc909a -- autofit/engine.py autofit/grammar.py autofit/regions/c1s.py app.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-lbFaPNPr' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RpeCbXxy' (errno=Operation not permitted)
templates/index.html
tests/autofit/test_c1s_mixed_material_class.py
tests/js/fp_material_mixed.test.js
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-RAqau3K4' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-E8NDZnO4' (errno=Operation not permitted)

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from autofit.grammar import MaterialClass, Phase, resolve; regions=(\"U 4f\",\"Cl 2p\",\"B 1s\",\"N 1s\");
for region in regions:
    c=resolve([Phase(id=\"s\", material_class=MaterialClass.CONDUCTOR, regions=(region,))], region).candidates
    m=resolve([Phase(id=\"s\", material_class=MaterialClass.MIXED, regions=(region,))], region).candidates
    sig=lambda cs:[(cand.name, [(slot.role, slot.fwhm_range, slot.be_window, slot.linked_offset_range, slot.broad_justification) for slot in cand.slots], cand.shared_fwhm_params) for cand in cs]
    print(region, sig(c)==sig(m), len(c), len(m))'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-cckKxgnL' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-Tn19XAV6' (errno=Operation not permitted)
U 4f True 4 4
Cl 2p True 4 4
B 1s True 4 4
N 1s True 2 2

2026-07-20T19:25:23.692435Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
1. No BLOCKER/MAJOR/MINOR findings.

Verification notes:
- Red-green check holds by trace: old numeric rule exempts MIXED `(0.8, 15.0)` slots, so [test_c1s_mixed_material_class.py](/Users/skyefortier/xps-verify/tests/autofit/test_c1s_mixed_material_class.py:209) fails at `assert flags`, and the routing test fails at [line 318](/Users/skyefortier/xps-verify/tests/autofit/test_c1s_mixed_material_class.py:318).
- Shared-width paths check out. A/A-offset/AG linked slots all use the same unvouched widened range, and B-linked ties to unvouched `main_aliphatic`; all flag independently under the current rule in [engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:791).
- Provenance digit guard rejects `"relax to 3.5 eV based on our spectra"` and the current value at [c1s.py](/Users/skyefortier/xps-verify/autofit/regions/c1s.py:243) contains no digits.
- Frontend copy at [index.html](/Users/skyefortier/xps-verify/templates/index.html:13028) now scopes relaxation to C 1s contamination/adventitious widths and still says it does not correct charge uncertainty.
- Commit scope is exactly the claimed three files. No diff in `autofit/engine.py`, `autofit/grammar.py`, `autofit/regions/c1s.py`, or `app.py`.
- Ran `node --test tests/js/fp_material_mixed.test.js`: pass. Could not run pytest in this sandbox because system Python lacks `pytest` and `lmfit`.

VERDICT: GO
tokens used
74,959
1. No BLOCKER/MAJOR/MINOR findings.

Verification notes:
- Red-green check holds by trace: old numeric rule exempts MIXED `(0.8, 15.0)` slots, so [test_c1s_mixed_material_class.py](/Users/skyefortier/xps-verify/tests/autofit/test_c1s_mixed_material_class.py:209) fails at `assert flags`, and the routing test fails at [line 318](/Users/skyefortier/xps-verify/tests/autofit/test_c1s_mixed_material_class.py:318).
- Shared-width paths check out. A/A-offset/AG linked slots all use the same unvouched widened range, and B-linked ties to unvouched `main_aliphatic`; all flag independently under the current rule in [engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:791).
- Provenance digit guard rejects `"relax to 3.5 eV based on our spectra"` and the current value at [c1s.py](/Users/skyefortier/xps-verify/autofit/regions/c1s.py:243) contains no digits.
- Frontend copy at [index.html](/Users/skyefortier/xps-verify/templates/index.html:13028) now scopes relaxation to C 1s contamination/adventitious widths and still says it does not correct charge uncertainty.
- Commit scope is exactly the claimed three files. No diff in `autofit/engine.py`, `autofit/grammar.py`, `autofit/regions/c1s.py`, or `app.py`.
- Ran `node --test tests/js/fp_material_mixed.test.js`: pass. Could not run pytest in this sandbox because system Python lacks `pytest` and `lmfit`.

VERDICT: GO
