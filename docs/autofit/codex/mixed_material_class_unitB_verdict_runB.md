2026-07-20T19:22:43.292828Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 86 column 5
OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f80fb-0bd0-7fc0-b6c3-c462ed0c515a
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
I’ll review this as a targeted commit audit. I’ll inspect the diff and the relevant engine/region/API paths, then try to run the specific tests or a direct Python reproduction if the sandbox permits.
exec
/bin/zsh -lc 'git status --short --branch' in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'git show --stat --oneline --decorate --name-only bdc909a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YM0VpeSD' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-yYfWbp0i' (errno=Operation not permitted)
## feature-autofit-stage2...origin/feature-autofit-stage2
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XXrpmn3F' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-4kzpgS1F' (errno=Operation not permitted)
bdc909a fix(mixed): rebase MIXED's own 2 accepted Codex findings onto the corrected engine
templates/index.html
tests/autofit/test_c1s_mixed_material_class.py
tests/js/fp_material_mixed.test.js

exec
/bin/zsh -lc 'git show --find-renames --find-copies --stat bdc909a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-qX91yCR3' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-lvJd8X02' (errno=Operation not permitted)
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

 templates/index.html                           |  13 ++-
 tests/autofit/test_c1s_mixed_material_class.py | 147 +++++++++++++++++++++++++
 tests/js/fp_material_mixed.test.js             |  11 ++
 3 files changed, 165 insertions(+), 6 deletions(-)

codex
The commit scope matches the claimed three files by name. I’m going deeper now into the added tests and the implementation they’re meant to pin, especially the old-rule red/green path and the linked-family construction.
exec
/bin/zsh -lc 'rg -n "def _unphysical_width_flags|FWHM_MAX_ORDINARY_EV|broad_justification|_SHARED_CONTAM_FWHM|shared_fwhm_params|A3_linked|MG.*linked|mixed_material_class_width_relaxation|def provenance|material_class|corrected = energy - cc_shift" autofit tests templates app.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
app.py:243:    mc_raw = body.get("material_class", "")
app.py:247:        raise _AnalyzeError(f"Unknown material_class '{mc_raw}'")
app.py:253:    corrected = energy - cc_shift   # frontend getCorrectedBE convention
app.py:289:                      material_class=mclass,
app.py:881:            "material_classes": [m.value for m in MaterialClass],
app.py:897:          "material_class": "conductor" | "insulator" | "semiconductor" | "mixed",
autofit/candidates.py:73:# 2.4 eV (just above FWHM_MAX_ORDINARY_EV = 2.0, the engine's ordinary-
tests/test_api_analyze_coverage.py:81:        "session_id": sid, "material_class": "conductor",
tests/test_api_analyze_coverage.py:102:        "session_id": sid, "material_class": "insulator",
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
tests/test_api_analyze.py:180:    tests/autofit/test_c1s_mixed_material_class.py, against C 1s)."""
tests/test_api_analyze.py:183:        "session_id": sid, "material_class": "mixed",
tests/test_api_analyze.py:192:def test_analyze_start_material_class_mixed_accepted(client):
tests/test_api_analyze.py:199:        "session_id": sid, "material_class": "mixed",
tests/test_api_analyze.py:208:def test_material_class_does_not_affect_charge_correction(client):
tests/test_api_analyze.py:214:    must be byte-identical regardless of material_class. material_class
tests/test_api_analyze.py:215:    only ever reaches Phase.material_class, consumed by grammar
tests/test_api_analyze.py:228:        {**base, "material_class": "conductor"}, upload_folder)
tests/test_api_analyze.py:230:        {**base, "material_class": "mixed"}, upload_folder)
autofit/engine.py:116:FWHM_MAX_ORDINARY_EV = 2.0
autofit/engine.py:120:PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV
autofit/engine.py:494:    for name, lo_b, hi_b in model.shared_fwhm_params:
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
autofit/engine.py:1915:        shared_fwhm_params=base.shared_fwhm_params,
autofit/engine.py:2122:        shared_fwhm_params=base.shared_fwhm_params,
tests/test_api_fit_full_window_option.py:60:        "session_id": sid, "material_class": "insulator",
tests/test_api_fit_full_window_option.py:75:        "session_id": sid, "material_class": "insulator",
autofit/coverage.py:124:    "user-overridable: the declared Phase.material_class wins."
autofit/coverage.py:405:                   "Phase.material_class wins)"},
autofit/fit_physics.py:80:def provenance_entries(
autofit/grammar.py:88:    # tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction).
autofit/grammar.py:102:    material_class: MaterialClass
autofit/grammar.py:176:    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
autofit/grammar.py:181:    broad_justification: Optional[str] = None
autofit/grammar.py:199:    shared_fwhm_params: tuple[tuple[str, float, float], ...] = ()
autofit/grammar.py:402:                f"{chosen.material_class.value}) — derived structure only")
autofit/grammar.py:436:            f"{slug}: phase {chosen.id!r} ({chosen.material_class.value}"
autofit/grammar.py:570:            shared_rename = {name: f"{slug}__{name}" for name, _, _ in cand.shared_fwhm_params}
autofit/grammar.py:573:            for name, lo, hi in cand.shared_fwhm_params:
autofit/grammar.py:579:            shared_fwhm_params=tuple(shared),
autofit/grammar.py:595:    reconstruction this replaced was exactly how broad_justification got
autofit/grammar.py:599:    tests/autofit/test_broad_justification.py's
autofit/regions/__init__.py:31:    def provenance(self) -> list[dict]:
autofit/regions/n1s.py:49:    def provenance(self) -> list[dict]:
autofit/regions/n1s.py:80:            broad_justification=_justification,
autofit/regions/n1s.py:87:            broad_justification=_justification,
tests/autofit/test_bayesian_u4f_unresolved_gate.py:37:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_bayesian_real_gate.py:37:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
autofit/regions/b1s.py:63:    def provenance(self) -> list[dict]:
autofit/regions/b1s.py:96:                broad_justification=(
autofit/regions/cl2p.py:80:    def provenance(self) -> list[dict]:
autofit/regions/cl2p.py:147:                broad_justification=_empirical_justification,
autofit/regions/cl2p.py:164:                    broad_justification=_coster_kronig_justification,
autofit/regions/cl2p.py:175:                broad_justification=_empirical_justification,
autofit/regions/u4f.py:116:    def provenance(self) -> list[dict]:
autofit/regions/u4f.py:222:            broad_justification=_main_justification,
autofit/regions/u4f.py:231:            broad_justification=_main_justification,
autofit/regions/u4f.py:239:            broad_justification=_sat_justification,
autofit/regions/u4f.py:249:            broad_justification=_sat_justification,
autofit/regions/u4f.py:260:            broad_justification=_sat_justification,
autofit/regions/u4f.py:270:            broad_justification=_sat_justification,
autofit/regions/u4f.py:277:            broad_justification=_sat_justification,
tests/autofit/test_c1s_parity_gate.py:95:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:94:    pa = Phase(id="B-4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:96:    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:103:    pa = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_stage2_rereview_findings.py:105:    pb = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_stage2_rereview_findings.py:124:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_region_provenance_honesty.py:81:    """Unit 5: the MG-family aliphatic linked-offset window (0.2, 0.6) is
autofit/regions/c1s.py:125:def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
autofit/regions/c1s.py:128:    if material_class is MaterialClass.MIXED:
autofit/regions/c1s.py:165:_SHARED_CONTAM_FWHM = "shared_contamination_fwhm"
autofit/regions/c1s.py:174:    def provenance(self) -> list[dict]:
autofit/regions/c1s.py:243:            {"constant": "mixed_material_class_width_relaxation",
autofit/regions/c1s.py:289:        - A1–A3_linked:         shared contamination FWHM (Biesinger 2022)
autofit/regions/c1s.py:290:        - A1–A3_linked_offset:  + contaminant centers as bounded offsets
autofit/regions/c1s.py:306:        contam_fwhm = _contamination_fwhm_range(phase.material_class)
autofit/regions/c1s.py:337:            broad_justification=(
autofit/regions/c1s.py:359:        shared_decl = ((_SHARED_CONTAM_FWHM, contam_fwhm[0], contam_fwhm[1]),)
autofit/regions/c1s.py:367:                slots=tuple(slots), shared_fwhm_params=tuple(shared),
autofit/regions/c1s.py:379:        linked = [contam(k, linked_fwhm=_SHARED_CONTAM_FWHM) for k in keys]
autofit/regions/c1s.py:385:            contam(k, linked_fwhm=_SHARED_CONTAM_FWHM, offset=CONTAM_OFFSETS[k])
tests/autofit/test_u4f_parity_gate.py:30:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_u4f_parity_gate.py:32:BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_fit_physics_wiring.py:15:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_fit_physics_wiring.py:17:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_resolver.py:18:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_resolver.py:20:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_resolver.py:22:BN = Phase(id="BN", material_class=MaterialClass.INSULATOR,
tests/autofit/test_resolver.py:84:        xe = Phase(id="x", material_class=MaterialClass.CONDUCTOR, regions=("Xe 3d",))
tests/autofit/test_resolver.py:131:    both = Phase(id="mix", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_resolver.py:149:    shared_names = [n for n, _, _ in linked_cand.shared_fwhm_params]
tests/autofit/test_resolver.py:158:    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
tests/autofit/test_resolver.py:159:    p2 = Phase(id="ph2", material_class=MaterialClass.SEMICONDUCTOR, regions=("Fk 2p",))
tests/autofit/test_resolver.py:183:    p1 = Phase(id="ph1", material_class=MaterialClass.INSULATOR, regions=("Fk 2p",))
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
tests/autofit/test_c1s_mixed_material_class.py:158:    rec = _by_constant(records, "mixed_material_class_width_relaxation")
tests/autofit/test_c1s_mixed_material_class.py:205:# so the app must not vouch for it). Fixed by Unit A (broad_justification):
tests/autofit/test_c1s_mixed_material_class.py:219:    assert slot.broad_justification is None, (
tests/autofit/test_c1s_mixed_material_class.py:236:    width parameter (_SHARED_CONTAM_FWHM) across all 3 contaminant slots,
tests/autofit/test_c1s_mixed_material_class.py:245:    linked slots keeps its OWN fwhm_range/broad_justification, and
tests/autofit/test_c1s_mixed_material_class.py:252:    cand = next(c for c in g.candidates if c.name == "A3_linked")
tests/autofit/test_c1s_mixed_material_class.py:253:    assert cand.shared_fwhm_params, (
tests/autofit/test_c1s_mixed_material_class.py:254:        "fixture assumption: A3_linked really does share one width "
tests/autofit/test_c1s_mixed_material_class.py:260:        assert slot.broad_justification is None, (
tests/autofit/test_cl2p_freewidth.py:41:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_structural_fallback.py:34:    return Phase(id="sample", material_class=MaterialClass(mc),
tests/autofit/test_structural_fallback.py:227:    p1 = Phase(id="a", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:229:    p2 = Phase(id="b", material_class=MaterialClass("conductor"),
tests/autofit/test_structural_fallback.py:280:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:304:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:322:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_structural_fallback.py:351:        "session_id": sid, "material_class": "insulator",
tests/autofit/test_structural_fallback.py:374:        "session_id": sid, "material_class": "conductor",
tests/autofit/test_candidate_pool_real_gate.py:86:    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
tests/autofit/test_candidate_pool_real_gate.py:226:    phase = Phase(id="sample", material_class=MaterialClass("conductor"),
tests/autofit/test_b1s_cl2p_parity_gates.py:36:B4C = Phase(id="B4C", material_class=MaterialClass.SEMICONDUCTOR,
tests/autofit/test_b1s_cl2p_parity_gates.py:38:UCL4 = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
tests/autofit/test_methods_seam.py:9:GRAPHITE = Phase(id="graphite", material_class=MaterialClass.CONDUCTOR,
tests/autofit/test_preseed_dominants.py:154:        assert p["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6, \
tests/autofit/test_preseed_dominants.py:163:    ``broad_justification``, e.g. a satellite) are NOT.
tests/autofit/test_preseed_dominants.py:165:    2026-07-20 (Unit A, broad_justification refactor): the exemption used
tests/autofit/test_preseed_dominants.py:172:    Updated to set broad_justification explicitly, matching how every real
tests/autofit/test_preseed_dominants.py:178:    def slot(role, lo, hi, broad_justification=None):
tests/autofit/test_preseed_dominants.py:182:                             broad_justification=broad_justification)
tests/autofit/test_preseed_dominants.py:191:             broad_justification="synthetic: pi->pi* shake-up, physically broad"),
tests/autofit/test_preseed_dominants.py:208:    declared fwhm_range but NO broad_justification must be flagged when it
tests/autofit/test_preseed_dominants.py:236:    assert seeded.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
tests/autofit/test_preseed_dominants.py:243:    assert aug.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
tests/autofit/test_preseed_dominants.py:269:    assert p["fitted_fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6   # NOT 3 eV
tests/autofit/test_preseed_dominants.py:278:            assert pk["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6
tests/autofit/test_reference_bridge.py:271:    phase = Phase(id="s", material_class=MaterialClass("conductor"),
tests/autofit/test_reference_bridge.py:289:    phase2 = Phase(id="s", material_class=MaterialClass("conductor"),
tests/autofit/test_broad_justification.py:11:(1) via a bare numeric test (``declared_hi > FWHM_MAX_ORDINARY_EV``). The
tests/autofit/test_broad_justification.py:18:mixed_material_class_verdict_run{A,B}.md).
tests/autofit/test_broad_justification.py:20:The fix: ``ComponentSlot.broad_justification`` makes meaning (2) an
tests/autofit/test_broad_justification.py:22:exemption off ``broad_justification is not None``, never off the bound's
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
tests/autofit/test_broad_justification.py:270:    been auto-exempt under the old numeric rule) but broad_justification
tests/autofit/test_broad_justification.py:279:        fwhm_range=(0.8, 15.0), broad_justification=None,
tests/autofit/test_broad_justification.py:286:        "a slot with a wide bound but NO broad_justification must still "
tests/autofit/test_broad_justification.py:293:    """Mirror case: an explicit broad_justification grants exemption even
tests/autofit/test_broad_justification.py:302:        fwhm_range=(0.5, 2.0), broad_justification="synthetic test justification",
tests/autofit/test_broad_justification.py:309:        "an explicit broad_justification must exempt a slot even when its "
tests/autofit/test_broad_justification.py:314:def test_component_slot_broad_justification_defaults_to_none():
tests/autofit/test_broad_justification.py:320:    assert s.broad_justification is None

exec
/bin/zsh -lc 'git show --unified=80 bdc909a -- templates/index.html tests/autofit/test_c1s_mixed_material_class.py tests/js/fp_material_mixed.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-JHxAKzRb' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-skoK3Us3' (errno=Operation not permitted)
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

exec
/bin/zsh -lc 'git show --name-status --format=fuller bdc909a' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ypgRA1Gx' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-os4w3lsX' (errno=Operation not permitted)
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

M	templates/index.html
M	tests/autofit/test_c1s_mixed_material_class.py
M	tests/js/fp_material_mixed.test.js

codex
The added tests are direct enough on first read: one calls `_unphysical_width_flags` on an 8 eV MIXED contamination component, and the tiering test injects the actual produced flag into a real report. I’m checking whether any linked candidate family has a different construction that the new A3-linked test misses.
exec
/bin/zsh -lc "sed -n '753,855p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
def _unphysical_width_flags(
    components: "list[FittedComponent]", model: CandidateModel
) -> list[str]:
    """Fitted components whose width reaches the ordinary physical FWHM
    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.

    A slot is grammar-sanctioned-broad — EXEMPT, because its width is region
    physics cited in the region module, not an unphysical stretch — if and
    only if it carries an explicit ``ComponentSlot.broad_justification``
    (C 1s π→π* satellite, U 4f mains, B 1s, …; see each region module for its
    citation or honest UNVERIFIED-empirical disclosure). Any other slot —
    contamination, the aliphatic main, and the region-``unassigned`` F1
    pre-seed / F2-F3 proposal slots — that fits at/above the ordinary
    ceiling is flagged: the optimizer wanted a wider (fatter) peak than an
    ordinary component physically has, the cap held it at the limit, and the
    decomposition must be reported low-confidence (routes to the CONDITIONAL
    tier via rank_and_filter) rather than silently accepted.

    ``broad_justification`` is INDEPENDENT of ``fwhm_range``'s own magnitude
    (2026-07-20 refactor, Codex-caught in the MIXED material-class review):
    the exemption used to be inferred from ``declared_hi >
    FWHM_MAX_ORDINARY_EV`` alone, which conflated "the optimizer may search
    this wide" with "this region module vouches the width is real physics".
    Widening a bound for an unrelated reason (numerical-stability headroom,
    a wider calibration envelope, MIXED material class's relaxed
    contamination ceiling) used to silently grant the vouching exemption as
    a side effect. Region-agnostic: the exemption is driven entirely by
    each slot's own declared field, so no region's cited widths are ever
    mis-flagged, and no bound can ever again disable this safety net merely
    by being wide.
    """
    slots_by_role = {s.role: s for s in model.slots}
    flags: list[str] = []
    for c in components:
        slot = slots_by_role.get(c.slot_role)
        if slot is None:
            continue
        declared_lo, declared_hi = slot.fwhm_range
        vouched = slot.broad_justification is not None
        # EFFECTIVE width (Stage-2 PHYSICAL bar): DS+G's width lives in TWO
        # params — beta (Lorentzian HWHM, eV) and m_gauss (Gaussian FWHM;
        # what comp.fwhm carries) — so the checks below must see the
        # convolved width, not the Gaussian part alone (a component could
        # otherwise be ~3+ eV wide while every width check reads 1.0:
        # exactly the 'neighbor broadened to hide a missed peak' channel).
        # Olivero & Longbothum 1977 Voigt-FWHM approximation (0.02%).
        eff_fwhm = c.fwhm
        if c.line_shape is LineShape.DS_G:
            f_l = 2.0 * float(c.shape_params.get("beta", 0.0))
            eff_fwhm = 0.5346 * f_l + np.sqrt(0.2166 * f_l ** 2 + c.fwhm ** 2)
            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
                flags.append(
                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
                    f"β={c.shape_params.get('beta', 0.0):.2f} + "
                    f"m={c.fwhm:.2f}; no known-broad justification)")
                continue
        elif c.line_shape is LineShape.ASYM_GL:
            # asym-GL broadens its high-BE side to fwhm×(1+asymmetry)
            # (fitting.py convention) — the MEAN effective width
            # fwhm×(1+asym/2) closes the remaining papering-over channel
            # (Codex Stage-2 review, run A MAJOR).
            asym = float(c.shape_params.get("asymmetry", 0.0))
            eff_fwhm = c.fwhm * (1.0 + 0.5 * asym)
            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
                flags.append(
                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
                    f"fwhm={c.fwhm:.2f}×(1+{asym:.2f}/2); no known-broad "
                    "justification)")
                continue
        # detection-family slots (scale-relative ceilings, usually > the
        # ordinary cap): a component at ≥ DETECTION_WIDTH_ABSORB_FRACTION
        # of its own ceiling (= 1.75× the DETECTED width via the 2.5×
        # ceiling) is absorbing neighboring intensity — the papering-over
        # signature in transferable units. Unaffected by broad_justification
        # (these are engine-constructed proposal/pre-seed slots, not
        # region-module-authored grammar; their ceiling is scale-relative,
        # not a physics vouch).
        if c.slot_role.startswith("detected_peak_"):
            if eff_fwhm >= DETECTION_WIDTH_ABSORB_FRACTION * declared_hi:
                flags.append(
                    f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥"
                    f"{DETECTION_WIDTH_ABSORB_FRACTION:.2f}×ceiling "
                    f"({declared_hi:.2f}eV) — ~1.75× its detected width; "
                    "likely absorbing a neighbor")
            continue
        if vouched:
            continue                       # grammar-sanctioned-broad slot
        # pegging the ordinary ceiling — same 1%-of-range tol as boundary
        # detection, so a component held AT the 2.0 cap is caught
        tol = 0.01 * (declared_hi - declared_lo) if declared_hi > declared_lo else 0.0
        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
            flags.append(
                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
                "ordinary cap (no known-broad justification)")
    return flags


def fit_candidate(
    x: np.ndarray,
    y: np.ndarray,
    weights: np.ndarray,

exec
/bin/zsh -lc "sed -n '120,410p' autofit/regions/c1s.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
# is the same class of risk, now reachable through a wider ceiling instead
# of a free position. Should be adversarially fit-tested, not just read.
FWHM_MIXED_CEILING_NUMERIC_GUARD_EV = 15.0


def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
    """FWHM_RANGE_CONTAMINATION, widened under MIXED. See the constant
    comment above — this relaxes a constraint, it never asserts a new one."""
    if material_class is MaterialClass.MIXED:
        return (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
    return FWHM_RANGE_CONTAMINATION


# DS+G Lorentzian HWHM fixed at the C 1s core-hole lifetime:
# Campbell & Papp, At. Data Nucl. Data Tables 77 (2001) 1–56
# (DOI 10.1006/adnd.2000.0848): Γ_K(C) ≈ 0.10 eV FWHM → 0.05 eV HWHM.
# VERIFIED (spec §9). Breaks the α/β/m_gauss broadening degeneracy.
DSG_LORENTZIAN_HWHM_C1S = 0.05

# Graphitic asymmetry-index cap ≤ 0.3 — UNVERIFIED numeric guard (fitalg;
# keeps the optimizer away from the α→0.5 singularity).
DSG_ALPHA_RANGE_GRAPHITIC = (0.0, 0.3)

# asym-GL graphitic parameter windows — UNVERIFIED-empirical: chosen to
# bracket the expert reference fits (asymmetry ≈ 0.10, glMix ≈ 0.08–0.5)
# rather than derived from literature. The AG family exists so the engine
# can express the analysts' asym-GL practice; treat its constants as
# calibration targets, not physics.
ASYMGL_ASYMMETRY_RANGE = (0.0, 0.5)

# Adventitious-carbon chemical shifts from the C-C/C-H reference — soft
# priors/windows per Biesinger (2022): C-O +1.5±0.3, C=O +3.0±0.3,
# O-C=O +4.0±0.4 (CONDITIONAL per spec §9 — convention, not universal).
CONTAM_OFFSETS = {"CO": (1.5, 0.3), "C=O": (3.0, 0.3), "OC=O": (4.0, 0.4)}

# π→π* satellite offset window from the graphitic main (fitalg; UNVERIFIED
# tunable).
SATELLITE_OFFSET_RANGE = (5.5, 7.0)

_MAIN_FWHM_BY_MATERIAL = {
    "graphite": FWHM_RANGE_GRAPHITIC,
    None: FWHM_RANGE_GRAPHITIC,          # default material for a conductor
    "polymer": FWHM_RANGE_AROMATIC_POLYMER,
}

_SHARED_CONTAM_FWHM = "shared_contamination_fwhm"


class C1sModule:
    region = REGION

    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
        return dict(C1S_WINDOWS)

    def provenance(self) -> list[dict]:
        return [
            {"constant": "graphite_reference_ev", "value": 284.4,
             "status": "VERIFIED",
             "source": "Leiro DOI 10.1016/S0368-2048(02)00284-0; HOPG SSS "
                       "10.1116/1.1247695 (window anchor)"},
            {"constant": "adventitious_reference_ev", "value": 284.8,
             "status": "CONDITIONAL",
             "source": "Biesinger 2022 10.1016/j.apsusc.2022.153681; "
                       "Greczynski 10.1002/anie.201916000 — convention"},
            {"constant": "dsg_core_hole_beta_ev", "value": DSG_LORENTZIAN_HWHM_C1S,
             "status": "VERIFIED",
             "source": "Campbell & Papp 2001 DOI 10.1006/adnd.2000.0848 "
                       "(Γ_K(C) ≈ 0.10 eV FWHM → 0.05 HWHM)"},
            {"constant": "contamination_offsets_ev",
             "value": {k: list(v) for k, v in CONTAM_OFFSETS.items()},
             "status": "CONDITIONAL",
             "source": "Biesinger 2022 soft priors (+1.5/+3.0/+4.0)"},
            {"constant": "window_widths", "value": {k: list(v) for k, v in C1S_WINDOWS.items()},
             "status": "UNVERIFIED", "source": "fitalg prototype bins around cited anchors"},
            {"constant": "fwhm_graphitic_ev", "value": list(FWHM_RANGE_GRAPHITIC),
             "status": "UNVERIFIED", "source": "fitalg; instrument-dependent"},
            {"constant": "fwhm_contamination_floor_ev",
             "value": FWHM_RANGE_CONTAMINATION[0],
             "status": "CONDITIONAL",
             "source": "Biesinger, Appl. Surf. Sci. 597 (2022) 153681; "
                       "Greczynski & Hultman (2020) — published lower "
                       "bound for adventitious/aliphatic carbon FWHM"},
            {"constant": "fwhm_contamination_ceiling_ev",
             "value": FWHM_RANGE_CONTAMINATION[1],
             "status": "UNVERIFIED",
             "source": "lab-adjudicated cap, not a literature value — "
                       "expert adjudication 2026-07-03 "
                       "(docs/autofit/adjudication-decisions.md #5); a "
                       "literature-reasonable upper bound but a cap, not "
                       "a target; replaces the prior split 1.6/3.5 caps"},
            {"constant": "fwhm_satellite_ev", "value": list(FWHM_RANGE_SATELLITE),
             "status": "UNVERIFIED",
             "source": "labeled-set calibration (44 fits, 1.9–5.0 eV)"},
            {"constant": "dsg_alpha_cap", "value": list(DSG_ALPHA_RANGE_GRAPHITIC),
             "status": "UNVERIFIED", "source": "fitalg numeric guard"},
            {"constant": "asymgl_family", "value": "empirical asymmetric envelope",
             "status": "UNVERIFIED", "source": "expert-practice family (AG/MG)"},
            {"constant": "asymgl_asymmetry_range", "value": list(ASYMGL_ASYMMETRY_RANGE),
             "status": "UNVERIFIED",
             "source": "UNVERIFIED-empirical: chosen to bracket the expert "
                       "reference fits (asymmetry ≈ 0.10, glMix ≈ "
                       "0.08–0.5) rather than derived from literature; "
                       "treat as a calibration target, not physics"},
            {"constant": "satellite_offset_range_ev", "value": list(SATELLITE_OFFSET_RANGE),
             "status": "UNVERIFIED",
             "source": "fitalg tunable — the π→π* satellite "
                       "offset window from the graphitic main"},
            {"constant": "aromatic_polymer_fwhm_ev",
             "value": list(FWHM_RANGE_AROMATIC_POLYMER),
             "status": "CONDITIONAL",
             "source": "Beamson & Briggs, High Resolution XPS of Organic "
                       "Polymers — The Scienta ESCA300 Database, Wiley "
                       "(1992): aromatic C 1s 0.9–1.5 eV; widened to "
                       "0.8–1.8 as the generous cross-instrument envelope "
                       "(the widening beyond the cited range is editorial, "
                       "not itself literature-derived)"},
            {"constant": "aliphatic_linked_offset_range_ev", "value": [0.2, 0.6],
             "status": "UNVERIFIED",
             "source": "UNVERIFIED-empirical (labeled-set + convention): "
                       "brackets both expert practice (+0.30: graphitic "
                       "284.5 vs aliphatic 284.8) and Biesinger's "
                       "adventitious C-C/C-H convention (284.8 vs "
                       "graphite 284.4, +0.4)"},
            {"constant": "mixed_material_class_width_relaxation",
             "value": "under MaterialClass.MIXED (analyte embedded in a "
                      "different matrix), the contamination/adventitious "
                      "FWHM ceiling's single-species-homogeneity "
                      "assumption is withdrawn and the ceiling is relaxed "
                      "toward unconstrained; no new position or width "
                      "value is asserted — position windows and every "
                      "other FWHM family are unchanged",
             "status": "CONDITIONAL",
             "source": "differential charging between analyte and matrix "
                       "causes inhomogeneous broadening (Baer, "
                       "Artyushkova, Cohen, Easton, Engelhard, Gengenbach, "
                       "Greczynski, Mack, Morgan, Roberts, \"XPS Guide: "
                       "Charge neutralization and binding energy "
                       "referencing for insulating samples,\" J. Vac. Sci. "
                       "Technol. A 38, 031204 (2020), DOI "
                       "10.1116/6.0000057 — differential charging "
                       "broadens peaks, and a single charge correction is "
                       "insufficient once it is present; internal "
                       "referencing has \"limited accuracy ... often "
                       "including multiphase and other complex samples\"; "
                       "Greczynski & Hultman, \"X-ray photoelectron "
                       "spectroscopy: Towards reliable binding energy "
                       "referencing,\" Prog. Mater. Sci. 107 (2020) "
                       "100591, DOI 10.1016/j.pmatsci.2019.100591)"},
            {"constant": "mixed_fwhm_ceiling_numeric_guard",
             "value": FWHM_MIXED_CEILING_NUMERIC_GUARD_EV,
             "status": "UNVERIFIED",
             "source": "a fully unconstrained (infinite) ceiling breaks "
                       "the engine's initial-value seeding (the FWHM "
                       "guess is the fwhm_range midpoint); this reuses "
                       "fitting.py's own existing fwhm_max default, the "
                       "ceiling the manual /api/fit path already applies "
                       "to every peak in this app — a numeric guard for "
                       "optimizer stability, not a chemistry or physics "
                       "claim (same footing as dsg_alpha_cap above)"},
        ]

    def build_candidates(
        self, phase: Phase, oxidation_state: Optional[str] = None
    ) -> list[CandidateModel]:
        """
        Model families (admissibility encoded structurally, fitalg §):

        - A0–A3:  DS+G asymmetric graphitic main + π→π* satellite
                  + 0–3 contaminants (absolute windows)
        - A1–A3_linked:         shared contamination FWHM (Biesinger 2022)
        - A1–A3_linked_offset:  + contaminant centers as bounded offsets
        - AG0–AG3_linked:       asym-GL graphitic main variants (expert-fit
                                parity family; UNVERIFIED-empirical shape)
        - M0–M3:  mixed graphitic (DS+G) + aliphatic (PV) two-main models
        - B2/B3 (+_linked):     symmetric adventitious-carbon models
        - shake-up satellite only with an asymmetric main (admissibility)

        ``oxidation_state`` is accepted for the Layer-C seam; C 1s defines
        no oxidation-state overrides.
        """
        if oxidation_state is not None:
            raise KeyError(
                f"C 1s defines no oxidation-state override {oxidation_state!r}"
            )
        pid = phase.id
        main_fwhm = _MAIN_FWHM_BY_MATERIAL.get(phase.material, FWHM_RANGE_GRAPHITIC)
        contam_fwhm = _contamination_fwhm_range(phase.material_class)

        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
            return ComponentSlot(
                role=role, region=REGION, phase_id=pid,
                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
            )

        def graphitic_main_dsg() -> ComponentSlot:
            return slot(
                "main_graphitic", C1S_WINDOWS["graphitic"], LineShape.DS_G,
                main_fwhm,
                fixed_params=(("beta", DSG_LORENTZIAN_HWHM_C1S),),
                param_ranges=(("alpha", DSG_ALPHA_RANGE_GRAPHITIC),),
            )

        def graphitic_main_asymgl() -> ComponentSlot:
            return slot(
                "main_graphitic", C1S_WINDOWS["graphitic"], LineShape.ASYM_GL,
                main_fwhm,
                param_ranges=(("asymmetry", ASYMGL_ASYMMETRY_RANGE),),
            )

        def aliphatic_main() -> ComponentSlot:
            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
                        LineShape.PSEUDO_VOIGT, contam_fwhm)

        shake_up = slot(
            "satellite_pi", C1S_WINDOWS["shake_up_pi"], LineShape.PSEUDO_VOIGT,
            FWHM_RANGE_SATELLITE,
            linked_to="main_graphitic", linked_offset_range=SATELLITE_OFFSET_RANGE,
            broad_justification=(
                "pi->pi* shake-up satellite: physically broad due to "
                "multi-electron excitation (a genuine broadening "
                "mechanism, not merely calibration); the specific range "
                "is further calibrated to the labeled expert set (44 "
                "fits, 1.9-5.0 eV, CALIBRATED 2026-07-03)"
            ),
        )

        def contam(key, linked_fwhm=None, offset=None,
                   fwhm_range=None) -> ComponentSlot:
            kw = {}
            if linked_fwhm:
                kw["fwhm_linked_to"] = linked_fwhm
            if offset:
                mid, hw = offset
                kw["linked_to"] = "main_graphitic"
                kw["linked_offset_range"] = (mid - hw, mid + hw)
            return slot(f"contamination_{key}", C1S_WINDOWS[key],
                        LineShape.PSEUDO_VOIGT,
                        fwhm_range if fwhm_range is not None else contam_fwhm, **kw)

        shared_decl = ((_SHARED_CONTAM_FWHM, contam_fwhm[0], contam_fwhm[1]),)
        keys = ["CO", "C=O", "OC=O"]

        candidates: list[CandidateModel] = []

        def add(name, slots, shared=()):
            candidates.append(CandidateModel(
                name=name, background=BackgroundType.SHIRLEY,
                slots=tuple(slots), shared_fwhm_params=tuple(shared),
            ))

        # --- A family: DS+G asymmetric main + satellite + contaminants ---
        base_a = [graphitic_main_dsg(), shake_up]
        plain = [contam(k) for k in keys]
        add("A0_graphite_asym_satellite", base_a)
        for n in (1, 2, 3):
            add(f"A{n}_graphite_asym_sat_plus_{'_'.join(keys[:n])}",
                base_a + plain[:n])

        # --- A_linked: shared contamination width (Biesinger 2022) ---
        linked = [contam(k, linked_fwhm=_SHARED_CONTAM_FWHM) for k in keys]
        for n in (1, 2, 3):
            add(f"A{n}_linked", base_a + linked[:n], shared_decl)

        # --- A_linked_offset: + offset-parameterized contaminant centers ---
        offset_linked = [
            contam(k, linked_fwhm=_SHARED_CONTAM_FWHM, offset=CONTAM_OFFSETS[k])
            for k in keys
        ]
        for n in (1, 2, 3):
            add(f"A{n}_linked_offset", base_a + offset_linked[:n], shared_decl)

        # --- AG family: asym-GL graphitic main (expert-fit parity family).
        #     Contamination widths use the UNIFORM adjudicated cap — the
        #     former split lab-practice (0.8, 3.5) convention was replaced
        #     per adjudication #5; AG/MG now differ from A/M only in the
        #     graphitic main lineshape. ---
        base_ag = [graphitic_main_asymgl(), shake_up]
        add("AG0_graphite_asymGL_satellite", base_ag)
        for n in (1, 2, 3):
            add(f"AG{n}_graphite_asymGL_sat_plus_{'_'.join(keys[:n])}",
                base_ag + plain[:n])
        for n in (1, 2, 3):
            add(f"AG{n}_linked", base_ag + linked[:n], shared_decl)

        # --- M family: mixed graphitic (DS+G) + aliphatic (PV) two mains ---
        base_m = [graphitic_main_dsg(), aliphatic_main(), shake_up]
        add("M0_graph_asym_aliph_sym_satellite", base_m)
        for n in (1, 2, 3):
            add(f"M{n}_graph_asym_aliph_sym_sat_{'_'.join(keys[:n])}",
                base_m + plain[:n])


exec
/bin/zsh -lc "sed -n '208,260p' tests/test_api_analyze.py" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "sed -n '230,300p' app.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    except KeyError:
        raise _AnalyzeError(f"Session '{session_id}' not found", 404)

    method_id = body.get("method", "ic_model_comparison")
    if method_id not in _ANALYZE_METHODS:
        raise _AnalyzeError(f"Unknown analyze method '{method_id}' "
                            f"(available: {sorted(_ANALYZE_METHODS)})")

    regions = body.get("regions") or []
    if (not isinstance(regions, list) or not regions
            or not all(isinstance(r, str) for r in regions)):
        raise _AnalyzeError("'regions' must be a non-empty list of region names")

    mc_raw = body.get("material_class", "")
    try:
        mclass = MaterialClass(mc_raw)
    except ValueError:
        raise _AnalyzeError(f"Unknown material_class '{mc_raw}'")

    try:
        cc_shift = float(body.get("cc_shift", 0.0))
    except (TypeError, ValueError):
        raise _AnalyzeError("cc_shift must be a number")
    corrected = energy - cc_shift   # frontend getCorrectedBE convention

    # present-but-falsy non-objects ([], "", false) must be clean 400s,
    # not silently treated as omitted (Codex re-check)
    roi = body.get("roi")
    roi = {} if roi is None else roi
    if not isinstance(roi, dict):
        raise _AnalyzeError("'roi' must be an object")
    try:
        be_min = float(roi.get("be_min", float(corrected.min())))
        be_max = float(roi.get("be_max", float(corrected.max())))
    except (TypeError, ValueError):
        raise _AnalyzeError("roi.be_min/be_max must be numbers")
    mask = (corrected >= be_min) & (corrected <= be_max)
    if int(mask.sum()) < 20:
        raise _AnalyzeError("ROI selects fewer than 20 points")
    x, y = corrected[mask], counts[mask]

    options = body.get("options")
    options = {} if options is None else options
    if not isinstance(options, dict):
        raise _AnalyzeError("'options' must be an object")
    opts = {**_ANALYZE_METHODS[method_id], **options}

    peak_specs = body.get("peak_specs") or None
    if method_id == "least_squares" and not peak_specs:
        raise _AnalyzeError("least_squares is the manual-model baseline — "
                            "provide 'peak_specs'")

    phase_kwargs = body.get("phase")
    phase_kwargs = {} if phase_kwargs is None else phase_kwargs
    if not isinstance(phase_kwargs, dict):
        raise _AnalyzeError("'phase' must be an object")
    grammar = None
    if method_id != "least_squares":
        phase = Phase(id=str(phase_kwargs.get("id", "sample")),
                      material_class=mclass,
                      regions=tuple(regions),
                      material=phase_kwargs.get("material"))
        try:
            # Phase D: regions without a deep module degrade to derived
            # structure instead of erroring (unparseable labels still 400)
            grammar = resolve(
                [phase], regions if len(regions) > 1 else regions[0],
                allow_structural_fallback=True)
        except (UnknownRegionError, PhaseAmbiguityError, ValueError) as exc:
            raise _AnalyzeError(str(exc))


 succeeded in 0ms:
def test_material_class_does_not_affect_charge_correction(client):
    """DECIDED (Skye, 2026-07-17): MIXED must not alter the charge-
    correction step in any way -- not suppressed, not adjusted, not
    conditionally applied. Verified at the mechanism, not just by reading
    the diff: _validate_analyze_request's corrected/ROI-masked (x, y)
    arrays -- the actual output of the cc_shift charge-correction step --
    must be byte-identical regardless of material_class. material_class
    only ever reaches Phase.material_class, consumed by grammar
    resolution/candidate building, which happens strictly AFTER x/y are
    already fixed."""
    from app import _validate_analyze_request

    sid = _upload_doublet(client)
    upload_folder = client.application.config["UPLOAD_FOLDER"]
    base = {
        "session_id": sid, "regions": ["Cl 2p"],
        "method": "ic_model_comparison", "cc_shift": 1.23,
        "roi": {"be_min": 192.0, "be_max": 205.0},
    }
    ctx_conductor = _validate_analyze_request(
        {**base, "material_class": "conductor"}, upload_folder)
    ctx_mixed = _validate_analyze_request(
        {**base, "material_class": "mixed"}, upload_folder)
    assert np.array_equal(ctx_conductor.x, ctx_mixed.x)
    assert np.array_equal(ctx_conductor.y, ctx_mixed.y)


def test_json_sanitize_non_finite():
    """inf/NaN (degenerate-fit BIC values) must become null, not invalid
    JSON tokens browsers refuse to parse."""
    from app import _json_sanitize
    out = _json_sanitize({"a": float("inf"), "b": float("nan"),
                          "c": [1.0, float("-inf")],
                          "d": np.float64("inf"), "e": 2.5})
    assert out == {"a": None, "b": None, "c": [1.0, None],
                   "d": None, "e": 2.5}
    json.dumps(out, allow_nan=False)

exec
/bin/zsh -lc "sed -n '1,130p' tests/autofit/test_c1s_mixed_material_class.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
"""MIXED material class (2026-07-20 unit): analyte-in-matrix samples can
show DIFFERENTIAL CHARGING between phases -- the sample charges
non-uniformly under X-ray illumination, so a distribution of local surface
potentials broadens observed peaks (inhomogeneous broadening). That
broadening voids the single-species-homogeneity assumption behind the C 1s
adventitious/contamination FWHM ceiling, so MIXED relaxes it.

The provenance-audit trap this unit must NOT fall into: asserting a new
numeric position/width value derived from this lab's own spectra (e.g.
"MIXED widens the cap to 3.5 eV because that's what our UCl4-in-graphite
samples do") would reintroduce exactly the self-reference the provenance
audit removed -- wearing a feature label instead of a tier badge.
Withdrawing an assumption needs no citation; asserting a new numeric
window does, and this feature has none. So MIXED only RELAXES an existing
constraint (widens toward the engine's own pre-existing numeric-stability
ceiling) -- it never asserts a new position or width VALUE.

Citations for the physical rationale (see also C1sModule.provenance()):
Baer, Artyushkova, Cohen, Easton, Engelhard, Gengenbach, Greczynski, Mack,
Morgan, Roberts, "XPS Guide: Charge neutralization and binding energy
referencing for insulating samples," J. Vac. Sci. Technol. A 38, 031204
(2020), DOI 10.1116/6.0000057 -- differential charging broadens peaks
(examining the leading edge across analysis points/time "identif[ies]
peak broadening as a result of differential charging"), and a single
charge correction is insufficient once differential charging is present:
internal referencing has "limited accuracy... often including multiphase
and other complex samples." Greczynski & Hultman, "X-ray photoelectron
spectroscopy: Towards reliable binding energy referencing," Prog. Mater.
Sci. 107 (2020) 100591, DOI 10.1016/j.pmatsci.2019.100591 (referencing
reliability, general).
"""
from __future__ import annotations

import pytest

from autofit.grammar import MaterialClass, Phase, resolve
from autofit.regions.c1s import C1sModule, FWHM_RANGE_CONTAMINATION

NON_MIXED = [MaterialClass.CONDUCTOR, MaterialClass.SEMICONDUCTOR,
             MaterialClass.INSULATOR]


def _by_constant(records, name):
    hits = [r for r in records if r["constant"] == name]
    assert len(hits) == 1, f"expected exactly one {name!r} record, got {len(hits)}"
    return hits[0]


def _resolve(material_class):
    phase = Phase(id="sample", material_class=material_class, regions=("C 1s",))
    return resolve([phase], "C 1s")


def _contamination_slots(grammar):
    """Every slot governed by FWHM_RANGE_CONTAMINATION under the DEFAULT
    (non-MIXED) convention -- identified by its FLOOR, which MIXED never
    changes, so this selector is stable across material classes."""
    out = []
    for c in grammar.candidates:
        for s in c.slots:
            if s.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0]:
                out.append((c.name, s))
    return out


@pytest.mark.parametrize("material_class", NON_MIXED)
def test_non_mixed_candidate_pool_unchanged(material_class):
    """Non-regression, structural pin: conductor/semiconductor/insulator
    must build EXACTLY the pre-MIXED contamination fwhm_range -- byte
    (tuple) identical, not just close."""
    g = _resolve(material_class)
    slots = _contamination_slots(g)
    assert slots, "fixture assumption: at least one contamination-governed slot"
    for name, slot in slots:
        assert slot.fwhm_range == FWHM_RANGE_CONTAMINATION, (
            f"{name}/{slot.role}: fwhm_range changed for non-MIXED "
            f"material_class {material_class}"
        )


@pytest.mark.parametrize("material_class", NON_MIXED)
def test_non_mixed_candidate_names_unchanged(material_class):
    """Non-regression at the coarsest level: the SET of candidate model
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

exec
/bin/zsh -lc "sed -n '410,500p' autofit/regions/c1s.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:

        # --- MG family: the expert-practice STRUCTURE — asym-GL graphitic +
        #     aliphatic + satellite + contaminants (uniform adjudicated
        #     contamination cap).  The
        #     reference C 1s fits are exactly MG2-shaped (graphitic asym-GL
        #     284.5 + adventitious 284.8/285.9/287.6 + π→π* ~290.9).
        #     The aliphatic center is OFFSET-LINKED to the graphitic main
        #     (+0.2…+0.6 eV): with a free center the optimizer slides the
        #     aliphatic into the graphitic flank and pegs the window floor
        #     (overlap degeneracy, fitalg LIMITATIONS §9).  The offset window
        #     brackets both the expert practice (+0.30: 284.8 vs 284.5) and
        #     Biesinger's adventitious C-C/C-H at 284.8 vs graphite 284.4
        #     (+0.4).  UNVERIFIED-empirical (labeled-set + convention). ---
        def aliphatic_main_offset() -> ComponentSlot:
            return slot("main_aliphatic", C1S_WINDOWS["aliphatic"],
                        LineShape.PSEUDO_VOIGT, contam_fwhm,
                        linked_to="main_graphitic",
                        linked_offset_range=(0.2, 0.6))

        base_mg = [graphitic_main_asymgl(), aliphatic_main_offset(), shake_up]
        add("MG0_graphAsymGL_aliph_satellite", base_mg)
        for n in (1, 2, 3):
            add(f"MG{n}_graphAsymGL_aliph_sat_{'_'.join(keys[:n])}",
                base_mg + plain[:n])

        # --- B family: symmetric adventitious-carbon models (no satellite —
        #     admissibility: shake-up requires an asymmetric sp² main) ---
        aliph = aliphatic_main()
        aliph_fwhm_param = "s_main_aliphatic_fwhm"
        blinked = [contam(k, linked_fwhm=aliph_fwhm_param) for k in keys]
        add("B2_linked", [aliph] + blinked[:2])
        add("B3_linked", [aliph] + blinked[:3])
        # plain-window symmetric variants (low-priority but admissible)
        graph_sym = slot("main_graphitic", C1S_WINDOWS["graphitic"],
                         LineShape.PSEUDO_VOIGT, main_fwhm)
        add("B2_graphite_sym_CO_C=O", [graph_sym] + plain[:2])
        add("B3_graphite_sym_CO_C=O_OC=O", [graph_sym] + plain[:3])

        return candidates


register_region(C1sModule())

exec
/bin/zsh -lc "sed -n '450,520p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    their offset from the parent is a cited physical splitting, entirely
    unrelated to ROI cropping.
    """
    if x is None or len(x) == 0:
        return {}
    roi_lo, roi_hi = float(np.min(x)), float(np.max(x))
    primary = [s for s in model.slots if s.linked_to is None]
    overrides: dict[str, tuple[float, float]] = {
        s.role: (roi_lo, roi_hi) for s in primary if s.region == "unassigned"
    }
    curated = [s for s in primary if s.region != "unassigned"]
    if curated:
        lo_role = min(curated, key=lambda s: s.be_window[0]).role
        hi_role = max(curated, key=lambda s: s.be_window[1]).role
        for s in curated:
            # min()/max() against the ORIGINAL bound (never a bare ROI edge)
            # so this can only ever widen, never narrow or invert a bound —
            # a ROI that doesn't fully contain the slot's own literature
            # window (Codex-caught: e.g. ROI 287-300 vs a slot window
            # (284, 285)) must leave that side exactly as it was, not
            # produce an inverted (min > max) or narrowed bound.
            lo = min(s.be_window[0], roi_lo) if s.role == lo_role else s.be_window[0]
            hi = max(s.be_window[1], roi_hi) if s.role == hi_role else s.be_window[1]
            overrides[s.role] = (lo, hi)
    return overrides


def _default_params_from_slots(
    model: CandidateModel,
    x: Optional[np.ndarray] = None,
    y_net: Optional[np.ndarray] = None,
    fit_full_window: bool = False,
) -> Parameters:
    """Slot midpoints as starting values, slot bounds as hard constraints.

    ``fit_full_window`` (default False — every existing caller's behavior
    is unchanged unless it opts in) relaxes the primary-slot CENTER bound
    per ``_full_window_bound_overrides``; the starting guess and the
    amplitude-estimate window always stay anchored to the slot's own
    ``be_window``, so relaxing the bound never changes where the search
    starts, only how far it may wander.
    """
    p = Parameters()

    for name, lo_b, hi_b in model.shared_fwhm_params:
        p.add(name, value=0.5 * (lo_b + hi_b), min=lo_b, max=hi_b)

    if y_net is not None and len(y_net) > 0:
        y_peak = max(float(np.max(y_net)), 1.0)
    else:
        y_peak = 1.0e5

    def _amp_bounds(window: tuple[float, float]) -> tuple[float, float]:
        if x is not None and y_net is not None:
            init = _peak_estimate_in_window(x, y_net, window)
            return init, max(2.0 * y_peak, 10.0 * init, 1.0)
        return 1000.0, 1.0e5

    bound_overrides = (_full_window_bound_overrides(model, x)
                       if fit_full_window else {})

    # Pass 1: primary (non-linked) slots
    for slot in model.slots:
        if slot.linked_to is not None:
            continue
        prefix = _slot_prefix(slot.role)
        cmid = 0.5 * (slot.be_window[0] + slot.be_window[1])
        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
        amp_init, amp_max = _amp_bounds(slot.be_window)
        bound = bound_overrides.get(slot.role, slot.be_window)
        p.add(f"{prefix}center", value=cmid, min=bound[0], max=bound[1])

exec
/bin/zsh -lc "sed -n '540,620p' autofit/grammar.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
                raise ValueError(
                    f"candidate {cand.name!r}: slot {slot.role!r} region "
                    f"{slot.region!r} is not contributed by phase {phase.id!r}"
                )


def _compose_joint_candidates(
    slugs: list[str],
    per_request: list[list[CandidateModel]],
) -> list[CandidateModel]:
    """
    Cartesian composition of per-request candidate sets into joint models for
    one shared spectral window.  Slot roles are prefixed with the request's
    slug (region name, phase-qualified when the same region appears for
    multiple phases) to stay unique; the shared window uses ONE background
    (co-fit means one physical loss continuum).
    """
    composed: list[CandidateModel] = []
    for combo in itertools.product(*per_request):
        backgrounds = {c.background for c in combo}
        if len(backgrounds) != 1:
            raise ValueError(
                f"joint candidates must share one background, got {backgrounds} "
                f"for {[c.name for c in combo]}"
            )
        slots: list[ComponentSlot] = []
        shared: list[tuple[str, float, float]] = []
        for slug, cand in zip(slugs, combo):
            slug = re.sub(r"[^A-Za-z0-9_]", "", slug.replace(" ", ""))
            rename = {s.role: f"{slug}__{s.role}" for s in cand.slots}
            shared_rename = {name: f"{slug}__{name}" for name, _, _ in cand.shared_fwhm_params}
            for s in cand.slots:
                slots.append(_retag_slot(s, rename, shared_rename))
            for name, lo, hi in cand.shared_fwhm_params:
                shared.append((shared_rename[name], lo, hi))
        composed.append(CandidateModel(
            name="+".join(c.name for c in combo),
            background=combo[0].background,
            slots=tuple(slots),
            shared_fwhm_params=tuple(shared),
        ))
    return composed


def _retag_slot(
    s: ComponentSlot,
    rename: dict[str, str],
    shared_rename: dict[str, str],
) -> ComponentSlot:
    """Rewrite role / linked_to / fwhm_linked_to under the region prefix.

    Uses dataclasses.replace (ComponentSlot is frozen) rather than
    reconstructing the slot field-by-field: replace() carries every field
    NOT explicitly overridden forward unchanged, including any field added
    to ComponentSlot after this function was written. The manual
    reconstruction this replaced was exactly how broad_justification got
    silently dropped for every multi-region composed candidate (Codex-caught
    regression, 2026-07-20): a new field simply wasn't in the list, so it
    defaulted back to None for every slot passing through here — see
    tests/autofit/test_broad_justification.py's
    test_retag_slot_preserves_all_fields_except_the_three_rewritten, which
    guards against this exact class of bug recurring for whatever field
    comes next.
    """
    fwhm_link = s.fwhm_linked_to
    if fwhm_link is not None:
        # fwhm_linked_to may reference either a shared param or another
        # slot's parameter name (prefix-based); rewrite whichever matches.
        if fwhm_link in shared_rename:
            fwhm_link = shared_rename[fwhm_link]
        else:
            for old, new in rename.items():
                old_prefix = _slot_param_prefix(old)
                if fwhm_link.startswith(old_prefix):
                    fwhm_link = _slot_param_prefix(new) + fwhm_link[len(old_prefix):]
                    break
    return replace(
        s,
        role=rename[s.role],
        linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None,
        fwhm_linked_to=fwhm_link,

codex
One interesting detail: the new shared-width test covers `A3_linked`, and the same `linked` slot objects plus the same `shared_decl` are reused for `A*_linked`, `A*_linked_offset`, and `AG*_linked`. I’m checking `B*_linked` separately because it links contaminant widths to the aliphatic slot parameter rather than `shared_fwhm_params`.
exec
/bin/zsh -lc "sed -n '620,660p' autofit/grammar.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
        fwhm_linked_to=fwhm_link,
    )


def _slot_param_prefix(role: str) -> str:
    """Must match engine._slot_prefix — kept here to rewrite fwhm links."""
    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"

exec
/bin/zsh -lc "sed -n '520,610p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
        p.add(f"{prefix}center", value=cmid, min=bound[0], max=bound[1])
        p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
        _add_shape_params(p, prefix, slot, fmid)

    # Pass 2: linked slots (satellites, chemically-shifted contaminants,
    # spin-orbit partners) — center via offset expression; amplitude either
    # free (satellite) or ratio-linked (doublet).  Processed in dependency
    # order so a chain (main ← sat7/2 ← sat5/2) resolves: lmfit exprs may
    # not reference parameters that do not exist yet.
    done_roles = {s.role for s in model.slots if s.linked_to is None}
    pending = [s for s in model.slots if s.linked_to is not None]
    ordered: list[ComponentSlot] = []
    while pending:
        ready = [s for s in pending if s.linked_to in done_roles]
        if not ready:
            raise ValueError(
                f"unresolvable linkage chain among {[s.role for s in pending]} "
                "(missing parent or cycle)"
            )
        for s in ready:
            ordered.append(s)
            done_roles.add(s.role)
            pending.remove(s)

    for slot in ordered:
        prefix = _slot_prefix(slot.role)
        parent = model.slot_by_role(slot.linked_to)
        if parent is None:
            raise ValueError(f"Slot {slot.role!r} linked to unknown role {slot.linked_to!r}")
        parent_prefix = _slot_prefix(parent.role)
        offs_lo, offs_hi = slot.linked_offset_range or (0.0, 0.0)
        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])

        if offs_hi > offs_lo:
            p.add(f"{prefix}offset", value=0.5 * (offs_lo + offs_hi),
                  min=offs_lo, max=offs_hi)
            p.add(f"{prefix}center", value=0.0,
                  expr=f"{parent_prefix}center + {prefix}offset")
        else:
            # Degenerate range = fixed offset
            p.add(f"{prefix}center", value=0.0,
                  expr=f"{parent_prefix}center + {offs_lo}")

        # Shape params (incl. the width) BEFORE the amplitude: the width-
        # aware area-ratio expression below references this slot's width.
        _add_shape_params(p, prefix, slot, fmid, parent_prefix=parent_prefix)

        # ``area_ratio`` is an AREA statement (2j+1 statistical intensity).
        # With a shared width, height ratio == area ratio and the plain
        # height link is exact.  Under width-inequality linkage
        # (fwhm_excess_range) the height link must carry the width
        # correction: same-shape peaks have area ∝ amplitude × width (the
        # lineshape factor cancels only when the mixing params are shared —
        # guarded in _add_shape_params/_validate below).
        ratio_expr: Optional[str] = None
        if slot.area_ratio_range is not None:
            rlo, rhi = slot.area_ratio_range
            rinit = slot.area_ratio if slot.area_ratio is not None else 0.5 * (rlo + rhi)
            p.add(f"{prefix}ratio", value=float(np.clip(rinit, rlo, rhi)),
                  min=rlo, max=rhi)
            ratio_expr = f"{prefix}ratio"
        elif slot.area_ratio is not None:
            ratio_expr = repr(float(slot.area_ratio))

        if ratio_expr is None:
            amp_init, amp_max = _amp_bounds(slot.be_window)
            p.add(f"{prefix}amplitude", value=amp_init, min=0.0, max=amp_max)
        elif slot.fwhm_excess_range is not None:
            # Area-ratio linkage under independent widths is implemented
            # ONLY for the pseudo-Voigt with a shared mixing parameter —
            # the one case where area ∝ height × width with a cancelling
            # shape factor.  Other shapes (asym-GL asymmetry, DS α/γ,
            # DS+G's m_gauss-only width, LACX α/β/m) do NOT scale that way;
            # a shape-specific area factor is FUTURE WORK, and silently
            # emitting the height×width link there would enforce a wrong
            # area ratio (Codex adjudication-unit review, both runs).
            if parent.line_shape is not slot.line_shape:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range requires the parent to share the "
                    "line shape (area ∝ amplitude × width only holds "
                    "within one shape family)"
                )
            if slot.line_shape is not LineShape.PSEUDO_VOIGT:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range is implemented only for "
                    "PSEUDO_VOIGT (shape-specific area factors for other "
                    "shapes are future work)"
                )
            if "gl_ratio" not in slot.share_parent_params:

exec
/bin/zsh -lc "rg -n \"def _extract_components|FittedComponent\\(\" autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
675:        out.append(FittedComponent(
1076:            orphans.append(FittedComponent(
1094:        claimed = FittedComponent(

exec
/bin/zsh -lc "sed -n '1,230p' tests/autofit/test_broad_justification.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
"""Unit A (2026-07-20): decouples two meanings that ``fwhm_range``'s upper
bound used to carry at once:

  1. the optimizer's own search bound ("the width parameter may search up
     to here");
  2. a semantic claim consumed by quality reporting ("this region module
     VOUCHES that a component this wide is legitimate physics, not an
     optimizer papering over a missed feature").

``autofit/engine.py``'s ``_unphysical_width_flags`` used to infer (2) from
(1) via a bare numeric test (``declared_hi > FWHM_MAX_ORDINARY_EV``). The
MIXED material-class unit (77bf3a8) relaxed (1) for C 1s contamination
slots to make room for differential-charging broadening, and thereby
silently asserted (2) as a side effect -- exactly backwards, since MIXED's
entire premise is that we do NOT know how broad differential charging
makes the peak, the opposite of vouching for it. Both Codex reviews of
77bf3a8 independently caught this (see docs/autofit/codex/
mixed_material_class_verdict_run{A,B}.md).

The fix: ``ComponentSlot.broad_justification`` makes meaning (2) an
explicit, independent field. ``_unphysical_width_flags`` keys its
exemption off ``broad_justification is not None``, never off the bound's
magnitude. This file is the safety net for that refactor: it encodes, as
an explicit and auditable fixture, EXACTLY which slots are exempt today
(under the old numeric rule) so the same set stays exempt under the new
field-based rule -- pure refactor, behavior-neutral, proven rather than
asserted.
"""
from __future__ import annotations

import pytest

from autofit.engine import FittedComponent, _unphysical_width_flags
from autofit.grammar import LineShape, MaterialClass, Phase, resolve

# ── Ground truth: which slots are grammar-sanctioned-broad TODAY ───────────
# (declared_hi > FWHM_MAX_ORDINARY_EV == 2.0 eV, the pre-refactor rule),
# derived by reading every region module's build_candidates(). Each entry
# names the region, the exact CandidateModel to fetch it from, and the
# slot role. This is the fixture the refactor must reproduce exactly.

_CONDUCTOR_C1S = Phase(id="s", material_class=MaterialClass.CONDUCTOR,
                       regions=("C 1s",))
_INSULATOR_B1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
                       regions=("B 1s",))
_INSULATOR_CL2P = Phase(id="s", material_class=MaterialClass.INSULATOR,
                        regions=("Cl 2p",))
_INSULATOR_N1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
                       regions=("N 1s",))
_INSULATOR_U4F = Phase(id="s", material_class=MaterialClass.INSULATOR,
                       regions=("U 4f",))


def _slot(phase, region, candidate_name, role):
    g = resolve([phase], region)
    cand = next(c for c in g.candidates if c.name == candidate_name)
    slot = cand.slot_by_role(role)
    assert slot is not None, f"{candidate_name}/{role} not found"
    return slot


# (phase, region, candidate_name, role, currently_exempt)
EXEMPTION_FIXTURE = [
    # C 1s: only the pi->pi* satellite is exempt (declared 1.0-5.5).
    (_CONDUCTOR_C1S, "C 1s", "A0_graphite_asym_satellite", "satellite_pi", True),
    (_CONDUCTOR_C1S, "C 1s", "A0_graphite_asym_satellite", "main_graphitic", False),
    (_CONDUCTOR_C1S, "C 1s", "B2_linked", "main_aliphatic", False),
    (_CONDUCTOR_C1S, "C 1s", "A1_linked", "contamination_CO", False),
    # B 1s: all three mains share B1S_FWHM_RANGE (1.2-2.5) -- all exempt.
    (_INSULATOR_B1S, "B 1s", "B1_low", "main_b_low", True),
    (_INSULATOR_B1S, "B 1s", "B2_low_mid", "main_b_mid", True),
    (_INSULATOR_B1S, "B 1s", "B2b_low_oxide", "main_b_oxide", True),
    # Cl 2p: both p32 (shared-width family) and p12 exempt at CL2P_FWHM_RANGE
    # (1.2-2.2) / CL2P_12_FWHM_RANGE (free-width family, up to 3.0).
    (_INSULATOR_CL2P, "Cl 2p", "Cl0_doublet", "main_cl2p32", True),
    (_INSULATOR_CL2P, "Cl 2p", "Cl0_doublet", "main_cl2p12", True),
    (_INSULATOR_CL2P, "Cl 2p", "Cl0w_doublet_freewidth", "main_cl2p12", True),
    # N 1s: main_n1s exempt at N1S_FWHM_RANGE (0.7-2.5) in both shape variants.
    (_INSULATOR_N1S, "N 1s", "N0_pv", "main_n1s", True),
    (_INSULATOR_N1S, "N 1s", "N0_asymGL", "main_n1s", True),
    # U 4f: mains (1.5-3.5) and satellites (1.5-4.5) both exempt, incl.
    # the pair-linked / free-separation / independent satellite variants
    # (Codex-caught gap, round 1 of this refactor's own review: the
    # original fixture only covered U0_mains, not U1/U1b/U2's satellites).
    (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f72", True),
    (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f52", True),
    (_INSULATOR_U4F, "U 4f", "U1_mains_satpair", "satellite_u4f72", True),
    (_INSULATOR_U4F, "U 4f", "U1_mains_satpair", "satellite_u4f52", True),
    (_INSULATOR_U4F, "U 4f", "U1b_mains_satpair_freesep", "satellite_u4f52", True),
    (_INSULATOR_U4F, "U 4f", "U2_mains_satfree", "satellite_u4f72", True),
    (_INSULATOR_U4F, "U 4f", "U2_mains_satfree", "satellite_u4f52", True),
]

# ── Composed (multi-region joint co-fit) coverage ──────────────────────────
# The actual bug this section guards against (Codex-caught, round 1 of this
# refactor's own review): resolve() with >1 region composes candidates via
# autofit.grammar._retag_slot, which used to reconstruct each ComponentSlot
# by manually re-listing every field -- broad_justification wasn't in that
# list, so EVERY composed candidate silently lost EVERY exemption. Fixed by
# switching _retag_slot to dataclasses.replace(). This fixture exercises the
# exact U 4f + N 1s co-fit scenario both Codex reviews used to demonstrate
# the bug (this lab's real UCl4-in-BN samples).

_U4F_PHASE = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
                   regions=("U 4f",))
_N1S_PHASE = Phase(id="BN", material_class=MaterialClass.INSULATOR,
                   regions=("N 1s",))

# (candidate_name, role, currently_exempt) -- resolved via [_U4F_PHASE, _N1S_PHASE]
COMPOSED_EXEMPTION_FIXTURE = [
    ("U0_mains+N0_pv", "U4f__main_u4f72", True),
    ("U0_mains+N0_pv", "U4f__main_u4f52", True),
    ("U0_mains+N0_pv", "N1s__main_n1s", True),
    ("U1_mains_satpair+N0_pv", "U4f__satellite_u4f72", True),
    ("U1_mains_satpair+N0_pv", "U4f__satellite_u4f52", True),
    ("U1b_mains_satpair_freesep+N0_asymGL", "U4f__satellite_u4f52", True),
    ("U2_mains_satfree+N0_asymGL", "U4f__satellite_u4f72", True),
]


def _composed_slot(candidate_name, role):
    g = resolve([_U4F_PHASE, _N1S_PHASE], ["U 4f", "N 1s"])
    cand = next(c for c in g.candidates if c.name == candidate_name)
    slot = cand.slot_by_role(role)
    assert slot is not None, f"{candidate_name}/{role} not found"
    return slot


@pytest.mark.parametrize("candidate_name,role,exempt", COMPOSED_EXEMPTION_FIXTURE)
def test_composed_candidate_preserves_broad_justification(
        candidate_name, role, exempt):
    """The exact regression: a slot that is grammar-sanctioned-broad in its
    OWN region module must stay that way after _retag_slot composes it into
    a multi-region joint-fit candidate."""
    slot = _composed_slot(candidate_name, role)
    if exempt:
        assert slot.broad_justification is not None, (
            f"{candidate_name}/{role} lost its broad_justification during "
            "multi-region composition (_retag_slot regression)"
        )
    else:
        assert slot.broad_justification is None


def test_retag_slot_preserves_all_fields_except_the_three_rewritten():
    """Structural guard against this bug class recurring: _retag_slot must
    carry every ComponentSlot field forward unchanged except role/
    linked_to/fwhm_linked_to (deliberately rewritten for region-prefixing).
    Driven off dataclasses.fields(ComponentSlot) rather than a hardcoded
    list, so this test automatically covers any field added to
    ComponentSlot later -- a class-level guard, not another point fix."""
    import dataclasses

    from autofit.grammar import ComponentSlot, _retag_slot

    rewritten = {"role", "linked_to", "fwhm_linked_to"}

    sentinel_by_field = {
        "role": "orig_role",
        "region": "orig_region",
        "phase_id": "orig_phase",
        "be_window": (100.0, 200.0),
        "line_shape": LineShape.PSEUDO_VOIGT,
        "fwhm_range": (0.5, 9.99),
        "linked_to": "orig_role",
        "linked_offset_range": (1.0, 2.0),
        "area_ratio": 0.123456,
        "area_ratio_range": (0.1, 0.9),
        "fixed_params": (("beta", 0.05),),
        "param_ranges": (("alpha", (0.0, 0.3)),),
        "fwhm_linked_to": None,
        "fwhm_excess_range": (0.0, 0.8),
        "share_parent_params": ("alpha", "beta"),
        "broad_justification": "sentinel justification text",
    }
    field_names = {f.name for f in dataclasses.fields(ComponentSlot)}
    missing = field_names - set(sentinel_by_field)
    assert not missing, (
        f"ComponentSlot gained new field(s) {missing} this test doesn't "
        "sentinel-fill -- add a case above so the guard covers it"
    )

    original = ComponentSlot(**sentinel_by_field)
    rename = {"orig_role": "PhaseX__orig_role"}
    retagged = _retag_slot(original, rename, shared_rename={})

    for name in field_names:
        if name in rewritten:
            continue
        assert getattr(retagged, name) == getattr(original, name), (
            f"_retag_slot lost field {name!r}: "
            f"{getattr(original, name)!r} -> {getattr(retagged, name)!r}"
        )
    assert retagged.role == "PhaseX__orig_role"
    assert retagged.linked_to == "PhaseX__orig_role"


@pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
                         EXEMPTION_FIXTURE)
def test_exemption_fixture_matches_broad_justification(
        phase, region, candidate_name, role, exempt):
    """Each currently-exempt slot must carry a real broad_justification;
    each currently-non-exempt slot must not. This IS the byte-identical
    proof requested: the exemption SET, read directly off the grammar,
    matches the pre-refactor numeric rule exactly."""
    slot = _slot(phase, region, candidate_name, role)
    if exempt:
        assert slot.broad_justification is not None, (
            f"{region}/{candidate_name}/{role} was grammar-sanctioned-broad "
            f"under the old numeric rule (fwhm_range={slot.fwhm_range}) but "
            "lost its exemption in the refactor"
        )
        assert slot.fwhm_range[1] > 2.0, (
            "fixture sanity: this entry's OWN historical exemption basis "
            "was declared_hi > 2.0 -- if this fails, the fixture itself is "
            "wrong, not the code"
        )
    else:
        assert slot.broad_justification is None, (
            f"{region}/{candidate_name}/{role} was NOT grammar-sanctioned-"
            f"broad under the old numeric rule (fwhm_range={slot.fwhm_range}) "
            "but gained an unjustified exemption in the refactor"
        )


def _fitted(role, fwhm, line_shape=LineShape.PSEUDO_VOIGT, **shape_params):
    return FittedComponent(slot_role=role, position=0.0, fwhm=fwhm,
                           amplitude=1.0, shape_params=shape_params,
                           line_shape=line_shape)


2026-07-20T19:23:28.799156Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "sed -n '610,710p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
            if "gl_ratio" not in slot.share_parent_params:
                raise ValueError(
                    f"slot {slot.role!r}: area-ratio linkage under "
                    "fwhm_excess_range requires gl_ratio in "
                    "share_parent_params (the pseudo-Voigt area factor "
                    "must cancel in the ratio)"
                )
            wname = _width_param(slot.line_shape)
            p.add(f"{prefix}amplitude", value=0.0,
                  expr=(f"{parent_prefix}amplitude * {ratio_expr} * "
                        f"{parent_prefix}{wname} / {prefix}{wname}"))
        else:
            p.add(f"{prefix}amplitude", value=0.0,
                  expr=f"{parent_prefix}amplitude * {ratio_expr}")

    return p


# ─────────────────────────────────────────────────────────────────────────────
# Fit outcome + component extraction
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class FittedComponent:
    slot_role: str
    position: float
    fwhm: float          # width-parameter value (m_gauss for DS+G — fitalg convention)
    amplitude: float
    shape_params: dict
    line_shape: Optional[LineShape] = None


@dataclass
class FitOutcome:
    converged: bool
    components: list[FittedComponent]
    residual_sum_sq: float
    weighted_chi_sq: float
    n_params: int
    n_data: int
    lmfit_result: Optional[ModelResult] = None
    background: Optional[np.ndarray] = None
    boundary_hits: list[str] = field(default_factory=list)


def _extract_fitted_components(
    result: ModelResult, model: CandidateModel
) -> list[FittedComponent]:
    out: list[FittedComponent] = []
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        pars = result.params
        try:
            center = float(pars[f"{prefix}center"].value)
            amplitude = float(pars[f"{prefix}amplitude"].value)
            fwhm = float(pars[f"{prefix}{_width_param(slot.line_shape)}"].value)
        except KeyError:
            continue
        shape_params = {}
        for name, _, _, _ in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
            par = pars.get(f"{prefix}{name}")
            if par is not None:
                shape_params[name] = float(par.value)
        if slot.line_shape is LineShape.DS_G:
            shape_params["m_gauss"] = fwhm
        out.append(FittedComponent(
            slot_role=slot.role, position=center, fwhm=fwhm,
            amplitude=amplitude, shape_params=shape_params,
            line_shape=slot.line_shape,
        ))
    return out


# Shape-parameter names allowed to saturate at bounds per lineshape (shape
# preference, not pathology).  Width-like params are NOT excluded.
_BOUNDARY_EXCLUDED: dict[LineShape, frozenset[str]] = {
    LineShape.GAUSSIAN: frozenset(),
    LineShape.LORENTZIAN: frozenset(),
    LineShape.PSEUDO_VOIGT: frozenset({"gl_ratio"}),
    LineShape.ASYM_GL: frozenset({"gl_ratio", "asymmetry"}),
    LineShape.DS: frozenset({"alpha", "gamma_asym"}),
    LineShape.DS_G: frozenset({"alpha"}),          # beta is a WIDTH here — counted
    LineShape.LACX: frozenset({"alpha", "beta"}),  # both are exponents here
}


def _role_for_param(pname: str, role_by_prefix: dict[str, str]) -> Optional[str]:
    for prefix in sorted(role_by_prefix, key=len, reverse=True):
        if pname.startswith(prefix):
            return role_by_prefix[prefix]
    return None


def _detect_boundary_hits(params: Parameters, model: CandidateModel) -> list[str]:
    """Varying params within 1% of a finite bound → 'role:param@min|max'."""
    hits: list[str] = []
    role_by_prefix = {_slot_prefix(s.role): s.role for s in model.slots}
    shape_by_role = {s.role: s.line_shape for s in model.slots}

    for pname, par in params.items():
        if not par.vary:

exec
/bin/zsh -lc 'rg -n "def _add_shape_params|fwhm_linked_to|shared_fwhm" autofit/engine.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
367:def _add_shape_params(
392:        if wname in shared or wname in fixed or slot.fwhm_linked_to is not None:
410:    elif slot.fwhm_linked_to is not None:
412:              expr=slot.fwhm_linked_to)
494:    for name, lo_b, hi_b in model.shared_fwhm_params:
1915:        shared_fwhm_params=base.shared_fwhm_params,
2122:        shared_fwhm_params=base.shared_fwhm_params,

2026-07-20T19:23:49.067901Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "sed -n '360,420p' autofit/engine.py" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -p no:cacheprovider tests/autofit/test_c1s_mixed_material_class.py::test_mixed_wide_contamination_is_flagged_unphysical tests/autofit/test_c1s_mixed_material_class.py::test_mixed_wide_contamination_routes_to_conditional tests/autofit/test_c1s_mixed_material_class.py::test_mixed_shared_width_contamination_all_flagged_independently tests/autofit/test_c1s_mixed_material_class.py::test_mixed_provenance_relaxation_record_asserts_no_new_value tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction tests/js/fp_material_mixed.test.js' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
}

# Which parameter carries the slot's fwhm_range for each shape.
def _width_param(shape: LineShape) -> str:
    return "m_gauss" if shape is LineShape.DS_G else "fwhm"


def _add_shape_params(
    p: Parameters, prefix: str, slot: ComponentSlot, fwhm_init: float,
    parent_prefix: Optional[str] = None,
) -> None:
    """Width + shape-specific parameters for one slot, with bounds/overrides."""
    flo, fhi = slot.fwhm_range
    fixed = dict(slot.fixed_params)
    ranges = dict(slot.param_ranges)
    shared = set(slot.share_parent_params)
    if shared and parent_prefix is None:
        raise ValueError(
            f"slot {slot.role!r} declares share_parent_params but has no "
            "linked parent"
        )

    # Width parameter (fwhm, or m_gauss for DS+G)
    wname = _width_param(slot.line_shape)
    if slot.fwhm_excess_range is not None:
        # width-inequality linkage: width = parent width + free excess >= 0
        # (Coster-Kronig doublet broadening — grammar.ComponentSlot docs)
        if parent_prefix is None:
            raise ValueError(
                f"slot {slot.role!r} declares fwhm_excess_range but has no "
                "linked parent"
            )
        if wname in shared or wname in fixed or slot.fwhm_linked_to is not None:
            raise ValueError(
                f"slot {slot.role!r}: fwhm_excess_range is mutually exclusive "
                "with sharing/fixing/expression-linking the width"
            )
        elo, ehi = slot.fwhm_excess_range
        if not (0.0 <= elo < ehi):
            raise ValueError(
                f"slot {slot.role!r}: fwhm_excess_range must be a "
                f"non-negative interval, got {slot.fwhm_excess_range}"
            )
        p.add(f"{prefix}fwhm_excess", value=0.5 * (elo + ehi), min=elo, max=ehi)
        p.add(f"{prefix}{wname}", value=0.0,
              expr=f"{parent_prefix}{wname} + {prefix}fwhm_excess")
    elif wname in shared:
        p.add(f"{prefix}{wname}", value=0.0, expr=f"{parent_prefix}{wname}")
    elif wname in fixed:
        p.add(f"{prefix}{wname}", value=float(fixed[wname]), vary=False)
    elif slot.fwhm_linked_to is not None:
        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, flo, fhi)),
              expr=slot.fwhm_linked_to)
    else:
        wlo, whi = ranges.get(wname, (flo, fhi))
        p.add(f"{prefix}{wname}", value=float(np.clip(fwhm_init, wlo, whi)),
              min=wlo, max=whi)

    for name, init, lo, hi in _SHAPE_PARAM_DEFAULTS[slot.line_shape]:
        if name in shared:
            p.add(f"{prefix}{name}", value=0.0, expr=f"{parent_prefix}{name}")

 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python -c \"from autofit.grammar import MaterialClass, Phase, resolve; from autofit.engine import FittedComponent, _unphysical_width_flags; phase=Phase(id='sample', material_class=MaterialClass.MIXED, regions=('C 1s',)); g=resolve([phase], 'C 1s'); names=['A1_linked','A2_linked','A3_linked','A1_linked_offset','A2_linked_offset','A3_linked_offset','AG1_linked','AG2_linked','AG3_linked','B2_linked','B3_linked'];\\nfor name in names:\\n    cand=next(c for c in g.candidates if c.name==name); roles=[s.role for s in cand.slots if s.role.startswith('contamination_')]; comps=[FittedComponent(slot_role=r, position=0.0, fwhm=8.0, amplitude=1.0, shape_params={}, line_shape=cand.slot_by_role(r).line_shape) for r in roles]; flags=_unphysical_width_flags(comps, cand); print(name, 'shared=', cand.shared_fwhm_params, 'roles=', roles, 'flags=', [f.split(':')[0] for f in flags])\"" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

2026-07-20T19:24:02.456043Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
This environment has no `python` executable on PATH, so I’m retrying with `python3`. The filesystem is read-only, so I’m using no-cache/no-bytecode execution paths where possible.
exec
/bin/zsh -lc 'node --test tests/js/fp_material_mixed.test.js' in /Users/skyefortier/xps-verify
 succeeded in 150ms:
# Subtest: FP_STRINGS.materials.mixed has a clear, non-bare label
ok 1 - FP_STRINGS.materials.mixed has a clear, non-bare label
  ---
  duration_ms: 1.045351
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint is advisory, never claims correction
ok 2 - FP_STRINGS.materials.mixed hint is advisory, never claims correction
  ---
  duration_ms: 0.327617
  type: 'test'
  ...
# Subtest: FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
ok 3 - FP_STRINGS has no override entries for the other 3 material classes (dropdown rendering must stay byte-identical for them)
  ---
  duration_ms: 0.175445
  type: 'test'
  ...
# Subtest: FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
ok 4 - FP_STRINGS.materials.mixed hint names C 1s specifically and does not overstate scope to other regions (Codex run B MAJOR, 77bf3a8 recheck)
  ---
  duration_ms: 0.227591
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
# duration_ms 97.275647

2026-07-20T19:24:16.301472Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
`pytest` is not installed for this interpreter, but direct Python imports are available enough to keep probing. I’m switching the Python checks to direct function calls instead of invoking pytest.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import MaterialClass, Phase, resolve\\nfrom autofit.engine import FittedComponent, _unphysical_width_flags\\nphase=Phase(id=\"sample\", material_class=MaterialClass.MIXED, regions=(\"C 1s\",))\\ng=resolve([phase], \"C 1s\")\\nfor name in [\"A1_linked\",\"A2_linked\",\"A3_linked\",\"A1_linked_offset\",\"A2_linked_offset\",\"A3_linked_offset\",\"AG1_linked\",\"AG2_linked\",\"AG3_linked\",\"B2_linked\",\"B3_linked\"]:\\n    cand=next(c for c in g.candidates if c.name==name)\\n    roles=[s.role for s in cand.slots if s.role.startswith(\"contamination_\")]\\n    comps=[FittedComponent(slot_role=r, position=0.0, fwhm=8.0, amplitude=1.0, shape_params={}, line_shape=cand.slot_by_role(r).line_shape) for r in roles]\\n    flags=_unphysical_width_flags(comps, cand)\\n    print(name, \"shared=\", cand.shared_fwhm_params, \"roles=\", roles, \"flags=\", [f.split(\":\")[0] for f in flags])'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.regions.c1s import C1sModule\\nrecords=C1sModule().provenance()\\nrec=next(r for r in records if r[\"constant\"]==\"mixed_material_class_width_relaxation\")\\nprint(rec[\"value\"])\\nprint(\"actual_has_digit\", any(ch.isdigit() for ch in rec[\"value\"]))\\ns=\"relax to 3.5 eV based on our spectra\"\\nprint(\"example_has_digit\", any(ch.isdigit() for ch in s))'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-Qm2C0Snm' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-y2YubiLE' (errno=Operation not permitted)
under MaterialClass.MIXED (analyte embedded in a different matrix), the contamination/adventitious FWHM ceiling's single-species-homogeneity assumption is withdrawn and the ceiling is relaxed toward unconstrained; no new position or width value is asserted — position windows and every other FWHM family are unchanged
actual_has_digit False
example_has_digit True

 exited 1 in 149ms:
Traceback (most recent call last):
  File "<string>", line 2, in <module>
  File "/Users/skyefortier/xps-verify/autofit/engine.py", line 38, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

2026-07-20T19:24:32.789705Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "rg --files -g 'pyproject.toml' -g 'requirements*.txt' -g 'Pipfile' -g 'poetry.lock' -g '.venv' -g 'venv' -g 'pytest.ini' -g 'tox.ini' -g 'setup.cfg' -g 'package.json'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
requirements-dev.txt
requirements.txt

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

exec
/bin/zsh -lc "find . -maxdepth 3 -type f \\( -path './.venv/*' -o -path './venv/*' \\) | head" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
2026-07-20T19:24:39.720077Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The available `python3` lacks `pytest` and `lmfit`, so I can’t execute the Python tests in this sandbox. The JS test did run and passed. For the Python-specific claims I’m using close reading plus importable region/provenance code where dependencies allow it.
exec
/bin/zsh -lc 'which -a python3 pytest python pip3 pip' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
/usr/bin/python3
/usr/bin/pip3

exec
/bin/zsh -lc "sed -n '1,120p' requirements.txt && sed -n '1,120p' requirements-dev.txt" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
# XPS Peak Fitting – Python dependencies
# Install: pip install -r requirements.txt

flask>=3.0,<4
werkzeug>=3.0
gunicorn>=22.0

# Numerics & fitting
numpy>=1.26
scipy>=1.13
lmfit>=1.3

# File parsing
pandas>=2.2
openpyxl>=3.1       # .xlsx read/write

# Reference-data validation (data/xps/ against schema.json)
jsonschema>=4.21

# Optional – uncomment if you need CORS (e.g. separate frontend dev server)
# flask-cors>=4.0
olefile
gunicorn
# Test/development dependencies (runtime deps live in requirements.txt).
# The browser tests (tests/test_browser_*.py, tests/autofit/test_browser_*)
# additionally need a Playwright Chromium build:  playwright install chromium
# They self-skip when playwright/gunicorn/chromium are absent.
pytest>=9.0
playwright>=1.60

exec
/bin/zsh -lc "find /Users/skyefortier -maxdepth 4 \\( -name python -o -name pytest \\) -type f 2>/dev/null | head -50" in /Users/skyefortier/xps-verify
 succeeded in 3205ms:
/Users/skyefortier/xps-app/venv/bin/pytest

2026-07-20T19:24:51.338292Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
There is a separate virtualenv under `/Users/skyefortier/xps-app/venv`; I’m checking whether it has the needed dependencies and can run against this repo without writing into the workspace.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -c \"import pytest, lmfit; print('ok', pytest.__version__, lmfit.__version__)\"" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 /Users/skyefortier/xps-app/venv/bin/python -m pytest -q -p no:cacheprovider tests/autofit/test_c1s_mixed_material_class.py::test_mixed_wide_contamination_is_flagged_unphysical tests/autofit/test_c1s_mixed_material_class.py::test_mixed_wide_contamination_routes_to_conditional tests/autofit/test_c1s_mixed_material_class.py::test_mixed_shared_width_contamination_all_flagged_independently tests/autofit/test_c1s_mixed_material_class.py::test_mixed_provenance_relaxation_record_asserts_no_new_value tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction' in /Users/skyefortier/xps-verify
 exited 1 in 199ms:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pytest/__main__.py", line 9, in <module>
    raise SystemExit(pytest.console_main())
                     ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 223, in console_main
    code = main()
           ^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 193, in main
    config = _prepareconfig(new_args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 361, in _prepareconfig
    config: Config = pluginmanager.hook.pytest_cmdline_parse(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/helpconfig.py", line 124, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 121, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1192, in pytest_cmdline_parse
    self.parse(args)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/config/__init__.py", line 1562, in parse
    self.hook.pytest_load_initial_conftests(
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_hooks.py", line 512, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 167, in _multicall
    raise exception
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 139, in _multicall
    teardown.throw(exception)
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/warnings.py", line 128, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/pluggy/_callers.py", line 116, in _multicall
    next(function_gen)  # first yield
    ^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 170, in pytest_load_initial_conftests
    capman.start_global_capturing()
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 773, in start_global_capturing
    self._global_capturing = _get_multicapture(self._method)
                             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 714, in _get_multicapture
    return MultiCapture(in_=FDCapture(0), out=FDCapture(1), err=FDCapture(2))
                                              ^^^^^^^^^^^^
  File "/Users/skyefortier/xps-app/venv/lib/python3.12/site-packages/_pytest/capture.py", line 493, in __init__
    TemporaryFile(buffering=0),
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 631, in TemporaryFile
    prefix, suffix, dir, output_type = _sanitize_params(prefix, suffix, dir)
                                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 126, in _sanitize_params
    dir = gettempdir()
          ^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 315, in gettempdir
    return _os.fsdecode(_gettempdir())
                        ^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 308, in _gettempdir
    tempdir = _get_default_tempdir()
              ^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/Cellar/python@3.12/3.12.13_2/Frameworks/Python.framework/Versions/3.12/lib/python3.12/tempfile.py", line 223, in _get_default_tempdir
    raise FileNotFoundError(_errno.ENOENT,
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-verify']

 exited 1 in 1245ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
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
FileNotFoundError: [Errno 2] No usable temporary directory found in ['/var/folders/tv/_6g9gqh555q9xg8pshyzch7w0000gn/T/', '/tmp', '/var/tmp', '/usr/tmp', '/Users/skyefortier/xps-verify']

2026-07-20T19:25:01.745955Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The virtualenv has the packages, but Python libraries that call `tempfile.gettempdir()` fail because the sandbox has no writable temp directory. That prevents full Python execution here; it doesn’t affect the source review, but I’ll call it out accurately.
exec
/bin/zsh -lc 'rg -n "class RankResult|def rank_and_filter|conditional_reason|unphysical_widths" autofit/engine.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
83:# candidate; the result carries conditional_reason='decisive_override'.
112:# the physical limit and the result is flagged (unphysical_widths →
1437:    unphysical_widths: list[str] = field(default_factory=list)
1601:    conditional_reason: Optional[str] = None
1642:def rank_and_filter(
1667:        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
1685:    conditional_reason = None
1689:        conditional_reason = "no_clean_survivor"
1712:            conditional_reason = "unstable_last_resort"
1738:        conditional=conditional, conditional_reason=conditional_reason,
2217:    # (unphysical_widths + the fwhm@max boundary hit → CONDITIONAL) rather
2318:            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
2457:            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
2513:        result.conditional_reason = "decisive_override"
2830:                unphysical_widths=_unphysical_width_flags(primary.components, model),

exec
/bin/zsh -lc "sed -n '1,80p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
"""
Model-comparison engine — the fitalg pipeline ported onto main's fitting.py
and generalized to region-agnostic grammars (spec v2.1 §6).

Pipeline per candidate: primary fit → N perturbed refits (stability) →
slot matching by grammar role → absent-slot detection → residual
diagnostics → residual-guided proposal pass → filter-then-rank with BIC*.

Provenance: ported from the public ``xps-app-fitalg`` repo's
``model_comparison.py`` (validated there on HOPG + PET C 1s).  Changes made
in the port, besides symbol renames:

- lineshape layer rebuilt against CURRENT ``fitting.py``: fitalg's
  ``LA_ASYMMETRIC`` (α, β=Lorentzian-HWHM, m_gauss) is main's ``ds_g``; the
  true CasaXPS ``la_casaxps`` (exponent α/β + kernel-points m) is new here,
  as are ``asymmetric_gl`` / ``gaussian`` / ``lorentzian``.
- generic per-slot ``fixed_params`` / ``param_ranges`` replace the
  LA-specific ``fixed_lorentzian_hwhm`` / ``alpha_range`` fields.
- spin-orbit amplitude linkage (``area_ratio`` fixed, or
  ``area_ratio_range`` bounded-relaxed) — needed by doublet regions.
- boundary-hit shape-parameter exclusions are per-lineshape (a width-like
  ``beta`` in DS+G at a bound is a pathology; an exponent-like ``beta`` in
  LACX at a bound is a shape preference).

All numeric thresholds below are **UNVERIFIED tunables** (spec §9 —
sensitivity-test before publication claims); they carry fitalg's defaults.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

import numpy as np
from lmfit import Model, Parameters
from lmfit.model import ModelResult
from scipy.integrate import trapezoid

from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background

from .candidates import (build_candidate_pool, build_detection_candidate,
                         merge_residual_attempts)

from .grammar import (
    BACKEND_SHAPE,
    BackgroundType,
    CandidateGrammar,
    CandidateModel,
    ComponentSlot,
    LineShape,
)

log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# UNVERIFIED tunables (fitalg defaults; spec §9 sensitivity-test items)
# ─────────────────────────────────────────────────────────────────────────────

ABSENT_SLOT_AREA_FRACTION = 0.02
ABSENT_SLOT_PERSISTENCE_THRESHOLD = 0.7
DEFAULT_PERSISTENCE_THRESHOLD = 0.7
DEFAULT_BIC_AMBIGUITY = 2.0
# Decisive-override DOMINANCE rule (Codex cookbook review, blockers 2–3).
# A stable-but-boundary-limited candidate is promoted ahead of the clean
# tier only when ALL of the following hold:
#   (1) it is REFIT with its pegged parameters FIXED at their bounds — the
#       Laplace-style BIC* approximation is invalid at a constraint wall,
#       and the fixed-bound refit gives an honest parameter count;
#   (2) the refit's BIC* beats the best clean candidate's by more than
#       CONDITIONAL_OVERRIDE_DELTA_BIC (10 — the conventional "very strong"
#       threshold, Kass & Raftery, JASA 90 (1995) 773; UNVERIFIED as applied
#       to this heuristic BIC* on processed XPS data — tunable);
#   (3) its reduced χ² is also strictly better (BIC* is never the sole
#       decision axis — spec §6 trust order); and
#   (4) the clean best shows residual-structure flags (autocorrelation or
#       flagged windows) — evidence that it is genuinely mis-fitting, not

exec
/bin/zsh -lc "sed -n '880,980p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    bg = _compute_background(x, y, model.background)
    y_sub = y - bg
    composite = _build_composite_model(model)
    params = initial_params if initial_params is not None else \
        _default_params_from_slots(model, x=x, y_net=y_sub,
                                   fit_full_window=fit_full_window)

    try:
        result = composite.fit(y_sub, params, x=x, weights=weights,
                               method="leastsq", nan_policy="omit",
                               max_nfev=max_nfev)
        if (not result.success and result.chisqr is not None
                and np.isfinite(result.chisqr)):
            # ONE warm restart (Stage-2, measured on the real diagnosis
            # scans): a model whose optimum sits against parameter bounds
            # stalls MINPACK on a flat transformed gradient — it reaches
            # the minimum, then burns the whole nfev budget without
            # satisfying ftol (success=False at a genuinely converged
            # χ²).  Restarting AT the exit point resets leastsq's internal
            # diag scaling and it certifies in tens of evaluations
            # (measured: 6000 nfev burned cold → 33 nfev warm, identical
            # χ²).  Fires ONLY on a failed-but-finite fit, so converging
            # fits are byte-identical; cost is bounded by one
            # WARM_RESTART_MAX_NFEV fit.
            retry = composite.fit(y_sub, result.params.copy(), x=x,
                                  weights=weights, method="leastsq",
                                  nan_policy="omit",
                                  max_nfev=WARM_RESTART_MAX_NFEV)
            if retry.success:
                result = retry
    except Exception as exc:
        log.debug("fit_candidate failed for %s: %s", model.name, exc)
        return FitOutcome(
            converged=False, components=[], residual_sum_sq=float("inf"),
            weighted_chi_sq=float("inf"),
            n_params=len([q for q in params.values() if q.vary]),
            n_data=len(y_sub), lmfit_result=None, background=bg,
        )

    unweighted_r = y_sub - result.best_fit
    return FitOutcome(
        converged=bool(result.success),
        components=_extract_fitted_components(result, model),
        residual_sum_sq=float(np.sum(unweighted_r ** 2)),
        weighted_chi_sq=float(result.chisqr) if result.chisqr is not None else float("inf"),
        n_params=result.nvarys,
        n_data=len(y_sub),
        lmfit_result=result,
        background=bg,
        boundary_hits=_detect_boundary_hits(result.params, model),
    )


def compute_slot_areas(
    model: CandidateModel, primary: FitOutcome, x: np.ndarray
) -> dict[str, float]:
    if primary.lmfit_result is None:
        return {}
    composite = primary.lmfit_result.model
    params = primary.lmfit_result.params
    out: dict[str, float] = {}
    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        sub = next((c for c in composite.components if c.prefix == prefix), None)
        if sub is None:
            continue
        out[slot.role] = float(abs(trapezoid(sub.eval(params, x=x), x)))
    return out


def perturb_initial_params(
    model: CandidateModel,
    seed: int,
    position_jitter_eV: float = 0.15,
    fwhm_jitter_frac: float = 0.20,
    amplitude_jitter_frac: float = 0.30,
    x: Optional[np.ndarray] = None,
    y_net: Optional[np.ndarray] = None,
    fit_full_window: bool = False,
) -> Parameters:
    """
    Perturbed starting parameters for a multi-start refit (bounds-clipped).

    Port improvement over fitalg: when (x, y_net) are provided the defaults
    are data-informed — in particular the amplitude UPPER bound scales with
    the spectrum instead of the fixed 1e5 fallback, which silently clamped
    (and systematically failed) stability refits on peaks brighter than 1e5
    counts (e.g. the UCl4-BN N 1s line at ~1.06e5).
    """
    rng = np.random.default_rng(seed)
    params = _default_params_from_slots(model, x=x, y_net=y_net,
                                        fit_full_window=fit_full_window)

    def _clip(par, new_val: float) -> None:
        lo = par.min if np.isfinite(par.min) else -np.inf
        hi = par.max if np.isfinite(par.max) else np.inf
        par.set(value=float(np.clip(new_val, lo, hi)))

    for slot in model.slots:
        prefix = _slot_prefix(slot.role)
        if slot.linked_to is None:

2026-07-20T19:25:11.092867Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The ranker path lines up with the test’s expectation: `unphysical_widths` disqualifies the report from the clean set, and with `allow_conditional=True` the fallback reason becomes `no_clean_survivor`. I’m now doing final line-number checks for the report.
exec
/bin/zsh -lc "sed -n '1590,1745p' autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
    proposal_pass_timings: list[ProposalPassTiming] = field(default_factory=list)
    # True when the leading survivor is constraint-limited.  Reason:
    #   'no_clean_survivor'  — nothing passed plausibility cleanly; the
    #                          stable-but-boundary-limited tier is ranked.
    #   'decisive_override'  — clean survivors exist but a bound-fixed refit
    #                          of a boundary-limited candidate dominates them
    #                          (see CONDITIONAL_OVERRIDE_DELTA_BIC); clean
    #                          survivors remain as ranked alternatives.
    # Never silent (spec stance: best-evidenced proposal + honest
    # uncertainty, not a dead end).
    conditional: bool = False
    conditional_reason: Optional[str] = None
    # The ambiguity threshold ACTUALLY used for ambiguous_pairs — consumers
    # (criteria panel) must reuse it so the payload can never disagree with
    # the ranking (Codex Stage-2 re-review finding #1).
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY
    # A filtered candidate whose BIC* beats the winner's by more than the
    # decisive threshold — {name, bic_star, delta_bic_vs_winner,
    # filter_reason} or None.  Stress-suite finding 0: evidence burial must
    # be machine-visible at the result level.
    filtered_dominant_alternative: Optional[dict] = None
    # The weighted-χ² criterion (consistent with the fit weights) prefers a
    # DIFFERENT survivor than the ranking's RSS-form BIC* — {rss_bic_top,
    # weighted_bic_top, note} or None (BIC/IC math review blocker:
    # selection must not silently rest on a likelihood the fits reject).
    weighted_ic_disagreement: Optional[dict] = None
    # Set when the sweep hit TOTAL_ANALYSIS_TIMEOUT_SEC and stopped before
    # evaluating every candidate in the grammar. The candidates evaluated so
    # far are still ranked/reported normally (best-so-far) — this only flags
    # that the comparison is partial, so a slow/pathological spectrum
    # returns an honest incomplete result instead of a request timeout.
    analysis_truncated: bool = False
    n_candidates_evaluated: int = 0
    n_candidates_total: int = 0
    # Pre-fit out-of-grammar dominant seeding (unit F1): the detected
    # features every candidate was augmented with, incl. the gate values
    # (UNVERIFIED tunables) — empty when detection found nothing, in which
    # case the candidate set ran unmodified.
    preseeded_features: list[dict] = field(default_factory=list)
    # Two-phase sweep record (unit F3) — None when the classic single-phase
    # path ran (candidate set ≤ SCREEN_TOP_K).  Otherwise every candidate's
    # screen outcome: {name, converged, bic, selected} — screened-out
    # candidates are visible here and can never be survivors.
    screen: Optional[list[dict]] = None
    # Candidate-generation layer (autofit.candidates): the OVERCOMPLETE,
    # provenance-tagged detection pool payload — every feature any source
    # (local_max / curvature_shoulder / residual_gap / grammar) proposed,
    # with per-feature gate outcomes and seeding decisions.  None when the
    # layer did not run (enable_preseed=False or no candidates).
    candidate_pool: Optional[dict] = None


def rank_and_filter(
    reports: list[ModelReport],
    persistence_threshold: float = DEFAULT_PERSISTENCE_THRESHOLD,
    bic_ambiguity_threshold: float = DEFAULT_BIC_AMBIGUITY,
    allow_conditional: bool = True,
    allow_last_resort: bool = False,
) -> ComparisonResult:
    """
    Filter (plausibility, active persistence) then rank (χ²ᵣ, BIC*).

    Two-tier semantics (departure from fitalg, which returned zero survivors
    whenever every candidate had any boundary hit — routine on real composite
    samples): when NO candidate passes plausibility cleanly but some are
    otherwise stable, those are ranked as a CONDITIONAL tier with
    ``result.conditional = True`` and every violation preserved.  Stability
    failures are never promoted — an unstable fit is pathology, not a
    constraint conflict.
    """
    filtered_out: list[tuple[ModelReport, str]] = []
    survivors: list[ModelReport] = []
    conditional_pool: list[ModelReport] = []

    for r in reports:
        active_min = r.active_min_persistence
        stable = active_min >= persistence_threshold
        if r.plausibility.boundary_hits or r.plausibility.unphysical_widths \
                or r.plausibility.orphan_peaks:
            # orphan_peaks included (Codex Stage-2 re-review finding #3):
            # refits repeatedly producing unmatched components is a
            # plausibility violation, not clean-survivor material.
            filtered_out.append((r, f"plausibility: {r.plausibility}"))
            if stable:
                conditional_pool.append(r)
            continue
        if not stable:
            absent_roles = [a.role for a in r.absent_slots]
            extra = f"  (absent slots excluded: {absent_roles})" if absent_roles else ""
            filtered_out.append((r, f"stability: active min persistence "
                                    f"{active_min:.2f} < {persistence_threshold}{extra}"))
            continue
        survivors.append(r)

    conditional = False
    conditional_reason = None
    if allow_conditional and conditional_pool and not survivors:
        survivors = conditional_pool
        conditional = True
        conditional_reason = "no_clean_survivor"
    elif allow_conditional and allow_last_resort and not survivors and reports:
        # LAST-RESORT tier (Stage-2, 2026-07-10; measured on real low-res
        # Fe 2p): fires ONLY when the caller says detection found real
        # structure (allow_last_resort = detection seeds exist) — its job
        # is rescuing DETECTED structure from selection instability, never
        # forcing an answer on featureless data (a flat-noise grammar fit
        # can converge; the honest result there stays no-survivor).
        # Every candidate failed BOTH tiers — typically cross-refit
        # label instability (orphan_peaks) on heavily-overlapped low-res
        # structure.  For a suggest-a-profile tool an EMPTY answer is the
        # worst answer: emit the single best CONVERGED model, loudly
        # flagged unstable.  This tier exists only when clean and
        # conditional are BOTH empty — stability failures are still never
        # preferred over anything (the original design rule stands).
        viable = [r for r in reports
                  if r.primary_fit.converged
                  and np.isfinite(r.bic_adjusted)]
        if viable:
            best = min(viable,
                       key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))
            survivors = [best]
            conditional = True
            conditional_reason = "unstable_last_resort"
    # NOTE: the decisive-override path (clean survivors exist but a
    # bound-fixed refit of a conditional candidate dominates) lives in
    # compare_models — it needs the spectrum to refit; rank_and_filter is
    # pure ranking.

    # BIC* is the ranking default (spec §6); χ²ᵣ breaks ties only.  fitalg
    # ranked (χ²ᵣ, BIC*) — spec-noncompliant, changed per Codex finding #3.
    survivors.sort(key=lambda r: (r.bic_adjusted, r.reduced_chi_sq))

    ambiguous: list[tuple[str, str, str]] = []
    for i in range(len(survivors)):
        for j in range(i + 1, len(survivors)):
            a, b = survivors[i], survivors[j]
            if abs(a.bic_adjusted - b.bic_adjusted) <= bic_ambiguity_threshold \
               and a.model.n_components != b.model.n_components:
                diff = {s.role for s in a.model.slots} ^ {s.role for s in b.model.slots}
                ambiguous.append((
                    a.model.name, b.model.name,
                    f"Indistinguishable on fit quality and BIC* "
                    f"(ΔBIC*={abs(a.bic_adjusted - b.bic_adjusted):.2f}); "
                    f"structural difference: {diff}",
                ))
    return ComparisonResult(
        reports=reports, survivors=survivors,
        filtered_out=filtered_out, ambiguous_pairs=ambiguous,
        conditional=conditional, conditional_reason=conditional_reason,
        bic_ambiguity_threshold=bic_ambiguity_threshold,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Pre-fit out-of-grammar dominant seeding (unit F1 — see the constants block)
# ─────────────────────────────────────────────────────────────────────────────

exec
/bin/zsh -lc "nl -ba tests/autofit/test_c1s_mixed_material_class.py | sed -n '150,315p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba templates/index.html | sed -n '13010,13036p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba autofit/regions/c1s.py | sed -n '236,390p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
 13010	
 13011	// ═══ ALL user-facing wording lives HERE (one place, easy to iterate). ═══
 13012	// Audience: bench chemists/spectroscopists. Engine jargon (grammar,
 13013	// candidate-model, decisive_override, +bfix, role slugs) must never reach
 13014	// the screen — the honest CONTENT stays, said plainly.
 13015	const FP_STRINGS = {
 13016	  blurb: 'Suggests a set of peaks for the region(s) you select and shows ' +
 13017	         'how confident it is. These are <b>starting suggestions to ' +
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

 succeeded in 0ms:
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

2026-07-20T19:25:20.451854Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
I have enough to decide now. I’m pulling exact references for the implementation points so the final verdict is tied to file and line, even though there are no actionable findings.
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '753,850p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '1642,1695p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba autofit/regions/c1s.py | sed -n '388,445p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba app.py | sed -n '243,255p' && nl -ba tests/test_api_analyze.py | sed -n '208,232p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

2026-07-20T19:25:28.752080Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "rg -n \"MaterialClass\\.MIXED|material_class is MaterialClass|material_class == MaterialClass|\\.material_class\" autofit app.py templates tests | head -200" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
templates/index.html:13430:  mat.innerHTML = _fpMeta.material_classes
tests/test_api_analyze.py:176:    """MaterialClass.MIXED (2026-07-20 unit) round-trips through the
tests/test_api_analyze.py:215:    only ever reaches Phase.material_class, consumed by grammar
autofit/grammar.py:402:                f"{chosen.material_class.value}) — derived structure only")
autofit/grammar.py:436:            f"{slug}: phase {chosen.id!r} ({chosen.material_class.value}"
autofit/coverage.py:124:    "user-overridable: the declared Phase.material_class wins."
autofit/coverage.py:405:                   "Phase.material_class wins)"},
autofit/regions/c1s.py:128:    if material_class is MaterialClass.MIXED:
autofit/regions/c1s.py:244:             "value": "under MaterialClass.MIXED (analyte embedded in a "
autofit/regions/c1s.py:306:        contam_fwhm = _contamination_fwhm_range(phase.material_class)
tests/autofit/test_c1s_mixed_material_class.py:98:    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
tests/autofit/test_c1s_mixed_material_class.py:118:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:139:    g_mixed = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:194:    slots = _contamination_slots(_resolve(MaterialClass.MIXED))
tests/autofit/test_c1s_mixed_material_class.py:216:    g = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:251:    g = _resolve(MaterialClass.MIXED)
tests/autofit/test_c1s_mixed_material_class.py:305:    g = _resolve(MaterialClass.MIXED)

exec
/bin/zsh -lc "git show --name-only --format='' bdc909a | sed '/"'^$/d'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-dOV87Zcc' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-MHr3Gnow' (errno=Operation not permitted)
templates/index.html
tests/autofit/test_c1s_mixed_material_class.py
tests/js/fp_material_mixed.test.js

2026-07-20T19:25:57.265961Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
**Findings**

1. No BLOCKER/MAJOR/MINOR findings.

**Verification Notes**

The regression tests are not laundered. For `tests/autofit/test_c1s_mixed_material_class.py:209`, an 8.0 eV MIXED `contamination_CO` slot has `fwhm_range=(0.8, 15.0)` and `broad_justification is None`. Under the old numeric rule, `declared_hi > 2.0` would mark it vouched and return no flag. Under the current rule in `autofit/engine.py:790`, vouching depends only on `slot.broad_justification`, so the same component flags at `autofit/engine.py:845`.

Shared-width handling checks out. `_unphysical_width_flags` iterates fitted components independently by `slot_role` at `autofit/engine.py:784`, and the A-linked, offset-linked, and AG-linked C 1s slots all retain individual non-vouched contamination slots from `autofit/regions/c1s.py:379`, `:384`, and `:402`. I do not see a path where a wide shared contamination width becomes one shared exemption. `B*_linked` uses an aliphatic-width expression rather than `_SHARED_CONTAM_FWHM`, but those slots are also non-vouched, so wide reported components still flag.

The provenance digit guard is correctly aimed: `"relax to 3.5 eV based on our spectra"` fails `any(ch.isdigit()...)`, while the actual `mixed_material_class_width_relaxation` value at `autofit/regions/c1s.py:244` contains no digits. The DOI/year digits remain in `source`, not `value`.

Frontend copy at `templates/index.html:13030` now scopes relaxation to C 1s contamination/adventitious widths, says other regions are unaffected, and explicitly says it does not correct charge uncertainty. `rg` shows `MaterialClass.MIXED` affects only `autofit/regions/c1s.py`. Charge correction remains isolated: `app.py:253` computes `corrected = energy - cc_shift` before grammar construction, and the unchanged API test checks conductor vs mixed arrays at `tests/test_api_analyze.py:208`.

Diff scope is exactly the three claimed files. I could run the JS material-copy test successfully; Python pytest execution was blocked by this read-only sandbox/no writable tempdir plus missing default-interpreter deps, so the Python claims above are from close source tracing and the importable provenance check.

VERDICT: GO
tokens used
82,491
**Findings**

1. No BLOCKER/MAJOR/MINOR findings.

**Verification Notes**

The regression tests are not laundered. For `tests/autofit/test_c1s_mixed_material_class.py:209`, an 8.0 eV MIXED `contamination_CO` slot has `fwhm_range=(0.8, 15.0)` and `broad_justification is None`. Under the old numeric rule, `declared_hi > 2.0` would mark it vouched and return no flag. Under the current rule in `autofit/engine.py:790`, vouching depends only on `slot.broad_justification`, so the same component flags at `autofit/engine.py:845`.

Shared-width handling checks out. `_unphysical_width_flags` iterates fitted components independently by `slot_role` at `autofit/engine.py:784`, and the A-linked, offset-linked, and AG-linked C 1s slots all retain individual non-vouched contamination slots from `autofit/regions/c1s.py:379`, `:384`, and `:402`. I do not see a path where a wide shared contamination width becomes one shared exemption. `B*_linked` uses an aliphatic-width expression rather than `_SHARED_CONTAM_FWHM`, but those slots are also non-vouched, so wide reported components still flag.

The provenance digit guard is correctly aimed: `"relax to 3.5 eV based on our spectra"` fails `any(ch.isdigit()...)`, while the actual `mixed_material_class_width_relaxation` value at `autofit/regions/c1s.py:244` contains no digits. The DOI/year digits remain in `source`, not `value`.

Frontend copy at `templates/index.html:13030` now scopes relaxation to C 1s contamination/adventitious widths, says other regions are unaffected, and explicitly says it does not correct charge uncertainty. `rg` shows `MaterialClass.MIXED` affects only `autofit/regions/c1s.py`. Charge correction remains isolated: `app.py:253` computes `corrected = energy - cc_shift` before grammar construction, and the unchanged API test checks conductor vs mixed arrays at `tests/test_api_analyze.py:208`.

Diff scope is exactly the three claimed files. I could run the JS material-copy test successfully; Python pytest execution was blocked by this read-only sandbox/no writable tempdir plus missing default-interpreter deps, so the Python claims above are from close source tracing and the importable provenance check.

VERDICT: GO
