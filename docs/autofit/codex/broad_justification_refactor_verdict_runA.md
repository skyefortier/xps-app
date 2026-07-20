2026-07-20T17:49:24.126570Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 86 column 5
OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f80a5-9c39-7a91-863c-4f6d22949268
--------
user
You are an adversarial reviewer for a refactor commit in this repo (XPS
peak-fitting web app). Review commit 5070662 ("refactor(autofit): decouple
broad_justification from fwhm_range's magnitude") on branch
feature-autofit-stage2 -- `git show 5070662` gives the full diff. This
commit exists because BOTH Codex reviews of an earlier commit (77bf3a8,
the MIXED material class feature) independently caught the same MAJOR
finding, and the human maintainer (not Claude Code) diagnosed the root
cause and specified this exact fix. Your job is to verify the diagnosis
and the fix are both actually correct, not to re-litigate whether a fix
was needed.

THE DIAGNOSIS (read this before reviewing the diff): ``ComponentSlot.
fwhm_range``'s upper bound used to carry two independent meanings at once:
(1) "the optimizer may search up to here" (a bound), and (2) "this region
module vouches this width is real physics, not an optimizer papering over
a missed feature" (a semantic claim consumed by ``autofit/engine.py``'s
``_unphysical_width_flags``, which decides whether a fat fitted component
gets reported as suspicious). The old code inferred (2) from (1) via
``declared_hi > FWHM_MAX_ORDINARY_EV`` (2.0 eV) — so ANY slot whose bound
happened to exceed 2.0 eV was automatically treated as vouched-for,
regardless of why the bound was wide. The MIXED unit widened C1s
contamination's bound to 15.0 eV purely for differential-charging
numerical headroom and thereby silently ALSO granted it the vouching
exemption — meaning a MIXED contaminant fitting unrealistically wide
(6-10 eV, plausibly absorbing a neighbor) sailed through unflagged.

THE FIX: ``ComponentSlot`` gains ``broad_justification: Optional[str] =
None`` (autofit/grammar.py). ``_unphysical_width_flags`` now keys
exemption off ``slot.broad_justification is not None`` — never off
``fwhm_range``'s magnitude. Every slot that was exempt under the OLD
numeric rule needs this field set for the refactor to be behavior-neutral;
every slot that was NOT exempt must NOT get it, or the refactor silently
loosens the safety net instead of merely relocating it.

THE CLAIMED EXHAUSTIVE LIST (verify this yourself — do not trust it):
- C1s satellite_pi (FWHM_RANGE_SATELLITE, 1.0-5.5 eV): genuine mechanism
  claimed (pi->pi* shake-up, multi-electron excitation).
- B1s all 3 mains (B1S_FWHM_RANGE, 1.2-2.5 eV): claimed HONESTLY
  empirical-only, no mechanism cited.
- Cl2p main_cl2p32 + the SHARED-width main_cl2p12 variant (CL2P_FWHM_RANGE,
  1.2-2.2 eV): claimed empirical-only.
- Cl2p the FREE-WIDTH main_cl2p12 variant (CL2P_12_FWHM_RANGE, up to
  3.0 eV, via fwhm_excess_range): genuine mechanism claimed (2p1/2
  Coster-Kronig broadening, adjudication #7), but the SPECIFIC 0.8 eV
  excess bound itself is disclosed as still-unverified.
- N1s main_n1s in both shape variants (N1S_FWHM_RANGE, 0.7-2.5 eV):
  claimed empirical-only, single labeled exemplar.
- U4f mains (U4F_MAIN_FWHM_RANGE, 1.5-3.5 eV): genuine VERIFIED mechanism
  claimed (U(IV) 5f2 unresolved multiplet manifold, Ilton & Bagus 2011).
- U4f all satellite variants (U4F_SAT_FWHM_RANGE, 1.5-4.5 eV): the
  satellite's EXISTENCE is real physics, but the specific width bound is
  disclosed as empirical-only.
- C1s contamination slots under MaterialClass.MIXED (widened to 0.8-15.0
  eV in the earlier 77bf3a8 commit): deliberately NOT given
  broad_justification — this is the whole point of the fix.
- Every other slot in every region module (C1s graphitic main, aromatic-
  polymer main, plain contamination under non-MIXED classes; any slot
  anywhere with a declared ceiling <= 2.0 eV): must NOT get
  broad_justification — they were never exempt.

ADVERSARIAL QUESTIONS -- ATTACK THESE SPECIFICALLY:

(a) SILENT TIGHTENING (the mirror-image regression). Re-derive the
    exhaustive exemption list yourself by reading every region module's
    build_candidates() in autofit/regions/*.py from scratch — grep every
    ComponentSlot(...) construction and every fwhm_range constant, don't
    just check the list above. Is there ANY slot whose declared_hi
    EXCEEDED 2.0 eV under the OLD code (so it was exempt) that did NOT
    receive broad_justification in this commit? That slot would now be
    flagged as unphysical when it previously wasn't — a real behavior
    change this commit claims NOT to make. Pay special attention to
    linked/shared-width slots (e.g. Cl2p's shared vs free-width
    main_cl2p12, U4f's satellite pair-linked variants sat_52/sat_52_freesep)
    where the same role appears in multiple CandidateModel variants with
    potentially different fwhm_range values — every variant needs its own
    check.

(b) RELOCATED OVERLOAD (the honesty check). For each slot that DID
    receive broad_justification, read its actual justification string
    (git show 5070662, or read the region module directly) and judge: is
    it an honest description of what's actually cited elsewhere in that
    module (the module's own top-of-file docstring and inline comments),
    or does it overclaim a physical mechanism the module doesn't actually
    establish? Specifically interrogate whether B1s's, N1s's, Cl2p's
    shared-width variant's, and U4f satellites' "empirical-only, no
    mechanism cited" framing is ACCURATE — i.e. does the region module
    genuinely lack a cited broadening mechanism for these, or did the
    commit understate an existing citation? And conversely, for the
    slots claiming a genuine mechanism (C1s satellite, Cl2p free-width,
    U4f mains) — is the citation/mechanism actually present and correctly
    characterized in that module's own comments, not invented for this
    commit?

(c) THE FIX'S ACTUAL EFFECT. Independently verify (read the code, or run
    Python if your sandbox allows importing autofit) that a C1s
    contamination slot under MaterialClass.MIXED has fwhm_range=(0.8,
    15.0) and broad_justification=None, and that
    autofit.engine._unphysical_width_flags flags a component fit at, say,
    8.0 eV in that slot. This is the entire point of the refactor —
    confirm it actually holds in the current code, not just in the
    commit message's narrative.

(d) SCOPE. Confirm the diff is contained to autofit/grammar.py,
    autofit/engine.py, the 5 region modules, and the 2 test files. No
    diff in app.py, templates/index.html, fitting.py, or autofit/methods/
    *.py.

(e) TEST DISCRIMINATION. tests/autofit/test_broad_justification.py's
    EXEMPTION_FIXTURE is the safety net for the "byte-identical" claim —
    for a few entries of your choosing, verify independently that the
    listed (phase, region, candidate_name, role, exempt) tuple is actually
    correct by reading the region module yourself, not by trusting the
    fixture. Also check test_preseed_dominants.py's updated
    test_unphysical_width_flags_helper: does the updated version still
    test something meaningful, or did the fix just paper over the failure
    by adding whatever kwarg made it pass?

Deliver: a numbered findings list (severity BLOCKER/MAJOR/MINOR, each with
file/line and a concrete failure scenario), then a final line exactly
"VERDICT: GO" or "VERDICT: NO-GO".

codex
I’ll review this as a commit review, starting from the actual diff and then re-deriving the exemption set from the region modules instead of trusting the fixture. Since the workspace is read-only, I’ll only run inspection and test/import commands that don’t write files.
exec
/bin/zsh -lc "rg -n \"ComponentSlot\\(|fwhm_range|broad_justification|FWHM_MAX_ORDINARY_EV|_unphysical_width_flags\" autofit tests" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'git show --stat --oneline --name-only 5070662' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-tXhrn0mf' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-BxWZJF5x' (errno=Operation not permitted)
5070662 refactor(autofit): decouple broad_justification from fwhm_range's magnitude
autofit/engine.py
autofit/grammar.py
autofit/regions/b1s.py
autofit/regions/c1s.py
autofit/regions/cl2p.py
autofit/regions/n1s.py
autofit/regions/u4f.py
tests/autofit/test_broad_justification.py
tests/autofit/test_preseed_dominants.py

 succeeded in 0ms:
autofit/candidates.py:73:# 2.4 eV (just above FWHM_MAX_ORDINARY_EV = 2.0, the engine's ordinary-
autofit/candidates.py:463:        slots.append(ComponentSlot(
autofit/candidates.py:469:            fwhm_range=(lo_w, hi_w),
autofit/engine.py:116:FWHM_MAX_ORDINARY_EV = 2.0
autofit/engine.py:120:PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV
autofit/engine.py:355:    # DS+G: fitalg convention — slot.fwhm_range bounds m_gauss (the Gaussian
autofit/engine.py:362:# Which parameter carries the slot's fwhm_range for each shape.
autofit/engine.py:372:    flo, fhi = slot.fwhm_range
autofit/engine.py:517:        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
autofit/engine.py:551:        fmid = 0.5 * (slot.fwhm_range[0] + slot.fwhm_range[1])
autofit/engine.py:753:def _unphysical_width_flags(
autofit/engine.py:757:    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.
autofit/engine.py:761:    only if it carries an explicit ``ComponentSlot.broad_justification``
autofit/engine.py:771:    ``broad_justification`` is INDEPENDENT of ``fwhm_range``'s own magnitude
autofit/engine.py:774:    FWHM_MAX_ORDINARY_EV`` alone, which conflated "the optimizer may search
autofit/engine.py:790:        declared_lo, declared_hi = slot.fwhm_range
autofit/engine.py:791:        vouched = slot.broad_justification is not None
autofit/engine.py:803:            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
autofit/engine.py:806:                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
autofit/engine.py:817:            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
autofit/engine.py:820:                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
autofit/engine.py:828:        # signature in transferable units. Unaffected by broad_justification
autofit/engine.py:845:        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
autofit/engine.py:847:                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
autofit/engine.py:1056:                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
autofit/engine.py:1901:        ComponentSlot(
autofit/engine.py:1907:            fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:1949:    mids = [0.5 * (s.fwhm_range[0] + s.fwhm_range[1])
autofit/engine.py:2110:    proposed = ComponentSlot(
autofit/engine.py:2116:        fwhm_range=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/engine.py:2318:            unphysical_widths=_unphysical_width_flags(primary.components, aug_model),
autofit/engine.py:2457:            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
autofit/engine.py:2830:                unphysical_widths=_unphysical_width_flags(primary.components, model),
autofit/grammar.py:127:    fwhm_range: tuple[float, float]
autofit/grammar.py:166:    # Explicit semantic claim, independent of fwhm_range's magnitude
autofit/grammar.py:172:    # autofit.engine._unphysical_width_flags must not exempt it, REGARDLESS
autofit/grammar.py:173:    # of how wide fwhm_range happens to be. Before this field existed,
autofit/grammar.py:174:    # fwhm_range's upper bound alone served double duty as both the
autofit/grammar.py:176:    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
autofit/grammar.py:181:    broad_justification: Optional[str] = None
autofit/grammar.py:187:            and self.fwhm_range[0] <= fwhm <= self.fwhm_range[1]
autofit/grammar.py:602:    return ComponentSlot(
autofit/grammar.py:608:        fwhm_range=s.fwhm_range,
autofit/regions/b1s.py:75:            {"constant": "fwhm_range_ev", "value": list(B1S_FWHM_RANGE),
autofit/regions/b1s.py:92:            return ComponentSlot(
autofit/regions/b1s.py:95:                fwhm_range=B1S_FWHM_RANGE,
autofit/regions/b1s.py:96:                broad_justification=(
autofit/regions/n1s.py:55:            {"constant": "fwhm_range_ev", "value": list(N1S_FWHM_RANGE),
autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
autofit/regions/n1s.py:79:            fwhm_range=N1S_FWHM_RANGE,
autofit/regions/n1s.py:80:            broad_justification=_justification,
autofit/regions/n1s.py:82:        ag_main = ComponentSlot(
autofit/regions/n1s.py:85:            fwhm_range=N1S_FWHM_RANGE,
autofit/regions/n1s.py:87:            broad_justification=_justification,
autofit/regions/cl2p.py:91:            {"constant": "fwhm_range_ev", "value": list(CL2P_FWHM_RANGE),
autofit/regions/cl2p.py:143:            return ComponentSlot(
autofit/regions/cl2p.py:146:                fwhm_range=CL2P_FWHM_RANGE,
autofit/regions/cl2p.py:147:                broad_justification=_empirical_justification,
autofit/regions/cl2p.py:154:                return ComponentSlot(
autofit/regions/cl2p.py:157:                    fwhm_range=CL2P_12_FWHM_RANGE,
autofit/regions/cl2p.py:164:                    broad_justification=_coster_kronig_justification,
autofit/regions/cl2p.py:166:            return ComponentSlot(
autofit/regions/cl2p.py:169:                fwhm_range=CL2P_FWHM_RANGE,
autofit/regions/cl2p.py:175:                broad_justification=_empirical_justification,
autofit/regions/u4f.py:154:            {"constant": "main_fwhm_range_ev", "value": list(U4F_MAIN_FWHM_RANGE),
autofit/regions/u4f.py:196:        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
autofit/regions/u4f.py:197:            return ComponentSlot(
autofit/regions/u4f.py:199:                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
autofit/regions/u4f.py:222:            broad_justification=_main_justification,
autofit/regions/u4f.py:231:            broad_justification=_main_justification,
autofit/regions/u4f.py:239:            broad_justification=_sat_justification,
autofit/regions/u4f.py:249:            broad_justification=_sat_justification,
autofit/regions/u4f.py:260:            broad_justification=_sat_justification,
autofit/regions/u4f.py:270:            broad_justification=_sat_justification,
autofit/regions/u4f.py:277:            broad_justification=_sat_justification,
tests/autofit/stress_cases.py:108:    return ComponentSlot(role=role, region=REGION, phase_id=PHASE,
tests/autofit/stress_cases.py:110:                         fwhm_range=fwhm, **kw)
autofit/regions/c1s.py:11:   the slot's fwhm_range.
autofit/regions/c1s.py:102:# of fwhm_range, so an infinite upper bound would seed an infinite
autofit/regions/c1s.py:125:def _contamination_fwhm_range(material_class: MaterialClass) -> tuple[float, float]:
autofit/regions/c1s.py:273:                       "guess is the fwhm_range midpoint); this reuses "
autofit/regions/c1s.py:306:        contam_fwhm = _contamination_fwhm_range(phase.material_class)
autofit/regions/c1s.py:308:        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
autofit/regions/c1s.py:309:            return ComponentSlot(
autofit/regions/c1s.py:311:                be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
autofit/regions/c1s.py:337:            broad_justification=(
autofit/regions/c1s.py:347:                   fwhm_range=None) -> ComponentSlot:
autofit/regions/c1s.py:357:                        fwhm_range if fwhm_range is not None else contam_fwhm, **kw)
tests/autofit/test_preseed_dominants.py:154:        assert p["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6, \
tests/autofit/test_preseed_dominants.py:160:def test_unphysical_width_flags_helper():
tests/autofit/test_preseed_dominants.py:163:    ``broad_justification``, e.g. a satellite) are NOT.
tests/autofit/test_preseed_dominants.py:165:    2026-07-20 (Unit A, broad_justification refactor): the exemption used
tests/autofit/test_preseed_dominants.py:166:    to be inferred from ``fwhm_range``'s own magnitude (declared max >
tests/autofit/test_preseed_dominants.py:172:    Updated to set broad_justification explicitly, matching how every real
tests/autofit/test_preseed_dominants.py:178:    def slot(role, lo, hi, broad_justification=None):
tests/autofit/test_preseed_dominants.py:179:        return ComponentSlot(role=role, region="r", phase_id="p",
tests/autofit/test_preseed_dominants.py:181:                             fwhm_range=(lo, hi),
tests/autofit/test_preseed_dominants.py:182:                             broad_justification=broad_justification)
tests/autofit/test_preseed_dominants.py:191:             broad_justification="synthetic: pi->pi* shake-up, physically broad"),
tests/autofit/test_preseed_dominants.py:193:    flags = eng._unphysical_width_flags(
tests/autofit/test_preseed_dominants.py:203:    assert eng._unphysical_width_flags([comp("contamination_CO", 1.5)], m) == []
tests/autofit/test_preseed_dominants.py:206:def test_unphysical_width_flags_wide_range_alone_no_longer_exempts():
tests/autofit/test_preseed_dominants.py:208:    declared fwhm_range but NO broad_justification must be flagged when it
tests/autofit/test_preseed_dominants.py:216:    slot = ComponentSlot(role="wide_unvouched", region="r", phase_id="p",
tests/autofit/test_preseed_dominants.py:218:                         fwhm_range=(0.8, 15.0))
tests/autofit/test_preseed_dominants.py:222:    flags = eng._unphysical_width_flags([comp], m)
tests/autofit/test_preseed_dominants.py:236:    assert seeded.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
tests/autofit/test_preseed_dominants.py:243:    assert aug.slots[-1].fwhm_range[1] == eng.FWHM_MAX_ORDINARY_EV
tests/autofit/test_preseed_dominants.py:269:    assert p["fitted_fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6   # NOT 3 eV
tests/autofit/test_preseed_dominants.py:278:            assert pk["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6
tests/autofit/test_preseed_dominants.py:293:    slot = ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
tests/autofit/test_preseed_dominants.py:295:                         fwhm_range=(0.5, 2.0))
tests/autofit/test_preseed_dominants.py:397:        return ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
tests/autofit/test_preseed_dominants.py:399:                             fwhm_range=(0.5, 3.0))
autofit/methods/sparse_map.py:19:  each slot's fwhm_range.  Gaussian atoms are a documented simplification —
autofit/methods/sparse_map.py:85:            wlo, whi = s.fwhm_range
tests/autofit/test_region_provenance_honesty.py:153:def test_u4f_satellite_fwhm_range_has_provenance_entry():
tests/autofit/test_resolver.py:107:        main = ComponentSlot(
tests/autofit/test_resolver.py:110:            fwhm_range=(0.5, 2.0),
tests/autofit/test_resolver.py:112:        doublet = ComponentSlot(
tests/autofit/test_resolver.py:115:            fwhm_range=(0.5, 2.0),
tests/autofit/test_stage2_completeness.py:293:    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
tests/autofit/test_stage2_completeness.py:295:                         fwhm_range=(0.5, 2.0))
tests/autofit/test_stage2_completeness.py:301:    flags = eng._unphysical_width_flags([fat], m)
tests/autofit/test_stage2_completeness.py:306:    assert eng._unphysical_width_flags([thin], m) == []
tests/autofit/test_stage2_completeness.py:317:    slot = ComponentSlot(role="detected_peak_0", region="unassigned",
tests/autofit/test_stage2_completeness.py:320:                         fwhm_range=(0.5, 5.0))
tests/autofit/test_stage2_completeness.py:327:    assert eng._unphysical_width_flags([comp(4.0)], m), "4.0 ≥ 0.7×5.0"
tests/autofit/test_stage2_completeness.py:328:    assert eng._unphysical_width_flags([comp(3.0)], m) == []
tests/autofit/test_stage2_completeness.py:369:    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
tests/autofit/test_stage2_completeness.py:371:                         fwhm_range=(0.5, 2.0))
tests/autofit/test_stage2_completeness.py:377:    flags = eng._unphysical_width_flags([fat], m)   # eff = 1.7×1.25 = 2.13
tests/autofit/test_stage2_completeness.py:382:    assert eng._unphysical_width_flags([ok], m) == []   # eff = 1.65
tests/autofit/test_fit_full_window_option.py:41:    return ComponentSlot(role=role, region=region, phase_id="p",
tests/autofit/test_fit_full_window_option.py:43:                         fwhm_range=(0.6, 2.2), **kw)
tests/autofit/test_criteria.py:23:    return ComponentSlot(role=role, region="T", phase_id="t",
tests/autofit/test_criteria.py:26:                         fwhm_range=(0.5, 3.0))
tests/autofit/test_sparse_map.py:28:    return ComponentSlot(role=role, region="T", phase_id="t",
tests/autofit/test_sparse_map.py:30:                         fwhm_range=(0.6, 2.2))
tests/autofit/test_broad_justification.py:1:"""Unit A (2026-07-20): decouples two meanings that ``fwhm_range``'s upper
tests/autofit/test_broad_justification.py:10:``autofit/engine.py``'s ``_unphysical_width_flags`` used to infer (2) from
tests/autofit/test_broad_justification.py:11:(1) via a bare numeric test (``declared_hi > FWHM_MAX_ORDINARY_EV``). The
tests/autofit/test_broad_justification.py:20:The fix: ``ComponentSlot.broad_justification`` makes meaning (2) an
tests/autofit/test_broad_justification.py:21:explicit, independent field. ``_unphysical_width_flags`` keys its
tests/autofit/test_broad_justification.py:22:exemption off ``broad_justification is not None``, never off the bound's
tests/autofit/test_broad_justification.py:33:from autofit.engine import FittedComponent, _unphysical_width_flags
tests/autofit/test_broad_justification.py:37:# (declared_hi > FWHM_MAX_ORDINARY_EV == 2.0 eV, the pre-refactor rule),
tests/autofit/test_broad_justification.py:89:def test_exemption_fixture_matches_broad_justification(
tests/autofit/test_broad_justification.py:91:    """Each currently-exempt slot must carry a real broad_justification;
tests/autofit/test_broad_justification.py:97:        assert slot.broad_justification is not None, (
tests/autofit/test_broad_justification.py:99:            f"under the old numeric rule (fwhm_range={slot.fwhm_range}) but "
tests/autofit/test_broad_justification.py:102:        assert slot.fwhm_range[1] > 2.0, (
tests/autofit/test_broad_justification.py:108:        assert slot.broad_justification is None, (
tests/autofit/test_broad_justification.py:110:            f"broad under the old numeric rule (fwhm_range={slot.fwhm_range}) "
tests/autofit/test_broad_justification.py:122:    """Minimal stand-in for CandidateModel -- _unphysical_width_flags only
tests/autofit/test_broad_justification.py:132:    """The actual OUTPUT of _unphysical_width_flags for a component fitted
tests/autofit/test_broad_justification.py:140:    fwhm_at_ceiling = slot.fwhm_range[1] if exempt else 2.0
tests/autofit/test_broad_justification.py:142:    flags = _unphysical_width_flags([comp], cand)
tests/autofit/test_broad_justification.py:158:    """THE FIX, encoded directly: a slot with a wide fwhm_range (would have
tests/autofit/test_broad_justification.py:159:    been auto-exempt under the old numeric rule) but broad_justification
tests/autofit/test_broad_justification.py:165:    wide_no_justification = ComponentSlot(
tests/autofit/test_broad_justification.py:168:        fwhm_range=(0.8, 15.0), broad_justification=None,
tests/autofit/test_broad_justification.py:173:    flags = _unphysical_width_flags([comp], model)
tests/autofit/test_broad_justification.py:175:        "a slot with a wide bound but NO broad_justification must still "
tests/autofit/test_broad_justification.py:182:    """Mirror case: an explicit broad_justification grants exemption even
tests/autofit/test_broad_justification.py:188:    narrow_but_justified = ComponentSlot(
tests/autofit/test_broad_justification.py:191:        fwhm_range=(0.5, 2.0), broad_justification="synthetic test justification",
tests/autofit/test_broad_justification.py:196:    flags = _unphysical_width_flags([comp], model)
tests/autofit/test_broad_justification.py:198:        "an explicit broad_justification must exempt a slot even when its "
tests/autofit/test_broad_justification.py:203:def test_component_slot_broad_justification_defaults_to_none():
tests/autofit/test_broad_justification.py:206:    s = ComponentSlot(role="r", region="Test", phase_id="s",
tests/autofit/test_broad_justification.py:208:                      fwhm_range=(0.5, 1.0))
tests/autofit/test_broad_justification.py:209:    assert s.broad_justification is None
tests/autofit/test_cl2p_freewidth.py:129:                    line_shape=LineShape.PSEUDO_VOIGT, fwhm_range=(0.6, 2.2))
tests/autofit/test_cl2p_freewidth.py:131:    return ComponentSlot(role=role, **defaults)
tests/autofit/test_bayesian_method.py:29:    return ComponentSlot(role=role, region="T", phase_id="t",
tests/autofit/test_bayesian_method.py:31:                         fwhm_range=(0.5, 2.5))
tests/autofit/test_c1s_mixed_material_class.py:61:            if s.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0]:
tests/autofit/test_c1s_mixed_material_class.py:69:    must build EXACTLY the pre-MIXED contamination fwhm_range -- byte
tests/autofit/test_c1s_mixed_material_class.py:75:        assert slot.fwhm_range == FWHM_RANGE_CONTAMINATION, (
tests/autofit/test_c1s_mixed_material_class.py:76:            f"{name}/{slot.role}: fwhm_range changed for non-MIXED "
tests/autofit/test_c1s_mixed_material_class.py:101:        assert slot.fwhm_range[0] == FWHM_RANGE_CONTAMINATION[0], (
tests/autofit/test_c1s_mixed_material_class.py:105:        assert slot.fwhm_range[1] > FWHM_RANGE_CONTAMINATION[1], (
tests/autofit/test_c1s_mixed_material_class.py:142:        return {(c.name, s.role): s.fwhm_range
tests/autofit/test_c1s_mixed_material_class.py:144:                if s.fwhm_range[0] != FWHM_RANGE_CONTAMINATION[0]}
tests/autofit/test_c1s_mixed_material_class.py:195:    actual_ceiling = slots[0][1].fwhm_range[1]
tests/autofit/test_c1s_mixed_material_class.py:202:# in autofit.engine._unphysical_width_flags, so a MIXED contaminant fitting
tests/autofit/test_c1s_mixed_material_class.py:205:# so the app must not vouch for it). Fixed by Unit A (broad_justification):
tests/autofit/test_c1s_mixed_material_class.py:214:    from autofit.engine import FittedComponent, _unphysical_width_flags
tests/autofit/test_c1s_mixed_material_class.py:219:    assert slot.broad_justification is None, (
tests/autofit/test_c1s_mixed_material_class.py:225:    flags = _unphysical_width_flags([comp], cand)
tests/autofit/test_c1s_mixed_material_class.py:239:    autofit.engine._unphysical_width_flags produces for the 8 eV scenario
tests/autofit/test_c1s_mixed_material_class.py:248:                                _unphysical_width_flags)
tests/autofit/test_c1s_mixed_material_class.py:268:    injected_flags = _unphysical_width_flags([fake_comp], report.model)
tests/autofit/test_engine_doublet.py:23:    p32 = ComponentSlot(
tests/autofit/test_engine_doublet.py:26:        fwhm_range=(0.6, 2.2),
tests/autofit/test_engine_doublet.py:28:    p12 = ComponentSlot(
tests/autofit/test_engine_doublet.py:31:        fwhm_range=(0.6, 2.2),
tests/autofit/test_engine_doublet.py:127:        return ComponentSlot(
tests/autofit/test_engine_doublet.py:130:            fwhm_range=(0.5, 3.0),

exec
/bin/zsh -lc 'git status --short --branch' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-T9VdpZtg' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-iTW5TTQ7' (errno=Operation not permitted)
## feature-autofit-stage2...origin/feature-autofit-stage2
 M templates/index.html
 M tests/autofit/test_c1s_mixed_material_class.py
 M tests/js/fp_material_mixed.test.js
?? "docs/autofit/test_data/7 - GTA-2-66 U-naph and COT.DATA"
?? "docs/autofit/test_data/8 GTA-2-46ii U-naph and XeF2, graphite 40%, powder, Cu, 0.4eV, 400 um.DATA"
?? docs/autofit/test_data/Ugly_Fe_2p.spec.json
?? docs/autofit/test_data/Ugly_Fe_2p_2.spec.json
?? docs/autofit/test_data/ds7_Skye_Test_fit_C1s.spec.json
?? docs/autofit/test_data/ds8_Skye_Test_fit_C1s.spec.json

codex
The top-level scope matches the claimed file set. I also see unrelated working-tree changes already present; I’ll ignore them unless they affect the reviewed commit. Next I’m reading the region modules and the tests around the new field so I can compare old numeric exemptions to explicit `broad_justification`.
exec
/bin/zsh -lc "nl -ba autofit/regions/b1s.py | sed -n '1,180p'" in /Users/skyefortier/xps-verify
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

exec
/bin/zsh -lc "nl -ba autofit/regions/c1s.py | sed -n '1,430p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	C 1s region module — the Stage-2 parity anchor (spec §3.1).
     3	
     4	Ported from fitalg's ``build_c1s_graphite_candidates`` (validated there on
     5	HOPG-like graphite and PET), with two changes for main:
     6	
     7	1. fitalg's asymmetric main used its then-``la_casaxps`` shape, which is
     8	   TODAY's ``ds_g`` (DS core ⊗ Gaussian; β = Lorentzian HWHM in eV).  The
     9	   port maps those slots to :attr:`LineShape.DS_G`, preserving the math —
    10	   fixed β at the C 1s core-hole lifetime, α capped, ``m_gauss`` carrying
    11	   the slot's fwhm_range.
    12	2. an ``AG*`` family with an ``asym-GL`` graphitic main is added.  The
    13	   expert reference fits in docs/autofit/test_data model graphitic carbon
    14	   as asym-GL (+ GL contaminants/satellite); the engine must be able to
    15	   EXPRESS the expert model for the parity gate.  asym-GL is an empirical
    16	   asymmetric envelope (no lit-derived parameterization) — flagged
    17	   UNVERIFIED-empirical below.
    18	
    19	Citations for constants are inline; everything without a citation is an
    20	UNVERIFIED tunable per spec §9.
    21	"""
    22	
    23	from __future__ import annotations
    24	
    25	from typing import Optional
    26	
    27	from ..grammar import (
    28	    BackgroundType,
    29	    CandidateModel,
    30	    ComponentSlot,
    31	    LineShape,
    32	    MaterialClass,
    33	    Phase,
    34	)
    35	from . import register_region
    36	
    37	REGION = "C 1s"
    38	
    39	# BE windows (eV, corrected frame). UNVERIFIED-calibration: the window
    40	# CENTERS are anchored on cited values — graphite C 1s 284.4 (Leiro,
    41	# 10.1016/S0368-2048(02)00284-0), adventitious C-C/C-H 284.8 and the
    42	# +1.5/+3.0/+4.0 oxidised-carbon shifts (Biesinger 2022, CONDITIONAL soft
    43	# priors per spec §9) — but the window WIDTHS are generous prototype bins
    44	# from fitalg with no primary source; they gate candidate admissibility and
    45	# must be sensitivity-tested before publication claims.
    46	C1S_WINDOWS: dict[str, tuple[float, float]] = {
    47	    "graphitic":   (284.0, 284.8),   # sp² graphitic C-C
    48	    "aliphatic":   (284.6, 285.4),   # adventitious C-C/C-H
    49	    "CO":          (285.8, 286.8),   # C-O / C-OH
    50	    "C=O":         (287.3, 288.3),
    51	    "OC=O":        (288.5, 289.6),
    52	    "shake_up_pi": (290.0, 292.0),   # π→π* shake-up
    53	}
    54	
    55	# FWHM priors (eV):
    56	# graphitic main — ordered single species, may be narrow.  UNVERIFIED
    57	# (fitalg; instrument-dependent; no primary source — labeled expert fits
    58	# put the graphitic main at 0.61–0.73 eV on this instrument, consistent
    59	# with but not derived from this range).
    60	FWHM_RANGE_GRAPHITIC = (0.4, 1.2)
    61	# aromatic-polymer main — Beamson & Briggs, "High Resolution XPS of Organic
    62	# Polymers — The Scienta ESCA300 Database", Wiley (1992): aromatic C 1s
    63	# 0.9–1.5 eV; (0.8, 1.8) is the generous cross-instrument envelope.
    64	FWHM_RANGE_AROMATIC_POLYMER = (0.8, 1.8)
    65	# π→π* satellite — intrinsically broad (multi-electron excitation).
    66	# fitalg's (1.0, 3.0) was an UNVERIFIED tunable; CALIBRATED 2026-07-03 on the
    67	# labeled expert set: 44 expert C 1s fits across 5 projects / 2 analysts fit
    68	# the satellite at 1.9–5.0 eV (median 4.17).  With the 3.0 cap every gate
    69	# candidate pegged satellite_pi:fwhm@max and was filtered — zero survivors.
    70	FWHM_RANGE_SATELLITE = (1.0, 5.5)
    71	# adventitious carbon (incl. aliphatic main): 0.8 eV floor per Biesinger,
    72	# Appl. Surf. Sci. 597 (2022) 153681 and Greczynski & Hultman (2020);
    73	# ~2.0 eV UNIFORM CAP per expert adjudication 2026-07-03
    74	# (docs/autofit/adjudication-decisions.md #5) — a literature-reasonable
    75	# upper bound, instrument/pass-energy-dependent; a CAP, not a target.
    76	# Replaces the previous SPLIT convention (Biesinger 1.6 ceiling for the
    77	# A/M/B families vs a 3.5 labeled-set-calibrated ceiling for the AG/MG
    78	# expert-practice families).  NOTE the labeled expert set fits adventitious
    79	# components at median 2.08 eV (70% above 1.6, max 5.46): under the
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

exec
/bin/zsh -lc 'git show --find-renames --find-copies --patch 5070662 -- autofit/regions/c1s.py autofit/regions/b1s.py autofit/regions/cl2p.py autofit/regions/n1s.py autofit/regions/u4f.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-XMvbuHhi' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-06Ad9Uhm' (errno=Operation not permitted)
commit 50706627acd94fc45e32840a414e7517468f5463
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Mon Jul 20 11:47:22 2026 -0600

    refactor(autofit): decouple broad_justification from fwhm_range's magnitude
    
    Both Codex reviews of 77bf3a8 (MIXED material class) independently caught
    the same MAJOR finding: autofit/engine.py's _unphysical_width_flags
    inferred "this region module vouches this width is real physics" from a
    bare numeric test (declared_hi > FWHM_MAX_ORDINARY_EV). fwhm_range's upper
    bound was overloaded with two independent meanings — "the optimizer may
    search up to here" and "this slot's width is cited region physics, not an
    optimizer papering over a missed feature" — with the badge following
    whichever number happened to be in the tuple. Widening a bound for an
    UNRELATED reason (77bf3a8 relaxed C1s contamination to 15.0 eV purely for
    differential-charging headroom) silently asserted the second meaning as a
    side effect — backwards, since MIXED's entire premise is that we do NOT
    know how broad differential charging makes the peak, the opposite of
    vouching for it. Same failure-mode family as the provenance audit's own
    C 1s self-reference fix: one field serving two roles, with the badge
    following the wrong one.
    
    Fix: ComponentSlot gains broad_justification: Optional[str] = None
    (autofit/grammar.py). _unphysical_width_flags (both its DS+G/asym-GL
    effective-width branches and the plain pegging check) now keys exemption
    off `slot.broad_justification is not None`, never off fwhm_range's
    magnitude. Pure refactor — the exemption SET does not change for any
    existing (non-MIXED) slot.
    
    Set broad_justification on every slot currently exempt under the old
    numeric rule, read directly off each region module (exhaustively, not
    guessed): C1s satellite_pi (genuine mechanism — pi->pi* shake-up,
    multi-electron excitation, further calibrated on the labeled expert set);
    B1s all 3 mains (honestly UNVERIFIED-empirical only — labeled-set
    calibration, no mechanism cited); Cl2p main_cl2p32 + the shared-width
    main_cl2p12 variant (same honest empirical-only disclosure) and the
    free-width main_cl2p12 variant (genuine mechanism — 2p1/2 Coster-Kronig
    broadening per adjudication #7, though the specific 0.8 eV excess bound
    is itself still an unverified tunable); N1s main_n1s in both shape
    variants (honestly UNVERIFIED-empirical, single labeled exemplar only);
    U4f mains (genuine VERIFIED mechanism — U(IV) 5f2 unresolved multiplet
    manifold, Ilton & Bagus 2011) and U4f satellites (real physical feature,
    but the specific width bound is itself empirical-only). Deliberately NOT
    uniform prose — some slots get a real physical citation, others get an
    honest "empirical-only, no mechanism cited" disclosure, matching exactly
    what each module's own existing comments already supported. Writing every
    justification the same way would just relocate the original overload
    into the new field with better spelling.
    
    Consequence, already true before Unit B (MIXED's own follow-up fixes)
    even lands: a C1s contamination slot under MIXED, which has a wide
    fwhm_range but (by design) no broad_justification, is no longer exempt.
    Independently verified with a one-off script: an 8 eV MIXED contaminant
    now correctly produces an unphysical-widths flag, closing the exact
    scenario both Codex reviews described.
    
    Tests (TDD): tests/autofit/test_broad_justification.py (31 tests) —
    an explicit fixture enumerating every currently-exempt/non-exempt slot
    across all 5 regions (14 cases), proving broad_justification's presence
    matches the pre-refactor numeric rule exactly, and that
    _unphysical_width_flags' actual OUTPUT at each slot's own ceiling matches
    too; two generic engine-level tests proving exemption is governed by the
    field alone, independent of the bound's magnitude in either direction
    (a wide unjustified bound is no longer exempt; a narrow justified one
    is). One pre-existing test fixed:
    tests/autofit/test_preseed_dominants.py::test_unphysical_width_flags_helper
    hand-constructed a synthetic "satellite_pi" slot relying on the old
    numeric-only mechanism (wide range, no explicit vouch) — updated to set
    broad_justification explicitly, matching how every real region module now
    grants the exemption, plus a new pinned case for the wide-but-unvouched
    scenario.
    
    Full suite: 727 passed, 6 skipped, 1 failed (test_u4f_n1s_cofit, a
    pre-existing timing/hash-seed-sensitive flake, byte-identical to failures
    already independently confirmed unrelated earlier this session).
    RUN_AUTOFIT_GATE=1 gate suite: 11 passed, 1 failed (the other known
    pre-existing test_candidate_pool_real_gate.py ds8 timing-budget flake,
    also byte-identical to prior confirmed instances).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>

diff --git a/autofit/regions/b1s.py b/autofit/regions/b1s.py
index 3d6a148..c17537f 100644
--- a/autofit/regions/b1s.py
+++ b/autofit/regions/b1s.py
@@ -93,6 +93,12 @@ class B1sModule:
                 role=role, region=REGION, phase_id=pid,
                 be_window=window, line_shape=LineShape.PSEUDO_VOIGT,
                 fwhm_range=B1S_FWHM_RANGE,
+                broad_justification=(
+                    "UNVERIFIED-empirical: labeled-set calibration only "
+                    "(B4C-UCl4 exemplar, labeled fits 1.49-2.27 eV) -- no "
+                    "region-specific physical broadening mechanism is "
+                    "cited; the range simply brackets the labeled data"
+                ),
             )
 
         low = pv("main_b_low", B1S_LOW_WINDOW)
diff --git a/autofit/regions/c1s.py b/autofit/regions/c1s.py
index 9e68678..aa31c40 100644
--- a/autofit/regions/c1s.py
+++ b/autofit/regions/c1s.py
@@ -334,6 +334,13 @@ class C1sModule:
             "satellite_pi", C1S_WINDOWS["shake_up_pi"], LineShape.PSEUDO_VOIGT,
             FWHM_RANGE_SATELLITE,
             linked_to="main_graphitic", linked_offset_range=SATELLITE_OFFSET_RANGE,
+            broad_justification=(
+                "pi->pi* shake-up satellite: physically broad due to "
+                "multi-electron excitation (a genuine broadening "
+                "mechanism, not merely calibration); the specific range "
+                "is further calibrated to the labeled expert set (44 "
+                "fits, 1.9-5.0 eV, CALIBRATED 2026-07-03)"
+            ),
         )
 
         def contam(key, linked_fwhm=None, offset=None,
diff --git a/autofit/regions/cl2p.py b/autofit/regions/cl2p.py
index eebaae0..86b814d 100644
--- a/autofit/regions/cl2p.py
+++ b/autofit/regions/cl2p.py
@@ -123,11 +123,28 @@ class Cl2pModule:
             )
         pid = phase.id
 
+        _empirical_justification = (
+            "UNVERIFIED-empirical: labeled-set calibration only (labeled "
+            "fits 1.65-1.80 eV) -- no region-specific physical broadening "
+            "mechanism is cited"
+        )
+        _coster_kronig_justification = (
+            "2p1/2 Coster-Kronig broadening is a genuine physical "
+            "mechanism (an additional non-radiative decay channel "
+            "unavailable to 2p3/2 shortens the 2p1/2 core-hole lifetime "
+            "and broadens its linewidth; adjudication 2026-07-03, "
+            "docs/autofit/adjudication-decisions.md #7), but the specific "
+            "excess bound (0.8 eV, ~45% of the labeled shared width) is "
+            "itself an UNVERIFIED bounded-relaxation tunable, not a cited "
+            "magnitude"
+        )
+
         def p32() -> ComponentSlot:
             return ComponentSlot(
                 role="main_cl2p32", region=REGION, phase_id=pid,
                 be_window=CL2P_32_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
                 fwhm_range=CL2P_FWHM_RANGE,
+                broad_justification=_empirical_justification,
             )
 
         def p12(ratio, ratio_range, free_width=False) -> ComponentSlot:
@@ -144,6 +161,7 @@ class Cl2pModule:
                     area_ratio_range=ratio_range,
                     share_parent_params=("gl_ratio",),
                     fwhm_excess_range=CL2P_12_FWHM_EXCESS_RANGE,
+                    broad_justification=_coster_kronig_justification,
                 )
             return ComponentSlot(
                 role="main_cl2p12", region=REGION, phase_id=pid,
@@ -154,6 +172,7 @@ class Cl2pModule:
                 area_ratio=ratio,
                 area_ratio_range=ratio_range,
                 share_parent_params=("gl_ratio", "fwhm"),
+                broad_justification=_empirical_justification,
             )
 
         return [
diff --git a/autofit/regions/n1s.py b/autofit/regions/n1s.py
index dc32cae..84de505 100644
--- a/autofit/regions/n1s.py
+++ b/autofit/regions/n1s.py
@@ -68,16 +68,23 @@ class N1sModule:
                 f"N 1s defines no oxidation-state override {oxidation_state!r}"
             )
         pid = phase.id
+        _justification = (
+            "UNVERIFIED-empirical: single labeled exemplar only (fwhm "
+            "1.05 eV) -- no physical broadening mechanism cited; this is "
+            "Stage-3 minimal N 1s support, not the full cookbook module"
+        )
         pv_main = ComponentSlot(
             role="main_n1s", region=REGION, phase_id=pid,
             be_window=N1S_WINDOW, line_shape=LineShape.PSEUDO_VOIGT,
             fwhm_range=N1S_FWHM_RANGE,
+            broad_justification=_justification,
         )
         ag_main = ComponentSlot(
             role="main_n1s", region=REGION, phase_id=pid,
             be_window=N1S_WINDOW, line_shape=LineShape.ASYM_GL,
             fwhm_range=N1S_FWHM_RANGE,
             param_ranges=(("asymmetry", N1S_ASYM_RANGE),),
+            broad_justification=_justification,
         )
         return [
             CandidateModel(name="N0_pv", background=N1S_BACKGROUND,
diff --git a/autofit/regions/u4f.py b/autofit/regions/u4f.py
index 135e956..555b975 100644
--- a/autofit/regions/u4f.py
+++ b/autofit/regions/u4f.py
@@ -199,11 +199,27 @@ class U4fModule:
                 be_window=window, line_shape=shape, fwhm_range=fwhm_range, **kw,
             )
 
+        _main_justification = (
+            "U(IV) 5f2 open-shell final state: an unresolved multiplet "
+            "manifold of unknown line count is the physically-correct "
+            "reading of this width (VERIFIED mechanism, Ilton & Bagus, "
+            "Surf. Interface Anal. 43 (2011) 1549, DOI 10.1002/sia.3836; "
+            "see module docstring); the specific range is UNVERIFIED-"
+            "empirical (labeled set 2.44-2.74 eV)"
+        )
+        _sat_justification = (
+            "the U(IV) shake-up satellite is a real physical feature "
+            "(Ilton & Bagus 2011), but this specific WIDTH bound is "
+            "UNVERIFIED-empirical (labeled set 2.09-3.30 eV), not itself "
+            "derived from a cited broadening magnitude"
+        )
+
         main_72 = slot(
             "main_u4f72", U4F72_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
             param_ranges=(("alpha", U4F_LACX_ALPHA_RANGE),
                           ("beta", U4F_LACX_BETA_RANGE),
                           ("m", U4F_LACX_M_RANGE)),
+            broad_justification=_main_justification,
         )
         main_52 = slot(
             "main_u4f52", U4F52_WINDOW, LineShape.LACX, U4F_MAIN_FWHM_RANGE,
@@ -212,6 +228,7 @@ class U4fModule:
             area_ratio=U4F_RATIO_DEFAULT,
             area_ratio_range=U4F_RATIO_RANGE,
             share_parent_params=("alpha", "beta", "m", "fwhm"),
+            broad_justification=_main_justification,
         )
 
         sat_72 = slot(
@@ -219,6 +236,7 @@ class U4fModule:
             U4F_SAT_FWHM_RANGE,
             linked_to="main_u4f72",
             linked_offset_range=U4F_SAT_OFFSET_RANGE,
+            broad_justification=_sat_justification,
         )
         sat_52 = slot(
             "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
@@ -228,6 +246,7 @@ class U4fModule:
             area_ratio=U4F_RATIO_DEFAULT,
             area_ratio_range=U4F_RATIO_RANGE,
             share_parent_params=("gl_ratio", "fwhm"),
+            broad_justification=_sat_justification,
         )
         # Free pair separation, everything else still tied (U1b).
         sat_52_freesep = slot(
@@ -238,6 +257,7 @@ class U4fModule:
             area_ratio=U4F_RATIO_DEFAULT,
             area_ratio_range=U4F_RATIO_RANGE,
             share_parent_params=("gl_ratio", "fwhm"),
+            broad_justification=_sat_justification,
         )
 
         # Robustness variant: satellites ride their own mains independently
@@ -247,12 +267,14 @@ class U4fModule:
             U4F_SAT_FWHM_RANGE,
             linked_to="main_u4f72",
             linked_offset_range=U4F_SAT_OFFSET_RANGE,
+            broad_justification=_sat_justification,
         )
         sat_52_free = slot(
             "satellite_u4f52", U4F_SAT52_WINDOW, LineShape.PSEUDO_VOIGT,
             U4F_SAT_FWHM_RANGE,
             linked_to="main_u4f52",
             linked_offset_range=U4F_SAT_OFFSET_RANGE,
+            broad_justification=_sat_justification,
         )
 
         return [

exec
/bin/zsh -lc 'git show --find-renames --find-copies --stat --patch 5070662 -- autofit/grammar.py autofit/engine.py tests/autofit/test_broad_justification.py tests/autofit/test_preseed_dominants.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-FHdSPu6l' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-rM8XsdUN' (errno=Operation not permitted)
commit 50706627acd94fc45e32840a414e7517468f5463
Author: Skye Fortier <skyefortier@gmail.com>
Date:   Mon Jul 20 11:47:22 2026 -0600

    refactor(autofit): decouple broad_justification from fwhm_range's magnitude
    
    Both Codex reviews of 77bf3a8 (MIXED material class) independently caught
    the same MAJOR finding: autofit/engine.py's _unphysical_width_flags
    inferred "this region module vouches this width is real physics" from a
    bare numeric test (declared_hi > FWHM_MAX_ORDINARY_EV). fwhm_range's upper
    bound was overloaded with two independent meanings — "the optimizer may
    search up to here" and "this slot's width is cited region physics, not an
    optimizer papering over a missed feature" — with the badge following
    whichever number happened to be in the tuple. Widening a bound for an
    UNRELATED reason (77bf3a8 relaxed C1s contamination to 15.0 eV purely for
    differential-charging headroom) silently asserted the second meaning as a
    side effect — backwards, since MIXED's entire premise is that we do NOT
    know how broad differential charging makes the peak, the opposite of
    vouching for it. Same failure-mode family as the provenance audit's own
    C 1s self-reference fix: one field serving two roles, with the badge
    following the wrong one.
    
    Fix: ComponentSlot gains broad_justification: Optional[str] = None
    (autofit/grammar.py). _unphysical_width_flags (both its DS+G/asym-GL
    effective-width branches and the plain pegging check) now keys exemption
    off `slot.broad_justification is not None`, never off fwhm_range's
    magnitude. Pure refactor — the exemption SET does not change for any
    existing (non-MIXED) slot.
    
    Set broad_justification on every slot currently exempt under the old
    numeric rule, read directly off each region module (exhaustively, not
    guessed): C1s satellite_pi (genuine mechanism — pi->pi* shake-up,
    multi-electron excitation, further calibrated on the labeled expert set);
    B1s all 3 mains (honestly UNVERIFIED-empirical only — labeled-set
    calibration, no mechanism cited); Cl2p main_cl2p32 + the shared-width
    main_cl2p12 variant (same honest empirical-only disclosure) and the
    free-width main_cl2p12 variant (genuine mechanism — 2p1/2 Coster-Kronig
    broadening per adjudication #7, though the specific 0.8 eV excess bound
    is itself still an unverified tunable); N1s main_n1s in both shape
    variants (honestly UNVERIFIED-empirical, single labeled exemplar only);
    U4f mains (genuine VERIFIED mechanism — U(IV) 5f2 unresolved multiplet
    manifold, Ilton & Bagus 2011) and U4f satellites (real physical feature,
    but the specific width bound is itself empirical-only). Deliberately NOT
    uniform prose — some slots get a real physical citation, others get an
    honest "empirical-only, no mechanism cited" disclosure, matching exactly
    what each module's own existing comments already supported. Writing every
    justification the same way would just relocate the original overload
    into the new field with better spelling.
    
    Consequence, already true before Unit B (MIXED's own follow-up fixes)
    even lands: a C1s contamination slot under MIXED, which has a wide
    fwhm_range but (by design) no broad_justification, is no longer exempt.
    Independently verified with a one-off script: an 8 eV MIXED contaminant
    now correctly produces an unphysical-widths flag, closing the exact
    scenario both Codex reviews described.
    
    Tests (TDD): tests/autofit/test_broad_justification.py (31 tests) —
    an explicit fixture enumerating every currently-exempt/non-exempt slot
    across all 5 regions (14 cases), proving broad_justification's presence
    matches the pre-refactor numeric rule exactly, and that
    _unphysical_width_flags' actual OUTPUT at each slot's own ceiling matches
    too; two generic engine-level tests proving exemption is governed by the
    field alone, independent of the bound's magnitude in either direction
    (a wide unjustified bound is no longer exempt; a narrow justified one
    is). One pre-existing test fixed:
    tests/autofit/test_preseed_dominants.py::test_unphysical_width_flags_helper
    hand-constructed a synthetic "satellite_pi" slot relying on the old
    numeric-only mechanism (wide range, no explicit vouch) — updated to set
    broad_justification explicitly, matching how every real region module now
    grants the exemption, plus a new pinned case for the wide-but-unvouched
    scenario.
    
    Full suite: 727 passed, 6 skipped, 1 failed (test_u4f_n1s_cofit, a
    pre-existing timing/hash-seed-sensitive flake, byte-identical to failures
    already independently confirmed unrelated earlier this session).
    RUN_AUTOFIT_GATE=1 gate suite: 11 passed, 1 failed (the other known
    pre-existing test_candidate_pool_real_gate.py ds8 timing-budget flake,
    also byte-identical to prior confirmed instances).
    
    Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
---
 autofit/engine.py                         |  54 +++++---
 autofit/grammar.py                        |  17 +++
 tests/autofit/test_broad_justification.py | 209 ++++++++++++++++++++++++++++++
 tests/autofit/test_preseed_dominants.py   |  48 ++++++-
 4 files changed, 301 insertions(+), 27 deletions(-)

diff --git a/autofit/engine.py b/autofit/engine.py
index fa9695d..1824cbb 100644
--- a/autofit/engine.py
+++ b/autofit/engine.py
@@ -756,26 +756,39 @@ def _unphysical_width_flags(
     """Fitted components whose width reaches the ordinary physical FWHM
     ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.
 
-    A slot whose grammar-declared ``fwhm_range`` maximum EXCEEDS the ordinary
-    cap is grammar-sanctioned-broad (C 1s π→π* satellite 5.5, U 4f mains 3.5,
-    B 1s 2.5, …) and is EXEMPT — its width is region physics, cited in the
-    region module, not an unphysical stretch.  Any other slot — contamination,
-    the aliphatic main, and the region-``unassigned`` F1 pre-seed / F2-F3
-    proposal slots (all capped AT the ordinary ceiling) — that fits at/above
-    the ceiling is flagged: the optimizer wanted a wider (fatter) peak than an
+    A slot is grammar-sanctioned-broad — EXEMPT, because its width is region
+    physics cited in the region module, not an unphysical stretch — if and
+    only if it carries an explicit ``ComponentSlot.broad_justification``
+    (C 1s π→π* satellite, U 4f mains, B 1s, …; see each region module for its
+    citation or honest UNVERIFIED-empirical disclosure). Any other slot —
+    contamination, the aliphatic main, and the region-``unassigned`` F1
+    pre-seed / F2-F3 proposal slots — that fits at/above the ordinary
+    ceiling is flagged: the optimizer wanted a wider (fatter) peak than an
     ordinary component physically has, the cap held it at the limit, and the
     decomposition must be reported low-confidence (routes to the CONDITIONAL
-    tier via rank_and_filter) rather than silently accepted.  Region-agnostic:
-    the exemption is driven entirely by each slot's own declared range, so no
-    region's cited widths are ever mis-flagged.
+    tier via rank_and_filter) rather than silently accepted.
+
+    ``broad_justification`` is INDEPENDENT of ``fwhm_range``'s own magnitude
+    (2026-07-20 refactor, Codex-caught in the MIXED material-class review):
+    the exemption used to be inferred from ``declared_hi >
+    FWHM_MAX_ORDINARY_EV`` alone, which conflated "the optimizer may search
+    this wide" with "this region module vouches the width is real physics".
+    Widening a bound for an unrelated reason (numerical-stability headroom,
+    a wider calibration envelope, MIXED material class's relaxed
+    contamination ceiling) used to silently grant the vouching exemption as
+    a side effect. Region-agnostic: the exemption is driven entirely by
+    each slot's own declared field, so no region's cited widths are ever
+    mis-flagged, and no bound can ever again disable this safety net merely
+    by being wide.
     """
-    ranges = {s.role: s.fwhm_range for s in model.slots}
+    slots_by_role = {s.role: s for s in model.slots}
     flags: list[str] = []
     for c in components:
-        rng = ranges.get(c.slot_role)
-        if rng is None:
+        slot = slots_by_role.get(c.slot_role)
+        if slot is None:
             continue
-        declared_lo, declared_hi = rng
+        declared_lo, declared_hi = slot.fwhm_range
+        vouched = slot.broad_justification is not None
         # EFFECTIVE width (Stage-2 PHYSICAL bar): DS+G's width lives in TWO
         # params — beta (Lorentzian HWHM, eV) and m_gauss (Gaussian FWHM;
         # what comp.fwhm carries) — so the checks below must see the
@@ -787,8 +800,7 @@ def _unphysical_width_flags(
         if c.line_shape is LineShape.DS_G:
             f_l = 2.0 * float(c.shape_params.get("beta", 0.0))
             eff_fwhm = 0.5346 * f_l + np.sqrt(0.2166 * f_l ** 2 + c.fwhm ** 2)
-            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and \
-                    declared_hi <= FWHM_MAX_ORDINARY_EV:
+            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
                 flags.append(
                     f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                     f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
@@ -802,8 +814,7 @@ def _unphysical_width_flags(
             # (Codex Stage-2 review, run A MAJOR).
             asym = float(c.shape_params.get("asymmetry", 0.0))
             eff_fwhm = c.fwhm * (1.0 + 0.5 * asym)
-            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and \
-                    declared_hi <= FWHM_MAX_ORDINARY_EV:
+            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and not vouched:
                 flags.append(
                     f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
                     f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
@@ -814,7 +825,10 @@ def _unphysical_width_flags(
         # ordinary cap): a component at ≥ DETECTION_WIDTH_ABSORB_FRACTION
         # of its own ceiling (= 1.75× the DETECTED width via the 2.5×
         # ceiling) is absorbing neighboring intensity — the papering-over
-        # signature in transferable units.
+        # signature in transferable units. Unaffected by broad_justification
+        # (these are engine-constructed proposal/pre-seed slots, not
+        # region-module-authored grammar; their ceiling is scale-relative,
+        # not a physics vouch).
         if c.slot_role.startswith("detected_peak_"):
             if eff_fwhm >= DETECTION_WIDTH_ABSORB_FRACTION * declared_hi:
                 flags.append(
@@ -823,7 +837,7 @@ def _unphysical_width_flags(
                     f"({declared_hi:.2f}eV) — ~1.75× its detected width; "
                     "likely absorbing a neighbor")
             continue
-        if declared_hi > FWHM_MAX_ORDINARY_EV:
+        if vouched:
             continue                       # grammar-sanctioned-broad slot
         # pegging the ordinary ceiling — same 1%-of-range tol as boundary
         # detection, so a component held AT the 2.0 cap is caught
diff --git a/autofit/grammar.py b/autofit/grammar.py
index 01ad401..1e291f2 100644
--- a/autofit/grammar.py
+++ b/autofit/grammar.py
@@ -163,6 +163,23 @@ class ComponentSlot:
     # linked-peak sync.
     share_parent_params: tuple[str, ...] = ()
 
+    # Explicit semantic claim, independent of fwhm_range's magnitude
+    # (2026-07-20 refactor): the region module VOUCHES that a component
+    # this wide is legitimate physics for this slot specifically — e.g. the
+    # C 1s π→π* shake-up satellite's intrinsic multi-electron-excitation
+    # breadth, or U 4f's unresolved 5f² multiplet manifold. None means the
+    # slot's width is ordinary — no known-broad justification exists, so
+    # autofit.engine._unphysical_width_flags must not exempt it, REGARDLESS
+    # of how wide fwhm_range happens to be. Before this field existed,
+    # fwhm_range's upper bound alone served double duty as both the
+    # optimizer's search bound AND this semantic claim (declared_hi >
+    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
+    # bound for an UNRELATED reason (numerical-stability headroom, a wider
+    # calibration envelope) silently asserted "this is vouched-for physics"
+    # as a side effect. A region module that just needs search headroom
+    # without vouching for width MUST leave this None.
+    broad_justification: Optional[str] = None
+
     def contains(self, be: float, fwhm: float, amplitude: float,
                  noise_floor: float) -> bool:
         return (
diff --git a/tests/autofit/test_broad_justification.py b/tests/autofit/test_broad_justification.py
new file mode 100644
index 0000000..b7dcb05
--- /dev/null
+++ b/tests/autofit/test_broad_justification.py
@@ -0,0 +1,209 @@
+"""Unit A (2026-07-20): decouples two meanings that ``fwhm_range``'s upper
+bound used to carry at once:
+
+  1. the optimizer's own search bound ("the width parameter may search up
+     to here");
+  2. a semantic claim consumed by quality reporting ("this region module
+     VOUCHES that a component this wide is legitimate physics, not an
+     optimizer papering over a missed feature").
+
+``autofit/engine.py``'s ``_unphysical_width_flags`` used to infer (2) from
+(1) via a bare numeric test (``declared_hi > FWHM_MAX_ORDINARY_EV``). The
+MIXED material-class unit (77bf3a8) relaxed (1) for C 1s contamination
+slots to make room for differential-charging broadening, and thereby
+silently asserted (2) as a side effect -- exactly backwards, since MIXED's
+entire premise is that we do NOT know how broad differential charging
+makes the peak, the opposite of vouching for it. Both Codex reviews of
+77bf3a8 independently caught this (see docs/autofit/codex/
+mixed_material_class_verdict_run{A,B}.md).
+
+The fix: ``ComponentSlot.broad_justification`` makes meaning (2) an
+explicit, independent field. ``_unphysical_width_flags`` keys its
+exemption off ``broad_justification is not None``, never off the bound's
+magnitude. This file is the safety net for that refactor: it encodes, as
+an explicit and auditable fixture, EXACTLY which slots are exempt today
+(under the old numeric rule) so the same set stays exempt under the new
+field-based rule -- pure refactor, behavior-neutral, proven rather than
+asserted.
+"""
+from __future__ import annotations
+
+import pytest
+
+from autofit.engine import FittedComponent, _unphysical_width_flags
+from autofit.grammar import LineShape, MaterialClass, Phase, resolve
+
+# ── Ground truth: which slots are grammar-sanctioned-broad TODAY ───────────
+# (declared_hi > FWHM_MAX_ORDINARY_EV == 2.0 eV, the pre-refactor rule),
+# derived by reading every region module's build_candidates(). Each entry
+# names the region, the exact CandidateModel to fetch it from, and the
+# slot role. This is the fixture the refactor must reproduce exactly.
+
+_CONDUCTOR_C1S = Phase(id="s", material_class=MaterialClass.CONDUCTOR,
+                       regions=("C 1s",))
+_INSULATOR_B1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
+                       regions=("B 1s",))
+_INSULATOR_CL2P = Phase(id="s", material_class=MaterialClass.INSULATOR,
+                        regions=("Cl 2p",))
+_INSULATOR_N1S = Phase(id="s", material_class=MaterialClass.INSULATOR,
+                       regions=("N 1s",))
+_INSULATOR_U4F = Phase(id="s", material_class=MaterialClass.INSULATOR,
+                       regions=("U 4f",))
+
+
+def _slot(phase, region, candidate_name, role):
+    g = resolve([phase], region)
+    cand = next(c for c in g.candidates if c.name == candidate_name)
+    slot = cand.slot_by_role(role)
+    assert slot is not None, f"{candidate_name}/{role} not found"
+    return slot
+
+
+# (phase, region, candidate_name, role, currently_exempt)
+EXEMPTION_FIXTURE = [
+    # C 1s: only the pi->pi* satellite is exempt (declared 1.0-5.5).
+    (_CONDUCTOR_C1S, "C 1s", "A0_graphite_asym_satellite", "satellite_pi", True),
+    (_CONDUCTOR_C1S, "C 1s", "A0_graphite_asym_satellite", "main_graphitic", False),
+    (_CONDUCTOR_C1S, "C 1s", "B2_linked", "main_aliphatic", False),
+    (_CONDUCTOR_C1S, "C 1s", "A1_linked", "contamination_CO", False),
+    # B 1s: all three mains share B1S_FWHM_RANGE (1.2-2.5) -- all exempt.
+    (_INSULATOR_B1S, "B 1s", "B1_low", "main_b_low", True),
+    (_INSULATOR_B1S, "B 1s", "B2_low_mid", "main_b_mid", True),
+    (_INSULATOR_B1S, "B 1s", "B2b_low_oxide", "main_b_oxide", True),
+    # Cl 2p: both p32 (shared-width family) and p12 exempt at CL2P_FWHM_RANGE
+    # (1.2-2.2) / CL2P_12_FWHM_RANGE (free-width family, up to 3.0).
+    (_INSULATOR_CL2P, "Cl 2p", "Cl0_doublet", "main_cl2p32", True),
+    (_INSULATOR_CL2P, "Cl 2p", "Cl0_doublet", "main_cl2p12", True),
+    (_INSULATOR_CL2P, "Cl 2p", "Cl0w_doublet_freewidth", "main_cl2p12", True),
+    # N 1s: main_n1s exempt at N1S_FWHM_RANGE (0.7-2.5) in both shape variants.
+    (_INSULATOR_N1S, "N 1s", "N0_pv", "main_n1s", True),
+    (_INSULATOR_N1S, "N 1s", "N0_asymGL", "main_n1s", True),
+    # U 4f: mains (1.5-3.5) and satellites (1.5-4.5) both exempt.
+    (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f72", True),
+    (_INSULATOR_U4F, "U 4f", "U0_mains", "main_u4f52", True),
+]
+
+
+@pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
+                         EXEMPTION_FIXTURE)
+def test_exemption_fixture_matches_broad_justification(
+        phase, region, candidate_name, role, exempt):
+    """Each currently-exempt slot must carry a real broad_justification;
+    each currently-non-exempt slot must not. This IS the byte-identical
+    proof requested: the exemption SET, read directly off the grammar,
+    matches the pre-refactor numeric rule exactly."""
+    slot = _slot(phase, region, candidate_name, role)
+    if exempt:
+        assert slot.broad_justification is not None, (
+            f"{region}/{candidate_name}/{role} was grammar-sanctioned-broad "
+            f"under the old numeric rule (fwhm_range={slot.fwhm_range}) but "
+            "lost its exemption in the refactor"
+        )
+        assert slot.fwhm_range[1] > 2.0, (
+            "fixture sanity: this entry's OWN historical exemption basis "
+            "was declared_hi > 2.0 -- if this fails, the fixture itself is "
+            "wrong, not the code"
+        )
+    else:
+        assert slot.broad_justification is None, (
+            f"{region}/{candidate_name}/{role} was NOT grammar-sanctioned-"
+            f"broad under the old numeric rule (fwhm_range={slot.fwhm_range}) "
+            "but gained an unjustified exemption in the refactor"
+        )
+
+
+def _fitted(role, fwhm, line_shape=LineShape.PSEUDO_VOIGT, **shape_params):
+    return FittedComponent(slot_role=role, position=0.0, fwhm=fwhm,
+                           amplitude=1.0, shape_params=shape_params,
+                           line_shape=line_shape)
+
+
+class _FakeModel:
+    """Minimal stand-in for CandidateModel -- _unphysical_width_flags only
+    reads .slots."""
+    def __init__(self, slots):
+        self.slots = slots
+
+
+@pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
+                         EXEMPTION_FIXTURE)
+def test_flag_behavior_matches_pre_refactor_rule_at_the_ceiling(
+        phase, region, candidate_name, role, exempt):
+    """The actual OUTPUT of _unphysical_width_flags for a component fitted
+    right at its slot's declared ceiling must match what the pre-refactor
+    numeric rule would have produced: no flag for an exempt slot even
+    though it pegs a wide ceiling; a flag for a non-exempt slot pegging
+    the ordinary 2.0 eV cap."""
+    slot = _slot(phase, region, candidate_name, role)
+    g = resolve([phase], region)
+    cand = next(c for c in g.candidates if c.name == candidate_name)
+    fwhm_at_ceiling = slot.fwhm_range[1] if exempt else 2.0
+    comp = _fitted(role, fwhm_at_ceiling, line_shape=slot.line_shape)
+    flags = _unphysical_width_flags([comp], cand)
+    if exempt:
+        assert not flags, (
+            f"{region}/{candidate_name}/{role}: exempt slot got flagged "
+            f"at its own ceiling -- {flags}"
+        )
+    else:
+        assert flags, (
+            f"{region}/{candidate_name}/{role}: non-exempt slot pegging "
+            "the ordinary 2.0 eV cap should be flagged"
+        )
+
+
+# ── The actual bug fix, tested generically at the engine level ────────────
+
+def test_wide_declared_range_without_justification_is_no_longer_exempt():
+    """THE FIX, encoded directly: a slot with a wide fwhm_range (would have
+    been auto-exempt under the old numeric rule) but broad_justification
+    left None must now be flagged when fitted well above the ordinary
+    2.0 eV cap -- this is the MIXED contamination scenario, tested here
+    independent of MIXED or C 1s at all."""
+    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
+
+    wide_no_justification = ComponentSlot(
+        role="wide_slot", region="Test", phase_id="s",
+        be_window=(280.0, 295.0), line_shape=LineShape.PSEUDO_VOIGT,
+        fwhm_range=(0.8, 15.0), broad_justification=None,
+    )
+    model = CandidateModel(name="synthetic", background=BackgroundType.SHIRLEY,
+                           slots=(wide_no_justification,))
+    comp = _fitted("wide_slot", 8.0)   # well above 2.0, well below 15.0
+    flags = _unphysical_width_flags([comp], model)
+    assert flags, (
+        "a slot with a wide bound but NO broad_justification must still "
+        "be flagged when it fits wide -- the bound alone must never grant "
+        "exemption"
+    )
+
+
+def test_narrow_declared_range_with_justification_is_exempt():
+    """Mirror case: an explicit broad_justification grants exemption even
+    for a slot whose declared ceiling never exceeded the ordinary cap --
+    proving exemption is governed by the field, not a numeric side effect
+    of the bound's magnitude."""
+    from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
+
+    narrow_but_justified = ComponentSlot(
+        role="narrow_slot", region="Test", phase_id="s",
+        be_window=(280.0, 295.0), line_shape=LineShape.PSEUDO_VOIGT,
+        fwhm_range=(0.5, 2.0), broad_justification="synthetic test justification",
+    )
+    model = CandidateModel(name="synthetic", background=BackgroundType.SHIRLEY,
+                           slots=(narrow_but_justified,))
+    comp = _fitted("narrow_slot", 2.0)   # pegs its own (narrow) ceiling
+    flags = _unphysical_width_flags([comp], model)
+    assert not flags, (
+        "an explicit broad_justification must exempt a slot even when its "
+        "declared ceiling never exceeded the ordinary cap"
+    )
+
+
+def test_component_slot_broad_justification_defaults_to_none():
+    from autofit.grammar import ComponentSlot
+
+    s = ComponentSlot(role="r", region="Test", phase_id="s",
+                      be_window=(0.0, 1.0), line_shape=LineShape.PSEUDO_VOIGT,
+                      fwhm_range=(0.5, 1.0))
+    assert s.broad_justification is None
diff --git a/tests/autofit/test_preseed_dominants.py b/tests/autofit/test_preseed_dominants.py
index 574fcd2..74ec475 100644
--- a/tests/autofit/test_preseed_dominants.py
+++ b/tests/autofit/test_preseed_dominants.py
@@ -159,16 +159,27 @@ def test_multi_env_low_be_dominant_recovered():
 
 def test_unphysical_width_flags_helper():
     """The width-flag helper: an ordinary slot pegging the 2.0 cap is
-    flagged; a narrow main and a grammar-sanctioned-broad slot (declared max
-    > 2.0, e.g. a satellite) are NOT."""
+    flagged; a narrow main and a grammar-sanctioned-broad slot (explicit
+    ``broad_justification``, e.g. a satellite) are NOT.
+
+    2026-07-20 (Unit A, broad_justification refactor): the exemption used
+    to be inferred from ``fwhm_range``'s own magnitude (declared max >
+    2.0 eV) — this test originally built its synthetic "satellite_pi" slot
+    with only a wide range and no explicit vouch, which is now correctly
+    NOT exempt (that numeric-only inference is exactly the bug the MIXED
+    material-class Codex review caught: widening a bound for an unrelated
+    reason silently asserted "this is vouched physics" as a side effect).
+    Updated to set broad_justification explicitly, matching how every real
+    region module now grants this exemption."""
     from autofit.grammar import (CandidateModel, ComponentSlot, LineShape,
                                  BackgroundType)
     from autofit.engine import FittedComponent
 
-    def slot(role, lo, hi):
+    def slot(role, lo, hi, broad_justification=None):
         return ComponentSlot(role=role, region="r", phase_id="p",
                              be_window=(199., 201.), line_shape=LineShape.PSEUDO_VOIGT,
-                             fwhm_range=(lo, hi))
+                             fwhm_range=(lo, hi),
+                             broad_justification=broad_justification)
 
     def comp(role, fwhm):
         return FittedComponent(slot_role=role, position=200.0, fwhm=fwhm,
@@ -176,19 +187,42 @@ def test_unphysical_width_flags_helper():
 
     m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
         slot("contamination_CO", 0.8, 2.0), slot("main_graphitic", 0.4, 1.2),
-        slot("satellite_pi", 1.0, 5.5), slot("proposed_peak_0", 0.5, 2.0)))
+        slot("satellite_pi", 1.0, 5.5,
+             broad_justification="synthetic: pi->pi* shake-up, physically broad"),
+        slot("proposed_peak_0", 0.5, 2.0)))
     flags = eng._unphysical_width_flags(
         [comp("contamination_CO", 1.99), comp("main_graphitic", 1.2),
          comp("satellite_pi", 5.16), comp("proposed_peak_0", 2.0)], m)
     flagged_roles = {f.split(":")[0] for f in flags}
     assert flagged_roles == {"contamination_CO", "proposed_peak_0"}
-    # a satellite at 5.16 (declared-broad slot) is NEVER flagged — this is
-    # exactly the "wide contamination" the fat-peak report was really about
+    # a satellite at 5.16 (explicitly vouched-broad slot) is NEVER flagged —
+    # this is exactly the "wide contamination" the fat-peak report was
+    # really about
     assert not any("satellite" in f for f in flags)
     # a component comfortably under the cap → no flag at all
     assert eng._unphysical_width_flags([comp("contamination_CO", 1.5)], m) == []
 
 
+def test_unphysical_width_flags_wide_range_alone_no_longer_exempts():
+    """The bug this refactor fixes, pinned directly: a slot with a WIDE
+    declared fwhm_range but NO broad_justification must be flagged when it
+    fits wide — the bound's magnitude alone must never grant exemption.
+    Mirrors the real MIXED material-class scenario (a relaxed contamination
+    ceiling with no physics vouch) at the helper level, region-agnostic."""
+    from autofit.grammar import (CandidateModel, ComponentSlot, LineShape,
+                                 BackgroundType)
+    from autofit.engine import FittedComponent
+
+    slot = ComponentSlot(role="wide_unvouched", region="r", phase_id="p",
+                         be_window=(199., 201.), line_shape=LineShape.PSEUDO_VOIGT,
+                         fwhm_range=(0.8, 15.0))
+    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
+    comp = FittedComponent(slot_role="wide_unvouched", position=200.0,
+                           fwhm=8.0, amplitude=1e3, shape_params={})
+    flags = eng._unphysical_width_flags([comp], m)
+    assert flags, "a wide-but-unvouched slot must be flagged, not exempted"
+
+
 def test_preseed_and_proposal_slots_capped_at_ordinary():
     """F1 pre-seed slots and F2/F3 proposal slots must be built with the
     ordinary physical FWHM ceiling as their upper bound — not the old

exec
/bin/zsh -lc "nl -ba autofit/regions/c1s.py | sed -n '430,560p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
/bin/zsh -lc "nl -ba autofit/regions/n1s.py | sed -n '1,140p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba autofit/regions/cl2p.py | sed -n '1,260p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	Cl 2p region module — the doublet exemplar (spec §3.4).
     3	
     4	Constants:
     5	- Δso = 1.60 eV and 2p3/2:2p1/2 = 2:1 (ratio 0.5): **CONDITIONAL** per spec
     6	  §9 (NaCl, Surf. Sci. Spectra — DOI 10.1116/1.1247741) until a
     7	  chloride-source primary fit is cited.  The labeled fits use exactly
     8	  1.60 / 0.5 with shared FWHM + GL mix.
     9	- 2p3/2 window: UNVERIFIED-calibration around the labeled chloride fits
    10	  (197.83–197.92, corrected frame).  NOTE the labeled set's uncorrected tab
    11	  (Cl2p Scan_1, ccShift 0, 2p3/2 at 193.38 raw) is OUT of this window by
    12	  construction — the engine consumes charge-corrected data.
    13	- The labeled Cl 2p fits carry the documented elevated χ²ᵣ (2.85/4.94) —
    14	  unmodeled structure is expected; the residual diagnostics/proposal pass
    15	  reports it rather than the grammar inventing an uncited second species.
    16	
    17	ADJUDICATION #7 (2026-07-03) — IMPLEMENTED, HYPOTHESIS REJECTED BY THE DATA
    18	(2026-07-04): the ruling ordered independent doublet widths (2p1/2 >=
    19	2p3/2, Coster-Kronig) with the expectation the area ratio returns to ~0.5.
    20	The machinery is implemented (``fwhm_excess_range`` + width-aware AREA-ratio
    21	linkage, validated on synthetic truth) and the free-width candidates are
    22	enumerated below — but on BOTH corrected real anchors the excess pegs at 0
    23	(width freedom buys nothing: χ²ᵣ 2.41/3.27 vs 2.40/3.25 shared-width) and
    24	the relaxed ratio still pegs at 0.55 with or without width freedom.  The
    25	ratio anomaly is therefore NOT a shared-FWHM artifact.  Per the ruling's
    26	fallback, secondary diagnostics were run and logged in PROGRESS.md (no
    27	scan-order ratio trend → no beam-damage signal; shallow ratio↔excess
    28	identifiability valley on Scan; residual dipole in the doublet valley plus
    29	positive low-BE shoulders at −2…−4.8 eV — differential-charging candidate,
    30	for Skye).  Consequently Δso/ratio REMAIN CONDITIONAL — the adjudicated
    31	lift was contingent on the ratio returning to ~0.5, which did not occur.
    32	"""
    33	
    34	from __future__ import annotations
    35	
    36	from typing import Optional
    37	
    38	from ..grammar import (
    39	    BackgroundType,
    40	    CandidateModel,
    41	    ComponentSlot,
    42	    LineShape,
    43	    Phase,
    44	)
    45	from . import register_region
    46	
    47	REGION = "Cl 2p"
    48	
    49	CL2P_32_WINDOW = (196.8, 199.0)     # UNVERIFIED-calibration (labeled 197.8–197.9)
    50	# Δso window around the CONDITIONAL 1.60 eV (10.1116/1.1247741).
    51	CL2P_SPLITTING_RANGE = (1.55, 1.65)
    52	CL2P_RATIO = 0.5                    # 2:1 statistical — CONDITIONAL (same source)
    53	CL2P_RATIO_RANGE = (0.45, 0.55)     # bounded relaxation variant — UNVERIFIED
    54	CL2P_FWHM_RANGE = (1.2, 2.2)        # UNVERIFIED-empirical (labeled 1.65–1.80)
    55	# 2p1/2 Coster-Kronig width EXCESS over the 2p3/2 (adjudication 2026-07-03,
    56	# docs/autofit/adjudication-decisions.md #7: the 2p1/2 is intrinsically
    57	# broader — the shared-FWHM constraint was mis-partitioning doublet area and
    58	# pushing the apparent ratio above 0.5).  Widths are INDEPENDENT under the
    59	# physical inequality fwhm(2p1/2) = fwhm(2p3/2) + excess, excess >= 0.
    60	# The excess UPPER bound is an UNVERIFIED bounded-relaxation tunable
    61	# (~45% of the labeled shared width); the data decides within it.
    62	CL2P_12_FWHM_EXCESS_RANGE = (0.0, 0.8)
    63	# containment range for the free-width 2p1/2 (32-range + excess cap)
    64	CL2P_12_FWHM_RANGE = (CL2P_FWHM_RANGE[0],
    65	                      CL2P_FWHM_RANGE[1] + CL2P_12_FWHM_EXCESS_RANGE[1])
    66	# 2p1/2 fallback window (matching only; center is expression-driven).
    67	CL2P_12_WINDOW = (CL2P_32_WINDOW[0] + CL2P_SPLITTING_RANGE[0],
    68	                  CL2P_32_WINDOW[1] + CL2P_SPLITTING_RANGE[1])
    69	
    70	# Expert practice for this data set (ui.bgType 'smart_exp') — UNVERIFIED.
    71	CL2P_BACKGROUND = BackgroundType.SMART_EXP
    72	
    73	
    74	class Cl2pModule:
    75	    region = REGION
    76	
    77	    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
    78	        return {"p32": CL2P_32_WINDOW, "p12": CL2P_12_WINDOW}
    79	
    80	    def provenance(self) -> list[dict]:
    81	        return [
    82	            {"constant": "spin_orbit_splitting_ev", "value": 1.60,
    83	             "status": "CONDITIONAL",
    84	             "source": "NaCl, Surf. Sci. Spectra, DOI 10.1116/1.1247741 — "
    85	                       "conditional until a chloride-source primary fit is cited"},
    86	            {"constant": "area_ratio_2p12_over_2p32", "value": CL2P_RATIO,
    87	             "status": "CONDITIONAL", "source": "2:1 statistical; same source"},
    88	            {"constant": "p32_window_ev", "value": list(CL2P_32_WINDOW),
    89	             "status": "UNVERIFIED",
    90	             "source": "labeled-set calibration (197.83–197.92 corrected)"},
    91	            {"constant": "fwhm_range_ev", "value": list(CL2P_FWHM_RANGE),
    92	             "status": "UNVERIFIED", "source": "labeled-set calibration"},
    93	            {"constant": "ratio_relaxation_range", "value": list(CL2P_RATIO_RANGE),
    94	             "status": "UNVERIFIED", "source": "bounded-relaxation tunable"},
    95	            {"constant": "p12_fwhm_excess_range_ev",
    96	             "value": list(CL2P_12_FWHM_EXCESS_RANGE),
    97	             "status": "UNVERIFIED",
    98	             "source": "bounded-relaxation tunable; independence itself per "
    99	                       "expert adjudication 2026-07-03 "
   100	                       "(docs/autofit/adjudication-decisions.md #7 — "
   101	                       "Coster-Kronig 2p1/2 broadening)"},
   102	            {"constant": "background", "value": "smart_exp",
   103	             "status": "UNVERIFIED", "source": "expert practice for this data set"},
   104	        ]
   105	
   106	    def build_candidates(
   107	        self, phase: Phase, oxidation_state: Optional[str] = None
   108	    ) -> list[CandidateModel]:
   109	        """
   110	        - ``Cl0_doublet``           — fixed 2:1 ratio, shared FWHM
   111	        - ``Cl0r_doublet_relaxed``  — bounded-relaxed ratio, shared FWHM
   112	        - ``Cl0w_doublet_freewidth``          — fixed 2:1 ratio, independent
   113	          widths (2p1/2 >= 2p3/2, Coster-Kronig — adjudication #7)
   114	        - ``Cl0rw_doublet_relaxed_freewidth`` — relaxed ratio + independent
   115	          widths (the full test: with width freedom the fitted ratio is
   116	          expected back at ~0.5)
   117	
   118	        The enumeration decides which hypothesis the data pays for.
   119	        """
   120	        if oxidation_state is not None:
   121	            raise KeyError(
   122	                f"Cl 2p defines no oxidation-state override {oxidation_state!r}"
   123	            )
   124	        pid = phase.id
   125	
   126	        _empirical_justification = (
   127	            "UNVERIFIED-empirical: labeled-set calibration only (labeled "
   128	            "fits 1.65-1.80 eV) -- no region-specific physical broadening "
   129	            "mechanism is cited"
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
/bin/zsh -lc "nl -ba autofit/regions/u4f.py | sed -n '1,330p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
     1	"""
     2	U 4f region module (spec v2.1 §3.2 — the Stage-3 deliverable).
     3	
     4	Model decision (Skye, domain expert; spec §3.2): U(IV) 5f² is an open-shell
     5	final state whose multiplet manifold is an unknown number of closely-spaced,
     6	individually unresolvable lines — the **asymmetric LACX lineshape is the
     7	physically-correct envelope of that manifold** (multiplet/final-state
     8	origin, NOT metallic screening — Ilton & Bagus, Surf. Interface Anal. 43
     9	(2011) 1549, DOI 10.1002/sia.3836; VERIFIED per spec §9).  The engine does
    10	not force a multiplet-peak decomposition; oxidation-state ASSIGNMENT is out
    11	of scope (parked).
    12	
    13	Structure (validated against 40+ expert U 4f fits in docs/autofit/test_data;
    14	see PROGRESS.md "U 4f design extraction"):
    15	
    16	- **Main doublet**: LACX 4f7/2 (free α/β/m — "FitAllFree" expert practice)
    17	  + 4f5/2 amplitude- and shape-linked at the spin-orbit splitting.
    18	- **Satellite doublet**: the U(IV) shake-up satellite rides BOTH mains — one
    19	  Voigt pair (sat7/2 offset-linked to the main; sat5/2 linked to sat7/2 at
    20	  the same splitting).  This one pair explains both observed satellites
    21	  (main+~6.3 eV and main+~17.2 eV = 6.3 + Δso).
    22	- Everything fits JOINTLY in one window; N 1s overlap is handled by
    23	  composing this module with the N 1s module via ``resolve`` (spec §2).
    24	
    25	Safeguards (spec §3.2, retained):
    26	- **Bounded asymmetry**: LACX α/β confined to a labeled-set-calibrated
    27	  window so the tail cannot silently absorb a genuinely separable feature.
    28	- The residual/proposal pass (engine-level) flags unexplained tail
    29	  structure as a possible separate component without forcing
    30	  over-parameterization.
    31	"""
    32	
    33	from __future__ import annotations
    34	
    35	from typing import Optional
    36	
    37	from ..grammar import (
    38	    BackgroundType,
    39	    CandidateModel,
    40	    ComponentSlot,
    41	    LineShape,
    42	    Phase,
    43	)
    44	from . import register_region
    45	
    46	REGION = "U 4f"
    47	
    48	# ── Constants (cited or flagged) ────────────────────────────────────────────
    49	
    50	# Spin-orbit splitting: 10.8–10.9 eV — VERIFIED (Ilton & Bagus 2011,
    51	# 10.1002/sia.3836; NIST SRD 20 gives 10.8, see data/xps/elements-actinides.json
    52	# U-4f7/2.spin_orbit).  Expert fits use 10.90 exactly.  Bounded, not fixed,
    53	# so small calibration deviations remain expressible.
    54	U4F_SPLITTING_RANGE = (10.75, 10.95)
    55	
    56	# Theoretical 4f7/2:4f5/2 area ratio 4:3 → 0.75 — VERIFIED (Bagus et al.,
    57	# 10.1063/1.4846135; NIST SRD 20 area_ratio 0.75).  Expert fits use a
    58	# RELAXED empirical ratio 0.65–0.75 (spec §3.2: "relaxed empirical ratio,
    59	# not a contradiction").  Default 0.75, bounded relaxation; the bounds are
    60	# UNVERIFIED-empirical (labeled set ± margin).
    61	U4F_RATIO_DEFAULT = 0.75
    62	U4F_RATIO_RANGE = (0.60, 0.85)
    63	
    64	# 4f7/2 BE window (corrected frame): inside the NIST-curated, oxidation-
    65	# widened expected region 375.5–383.0 eV (data/xps/elements-actinides.json,
    66	# nist-srd-20; metal nominal 377.3, real samples oxidized → higher).
    67	# Tightened to the U(IV)-like practice of the labeled set (379.5–380.6):
    68	# UNVERIFIED-calibration widths around cited anchors.
    69	U4F72_WINDOW = (378.0, 382.5)
    70	# 4f5/2 fallback window = 7/2 window + splitting (matching only; the fitted
    71	# center is expression-driven).
    72	U4F52_WINDOW = (388.75, 393.45)
    73	
    74	# Main FWHM range — UNVERIFIED-empirical (labeled set 2.44–2.74 eV).
    75	U4F_MAIN_FWHM_RANGE = (1.5, 3.5)
    76	
    77	# Bounded-asymmetry safeguard (spec §3.2): LACX exponents confined around
    78	# the labeled set (α 0.96–1.24, β 2.23–2.85) with margin.  UNVERIFIED-
    79	# empirical — deliberately narrower than the generic (0.1, 5.0) so the tail
    80	# cannot silently absorb a separable overlapping feature; the residual pass
    81	# flags what the bounded tail cannot express.
    82	U4F_LACX_ALPHA_RANGE = (0.5, 2.0)
    83	U4F_LACX_BETA_RANGE = (1.0, 4.5)
    84	# Gaussian kernel width in DATA POINTS (labeled set 0–8.2) — UNVERIFIED.
    85	U4F_LACX_M_RANGE = (0.0, 100.0)
    86	
    87	# Shake-up satellite offset from its main line: literature U(IV)
    88	# satellite-to-main separation ≈ 6.8–7.1 eV (Ilton & Bagus 2011; Schindler
    89	# et al., GCA 73 (2009) 2488, 10.1016/j.gca.2009.02.008); labeled set fits
    90	# 6.07–6.38 eV.  Envelope brackets both — UNVERIFIED-calibration.
    91	U4F_SAT_OFFSET_RANGE = (5.5, 8.5)
    92	# Satellite-PAIR separation window for the free-separation candidates: the
    93	# labeled set fits the pair 11.2 eV apart while the core splitting is 10.9
    94	# (satellite separations need not track the core splitting) — bracketed
    95	# around both; UNVERIFIED-calibration.
    96	U4F_SATPAIR_SEP_RANGE = (10.5, 12.0)
    97	# Satellite width — UNVERIFIED-empirical (labeled set 2.09–3.30 eV).
    98	U4F_SAT_FWHM_RANGE = (1.5, 4.5)
    99	# Satellite absolute fallback windows: DERIVED from the cited/flagged
   100	# constants above (main window ± satellite offsets; used for slot MATCHING
   101	# only — fitted centers are expression-driven off the mains).
   102	U4F_SAT72_WINDOW = (U4F72_WINDOW[0] + U4F_SAT_OFFSET_RANGE[0],
   103	                    U4F72_WINDOW[1] + U4F_SAT_OFFSET_RANGE[1])
   104	U4F_SAT52_WINDOW = (U4F_SAT72_WINDOW[0] + U4F_SATPAIR_SEP_RANGE[0],
   105	                    U4F_SAT72_WINDOW[1] + U4F_SATPAIR_SEP_RANGE[1])
   106	
   107	# Background: the labeled U 4f fits all use the 'smart' (constrained
   108	# Shirley) background — adopted to match expert practice; UNVERIFIED
   109	# methodological choice (plain Shirley is the spec default elsewhere).
   110	U4F_BACKGROUND = BackgroundType.SMART
   111	
   112	
   113	class U4fModule:
   114	    region = REGION
   115	
   116	    def provenance(self) -> list[dict]:
   117	        return [
   118	            {"constant": "spin_orbit_splitting_ev", "value": list(U4F_SPLITTING_RANGE),
   119	             "status": "VERIFIED",
   120	             "source": "Ilton & Bagus 2011 DOI 10.1002/sia.3836 (10.8–10.9); "
   121	                       "NIST SRD 20 via data/xps/elements-actinides.json (10.8)"},
   122	            {"constant": "area_ratio_default", "value": U4F_RATIO_DEFAULT,
   123	             "status": "VERIFIED",
   124	             "source": "4:3 theoretical, Bagus DOI 10.1063/1.4846135; NIST SRD 20"},
   125	            {"constant": "area_ratio_relaxation", "value": list(U4F_RATIO_RANGE),
   126	             "status": "UNVERIFIED", "source": "labeled-set bounds (0.65–0.75 fitted)"},
   127	            {"constant": "asymmetry_origin", "value": "5f2 multiplet/final-state",
   128	             "status": "VERIFIED", "source": "Ilton & Bagus 2011 — supports the "
   129	                                             "asymmetric-envelope model (spec §3.2)"},
   130	            {"constant": "main72_window_ev", "value": list(U4F72_WINDOW),
   131	             "status": "UNVERIFIED",
   132	             "source": "within NIST-curated oxidation-widened region "
   133	                       "(375.5–383.0, data/xps); widths labeled-set calibration"},
   134	            {"constant": "lacx_alpha_range", "value": list(U4F_LACX_ALPHA_RANGE),
   135	             "status": "UNVERIFIED", "source": "bounded-asymmetry safeguard, "
   136	                                               "labeled-set calibration"},
   137	            {"constant": "lacx_beta_range", "value": list(U4F_LACX_BETA_RANGE),
   138	             "status": "UNVERIFIED", "source": "same"},
   139	            {"constant": "lacx_m_range", "value": list(U4F_LACX_M_RANGE),
   140	             "status": "UNVERIFIED",
   141	             "source": "Gaussian kernel width in DATA POINTS — "
   142	                       "labeled-set calibration (labeled set 0–8.2)"},
   143	            {"constant": "satellite_offset_ev", "value": list(U4F_SAT_OFFSET_RANGE),
   144	             "status": "CONDITIONAL",
   145	             "source": "lit 6.8–7.1 (Ilton & Bagus 2011; Schindler 2009 "
   146	                       "10.1016/j.gca.2009.02.008); labeled set 6.07–6.38 — "
   147	                       "envelope brackets both"},
   148	            {"constant": "satellite_pair_separation_ev",
   149	             "value": list(U4F_SATPAIR_SEP_RANGE), "status": "UNVERIFIED",
   150	             "source": "labeled-set finding: pair separation ~11.2 ≠ Δso"},
   151	            {"constant": "satellite_fwhm_ev", "value": list(U4F_SAT_FWHM_RANGE),
   152	             "status": "UNVERIFIED",
   153	             "source": "UNVERIFIED-empirical (labeled set 2.09–3.30 eV)"},
   154	            {"constant": "main_fwhm_range_ev", "value": list(U4F_MAIN_FWHM_RANGE),
   155	             "status": "UNVERIFIED", "source": "labeled-set calibration"},
   156	            {"constant": "background", "value": "smart",
   157	             "status": "UNVERIFIED", "source": "expert practice for this data set"},
   158	        ]
   159	
   160	    def diagnostic_windows(self) -> dict[str, tuple[float, float]]:
   161	        return {
   162	            "main_72": U4F72_WINDOW,
   163	            "main_52": U4F52_WINDOW,
   164	            "satellite_72": U4F_SAT72_WINDOW,
   165	            "satellite_52": U4F_SAT52_WINDOW,
   166	        }
   167	
   168	    def build_candidates(
   169	        self, phase: Phase, oxidation_state: Optional[str] = None
   170	    ) -> list[CandidateModel]:
   171	        """
   172	        Candidates (a controlled ladder of satellite-pair freedom, so model
   173	        comparison can isolate WHICH freedom the data pays for — Codex
   174	        Stage-3 finding #1):
   175	
   176	        - ``U0_mains``            — main doublet only (reduced model for IC)
   177	        - ``U1_mains_satpair``    — + satellite doublet locked to the core
   178	                                    splitting (shape + amplitude tied)
   179	        - ``U1b_mains_satpair_freesep`` — satellite doublet with FREE pair
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
   286	                           background=U4F_BACKGROUND,
   287	                           slots=(main_72, main_52, sat_72, sat_52_freesep)),
   288	            CandidateModel(name="U2_mains_satfree", background=U4F_BACKGROUND,
   289	                           slots=(main_72, main_52, sat_72_free, sat_52_free)),
   290	        ]
   291	
   292	
   293	register_region(U4fModule())

codex
The region docs line up with the “honesty” split so far: B1s/N1s/Cl2p shared widths really are labeled-set calibration only, while Cl2p free-width and U4f mains have the cited physical mechanism in-module. I’m now checking this mechanically across every registered region file and every candidate variant, because the likely failure mode would be a missed variant that shares a role name but not the same slot object.
exec
/bin/zsh -lc 'rg --files autofit/regions' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/regions/u4f.py
autofit/regions/n1s.py
autofit/regions/b1s.py
autofit/regions/c1s.py
autofit/regions/__init__.py
autofit/regions/cl2p.py

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '740,855p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc 'rg -n "''^[A-Z0-9_]+.*FWHM|fwhm_range=.*'"\\(|fwhm_range=[A-Z]|ComponentSlot\\(\" autofit/regions" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/regions/u4f.py:75:U4F_MAIN_FWHM_RANGE = (1.5, 3.5)
autofit/regions/u4f.py:98:U4F_SAT_FWHM_RANGE = (1.5, 4.5)
autofit/regions/u4f.py:197:            return ComponentSlot(
autofit/regions/n1s.py:35:N1S_FWHM_RANGE = (0.7, 2.5)       # UNVERIFIED-empirical (exemplar 1.05 eV)
autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
autofit/regions/n1s.py:79:            fwhm_range=N1S_FWHM_RANGE,
autofit/regions/n1s.py:82:        ag_main = ComponentSlot(
autofit/regions/n1s.py:85:            fwhm_range=N1S_FWHM_RANGE,
autofit/regions/b1s.py:49:B1S_FWHM_RANGE = (1.2, 2.5)
autofit/regions/b1s.py:92:            return ComponentSlot(
autofit/regions/b1s.py:95:                fwhm_range=B1S_FWHM_RANGE,
autofit/regions/c1s.py:159:_MAIN_FWHM_BY_MATERIAL = {
autofit/regions/c1s.py:165:_SHARED_CONTAM_FWHM = "shared_contamination_fwhm"
autofit/regions/c1s.py:309:            return ComponentSlot(
autofit/regions/c1s.py:347:                   fwhm_range=None) -> ComponentSlot:
autofit/regions/cl2p.py:54:CL2P_FWHM_RANGE = (1.2, 2.2)        # UNVERIFIED-empirical (labeled 1.65–1.80)
autofit/regions/cl2p.py:62:CL2P_12_FWHM_EXCESS_RANGE = (0.0, 0.8)
autofit/regions/cl2p.py:64:CL2P_12_FWHM_RANGE = (CL2P_FWHM_RANGE[0],
autofit/regions/cl2p.py:143:            return ComponentSlot(
autofit/regions/cl2p.py:146:                fwhm_range=CL2P_FWHM_RANGE,
autofit/regions/cl2p.py:154:                return ComponentSlot(
autofit/regions/cl2p.py:157:                    fwhm_range=CL2P_12_FWHM_RANGE,
autofit/regions/cl2p.py:166:            return ComponentSlot(
autofit/regions/cl2p.py:169:                fwhm_range=CL2P_FWHM_RANGE,

exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '120,195p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   120	    per-parameter fixes/bounds instead of LA-specific fields.
   121	    """
   122	    role: str
   123	    region: str
   124	    phase_id: str
   125	    be_window: tuple[float, float]
   126	    line_shape: LineShape
   127	    fwhm_range: tuple[float, float]
   128	
   129	    # Offset-linkage (satellites, chemically-shifted contaminants):
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

2026-07-20T17:50:06.911423Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '585,615p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   585	    s: ComponentSlot,
   586	    rename: dict[str, str],
   587	    shared_rename: dict[str, str],
   588	) -> ComponentSlot:
   589	    """Rewrite role / linked_to / fwhm_linked_to under the region prefix."""
   590	    fwhm_link = s.fwhm_linked_to
   591	    if fwhm_link is not None:
   592	        # fwhm_linked_to may reference either a shared param or another
   593	        # slot's parameter name (prefix-based); rewrite whichever matches.
   594	        if fwhm_link in shared_rename:
   595	            fwhm_link = shared_rename[fwhm_link]
   596	        else:
   597	            for old, new in rename.items():
   598	                old_prefix = _slot_param_prefix(old)
   599	                if fwhm_link.startswith(old_prefix):
   600	                    fwhm_link = _slot_param_prefix(new) + fwhm_link[len(old_prefix):]
   601	                    break
   602	    return ComponentSlot(
   603	        role=rename[s.role],
   604	        region=s.region,
   605	        phase_id=s.phase_id,
   606	        be_window=s.be_window,
   607	        line_shape=s.line_shape,
   608	        fwhm_range=s.fwhm_range,
   609	        linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None,
   610	        linked_offset_range=s.linked_offset_range,
   611	        area_ratio=s.area_ratio,
   612	        area_ratio_range=s.area_ratio_range,
   613	        fixed_params=s.fixed_params,
   614	        param_ranges=s.param_ranges,
   615	        fwhm_linked_to=fwhm_link,

exec
/bin/zsh -lc 'git show 5070662''^:autofit/engine.py | nl -ba | sed -n '"'753,845p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-M3NEJYjo' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-EsJqIHh1' (errno=Operation not permitted)
   753	def _unphysical_width_flags(
   754	    components: "list[FittedComponent]", model: CandidateModel
   755	) -> list[str]:
   756	    """Fitted components whose width reaches the ordinary physical FWHM
   757	    ceiling (:data:`FWHM_MAX_ORDINARY_EV`) with NO known-broad justification.
   758	
   759	    A slot whose grammar-declared ``fwhm_range`` maximum EXCEEDS the ordinary
   760	    cap is grammar-sanctioned-broad (C 1s π→π* satellite 5.5, U 4f mains 3.5,
   761	    B 1s 2.5, …) and is EXEMPT — its width is region physics, cited in the
   762	    region module, not an unphysical stretch.  Any other slot — contamination,
   763	    the aliphatic main, and the region-``unassigned`` F1 pre-seed / F2-F3
   764	    proposal slots (all capped AT the ordinary ceiling) — that fits at/above
   765	    the ceiling is flagged: the optimizer wanted a wider (fatter) peak than an
   766	    ordinary component physically has, the cap held it at the limit, and the
   767	    decomposition must be reported low-confidence (routes to the CONDITIONAL
   768	    tier via rank_and_filter) rather than silently accepted.  Region-agnostic:
   769	    the exemption is driven entirely by each slot's own declared range, so no
   770	    region's cited widths are ever mis-flagged.
   771	    """
   772	    ranges = {s.role: s.fwhm_range for s in model.slots}
   773	    flags: list[str] = []
   774	    for c in components:
   775	        rng = ranges.get(c.slot_role)
   776	        if rng is None:
   777	            continue
   778	        declared_lo, declared_hi = rng
   779	        # EFFECTIVE width (Stage-2 PHYSICAL bar): DS+G's width lives in TWO
   780	        # params — beta (Lorentzian HWHM, eV) and m_gauss (Gaussian FWHM;
   781	        # what comp.fwhm carries) — so the checks below must see the
   782	        # convolved width, not the Gaussian part alone (a component could
   783	        # otherwise be ~3+ eV wide while every width check reads 1.0:
   784	        # exactly the 'neighbor broadened to hide a missed peak' channel).
   785	        # Olivero & Longbothum 1977 Voigt-FWHM approximation (0.02%).
   786	        eff_fwhm = c.fwhm
   787	        if c.line_shape is LineShape.DS_G:
   788	            f_l = 2.0 * float(c.shape_params.get("beta", 0.0))
   789	            eff_fwhm = 0.5346 * f_l + np.sqrt(0.2166 * f_l ** 2 + c.fwhm ** 2)
   790	            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and \
   791	                    declared_hi <= FWHM_MAX_ORDINARY_EV:
   792	                flags.append(
   793	                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
   794	                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (DS+G "
   795	                    f"β={c.shape_params.get('beta', 0.0):.2f} + "
   796	                    f"m={c.fwhm:.2f}; no known-broad justification)")
   797	                continue
   798	        elif c.line_shape is LineShape.ASYM_GL:
   799	            # asym-GL broadens its high-BE side to fwhm×(1+asymmetry)
   800	            # (fitting.py convention) — the MEAN effective width
   801	            # fwhm×(1+asym/2) closes the remaining papering-over channel
   802	            # (Codex Stage-2 review, run A MAJOR).
   803	            asym = float(c.shape_params.get("asymmetry", 0.0))
   804	            eff_fwhm = c.fwhm * (1.0 + 0.5 * asym)
   805	            if eff_fwhm >= FWHM_MAX_ORDINARY_EV and \
   806	                    declared_hi <= FWHM_MAX_ORDINARY_EV:
   807	                flags.append(
   808	                    f"{c.slot_role}:effective fwhm={eff_fwhm:.2f}eV≥"
   809	                    f"{FWHM_MAX_ORDINARY_EV:.1f}eV ordinary cap (asym-GL "
   810	                    f"fwhm={c.fwhm:.2f}×(1+{asym:.2f}/2); no known-broad "
   811	                    "justification)")
   812	                continue
   813	        # detection-family slots (scale-relative ceilings, usually > the
   814	        # ordinary cap): a component at ≥ DETECTION_WIDTH_ABSORB_FRACTION
   815	        # of its own ceiling (= 1.75× the DETECTED width via the 2.5×
   816	        # ceiling) is absorbing neighboring intensity — the papering-over
   817	        # signature in transferable units.
   818	        if c.slot_role.startswith("detected_peak_"):
   819	            if eff_fwhm >= DETECTION_WIDTH_ABSORB_FRACTION * declared_hi:
   820	                flags.append(
   821	                    f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥"
   822	                    f"{DETECTION_WIDTH_ABSORB_FRACTION:.2f}×ceiling "
   823	                    f"({declared_hi:.2f}eV) — ~1.75× its detected width; "
   824	                    "likely absorbing a neighbor")
   825	            continue
   826	        if declared_hi > FWHM_MAX_ORDINARY_EV:
   827	            continue                       # grammar-sanctioned-broad slot
   828	        # pegging the ordinary ceiling — same 1%-of-range tol as boundary
   829	        # detection, so a component held AT the 2.0 cap is caught
   830	        tol = 0.01 * (declared_hi - declared_lo) if declared_hi > declared_lo else 0.0
   831	        if eff_fwhm >= FWHM_MAX_ORDINARY_EV - tol:
   832	            flags.append(
   833	                f"{c.slot_role}:fwhm={eff_fwhm:.2f}eV≥{FWHM_MAX_ORDINARY_EV:.1f}eV "
   834	                "ordinary cap (no known-broad justification)")
   835	    return flags
   836	
   837	
   838	def fit_candidate(
   839	    x: np.ndarray,
   840	    y: np.ndarray,
   841	    weights: np.ndarray,
   842	    model: CandidateModel,
   843	    initial_params: Optional[Parameters] = None,
   844	    max_nfev: int = FIT_CANDIDATE_MAX_NFEV,
   845	    fit_full_window: bool = False,

exec
/bin/zsh -lc 'git diff-tree --no-commit-id --name-only -r 5070662' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-zlHJThde' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZQSYjW3N' (errno=Operation not permitted)
autofit/engine.py
autofit/grammar.py
autofit/regions/b1s.py
autofit/regions/c1s.py
autofit/regions/cl2p.py
autofit/regions/n1s.py
autofit/regions/u4f.py
tests/autofit/test_broad_justification.py
tests/autofit/test_preseed_dominants.py

exec
/bin/zsh -lc "nl -ba tests/autofit/test_preseed_dominants.py | sed -n '150,225p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   150	    # and dominant recovered without a fat peak
   151	    for p in res.peaks:
   152	        if "satellite" in p["role"]:
   153	            continue
   154	        assert p["fwhm"] <= eng.FWHM_MAX_ORDINARY_EV + 1e-6, \
   155	            f"{p['role']} fwhm {p['fwhm']} exceeds the ordinary cap"
   156	
   157	
   158	# ── Physical FWHM caps (2026-07-08) ────────────────────────────────────────
   159	
   160	def test_unphysical_width_flags_helper():
   161	    """The width-flag helper: an ordinary slot pegging the 2.0 cap is
   162	    flagged; a narrow main and a grammar-sanctioned-broad slot (explicit
   163	    ``broad_justification``, e.g. a satellite) are NOT.
   164	
   165	    2026-07-20 (Unit A, broad_justification refactor): the exemption used
   166	    to be inferred from ``fwhm_range``'s own magnitude (declared max >
   167	    2.0 eV) — this test originally built its synthetic "satellite_pi" slot
   168	    with only a wide range and no explicit vouch, which is now correctly
   169	    NOT exempt (that numeric-only inference is exactly the bug the MIXED
   170	    material-class Codex review caught: widening a bound for an unrelated
   171	    reason silently asserted "this is vouched physics" as a side effect).
   172	    Updated to set broad_justification explicitly, matching how every real
   173	    region module now grants this exemption."""
   174	    from autofit.grammar import (CandidateModel, ComponentSlot, LineShape,
   175	                                 BackgroundType)
   176	    from autofit.engine import FittedComponent
   177	
   178	    def slot(role, lo, hi, broad_justification=None):
   179	        return ComponentSlot(role=role, region="r", phase_id="p",
   180	                             be_window=(199., 201.), line_shape=LineShape.PSEUDO_VOIGT,
   181	                             fwhm_range=(lo, hi),
   182	                             broad_justification=broad_justification)
   183	
   184	    def comp(role, fwhm):
   185	        return FittedComponent(slot_role=role, position=200.0, fwhm=fwhm,
   186	                               amplitude=1e3, shape_params={})
   187	
   188	    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(
   189	        slot("contamination_CO", 0.8, 2.0), slot("main_graphitic", 0.4, 1.2),
   190	        slot("satellite_pi", 1.0, 5.5,
   191	             broad_justification="synthetic: pi->pi* shake-up, physically broad"),
   192	        slot("proposed_peak_0", 0.5, 2.0)))
   193	    flags = eng._unphysical_width_flags(
   194	        [comp("contamination_CO", 1.99), comp("main_graphitic", 1.2),
   195	         comp("satellite_pi", 5.16), comp("proposed_peak_0", 2.0)], m)
   196	    flagged_roles = {f.split(":")[0] for f in flags}
   197	    assert flagged_roles == {"contamination_CO", "proposed_peak_0"}
   198	    # a satellite at 5.16 (explicitly vouched-broad slot) is NEVER flagged —
   199	    # this is exactly the "wide contamination" the fat-peak report was
   200	    # really about
   201	    assert not any("satellite" in f for f in flags)
   202	    # a component comfortably under the cap → no flag at all
   203	    assert eng._unphysical_width_flags([comp("contamination_CO", 1.5)], m) == []
   204	
   205	
   206	def test_unphysical_width_flags_wide_range_alone_no_longer_exempts():
   207	    """The bug this refactor fixes, pinned directly: a slot with a WIDE
   208	    declared fwhm_range but NO broad_justification must be flagged when it
   209	    fits wide — the bound's magnitude alone must never grant exemption.
   210	    Mirrors the real MIXED material-class scenario (a relaxed contamination
   211	    ceiling with no physics vouch) at the helper level, region-agnostic."""
   212	    from autofit.grammar import (CandidateModel, ComponentSlot, LineShape,
   213	                                 BackgroundType)
   214	    from autofit.engine import FittedComponent
   215	
   216	    slot = ComponentSlot(role="wide_unvouched", region="r", phase_id="p",
   217	                         be_window=(199., 201.), line_shape=LineShape.PSEUDO_VOIGT,
   218	                         fwhm_range=(0.8, 15.0))
   219	    m = CandidateModel(name="M", background=BackgroundType.LINEAR, slots=(slot,))
   220	    comp = FittedComponent(slot_role="wide_unvouched", position=200.0,
   221	                           fwhm=8.0, amplitude=1e3, shape_params={})
   222	    flags = eng._unphysical_width_flags([comp], m)
   223	    assert flags, "a wide-but-unvouched slot must be flagged, not exempted"
   224	
   225	

2026-07-20T17:50:14.761714Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '615,635p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   615	        fwhm_linked_to=fwhm_link,
   616	        share_parent_params=s.share_parent_params,
   617	        fwhm_excess_range=s.fwhm_excess_range,
   618	    )
   619	
   620	
   621	def _slot_param_prefix(role: str) -> str:
   622	    """Must match engine._slot_prefix — kept here to rewrite fwhm links."""
   623	    return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"

2026-07-20T17:50:19.374461Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
I found a propagation risk in the grammar composition helper: the new field is present on base slots, but `_prefix_slot()` currently reconstructs `ComponentSlot` without copying it. I’m checking whether `resolve()` actually uses this path for multi-region or multi-phase candidates; if so, this is a concrete missed-exemption regression, not just a style issue.
exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '430,620p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'rg -n "def resolve|_prefix_slot|_prefix_candidate|compose|prefix" autofit/grammar.py tests/autofit' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/grammar.py:22:all requested regions are composed into joint candidates fit together in the
autofit/grammar.py:214:    """resolve() output: the composed, admissible candidate set."""
autofit/grammar.py:264:def resolve(
autofit/grammar.py:326:    # composed slot roles stay unique across phases.
autofit/grammar.py:465:    # Role-prefix collision guard (Codex Stage-2 re-review finding #2): the
autofit/grammar.py:467:    # phase ids like 'B-4C' and 'B4C' would collapse into one role prefix and
autofit/grammar.py:482:        composed: list[CandidateModel] = []
autofit/grammar.py:484:        composed = per_request_candidates[0]
autofit/grammar.py:486:        composed = _compose_joint_candidates(slugs, per_request_candidates)
autofit/grammar.py:488:            f"joint co-fit of {slugs}: {len(composed)} composed candidates"
autofit/grammar.py:494:            "windows or candidates to compose)")
autofit/grammar.py:499:        candidates=composed,
autofit/grammar.py:546:def _compose_joint_candidates(
autofit/grammar.py:552:    one shared spectral window.  Slot roles are prefixed with the request's
autofit/grammar.py:557:    composed: list[CandidateModel] = []
autofit/grammar.py:575:        composed.append(CandidateModel(
autofit/grammar.py:581:    return composed
autofit/grammar.py:589:    """Rewrite role / linked_to / fwhm_linked_to under the region prefix."""
autofit/grammar.py:593:        # slot's parameter name (prefix-based); rewrite whichever matches.
autofit/grammar.py:598:                old_prefix = _slot_param_prefix(old)
autofit/grammar.py:599:                if fwhm_link.startswith(old_prefix):
autofit/grammar.py:600:                    fwhm_link = _slot_param_prefix(new) + fwhm_link[len(old_prefix):]
autofit/grammar.py:621:def _slot_param_prefix(role: str) -> str:
autofit/grammar.py:622:    """Must match engine._slot_prefix — kept here to rewrite fwhm links."""
tests/autofit/test_u4f_parity_gate.py:100:    """The U-in-BN joint window: U 4f grammar composed with N 1s (spec §2),
tests/autofit/test_resolver.py:46:    assert g.diagnostic_windows  # region-prefixed labels
tests/autofit/test_resolver.py:138:    # region-slug prefixes keep roles unique; linkage rewritten
tests/autofit/test_fit_full_window_option.py:35:                            _slot_prefix, fit_candidate,
tests/autofit/test_fit_full_window_option.py:51:    par = params[f"{_slot_prefix(role)}center"]
tests/autofit/test_fit_full_window_option.py:56:    return params[f"{_slot_prefix(role)}center"].value
tests/autofit/test_fit_full_window_option.py:180:    offset_name = f"{_slot_prefix('main_p12')}offset"
tests/autofit/test_preseed_dominants.py:292:    prefix = eng._slot_prefix(role)
tests/autofit/test_preseed_dominants.py:298:    p.add(f"{prefix}center", value=200.0, min=199.0, max=201.0)      # interior
tests/autofit/test_preseed_dominants.py:299:    p.add(f"{prefix}amplitude", value=5000.0, min=0.0, max=1e5)      # interior
tests/autofit/test_preseed_dominants.py:300:    p.add(f"{prefix}fwhm", value=2.0, min=0.5, max=2.0)             # fwhm@max
tests/autofit/test_preseed_dominants.py:301:    p.add(f"{prefix}gl_ratio", value=1.0, min=0.0, max=1.0)         # shape endpoint
tests/autofit/test_preseed_dominants.py:305:    p[f"{prefix}center"].set(value=199.0)          # drifted to the window edge
tests/autofit/test_preseed_dominants.py:382:    # roles stay unique across rounds (param-prefix collision guard)
tests/autofit/test_preseed_dominants.py:393:    prefix.  This pins the helper directly on that exact gap."""
tests/autofit/test_structural_fallback.py:194:        sourced_prefixes = ("fit_physics", "cited:", "reference:")
tests/autofit/test_structural_fallback.py:197:            if const.startswith(sourced_prefixes):

 succeeded in 0ms:
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
   589	    """Rewrite role / linked_to / fwhm_linked_to under the region prefix."""
   590	    fwhm_link = s.fwhm_linked_to
   591	    if fwhm_link is not None:
   592	        # fwhm_linked_to may reference either a shared param or another
   593	        # slot's parameter name (prefix-based); rewrite whichever matches.
   594	        if fwhm_link in shared_rename:
   595	            fwhm_link = shared_rename[fwhm_link]
   596	        else:
   597	            for old, new in rename.items():
   598	                old_prefix = _slot_param_prefix(old)
   599	                if fwhm_link.startswith(old_prefix):
   600	                    fwhm_link = _slot_param_prefix(new) + fwhm_link[len(old_prefix):]
   601	                    break
   602	    return ComponentSlot(
   603	        role=rename[s.role],
   604	        region=s.region,
   605	        phase_id=s.phase_id,
   606	        be_window=s.be_window,
   607	        line_shape=s.line_shape,
   608	        fwhm_range=s.fwhm_range,
   609	        linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None,
   610	        linked_offset_range=s.linked_offset_range,
   611	        area_ratio=s.area_ratio,
   612	        area_ratio_range=s.area_ratio_range,
   613	        fixed_params=s.fixed_params,
   614	        param_ranges=s.param_ranges,
   615	        fwhm_linked_to=fwhm_link,
   616	        share_parent_params=s.share_parent_params,
   617	        fwhm_excess_range=s.fwhm_excess_range,
   618	    )
   619	
   620	

2026-07-20T17:50:31.361735Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python -c \"from autofit.grammar import Phase,MaterialClass,resolve; p=Phase(id='s',material_class=MaterialClass.INSULATOR,regions=('U 4f','N 1s')); g=resolve([p],'U 4f+N 1s'); print(len(g.candidates)); print(g.regions); print(g.notes[:5]);\\nfor cand in g.candidates[:2]: print(cand.name, [(s.role,s.fwhm_range,s.broad_justification is not None) for s in cand.slots])\"" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '250,430p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   250	        return [(regions[0], regions[1])]
   251	    out: list[tuple[str, Optional[str]]] = []
   252	    for r in regions:
   253	        if isinstance(r, str):
   254	            out.append((r, None))
   255	        elif isinstance(r, tuple) and len(r) == 2:
   256	            out.append((str(r[0]), str(r[1])))
   257	        else:
   258	            raise ValueError(
   259	                f"region request must be 'Region' or ('Region', 'phase_id'), got {r!r}"
   260	            )
   261	    return out
   262	
   263	
   264	def resolve(
   265	    phases: list[Phase],
   266	    regions: "list[str | tuple[str, str]] | str",
   267	    oxidation_state: Optional[str] = None,
   268	    target_phases: Optional[dict[str, str]] = None,
   269	    allow_structural_fallback: bool = False,
   270	    cited_values: Optional[list] = None,
   271	) -> CandidateGrammar:
   272	    """
   273	    Compose the candidate grammar for ``regions`` over ``phases``.
   274	
   275	    Parameters
   276	    ----------
   277	    phases          : the sample's phase list (length 1 = single-phase default)
   278	    regions         : region requests for one (possibly joint) fit window.
   279	                      Each request is either a region name (``"C 1s"``) or a
   280	                      phase-qualified ``("B 1s", "BN")`` pair.  The SAME
   281	                      region may appear once per phase — that is how a
   282	                      BN/B4C sample co-fits both phases' B 1s contributions
   283	                      in one window (spec §2: phase-scoped slot families).
   284	    oxidation_state : Layer-C override, forwarded to region modules
   285	    target_phases   : {region: phase_id} disambiguation for UNqualified
   286	                      requests of a region contributed by more than one phase
   287	    allow_structural_fallback : Phase D, OPT-IN (default False keeps every
   288	                      existing caller byte-identical).  A region with no
   289	                      registered module that parses as an element/level in
   290	                      the Z=1..96 table resolves to DERIVED STRUCTURE only
   291	                      (autofit.coverage): zero fit candidates, provenance
   292	                      records for the doublet/singlet structure, ratio
   293	                      expectation, multiplet/conductor flags, and an
   294	                      UNVERIFIED value-None position — 'structure known,
   295	                      positions UNVERIFIED, supply a cited source'.  Such
   296	                      regions are listed in ``CandidateGrammar.
   297	                      structural_only`` and excluded from joint candidate
   298	                      composition.
   299	    cited_values    : optional list of autofit.cited_values.CitedValue —
   300	                      cited empirical values whose matching records ride
   301	                      into the structural provenance (they do NOT build
   302	                      candidates; windows/widths remain curation work).
   303	
   304	    Raises
   305	    ------
   306	    PhaseAmbiguityError : unqualified region in multiple phases w/o a target
   307	    UnknownRegionError  : region not registered, or not covered by any phase
   308	                          (with fallback enabled: also not derivable —
   309	                          unparseable label, unknown element, or an
   310	                          unoccupied subshell)
   311	    """
   312	    from .regions import get_region_module  # local import: avoid cycle
   313	
   314	    requests = _parse_region_requests(regions)
   315	    if not phases:
   316	        raise ValueError("phases must be a non-empty list (single-phase = length 1)")
   317	    if not requests:
   318	        raise ValueError("regions must be a non-empty list")
   319	    target_phases = target_phases or {}
   320	
   321	    ids = [p.id for p in phases]
   322	    if len(set(ids)) != len(ids):
   323	        raise ValueError(f"duplicate phase ids: {ids}")
   324	
   325	    # Region names occurring in >1 request get phase-qualified slugs so the
   326	    # composed slot roles stay unique across phases.
   327	    region_counts: dict[str, int] = {}
   328	    for region, _ in requests:
   329	        region_counts[region] = region_counts.get(region, 0) + 1
   330	
   331	    notes: list[str] = []
   332	    per_request_candidates: list[list[CandidateModel]] = []
   333	    slugs: list[str] = []            # module-backed requests (composition)
   334	    all_slugs: list[str] = []        # module-backed + structural (collision)
   335	    structural_regions: list[str] = []
   336	    diagnostic_windows: dict[str, tuple[float, float]] = {}
   337	    provenance: dict[str, list[dict]] = {}
   338	    used_phase_ids: list[str] = []
   339	    resolved_pairs: set[tuple[str, str]] = set()
   340	
   341	    for region, explicit_phase in requests:
   342	        contributors = [p for p in phases if region in p.regions]
   343	        if not contributors:
   344	            raise UnknownRegionError(
   345	                f"region {region!r} is not contributed by any declared phase "
   346	                f"(phases: {[p.id for p in phases]})"
   347	            )
   348	        if explicit_phase is not None:
   349	            chosen = next((p for p in contributors if p.id == explicit_phase), None)
   350	            if chosen is None:
   351	                raise ValueError(
   352	                    f"request ({region!r}, {explicit_phase!r}): phase does not "
   353	                    f"contribute this region (contributors: "
   354	                    f"{[p.id for p in contributors]})"
   355	                )
   356	        elif len(contributors) > 1:
   357	            tid = target_phases.get(region)
   358	            if tid is None:
   359	                raise PhaseAmbiguityError(
   360	                    f"region {region!r} appears in phases "
   361	                    f"{[p.id for p in contributors]} — request it per-phase "
   362	                    f"(({region!r}, <phase_id>)) or pass "
   363	                    f"target_phases={{{region!r}: <phase_id>}} "
   364	                    "(spec v2.1 §2: region is not a unique key)"
   365	                )
   366	            chosen = next((p for p in contributors if p.id == tid), None)
   367	            if chosen is None:
   368	                raise PhaseAmbiguityError(
   369	                    f"target phase {tid!r} for region {region!r} is not among "
   370	                    f"its contributors {[p.id for p in contributors]}"
   371	                )
   372	        else:
   373	            chosen = contributors[0]
   374	
   375	        pair = (region, chosen.id)
   376	        if pair in resolved_pairs:
   377	            raise ValueError(f"duplicate region request {pair}")
   378	        resolved_pairs.add(pair)
   379	
   380	        slug = region if region_counts[region] == 1 else f"{region}@{chosen.id}"
   381	        try:
   382	            module = get_region_module(region)
   383	        except UnknownRegionError:
   384	            # ── Phase D structural fallback (opt-in) ─────────────────────
   385	            if not allow_structural_fallback:
   386	                raise
   387	            from . import coverage
   388	            try:
   389	                records, s_notes = coverage.structural_provenance(
   390	                    region, cited_values=cited_values)
   391	            except KeyError as exc:
   392	                raise UnknownRegionError(
   393	                    f"region {region!r}: no registered module and no "
   394	                    f"derivable structure — {exc}"
   395	                ) from None
   396	            all_slugs.append(slug)
   397	            structural_regions.append(region)
   398	            used_phase_ids.append(chosen.id)
   399	            provenance[slug] = records
   400	            notes.append(
   401	                f"{slug}: STRUCTURAL FALLBACK (phase {chosen.id!r}, "
   402	                f"{chosen.material_class.value}) — derived structure only")
   403	            notes.extend(f"{slug}: {n}" for n in s_notes)
   404	            if oxidation_state is not None:
   405	                notes.append(
   406	                    f"{slug}: oxidation_state {oxidation_state!r} has no "
   407	                    "effect on a structural-fallback region (Layer C needs "
   408	                    "a region module)")
   409	            # the tiered fit-physics DB exposure rides along here too —
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

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python -c \"from autofit.grammar import Phase,MaterialClass,resolve;\\nfor reg in ['C 1s','B 1s','Cl 2p','N 1s','U 4f']:\\n p=Phase(id='s',material_class=MaterialClass.MIXED if reg=='C 1s' else MaterialClass.INSULATOR,regions=(reg,)); g=resolve([p],reg); print('REG',reg);\\n seen=set();\\n for cand in g.candidates:\\n  for s in cand.slots:\\n   key=(cand.name,s.role,s.fwhm_range,s.broad_justification is not None);\\n   if s.fwhm_range[1]>2.0 or s.broad_justification is not None:\\n    print(cand.name,s.role,s.fwhm_range,'just' if s.broad_justification else 'NOJUST');\\n print()\"" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

2026-07-20T17:50:43.240276Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The propagation path is real: composed candidates go through `_compose_joint_candidates()` and `_retag_slot()`. I’ll run the import check with `python3` instead of `python` to verify the exact runtime behavior and the MIXED contamination scenario.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit.grammar import Phase,MaterialClass,resolve; from autofit.engine import FittedComponent,_unphysical_width_flags; p=Phase(id='s',material_class=MaterialClass.MIXED,regions=('C 1s',)); g=resolve([p],'C 1s'); cand=next(c for c in g.candidates if c.name=='A1_linked'); slot=cand.slot_by_role('contamination_CO'); print(slot.fwhm_range, slot.broad_justification); comp=FittedComponent(slot_role='contamination_CO', position=286.2, fwhm=8.0, amplitude=1000.0, shape_params={}); print(_unphysical_width_flags([comp], cand))\"" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit.grammar import Phase,MaterialClass,resolve; from autofit.engine import FittedComponent,_unphysical_width_flags; p=Phase(id='s',material_class=MaterialClass.INSULATOR,regions=('U 4f','N 1s')); g=resolve([p],['U 4f','N 1s']); cand=next(c for c in g.candidates if c.name.startswith('U0_mains+N0_pv')); slot=next(s for s in cand.slots if s.role.endswith('main_u4f72')); print(slot.role, slot.fwhm_range, slot.broad_justification); comp=FittedComponent(slot_role=slot.role, position=380.0, fwhm=3.0, amplitude=1000.0, shape_params={}, line_shape=slot.line_shape); print(_unphysical_width_flags([comp], cand))\"" in /Users/skyefortier/xps-verify
 exited 1 in 285ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/autofit/engine.py", line 38, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

 exited 1 in 289ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/autofit/engine.py", line 38, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

2026-07-20T17:51:02.856565Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The Python import path is available, but the system `python3` lacks `lmfit`, so direct engine execution is blocked in this sandbox. I can still use `autofit.grammar` for slot construction checks and the engine code itself for the flag condition.
exec
/bin/zsh -lc 'ls -la' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
total 560
drwxr-xr-x   29 skyefortier  staff    928 Jul 20 00:14 .
drwxr-xr-x+  74 skyefortier  staff   2368 Jul 20 11:46 ..
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
drwxr-xr-x   20 skyefortier  staff    640 Jul 20 11:12 autofit
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
drwxr-xr-x  135 skyefortier  staff   4320 Jul 20 11:37 uploads
-rw-r--r--    1 skyefortier  staff   6062 Jul 10 15:28 vgd_parser.py
-rw-r--r--    1 skyefortier  staff  68252 Jul 10 15:28 xps-fitting-tool.html
-rw-r--r--    1 skyefortier  staff  18124 Jul 10 15:28 xps_reference.py

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit.grammar import Phase,MaterialClass,resolve; p=Phase(id='s',material_class=MaterialClass.INSULATOR,regions=('U 4f','N 1s')); g=resolve([p],['U 4f','N 1s']); print(len(g.candidates)); print(g.regions); print(g.notes[:3]); [print(cand.name, [(s.role,s.fwhm_range,s.broad_justification is not None) for s in cand.slots]) for cand in g.candidates[:2]]\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-HzIJqodV' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-feuklBTt' (errno=Operation not permitted)
8
('U 4f', 'N 1s')
["U 4f: phase 's' (insulator), 4 candidates", "N 1s: phase 's' (insulator), 2 candidates", "joint co-fit of ['U 4f', 'N 1s']: 8 composed candidates"]
U0_mains+N0_pv [('U4f__main_u4f72', (1.5, 3.5), False), ('U4f__main_u4f52', (1.5, 3.5), False), ('N1s__main_n1s', (0.7, 2.5), False)]
U0_mains+N0_asymGL [('U4f__main_u4f72', (1.5, 3.5), False), ('U4f__main_u4f52', (1.5, 3.5), False), ('N1s__main_n1s', (0.7, 2.5), False)]

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit.grammar import Phase,MaterialClass,resolve; p=Phase(id='s',material_class=MaterialClass.MIXED,regions=('C 1s',)); g=resolve([p],'C 1s'); cand=next(c for c in g.candidates if c.name=='A1_linked'); slot=cand.slot_by_role('contamination_CO'); print(slot.fwhm_range, slot.broad_justification)\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-7yeaRAPk' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-HFOljjaO' (errno=Operation not permitted)
(0.8, 15.0) None

2026-07-20T17:51:15.902168Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
1. **MAJOR** [autofit/grammar.py](/Users/skyefortier/xps-verify/autofit/grammar.py:602): `_retag_slot()` reconstructs composed/joint-fit slots without copying `s.broad_justification`. Any multi-region composition loses every explicit exemption. Concrete scenario: `resolve([Phase(... regions=("U 4f", "N 1s"))], ["U 4f", "N 1s"])` emits `U4f__main_u4f72` with `fwhm_range=(1.5, 3.5)` and `broad_justification=None`. Under the old numeric rule a 3.0 eV U 4f main was exempt; now `_unphysical_width_flags()` reaches the ordinary-cap check at [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:840) and flags it. This is silent tightening in the explicit U 4f + N 1s co-fit path.

2. **MINOR** [tests/autofit/test_broad_justification.py](/Users/skyefortier/xps-verify/tests/autofit/test_broad_justification.py:36): `EXEMPTION_FIXTURE` is not exhaustive despite claiming to encode every exempt/non-exempt slot. It omits U 4f satellite variants (`U1_mains_satpair`, `U1b_mains_satpair_freesep`, `U2_mains_satfree`) and does not exercise composed candidates, which is exactly where finding #1 escapes. A future or current loss of satellite/co-fit justification is not caught by this safety net.

Other checks: diff scope is limited to the claimed files. C1s MIXED contamination constructs as `(0.8, 15.0)` with `broad_justification=None`; direct engine import was blocked by missing `lmfit`, but reading the code confirms an 8.0 eV non-vouched non-detected slot will flag. The B1s/N1s/Cl2p shared/U4f satellite empirical-only wording matches the module comments; C1s satellite, Cl2p free-width, and U4f mains have the cited mechanisms in-module.

VERDICT: NO-GO
tokens used
75,660
1. **MAJOR** [autofit/grammar.py](/Users/skyefortier/xps-verify/autofit/grammar.py:602): `_retag_slot()` reconstructs composed/joint-fit slots without copying `s.broad_justification`. Any multi-region composition loses every explicit exemption. Concrete scenario: `resolve([Phase(... regions=("U 4f", "N 1s"))], ["U 4f", "N 1s"])` emits `U4f__main_u4f72` with `fwhm_range=(1.5, 3.5)` and `broad_justification=None`. Under the old numeric rule a 3.0 eV U 4f main was exempt; now `_unphysical_width_flags()` reaches the ordinary-cap check at [autofit/engine.py](/Users/skyefortier/xps-verify/autofit/engine.py:840) and flags it. This is silent tightening in the explicit U 4f + N 1s co-fit path.

2. **MINOR** [tests/autofit/test_broad_justification.py](/Users/skyefortier/xps-verify/tests/autofit/test_broad_justification.py:36): `EXEMPTION_FIXTURE` is not exhaustive despite claiming to encode every exempt/non-exempt slot. It omits U 4f satellite variants (`U1_mains_satpair`, `U1b_mains_satpair_freesep`, `U2_mains_satfree`) and does not exercise composed candidates, which is exactly where finding #1 escapes. A future or current loss of satellite/co-fit justification is not caught by this safety net.

Other checks: diff scope is limited to the claimed files. C1s MIXED contamination constructs as `(0.8, 15.0)` with `broad_justification=None`; direct engine import was blocked by missing `lmfit`, but reading the code confirms an 8.0 eV non-vouched non-detected slot will flag. The B1s/N1s/Cl2p shared/U4f satellite empirical-only wording matches the module comments; C1s satellite, Cl2p free-width, and U4f mains have the cited mechanisms in-module.

VERDICT: NO-GO
