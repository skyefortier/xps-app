2026-07-20T18:54:52.960469Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 86 column 5
OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f80e1-8f1c-7970-9207-c67157e4b573
--------
user
You are an adversarial reviewer for a follow-up fix in this repo (XPS
peak-fitting web app), branch feature-autofit-stage2. Review commit
ad7e668 ("fix(autofit): _retag_slot silently dropped broad_justification
during composition") -- `git show ad7e668` gives the full diff. This is a
recheck: both prior Codex reviews of commit 5070662 (the
broad_justification refactor) independently found the exact bug this
commit fixes, and the human maintainer specified the fix. Your job is to
verify the fix actually closes the finding and to hunt for the SAME class
of regression recurring elsewhere -- not to re-litigate whether a fix was
needed.

THE ORIGINAL FINDING (round 1, both runs independently): autofit/
grammar.py's _retag_slot -- called by resolve() whenever it composes a
multi-region joint co-fit (e.g. this lab's real U 4f + N 1s co-fit for
UCl4-in-BN samples) -- reconstructed each ComponentSlot by manually
re-listing every field. ComponentSlot.broad_justification wasn't in that
list, so every slot passing through composition silently lost its
exemption from autofit/engine.py's _unphysical_width_flags, regardless of
what the source region module had set. Confirmed via:

    resolve([Phase(id='UCl4', material_class=MaterialClass.INSULATOR,
                    regions=('U 4f',)),
             Phase(id='BN', material_class=MaterialClass.INSULATOR,
                    regions=('N 1s',))],
            ['U 4f', 'N 1s'])

    -> U4f__main_u4f72 (1.5, 3.5) broad_justification=None  (BUG: should
       be set, matching the un-composed U 4f module's own main_u4f72)

THE FIX (ad7e668): _retag_slot now returns
`dataclasses.replace(s, role=..., linked_to=..., fwhm_linked_to=...)`
instead of manually reconstructing ComponentSlot field-by-field.
ComponentSlot is frozen; replace() carries every field NOT explicitly
overridden forward unchanged.

ALSO IN THIS COMMIT: tests/autofit/test_broad_justification.py's
EXEMPTION_FIXTURE extended to cover U 4f satellite-pair variants
(U1_mains_satpair, U1b_mains_satpair_freesep, U2_mains_satfree -- round
1's own MINOR finding said the original fixture missed exactly these); a
new COMPOSED_EXEMPTION_FIXTURE exercising the real U 4f + N 1s scenario
across every composed candidate name/role; and a new class-level
structural guard, test_retag_slot_preserves_all_fields_except_the_three_
rewritten, driven off dataclasses.fields(ComponentSlot) rather than a
hardcoded field list.

ADVERSARIAL QUESTIONS -- ATTACK THESE SPECIFICALLY:

(a) VERIFY THE FIX ACTUALLY CLOSES THE ORIGINAL FINDING. Reproduce the
    exact repro above yourself (or read _retag_slot's new body closely
    enough to be certain) and confirm U4f__main_u4f72 (and every other
    previously-exempt slot: U4f__main_u4f52, N1s__main_n1s,
    U4f__satellite_u4f72, U4f__satellite_u4f52 in the satellite-pair
    composed candidates) now carries broad_justification through
    composition, matching what the un-composed region module sets.

(b) HUNT THE SAME REGRESSION CLASS AGAIN, NOW THAT THE FIXTURE IS WIDER.
    Is _retag_slot really the ONLY place in the codebase that copies-and-
    modifies an existing ComponentSlot (as opposed to constructing a
    fresh one from scratch)? Grep for every `ComponentSlot(` construction
    site and every place that takes an existing `ComponentSlot` instance
    and produces a modified copy of it (dataclasses.replace, manual
    reconstruction, or otherwise). If there is a SECOND such site the
    original two reviews and this fix all missed, that's a live instance
    of the same bug class, not a hypothetical. Also check: does ANY
    combination of phases/regions produce a composed candidate not
    covered by COMPOSED_EXEMPTION_FIXTURE or EXEMPTION_FIXTURE where a
    slot that SHOULD be exempt (declared broad_justification in its
    source region module) fails to carry it through? Try at least one
    combination neither fixture covers (e.g. C 1s + another region, or a
    3-phase composition) if resolve() supports it.

(c) VERIFY THE STRUCTURAL GUARD ACTUALLY GUARDS. Take
    test_retag_slot_preserves_all_fields_except_the_three_rewritten and
    confirm it would have caught the ORIGINAL bug: revert _retag_slot to
    its pre-ad7e668 manual-reconstruction form (git show
    5070662:autofit/grammar.py has it, or read the diff in ad7e668
    backwards) and confirm the test fails against that reverted version.
    Don't just read the test and assume it works -- actually exercise the
    logic (mentally or by running Python if your sandbox allows) against
    both the old and new _retag_slot bodies.

(d) THE OTHER 3 SLOT-CONSTRUCTION SITES. The commit message claims
    autofit/engine.py's _preseed_augmented and _augmented_candidate
    (proposal) construct fresh ComponentSlots with fwhm_range=
    (PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX), and PROPOSAL_FWHM_MAX ==
    FWHM_MAX_ORDINARY_EV == 2.0 -- so declared_hi was never > 2.0 and
    these were never exempt under the OLD numeric rule either, meaning
    zero behavior change from this whole refactor+fix pair. Verify this
    claim directly: check PROPOSAL_FWHM_MAX's actual value and confirm
    it equals FWHM_MAX_ORDINARY_EV exactly (not just approximately). Also
    verify autofit/candidates.py's detection slots (role prefix
    "detected_peak_") really do return early in
    _unphysical_width_flags before the broad_justification check, for
    every code path (not just the common case) -- read the function's
    control flow directly rather than trusting the commit message's
    characterization.

(e) SCOPE. Confirm ad7e668's diff touches only autofit/grammar.py and
    tests/autofit/test_broad_justification.py.

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll inspect the target commit and the relevant construction paths first, then run focused tests or small Python probes where the read-only sandbox permits execution. I’ll keep this as a review: findings first, and I’ll only call out concrete regressions.
exec
/bin/zsh -lc 'git show --stat --oneline ad7e668 && git show --name-only --format=fuller ad7e668' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-F9G5k7Cg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-pOUZStCW' (errno=Operation not permitted)
ad7e668 fix(autofit): _retag_slot silently dropped broad_justification during composition
 autofit/grammar.py                        |  33 +++++----
 tests/autofit/test_broad_justification.py | 113 +++++++++++++++++++++++++++++-
 2 files changed, 130 insertions(+), 16 deletions(-)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iqOid1wf' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-YcVKz71t' (errno=Operation not permitted)
commit ad7e6683f5a64e0fb12c15e42a9423821e02d731
Author:     Skye Fortier <skyefortier@gmail.com>
AuthorDate: Mon Jul 20 12:53:49 2026 -0600
Commit:     Skye Fortier <skyefortier@gmail.com>
CommitDate: Mon Jul 20 12:53:49 2026 -0600

    fix(autofit): _retag_slot silently dropped broad_justification during composition
    
    Both Codex reviews of 5070662 (the broad_justification refactor)
    independently caught the same MAJOR: _retag_slot (used by resolve()
    whenever it composes a multi-region joint co-fit, e.g. this lab's real
    U 4f + N 1s co-fit for UCl4-in-BN samples) reconstructed each
    ComponentSlot by manually re-listing every field. broad_justification
    wasn't in that list, so it silently defaulted back to None for every
    slot passing through composition — every previously-exempt slot (U 4f
    mains, U 4f satellites, N 1s main, in any joint model) lost its
    exemption and started getting flagged as unphysical, purely as an
    artifact of going through resolve() with more than one region. Verified
    independently before accepting the finding:
    
        resolve([UCl4(U 4f), BN(N 1s)], ["U 4f", "N 1s"])
        -> U4f__main_u4f72 (1.5, 3.5) broad_justification=None  (should be set)
    
    Fix: dataclasses.replace(s, role=..., linked_to=..., fwhm_linked_to=...)
    instead of manual field listing. ComponentSlot is frozen, so replace()
    is the idiomatic approach — it carries every field NOT explicitly
    overridden forward unchanged, including any field added to ComponentSlot
    after this function was written. This closes not just today's instance
    but the whole class of bug: the manual-reconstruction pattern is exactly
    how broad_justification got lost, and would silently lose the next field
    too.
    
    Test coverage, per the two gaps Codex's own round-1 review named:
    
    - EXEMPTION_FIXTURE (tests/autofit/test_broad_justification.py) extended
      to cover the U 4f satellite-pair variants (U1_mains_satpair,
      U1b_mains_satpair_freesep, U2_mains_satfree) — the original fixture
      only covered U0_mains, exactly where this bug's blast radius was
      invisible to the existing safety net.
    - New COMPOSED_EXEMPTION_FIXTURE exercises the real U 4f + N 1s co-fit
      scenario both Codex reviews used to demonstrate the bug, across every
      composed candidate name and role.
    - New test_retag_slot_preserves_all_fields_except_the_three_rewritten:
      a class-level structural guard, not another point fix. Driven off
      dataclasses.fields(ComponentSlot) rather than a hardcoded field list,
      so it automatically covers any field added to ComponentSlot later —
      confirmed to actually catch the original bug (fails against a
      reverted, manually-reconstructing _retag_slot).
    
    Verified the other 3 slot-construction sites are unaffected, as
    expected: autofit/engine.py's pre-seed (_preseed_augmented) and proposal
    (_augmented_candidate) slots use fwhm_range=(PROPOSAL_FWHM_MIN,
    PROPOSAL_FWHM_MAX), and PROPOSAL_FWHM_MAX == FWHM_MAX_ORDINARY_EV == 2.0
    — declared_hi is never > 2.0, so these were never exempt under the old
    numeric rule either, no behavior change either way. autofit/candidates.py's
    detection slots (role prefix detected_peak_) return early via
    _unphysical_width_flags' own scale-relative branch, before the
    broad_justification check is ever reached.
    
    Full suite: 747 passed, 6 skipped, 1 failed (test_u4f_n1s_cofit — a
    pre-existing timing/hash-seed-sensitive flake; same test exercises the
    REAL U 4f + N 1s composed co-fit this fix targets, failed with the
    byte-identical known signature, and passed cleanly on an immediate
    rerun with zero code changes, confirming flakiness rather than
    regression). RUN_AUTOFIT_GATE=1 gate suite: 10 passed, 2 failed (the
    same test_u4f_n1s_cofit flake plus the already-known
    test_candidate_pool_real_gate.py ds8 timing-budget flake, both
    byte-identical to prior confirmed instances).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

autofit/grammar.py
tests/autofit/test_broad_justification.py

exec
/bin/zsh -lc "git status --short && git branch --show-current && rg -n \"ComponentSlot\\(|dataclasses\\.replace|replace\\(|_retag_slot|broad_justification|_unphysical_width_flags|PROPOSAL_FWHM_MAX|FWHM_MAX_ORDINARY_EV\" autofit tests/autofit" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-mWHtDOZk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-0O1UxQwu' (errno=Operation not permitted)
 M templates/index.html
 M tests/autofit/test_c1s_mixed_material_class.py
 M tests/js/fp_material_mixed.test.js
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-IMLTEG2r' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Xg9s3Smh' (errno=Operation not permitted)
feature-autofit-stage2
autofit/candidates.py:73:# 2.4 eV (just above FWHM_MAX_ORDINARY_EV = 2.0, the engine's ordinary-
autofit/candidates.py:463:        slots.append(ComponentSlot(
tests/autofit/test_cl2p_freewidth.py:131:    return ComponentSlot(role=role, **defaults)
tests/autofit/test_resolver.py:107:        main = ComponentSlot(
tests/autofit/test_resolver.py:112:        doublet = ComponentSlot(
tests/autofit/test_broad_justification.py:10:``autofit/engine.py``'s ``_unphysical_width_flags`` used to infer (2) from
tests/autofit/test_broad_justification.py:11:(1) via a bare numeric test (``declared_hi > FWHM_MAX_ORDINARY_EV``). The
tests/autofit/test_broad_justification.py:20:The fix: ``ComponentSlot.broad_justification`` makes meaning (2) an
tests/autofit/test_broad_justification.py:21:explicit, independent field. ``_unphysical_width_flags`` keys its
tests/autofit/test_broad_justification.py:22:exemption off ``broad_justification is not None``, never off the bound's
tests/autofit/test_broad_justification.py:33:from autofit.engine import FittedComponent, _unphysical_width_flags
tests/autofit/test_broad_justification.py:37:# (declared_hi > FWHM_MAX_ORDINARY_EV == 2.0 eV, the pre-refactor rule),
tests/autofit/test_broad_justification.py:97:# autofit.grammar._retag_slot, which used to reconstruct each ComponentSlot
tests/autofit/test_broad_justification.py:98:# by manually re-listing every field -- broad_justification wasn't in that
tests/autofit/test_broad_justification.py:100:# switching _retag_slot to dataclasses.replace(). This fixture exercises the
tests/autofit/test_broad_justification.py:130:def test_composed_candidate_preserves_broad_justification(
tests/autofit/test_broad_justification.py:133:    OWN region module must stay that way after _retag_slot composes it into
tests/autofit/test_broad_justification.py:137:        assert slot.broad_justification is not None, (
tests/autofit/test_broad_justification.py:138:            f"{candidate_name}/{role} lost its broad_justification during "
tests/autofit/test_broad_justification.py:139:            "multi-region composition (_retag_slot regression)"
tests/autofit/test_broad_justification.py:142:        assert slot.broad_justification is None
tests/autofit/test_broad_justification.py:145:def test_retag_slot_preserves_all_fields_except_the_three_rewritten():
tests/autofit/test_broad_justification.py:146:    """Structural guard against this bug class recurring: _retag_slot must
tests/autofit/test_broad_justification.py:154:    from autofit.grammar import ComponentSlot, _retag_slot
tests/autofit/test_broad_justification.py:174:        "broad_justification": "sentinel justification text",
tests/autofit/test_broad_justification.py:183:    original = ComponentSlot(**sentinel_by_field)
tests/autofit/test_broad_justification.py:185:    retagged = _retag_slot(original, rename, shared_rename={})
tests/autofit/test_broad_justification.py:191:            f"_retag_slot lost field {name!r}: "
tests/autofit/test_broad_justification.py:200:def test_exemption_fixture_matches_broad_justification(
tests/autofit/test_broad_justification.py:202:    """Each currently-exempt slot must carry a real broad_justification;
tests/autofit/test_broad_justification.py:208:        assert slot.broad_justification is not None, (
tests/autofit/test_broad_justification.py:219:        assert slot.broad_justification is None, (
tests/autofit/test_broad_justification.py:233:    """Minimal stand-in for CandidateModel -- _unphysical_width_flags only
tests/autofit/test_broad_justification.py:243:    """The actual OUTPUT of _unphysical_width_flags for a component fitted
tests/autofit/test_broad_justification.py:253:    flags = _unphysical_width_flags([comp], cand)
tests/autofit/test_broad_justification.py:270:    been auto-exempt under the old numeric rule) but broad_justification
tests/autofit/test_broad_justification.py:276:    wide_no_justification = ComponentSlot(
tests/autofit/test_broad_justification.py:279:        fwhm_range=(0.8, 15.0), broad_justification=None,
tests/autofit/test_broad_justification.py:284:    flags = _unphysical_width_flags([comp], model)
tests/autofit/test_broad_justification.py:286:        "a slot with a wide bound but NO broad_justification must still "
tests/autofit/test_broad_justification.py:293:    """Mirror case: an explicit broad_justification grants exemption even
tests/autofit/test_broad_justification.py:299:    narrow_but_justified = ComponentSlot(
tests/autofit/test_broad_justification.py:302:        fwhm_range=(0.5, 2.0), broad_justification="synthetic test justification",
tests/autofit/test_broad_justification.py:307:    flags = _unphysical_width_flags([comp], model)
tests/autofit/test_broad_justification.py:309:        "an explicit broad_justification must exempt a slot even when its "
tests/autofit/test_broad_justification.py:314:def test_component_slot_broad_justification_defaults_to_none():
tests/autofit/test_broad_justification.py:317:    s = ComponentSlot(role="r", region="Test", phase_id="s",
tests/autofit/test_broad_justification.py:320:    assert s.broad_justification is None
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
autofit/engine.py:1867:                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
autofit/engine.py:1901:        ComponentSlot(
autofit/engine.py:1907:            fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2068:                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
autofit/engine.py:2110:    proposed = ComponentSlot(
autofit/engine.py:2116:        fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2318:            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
autofit/engine.py:2446:        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
autofit/engine.py:2457:            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
autofit/engine.py:2633:                fwhm_clip=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2830:                unphysical_widths=_unphysical_width_flags(primary.components, model),
tests/autofit/test_preseed_dominants.py:154:        assert p["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6, \
tests/autofit/test_preseed_dominants.py:160:def test_unphysical_width_flags_helper():
tests/autofit/test_preseed_dominants.py:163:    ``broad_justification``, e.g. a satellite) are NOT.
tests/autofit/test_preseed_dominants.py:165:    2026-07-20 (Unit A, broad_justification refactor): the exemption used
tests/autofit/test_preseed_dominants.py:172:    Updated to set broad_justification explicitly, matching how every real
tests/autofit/test_preseed_dominants.py:178:    def slot(role, lo, hi, broad_justification=None):
tests/autofit/test_preseed_dominants.py:179:        return ComponentSlot(role=role, region="r", phase_id="p",
tests/autofit/test_preseed_dominants.py:182:                             broad_justification=broad_justification)
tests/autofit/test_preseed_dominants.py:191:             broad_justification="synthetic: pi->pi* shake-up, physically broad"),
tests/autofit/test_preseed_dominants.py:193:    flags = eng._unphysical_width_flags(
tests/autofit/test_preseed_dominants.py:203:    assert eng._unphysical_width_flags([comp("contamination_CO", 1.5)], m) == []
tests/autofit/test_preseed_dominants.py:206:def test_unphysical_width_flags_wide_range_alone_no_longer_exempts():
tests/autofit/test_preseed_dominants.py:208:    declared fwhm_range but NO broad_justification must be flagged when it
tests/autofit/test_preseed_dominants.py:216:    slot = ComponentSlot(role="wide_unvouched", region="r", phase_id="p",
tests/autofit/test_preseed_dominants.py:222:    flags = eng._unphysical_width_flags([comp], m)
tests/autofit/test_preseed_dominants.py:236:    assert seeded.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
tests/autofit/test_preseed_dominants.py:243:    assert aug.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
tests/autofit/test_preseed_dominants.py:269:    assert p["fitted_fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6   # NOT 3 eV
tests/autofit/test_preseed_dominants.py:278:            assert pk["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6
tests/autofit/test_preseed_dominants.py:293:    slot = ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
tests/autofit/test_preseed_dominants.py:335:    promoted = dataclasses.replace(
tests/autofit/test_preseed_dominants.py:397:        return ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
tests/autofit/test_bayesian_real_gate.py:72:    assert ic.diagnostics["winner"].replace("+bfix", "") == \
tests/autofit/test_fit_full_window_option.py:41:    return ComponentSlot(role=role, region=region, phase_id="p",
tests/autofit/stress_cases.py:108:    return ComponentSlot(role=role, region=REGION, phase_id=PHASE,
autofit/grammar.py:172:    # autofit.engine._unphysical_width_flags must not exempt it, REGARDLESS
autofit/grammar.py:176:    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
autofit/grammar.py:181:    broad_justification: Optional[str] = None
autofit/grammar.py:469:    sanitized = [re.sub(r"[^A-Za-z0-9_]", "", s.replace(" ", ""))
autofit/grammar.py:568:            slug = re.sub(r"[^A-Za-z0-9_]", "", slug.replace(" ", ""))
autofit/grammar.py:572:                slots.append(_retag_slot(s, rename, shared_rename))
autofit/grammar.py:584:def _retag_slot(
autofit/grammar.py:591:    Uses dataclasses.replace (ComponentSlot is frozen) rather than
autofit/grammar.py:592:    reconstructing the slot field-by-field: replace() carries every field
autofit/grammar.py:595:    reconstruction this replaced was exactly how broad_justification got
autofit/grammar.py:599:    tests/autofit/test_broad_justification.py's
autofit/grammar.py:600:    test_retag_slot_preserves_all_fields_except_the_three_rewritten, which
autofit/grammar.py:616:    return replace(
tests/autofit/test_c1s_mixed_material_class.py:202:# in autofit.engine._unphysical_width_flags, so a MIXED contaminant fitting
tests/autofit/test_c1s_mixed_material_class.py:205:# so the app must not vouch for it). Fixed by Unit A (broad_justification):
tests/autofit/test_c1s_mixed_material_class.py:214:    from autofit.engine import FittedComponent, _unphysical_width_flags
tests/autofit/test_c1s_mixed_material_class.py:219:    assert slot.broad_justification is None, (
tests/autofit/test_c1s_mixed_material_class.py:225:    flags = _unphysical_width_flags([comp], cand)
tests/autofit/test_c1s_mixed_material_class.py:239:    autofit.engine._unphysical_width_flags produces for the 8 eV scenario
tests/autofit/test_c1s_mixed_material_class.py:248:                                _unphysical_width_flags)
tests/autofit/test_c1s_mixed_material_class.py:268:    injected_flags = _unphysical_width_flags([fake_comp], report.model)
tests/autofit/test_c1s_mixed_material_class.py:271:    conditional_report = dataclasses.replace(
tests/autofit/test_sparse_map.py:28:    return ComponentSlot(role=role, region="T", phase_id="t",
tests/autofit/test_fit_physics.py:48:    src = open(GEN).read().replace(
tests/autofit/test_fit_physics.py:50:        f'OUT = {str(out)!r}').replace(
tests/autofit/test_engine_doublet.py:23:    p32 = ComponentSlot(
tests/autofit/test_engine_doublet.py:28:    p12 = ComponentSlot(
tests/autofit/test_engine_doublet.py:127:        return ComponentSlot(
tests/autofit/test_bayesian_method.py:29:    return ComponentSlot(role=role, region="T", phase_id="t",
tests/autofit/test_candidate_pool_real_gate.py:114:        fwhm_clip=(eng.PROPOSAL_FWHM_MIN, eng.PROPOSAL_FWHM_MAX),
tests/autofit/test_criteria.py:23:    return ComponentSlot(role=role, region="T", phase_id="t",
tests/autofit/test_stage2_completeness.py:257:    stab = dataclasses.replace(report.stability, per_slot=bad_slots,
tests/autofit/test_stage2_completeness.py:261:    return dataclasses.replace(report, stability=stab, plausibility=plaus)
tests/autofit/test_stage2_completeness.py:293:    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
tests/autofit/test_stage2_completeness.py:301:    flags = eng._unphysical_width_flags([fat], m)
tests/autofit/test_stage2_completeness.py:306:    assert eng._unphysical_width_flags([thin], m) == []
tests/autofit/test_stage2_completeness.py:317:    slot = ComponentSlot(role="detected_peak_0", region="unassigned",
tests/autofit/test_stage2_completeness.py:327:    assert eng._unphysical_width_flags([comp(4.0)], m), "4.0 ≥ 0.7×5.0"
tests/autofit/test_stage2_completeness.py:328:    assert eng._unphysical_width_flags([comp(3.0)], m) == []
tests/autofit/test_stage2_completeness.py:350:    cond = dataclasses.replace(
tests/autofit/test_stage2_completeness.py:369:    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
tests/autofit/test_stage2_completeness.py:377:    flags = eng._unphysical_width_flags([fat], m)   # eff = 1.7×1.25 = 2.13
tests/autofit/test_stage2_completeness.py:382:    assert eng._unphysical_width_flags([ok], m) == []   # eff = 1.65
autofit/regions/b1s.py:92:            return ComponentSlot(
autofit/regions/b1s.py:96:                broad_justification=(
autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
autofit/regions/n1s.py:80:            broad_justification=_justification,
autofit/regions/n1s.py:82:        ag_main = ComponentSlot(
autofit/regions/n1s.py:87:            broad_justification=_justification,
autofit/regions/c1s.py:309:            return ComponentSlot(
autofit/regions/c1s.py:337:            broad_justification=(
autofit/regions/u4f.py:197:            return ComponentSlot(
autofit/regions/u4f.py:222:            broad_justification=_main_justification,
autofit/regions/u4f.py:231:            broad_justification=_main_justification,
autofit/regions/u4f.py:239:            broad_justification=_sat_justification,
autofit/regions/u4f.py:249:            broad_justification=_sat_justification,
autofit/regions/u4f.py:260:            broad_justification=_sat_justification,
autofit/regions/u4f.py:270:            broad_justification=_sat_justification,
autofit/regions/u4f.py:277:            broad_justification=_sat_justification,
autofit/regions/cl2p.py:143:            return ComponentSlot(
autofit/regions/cl2p.py:147:                broad_justification=_empirical_justification,
autofit/regions/cl2p.py:154:                return ComponentSlot(
autofit/regions/cl2p.py:164:                    broad_justification=_coster_kronig_justification,
autofit/regions/cl2p.py:166:            return ComponentSlot(
autofit/regions/cl2p.py:175:                broad_justification=_empirical_justification,

codex
The commit scope matches the stated two files. The worktree has unrelated local changes, so I’m treating the repository as dirty and reading the committed content directly where line accuracy matters.
exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '130,210p;540,635p'" in /Users/skyefortier/xps-verify
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
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '100,130p;753,850p;1840,1925p;2045,2130p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   100	# justification.  Ordinary C 1s core lines sit at ≲2 eV FWHM (Biesinger,
   101	# Appl. Surf. Sci. 597 (2022) 153681; Greczynski & Hultman 2020); wider is
   102	# defensible ONLY for classes KNOWN to be broad (π→π* and other satellites,
   103	# plasmon/loss features, or a literature-justified case).  This is the
   104	# engine-wide default cap for REGION-UNASSIGNED components — F1 pre-seeded
   105	# out-of-grammar slots and F2/F3 residual proposals — which by construction
   106	# have no region module vouching for a wider physical width.  Region grammar
   107	# slots keep their own cited ranges (C 1s satellite 5.5, U 4f mains 3.5,
   108	# B 1s 2.5, …); those declared maxima ABOVE this ceiling mark a slot as
   109	# grammar-sanctioned-broad and exempt it from the unphysical-width flag.  A
   110	# proposed/pre-seeded peak that PEGS this cap (wants wider than physical with
   111	# no known-broad justification) is NOT silently widened: the fit is held at
   112	# the physical limit and the result is flagged (unphysical_widths →
   113	# conditional/low-confidence), per the fit-quality rail "a defensible fit
   114	# with physical widths beats a lower χ² bought with a fat peak".  UNVERIFIED
   115	# numeric bound (a cap, not a target).
   116	FWHM_MAX_ORDINARY_EV = 2.0
   117	# The proposal/pre-seed upper FWHM bound IS the ordinary physical cap (was a
   118	# looser 3.0 that let residual proposals grow to fat, physically indefensible
   119	# widths — e.g. a real-data 281 eV feature fitting at 3.0 eV).
   120	PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV
   121	PROPOSED_PEAK_SHAPE = LineShape.PSEUDO_VOIGT
   122	PROPOSAL_GRAMMAR_SEPARATION_FACTOR = 0.5
   123	PROPOSAL_DELTABIC_THRESHOLD = 2.0
   124	PROPOSAL_PERSISTENCE_THRESHOLD = ABSENT_SLOT_PERSISTENCE_THRESHOLD
   125	PROPOSAL_AMPLITUDE_SNR = 5.0
   126	# Unit F2 (2026-07-07): raised 1 → 3 and made ITERATIVE — after an accepted
   127	# proposal, detection re-runs on the AUGMENTED model's residual and another
   128	# proposal may be accepted (same gates each round: SNR, ΔBIC*, persistence,
   129	# boundary cleanliness; same per-candidate wall budget).  Measured
   130	# motivation (PROGRESS.md diagnosis, cause c): with the old single-accept
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
  1840	    edge = max(2, k // 2)     # smoothing edge — 'same' convolution damps ends
  1841	    for i in range(edge, len(ys) - edge):
  1842	        if not (ys[i] >= ys[i - 1] and ys[i] > ys[i + 1]
  1843	                and ys[i] >= ys[i - 2] and ys[i] > ys[i + 2]):
  1844	            continue
  1845	        center = float(x_asc[i])
  1846	        amp = float(ys[i])
  1847	        if in_any_window(center):
  1848	            continue
  1849	        if amp < PRESEED_MIN_FRACTION_OF_MAX * global_max:
  1850	            continue
  1851	        mask = (x_asc >= center - PROPOSAL_WINDOW_WIDTH) & \
  1852	               (x_asc <= center + PROPOSAL_WINDOW_WIDTH)
  1853	        local_sigma = float(np.median(np.sqrt(np.maximum(y_asc[mask], noise_floor)))) \
  1854	            if mask.sum() > 1 else float(np.sqrt(max(noise_floor, 1.0)))
  1855	        if amp < PRESEED_AMPLITUDE_SNR * local_sigma:
  1856	            continue
  1857	        # FWHM estimate: half-height walk on the smoothed net signal
  1858	        half = 0.5 * amp
  1859	        left = i
  1860	        while left > 0 and ys[left - 1] > half:
  1861	            left -= 1
  1862	        right = i
  1863	        while right < len(ys) - 1 and ys[right + 1] > half:
  1864	            right += 1
  1865	        fwhh = float(x_asc[right] - x_asc[left])
  1866	        fwhm_init = float(np.clip(fwhh if fwhh > 0 else PROPOSAL_FWHM_MIN,
  1867	                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
  1868	        found.append(PreseedSpec(
  1869	            role="", center_init=center, fwhm_init=fwhm_init,
  1870	            amplitude_net=amp, fraction_of_max=amp / global_max,
  1871	            local_snr=amp / max(local_sigma, 1e-12),
  1872	        ))
  1873	
  1874	    # strongest first; enforce separation; cap; then stable role naming by BE
  1875	    found.sort(key=lambda s: s.amplitude_net, reverse=True)
  1876	    accepted: list[PreseedSpec] = []
  1877	    for s in found:
  1878	        if len(accepted) >= PRESEED_MAX:
  1879	            break
  1880	        if any(abs(s.center_init - a.center_init) < PRESEED_MIN_SEPARATION_BE
  1881	               for a in accepted):
  1882	            continue
  1883	        accepted.append(s)
  1884	    accepted.sort(key=lambda s: s.center_init)
  1885	    return [PreseedSpec(role=f"preseed_dominant_{i}", center_init=s.center_init,
  1886	                        fwhm_init=s.fwhm_init, amplitude_net=s.amplitude_net,
  1887	                        fraction_of_max=s.fraction_of_max, local_snr=s.local_snr)
  1888	            for i, s in enumerate(accepted)]
  1889	
  1890	
  1891	def _preseed_augmented(
  1892	    base: CandidateModel, specs: list[PreseedSpec]
  1893	) -> CandidateModel:
  1894	    """Every candidate gets the seeded slots — region/phase `unassigned`
  1895	    exactly like proposal slots (assignment is adjudication, not window
  1896	    inheritance; Codex Stage-2 finding #2 applies here identically).  The
  1897	    roles do not start with ``main_`` so the absent-slot machinery can
  1898	    classify a seed that carries no real signal absent, excluding it from
  1899	    the emitted peaks with the honest BIC* adjustment."""
  1900	    seeded = tuple(
  1901	        ComponentSlot(
  1902	            role=s.role,
  1903	            region="unassigned",
  1904	            phase_id="unassigned",
  1905	            be_window=(s.center_init - 0.75, s.center_init + 0.75),
  1906	            line_shape=PROPOSED_PEAK_SHAPE,
  1907	            fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
  1908	        )
  1909	        for s in specs
  1910	    )
  1911	    return CandidateModel(
  1912	        name=f"{base.name}+preseed",
  1913	        background=base.background,
  1914	        slots=base.slots + seeded,
  1915	        shared_fwhm_params=base.shared_fwhm_params,
  1916	    )
  1917	
  1918	
  1919	# ─────────────────────────────────────────────────────────────────────────────
  1920	# Proposal pass (residual-guided peak augmentation)
  1921	# ─────────────────────────────────────────────────────────────────────────────
  1922	
  1923	@dataclass
  1924	class ProposalSpec:
  1925	    role: str
  2045	    for idx, cluster in enumerate(clusters):
  2046	        lo = min(t["be_lo"] for t in cluster)
  2047	        hi = max(t["be_hi"] for t in cluster)
  2048	        mask = (x_asc >= lo) & (x_asc <= hi)
  2049	        if mask.sum() < 3:
  2050	            continue
  2051	        r_abs = np.abs(r_std_asc[mask])
  2052	        k = int(np.argmax(r_abs))
  2053	        span = x_asc[mask]
  2054	        center = float(span[k])
  2055	        r_at = float(r_asc[mask][k])
  2056	        if r_at <= 0:
  2057	            continue
  2058	        half = 0.5 * float(r_abs[k])
  2059	        above = r_abs > half
  2060	        left = k
  2061	        while left > 0 and above[left - 1]:
  2062	            left -= 1
  2063	        right = k
  2064	        while right < len(above) - 1 and above[right + 1]:
  2065	            right += 1
  2066	        fwhh = float(span[right] - span[left])
  2067	        fwhm_init = float(np.clip(fwhh if fwhh > 0 else PROPOSAL_FWHM_MIN,
  2068	                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
  2069	        if _proposal_blocked(center, base_model, fitted_components):
  2070	            continue
  2071	        specs.append(ProposalSpec(
  2072	            role=f"proposed_peak_{idx}",
  2073	            detection_windows=[t["label"] for t in cluster],
  2074	            detection_energy=float(sum(t["energy"] for t in cluster)),
  2075	            detection_ratio=float(max(t["ratio"] for t in cluster)),
  2076	            center_init=center, fwhm_init=fwhm_init,
  2077	            amplitude_init=max(r_at, 1.0),
  2078	            line_shape=PROPOSED_PEAK_SHAPE,
  2079	        ))
  2080	    specs.sort(key=lambda s: s.detection_energy, reverse=True)
  2081	    return specs
  2082	
  2083	
  2084	def _next_proposal_index(model: CandidateModel) -> int:
  2085	    """One past the highest existing ``proposed_peak_<n>`` suffix on ``model``
  2086	    (0 if none).  MUST be max-suffix+1, NOT a slot COUNT: within an F2 round
  2087	    the specs are numbered from a base and attempted in detection-energy
  2088	    order, so a rejected earlier spec followed by an accepted later one
  2089	    leaves e.g. ``proposed_peak_1`` present while ``proposed_peak_0`` never
  2090	    materialized — a count (1) would then re-issue ``proposed_peak_1`` next
  2091	    round, colliding the slot role and its lmfit param prefix (Codex
  2092	    c1s-fix review, both runs BLOCKER)."""
  2093	    mx = -1
  2094	    prefix = "proposed_peak_"
  2095	    for s in model.slots:
  2096	        if s.role.startswith(prefix):
  2097	            try:
  2098	                mx = max(mx, int(s.role[len(prefix):]))
  2099	            except ValueError:
  2100	                continue
  2101	    return mx + 1
  2102	
  2103	
  2104	def _augmented_candidate(base: CandidateModel, spec: ProposalSpec) -> CandidateModel:
  2105	    # Proposals spawn OUTSIDE every grammar window by construction (the
  2106	    # separation gate), so no region/phase can honestly be inherited —
  2107	    # assigning the base model's first slot's tags would leak a phase in
  2108	    # joint fits (Codex Stage-2 finding #2).  Region/phase assignment of a
  2109	    # proposed peak is a human adjudication step, not an inheritance.
  2110	    proposed = ComponentSlot(
  2111	        role=spec.role,
  2112	        region="unassigned",
  2113	        phase_id="unassigned",
  2114	        be_window=(spec.center_init - 0.75, spec.center_init + 0.75),
  2115	        line_shape=spec.line_shape,
  2116	        fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
  2117	    )
  2118	    return CandidateModel(
  2119	        name=f"{base.name}+prop",
  2120	        background=base.background,
  2121	        slots=base.slots + (proposed,),
  2122	        shared_fwhm_params=base.shared_fwhm_params,
  2123	    )
  2124	
  2125	
  2126	def _initial_params_for_augmented(
  2127	    aug_model: CandidateModel,
  2128	    base_fit: FitOutcome,
  2129	    spec: ProposalSpec,
  2130	    x: np.ndarray,

exec
/bin/zsh -lc 'git show --color=never --find-renames ad7e668 -- autofit/grammar.py tests/autofit/test_broad_justification.py' in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba autofit/candidates.py | sed -n '430,485p' && nl -ba tests/autofit/test_broad_justification.py | sed -n '1,330p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-fZ83cMKV' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-2WhZhtBi' (errno=Operation not permitted)
commit ad7e6683f5a64e0fb12c15e42a9423821e02d731
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Mon Jul 20 12:53:49 2026 -0600

    fix(autofit): _retag_slot silently dropped broad_justification during composition
    
    Both Codex reviews of 5070662 (the broad_justification refactor)
    independently caught the same MAJOR: _retag_slot (used by resolve()
    whenever it composes a multi-region joint co-fit, e.g. this lab's real
    U 4f + N 1s co-fit for UCl4-in-BN samples) reconstructed each
    ComponentSlot by manually re-listing every field. broad_justification
    wasn't in that list, so it silently defaulted back to None for every
    slot passing through composition — every previously-exempt slot (U 4f
    mains, U 4f satellites, N 1s main, in any joint model) lost its
    exemption and started getting flagged as unphysical, purely as an
    artifact of going through resolve() with more than one region. Verified
    independently before accepting the finding:
    
        resolve([UCl4(U 4f), BN(N 1s)], ["U 4f", "N 1s"])
        -> U4f__main_u4f72 (1.5, 3.5) broad_justification=None  (should be set)
    
    Fix: dataclasses.replace(s, role=..., linked_to=..., fwhm_linked_to=...)
    instead of manual field listing. ComponentSlot is frozen, so replace()
    is the idiomatic approach — it carries every field NOT explicitly
    overridden forward unchanged, including any field added to ComponentSlot
    after this function was written. This closes not just today's instance
    but the whole class of bug: the manual-reconstruction pattern is exactly
    how broad_justification got lost, and would silently lose the next field
    too.
    
    Test coverage, per the two gaps Codex's own round-1 review named:
    
    - EXEMPTION_FIXTURE (tests/autofit/test_broad_justification.py) extended
      to cover the U 4f satellite-pair variants (U1_mains_satpair,
      U1b_mains_satpair_freesep, U2_mains_satfree) — the original fixture
      only covered U0_mains, exactly where this bug's blast radius was
      invisible to the existing safety net.
    - New COMPOSED_EXEMPTION_FIXTURE exercises the real U 4f + N 1s co-fit
      scenario both Codex reviews used to demonstrate the bug, across every
      composed candidate name and role.
    - New test_retag_slot_preserves_all_fields_except_the_three_rewritten:
      a class-level structural guard, not another point fix. Driven off
      dataclasses.fields(ComponentSlot) rather than a hardcoded field list,
      so it automatically covers any field added to ComponentSlot later —
      confirmed to actually catch the original bug (fails against a
      reverted, manually-reconstructing _retag_slot).
    
    Verified the other 3 slot-construction sites are unaffected, as
    expected: autofit/engine.py's pre-seed (_preseed_augmented) and proposal
    (_augmented_candidate) slots use fwhm_range=(PROPOSAL_FWHM_MIN,
    PROPOSAL_FWHM_MAX), and PROPOSAL_FWHM_MAX == FWHM_MAX_ORDINARY_EV == 2.0
    — declared_hi is never > 2.0, so these were never exempt under the old
    numeric rule either, no behavior change either way. autofit/candidates.py's
    detection slots (role prefix detected_peak_) return early via
    _unphysical_width_flags' own scale-relative branch, before the
    broad_justification check is ever reached.
    
    Full suite: 747 passed, 6 skipped, 1 failed (test_u4f_n1s_cofit — a
    pre-existing timing/hash-seed-sensitive flake; same test exercises the
    REAL U 4f + N 1s composed co-fit this fix targets, failed with the
    byte-identical known signature, and passed cleanly on an immediate
    rerun with zero code changes, confirming flakiness rather than
    regression). RUN_AUTOFIT_GATE=1 gate suite: 10 passed, 2 failed (the
    same test_u4f_n1s_cofit flake plus the already-known
    test_candidate_pool_real_gate.py ds8 timing-budget flake, both
    byte-identical to prior confirmed instances).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

diff --git a/autofit/grammar.py b/autofit/grammar.py
index 1e291f2..c9a85cd 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -27,7 +27,7 @@ from __future__ import annotations
 
 import itertools
 import re
-from dataclasses import dataclass, field
+from dataclasses import dataclass, field, replace
 from enum import Enum
 from typing import Optional
 
@@ -586,7 +586,21 @@ def _retag_slot(
     rename: dict[str, str],
     shared_rename: dict[str, str],
 ) -> ComponentSlot:
-    """Rewrite role / linked_to / fwhm_linked_to under the region prefix."""
+    """Rewrite role / linked_to / fwhm_linked_to under the region prefix.
+
+    Uses dataclasses.replace (ComponentSlot is frozen) rather than
+    reconstructing the slot field-by-field: replace() carries every field
+    NOT explicitly overridden forward unchanged, including any field added
+    to ComponentSlot after this function was written. The manual
+    reconstruction this replaced was exactly how broad_justification got
+    silently dropped for every multi-region composed candidate (Codex-caught
+    regression, 2026-07-20): a new field simply wasn't in the list, so it
+    defaulted back to None for every slot passing through here — see
+    tests/autofit/test_broad_justification.py's
+    test_retag_slot_preserves_all_fields_except_the_three_rewritten, which
+    guards against this exact class of bug recurring for whatever field
+    comes next.
+    """
     fwhm_link = s.fwhm_linked_to
     if fwhm_link is not None:
         # fwhm_linked_to may reference either a shared param or another
@@ -599,22 +613,11 @@ def _retag_slot(
                 if fwhm_link.startswith(old_prefix):
                     fwhm_link = _slot_param_prefix(new) + fwhm_link[len(old_prefix):]
                     break
-    return ComponentSlot(
+    return replace(
+        s,
         role=rename[s.role],
-        region=s.region,
-        phase_id=s.phase_id,
-        be_window=s.be_window,
-        line_shape=s.line_shape,
-        fwhm_range=s.fwhm_range,
         linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None,
-        linked_offset_range=s.linked_offset_range,
-        area_ratio=s.area_ratio,
-        area_ratio_range=s.area_ratio_range,
-        fixed_params=s.fixed_params,
-        param_ranges=s.param_ranges,
         fwhm_linked_to=fwhm_link,
-        share_parent_params=s.share_parent_params,
-        fwhm_excess_range=s.fwhm_excess_range,
     )
 
 
diff --git a/tests/autofit/test_broad_justification.py b/tests/autofit/test_broad_justification.py
index b7dcb05..f676dd5 100644
--- a/tests/autofit/test_broad_justification.py
+++ b/tests/autofit/test_broad_justification.py
@@ -78,11 +78,122 @@ EXEMPTION_FIXTURE = [
     # N 1s: main_n1s exempt at N1S_FWHM_RANGE (0.7-2.5) in both shape variants.
     (_INSULATOR_N1S, "N 1s", "N0_pv", "main_n1s", True),
     (_INSULATOR_N1S, "N 1s", "N0_asymGL", "main_n1s", True),
-    # U 4f: mains (1.5-3.5) and satellites (1.5-4.5) both exempt.
+    # U 4f: mains (1.5-3.5) and satellites (1.5-4.5) both exempt, incl.
+    # the pair-linked / free-separation / independent satellite variants
+    # (Codex-caught gap, round 1 of this refactor's own review: the
+    # original fixture only covered U0_mains, not U1/U1b/U2's satellites).
     (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f72", True),
     (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f52", True),
+    (_INSULATOR_U4F, "U 4f", "U1_mains_satpair", "satellite_u4f72", True),
+    (_INSULATOR_U4F, "U 4f", "U1_mains_satpair", "satellite_u4f52", True),
+    (_INSULATOR_U4F, "U 4f", "U1b_mains_satpair_freesep", "satellite_u4f52", True),
+    (_INSULATOR_U4F, "U 4f", "U2_mains_satfree", "satellite_u4f72", True),
+    (_INSULATOR_U4F, "U 4f", "U2_mains_satfree", "satellite_u4f52", True),
 ]
 
+# ── Composed (multi-region joint co-fit) coverage ──────────────────────────
+# The actual bug this section guards against (Codex-caught, round 1 of this
+# refactor's own review): resolve() with >1 region composes candidates via
+# autofit.grammar._retag_slot, which used to reconstruct each ComponentSlot
+# by manually re-listing every field -- broad_justification wasn't in that
+# list, so EVERY composed candidate silently lost EVERY exemption. Fixed by
+# switching _retag_slot to dataclasses.replace(). This fixture exercises the
+# exact U 4f + N 1s co-fit scenario both Codex reviews used to demonstrate
+# the bug (this lab's real UCl4-in-BN samples).
+
+_U4F_PHASE = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
+                   regions=("U 4f",))
+_N1S_PHASE = Phase(id="BN", material_class=MaterialClass.INSULATOR,
+                   regions=("N 1s",))
+
+# (candidate_name, role, currently_exempt) -- resolved via [_U4F_PHASE, _N1S_PHASE]
+COMPOSED_EXEMPTION_FIXTURE = [
+    ("U0_mains+N0_pv", "U4f__main_u4f72", True),
+    ("U0_mains+N0_pv", "U4f__main_u4f52", True),
+    ("U0_mains+N0_pv", "N1s__main_n1s", True),
+    ("U1_mains_satpair+N0_pv", "U4f__satellite_u4f72", True),
+    ("U1_mains_satpair+N0_pv", "U4f__satellite_u4f52", True),
+    ("U1b_mains_satpair_freesep+N0_asymGL", "U4f__satellite_u4f52", True),
+    ("U2_mains_satfree+N0_asymGL", "U4f__satellite_u4f72", True),
+]
+
+
+def _composed_slot(candidate_name, role):
+    g = resolve([_U4F_PHASE, _N1S_PHASE], ["U 4f", "N 1s"])
+    cand = next(c for c in g.candidates if c.name == candidate_name)
+    slot = cand.slot_by_role(role)
+    assert slot is not None, f"{candidate_name}/{role} not found"
+    return slot
+
+
+@pytest.mark.parametrize("candidate_name,role,exempt", COMPOSED_EXEMPTION_FIXTURE)
+def test_composed_candidate_preserves_broad_justification(
+        candidate_name, role, exempt):
+    """The exact regression: a slot that is grammar-sanctioned-broad in its
+    OWN region module must stay that way after _retag_slot composes it into
+    a multi-region joint-fit candidate."""
+    slot = _composed_slot(candidate_name, role)
+    if exempt:
+        assert slot.broad_justification is not None, (
+            f"{candidate_name}/{role} lost its broad_justification during "
+            "multi-region composition (_retag_slot regression)"
+        )
+    else:
+        assert slot.broad_justification is None
+
+
+def test_retag_slot_preserves_all_fields_except_the_three_rewritten():
+    """Structural guard against this bug class recurring: _retag_slot must
+    carry every ComponentSlot field forward unchanged except role/
+    linked_to/fwhm_linked_to (deliberately rewritten for region-prefixing).
+    Driven off dataclasses.fields(ComponentSlot) rather than a hardcoded
+    list, so this test automatically covers any field added to
+    ComponentSlot later -- a class-level guard, not another point fix."""
+    import dataclasses
+
+    from autofit.grammar import ComponentSlot, _retag_slot
+
+    rewritten = {"role", "linked_to", "fwhm_linked_to"}
+
+    sentinel_by_field = {
+        "role": "orig_role",
+        "region": "orig_region",
+        "phase_id": "orig_phase",
+        "be_window": (100.0, 200.0),
+        "line_shape": LineShape.PSEUDO_VOIGT,
+        "fwhm_range": (0.5, 9.99),
+        "linked_to": "orig_role",
+        "linked_offset_range": (1.0, 2.0),
+        "area_ratio": 0.123456,
+        "area_ratio_range": (0.1, 0.9),
+        "fixed_params": (("beta", 0.05),),
+        "param_ranges": (("alpha", (0.0, 0.3)),),
+        "fwhm_linked_to": None,
+        "fwhm_excess_range": (0.0, 0.8),
+        "share_parent_params": ("alpha", "beta"),
+        "broad_justification": "sentinel justification text",
+    }
+    field_names = {f.name for f in dataclasses.fields(ComponentSlot)}
+    missing = field_names - set(sentinel_by_field)
+    assert not missing, (
+        f"ComponentSlot gained new field(s) {missing} this test doesn't "
+        "sentinel-fill -- add a case above so the guard covers it"
+    )
+
+    original = ComponentSlot(**sentinel_by_field)
+    rename = {"orig_role": "PhaseX__orig_role"}
+    retagged = _retag_slot(original, rename, shared_rename={})
+
+    for name in field_names:
+        if name in rewritten:
+            continue
+        assert getattr(retagged, name) == getattr(original, name), (
+            f"_retag_slot lost field {name!r}: "
+            f"{getattr(original, name)!r} -> {getattr(retagged, name)!r}"
+        )
+    assert retagged.role == "PhaseX__orig_role"
+    assert retagged.linked_to == "PhaseX__orig_role"
+
 
 @pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
                          EXEMPTION_FIXTURE)

 succeeded in 0ms:
   430	    if not feats:
   431	        return None, []
   432	    ranked = sorted(feats, key=lambda f: (f.amplitude_net or 0.0),
   433	                    reverse=True)
   434	    feats = ranked[:DETECTION_MODEL_MAX_SLOTS]
   435	    dropped = [{"center_be": round(float(f.center_be), 3),
   436	                "amplitude_net": (round(float(f.amplitude_net), 1)
   437	                                  if f.amplitude_net is not None else None),
   438	                "reason": ("detection_model_overflow (cap "
   439	                           f"{DETECTION_MODEL_MAX_SLOTS}, by amplitude)")}
   440	               for f in ranked[DETECTION_MODEL_MAX_SLOTS:]]
   441	    feats.sort(key=lambda f: f.center_be)
   442	    centers = [f.center_be for f in feats]
   443	    slots = []
   444	    for i, f in enumerate(feats):
   445	        width = float(f.fwhm_est) if f.fwhm_est else max(4.0 * step_ev, 0.5)
   446	        # SPACING-AWARE center bounds: a slot window must never enclose a
   447	        # neighboring slot's center — a merged close pair reads its
   448	        # fwhm_est at the envelope scale (measured: dominant est 2.4 eV vs
   449	        # true 0.7 with a neighbor 0.9 eV away → window swallowed the
   450	        # neighbor → label-switching degeneracy, screens burned all nfev).
   451	        # 0.45×gap keeps adjacent windows disjoint whatever the widths.
   452	        gaps = []
   453	        if i > 0:
   454	            gaps.append(f.center_be - centers[i - 1])
   455	        if i < len(centers) - 1:
   456	            gaps.append(centers[i + 1] - f.center_be)
   457	        half_win = max(DETECTION_SLOT_WINDOW_FRACTION * width, 3.0 * step_ev)
   458	        if gaps:
   459	            half_win = min(half_win, 0.45 * min(gaps))
   460	        half_win = max(half_win, 2.0 * step_ev)     # never below grid sanity
   461	        lo_w = max(DETECTION_SLOT_FWHM_LO_FRACTION * width, 2.0 * step_ev)
   462	        hi_w = max(DETECTION_SLOT_FWHM_HI_FRACTION * width, lo_w + 4.0 * step_ev)
   463	        slots.append(ComponentSlot(
   464	            role=f"detected_peak_{i}",
   465	            region="unassigned",
   466	            phase_id="unassigned",
   467	            be_window=(f.center_be - half_win, f.center_be + half_win),
   468	            line_shape=LineShape.PSEUDO_VOIGT,
   469	            fwhm_range=(lo_w, hi_w),
   470	        ))
   471	    return CandidateModel(name=name, background=background,
   472	                          slots=tuple(slots)), dropped
   473	
   474	
   475	def merge_residual_attempts(
   476	    pool_payload: dict,
   477	    attempts: list[dict],
   478	    coincidence_ev: float,
   479	    proposal_pass_ran: bool = True,
   480	) -> None:
   481	    """
   482	    Merge the F2 residual-proposal attempts into a pool PAYLOAD (post-fit —
   483	    residual proposals only exist per fitted candidate).  Each attempt is
   484	    ``{"center_be": float, "accepted": bool}``; attempts within
   485	    ``coincidence_ev`` of an existing detection entry annotate that entry
     1	"""Unit A (2026-07-20): decouples two meanings that ``fwhm_range``'s upper
     2	bound used to carry at once:
     3	
     4	  1. the optimizer's own search bound ("the width parameter may search up
     5	     to here");
     6	  2. a semantic claim consumed by quality reporting ("this region module
     7	     VOUCHES that a component this wide is legitimate physics, not an
     8	     optimizer papering over a missed feature").
     9	
    10	``autofit/engine.py``'s ``_unphysical_width_flags`` used to infer (2) from
    11	(1) via a bare numeric test (``declared_hi > FWHM_MAX_ORDINARY_EV``). The
    12	MIXED material-class unit (77bf3a8) relaxed (1) for C 1s contamination
    13	slots to make room for differential-charging broadening, and thereby
    14	silently asserted (2) as a side effect -- exactly backwards, since MIXED's
    15	entire premise is that we do NOT know how broad differential charging
    16	makes the peak, the opposite of vouching for it. Both Codex reviews of
    17	77bf3a8 independently caught this (see docs/autofit/codex/
    18	mixed_material_class_verdict_run{A,B}.md).
    19	
    20	The fix: ``ComponentSlot.broad_justification`` makes meaning (2) an
    21	explicit, independent field. ``_unphysical_width_flags`` keys its
    22	exemption off ``broad_justification is not None``, never off the bound's
    23	magnitude. This file is the safety net for that refactor: it encodes, as
    24	an explicit and auditable fixture, EXACTLY which slots are exempt today
    25	(under the old numeric rule) so the same set stays exempt under the new
    26	field-based rule -- pure refactor, behavior-neutral, proven rather than
    27	asserted.
    28	"""
    29	from __future__ import annotations
    30	
    31	import pytest
    32	
    33	from autofit.engine import FittedComponent, _unphysical_width_flags
    34	from autofit.grammar import LineShape, MaterialClass, Phase, resolve
    35	
    36	# ── Ground truth: which slots are grammar-sanctioned-broad TODAY ───────────
    37	# (declared_hi > FWHM_MAX_ORDINARY_EV == 2.0 eV, the pre-refactor rule),
    38	# derived by reading every region module's build_candidates(). Each entry
    39	# names the region, the exact CandidateModel to fetch it from, and the
    40	# slot role. This is the fixture the refactor must reproduce exactly.
    41	
    42	_CONDUCTOR_C1S = Phase(id="s", material_class=MaterialClass.CONDUCTOR,
    43	                       regions=("C 1s",))
    44	_INSULATOR_B1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
    45	                       regions=("B 1s",))
    46	_INSULATOR_CL2P = Phase(id="s", material_class=MaterialClass.INSULATOR,
    47	                        regions=("Cl 2p",))
    48	_INSULATOR_N1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
    49	                       regions=("N 1s",))
    50	_INSULATOR_U4F = Phase(id="s", material_class=MaterialClass.INSULATOR,
    51	                       regions=("U 4f",))
    52	
    53	
    54	def _slot(phase, region, candidate_name, role):
    55	    g = resolve([phase], region)
    56	    cand = next(c for c in g.candidates if c.name == candidate_name)
    57	    slot = cand.slot_by_role(role)
    58	    assert slot is not None, f"{candidate_name}/{role} not found"
    59	    return slot
    60	
    61	
    62	# (phase, region, candidate_name, role, currently_exempt)
    63	EXEMPTION_FIXTURE = [
    64	    # C 1s: only the pi->pi* satellite is exempt (declared 1.0-5.5).
    65	    (_CONDUCTOR_C1S, "C 1s", "A0_graphite_asym_satellite", "satellite_pi", True),
    66	    (_CONDUCTOR_C1S, "C 1s", "A0_graphite_asym_satellite", "main_graphitic", False),
    67	    (_CONDUCTOR_C1S, "C 1s", "B2_linked", "main_aliphatic", False),
    68	    (_CONDUCTOR_C1S, "C 1s", "A1_linked", "contamination_CO", False),
    69	    # B 1s: all three mains share B1S_FWHM_RANGE (1.2-2.5) -- all exempt.
    70	    (_INSULATOR_B1S, "B 1s", "B1_low", "main_b_low", True),
    71	    (_INSULATOR_B1S, "B 1s", "B2_low_mid", "main_b_mid", True),
    72	    (_INSULATOR_B1S, "B 1s", "B2b_low_oxide", "main_b_oxide", True),
    73	    # Cl 2p: both p32 (shared-width family) and p12 exempt at CL2P_FWHM_RANGE
    74	    # (1.2-2.2) / CL2P_12_FWHM_RANGE (free-width family, up to 3.0).
    75	    (_INSULATOR_CL2P, "Cl 2p", "Cl0_doublet", "main_cl2p32", True),
    76	    (_INSULATOR_CL2P, "Cl 2p", "Cl0_doublet", "main_cl2p12", True),
    77	    (_INSULATOR_CL2P, "Cl 2p", "Cl0w_doublet_freewidth", "main_cl2p12", True),
    78	    # N 1s: main_n1s exempt at N1S_FWHM_RANGE (0.7-2.5) in both shape variants.
    79	    (_INSULATOR_N1S, "N 1s", "N0_pv", "main_n1s", True),
    80	    (_INSULATOR_N1S, "N 1s", "N0_asymGL", "main_n1s", True),
    81	    # U 4f: mains (1.5-3.5) and satellites (1.5-4.5) both exempt, incl.
    82	    # the pair-linked / free-separation / independent satellite variants
    83	    # (Codex-caught gap, round 1 of this refactor's own review: the
    84	    # original fixture only covered U0_mains, not U1/U1b/U2's satellites).
    85	    (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f72", True),
    86	    (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f52", True),
    87	    (_INSULATOR_U4F, "U 4f", "U1_mains_satpair", "satellite_u4f72", True),
    88	    (_INSULATOR_U4F, "U 4f", "U1_mains_satpair", "satellite_u4f52", True),
    89	    (_INSULATOR_U4F, "U 4f", "U1b_mains_satpair_freesep", "satellite_u4f52", True),
    90	    (_INSULATOR_U4F, "U 4f", "U2_mains_satfree", "satellite_u4f72", True),
    91	    (_INSULATOR_U4F, "U 4f", "U2_mains_satfree", "satellite_u4f52", True),
    92	]
    93	
    94	# ── Composed (multi-region joint co-fit) coverage ──────────────────────────
    95	# The actual bug this section guards against (Codex-caught, round 1 of this
    96	# refactor's own review): resolve() with >1 region composes candidates via
    97	# autofit.grammar._retag_slot, which used to reconstruct each ComponentSlot
    98	# by manually re-listing every field -- broad_justification wasn't in that
    99	# list, so EVERY composed candidate silently lost EVERY exemption. Fixed by
   100	# switching _retag_slot to dataclasses.replace(). This fixture exercises the
   101	# exact U 4f + N 1s co-fit scenario both Codex reviews used to demonstrate
   102	# the bug (this lab's real UCl4-in-BN samples).
   103	
   104	_U4F_PHASE = Phase(id="UCl4", material_class=MaterialClass.INSULATOR,
   105	                   regions=("U 4f",))
   106	_N1S_PHASE = Phase(id="BN", material_class=MaterialClass.INSULATOR,
   107	                   regions=("N 1s",))
   108	
   109	# (candidate_name, role, currently_exempt) -- resolved via [_U4F_PHASE, _N1S_PHASE]
   110	COMPOSED_EXEMPTION_FIXTURE = [
   111	    ("U0_mains+N0_pv", "U4f__main_u4f72", True),
   112	    ("U0_mains+N0_pv", "U4f__main_u4f52", True),
   113	    ("U0_mains+N0_pv", "N1s__main_n1s", True),
   114	    ("U1_mains_satpair+N0_pv", "U4f__satellite_u4f72", True),
   115	    ("U1_mains_satpair+N0_pv", "U4f__satellite_u4f52", True),
   116	    ("U1b_mains_satpair_freesep+N0_asymGL", "U4f__satellite_u4f52", True),
   117	    ("U2_mains_satfree+N0_asymGL", "U4f__satellite_u4f72", True),
   118	]
   119	
   120	
   121	def _composed_slot(candidate_name, role):
   122	    g = resolve([_U4F_PHASE, _N1S_PHASE], ["U 4f", "N 1s"])
   123	    cand = next(c for c in g.candidates if c.name == candidate_name)
   124	    slot = cand.slot_by_role(role)
   125	    assert slot is not None, f"{candidate_name}/{role} not found"
   126	    return slot
   127	
   128	
   129	@pytest.mark.parametrize("candidate_name,role,exempt", COMPOSED_EXEMPTION_FIXTURE)
   130	def test_composed_candidate_preserves_broad_justification(
   131	        candidate_name, role, exempt):
   132	    """The exact regression: a slot that is grammar-sanctioned-broad in its
   133	    OWN region module must stay that way after _retag_slot composes it into
   134	    a multi-region joint-fit candidate."""
   135	    slot = _composed_slot(candidate_name, role)
   136	    if exempt:
   137	        assert slot.broad_justification is not None, (
   138	            f"{candidate_name}/{role} lost its broad_justification during "
   139	            "multi-region composition (_retag_slot regression)"
   140	        )
   141	    else:
   142	        assert slot.broad_justification is None
   143	
   144	
   145	def test_retag_slot_preserves_all_fields_except_the_three_rewritten():
   146	    """Structural guard against this bug class recurring: _retag_slot must
   147	    carry every ComponentSlot field forward unchanged except role/
   148	    linked_to/fwhm_linked_to (deliberately rewritten for region-prefixing).
   149	    Driven off dataclasses.fields(ComponentSlot) rather than a hardcoded
   150	    list, so this test automatically covers any field added to
   151	    ComponentSlot later -- a class-level guard, not another point fix."""
   152	    import dataclasses
   153	
   154	    from autofit.grammar import ComponentSlot, _retag_slot
   155	
   156	    rewritten = {"role", "linked_to", "fwhm_linked_to"}
   157	
   158	    sentinel_by_field = {
   159	        "role": "orig_role",
   160	        "region": "orig_region",
   161	        "phase_id": "orig_phase",
   162	        "be_window": (100.0, 200.0),
   163	        "line_shape": LineShape.PSEUDO_VOIGT,
   164	        "fwhm_range": (0.5, 9.99),
   165	        "linked_to": "orig_role",
   166	        "linked_offset_range": (1.0, 2.0),
   167	        "area_ratio": 0.123456,
   168	        "area_ratio_range": (0.1, 0.9),
   169	        "fixed_params": (("beta", 0.05),),
   170	        "param_ranges": (("alpha", (0.0, 0.3)),),
   171	        "fwhm_linked_to": None,
   172	        "fwhm_excess_range": (0.0, 0.8),
   173	        "share_parent_params": ("alpha", "beta"),
   174	        "broad_justification": "sentinel justification text",
   175	    }
   176	    field_names = {f.name for f in dataclasses.fields(ComponentSlot)}
   177	    missing = field_names - set(sentinel_by_field)
   178	    assert not missing, (
   179	        f"ComponentSlot gained new field(s) {missing} this test doesn't "
   180	        "sentinel-fill -- add a case above so the guard covers it"
   181	    )
   182	
   183	    original = ComponentSlot(**sentinel_by_field)
   184	    rename = {"orig_role": "PhaseX__orig_role"}
   185	    retagged = _retag_slot(original, rename, shared_rename={})
   186	
   187	    for name in field_names:
   188	        if name in rewritten:
   189	            continue
   190	        assert getattr(retagged, name) == getattr(original, name), (
   191	            f"_retag_slot lost field {name!r}: "
   192	            f"{getattr(original, name)!r} -> {getattr(retagged, name)!r}"
   193	        )
   194	    assert retagged.role == "PhaseX__orig_role"
   195	    assert retagged.linked_to == "PhaseX__orig_role"
   196	
   197	
   198	@pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
   199	                         EXEMPTION_FIXTURE)
   200	def test_exemption_fixture_matches_broad_justification(
   201	        phase, region, candidate_name, role, exempt):
   202	    """Each currently-exempt slot must carry a real broad_justification;
   203	    each currently-non-exempt slot must not. This IS the byte-identical
   204	    proof requested: the exemption SET, read directly off the grammar,
   205	    matches the pre-refactor numeric rule exactly."""
   206	    slot = _slot(phase, region, candidate_name, role)
   207	    if exempt:
   208	        assert slot.broad_justification is not None, (
   209	            f"{region}/{candidate_name}/{role} was grammar-sanctioned-broad "
   210	            f"under the old numeric rule (fwhm_range={slot.fwhm_range}) but "
   211	            "lost its exemption in the refactor"
   212	        )
   213	        assert slot.fwhm_range[1] > 2.0, (
   214	            "fixture sanity: this entry's OWN historical exemption basis "
   215	            "was declared_hi > 2.0 -- if this fails, the fixture itself is "
   216	            "wrong, not the code"
   217	        )
   218	    else:
   219	        assert slot.broad_justification is None, (
   220	            f"{region}/{candidate_name}/{role} was NOT grammar-sanctioned-"
   221	            f"broad under the old numeric rule (fwhm_range={slot.fwhm_range}) "
   222	            "but gained an unjustified exemption in the refactor"
   223	        )
   224	
   225	
   226	def _fitted(role, fwhm, line_shape=LineShape.PSEUDO_VOIGT, **shape_params):
   227	    return FittedComponent(slot_role=role, position=0.0, fwhm=fwhm,
   228	                           amplitude=1.0, shape_params=shape_params,
   229	                           line_shape=line_shape)
   230	
   231	
   232	class _FakeModel:
   233	    """Minimal stand-in for CandidateModel -- _unphysical_width_flags only
   234	    reads .slots."""
   235	    def __init__(self, slots):
   236	        self.slots = slots
   237	
   238	
   239	@pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
   240	                         EXEMPTION_FIXTURE)
   241	def test_flag_behavior_matches_pre_refactor_rule_at_the_ceiling(
   242	        phase, region, candidate_name, role, exempt):
   243	    """The actual OUTPUT of _unphysical_width_flags for a component fitted
   244	    right at its slot's declared ceiling must match what the pre-refactor
   245	    numeric rule would have produced: no flag for an exempt slot even
   246	    though it pegs a wide ceiling; a flag for a non-exempt slot pegging
   247	    the ordinary 2.0 eV cap."""
   248	    slot = _slot(phase, region, candidate_name, role)
   249	    g = resolve([phase], region)
   250	    cand = next(c for c in g.candidates if c.name == candidate_name)
   251	    fwhm_at_ceiling = slot.fwhm_range[1] if exempt else 2.0
   252	    comp = _fitted(role, fwhm_at_ceiling, line_shape=slot.line_shape)
   253	    flags = _unphysical_width_flags([comp], cand)
   254	    if exempt:
   255	        assert not flags, (
   256	            f"{region}/{candidate_name}/{role}: exempt slot got flagged "
   257	            f"at its own ceiling -- {flags}"
   258	        )
   259	    else:
   260	        assert flags, (
   261	            f"{region}/{candidate_name}/{role}: non-exempt slot pegging "
   262	            "the ordinary 2.0 eV cap should be flagged"
   263	        )
   264	
   265	
   266	# ── The actual bug fix, tested generically at the engine level ────────────
   267	
   268	def test_wide_declared_range_without_justification_is_no_longer_exempt():
   269	    """THE FIX, encoded directly: a slot with a wide fwhm_range (would have
   270	    been auto-exempt under the old numeric rule) but broad_justification
   271	    left None must now be flagged when fitted well above the ordinary
   272	    2.0 eV cap -- this is the MIXED contamination scenario, tested here
   273	    independent of MIXED or C 1s at all."""
   274	    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
   275	
   276	    wide_no_justification = ComponentSlot(
   277	        role="wide_slot", region="Test", phase_id="s",
   278	        be_window=(280.0, 295.0), line_shape=LineShape.PSEUDO_VOIGT,
   279	        fwhm_range=(0.8, 15.0), broad_justification=None,
   280	    )
   281	    model = CandidateModel(name="synthetic", background=BackgroundType.SHIRLEY,
   282	                           slots=(wide_no_justification,))
   283	    comp = _fitted("wide_slot", 8.0)   # well above 2.0, well below 15.0
   284	    flags = _unphysical_width_flags([comp], model)
   285	    assert flags, (
   286	        "a slot with a wide bound but NO broad_justification must still "
   287	        "be flagged when it fits wide -- the bound alone must never grant "
   288	        "exemption"
   289	    )
   290	
   291	
   292	def test_narrow_declared_range_with_justification_is_exempt():
   293	    """Mirror case: an explicit broad_justification grants exemption even
   294	    for a slot whose declared ceiling never exceeded the ordinary cap --
   295	    proving exemption is governed by the field, not a numeric side effect
   296	    of the bound's magnitude."""
   297	    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
   298	
   299	    narrow_but_justified = ComponentSlot(
   300	        role="narrow_slot", region="Test", phase_id="s",
   301	        be_window=(280.0, 295.0), line_shape=LineShape.PSEUDO_VOIGT,
   302	        fwhm_range=(0.5, 2.0), broad_justification="synthetic test justification",
   303	    )
   304	    model = CandidateModel(name="synthetic", background=BackgroundType.SHIRLEY,
   305	                           slots=(narrow_but_justified,))
   306	    comp = _fitted("narrow_slot", 2.0)   # pegs its own (narrow) ceiling
   307	    flags = _unphysical_width_flags([comp], model)
   308	    assert not flags, (
   309	        "an explicit broad_justification must exempt a slot even when its "
   310	        "declared ceiling never exceeded the ordinary cap"
   311	    )
   312	
   313	
   314	def test_component_slot_broad_justification_defaults_to_none():
   315	    from autofit.grammar import ComponentSlot
   316	
   317	    s = ComponentSlot(role="r", region="Test", phase_id="s",
   318	                      be_window=(0.0, 1.0), line_shape=LineShape.PSEUDO_VOIGT,
   319	                      fwhm_range=(0.5, 1.0))
   320	    assert s.broad_justification is None

codex
I’ve confirmed the new `_retag_slot` uses `dataclasses.replace`, which should preserve the field mechanically. Next I’m enumerating every production construction/copy site and probing composed candidates beyond the new fixtures.
exec
/bin/zsh -lc "nl -ba autofit/regions/b1s.py | sed -n '1,130p'; nl -ba autofit/regions/n1s.py | sed -n '1,120p'; nl -ba autofit/regions/u4f.py | sed -n '180,285p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	B 1s region module — the weak exemplar (spec §3.3).
     3	
     4	IMPORTANT — component-assignment conflict (PROGRESS.md discrepancy #8): the
     5	two expert sources SWAP the chemical labels of the two sub-oxide components
     6	(spec §3.3 quotes B-C 189.41 / B-B 187.39 from the 4-GTA analysis; the
     7	good-quality B4C-UCl4 fits label B-C 187.10–187.24 / B-B 188.12–188.77).
     8	This module therefore uses POSITION-NEUTRAL role names (``main_b_low``,
     9	``main_b_mid``, ``main_b_oxide``) and defers chemical assignment to the
    10	analyst.  All windows are UNVERIFIED-calibration, anchored on the
    11	GOOD-QUALITY labeled exemplar (B4C-UCl4, χ²ᵣ 1.4–2.5, graphite-referenced
    12	frame); the 4-GTA B 1s fits (χ²ᵣ 17–10⁵) are excluded as suspect per the
    13	run brief.
    14	
    15	Insulator/semiconductor boron phases → symmetric lineshapes only (Layer A);
    16	the labeled fits use GL/Gaussian.
    17	"""
    18	
    19	from __future__ import annotations
    20	
    21	from typing import Optional
    22	
    23	from ..grammar import (
    24	    BackgroundType,
    25	    CandidateModel,
    26	    ComponentSlot,
    27	    LineShape,
    28	    Phase,
    29	)
    30	from . import register_region
    31	
    32	REGION = "B 1s"
    33	
    34	# Windows (corrected frame of the labeled exemplar) — UNVERIFIED-calibration:
    35	# low  : labeled 187.10–187.24
    36	# mid  : labeled 188.12–188.77
    37	# oxide: labeled pinned 193.00 (analyst fixed); window allows freedom
    38	# low/mid OVERLAP deliberately (187.8–188.0): a knife-edge shared boundary
    39	# puts a component at the edge in both windows with tie-breaking left to
    40	# window ordering (Codex cookbook finding #7).  With overlap, the engine's
    41	# nearest-window-center rule owns the ambiguity band explicitly.  Role-swap
    42	# detection for symmetric overlapping components remains future work
    43	# (logged in PROGRESS.md).
    44	B1S_LOW_WINDOW = (186.4, 188.0)
    45	B1S_MID_WINDOW = (187.8, 189.4)
    46	B1S_OXIDE_WINDOW = (192.2, 193.8)
    47	
    48	# UNVERIFIED-empirical (labeled set 1.49–2.27 eV).
    49	B1S_FWHM_RANGE = (1.2, 2.5)
    50	
    51	# Expert practice for this data set (ui.bgType 'smart_exp') — UNVERIFIED
    52	# methodological choice.
    53	B1S_BACKGROUND = BackgroundType.SMART_EXP
    54	
    55	
    56	class B1sModule:
    57	    region = REGION
    58	
    59	    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
    60	        return {"low": B1S_LOW_WINDOW, "mid": B1S_MID_WINDOW,
    61	                "oxide": B1S_OXIDE_WINDOW}
    62	
    63	    def provenance(self) -> list[dict]:
    64	        return [
    65	            {"constant": "low_window_ev", "value": list(B1S_LOW_WINDOW),
    66	             "status": "UNVERIFIED",
    67	             "source": "labeled-set calibration (B4C-UCl4 exemplar); chemical "
    68	                       "assignment DISPUTED between expert sources "
    69	                       "(PROGRESS.md discrepancy #8)"},
    70	            {"constant": "mid_window_ev", "value": list(B1S_MID_WINDOW),
    71	             "status": "UNVERIFIED", "source": "same as low_window_ev"},
    72	            {"constant": "oxide_window_ev", "value": list(B1S_OXIDE_WINDOW),
    73	             "status": "UNVERIFIED",
    74	             "source": "labeled-set calibration (analyst-pinned 193.00)"},
    75	            {"constant": "fwhm_range_ev", "value": list(B1S_FWHM_RANGE),
    76	             "status": "UNVERIFIED", "source": "labeled-set calibration"},
    77	            {"constant": "background", "value": "smart_exp",
    78	             "status": "UNVERIFIED", "source": "expert practice for this data set"},
    79	        ]
    80	
    81	    def build_candidates(
    82	        self, phase: Phase, oxidation_state: Optional[str] = None
    83	    ) -> list[CandidateModel]:
    84	        """Component-count ladder over the three observed positions."""
    85	        if oxidation_state is not None:
    86	            raise KeyError(
    87	                f"B 1s defines no oxidation-state override {oxidation_state!r}"
    88	            )
    89	        pid = phase.id
    90	
    91	        def pv(role, window) -> ComponentSlot:
    92	            return ComponentSlot(
    93	                role=role, region=REGION, phase_id=pid,
    94	                be_window=window, line_shape=LineShape.PSEUDO_VOIGT,
    95	                fwhm_range=B1S_FWHM_RANGE,
    96	                broad_justification=(
    97	                    "UNVERIFIED-empirical: labeled-set calibration only "
    98	                    "(B4C-UCl4 exemplar, labeled fits 1.49-2.27 eV) -- no "
    99	                    "region-specific physical broadening mechanism is "
   100	                    "cited; the range simply brackets the labeled data"
   101	                ),
   102	            )
   103	
   104	        low = pv("main_b_low", B1S_LOW_WINDOW)
   105	        mid = pv("main_b_mid", B1S_MID_WINDOW)
   106	        oxide = pv("main_b_oxide", B1S_OXIDE_WINDOW)
   107	
   108	        def cand(name, slots):
   109	            return CandidateModel(name=name, background=B1S_BACKGROUND,
   110	                                  slots=tuple(slots))
   111	
   112	        return [
   113	            cand("B1_low", [low]),
   114	            cand("B2_low_mid", [low, mid]),
   115	            cand("B2b_low_oxide", [low, oxide]),
   116	            cand("B3_low_mid_oxide", [low, mid, oxide]),
   117	        ]
   118	
   119	
   120	register_region(B1sModule())
     1	"""
     2	N 1s region module — Stage-3 MINIMAL version.
     3	
     4	Exists at this stage primarily as the co-fit partner for the U 4f window
     5	(in U-in-BN samples the BN N 1s line at ~398.3 eV sits inside the U 4f scan
     6	and overshadows the U 4f5/2 shake-up satellite — spec §2/§3.2: the two
     7	grammars are composed and fit jointly).  The full N 1s cookbook module
     8	(charge-reference exemplar, spec §3.5) is a later unit.
     9	
    10	Constants:
    11	- h-BN N 1s ~398.0–398.3 eV: **UNVERIFIED** per spec §9 ("pull a primary
    12	  table") — the window below brackets the spec range and the labeled expert
    13	  fit (398.30 after N-referenced charge correction).  Do not cite until a
    14	  primary source is pulled.
    15	- Widths/shape: UNVERIFIED-empirical from the single labeled exemplar
    16	  (asym-GL, fwhm 1.05 eV, asymmetry 0.064).
    17	"""
    18	
    19	from __future__ import annotations
    20	
    21	from typing import Optional
    22	
    23	from ..grammar import (
    24	    BackgroundType,
    25	    CandidateModel,
    26	    ComponentSlot,
    27	    LineShape,
    28	    Phase,
    29	)
    30	from . import register_region
    31	
    32	REGION = "N 1s"
    33	
    34	N1S_WINDOW = (396.5, 400.0)       # UNVERIFIED (see module docstring)
    35	N1S_FWHM_RANGE = (0.7, 2.5)       # UNVERIFIED-empirical (exemplar 1.05 eV)
    36	N1S_ASYM_RANGE = (0.0, 0.3)       # UNVERIFIED-empirical (exemplar 0.064)
    37	
    38	# Matches the U 4f family so joint co-fit candidates share one background
    39	# (composition requires background agreement).  UNVERIFIED choice.
    40	N1S_BACKGROUND = BackgroundType.SMART
    41	
    42	
    43	class N1sModule:
    44	    region = REGION
    45	
    46	    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
    47	        return {"main": N1S_WINDOW}
    48	
    49	    def provenance(self) -> list[dict]:
    50	        return [
    51	            {"constant": "main_window_ev", "value": list(N1S_WINDOW),
    52	             "status": "UNVERIFIED",
    53	             "source": "spec §9: h-BN N 1s ~398.0–398.3 pending a primary "
    54	                       "table; window brackets spec range + labeled exemplar"},
    55	            {"constant": "fwhm_range_ev", "value": list(N1S_FWHM_RANGE),
    56	             "status": "UNVERIFIED", "source": "single labeled exemplar (1.05 eV)"},
    57	            {"constant": "asymmetry_range", "value": list(N1S_ASYM_RANGE),
    58	             "status": "UNVERIFIED", "source": "single labeled exemplar (0.064)"},
    59	            {"constant": "background", "value": "smart",
    60	             "status": "UNVERIFIED", "source": "matches U 4f family for co-fit"},
    61	        ]
    62	
    63	    def build_candidates(
    64	        self, phase: Phase, oxidation_state: Optional[str] = None
    65	    ) -> list[CandidateModel]:
    66	        if oxidation_state is not None:
    67	            raise KeyError(
    68	                f"N 1s defines no oxidation-state override {oxidation_state!r}"
    69	            )
    70	        pid = phase.id
    71	        _justification = (
    72	            "UNVERIFIED-empirical: single labeled exemplar only (fwhm "
    73	            "1.05 eV) -- no physical broadening mechanism cited; this is "
    74	            "Stage-3 minimal N 1s support, not the full cookbook module"
    75	        )
    76	        pv_main = ComponentSlot(
    77	            role="main_n1s", region=REGION, phase_id=pid,
    78	            be_window=N1S_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
    79	            fwhm_range=N1S_FWHM_RANGE,
    80	            broad_justification=_justification,
    81	        )
    82	        ag_main = ComponentSlot(
    83	            role="main_n1s", region=REGION, phase_id=pid,
    84	            be_window=N1S_WINDOW, line_shape=LineShape.ASYM_GL,
    85	            fwhm_range=N1S_FWHM_RANGE,
    86	            param_ranges=(("asymmetry", N1S_ASYM_RANGE),),
    87	            broad_justification=_justification,
    88	        )
    89	        return [
    90	            CandidateModel(name="N0_pv", background=N1S_BACKGROUND,
    91	                           slots=(pv_main,)),
    92	            CandidateModel(name="N0_asymGL", background=N1S_BACKGROUND,
    93	                           slots=(ag_main,)),
    94	        ]
    95	
    96	
    97	register_region(N1sModule())
   180	                                    separation but shape + amplitude still
   181	                                    tied: the clean test of "pair separation
   182	                                    ≠ core splitting"
   183	        - ``U2_mains_satfree``    — two fully independent satellites (each
   184	                                    rides its own main; robustness variant)
   185	
   186	        ``oxidation_state`` is accepted for the Layer-C seam; assignment is
   187	        parked (spec §3.2) so no overrides are defined.
   188	        """
   189	        if oxidation_state is not None:
   190	            raise KeyError(
   191	                f"U 4f defines no oxidation-state override {oxidation_state!r} "
   192	                "(oxidation-state assignment is parked, spec §3.2)"
   193	            )
   194	        pid = phase.id
   195	
   196	        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
   197	            return ComponentSlot(
   198	                role=role, region=REGION, phase_id=pid,
   199	                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
   200	            )
   201	
   202	        _main_justification = (
   203	            "U(IV) 5f2 open-shell final state: an unresolved multiplet "
   204	            "manifold of unknown line count is the physically-correct "
   205	            "reading of this width (VERIFIED mechanism, Ilton & Bagus, "
   206	            "Surf. Interface Anal. 43 (2011) 1549, DOI 10.1002/sia.3836; "
   207	            "see module docstring); the specific range is UNVERIFIED-"
   208	            "empirical (labeled set 2.44-2.74 eV)"
   209	        )
   210	        _sat_justification = (
   211	            "the U(IV) shake-up satellite is a real physical feature "
   212	            "(Ilton & Bagus 2011), but this specific WIDTH bound is "
   213	            "UNVERIFIED-empirical (labeled set 2.09-3.30 eV), not itself "
   214	            "derived from a cited broadening magnitude"
   215	        )
   216	
   217	        main_72 = slot(
   218	            "main_u4f72", U4F72_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
   219	            param_ranges=(("alpha", U4F_LACX_ALPHA_RANGE),
   220	                          ("beta", U4F_LACX_BETA_RANGE),
   221	                          ("m", U4F_LACX_M_RANGE)),
   222	            broad_justification=_main_justification,
   223	        )
   224	        main_52 = slot(
   225	            "main_u4f52", U4F52_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
   226	            linked_to="main_u4f72",
   227	            linked_offset_range=U4F_SPLITTING_RANGE,
   228	            area_ratio=U4F_RATIO_DEFAULT,
   229	            area_ratio_range=U4F_RATIO_RANGE,
   230	            share_parent_params=("alpha", "beta", "m", "fwhm"),
   231	            broad_justification=_main_justification,
   232	        )
   233	
   234	        sat_72 = slot(
   235	            "satellite_u4f72", U4F_SAT72_WINDOW, LineShape.PSEUDO_VOIGT,
   236	            U4F_SAT_FWHM_RANGE,
   237	            linked_to="main_u4f72",
   238	            linked_offset_range=U4F_SAT_OFFSET_RANGE,
   239	            broad_justification=_sat_justification,
   240	        )
   241	        sat_52 = slot(
   242	            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
   243	            U4F_SAT_FWHM_RANGE,
   244	            linked_to="satellite_u4f72",
   245	            linked_offset_range=U4F_SPLITTING_RANGE,
   246	            area_ratio=U4F_RATIO_DEFAULT,
   247	            area_ratio_range=U4F_RATIO_RANGE,
   248	            share_parent_params=("gl_ratio", "fwhm"),
   249	            broad_justification=_sat_justification,
   250	        )
   251	        # Free pair separation, everything else still tied (U1b).
   252	        sat_52_freesep = slot(
   253	            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
   254	            U4F_SAT_FWHM_RANGE,
   255	            linked_to="satellite_u4f72",
   256	            linked_offset_range=U4F_SATPAIR_SEP_RANGE,
   257	            area_ratio=U4F_RATIO_DEFAULT,
   258	            area_ratio_range=U4F_RATIO_RANGE,
   259	            share_parent_params=("gl_ratio", "fwhm"),
   260	            broad_justification=_sat_justification,
   261	        )
   262	
   263	        # Robustness variant: satellites ride their own mains independently
   264	        # (free amplitudes, independent offsets — no pair linkage).
   265	        sat_72_free = slot(
   266	            "satellite_u4f72", U4F_SAT72_WINDOW, LineShape.PSEUDO_VOIGT,
   267	            U4F_SAT_FWHM_RANGE,
   268	            linked_to="main_u4f72",
   269	            linked_offset_range=U4F_SAT_OFFSET_RANGE,
   270	            broad_justification=_sat_justification,
   271	        )
   272	        sat_52_free = slot(
   273	            "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
   274	            U4F_SAT_FWHM_RANGE,
   275	            linked_to="main_u4f52",
   276	            linked_offset_range=U4F_SAT_OFFSET_RANGE,
   277	            broad_justification=_sat_justification,
   278	        )
   279	
   280	        return [
   281	            CandidateModel(name="U0_mains", background=U4F_BACKGROUND,
   282	                           slots=(main_72, main_52)),
   283	            CandidateModel(name="U1_mains_satpair", background=U4F_BACKGROUND,
   284	                           slots=(main_72, main_52, sat_72, sat_52)),
   285	            CandidateModel(name="U1b_mains_satpair_freesep",

exec
/bin/zsh -lc "nl -ba autofit/regions/c1s.py | sed -n '285,350p'; nl -ba autofit/regions/cl2p.py | sed -n '130,180p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "rg -n \"ComponentSlot\\(\" autofit --glob '"'!**/__pycache__/**'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/candidates.py:463:        slots.append(ComponentSlot(
autofit/engine.py:1901:        ComponentSlot(
autofit/engine.py:2110:    proposed = ComponentSlot(
autofit/regions/c1s.py:309:            return ComponentSlot(
autofit/regions/u4f.py:197:            return ComponentSlot(
autofit/regions/b1s.py:92:            return ComponentSlot(
autofit/regions/cl2p.py:143:            return ComponentSlot(
autofit/regions/cl2p.py:154:                return ComponentSlot(
autofit/regions/cl2p.py:166:            return ComponentSlot(
autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
autofit/regions/n1s.py:82:        ag_main = ComponentSlot(

 succeeded in 0ms:
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
   130	        )
   131	        _coster_kronig_justification = (
   132	            "2p1/2 Coster-Kronig broadening is a genuine physical "
   133	            "mechanism (an additional non-radiative decay channel "
   134	            "unavailable to 2p3/2 shortens the 2p1/2 core-hole lifetime "
   135	            "and broadens its linewidth; adjudication 2026-07-03, "
   136	            "docs/autofit/adjudication-decisions.md #7), but the specific "
   137	            "excess bound (0.8 eV, ~45% of the labeled shared width) is "
   138	            "itself an UNVERIFIED bounded-relaxation tunable, not a cited "
   139	            "magnitude"
   140	        )
   141	
   142	        def p32() -> ComponentSlot:
   143	            return ComponentSlot(
   144	                role="main_cl2p32", region=REGION, phase_id=pid,
   145	                be_window=CL2P_32_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
   146	                fwhm_range=CL2P_FWHM_RANGE,
   147	                broad_justification=_empirical_justification,
   148	            )
   149	
   150	        def p12(ratio, ratio_range, free_width=False) -> ComponentSlot:
   151	            if free_width:
   152	                # independent width under the Coster-Kronig inequality
   153	                # (adjudication #7): fwhm12 = fwhm32 + excess, excess >= 0
   154	                return ComponentSlot(
   155	                    role="main_cl2p12", region=REGION, phase_id=pid,
   156	                    be_window=CL2P_12_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
   157	                    fwhm_range=CL2P_12_FWHM_RANGE,
   158	                    linked_to="main_cl2p32",
   159	                    linked_offset_range=CL2P_SPLITTING_RANGE,
   160	                    area_ratio=ratio,
   161	                    area_ratio_range=ratio_range,
   162	                    share_parent_params=("gl_ratio",),
   163	                    fwhm_excess_range=CL2P_12_FWHM_EXCESS_RANGE,
   164	                    broad_justification=_coster_kronig_justification,
   165	                )
   166	            return ComponentSlot(
   167	                role="main_cl2p12", region=REGION, phase_id=pid,
   168	                be_window=CL2P_12_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
   169	                fwhm_range=CL2P_FWHM_RANGE,
   170	                linked_to="main_cl2p32",
   171	                linked_offset_range=CL2P_SPLITTING_RANGE,
   172	                area_ratio=ratio,
   173	                area_ratio_range=ratio_range,
   174	                share_parent_params=("gl_ratio", "fwhm"),
   175	                broad_justification=_empirical_justification,
   176	            )
   177	
   178	        return [
   179	            CandidateModel(name="Cl0_doublet", background=CL2P_BACKGROUND,
   180	                           slots=(p32(), p12(CL2P_RATIO, None))),

exec
/bin/zsh -lc "rg -n \"replace\\(|dataclasses\\.replace|_replace\\(|ComponentSlot\\(|slots=.*\\+|slots=tuple|slots\\.append|for s in .*slots|for slot in .*slots\" autofit --glob '"'!**/__pycache__/**'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/candidates.py:463:        slots.append(ComponentSlot(
autofit/candidates.py:472:                          slots=tuple(slots)), dropped
autofit/criteria.py:68:    small = {s.role: s.line_shape for s in smaller.model.slots}
autofit/criteria.py:69:    large = {s.role: s.line_shape for s in larger.model.slots}
autofit/engine.py:325:    for slot in model.slots:
autofit/engine.py:456:    primary = [s for s in model.slots if s.linked_to is None]
autofit/engine.py:512:    for slot in model.slots:
autofit/engine.py:529:    done_roles = {s.role for s in model.slots if s.linked_to is None}
autofit/engine.py:530:    pending = [s for s in model.slots if s.linked_to is not None]
autofit/engine.py:659:    for slot in model.slots:
autofit/engine.py:706:    role_by_prefix = {_slot_prefix(s.role): s.role for s in model.slots}
autofit/engine.py:707:    shape_by_role = {s.role: s.line_shape for s in model.slots}
autofit/engine.py:784:    slots_by_role = {s.role: s for s in model.slots}
autofit/engine.py:941:    for slot in model.slots:
autofit/engine.py:978:    for slot in model.slots:
autofit/engine.py:1048:    slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
autofit/engine.py:1074:        candidate_slots = [s for s in model.slots if _accepts(s, comp)]
autofit/engine.py:1083:        shapes = {s.line_shape for s in candidate_slots}
autofit/engine.py:1086:                preferred = [s for s in candidate_slots if s.line_shape in asym_shapes]
autofit/engine.py:1088:                preferred = [s for s in candidate_slots if s.line_shape not in asym_shapes]
autofit/engine.py:1182:    pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
autofit/engine.py:1183:    fw: dict[str, list[float]] = {s.role: [] for s in model.slots}
autofit/engine.py:1184:    am: dict[str, list[float]] = {s.role: [] for s in model.slots}
autofit/engine.py:1185:    occupied: dict[str, int] = {s.role: 0 for s in model.slots}
autofit/engine.py:1311:    non_main = [s for s in model.slots if not _is_main_role(s.role)]
autofit/engine.py:1355:    for s in model.slots:
autofit/engine.py:1728:                diff = {s.role for s in a.model.slots} ^ {s.role for s in b.model.slots}
autofit/engine.py:1785:    wins = [s.be_window for c in candidates for s in c.slots]
autofit/engine.py:1901:        ComponentSlot(
autofit/engine.py:1914:        slots=base.slots + seeded,
autofit/engine.py:1950:            for s in model.slots if _is_main_role(s.role)]
autofit/engine.py:1991:    for slot in base_model.slots:
autofit/engine.py:2095:    for s in model.slots:
autofit/engine.py:2110:    proposed = ComponentSlot(
autofit/engine.py:2121:        slots=base.slots + (proposed,),
autofit/engine.py:2446:        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
autofit/engine.py:2711:                         for s in det_model.slots])
autofit/grammar.py:206:        for s in self.slots:
autofit/grammar.py:454:            for s in cand.slots:
autofit/grammar.py:469:    sanitized = [re.sub(r"[^A-Za-z0-9_]", "", s.replace(" ", ""))
autofit/grammar.py:512:        for slot in cand.slots:
autofit/grammar.py:529:        roles = [s.role for s in cand.slots]
autofit/grammar.py:532:        for slot in cand.slots:
autofit/grammar.py:568:            slug = re.sub(r"[^A-Za-z0-9_]", "", slug.replace(" ", ""))
autofit/grammar.py:569:            rename = {s.role: f"{slug}__{s.role}" for s in cand.slots}
autofit/grammar.py:571:            for s in cand.slots:
autofit/grammar.py:572:                slots.append(_retag_slot(s, rename, shared_rename))
autofit/grammar.py:578:            slots=tuple(slots),
autofit/grammar.py:591:    Uses dataclasses.replace (ComponentSlot is frozen) rather than
autofit/grammar.py:592:    reconstructing the slot field-by-field: replace() carries every field
autofit/grammar.py:616:    return replace(
autofit/regions/u4f.py:197:            return ComponentSlot(
autofit/methods/bayesian_exchange_mc.py:516:    for slot in model.slots:
autofit/methods/ic_model_comparison.py:107:            for slot in top.model.slots
autofit/methods/ic_model_comparison.py:112:            slot.role for slot in top.model.slots
autofit/methods/ic_model_comparison.py:212:    for slot in report.model.slots:
autofit/regions/c1s.py:309:            return ComponentSlot(
autofit/regions/c1s.py:367:                slots=tuple(slots), shared_fwhm_params=tuple(shared),
autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
autofit/regions/n1s.py:82:        ag_main = ComponentSlot(
autofit/regions/cl2p.py:143:            return ComponentSlot(
autofit/regions/cl2p.py:154:                return ComponentSlot(
autofit/regions/cl2p.py:166:            return ComponentSlot(
autofit/methods/sparse_map.py:83:        for s in cand.slots:
autofit/regions/b1s.py:92:            return ComponentSlot(
autofit/regions/b1s.py:110:                                  slots=tuple(slots))

exec
/bin/zsh -lc "nl -ba autofit/regions/c1s.py | sed -n '346,380p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba autofit/regions/u4f.py | sed -n '280,315p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   280	        return [
   281	            CandidateModel(name="U0_mains", background=U4F_BACKGROUND,
   282	                           slots=(main_72, main_52)),
   283	            CandidateModel(name="U1_mains_satpair", background=U4F_BACKGROUND,
   284	                           slots=(main_72, main_52, sat_72, sat_52)),
   285	            CandidateModel(name="U1b_mains_satpair_freesep",
   286	                           background=U4F_BACKGROUND,
   287	                           slots=(main_72, main_52, sat_72, sat_52_freesep)),
   288	            CandidateModel(name="U2_mains_satfree", background=U4F_BACKGROUND,
   289	                           slots=(main_72, main_52, sat_72_free, sat_52_free)),
   290	        ]
   291	
   292	
   293	register_region(U4fModule())

exec
/bin/zsh -lc "nl -ba autofit/regions/cl2p.py | sed -n '178,200p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   178	        return [
   179	            CandidateModel(name="Cl0_doublet", background=CL2P_BACKGROUND,
   180	                           slots=(p32(), p12(CL2P_RATIO, None))),
   181	            CandidateModel(name="Cl0r_doublet_relaxed",
   182	                           background=CL2P_BACKGROUND,
   183	                           slots=(p32(), p12(CL2P_RATIO, CL2P_RATIO_RANGE))),
   184	            # Free-width variants (adjudication #7).  Cl0w carries the
   185	            # adjudicated physics: statistical 2:1 ratio held, widths
   186	            # independent — the enumeration arbitrates it against the
   187	            # shared-width and relaxed-ratio hypotheses.
   188	            CandidateModel(name="Cl0w_doublet_freewidth",
   189	                           background=CL2P_BACKGROUND,
   190	                           slots=(p32(), p12(CL2P_RATIO, None,
   191	                                             free_width=True))),
   192	            CandidateModel(name="Cl0rw_doublet_relaxed_freewidth",
   193	                           background=CL2P_BACKGROUND,
   194	                           slots=(p32(), p12(CL2P_RATIO, CL2P_RATIO_RANGE,
   195	                                             free_width=True))),
   196	        ]
   197	
   198	
   199	register_region(Cl2pModule())

exec
/bin/zsh -lc "rg -n \"broad_justification|fwhm_range=.*\\(["'^)]*2'"\\.[1-9]|FWHM_RANGE|_RANGE =\" autofit/regions" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/regions/u4f.py:54:U4F_SPLITTING_RANGE = (10.75, 10.95)
autofit/regions/u4f.py:62:U4F_RATIO_RANGE = (0.60, 0.85)
autofit/regions/u4f.py:75:U4F_MAIN_FWHM_RANGE = (1.5, 3.5)
autofit/regions/u4f.py:82:U4F_LACX_ALPHA_RANGE = (0.5, 2.0)
autofit/regions/u4f.py:83:U4F_LACX_BETA_RANGE = (1.0, 4.5)
autofit/regions/u4f.py:85:U4F_LACX_M_RANGE = (0.0, 100.0)
autofit/regions/u4f.py:91:U4F_SAT_OFFSET_RANGE = (5.5, 8.5)
autofit/regions/u4f.py:96:U4F_SATPAIR_SEP_RANGE = (10.5, 12.0)
autofit/regions/u4f.py:98:U4F_SAT_FWHM_RANGE = (1.5, 4.5)
autofit/regions/u4f.py:151:            {"constant": "satellite_fwhm_ev", "value": list(U4F_SAT_FWHM_RANGE),
autofit/regions/u4f.py:154:            {"constant": "main_fwhm_range_ev", "value": list(U4F_MAIN_FWHM_RANGE),
autofit/regions/u4f.py:218:            "main_u4f72", U4F72_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
autofit/regions/u4f.py:222:            broad_justification=_main_justification,
autofit/regions/u4f.py:225:            "main_u4f52", U4F52_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
autofit/regions/u4f.py:231:            broad_justification=_main_justification,
autofit/regions/u4f.py:236:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:239:            broad_justification=_sat_justification,
autofit/regions/u4f.py:243:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:249:            broad_justification=_sat_justification,
autofit/regions/u4f.py:254:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:260:            broad_justification=_sat_justification,
autofit/regions/u4f.py:267:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:270:            broad_justification=_sat_justification,
autofit/regions/u4f.py:274:            U4F_SAT_FWHM_RANGE,
autofit/regions/u4f.py:277:            broad_justification=_sat_justification,
autofit/regions/n1s.py:35:N1S_FWHM_RANGE = (0.7, 2.5)       # UNVERIFIED-empirical (exemplar 1.05 eV)
autofit/regions/n1s.py:36:N1S_ASYM_RANGE = (0.0, 0.3)       # UNVERIFIED-empirical (exemplar 0.064)
autofit/regions/n1s.py:55:            {"constant": "fwhm_range_ev", "value": list(N1S_FWHM_RANGE),
autofit/regions/n1s.py:79:            fwhm_range=N1S_FWHM_RANGE,
autofit/regions/n1s.py:80:            broad_justification=_justification,
autofit/regions/n1s.py:85:            fwhm_range=N1S_FWHM_RANGE,
autofit/regions/n1s.py:87:            broad_justification=_justification,
autofit/regions/b1s.py:49:B1S_FWHM_RANGE = (1.2, 2.5)
autofit/regions/b1s.py:75:            {"constant": "fwhm_range_ev", "value": list(B1S_FWHM_RANGE),
autofit/regions/b1s.py:95:                fwhm_range=B1S_FWHM_RANGE,
autofit/regions/b1s.py:96:                broad_justification=(
autofit/regions/c1s.py:60:FWHM_RANGE_GRAPHITIC = (0.4, 1.2)
autofit/regions/c1s.py:64:FWHM_RANGE_AROMATIC_POLYMER = (0.8, 1.8)
autofit/regions/c1s.py:70:FWHM_RANGE_SATELLITE = (1.0, 5.5)
autofit/regions/c1s.py:82:FWHM_RANGE_CONTAMINATION = (0.8, 2.0)
autofit/regions/c1s.py:84:# MIXED material class (2026-07-20): FWHM_RANGE_CONTAMINATION's ceiling is
autofit/regions/c1s.py:126:    """FWHM_RANGE_CONTAMINATION, widened under MIXED. See the constant
autofit/regions/c1s.py:129:        return (FWHM_RANGE_CONTAMINATION[0], FWHM_MIXED_CEILING_NUMERIC_GUARD_EV)
autofit/regions/c1s.py:130:    return FWHM_RANGE_CONTAMINATION
autofit/regions/c1s.py:148:ASYMGL_ASYMMETRY_RANGE = (0.0, 0.5)
autofit/regions/c1s.py:157:SATELLITE_OFFSET_RANGE = (5.5, 7.0)
autofit/regions/c1s.py:160:    "graphite": FWHM_RANGE_GRAPHITIC,
autofit/regions/c1s.py:161:    None: FWHM_RANGE_GRAPHITIC,          # default material for a conductor
autofit/regions/c1s.py:162:    "polymer": FWHM_RANGE_AROMATIC_POLYMER,
autofit/regions/c1s.py:194:            {"constant": "fwhm_graphitic_ev", "value": list(FWHM_RANGE_GRAPHITIC),
autofit/regions/c1s.py:197:             "value": FWHM_RANGE_CONTAMINATION[0],
autofit/regions/c1s.py:203:             "value": FWHM_RANGE_CONTAMINATION[1],
autofit/regions/c1s.py:210:            {"constant": "fwhm_satellite_ev", "value": list(FWHM_RANGE_SATELLITE),
autofit/regions/c1s.py:228:             "value": list(FWHM_RANGE_AROMATIC_POLYMER),
autofit/regions/c1s.py:305:        main_fwhm = _MAIN_FWHM_BY_MATERIAL.get(phase.material, FWHM_RANGE_GRAPHITIC)
autofit/regions/c1s.py:335:            FWHM_RANGE_SATELLITE,
autofit/regions/c1s.py:337:            broad_justification=(
autofit/regions/cl2p.py:51:CL2P_SPLITTING_RANGE = (1.55, 1.65)
autofit/regions/cl2p.py:53:CL2P_RATIO_RANGE = (0.45, 0.55)     # bounded relaxation variant — UNVERIFIED
autofit/regions/cl2p.py:54:CL2P_FWHM_RANGE = (1.2, 2.2)        # UNVERIFIED-empirical (labeled 1.65–1.80)
autofit/regions/cl2p.py:62:CL2P_12_FWHM_EXCESS_RANGE = (0.0, 0.8)
autofit/regions/cl2p.py:64:CL2P_12_FWHM_RANGE = (CL2P_FWHM_RANGE[0],
autofit/regions/cl2p.py:65:                      CL2P_FWHM_RANGE[1] + CL2P_12_FWHM_EXCESS_RANGE[1])
autofit/regions/cl2p.py:91:            {"constant": "fwhm_range_ev", "value": list(CL2P_FWHM_RANGE),
autofit/regions/cl2p.py:146:                fwhm_range=CL2P_FWHM_RANGE,
autofit/regions/cl2p.py:147:                broad_justification=_empirical_justification,
autofit/regions/cl2p.py:157:                    fwhm_range=CL2P_12_FWHM_RANGE,
autofit/regions/cl2p.py:164:                    broad_justification=_coster_kronig_justification,
autofit/regions/cl2p.py:169:                fwhm_range=CL2P_FWHM_RANGE,
autofit/regions/cl2p.py:175:                broad_justification=_empirical_justification,

exec
/bin/zsh -lc 'rg -n "BACKGROUND|BackgroundType" autofit/regions/cl2p.py autofit/regions/c1s.py autofit/regions/b1s.py autofit/regions/u4f.py autofit/regions/n1s.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/regions/n1s.py:24:    BackgroundType,
autofit/regions/n1s.py:40:N1S_BACKGROUND = BackgroundType.SMART
autofit/regions/n1s.py:90:            CandidateModel(name="N0_pv", background=N1S_BACKGROUND,
autofit/regions/n1s.py:92:            CandidateModel(name="N0_asymGL", background=N1S_BACKGROUND,
autofit/regions/u4f.py:38:    BackgroundType,
autofit/regions/u4f.py:110:U4F_BACKGROUND = BackgroundType.SMART
autofit/regions/u4f.py:281:            CandidateModel(name="U0_mains", background=U4F_BACKGROUND,
autofit/regions/u4f.py:283:            CandidateModel(name="U1_mains_satpair", background=U4F_BACKGROUND,
autofit/regions/u4f.py:286:                           background=U4F_BACKGROUND,
autofit/regions/u4f.py:288:            CandidateModel(name="U2_mains_satfree", background=U4F_BACKGROUND,
autofit/regions/b1s.py:24:    BackgroundType,
autofit/regions/b1s.py:53:B1S_BACKGROUND = BackgroundType.SMART_EXP
autofit/regions/b1s.py:109:            return CandidateModel(name=name, background=B1S_BACKGROUND,
autofit/regions/c1s.py:28:    BackgroundType,
autofit/regions/c1s.py:366:                name=name, background=BackgroundType.SHIRLEY,
autofit/regions/cl2p.py:39:    BackgroundType,
autofit/regions/cl2p.py:71:CL2P_BACKGROUND = BackgroundType.SMART_EXP
autofit/regions/cl2p.py:179:            CandidateModel(name="Cl0_doublet", background=CL2P_BACKGROUND,
autofit/regions/cl2p.py:182:                           background=CL2P_BACKGROUND,
autofit/regions/cl2p.py:189:                           background=CL2P_BACKGROUND,
autofit/regions/cl2p.py:193:                           background=CL2P_BACKGROUND,

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 pytest -q tests/autofit/test_broad_justification.py -p no:cacheprovider' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: pytest

codex
The only production `ComponentSlot(` sites are the region modules, detection model generation, preseed, proposal, and `_retag_slot`; the broader copy search only found `dataclasses.replace` on `CandidateModel`/reports elsewhere, not on slots. The sandbox blocks here-doc temp files and `pytest` is not on PATH, so I’m switching to `python -c` probes and `python -m pytest`.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python -c \"from autofit.grammar import Phase,MaterialClass,resolve; phases=[Phase(id='UCl4', material_class=MaterialClass.INSULATOR, regions=('U 4f',)), Phase(id='BN', material_class=MaterialClass.INSULATOR, regions=('N 1s',))]; g=resolve(phases, ['U 4f','N 1s']); checks=[('U0_mains+N0_pv','U4f__main_u4f72'),('U0_mains+N0_pv','U4f__main_u4f52'),('U0_mains+N0_pv','N1s__main_n1s'),('U1_mains_satpair+N0_pv','U4f__satellite_u4f72'),('U1_mains_satpair+N0_pv','U4f__satellite_u4f52'),('U1b_mains_satpair_freesep+N0_asymGL','U4f__satellite_u4f52'),('U2_mains_satfree+N0_asymGL','U4f__satellite_u4f72'),('U2_mains_satfree+N0_asymGL','U4f__satellite_u4f52')]; [print(cname, role, s.fwhm_range, bool(s.broad_justification), (s.broad_justification or '')[:48]) for cname,role in checks for cand in [next(c for c in g.candidates if c.name==cname)] for s in [cand.slot_by_role(role)]]; print('candidate_count', len(g.candidates))\"" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python -c \"import dataclasses; import autofit.engine as e; print('PROPOSAL_FWHM_MAX', repr(e.PROPOSAL_FWHM_MAX)); print('FWHM_MAX_ORDINARY_EV', repr(e.FWHM_MAX_ORDINARY_EV)); print('equal', e.PROPOSAL_FWHM_MAX == e.FWHM_MAX_ORDINARY_EV, 'identical', e.PROPOSAL_FWHM_MAX is e.FWHM_MAX_ORDINARY_EV)\"" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/autofit/test_broad_justification.py -p no:cacheprovider' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit.grammar import Phase,MaterialClass,resolve; phases=[Phase(id='UCl4', material_class=MaterialClass.INSULATOR, regions=('U 4f',)), Phase(id='BN', material_class=MaterialClass.INSULATOR, regions=('N 1s',))]; g=resolve(phases, ['U 4f','N 1s']); checks=[('U0_mains+N0_pv','U4f__main_u4f72'),('U0_mains+N0_pv','U4f__main_u4f52'),('U0_mains+N0_pv','N1s__main_n1s'),('U1_mains_satpair+N0_pv','U4f__satellite_u4f72'),('U1_mains_satpair+N0_pv','U4f__satellite_u4f52'),('U1b_mains_satpair_freesep+N0_asymGL','U4f__satellite_u4f52'),('U2_mains_satfree+N0_asymGL','U4f__satellite_u4f72'),('U2_mains_satfree+N0_asymGL','U4f__satellite_u4f52')]; [print(cname, role, s.fwhm_range, bool(s.broad_justification), (s.broad_justification or '')[:48]) for cname,role in checks for cand in [next(c for c in g.candidates if c.name==cname)] for s in [cand.slot_by_role(role)]]; print('candidate_count', len(g.candidates))\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-YzsrHIav' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-8qUXlIzn' (errno=Operation not permitted)
U0_mains+N0_pv U4f__main_u4f72 (1.5, 3.5) True U(IV) 5f2 open-shell final state: an unresolved 
U0_mains+N0_pv U4f__main_u4f52 (1.5, 3.5) True U(IV) 5f2 open-shell final state: an unresolved 
U0_mains+N0_pv N1s__main_n1s (0.7, 2.5) True UNVERIFIED-empirical: single labeled exemplar on
U1_mains_satpair+N0_pv U4f__satellite_u4f72 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical 
U1_mains_satpair+N0_pv U4f__satellite_u4f52 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical 
U1b_mains_satpair_freesep+N0_asymGL U4f__satellite_u4f52 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical 
U2_mains_satfree+N0_asymGL U4f__satellite_u4f72 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical 
U2_mains_satfree+N0_asymGL U4f__satellite_u4f52 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical 
candidate_count 8

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"import autofit.engine as e; print('PROPOSAL_FWHM_MAX', repr(e.PROPOSAL_FWHM_MAX)); print('FWHM_MAX_ORDINARY_EV', repr(e.FWHM_MAX_ORDINARY_EV)); print('equal', e.PROPOSAL_FWHM_MAX == e.FWHM_MAX_ORDINARY_EV, 'identical', e.PROPOSAL_FWHM_MAX is e.FWHM_MAX_ORDINARY_EV)\"" in /Users/skyefortier/xps-verify
 exited 1 in 213ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/autofit/engine.py", line 38, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

2026-07-20T18:56:23.314852Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The exact U 4f + N 1s repro now passes under `python3`: all checked composed slots carry a non-`None` justification. System Python lacks `pytest`/`lmfit`, so for engine-level imports I’m looking for the project virtualenv and otherwise using direct source inspection for the constant/control-flow claims.
exec
/bin/zsh -lc "find . -maxdepth 3 \\( -path './.venv/bin/python' -o -path './venv/bin/python' -o -path './env/bin/python' \\) -print" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
exec
/bin/zsh -lc "ls -la && rg --files -g 'pyproject.toml' -g 'requirements*.txt' -g 'Pipfile' -g 'poetry.lock' -g 'tox.ini' -g 'pytest.ini' -g '.venv/**/python*' -g 'venv/**/python*'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
total 560
drwxr-xr-x   29 skyefortier  staff    928 Jul 20 00:14 .
drwxr-xr-x+  74 skyefortier  staff   2368 Jul 20 12:52 ..
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
drwxr-xr-x  135 skyefortier  staff   4320 Jul 20 12:42 uploads
-rw-r--r--    1 skyefortier  staff   6062 Jul 10 15:28 vgd_parser.py
-rw-r--r--    1 skyefortier  staff  68252 Jul 10 15:28 xps-fitting-tool.html
-rw-r--r--    1 skyefortier  staff  18124 Jul 10 15:28 xps_reference.py
requirements.txt
requirements-dev.txt

exec
/bin/zsh -lc "git show --color=never 5070662:autofit/grammar.py | sed -n '584,625p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-SNpHew35' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-siV90CVm' (errno=Operation not permitted)
def _retag_slot(
    s: ComponentSlot,
    rename: dict[str, str],
    shared_rename: dict[str, str],
) -> ComponentSlot:
    """Rewrite role / linked_to / fwhm_linked_to under the region prefix."""
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
    return ComponentSlot(
        role=rename[s.role],
        region=s.region,
        phase_id=s.phase_id,
        be_window=s.be_window,
        line_shape=s.line_shape,
        fwhm_range=s.fwhm_range,
        linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None,
        linked_offset_range=s.linked_offset_range,
        area_ratio=s.area_ratio,
        area_ratio_range=s.area_ratio_range,
        fixed_params=s.fixed_params,
        param_ranges=s.param_ranges,
        fwhm_linked_to=fwhm_link,
        share_parent_params=s.share_parent_params,
        fwhm_excess_range=s.fwhm_excess_range,
    )


def _slot_param_prefix(role: str) -> str:
    """Must match engine._slot_prefix — kept here to rewrite fwhm links."""
    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"

2026-07-20T18:56:31.895728Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The old `_retag_slot` body from `5070662` omits `broad_justification`, exactly as described. I’m exercising the structural guard’s logic in memory now, without modifying files.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"import dataclasses, re; from autofit.grammar import ComponentSlot, LineShape, _retag_slot, _slot_param_prefix; sentinel={'role':'orig_role','region':'orig_region','phase_id':'orig_phase','be_window':(100.0,200.0),'line_shape':LineShape.PSEUDO_VOIGT,'fwhm_range':(0.5,9.99),'linked_to':'orig_role','linked_offset_range':(1.0,2.0),'area_ratio':0.123456,'area_ratio_range':(0.1,0.9),'fixed_params':(('beta',0.05),),'param_ranges':(('alpha',(0.0,0.3)),),'fwhm_linked_to':None,'fwhm_excess_range':(0.0,0.8),'share_parent_params':('alpha','beta'),'broad_justification':'sentinel justification text'}; original=ComponentSlot(**sentinel); rename={'orig_role':'PhaseX__orig_role'}; new=_retag_slot(original, rename, {}); fields={f.name for f in dataclasses.fields(ComponentSlot)}; rewritten={'role','linked_to','fwhm_linked_to'}; print('new_mismatches', [(n,getattr(original,n),getattr(new,n)) for n in sorted(fields-rewritten) if getattr(original,n)"'!=getattr(new,n)]); fwhm_link=original.fwhm_linked_to; old=ComponentSlot(role=rename[original.role], region=original.region, phase_id=original.phase_id, be_window=original.be_window, line_shape=original.line_shape, fwhm_range=original.fwhm_range, linked_to=rename.get(original.linked_to, original.linked_to) if original.linked_to else None, linked_offset_range=original.linked_offset_range, area_ratio=original.area_ratio, area_ratio_range=original.area_ratio_range, fixed_params=original.fixed_params, param_ranges=original.param_ranges, fwhm_linked_to=fwhm_link, share_parent_params=original.share_parent_params, fwhm_excess_range=original.fwhm_excess_range); print('"'old_mismatches', [(n,getattr(original,n),getattr(old,n)) for n in sorted(fields-rewritten) if getattr(original,n)"'!=getattr(old,n)])"' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-zOEcw0WV' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-GrLYNq0F' (errno=Operation not permitted)
new_mismatches []
old_mismatches [('broad_justification', 'sentinel justification text', None)]

2026-07-20T18:56:55.123831Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The guard behaves as intended in a direct probe: the new implementation preserves every non-rewritten field, while the old manual reconstruction loses only `broad_justification` in that sentinel case. I’m rerunning the broader composition probe with shell-safe quoting.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import Phase,MaterialClass,resolve\\ncombos=[([Phase(id=\"Cgraph\", material_class=MaterialClass.CONDUCTOR, material=\"graphite\", regions=(\"C 1s\",)), Phase(id=\"ClSalt\", material_class=MaterialClass.INSULATOR, regions=(\"Cl 2p\",))], [\"C 1s\",\"Cl 2p\"]), ([Phase(id=\"B4C\", material_class=MaterialClass.INSULATOR, regions=(\"B 1s\",)), Phase(id=\"UCl4\", material_class=MaterialClass.INSULATOR, regions=(\"Cl 2p\",))], [\"B 1s\",\"Cl 2p\"]), ([Phase(id=\"UCl4\", material_class=MaterialClass.INSULATOR, regions=(\"U 4f\",)), Phase(id=\"BN\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",)), Phase(id=\"BNb\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",))], [\"U 4f\",\"N 1s\",\"N 1s\"])]\\nfor phases, regs in combos:\\n    print(\"COMBO\", [p.id for p in phases], regs)\\n    try:\\n        g=resolve(phases, regs)\\n        bad=[]; seen=0\\n        for c in g.candidates:\\n            for s in c.slots:\\n                if s.fwhm_range[1] > 2.0 and s.broad_justification is None:\\n                    bad.append((c.name,s.role,s.fwhm_range))\\n                if s.broad_justification is not None:\\n                    seen += 1\\n        print(\"candidates\", len(g.candidates), \"justified_slots_seen\", seen, \"bad_wide_unjustified\", bad[:10])\\n    except Exception as e:\\n        print(type(e).__name__, str(e))'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-GfBfMXoI' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-8oZcK4zW' (errno=Operation not permitted)
COMBO ['Cgraph', 'ClSalt'] ['C 1s', 'Cl 2p']
ValueError joint candidates must share one background, got {<BackgroundType.SHIRLEY: 'shirley'>, <BackgroundType.SMART_EXP: 'smart_exp'>} for ['A0_graphite_asym_satellite', 'Cl0_doublet']
COMBO ['B4C', 'UCl4'] ['B 1s', 'Cl 2p']
candidates 16 justified_slots_seen 64 bad_wide_unjustified []
COMBO ['UCl4', 'BN', 'BNb'] ['U 4f', 'N 1s', 'N 1s']
PhaseAmbiguityError region 'N 1s' appears in phases ['BN', 'BNb'] — request it per-phase (('N 1s', <phase_id>)) or pass target_phases={'N 1s': <phase_id>} (spec v2.1 §2: region is not a unique key)

2026-07-20T18:57:08.057019Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '410,540p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   410	            # the machine tier may already carry an (UNVERIFIED) entry
   411	            db_prov, db_notes = _fit_physics_provenance(
   412	                region, provenance[slug], slot_facts=None)
   413	            provenance[slug].extend(db_prov)
   414	            notes.extend(f"{slug}: {note}" for note in db_notes)
   415	            if any(str(r.get("constant", "")).startswith("fit_physics:")
   416	                   for r in db_prov):
   417	                # exposure semantics, stated where a consumer will read
   418	                # them: these are SOURCED tier values (sha256-pinned NIST
   419	                # archive; tier-status UNVERIFIED/CONDITIONAL), relayed
   420	                # for reference and curation — NOT used to build
   421	                # candidates, windows, or any fit-enabling quantity here
   422	                notes.append(
   423	                    f"{slug}: fit-physics DB entries exposed for reference "
   424	                    "only (sourced tier, hand-verification pending) — not "
   425	                    "used to build candidates or windows; positions remain "
   426	                    "UNVERIFIED until cited/curated")
   427	            continue
   428	
   429	        candidates = module.build_candidates(chosen, oxidation_state=oxidation_state)
   430	        _guard_slot_tags(candidates, region, chosen.id)
   431	        per_request_candidates.append(candidates)
   432	        slugs.append(slug)
   433	        all_slugs.append(slug)
   434	        used_phase_ids.append(chosen.id)
   435	        notes.append(
   436	            f"{slug}: phase {chosen.id!r} ({chosen.material_class.value}"
   437	            + (f", {chosen.material}" if chosen.material else "")
   438	            + f"), {len(candidates)} candidates"
   439	        )
   440	        for label, win in module.diagnostic_windows().items():
   441	            diagnostic_windows[f"{slug}:{label}"] = win
   442	        prov_fn = getattr(module, "provenance", None)
   443	        provenance[slug] = list(prov_fn()) if callable(prov_fn) else []
   444	        # tiered fit-physics DB exposure (run-brief item 4): the DB's
   445	        # matching entries + mechanical cross-checks ride along in the
   446	        # provenance (→ analysis namespace); candidate construction is
   447	        # untouched — grammar constants stand until the machine-tier
   448	        # human review (see autofit/fit_physics.py)
   449	        # slot FACTS (the constants actually building candidates) ride
   450	        # along so the DB cross-check cannot be satisfied by stale
   451	        # provenance prose alone (Codex analyze review)
   452	        slot_facts = {"splitting": [], "ratio": []}
   453	        for cand in candidates:
   454	            for s in cand.slots:
   455	                if s.linked_offset_range and s.area_ratio is not None:
   456	                    slot_facts["splitting"].append(
   457	                        (float(s.linked_offset_range[0]),
   458	                         float(s.linked_offset_range[1])))
   459	                    slot_facts["ratio"].append(float(s.area_ratio))
   460	        db_prov, db_notes = _fit_physics_provenance(
   461	            region, provenance[slug], slot_facts=slot_facts)
   462	        provenance[slug].extend(db_prov)
   463	        notes.extend(f"{slug}: {note}" for note in db_notes)
   464	
   465	    # Role-prefix collision guard (Codex Stage-2 re-review finding #2): the
   466	    # composition sanitizer strips non-alphanumerics from slugs, so distinct
   467	    # phase ids like 'B-4C' and 'B4C' would collapse into one role prefix and
   468	    # silently collide in the lmfit parameter namespace.  Fail loudly instead.
   469	    sanitized = [re.sub(r"[^A-Za-z0-9_]", "", s.replace(" ", ""))
   470	                 for s in all_slugs]
   471	    if len(set(sanitized)) != len(sanitized):
   472	        dupes = sorted({s for s in sanitized if sanitized.count(s) > 1})
   473	        raise ValueError(
   474	            f"phase-qualified role slugs collide after sanitization: {dupes} — "
   475	            "phase ids must remain distinct once spaces/punctuation are removed"
   476	        )
   477	
   478	    # Composition runs over MODULE-BACKED requests only: a structural-
   479	    # fallback region has no candidates, and letting its empty set into the
   480	    # cartesian product would wipe the deep regions' candidates.
   481	    if not per_request_candidates:
   482	        composed: list[CandidateModel] = []
   483	    elif len(per_request_candidates) == 1:
   484	        composed = per_request_candidates[0]
   485	    else:
   486	        composed = _compose_joint_candidates(slugs, per_request_candidates)
   487	        notes.append(
   488	            f"joint co-fit of {slugs}: {len(composed)} composed candidates"
   489	        )
   490	    if structural_regions and len(requests) > 1:
   491	        notes.append(
   492	            f"structural-fallback region(s) {structural_regions} excluded "
   493	            "from candidate composition (derived structure only — no "
   494	            "windows or candidates to compose)")
   495	
   496	    grammar = CandidateGrammar(
   497	        regions=tuple(region for region, _ in requests),
   498	        phase_ids=tuple(dict.fromkeys(used_phase_ids)),
   499	        candidates=composed,
   500	        diagnostic_windows=diagnostic_windows,
   501	        notes=notes,
   502	        provenance=provenance,
   503	        structural_only=tuple(structural_regions),
   504	    )
   505	    _guard_phase_leakage(grammar, phases)
   506	    return grammar
   507	
   508	
   509	def _guard_slot_tags(candidates: list[CandidateModel], region: str, phase_id: str) -> None:
   510	    """Region modules must tag every slot with the region + resolved phase."""
   511	    for cand in candidates:
   512	        for slot in cand.slots:
   513	            if slot.region != region:
   514	                raise ValueError(
   515	                    f"candidate {cand.name!r}: slot {slot.role!r} tagged region "
   516	                    f"{slot.region!r}, expected {region!r}"
   517	                )
   518	            if slot.phase_id != phase_id:
   519	                raise ValueError(
   520	                    f"candidate {cand.name!r}: slot {slot.role!r} tagged phase "
   521	                    f"{slot.phase_id!r}, expected {phase_id!r} (phase-id leakage)"
   522	                )
   523	
   524	
   525	def _guard_phase_leakage(grammar: CandidateGrammar, phases: list[Phase]) -> None:
   526	    """Every slot's phase must be declared AND contribute the slot's region."""
   527	    by_id = {p.id: p for p in phases}
   528	    for cand in grammar.candidates:
   529	        roles = [s.role for s in cand.slots]
   530	        if len(set(roles)) != len(roles):
   531	            raise ValueError(f"candidate {cand.name!r}: duplicate slot roles {roles}")
   532	        for slot in cand.slots:
   533	            phase = by_id.get(slot.phase_id)
   534	            if phase is None:
   535	                raise ValueError(
   536	                    f"candidate {cand.name!r}: slot {slot.role!r} references "
   537	                    f"undeclared phase {slot.phase_id!r}"
   538	                )
   539	            if slot.region not in phase.regions:
   540	                raise ValueError(

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import Phase,MaterialClass,resolve\\nphases=[Phase(id=\"UCl4\", material_class=MaterialClass.INSULATOR, regions=(\"U 4f\",)), Phase(id=\"BN\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",)), Phase(id=\"BNb\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",))]\\nfor req in [[(\"U 4f\",\"UCl4\"),(\"N 1s\",\"BN\"),(\"N 1s\",\"BNb\")], [(\"U 4f\",\"UCl4\"),(\"N 1s\",\"BN\")]]:\\n    print(\"REQ\", req)\\n    try:\\n        g=resolve(phases, req)\\n        bad=[]; seen=0; sample=[]\\n        for c in g.candidates:\\n            for s in c.slots:\\n                if s.fwhm_range[1] > 2.0 and s.broad_justification is None: bad.append((c.name,s.role,s.fwhm_range))\\n                if s.broad_justification is not None: seen+=1; sample.append((c.name,s.role))\\n        print(\"candidates\", len(g.candidates), \"justified_slots_seen\", seen, \"bad\", bad[:10], \"sample\", sample[:6])\\n    except Exception as e: print(type(e).__name__, str(e))'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-Z3gUgTyQ' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-Ueh6XngC' (errno=Operation not permitted)
REQ [('U 4f', 'UCl4'), ('N 1s', 'BN'), ('N 1s', 'BNb')]
candidates 16 justified_slots_seen 88 bad [] sample [('U0_mains+N0_pv+N0_pv', 'U4f__main_u4f72'), ('U0_mains+N0_pv+N0_pv', 'U4f__main_u4f52'), ('U0_mains+N0_pv+N0_pv', 'N1sBN__main_n1s'), ('U0_mains+N0_pv+N0_pv', 'N1sBNb__main_n1s'), ('U0_mains+N0_pv+N0_asymGL', 'U4f__main_u4f72'), ('U0_mains+N0_pv+N0_asymGL', 'U4f__main_u4f52')]
REQ [('U 4f', 'UCl4'), ('N 1s', 'BN')]
candidates 8 justified_slots_seen 36 bad [] sample [('U0_mains+N0_pv', 'U4f__main_u4f72'), ('U0_mains+N0_pv', 'U4f__main_u4f52'), ('U0_mains+N0_pv', 'N1s__main_n1s'), ('U0_mains+N0_asymGL', 'U4f__main_u4f72'), ('U0_mains+N0_asymGL', 'U4f__main_u4f52'), ('U0_mains+N0_asymGL', 'N1s__main_n1s')]

2026-07-20T18:57:18.820882Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '1,90p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	Model-comparison engine — the fitalg pipeline ported onto main's fitting.py
     3	and generalized to region-agnostic grammars (spec v2.1 §6).
     4	
     5	Pipeline per candidate: primary fit → N perturbed refits (stability) →
     6	slot matching by grammar role → absent-slot detection → residual
     7	diagnostics → residual-guided proposal pass → filter-then-rank with BIC*.
     8	
     9	Provenance: ported from the public ``xps-app-fitalg`` repo's
    10	``model_comparison.py`` (validated there on HOPG + PET C 1s).  Changes made
    11	in the port, besides symbol renames:
    12	
    13	- lineshape layer rebuilt against CURRENT ``fitting.py``: fitalg's
    14	  ``LA_ASYMMETRIC`` (α, β=Lorentzian-HWHM, m_gauss) is main's ``ds_g``; the
    15	  true CasaXPS ``la_casaxps`` (exponent α/β + kernel-points m) is new here,
    16	  as are ``asymmetric_gl`` / ``gaussian`` / ``lorentzian``.
    17	- generic per-slot ``fixed_params`` / ``param_ranges`` replace the
    18	  LA-specific ``fixed_lorentzian_hwhm`` / ``alpha_range`` fields.
    19	- spin-orbit amplitude linkage (``area_ratio`` fixed, or
    20	  ``area_ratio_range`` bounded-relaxed) — needed by doublet regions.
    21	- boundary-hit shape-parameter exclusions are per-lineshape (a width-like
    22	  ``beta`` in DS+G at a bound is a pathology; an exponent-like ``beta`` in
    23	  LACX at a bound is a shape preference).
    24	
    25	All numeric thresholds below are **UNVERIFIED tunables** (spec §9 —
    26	sensitivity-test before publication claims); they carry fitalg's defaults.
    27	"""
    28	
    29	from __future__ import annotations
    30	
    31	import logging
    32	import re
    33	import time
    34	from dataclasses import dataclass, field
    35	from typing import Callable, Optional
    36	
    37	import numpy as np
    38	from lmfit import Model, Parameters
    39	from lmfit.model import ModelResult
    40	from scipy.integrate import trapezoid
    41	
    42	from fitting import _SHAPE_FUNCS, linear_background, shirley_background, smart_background
    43	
    44	from .candidates import (build_candidate_pool, build_detection_candidate,
    45	                         merge_residual_attempts)
    46	
    47	from .grammar import (
    48	    BACKEND_SHAPE,
    49	    BackgroundType,
    50	    CandidateGrammar,
    51	    CandidateModel,
    52	    ComponentSlot,
    53	    LineShape,
    54	)
    55	
    56	log = logging.getLogger(__name__)
    57	
    58	
    59	# ─────────────────────────────────────────────────────────────────────────────
    60	# UNVERIFIED tunables (fitalg defaults; spec §9 sensitivity-test items)
    61	# ─────────────────────────────────────────────────────────────────────────────
    62	
    63	ABSENT_SLOT_AREA_FRACTION = 0.02
    64	ABSENT_SLOT_PERSISTENCE_THRESHOLD = 0.7
    65	DEFAULT_PERSISTENCE_THRESHOLD = 0.7
    66	DEFAULT_BIC_AMBIGUITY = 2.0
    67	# Decisive-override DOMINANCE rule (Codex cookbook review, blockers 2–3).
    68	# A stable-but-boundary-limited candidate is promoted ahead of the clean
    69	# tier only when ALL of the following hold:
    70	#   (1) it is REFIT with its pegged parameters FIXED at their bounds — the
    71	#       Laplace-style BIC* approximation is invalid at a constraint wall,
    72	#       and the fixed-bound refit gives an honest parameter count;
    73	#   (2) the refit's BIC* beats the best clean candidate's by more than
    74	#       CONDITIONAL_OVERRIDE_DELTA_BIC (10 — the conventional "very strong"
    75	#       threshold, Kass & Raftery, JASA 90 (1995) 773; UNVERIFIED as applied
    76	#       to this heuristic BIC* on processed XPS data — tunable);
    77	#   (3) its reduced χ² is also strictly better (BIC* is never the sole
    78	#       decision axis — spec §6 trust order); and
    79	#   (4) the clean best shows residual-structure flags (autocorrelation or
    80	#       flagged windows) — evidence that it is genuinely mis-fitting, not
    81	#       merely losing a scalar comparison.
    82	# The clean survivors are KEPT as ranked alternatives after the promoted
    83	# candidate; the result carries conditional_reason='decisive_override'.
    84	# Without any override, a clean-but-terrible fit masks a decisively better
    85	# fit that merely brushes a constraint wall (observed on the U 4f + N 1s
    86	# co-fit: clean χ²ᵣ 38 vs boundary-limited χ²ᵣ 7).
    87	CONDITIONAL_OVERRIDE_DELTA_BIC = 10.0
    88	
    89	PROPOSAL_WINDOW_WIDTH = 0.5
    90	PROPOSAL_WINDOW_STRIDE = 0.25

2026-07-20T18:57:51.667272Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The additional composition checks are clean: B 1s + Cl 2p produced 16 composed candidates with no wide unjustified slots, and a 3-request U 4f + two phase-qualified N 1s composition produced 16 candidates with no losses. A C 1s + Cl 2p composition is correctly rejected because the candidate backgrounds differ.
exec
/bin/zsh -lc "rg -n \"ComponentSlot|CandidateModel\\(|dataclasses\\.replace|from dataclasses import|import dataclasses\" autofit --glob '"'!**/__pycache__/**'"'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/candidates.py:48:from dataclasses import dataclass
autofit/candidates.py:427:    from .grammar import CandidateModel, ComponentSlot, LineShape
autofit/candidates.py:463:        slots.append(ComponentSlot(
autofit/candidates.py:471:    return CandidateModel(name=name, background=background,
autofit/grammar.py:16:``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
autofit/grammar.py:30:from dataclasses import dataclass, field, replace
autofit/grammar.py:37:    "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
autofit/grammar.py:115:class ComponentSlot:
autofit/grammar.py:197:    slots: tuple[ComponentSlot, ...]
autofit/grammar.py:205:    def slot_by_role(self, role: str) -> Optional[ComponentSlot]:
autofit/grammar.py:565:        slots: list[ComponentSlot] = []
autofit/grammar.py:575:        composed.append(CandidateModel(
autofit/grammar.py:585:    s: ComponentSlot,
autofit/grammar.py:588:) -> ComponentSlot:
autofit/grammar.py:591:    Uses dataclasses.replace (ComponentSlot is frozen) rather than
autofit/grammar.py:594:    to ComponentSlot after this function was written. The manual
autofit/reference.py:23:from dataclasses import dataclass, field
autofit/criteria.py:25:from dataclasses import dataclass
autofit/cited_values.py:35:from dataclasses import dataclass
autofit/regions/u4f.py:40:    ComponentSlot,
autofit/regions/u4f.py:196:        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
autofit/regions/u4f.py:197:            return ComponentSlot(
autofit/regions/u4f.py:281:            CandidateModel(name="U0_mains", background=U4F_BACKGROUND,
autofit/regions/u4f.py:283:            CandidateModel(name="U1_mains_satpair", background=U4F_BACKGROUND,
autofit/regions/u4f.py:285:            CandidateModel(name="U1b_mains_satpair_freesep",
autofit/regions/u4f.py:288:            CandidateModel(name="U2_mains_satfree", background=U4F_BACKGROUND,
autofit/regions/cl2p.py:41:    ComponentSlot,
autofit/regions/cl2p.py:142:        def p32() -> ComponentSlot:
autofit/regions/cl2p.py:143:            return ComponentSlot(
autofit/regions/cl2p.py:150:        def p12(ratio, ratio_range, free_width=False) -> ComponentSlot:
autofit/regions/cl2p.py:154:                return ComponentSlot(
autofit/regions/cl2p.py:166:            return ComponentSlot(
autofit/regions/cl2p.py:179:            CandidateModel(name="Cl0_doublet", background=CL2P_BACKGROUND,
autofit/regions/cl2p.py:181:            CandidateModel(name="Cl0r_doublet_relaxed",
autofit/regions/cl2p.py:188:            CandidateModel(name="Cl0w_doublet_freewidth",
autofit/regions/cl2p.py:192:            CandidateModel(name="Cl0rw_doublet_relaxed_freewidth",
autofit/noise.py:57:from dataclasses import dataclass, field
autofit/regions/c1s.py:30:    ComponentSlot,
autofit/regions/c1s.py:308:        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
autofit/regions/c1s.py:309:            return ComponentSlot(
autofit/regions/c1s.py:314:        def graphitic_main_dsg() -> ComponentSlot:
autofit/regions/c1s.py:322:        def graphitic_main_asymgl() -> ComponentSlot:
autofit/regions/c1s.py:329:        def aliphatic_main() -> ComponentSlot:
autofit/regions/c1s.py:347:                   fwhm_range=None) -> ComponentSlot:
autofit/regions/c1s.py:365:            candidates.append(CandidateModel(
autofit/regions/c1s.py:423:        def aliphatic_main_offset() -> ComponentSlot:
autofit/regions/b1s.py:26:    ComponentSlot,
autofit/regions/b1s.py:91:        def pv(role, window) -> ComponentSlot:
autofit/regions/b1s.py:92:            return ComponentSlot(
autofit/regions/b1s.py:109:            return CandidateModel(name=name, background=B1S_BACKGROUND,
autofit/regions/n1s.py:26:    ComponentSlot,
autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
autofit/regions/n1s.py:82:        ag_main = ComponentSlot(
autofit/regions/n1s.py:90:            CandidateModel(name="N0_pv", background=N1S_BACKGROUND,
autofit/regions/n1s.py:92:            CandidateModel(name="N0_asymGL", background=N1S_BACKGROUND,
autofit/engine.py:34:from dataclasses import dataclass, field
autofit/engine.py:52:    ComponentSlot,
autofit/engine.py:368:    p: Parameters, prefix: str, slot: ComponentSlot, fwhm_init: float,
autofit/engine.py:386:        # (Coster-Kronig doublet broadening — grammar.ComponentSlot docs)
autofit/engine.py:531:    ordered: list[ComponentSlot] = []
autofit/engine.py:761:    only if it carries an explicit ``ComponentSlot.broad_justification``
autofit/engine.py:1016:    slot: ComponentSlot, components: list[FittedComponent],
autofit/engine.py:1052:    def _accepts(slot: ComponentSlot, comp: FittedComponent) -> bool:
autofit/engine.py:1059:    def _window_center(slot: ComponentSlot) -> float:
autofit/engine.py:1291:def _count_slot_free_params(slot: ComponentSlot, primary: FitOutcome) -> int:
autofit/engine.py:1304:def _linked_groups(model: CandidateModel) -> list[list[ComponentSlot]]:
autofit/engine.py:1321:    groups: dict[str, list[ComponentSlot]] = {}
autofit/engine.py:1361:    def _member_report(slot: ComponentSlot) -> Optional[AbsentSlotReport]:
autofit/engine.py:1901:        ComponentSlot(
autofit/engine.py:1911:    return CandidateModel(
autofit/engine.py:2110:    proposed = ComponentSlot(
autofit/engine.py:2118:    return CandidateModel(
autofit/engine.py:2405:    import dataclasses
autofit/engine.py:2446:        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
autofit/methods/base.py:13:from dataclasses import dataclass, field
autofit/methods/bayesian_exchange_mc.py:51:from dataclasses import dataclass

exec
/bin/zsh -lc 'rg -n "FWHM_MAX_ORDINARY_EV|PROPOSAL_FWHM_MAX|detected_peak_|_unphysical_width_flags|broad_justification" autofit/engine.py autofit/candidates.py tests/autofit/test_preseed_dominants.py tests/autofit/test_stage2_completeness.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
autofit/candidates.py:73:# 2.4 eV (just above FWHM_MAX_ORDINARY_EV = 2.0, the engine's ordinary-
autofit/candidates.py:464:            role=f"detected_peak_{i}",
tests/autofit/test_stage2_completeness.py:301:    flags = eng._unphysical_width_flags([fat], m)
tests/autofit/test_stage2_completeness.py:306:    assert eng._unphysical_width_flags([thin], m) == []
tests/autofit/test_stage2_completeness.py:317:    slot = ComponentSlot(role="detected_peak_0", region="unassigned",
tests/autofit/test_stage2_completeness.py:324:        return FittedComponent(slot_role="detected_peak_0", position=200.0,
tests/autofit/test_stage2_completeness.py:327:    assert eng._unphysical_width_flags([comp(4.0)], m), "4.0 ≥ 0.7×5.0"
tests/autofit/test_stage2_completeness.py:328:    assert eng._unphysical_width_flags([comp(3.0)], m) == []
tests/autofit/test_stage2_completeness.py:377:    flags = eng._unphysical_width_flags([fat], m)   # eff = 1.7×1.25 = 2.13
tests/autofit/test_stage2_completeness.py:382:    assert eng._unphysical_width_flags([ok], m) == []   # eff = 1.65
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
autofit/engine.py:832:        if c.slot_role.startswith("detected_peak_"):
autofit/engine.py:845:        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
autofit/engine.py:847:                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
autofit/engine.py:1867:                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
autofit/engine.py:1907:            fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2068:                                  PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX))
autofit/engine.py:2116:        fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2318:            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
autofit/engine.py:2457:            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
autofit/engine.py:2633:                fwhm_clip=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2830:                unphysical_widths=_unphysical_width_flags(primary.components, model),

exec
/bin/zsh -lc 'git diff --name-only ad7e668''^ ad7e668 && git diff --stat ad7e668''^ ad7e668' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-O4lHjTXq' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-9lkk1Z5i' (errno=Operation not permitted)
autofit/grammar.py
tests/autofit/test_broad_justification.py
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VvWKKO2e' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Q79vhzby' (errno=Operation not permitted)
 autofit/grammar.py                        |  33 +++++----
 tests/autofit/test_broad_justification.py | 113 +++++++++++++++++++++++++++++-
 2 files changed, 130 insertions(+), 16 deletions(-)

2026-07-20T18:58:01.742470Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The constant claim is source-exact: `PROPOSAL_FWHM_MAX` is assigned directly from `FWHM_MAX_ORDINARY_EV`. Detection slots are built as pseudo-Voigt slots, and those hit the detection-family branch before the generic broad-slot exemption branch.
exec
/bin/zsh -lc "nl -ba tests/autofit/test_stage2_completeness.py | sed -n '312,330p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   312	    papering-over signature in transferable units.  Below that: clean."""
   313	    from autofit.grammar import (BackgroundType, CandidateModel,
   314	                                 ComponentSlot, LineShape)
   315	    from autofit.engine import FittedComponent
   316	
   317	    slot = ComponentSlot(role="detected_peak_0", region="unassigned",
   318	                         phase_id="unassigned", be_window=(199.0, 201.0),
   319	                         line_shape=LineShape.PSEUDO_VOIGT,
   320	                         fwhm_range=(0.5, 5.0))
   321	    m = CandidateModel(name="M", background=BackgroundType.LINEAR,
   322	                       slots=(slot,))
   323	    def comp(w):
   324	        return FittedComponent(slot_role="detected_peak_0", position=200.0,
   325	                               fwhm=w, amplitude=1e3, shape_params={},
   326	                               line_shape=LineShape.PSEUDO_VOIGT)
   327	    assert eng._unphysical_width_flags([comp(4.0)], m), "4.0 ≥ 0.7×5.0"
   328	    assert eng._unphysical_width_flags([comp(3.0)], m) == []
   329	
   330	

exec
/bin/zsh -lc "nl -ba tests/autofit/test_preseed_dominants.py | sed -n '228,246p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   228	    ordinary physical FWHM ceiling as their upper bound — not the old
   229	    looser 3.0 that let residual proposals grow to fat widths."""
   230	    spec = eng.PreseedSpec(role="preseed_dominant_0", center_init=279.0,
   231	                           fwhm_init=1.0, amplitude_net=1e4, fraction_of_max=1.0,
   232	                           local_snr=100.0)
   233	    from autofit.grammar import CandidateModel, BackgroundType
   234	    base = CandidateModel(name="B", background=BackgroundType.SHIRLEY, slots=())
   235	    seeded = eng._preseed_augmented(base, [spec])
   236	    assert seeded.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
   237	
   238	    pspec = eng.ProposalSpec(role="proposed_peak_0", detection_windows=[],
   239	                             detection_energy=1.0, detection_ratio=9.0,
   240	                             center_init=281.0, fwhm_init=1.0, amplitude_init=5e3,
   241	                             line_shape=eng.PROPOSED_PEAK_SHAPE)
   242	    aug = eng._augmented_candidate(base, pspec)
   243	    assert aug.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
   244	
   245	
   246	def test_wide_proposal_capped_and_flagged():

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import ast, pathlib\\nfor path in pathlib.Path(\"autofit\").rglob(\"*.py\"):\\n    tree=ast.parse(path.read_text())\\n    for node in ast.walk(tree):\\n        if isinstance(node, ast.Call):\\n            f=node.func\\n            name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)\\n            if name in {\"ComponentSlot\", \"replace\"}:\\n                print(f\"{path}:{node.lineno}:{name}\")'" in /Users/skyefortier/xps-verify
 succeeded in 175ms:
autofit/grammar.py:616:replace
autofit/grammar.py:469:replace
autofit/grammar.py:568:replace
autofit/engine.py:2110:ComponentSlot
autofit/engine.py:1901:ComponentSlot
autofit/engine.py:2446:replace
autofit/candidates.py:463:ComponentSlot
autofit/regions/cl2p.py:143:ComponentSlot
autofit/regions/cl2p.py:166:ComponentSlot
autofit/regions/cl2p.py:154:ComponentSlot
autofit/regions/c1s.py:309:ComponentSlot
autofit/regions/b1s.py:92:ComponentSlot
autofit/regions/n1s.py:76:ComponentSlot
autofit/regions/n1s.py:82:ComponentSlot
autofit/regions/u4f.py:197:ComponentSlot

2026-07-20T18:58:11.264469Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc 'ls autofit/regions && rg -n "register_region|REGION =|BackgroundType" autofit/regions' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
__init__.py
__pycache__
b1s.py
c1s.py
cl2p.py
n1s.py
u4f.py
autofit/regions/u4f.py:38:    BackgroundType,
autofit/regions/u4f.py:44:from . import register_region
autofit/regions/u4f.py:46:REGION = "U 4f"
autofit/regions/u4f.py:110:U4F_BACKGROUND = BackgroundType.SMART
autofit/regions/u4f.py:293:register_region(U4fModule())
autofit/regions/n1s.py:24:    BackgroundType,
autofit/regions/n1s.py:30:from . import register_region
autofit/regions/n1s.py:32:REGION = "N 1s"
autofit/regions/n1s.py:40:N1S_BACKGROUND = BackgroundType.SMART
autofit/regions/n1s.py:97:register_region(N1sModule())
autofit/regions/b1s.py:24:    BackgroundType,
autofit/regions/b1s.py:30:from . import register_region
autofit/regions/b1s.py:32:REGION = "B 1s"
autofit/regions/b1s.py:53:B1S_BACKGROUND = BackgroundType.SMART_EXP
autofit/regions/b1s.py:120:register_region(B1sModule())
autofit/regions/c1s.py:28:    BackgroundType,
autofit/regions/c1s.py:35:from . import register_region
autofit/regions/c1s.py:37:REGION = "C 1s"
autofit/regions/c1s.py:366:                name=name, background=BackgroundType.SHIRLEY,
autofit/regions/c1s.py:451:register_region(C1sModule())
autofit/regions/__init__.py:46:def register_region(module: RegionModule) -> None:
autofit/regions/cl2p.py:39:    BackgroundType,
autofit/regions/cl2p.py:45:from . import register_region
autofit/regions/cl2p.py:47:REGION = "Cl 2p"
autofit/regions/cl2p.py:71:CL2P_BACKGROUND = BackgroundType.SMART_EXP
autofit/regions/cl2p.py:199:register_region(Cl2pModule())

2026-07-20T18:58:25.708304Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
There is no second production copy-and-modify site for `ComponentSlot`: the AST scan found `_retag_slot` as the only `replace` call that can act on a slot, while engine/candidates/regions construct new slots from inputs. I’m doing one last same-background C 1s composition because C 1s cannot compose with Cl 2p due background mismatch.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import Phase,MaterialClass,resolve\\nphases=[Phase(id=\"Cgraph\", material_class=MaterialClass.CONDUCTOR, material=\"graphite\", regions=(\"C 1s\",)), Phase(id=\"Cpoly\", material_class=MaterialClass.INSULATOR, material=\"polymer\", regions=(\"C 1s\",))]\\ng=resolve(phases, [(\"C 1s\",\"Cgraph\"),(\"C 1s\",\"Cpoly\")])\\nbad=[]; seen=0; samples=[]\\nfor c in g.candidates:\\n    for s in c.slots:\\n        if s.broad_justification is not None:\\n            seen += 1; samples.append((c.name, s.role, s.fwhm_range))\\n# Compare every composed justified role with its own field present; no declared source broad slot should become None.\\nprint(\"candidates\", len(g.candidates), \"justified_slots_seen\", seen, \"sample\", samples[:8])\\nprint(\"lost\", bad)'" in /Users/skyefortier/xps-verify
 succeeded in 139ms:
candidates 841 justified_slots_seen 1450 sample [('A0_graphite_asym_satellite+A0_graphite_asym_satellite', 'C1sCgraph__satellite_pi', (1.0, 5.5)), ('A0_graphite_asym_satellite+A0_graphite_asym_satellite', 'C1sCpoly__satellite_pi', (1.0, 5.5)), ('A0_graphite_asym_satellite+A1_graphite_asym_sat_plus_CO', 'C1sCgraph__satellite_pi', (1.0, 5.5)), ('A0_graphite_asym_satellite+A1_graphite_asym_sat_plus_CO', 'C1sCpoly__satellite_pi', (1.0, 5.5)), ('A0_graphite_asym_satellite+A2_graphite_asym_sat_plus_CO_C=O', 'C1sCgraph__satellite_pi', (1.0, 5.5)), ('A0_graphite_asym_satellite+A2_graphite_asym_sat_plus_CO_C=O', 'C1sCpoly__satellite_pi', (1.0, 5.5)), ('A0_graphite_asym_satellite+A3_graphite_asym_sat_plus_CO_C=O_OC=O', 'C1sCgraph__satellite_pi', (1.0, 5.5)), ('A0_graphite_asym_satellite+A3_graphite_asym_sat_plus_CO_C=O_OC=O', 'C1sCpoly__satellite_pi', (1.0, 5.5))]
lost []

2026-07-20T18:58:35.200495Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
1. No BLOCKER/MAJOR/MINOR findings.

The fix closes the original finding. [`autofit/grammar.py:616`](/Users/skyefortier/xps-verify/autofit/grammar.py:616) now uses `replace(s, role=..., linked_to=..., fwhm_linked_to=...)`, and my direct repro of `resolve([UCl4(U 4f), BN(N 1s)], ["U 4f", "N 1s"])` shows `U4f__main_u4f72`, `U4f__main_u4f52`, `N1s__main_n1s`, and checked U 4f satellite roles all retain non-`None` `broad_justification`.

I found no second production copy-and-modify site for `ComponentSlot`. The remaining production `ComponentSlot(` sites are fresh construction in region modules, [`autofit/candidates.py:463`](/Users/skyefortier/xps-verify/autofit/candidates.py:463), [`autofit/engine.py:1901`](/Users/skyefortier/xps-verify/autofit/engine.py:1901), and [`autofit/engine.py:2110`](/Users/skyefortier/xps-verify/autofit/engine.py:2110). Additional composed probes for B 1s + Cl 2p, phase-qualified U 4f + N 1s + N 1s, and phase-qualified C 1s + C 1s preserved declared justifications.

The structural guard would have caught the original bug: exercising its sentinel logic against the current body produced no mismatches, while the old manual reconstruction from `5070662` lost `broad_justification`.

The other slot-construction claims check out by source: [`autofit/engine.py:120`](/Users/skyefortier/xps-verify/autofit/engine.py:120) assigns `PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV` exactly, and preseed/proposal slots use that bound at [`autofit/engine.py:1907`](/Users/skyefortier/xps-verify/autofit/engine.py:1907) and [`autofit/engine.py:2116`](/Users/skyefortier/xps-verify/autofit/engine.py:2116). Detection slots are built pseudo-Voigt at [`autofit/candidates.py:468`](/Users/skyefortier/xps-verify/autofit/candidates.py:468) and hit the detected-prefix branch before the generic vouched-slot exemption at [`autofit/engine.py:832`](/Users/skyefortier/xps-verify/autofit/engine.py:832). Commit scope is exactly `autofit/grammar.py` and `tests/autofit/test_broad_justification.py`.

I could not run pytest in this sandbox because system Python lacks `pytest` and `lmfit`; I used direct `python3` probes for the grammar-level reproductions.

VERDICT: GO
tokens used
82,203
1. No BLOCKER/MAJOR/MINOR findings.

The fix closes the original finding. [`autofit/grammar.py:616`](/Users/skyefortier/xps-verify/autofit/grammar.py:616) now uses `replace(s, role=..., linked_to=..., fwhm_linked_to=...)`, and my direct repro of `resolve([UCl4(U 4f), BN(N 1s)], ["U 4f", "N 1s"])` shows `U4f__main_u4f72`, `U4f__main_u4f52`, `N1s__main_n1s`, and checked U 4f satellite roles all retain non-`None` `broad_justification`.

I found no second production copy-and-modify site for `ComponentSlot`. The remaining production `ComponentSlot(` sites are fresh construction in region modules, [`autofit/candidates.py:463`](/Users/skyefortier/xps-verify/autofit/candidates.py:463), [`autofit/engine.py:1901`](/Users/skyefortier/xps-verify/autofit/engine.py:1901), and [`autofit/engine.py:2110`](/Users/skyefortier/xps-verify/autofit/engine.py:2110). Additional composed probes for B 1s + Cl 2p, phase-qualified U 4f + N 1s + N 1s, and phase-qualified C 1s + C 1s preserved declared justifications.

The structural guard would have caught the original bug: exercising its sentinel logic against the current body produced no mismatches, while the old manual reconstruction from `5070662` lost `broad_justification`.

The other slot-construction claims check out by source: [`autofit/engine.py:120`](/Users/skyefortier/xps-verify/autofit/engine.py:120) assigns `PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV` exactly, and preseed/proposal slots use that bound at [`autofit/engine.py:1907`](/Users/skyefortier/xps-verify/autofit/engine.py:1907) and [`autofit/engine.py:2116`](/Users/skyefortier/xps-verify/autofit/engine.py:2116). Detection slots are built pseudo-Voigt at [`autofit/candidates.py:468`](/Users/skyefortier/xps-verify/autofit/candidates.py:468) and hit the detected-prefix branch before the generic vouched-slot exemption at [`autofit/engine.py:832`](/Users/skyefortier/xps-verify/autofit/engine.py:832). Commit scope is exactly `autofit/grammar.py` and `tests/autofit/test_broad_justification.py`.

I could not run pytest in this sandbox because system Python lacks `pytest` and `lmfit`; I used direct `python3` probes for the grammar-level reproductions.

VERDICT: GO
