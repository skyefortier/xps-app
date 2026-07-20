2026-07-20T18:54:52.960235Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 86 column 5
OpenAI Codex v0.139.0
--------
workdir: /Users/skyefortier/xps-verify
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: high
reasoning summaries: none
session id: 019f80e1-8e98-7f02-9ead-a1e051f34d67
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
I’ll treat this as a targeted code review, not an implementation task. I’m going to inspect the commit, grep all `ComponentSlot` copy paths, and run focused Python/tests where the read-only sandbox permits.
exec
/bin/zsh -lc "rg -n \"ComponentSlot\\(|dataclasses\\.replace\\(|\\breplace\\(\" autofit tests -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/candidates.py:463:        slots.append(ComponentSlot(
tests/test_expand_coverage.py:49:        strip = lambda c: re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip()
autofit/engine.py:1901:        ComponentSlot(
autofit/engine.py:2110:    proposed = ComponentSlot(
autofit/engine.py:2446:        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
autofit/grammar.py:469:    sanitized = [re.sub(r"[^A-Za-z0-9_]", "", s.replace(" ", ""))
autofit/grammar.py:568:            slug = re.sub(r"[^A-Za-z0-9_]", "", slug.replace(" ", ""))
autofit/grammar.py:592:    reconstructing the slot field-by-field: replace() carries every field
autofit/grammar.py:616:    return replace(
tests/autofit/test_sparse_map.py:28:    return ComponentSlot(role=role, region="T", phase_id="t",
autofit/regions/u4f.py:197:            return ComponentSlot(
tests/autofit/test_broad_justification.py:100:# switching _retag_slot to dataclasses.replace(). This fixture exercises the
tests/autofit/test_broad_justification.py:183:    original = ComponentSlot(**sentinel_by_field)
tests/autofit/test_broad_justification.py:276:    wide_no_justification = ComponentSlot(
tests/autofit/test_broad_justification.py:299:    narrow_but_justified = ComponentSlot(
tests/autofit/test_broad_justification.py:317:    s = ComponentSlot(role="r", region="Test", phase_id="s",
tests/autofit/stress_cases.py:108:    return ComponentSlot(role=role, region=REGION, phase_id=PHASE,
tests/autofit/test_cl2p_freewidth.py:131:    return ComponentSlot(role=role, **defaults)
tests/autofit/test_bayesian_real_gate.py:72:    assert ic.diagnostics["winner"].replace("+bfix", "") == \
autofit/regions/c1s.py:309:            return ComponentSlot(
autofit/regions/cl2p.py:143:            return ComponentSlot(
autofit/regions/cl2p.py:154:                return ComponentSlot(
autofit/regions/cl2p.py:166:            return ComponentSlot(
autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
autofit/regions/n1s.py:82:        ag_main = ComponentSlot(
tests/autofit/test_engine_doublet.py:23:    p32 = ComponentSlot(
tests/autofit/test_engine_doublet.py:28:    p12 = ComponentSlot(
tests/autofit/test_engine_doublet.py:127:        return ComponentSlot(
tests/autofit/test_preseed_dominants.py:179:        return ComponentSlot(role=role, region="r", phase_id="p",
tests/autofit/test_preseed_dominants.py:216:    slot = ComponentSlot(role="wide_unvouched", region="r", phase_id="p",
tests/autofit/test_preseed_dominants.py:293:    slot = ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
tests/autofit/test_preseed_dominants.py:335:    promoted = dataclasses.replace(
tests/autofit/test_preseed_dominants.py:397:        return ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
tests/autofit/test_stage2_completeness.py:257:    stab = dataclasses.replace(report.stability, per_slot=bad_slots,
tests/autofit/test_stage2_completeness.py:261:    return dataclasses.replace(report, stability=stab, plausibility=plaus)
tests/autofit/test_stage2_completeness.py:293:    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
tests/autofit/test_stage2_completeness.py:317:    slot = ComponentSlot(role="detected_peak_0", region="unassigned",
tests/autofit/test_stage2_completeness.py:350:    cond = dataclasses.replace(
tests/autofit/test_stage2_completeness.py:369:    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
tests/autofit/test_resolver.py:107:        main = ComponentSlot(
tests/autofit/test_resolver.py:112:        doublet = ComponentSlot(
autofit/regions/b1s.py:92:            return ComponentSlot(
tests/autofit/test_criteria.py:23:    return ComponentSlot(role=role, region="T", phase_id="t",
tests/autofit/test_fit_full_window_option.py:41:    return ComponentSlot(role=role, region=region, phase_id="p",
tests/autofit/test_bayesian_method.py:29:    return ComponentSlot(role=role, region="T", phase_id="t",
tests/autofit/test_fit_physics.py:48:    src = open(GEN).read().replace(
tests/autofit/test_fit_physics.py:50:        f'OUT = {str(out)!r}').replace(
tests/autofit/test_c1s_mixed_material_class.py:271:    conditional_report = dataclasses.replace(

exec
/bin/zsh -lc 'git show --no-ext-diff --unified=80 ad7e668 -- autofit/grammar.py tests/autofit/test_broad_justification.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-VQc3mlVc' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ffc9DUQ2' (errno=Operation not permitted)
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
@@ -1,110 +1,110 @@
 """
 Composable grammar for the autofit engine (spec v2.1 §2).
 
 ``resolve(phases, regions, ...)`` → :class:`CandidateGrammar`.
 
 Three layers:
 
 - **Layer A** — material class (per phase): lineshape family admissibility,
   charge strategy, reference.
 - **Layer B** — region/element module (``autofit.regions``): doublet
   Δso/ratio, BE windows, allowed lineshapes, satellites, core-hole width.
 - **Layer C** — oxidation-state override (multiplet fingerprint, BE shift).
   Seam only in Stage 2 — region modules may accept it, none require it.
 
 Multi-phase model (v2 B1 fix): a ``phases`` list, never a pairwise
 ``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
 ``phase_id``; when the same region is contributed by more than one phase the
 caller MUST disambiguate with ``target_phases`` (Codex precondition 2 — a
 region is not a unique key).
 
 Multi-region co-fit ([Skye]): ``regions`` is multi-valued; the grammars of
 all requested regions are composed into joint candidates fit together in the
 shared window (e.g. U 4f + N 1s overlap).
 """
 
 from __future__ import annotations
 
 import itertools
 import re
-from dataclasses import dataclass, field
+from dataclasses import dataclass, field, replace
 from enum import Enum
 from typing import Optional
 
 from .fit_physics import provenance_entries as _fit_physics_provenance
 
 __all__ = [
     "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
     "CandidateModel", "CandidateGrammar", "PhaseAmbiguityError",
     "UnknownRegionError", "resolve", "BACKEND_SHAPE",
 ]
 
 
 class LineShape(Enum):
     GAUSSIAN = "gaussian"
     LORENTZIAN = "lorentzian"
     PSEUDO_VOIGT = "pseudo_voigt"    # backend pseudo_voigt_gl
     ASYM_GL = "asym_gl"              # backend asymmetric_gl
     DS = "doniach_sunjic"
     DS_G = "ds_g"                    # DS core ⊗ Gaussian (fitalg's "LA_ASYMMETRIC")
     LACX = "la_casaxps"              # true CasaXPS LA(α, β, m)
 
 
 # LineShape → fitting.py _SHAPE_FUNCS key
 BACKEND_SHAPE: dict[LineShape, str] = {
     LineShape.GAUSSIAN: "gaussian",
     LineShape.LORENTZIAN: "lorentzian",
     LineShape.PSEUDO_VOIGT: "pseudo_voigt_gl",
     LineShape.ASYM_GL: "asymmetric_gl",
     LineShape.DS: "doniach_sunjic",
     LineShape.DS_G: "ds_g",
     LineShape.LACX: "la_casaxps",
 }
 
 # Shapes whose asymmetric tail encodes physics (metallic screening or an
 # unresolvable multiplet envelope) — admissible only where Layer A allows.
 ASYMMETRIC_SHAPES = frozenset({LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX})
 
 
 class BackgroundType(Enum):
     SHIRLEY = "shirley"
     SMART = "smart"
     SMART_EXP = "smart_exp"      # Avantage-style constrained Shirley
     LINEAR = "linear"
     TOUGAARD = "tougaard"
 
 
 class MaterialClass(Enum):
     CONDUCTOR = "conductor"
     SEMICONDUCTOR = "semiconductor"
     INSULATOR = "insulator"
     # Analyte embedded in a different matrix (2026-07-20): differential
     # charging between analyte and matrix is possible, which voids the
     # single-species-homogeneity assumption behind some region modules'
     # width ceilings. MIXED only RELAXES existing constraints (region
     # modules opt in — see autofit.regions.c1s) — it asserts no new
     # position or width value, and it must never reach charge-correction
     # (that stays byte-identical to every other material class; see
     # tests/test_api_analyze.py::test_material_class_does_not_affect_charge_correction).
     # Appended LAST so the default dropdown/first-enum-member selection
     # (conductor) is unchanged.
     MIXED = "mixed"
 
 
 @dataclass(frozen=True)
 class Phase:
     """
     One physical phase of the sample (spec §2).  ``regions`` declares which
     core-level regions this phase's material contributes signal to — the
     resolver uses it to detect region↔phase ambiguity.
     """
     id: str
     material_class: MaterialClass
     regions: tuple[str, ...]
     role: str = "analyte"                    # analyte | matrix | phase
     material: Optional[str] = None           # e.g. "graphite" — region-module hint
     # Per-phase charge reference (Layer A default when None):
     #   conductor → internal (graphite C 1s 284.4 eV / Fermi edge)
     #   insulator → adventitious C 1s 284.8 eV (CONDITIONAL, Biesinger 2022)
     #   semiconductor → internal-if-present else adventitious
     charge_reference: Optional[dict] = None
@@ -509,115 +509,118 @@ def resolve(
 def _guard_slot_tags(candidates: list[CandidateModel], region: str, phase_id: str) -> None:
     """Region modules must tag every slot with the region + resolved phase."""
     for cand in candidates:
         for slot in cand.slots:
             if slot.region != region:
                 raise ValueError(
                     f"candidate {cand.name!r}: slot {slot.role!r} tagged region "
                     f"{slot.region!r}, expected {region!r}"
                 )
             if slot.phase_id != phase_id:
                 raise ValueError(
                     f"candidate {cand.name!r}: slot {slot.role!r} tagged phase "
                     f"{slot.phase_id!r}, expected {phase_id!r} (phase-id leakage)"
                 )
 
 
 def _guard_phase_leakage(grammar: CandidateGrammar, phases: list[Phase]) -> None:
     """Every slot's phase must be declared AND contribute the slot's region."""
     by_id = {p.id: p for p in phases}
     for cand in grammar.candidates:
         roles = [s.role for s in cand.slots]
         if len(set(roles)) != len(roles):
             raise ValueError(f"candidate {cand.name!r}: duplicate slot roles {roles}")
         for slot in cand.slots:
             phase = by_id.get(slot.phase_id)
             if phase is None:
                 raise ValueError(
                     f"candidate {cand.name!r}: slot {slot.role!r} references "
                     f"undeclared phase {slot.phase_id!r}"
                 )
             if slot.region not in phase.regions:
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
         # slot's parameter name (prefix-based); rewrite whichever matches.
         if fwhm_link in shared_rename:
             fwhm_link = shared_rename[fwhm_link]
         else:
             for old, new in rename.items():
                 old_prefix = _slot_param_prefix(old)
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
 
 
 def _slot_param_prefix(role: str) -> str:
     """Must match engine._slot_prefix — kept here to rewrite fwhm links."""
     return "s_" + re.sub(r"[^A-Za-z0-9_]", "_", role) + "_"
diff --git a/tests/autofit/test_broad_justification.py b/tests/autofit/test_broad_justification.py
index b7dcb05..f676dd5 100644
--- a/tests/autofit/test_broad_justification.py
+++ b/tests/autofit/test_broad_justification.py
@@ -1,165 +1,276 @@
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
 
 
 class _FakeModel:
     """Minimal stand-in for CandidateModel -- _unphysical_width_flags only
     reads .slots."""
     def __init__(self, slots):
         self.slots = slots
 
 
 @pytest.mark.parametrize("phase,region,candidate_name,role,exempt",
                          EXEMPTION_FIXTURE)
 def test_flag_behavior_matches_pre_refactor_rule_at_the_ceiling(
         phase, region, candidate_name, role, exempt):
     """The actual OUTPUT of _unphysical_width_flags for a component fitted
     right at its slot's declared ceiling must match what the pre-refactor
     numeric rule would have produced: no flag for an exempt slot even
     though it pegs a wide ceiling; a flag for a non-exempt slot pegging
     the ordinary 2.0 eV cap."""
     slot = _slot(phase, region, candidate_name, role)
     g = resolve([phase], region)
     cand = next(c for c in g.candidates if c.name == candidate_name)
     fwhm_at_ceiling = slot.fwhm_range[1] if exempt else 2.0
     comp = _fitted(role, fwhm_at_ceiling, line_shape=slot.line_shape)
     flags = _unphysical_width_flags([comp], cand)
     if exempt:
         assert not flags, (
             f"{region}/{candidate_name}/{role}: exempt slot got flagged "
             f"at its own ceiling -- {flags}"
         )
     else:
         assert flags, (
             f"{region}/{candidate_name}/{role}: non-exempt slot pegging "
             "the ordinary 2.0 eV cap should be flagged"
         )
 
 
 # ── The actual bug fix, tested generically at the engine level ────────────
 
 def test_wide_declared_range_without_justification_is_no_longer_exempt():
     """THE FIX, encoded directly: a slot with a wide fwhm_range (would have
     been auto-exempt under the old numeric rule) but broad_justification
     left None must now be flagged when fitted well above the ordinary
     2.0 eV cap -- this is the MIXED contamination scenario, tested here
     independent of MIXED or C 1s at all."""
     from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot
 
     wide_no_justification = ComponentSlot(

exec
/bin/zsh -lc 'git show --stat --oneline --decorate --name-only ad7e668' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-ZXoj4AMk' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-Q9dfV2U1' (errno=Operation not permitted)
ad7e668 fix(autofit): _retag_slot silently dropped broad_justification during composition
autofit/grammar.py
tests/autofit/test_broad_justification.py

codex
The commit scope check is clean: the diff only names `autofit/grammar.py` and `tests/autofit/test_broad_justification.py`. I’m now drilling into the actual copy sites and the engine control flow rather than relying on the commit message.
exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '120,230p'" in /Users/skyefortier/xps-verify
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

exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '560,630p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
/bin/zsh -lc "nl -ba autofit/candidates.py | sed -n '430,485p'" in /Users/skyefortier/xps-verify
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

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '2385,2460p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
  2385	    noise_floor: float,
  2386	    n_refits: int,
  2387	    rng_seed: int,
  2388	    fit_full_window: bool = False,
  2389	) -> Optional[ModelReport]:
  2390	    """
  2391	    Refit a boundary-limited candidate with each pegged parameter FIXED at
  2392	    the bound it pegged to, so its BIC* uses an honest parameter count (a
  2393	    bound-pegged free parameter invalidates the interior-Laplace BIC
  2394	    approximation).
  2395	
  2396	    Honesty requirements (Codex re-check blockers/major):
  2397	    - the refit must not itself peg any NEW bound — otherwise the
  2398	      interior-Laplace comparison is invalid again → return None;
  2399	    - a FRESH stability pass runs on the bound-fixed model (the constrained
  2400	      parameters stay fixed in every multi-start refit) — no inherited
  2401	      figures;
  2402	    - NO absent-slot adjustment is applied to the refit: its BIC* uses the
  2403	      full varying-parameter count (conservative — errs against promotion).
  2404	    """
  2405	    import dataclasses
  2406	
  2407	    lm = report.primary_fit.lmfit_result
  2408	    if lm is None or not report.plausibility.boundary_hits:
  2409	        return None
  2410	    params = lm.params.copy()
  2411	    fixed: dict[str, float] = {}
  2412	    for hit in report.plausibility.boundary_hits:
  2413	        try:
  2414	            role_param, side = hit.rsplit("@", 1)
  2415	            role, pname = role_param.split(":", 1)
  2416	        except ValueError:
  2417	            continue
  2418	        full = _slot_prefix(role) + pname
  2419	        par = params.get(full)
  2420	        if par is None or not par.vary:
  2421	            continue
  2422	        val = par.min if side == "min" else par.max
  2423	        par.set(value=val, vary=False)
  2424	        fixed[full] = float(val)
  2425	    if not fixed:
  2426	        return None
  2427	
  2428	    outcome = fit_candidate(x, y, weights, report.model, initial_params=params)
  2429	    if not outcome.converged:
  2430	        return None
  2431	    if outcome.boundary_hits:
  2432	        # fixing one wall pushed the fit onto another — still not an
  2433	        # interior optimum; no honest BIC* comparison is possible
  2434	        return None
  2435	
  2436	    stability = run_stability_analysis(
  2437	        x, y, weights, report.model, outcome,
  2438	        noise_floor=noise_floor, n_refits=n_refits, rng_seed=rng_seed,
  2439	        fixed_param_values=fixed,
  2440	        deadline=time.perf_counter() + CANDIDATE_TIMEOUT_SEC,
  2441	        fit_full_window=fit_full_window,
  2442	    )
  2443	    y_fit = (outcome.lmfit_result.best_fit + outcome.background
  2444	             if outcome.lmfit_result is not None else np.zeros_like(y))
  2445	    return ModelReport(
  2446	        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
  2447	        primary_fit=outcome,
  2448	        bic=compute_bic(outcome),
  2449	        stability=stability,
  2450	        residuals=compute_residual_diagnostics(
  2451	            x, y, y_fit, noise_floor, diagnostic_windows),
  2452	        plausibility=PlausibilityFlags(
  2453	            boundary_hits=[],
  2454	            # width pegs that were FIXED at the cap are still at the physical
  2455	            # ceiling — a fixed-at-2.0 ordinary component is no more physical
  2456	            # than a pegged one, so keep flagging it
  2457	            unphysical_widths=_unphysical_width_flags(outcome.components, report.model),
  2458	            orphan_peaks=stability.orphan_rate > 0.1,
  2459	        ),
  2460	        absent_slots=[],                      # conservative full-k BIC*

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '2065,2135p'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '1800,1935p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
  2131	    y_net: np.ndarray,
  2132	    fit_full_window: bool = False,
  2133	) -> Parameters:
  2134	    params = _default_params_from_slots(aug_model, x=x, y_net=y_net,
  2135	                                        fit_full_window=fit_full_window)

 succeeded in 0ms:
  1800	    x: np.ndarray,
  1801	    y: np.ndarray,
  1802	    background: np.ndarray,
  1803	    candidates: list[CandidateModel],
  1804	    canonical_windows: dict[str, tuple[float, float]],
  1805	    noise_floor: float = 1.0,
  1806	) -> list[PreseedSpec]:
  1807	    """
  1808	    Prominent smoothed local maxima of the background-subtracted data that
  1809	    lie outside EVERY grammar slot window and diagnostic window (+ the same
  1810	    separation margin the proposal pass uses).  Conservative by design —
  1811	    dominance (fraction-of-max) AND detection-floor SNR gates — so ordinary
  1812	    grammar-covered spectra return [] and small out-of-window features stay
  1813	    the residual-proposal pass's job.
  1814	    """
  1815	    if len(x) < max(PRESEED_SMOOTH_POINTS + 4, 8):
  1816	        return []
  1817	    # real raw_be grids DESCEND — normalize (np.interp-class bug family)
  1818	    if x[0] > x[-1]:
  1819	        x_asc, y_asc, bg_asc = x[::-1], y[::-1], background[::-1]
  1820	    else:
  1821	        x_asc, y_asc, bg_asc = x, y, background
  1822	    y_net = y_asc - bg_asc
  1823	    k = PRESEED_SMOOTH_POINTS
  1824	    kernel = np.ones(k) / k
  1825	    ys = np.convolve(y_net, kernel, mode="same")
  1826	    global_max = float(np.max(ys))
  1827	    if global_max <= 0:
  1828	        return []
  1829	
  1830	    # margin: mean main-FWHM midpoint across the candidate set × the
  1831	    # proposal separation factor (the same "too close to a window to be a
  1832	    # separate feature" convention)
  1833	    margin = _preseed_window_margin(candidates)
  1834	    windows = _all_grammar_windows(candidates, canonical_windows)
  1835	
  1836	    def in_any_window(be: float) -> bool:
  1837	        return any((lo - margin) <= be <= (hi + margin) for lo, hi in windows)
  1838	
  1839	    found: list[PreseedSpec] = []
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
  1926	    detection_windows: list[str]
  1927	    detection_energy: float
  1928	    detection_ratio: float
  1929	    center_init: float
  1930	    fwhm_init: float
  1931	    amplitude_init: float
  1932	    line_shape: LineShape
  1933	
  1934	
  1935	def _proposal_tiles(x: np.ndarray) -> list[tuple[str, tuple[float, float]]]:

codex
The only production `ComponentSlot(...)` constructors outside region modules are the three called out: detection, preseed, and proposal. I’m checking constants and the width-flag branches now, then I’ll run focused repros for composed candidates and an extra composition outside the new fixture.
exec
/bin/zsh -lc 'rg -n "FWHM_MAX_ORDINARY_EV|PROPOSAL_FWHM_MAX|def _unphysical_width_flags|detected_peak_|broad_justification" autofit/engine.py autofit/regions autofit/grammar.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/grammar.py:176:    # FWHM_MAX_ORDINARY_EV granted exemption automatically) — widening a
autofit/grammar.py:181:    broad_justification: Optional[str] = None
autofit/grammar.py:595:    reconstruction this replaced was exactly how broad_justification got
autofit/grammar.py:599:    tests/autofit/test_broad_justification.py's
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
autofit/engine.py:2633:                fwhm_clip=(PROPOSAL_FWHM_MIN, PROPOSAL_FWHM_MAX),
autofit/regions/u4f.py:222:            broad_justification=_main_justification,
autofit/regions/u4f.py:231:            broad_justification=_main_justification,
autofit/regions/u4f.py:239:            broad_justification=_sat_justification,
autofit/regions/u4f.py:249:            broad_justification=_sat_justification,
autofit/regions/u4f.py:260:            broad_justification=_sat_justification,
autofit/regions/u4f.py:270:            broad_justification=_sat_justification,
autofit/regions/u4f.py:277:            broad_justification=_sat_justification,
autofit/regions/n1s.py:80:            broad_justification=_justification,
autofit/regions/n1s.py:87:            broad_justification=_justification,
autofit/regions/b1s.py:96:                broad_justification=(
autofit/regions/c1s.py:337:            broad_justification=(
autofit/regions/cl2p.py:147:                broad_justification=_empirical_justification,
autofit/regions/cl2p.py:164:                    broad_justification=_coster_kronig_justification,
autofit/regions/cl2p.py:175:                broad_justification=_empirical_justification,

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '80,150p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
    91	PROPOSAL_FLAG_RATIO = 5.0
    92	PROPOSAL_MERGE_BE = 1.0
    93	PROPOSAL_FWHM_MIN = 0.5
    94	
    95	# Relative χ² tolerance for counting multi-start fits as landing in the SAME
    96	# basin as the best minimum (best_basin_support) — reporting-only honesty
    97	# diagnostic, never a ranking input.  UNVERIFIED tunable.
    98	BASIN_SUPPORT_RTOL = 1e-3
    99	# Physical FWHM ceiling for an ORDINARY component — one with no known-broad
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
   131	# break, two missing species (the real 279/281 eV pair, cluster-merged into
   132	# one detection) could never both be modeled — the second stayed a +65σ
   133	# residual.  fitalg's Iteration B was already capped/timeout-guarded; this
   134	# keeps those guards and bounds the rounds.  UNVERIFIED tunable.
   135	PROPOSAL_MAX_PER_CANDIDATE = 3
   136	PROPOSAL_MAX_ATTEMPTS_PER_CANDIDATE = 3
   137	# Whole ITERATIVE proposal pass per candidate (all F2 rounds share it).
   138	# Raised 30 → 60 with F2: the pass may now legitimately do up to
   139	# PROPOSAL_MAX_PER_CANDIDATE accepted rounds of (augmented fit + stability).
   140	# UNVERIFIED tunable.
   141	PROPOSAL_CANDIDATE_TIMEOUT_SEC = 60.0
   142	# One augmented-model stability pass inside the proposal pass.  Replaces the
   143	# old min(budget, CANDIDATE_TIMEOUT_SEC) clamp, whose 25 s ceiling cut the
   144	# n_refits=4 stability of a slow augmented model to 3 attempts and QUANTIZED
   145	# the persistence gate below its threshold — measured on the real C 1s
   146	# motivating case (PROGRESS.md diagnosis follow-up): a ΔBIC* −86 proposal
   147	# with no boundary hits was rejected at persistence 2/3 = 0.67 < 0.70 purely
   148	# because the 4th refit never ran.  35 s fits n_refits=4 at the measured
   149	# ~7-8 s worst-case per refit on 191-point real data.  UNVERIFIED tunable.
   150	PROPOSAL_STABILITY_TIMEOUT_SEC = 35.0

exec
/bin/zsh -lc "nl -ba autofit/regions/n1s.py | sed -n '60,95p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba autofit/regions/u4f.py | sed -n '160,235p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '1010,1095p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
  1010	        return abs(float(sp.get("alpha", 1.0)) - float(sp.get("beta", 1.0))) \
  1011	            > LACX_EXPONENT_ASYMMETRY
  1012	    return False
  1013	
  1014	
  1015	def _effective_be_window(
  1016	    slot: ComponentSlot, components: list[FittedComponent],
  1017	    bound_override: Optional[tuple[float, float]] = None,
  1018	) -> tuple[float, float]:
  1019	    """``bound_override`` (fit_full_window, unit 1 2026-07-13): the SAME
  1020	    widened bound the fit itself was built with
  1021	    (``_full_window_bound_overrides``) — a primary slot's fitted position
  1022	    identity-matching must agree with the bound it was actually allowed
  1023	    to search, or a component the widened fit correctly placed outside
  1024	    its ORIGINAL literature window becomes an orphan here (Codex-caught:
  1025	    tanks stability/persistence, silently rejecting the very component
  1026	    this option exists to rescue). Only applies to a primary slot
  1027	    (``linked_to is None`` — a linked slot's effective window is always
  1028	    the offset-derived one below, entirely unaffected by this option)."""
  1029	    if slot.linked_to is None or slot.linked_offset_range is None:
  1030	        return bound_override if bound_override is not None else slot.be_window
  1031	    parent = next((c for c in components if c.slot_role == slot.linked_to), None)
  1032	    if parent is None:
  1033	        return slot.be_window
  1034	    lo, hi = slot.linked_offset_range
  1035	    return (parent.position + lo, parent.position + hi)
  1036	
  1037	
  1038	def match_components_to_slots(
  1039	    components: list[FittedComponent],
  1040	    model: CandidateModel,
  1041	    noise_floor: float,
  1042	    bound_overrides: Optional[dict[str, tuple[float, float]]] = None,
  1043	) -> dict[str, Optional[FittedComponent]]:
  1044	    """Assign fitted peaks to grammar slots (role + effective window + width).
  1045	
  1046	    ``bound_overrides`` (fit_full_window) — see ``_effective_be_window``.
  1047	    """
  1048	    slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
  1049	    orphans: list[FittedComponent] = []
  1050	    asym_shapes = {LineShape.ASYM_GL, LineShape.DS, LineShape.DS_G, LineShape.LACX}
  1051	
  1052	    def _accepts(slot: ComponentSlot, comp: FittedComponent) -> bool:
  1053	        lo, hi = _effective_be_window(slot, components,
  1054	                                      (bound_overrides or {}).get(slot.role))
  1055	        return (lo <= comp.position <= hi
  1056	                and slot.fwhm_range[0] <= comp.fwhm <= slot.fwhm_range[1]
  1057	                and comp.amplitude > noise_floor)
  1058	
  1059	    def _window_center(slot: ComponentSlot) -> float:
  1060	        # NEVER the widened bound (Codex-caught, round 2): this is a
  1061	        # TIE-BREAK reference point ("how close is this component to
  1062	        # where this slot expects its peak"), not an acceptance test —
  1063	        # widening it would drag the reference point far from the
  1064	        # slot's true expected position (e.g. a curated slot's own
  1065	        # narrow window widened to a whole ROI), making a neighboring
  1066	        # slot's UNWIDENED, much-closer center win the tie-break even
  1067	        # when the component sits well inside THIS slot's own original
  1068	        # window. Acceptance (_accepts, above) is the only place the
  1069	        # widened bound belongs.
  1070	        lo, hi = _effective_be_window(slot, components)
  1071	        return 0.5 * (lo + hi)
  1072	
  1073	    for comp in components:
  1074	        candidate_slots = [s for s in model.slots if _accepts(s, comp)]
  1075	        if not candidate_slots:
  1076	            orphans.append(FittedComponent(
  1077	                slot_role="unmatched", position=comp.position, fwhm=comp.fwhm,
  1078	                amplitude=comp.amplitude, shape_params=comp.shape_params,
  1079	                line_shape=comp.line_shape,
  1080	            ))
  1081	            continue
  1082	
  1083	        shapes = {s.line_shape for s in candidate_slots}
  1084	        if len(shapes) > 1:
  1085	            if _is_asymmetric_component(comp):
  1086	                preferred = [s for s in candidate_slots if s.line_shape in asym_shapes]
  1087	            else:
  1088	                preferred = [s for s in candidate_slots if s.line_shape not in asym_shapes]
  1089	            if preferred:
  1090	                candidate_slots = preferred
  1091	
  1092	        best_slot = min(candidate_slots, key=lambda s: abs(comp.position - _window_center(s)))
  1093	        incumbent = slot_map[best_slot.role]
  1094	        claimed = FittedComponent(
  1095	            slot_role=best_slot.role, position=comp.position, fwhm=comp.fwhm,

exec
/bin/zsh -lc "rg -n \"broad_justification=\" autofit/regions -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/regions/u4f.py:222:            broad_justification=_main_justification,
autofit/regions/u4f.py:231:            broad_justification=_main_justification,
autofit/regions/u4f.py:239:            broad_justification=_sat_justification,
autofit/regions/u4f.py:249:            broad_justification=_sat_justification,
autofit/regions/u4f.py:260:            broad_justification=_sat_justification,
autofit/regions/u4f.py:270:            broad_justification=_sat_justification,
autofit/regions/u4f.py:277:            broad_justification=_sat_justification,
autofit/regions/n1s.py:80:            broad_justification=_justification,
autofit/regions/n1s.py:87:            broad_justification=_justification,
autofit/regions/b1s.py:96:                broad_justification=(
autofit/regions/c1s.py:337:            broad_justification=(
autofit/regions/cl2p.py:147:                broad_justification=_empirical_justification,
autofit/regions/cl2p.py:164:                    broad_justification=_coster_kronig_justification,
autofit/regions/cl2p.py:175:                broad_justification=_empirical_justification,

codex
The constant claim is exact in source: `PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV`, with `FWHM_MAX_ORDINARY_EV = 2.0`. Next I’m reading the full `_unphysical_width_flags` function around the detection branch and checking the runtime behavior.
exec
/bin/zsh -lc "nl -ba tests/autofit/test_broad_justification.py | sed -n '105,210p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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
/bin/zsh -lc "rg -n \"for .*slots|\\.slots|slot_by_role|ComponentSlot|replace\\(\" autofit -g '*.py'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
autofit/candidates.py:427:    from .grammar import CandidateModel, ComponentSlot, LineShape
autofit/candidates.py:463:        slots.append(ComponentSlot(
autofit/engine.py:52:    ComponentSlot,
autofit/engine.py:325:    for slot in model.slots:
autofit/engine.py:368:    p: Parameters, prefix: str, slot: ComponentSlot, fwhm_init: float,
autofit/engine.py:386:        # (Coster-Kronig doublet broadening — grammar.ComponentSlot docs)
autofit/engine.py:456:    primary = [s for s in model.slots if s.linked_to is None]
autofit/engine.py:512:    for slot in model.slots:
autofit/engine.py:529:    done_roles = {s.role for s in model.slots if s.linked_to is None}
autofit/engine.py:530:    pending = [s for s in model.slots if s.linked_to is not None]
autofit/engine.py:531:    ordered: list[ComponentSlot] = []
autofit/engine.py:546:        parent = model.slot_by_role(slot.linked_to)
autofit/engine.py:659:    for slot in model.slots:
autofit/engine.py:706:    role_by_prefix = {_slot_prefix(s.role): s.role for s in model.slots}
autofit/engine.py:707:    shape_by_role = {s.role: s.line_shape for s in model.slots}
autofit/engine.py:761:    only if it carries an explicit ``ComponentSlot.broad_justification``
autofit/engine.py:784:    slots_by_role = {s.role: s for s in model.slots}
autofit/engine.py:941:    for slot in model.slots:
autofit/engine.py:978:    for slot in model.slots:
autofit/engine.py:1016:    slot: ComponentSlot, components: list[FittedComponent],
autofit/engine.py:1048:    slot_map: dict[str, Optional[FittedComponent]] = {s.role: None for s in model.slots}
autofit/engine.py:1052:    def _accepts(slot: ComponentSlot, comp: FittedComponent) -> bool:
autofit/engine.py:1059:    def _window_center(slot: ComponentSlot) -> float:
autofit/engine.py:1074:        candidate_slots = [s for s in model.slots if _accepts(s, comp)]
autofit/engine.py:1083:        shapes = {s.line_shape for s in candidate_slots}
autofit/engine.py:1086:                preferred = [s for s in candidate_slots if s.line_shape in asym_shapes]
autofit/engine.py:1088:                preferred = [s for s in candidate_slots if s.line_shape not in asym_shapes]
autofit/engine.py:1182:    pos: dict[str, list[float]] = {s.role: [] for s in model.slots}
autofit/engine.py:1183:    fw: dict[str, list[float]] = {s.role: [] for s in model.slots}
autofit/engine.py:1184:    am: dict[str, list[float]] = {s.role: [] for s in model.slots}
autofit/engine.py:1185:    occupied: dict[str, int] = {s.role: 0 for s in model.slots}
autofit/engine.py:1291:def _count_slot_free_params(slot: ComponentSlot, primary: FitOutcome) -> int:
autofit/engine.py:1304:def _linked_groups(model: CandidateModel) -> list[list[ComponentSlot]]:
autofit/engine.py:1311:    non_main = [s for s in model.slots if not _is_main_role(s.role)]
autofit/engine.py:1321:    groups: dict[str, list[ComponentSlot]] = {}
autofit/engine.py:1347:    the global main area for slots without same-scope mains (e.g. proposals,
autofit/engine.py:1355:    for s in model.slots:
autofit/engine.py:1361:    def _member_report(slot: ComponentSlot) -> Optional[AbsentSlotReport]:
autofit/engine.py:1510:        removed = sum(a.removed_n_params for a in self.absent_slots)
autofit/engine.py:1567:        absent_roles = {a.role for a in self.absent_slots}
autofit/engine.py:1677:            absent_roles = [a.role for a in r.absent_slots]
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
autofit/engine.py:2709:                        det_model.name, len(det_model.slots),
autofit/engine.py:2711:                         for s in det_model.slots])
autofit/grammar.py:16:``mixed{analyte, matrix}``.  Every :class:`ComponentSlot` carries a
autofit/grammar.py:37:    "LineShape", "BackgroundType", "MaterialClass", "Phase", "ComponentSlot",
autofit/grammar.py:115:class ComponentSlot:
autofit/grammar.py:197:    slots: tuple[ComponentSlot, ...]
autofit/grammar.py:203:        return len(self.slots)
autofit/grammar.py:205:    def slot_by_role(self, role: str) -> Optional[ComponentSlot]:
autofit/grammar.py:206:        for s in self.slots:
autofit/grammar.py:454:            for s in cand.slots:
autofit/grammar.py:469:    sanitized = [re.sub(r"[^A-Za-z0-9_]", "", s.replace(" ", ""))
autofit/grammar.py:512:        for slot in cand.slots:
autofit/grammar.py:529:        roles = [s.role for s in cand.slots]
autofit/grammar.py:532:        for slot in cand.slots:
autofit/grammar.py:565:        slots: list[ComponentSlot] = []
autofit/grammar.py:568:            slug = re.sub(r"[^A-Za-z0-9_]", "", slug.replace(" ", ""))
autofit/grammar.py:569:            rename = {s.role: f"{slug}__{s.role}" for s in cand.slots}
autofit/grammar.py:571:            for s in cand.slots:
autofit/grammar.py:585:    s: ComponentSlot,
autofit/grammar.py:588:) -> ComponentSlot:
autofit/grammar.py:591:    Uses dataclasses.replace (ComponentSlot is frozen) rather than
autofit/grammar.py:592:    reconstructing the slot field-by-field: replace() carries every field
autofit/grammar.py:594:    to ComponentSlot after this function was written. The manual
autofit/grammar.py:616:    return replace(
autofit/confidence.py:38:    slot = report.model.slot_by_role(role)
autofit/methods/ic_model_comparison.py:103:        absent_roles = {a.role for a in top.absent_slots}
autofit/methods/ic_model_comparison.py:107:            for slot in top.model.slots
autofit/methods/ic_model_comparison.py:112:            slot.role for slot in top.model.slots
autofit/methods/ic_model_comparison.py:212:    for slot in report.model.slots:
autofit/methods/ic_model_comparison.py:274:                 "area_fraction": float(a.area_fraction)} for a in r.absent_slots
autofit/methods/sparse_map.py:83:        for s in cand.slots:
autofit/criteria.py:68:    small = {s.role: s.line_shape for s in smaller.model.slots}
autofit/criteria.py:69:    large = {s.role: s.line_shape for s in larger.model.slots}
autofit/methods/bayesian_exchange_mc.py:516:    for slot in model.slots:
autofit/regions/c1s.py:30:    ComponentSlot,
autofit/regions/c1s.py:308:        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
autofit/regions/c1s.py:309:            return ComponentSlot(
autofit/regions/c1s.py:314:        def graphitic_main_dsg() -> ComponentSlot:
autofit/regions/c1s.py:322:        def graphitic_main_asymgl() -> ComponentSlot:
autofit/regions/c1s.py:329:        def aliphatic_main() -> ComponentSlot:
autofit/regions/c1s.py:347:                   fwhm_range=None) -> ComponentSlot:
autofit/regions/c1s.py:423:        def aliphatic_main_offset() -> ComponentSlot:
autofit/regions/u4f.py:40:    ComponentSlot,
autofit/regions/u4f.py:196:        def slot(role, window, shape, fwhm_range, **kw) -> ComponentSlot:
autofit/regions/u4f.py:197:            return ComponentSlot(
autofit/regions/b1s.py:26:    ComponentSlot,
autofit/regions/b1s.py:91:        def pv(role, window) -> ComponentSlot:
autofit/regions/b1s.py:92:            return ComponentSlot(
autofit/regions/n1s.py:26:    ComponentSlot,
autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
autofit/regions/n1s.py:82:        ag_main = ComponentSlot(
autofit/regions/cl2p.py:41:    ComponentSlot,
autofit/regions/cl2p.py:142:        def p32() -> ComponentSlot:
autofit/regions/cl2p.py:143:            return ComponentSlot(
autofit/regions/cl2p.py:150:        def p12(ratio, ratio_range, free_width=False) -> ComponentSlot:
autofit/regions/cl2p.py:154:                return ComponentSlot(
autofit/regions/cl2p.py:166:            return ComponentSlot(

codex
`_unphysical_width_flags` handles `detected_peak_` after DS+G/asym-GL effective width checks but before the generic `broad_justification` exemption/generic ordinary-cap branch. Because detection slots are constructed as `PSEUDO_VOIGT`, the earlier DS+G/asym-GL branches cannot fire for those normal detection candidates. I’m going to validate that with a direct call too.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 pytest -q tests/autofit/test_broad_justification.py -q -p no:cacheprovider' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: pytest

codex
The sandbox blocks shell here-doc temporary files, and `pytest` is not on `PATH`. I can still exercise the logic with `python -c`; for the test file I’ll try `python -m pytest`, then fall back to direct function calls if pytest is unavailable.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python -c \"from autofit.grammar import MaterialClass, Phase, resolve; phases=[Phase(id='UCl4', material_class=MaterialClass.INSULATOR, regions=('U 4f',)), Phase(id='BN', material_class=MaterialClass.INSULATOR, regions=('N 1s',))]; g=resolve(phases, ['U 4f','N 1s']); checks=[('U0_mains+N0_pv','U4f__main_u4f72'),('U0_mains+N0_pv','U4f__main_u4f52'),('U0_mains+N0_pv','N1s__main_n1s'),('U1_mains_satpair+N0_pv','U4f__satellite_u4f72'),('U1_mains_satpair+N0_pv','U4f__satellite_u4f52'),('U1b_mains_satpair_freesep+N0_asymGL','U4f__satellite_u4f52'),('U2_mains_satfree+N0_asymGL','U4f__satellite_u4f72'),('U2_mains_satfree+N0_asymGL','U4f__satellite_u4f52')]; [print(cname, role, (s:=next(c for c in g.candidates if c.name==cname).slot_by_role(role)).fwhm_range, bool(s.broad_justification), (s.broad_justification or '')[:55]) for cname, role in checks]\"" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python -c \"from autofit.engine import FWHM_MAX_ORDINARY_EV, PROPOSAL_FWHM_MAX, _unphysical_width_flags, FittedComponent; from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape; print('constants', repr(FWHM_MAX_ORDINARY_EV), repr(PROPOSAL_FWHM_MAX), FWHM_MAX_ORDINARY_EV == PROPOSAL_FWHM_MAX); slot=ComponentSlot(role='detected_peak_0', region='unassigned', phase_id='unassigned', be_window=(0,1), line_shape=LineShape.PSEUDO_VOIGT, fwhm_range=(0.5,10.0)); model=CandidateModel(name='det', background=BackgroundType.SHIRLEY, slots=(slot,)); [print('detected fwhm', f, 'flags', _unphysical_width_flags([FittedComponent(slot_role='detected_peak_0', position=0.5, fwhm=f, amplitude=1.0, shape_params={}, line_shape=LineShape.PSEUDO_VOIGT)], model)) for f in (2.0,6.9,7.0)]\"" in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python -m pytest -q tests/autofit/test_broad_justification.py -q -p no:cacheprovider' in /Users/skyefortier/xps-verify
 exited 127 in 0ms:
zsh:1: command not found: python

codex
This environment exposes `python3`, not `python`. I’ll rerun the focused checks through that interpreter.
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit.engine import FWHM_MAX_ORDINARY_EV, PROPOSAL_FWHM_MAX, _unphysical_width_flags, FittedComponent; from autofit.grammar import BackgroundType, CandidateModel, ComponentSlot, LineShape; print('constants', repr(FWHM_MAX_ORDINARY_EV), repr(PROPOSAL_FWHM_MAX), FWHM_MAX_ORDINARY_EV == PROPOSAL_FWHM_MAX); slot=ComponentSlot(role='detected_peak_0', region='unassigned', phase_id='unassigned', be_window=(0,1), line_shape=LineShape.PSEUDO_VOIGT, fwhm_range=(0.5,10.0)); model=CandidateModel(name='det', background=BackgroundType.SHIRLEY, slots=(slot,)); [print('detected fwhm', f, 'flags', _unphysical_width_flags([FittedComponent(slot_role='detected_peak_0', position=0.5, fwhm=f, amplitude=1.0, shape_params={}, line_shape=LineShape.PSEUDO_VOIGT)], model)) for f in (2.0,6.9,7.0)]\"" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc "PYTHONDONTWRITEBYTECODE=1 python3 -c \"from autofit.grammar import MaterialClass, Phase, resolve; phases=[Phase(id='UCl4', material_class=MaterialClass.INSULATOR, regions=('U 4f',)), Phase(id='BN', material_class=MaterialClass.INSULATOR, regions=('N 1s',))]; g=resolve(phases, ['U 4f','N 1s']); checks=[('U0_mains+N0_pv','U4f__main_u4f72'),('U0_mains+N0_pv','U4f__main_u4f52'),('U0_mains+N0_pv','N1s__main_n1s'),('U1_mains_satpair+N0_pv','U4f__satellite_u4f72'),('U1_mains_satpair+N0_pv','U4f__satellite_u4f52'),('U1b_mains_satpair_freesep+N0_asymGL','U4f__satellite_u4f52'),('U2_mains_satfree+N0_asymGL','U4f__satellite_u4f72'),('U2_mains_satfree+N0_asymGL','U4f__satellite_u4f52')]; [print(cname, role, (s:=next(c for c in g.candidates if c.name==cname).slot_by_role(role)).fwhm_range, bool(s.broad_justification), (s.broad_justification or '')[:55]) for cname, role in checks]\"" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-8zCGGf24' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-0vj1e0a2' (errno=Operation not permitted)
U0_mains+N0_pv U4f__main_u4f72 (1.5, 3.5) True U(IV) 5f2 open-shell final state: an unresolved multipl
U0_mains+N0_pv U4f__main_u4f52 (1.5, 3.5) True U(IV) 5f2 open-shell final state: an unresolved multipl
U0_mains+N0_pv N1s__main_n1s (0.7, 2.5) True UNVERIFIED-empirical: single labeled exemplar only (fwh
U1_mains_satpair+N0_pv U4f__satellite_u4f72 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical feature
U1_mains_satpair+N0_pv U4f__satellite_u4f52 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical feature
U1b_mains_satpair_freesep+N0_asymGL U4f__satellite_u4f52 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical feature
U2_mains_satfree+N0_asymGL U4f__satellite_u4f72 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical feature
U2_mains_satfree+N0_asymGL U4f__satellite_u4f52 (1.5, 4.5) True the U(IV) shake-up satellite is a real physical feature

 exited 1 in 144ms:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/Users/skyefortier/xps-verify/autofit/engine.py", line 38, in <module>
    from lmfit import Model, Parameters
ModuleNotFoundError: No module named 'lmfit'

2026-07-20T18:56:36.553370Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '1,70p'" in /Users/skyefortier/xps-verify
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

2026-07-20T18:56:42.264197Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The Python environment is missing `lmfit` and `pytest`, so I can’t import `autofit.engine` or run the test module normally here. The grammar-only checks do run, which is enough to exercise `_retag_slot` and composed candidate preservation directly.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import dataclasses\\nfrom autofit.grammar import ComponentSlot, LineShape, _retag_slot\\nsentinel=dict(role=\"orig_role\", region=\"orig_region\", phase_id=\"orig_phase\", be_window=(100.0,200.0), line_shape=LineShape.PSEUDO_VOIGT, fwhm_range=(0.5,9.99), linked_to=\"orig_role\", linked_offset_range=(1.0,2.0), area_ratio=0.123456, area_ratio_range=(0.1,0.9), fixed_params=((\"beta\",0.05),), param_ranges=((\"alpha\",(0.0,0.3)),), fwhm_linked_to=None, fwhm_excess_range=(0.0,0.8), share_parent_params=(\"alpha\",\"beta\"), broad_justification=\"sentinel justification text\")\\noriginal=ComponentSlot(**sentinel)\\nretagged=_retag_slot(original,{\"orig_role\":\"PhaseX__orig_role\"},{})\\nprint(\"new broad preserved\", retagged.broad_justification == original.broad_justification, retagged.broad_justification)\\n\\ndef old_retag(s, rename, shared_rename):\\n    fwhm_link=s.fwhm_linked_to\\n    return ComponentSlot(role=rename[s.role], region=s.region, phase_id=s.phase_id, be_window=s.be_window, line_shape=s.line_shape, fwhm_range=s.fwhm_range, linked_to=rename.get(s.linked_to, s.linked_to) if s.linked_to else None, linked_offset_range=s.linked_offset_range, area_ratio=s.area_ratio, area_ratio_range=s.area_ratio_range, fixed_params=s.fixed_params, param_ranges=s.param_ranges, fwhm_linked_to=fwhm_link, share_parent_params=s.share_parent_params, fwhm_excess_range=s.fwhm_excess_range)\\nold=old_retag(original,{\"orig_role\":\"PhaseX__orig_role\"},{})\\nfailures=[name for name in {f.name for f in dataclasses.fields(ComponentSlot)}-{\"role\",\"linked_to\",\"fwhm_linked_to\"} if getattr(old,name)"'!=getattr(original,name)]'"\\nprint(\"old failures\", failures, \"old broad\", old.broad_justification)\\n'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-phVo7uYi' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-JGS6Flkc' (errno=Operation not permitted)
new broad preserved True sentinel justification text
old failures ['broad_justification'] old broad None

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import MaterialClass, Phase, resolve\\nphase_for={\"C 1s\": Phase(id=\"C\", material_class=MaterialClass.CONDUCTOR, regions=(\"C 1s\",)), \"B 1s\": Phase(id=\"B\", material_class=MaterialClass.INSULATOR, regions=(\"B 1s\",)), \"Cl 2p\": Phase(id=\"Cl\", material_class=MaterialClass.INSULATOR, regions=(\"Cl 2p\",)), \"N 1s\": Phase(id=\"N\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",)), \"U 4f\": Phase(id=\"U\", material_class=MaterialClass.INSULATOR, regions=(\"U 4f\",))}\\nchecks=[(\"C 1s\",\"N 1s\"),(\"B 1s\",\"N 1s\"),(\"Cl 2p\",\"N 1s\"),(\"U 4f\",\"B 1s\",\"N 1s\"),(\"C 1s\",\"B 1s\",\"N 1s\")]\\nfor regs in checks:\\n    try:\\n        g=resolve([phase_for[r] for r in regs], list(regs))\\n    except Exception as e:\\n        print(regs, \"ERROR\", type(e).__name__, str(e)[:100])\\n        continue\\n    missing=[]; present=0; total=0\\n    for cand in g.candidates:\\n        for s in cand.slots:\\n            total+=1\\n            if s.fwhm_range[1] > 2.0 and s.broad_justification is not None:\\n                present+=1\\n            if s.fwhm_range[1] > 2.0 and s.broad_justification is None:\\n                missing.append((cand.name,s.role,s.fwhm_range))\\n    print(regs, \"candidates\", len(g.candidates), \"slots\", total, \"wide+vouched\", present, \"wide+unvouched\", missing[:8])\\n'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-9Y2yGjSY' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-Ki9kDiDt' (errno=Operation not permitted)
('C 1s', 'N 1s') ERROR ValueError joint candidates must share one background, got {<BackgroundType.SMART: 'smart'>, <BackgroundType.SH
('B 1s', 'N 1s') ERROR ValueError joint candidates must share one background, got {<BackgroundType.SMART: 'smart'>, <BackgroundType.SM
('Cl 2p', 'N 1s') ERROR ValueError joint candidates must share one background, got {<BackgroundType.SMART: 'smart'>, <BackgroundType.SM
('U 4f', 'B 1s', 'N 1s') ERROR ValueError joint candidates must share one background, got {<BackgroundType.SMART: 'smart'>, <BackgroundType.SM
('C 1s', 'B 1s', 'N 1s') ERROR ValueError joint candidates must share one background, got {<BackgroundType.SMART: 'smart'>, <BackgroundType.SH

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import MaterialClass, Phase, resolve\\nphases=[Phase(id=\"UCl4\", material_class=MaterialClass.INSULATOR, regions=(\"U 4f\",)), Phase(id=\"BN\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",))]\\ng=resolve(phases,[\"U 4f\",\"N 1s\"])\\nfor cand in g.candidates:\\n    for s in cand.slots:\\n        if s.broad_justification is not None:\\n            print(cand.name, s.role, s.fwhm_range, \"BROAD\")\\n'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-OOxZonnZ' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-mT5Uk84Z' (errno=Operation not permitted)
U0_mains+N0_pv U4f__main_u4f72 (1.5, 3.5) BROAD
U0_mains+N0_pv U4f__main_u4f52 (1.5, 3.5) BROAD
U0_mains+N0_pv N1s__main_n1s (0.7, 2.5) BROAD
U0_mains+N0_asymGL U4f__main_u4f72 (1.5, 3.5) BROAD
U0_mains+N0_asymGL U4f__main_u4f52 (1.5, 3.5) BROAD
U0_mains+N0_asymGL N1s__main_n1s (0.7, 2.5) BROAD
U1_mains_satpair+N0_pv U4f__main_u4f72 (1.5, 3.5) BROAD
U1_mains_satpair+N0_pv U4f__main_u4f52 (1.5, 3.5) BROAD
U1_mains_satpair+N0_pv U4f__satellite_u4f72 (1.5, 4.5) BROAD
U1_mains_satpair+N0_pv U4f__satellite_u4f52 (1.5, 4.5) BROAD
U1_mains_satpair+N0_pv N1s__main_n1s (0.7, 2.5) BROAD
U1_mains_satpair+N0_asymGL U4f__main_u4f72 (1.5, 3.5) BROAD
U1_mains_satpair+N0_asymGL U4f__main_u4f52 (1.5, 3.5) BROAD
U1_mains_satpair+N0_asymGL U4f__satellite_u4f72 (1.5, 4.5) BROAD
U1_mains_satpair+N0_asymGL U4f__satellite_u4f52 (1.5, 4.5) BROAD
U1_mains_satpair+N0_asymGL N1s__main_n1s (0.7, 2.5) BROAD
U1b_mains_satpair_freesep+N0_pv U4f__main_u4f72 (1.5, 3.5) BROAD
U1b_mains_satpair_freesep+N0_pv U4f__main_u4f52 (1.5, 3.5) BROAD
U1b_mains_satpair_freesep+N0_pv U4f__satellite_u4f72 (1.5, 4.5) BROAD
U1b_mains_satpair_freesep+N0_pv U4f__satellite_u4f52 (1.5, 4.5) BROAD
U1b_mains_satpair_freesep+N0_pv N1s__main_n1s (0.7, 2.5) BROAD
U1b_mains_satpair_freesep+N0_asymGL U4f__main_u4f72 (1.5, 3.5) BROAD
U1b_mains_satpair_freesep+N0_asymGL U4f__main_u4f52 (1.5, 3.5) BROAD
U1b_mains_satpair_freesep+N0_asymGL U4f__satellite_u4f72 (1.5, 4.5) BROAD
U1b_mains_satpair_freesep+N0_asymGL U4f__satellite_u4f52 (1.5, 4.5) BROAD
U1b_mains_satpair_freesep+N0_asymGL N1s__main_n1s (0.7, 2.5) BROAD
U2_mains_satfree+N0_pv U4f__main_u4f72 (1.5, 3.5) BROAD
U2_mains_satfree+N0_pv U4f__main_u4f52 (1.5, 3.5) BROAD
U2_mains_satfree+N0_pv U4f__satellite_u4f72 (1.5, 4.5) BROAD
U2_mains_satfree+N0_pv U4f__satellite_u4f52 (1.5, 4.5) BROAD
U2_mains_satfree+N0_pv N1s__main_n1s (0.7, 2.5) BROAD
U2_mains_satfree+N0_asymGL U4f__main_u4f72 (1.5, 3.5) BROAD
U2_mains_satfree+N0_asymGL U4f__main_u4f52 (1.5, 3.5) BROAD
U2_mains_satfree+N0_asymGL U4f__satellite_u4f72 (1.5, 4.5) BROAD
U2_mains_satfree+N0_asymGL U4f__satellite_u4f52 (1.5, 4.5) BROAD
U2_mains_satfree+N0_asymGL N1s__main_n1s (0.7, 2.5) BROAD

2026-07-20T18:57:18.040264Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
The structural guard does catch the old bug when simulated against the previous manual constructor: the only failed preserved field is `broad_justification`. Some alternate region combinations fail before returning candidates because their candidate products mix backgrounds; I’m checking valid composed combinations across the currently registered broad regions.
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import MaterialClass, Phase, resolve\\nphase_for={\"C 1s\": Phase(id=\"C\", material_class=MaterialClass.CONDUCTOR, regions=(\"C 1s\",)), \"B 1s\": Phase(id=\"B\", material_class=MaterialClass.INSULATOR, regions=(\"B 1s\",)), \"Cl 2p\": Phase(id=\"Cl\", material_class=MaterialClass.INSULATOR, regions=(\"Cl 2p\",)), \"N 1s\": Phase(id=\"N\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",)), \"U 4f\": Phase(id=\"U\", material_class=MaterialClass.INSULATOR, regions=(\"U 4f\",))}\\nfor r,p in phase_for.items():\\n    g=resolve([p], r)\\n    print(r, sorted(set(c.background.value for c in g.candidates)), [(c.name,c.background.value) for c in g.candidates[:8]])\\n'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-XJB6RpOH' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-VcrzhXtb' (errno=Operation not permitted)
C 1s ['shirley'] [('A0_graphite_asym_satellite', 'shirley'), ('A1_graphite_asym_sat_plus_CO', 'shirley'), ('A2_graphite_asym_sat_plus_CO_C=O', 'shirley'), ('A3_graphite_asym_sat_plus_CO_C=O_OC=O', 'shirley'), ('A1_linked', 'shirley'), ('A2_linked', 'shirley'), ('A3_linked', 'shirley'), ('A1_linked_offset', 'shirley')]
B 1s ['smart_exp'] [('B1_low', 'smart_exp'), ('B2_low_mid', 'smart_exp'), ('B2b_low_oxide', 'smart_exp'), ('B3_low_mid_oxide', 'smart_exp')]
Cl 2p ['smart_exp'] [('Cl0_doublet', 'smart_exp'), ('Cl0r_doublet_relaxed', 'smart_exp'), ('Cl0w_doublet_freewidth', 'smart_exp'), ('Cl0rw_doublet_relaxed_freewidth', 'smart_exp')]
N 1s ['smart'] [('N0_pv', 'smart'), ('N0_asymGL', 'smart')]
U 4f ['smart'] [('U0_mains', 'smart'), ('U1_mains_satpair', 'smart'), ('U1b_mains_satpair_freesep', 'smart'), ('U2_mains_satfree', 'smart')]

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from itertools import combinations\\nfrom autofit.grammar import MaterialClass, Phase, resolve\\nphase_for={\"C 1s\": Phase(id=\"C\", material_class=MaterialClass.CONDUCTOR, regions=(\"C 1s\",)), \"B 1s\": Phase(id=\"B\", material_class=MaterialClass.INSULATOR, regions=(\"B 1s\",)), \"Cl 2p\": Phase(id=\"Cl\", material_class=MaterialClass.INSULATOR, regions=(\"Cl 2p\",)), \"N 1s\": Phase(id=\"N\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",)), \"U 4f\": Phase(id=\"U\", material_class=MaterialClass.INSULATOR, regions=(\"U 4f\",))}\\nfor n in (2,3):\\n  for regs in combinations(phase_for,n):\\n    try:\\n      g=resolve([phase_for[r] for r in regs], list(regs))\\n    except Exception as e:\\n      continue\\n    broad=[(c.name,s.role,s.fwhm_range) for c in g.candidates for s in c.slots if s.broad_justification is not None]\\n    print(regs, \"OK candidates\", len(g.candidates), \"broad slots\", len(broad), \"sample\", broad[:5])\\n'" in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'import itertools\\nfrom autofit.grammar import MaterialClass, Phase, _compose_joint_candidates, resolve\\nphase_for={\"C 1s\": Phase(id=\"C\", material_class=MaterialClass.CONDUCTOR, regions=(\"C 1s\",)), \"B 1s\": Phase(id=\"B\", material_class=MaterialClass.INSULATOR, regions=(\"B 1s\",)), \"Cl 2p\": Phase(id=\"Cl\", material_class=MaterialClass.INSULATOR, regions=(\"Cl 2p\",)), \"N 1s\": Phase(id=\"N\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",)), \"U 4f\": Phase(id=\"U\", material_class=MaterialClass.INSULATOR, regions=(\"U 4f\",))}\\n# Compose only same-background candidate subsets manually to exercise _retag_slot outside the fixture.\\nfor regs in [(\"C 1s\",\"N 1s\"),(\"B 1s\",\"N 1s\"),(\"U 4f\",\"B 1s\",\"N 1s\")]:\\n    per=[]\\n    for r in regs:\\n        g=resolve([phase_for[r]], r)\\n        per.append(g.candidates)\\n    groups={}\\n    for combo in itertools.product(*per):\\n        if len({c.background for c in combo})==1:\\n            groups.setdefault(combo[0].background.value,[]).append(combo)\\n    print(regs, \"same-bg combos\", {k:len(v) for k,v in groups.items()})\\n    if not groups: continue\\n    bg, combos=next(iter(groups.items()))\\n    # call _compose on a single selected combo per region by wrapping each selected candidate as singleton list\\n    combo=combos[0]\\n    composed=_compose_joint_candidates(list(regs), [[c] for c in combo])\\n    missing=[(c.name,s.role,s.fwhm_range) for c in composed for s in c.slots if s.fwhm_range[1]>2.0 and s.broad_justification is None]\\n    present=[(c.name,s.role,s.fwhm_range) for c in composed for s in c.slots if s.broad_justification is not None]\\n    print(\" selected\", [c.name for c in combo], \"bg\", bg, \"present\", present, \"missing_wide_unvouched\", missing)\\n'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-14ZzSPnA' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-vNHXOsTN' (errno=Operation not permitted)
('B 1s', 'Cl 2p') OK candidates 16 broad slots 64 sample [('B1_low+Cl0_doublet', 'B1s__main_b_low', (1.2, 2.5)), ('B1_low+Cl0_doublet', 'Cl2p__main_cl2p32', (1.2, 2.2)), ('B1_low+Cl0_doublet', 'Cl2p__main_cl2p12', (1.2, 2.2)), ('B1_low+Cl0r_doublet_relaxed', 'B1s__main_b_low', (1.2, 2.5)), ('B1_low+Cl0r_doublet_relaxed', 'Cl2p__main_cl2p32', (1.2, 2.2))]
('N 1s', 'U 4f') OK candidates 8 broad slots 36 sample [('N0_pv+U0_mains', 'N1s__main_n1s', (0.7, 2.5)), ('N0_pv+U0_mains', 'U4f__main_u4f72', (1.5, 3.5)), ('N0_pv+U0_mains', 'U4f__main_u4f52', (1.5, 3.5)), ('N0_pv+U1_mains_satpair', 'N1s__main_n1s', (0.7, 2.5)), ('N0_pv+U1_mains_satpair', 'U4f__main_u4f72', (1.5, 3.5))]

 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-JdTlilNw' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-F61aCybE' (errno=Operation not permitted)
('C 1s', 'N 1s') same-bg combos {}
('B 1s', 'N 1s') same-bg combos {}
('U 4f', 'B 1s', 'N 1s') same-bg combos {}

2026-07-20T18:57:46.219743Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
Valid full `resolve()` compositions among broad-region modules are currently `B 1s + Cl 2p` and `N 1s + U 4f`; cross-background pairs fail by design. I’m using `B 1s + Cl 2p` as the extra non-fixture combination, and I’ll also check whether a same-background three-phase composition is supported through target-phase disambiguation.
exec
/bin/zsh -lc 'rg -n "def resolve|target_phases|requests" autofit/grammar.py' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
18:caller MUST disambiguate with ``target_phases`` (Codex precondition 2 — a
243:def _parse_region_requests(
264:def resolve(
268:    target_phases: Optional[dict[str, str]] = None,
278:    regions         : region requests for one (possibly joint) fit window.
285:    target_phases   : {region: phase_id} disambiguation for UNqualified
286:                      requests of a region contributed by more than one phase
314:    requests = _parse_region_requests(regions)
317:    if not requests:
319:    target_phases = target_phases or {}
328:    for region, _ in requests:
333:    slugs: list[str] = []            # module-backed requests (composition)
341:    for region, explicit_phase in requests:
357:            tid = target_phases.get(region)
363:                    f"target_phases={{{region!r}: <phase_id>}} "
478:    # Composition runs over MODULE-BACKED requests only: a structural-
490:    if structural_regions and len(requests) > 1:
497:        regions=tuple(region for region, _ in requests),

exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '240,485p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   240	RegionRequest = "str | tuple[str, str]"  # region name, or (region, phase_id)
   241	
   242	
   243	def _parse_region_requests(
   244	    regions: "list[str | tuple[str, str]] | str | tuple[str, str]",
   245	) -> list[tuple[str, Optional[str]]]:
   246	    if isinstance(regions, str):
   247	        return [(regions, None)]
   248	    if isinstance(regions, tuple) and len(regions) == 2 \
   249	            and all(isinstance(v, str) for v in regions):
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

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import MaterialClass, Phase, resolve\\nphases=[Phase(id=\"B\", material_class=MaterialClass.INSULATOR, regions=(\"B 1s\",)), Phase(id=\"Cl\", material_class=MaterialClass.INSULATOR, regions=(\"Cl 2p\",))]\\ng=resolve(phases,[\"B 1s\",\"Cl 2p\"])\\nmissing=[(c.name,s.role,s.fwhm_range) for c in g.candidates for s in c.slots if s.fwhm_range[1]>2.0 and s.broad_justification is None]\\npresent=[(c.name,s.role,s.fwhm_range) for c in g.candidates for s in c.slots if s.broad_justification is not None]\\nprint(\"B+Cl candidates\",len(g.candidates),\"present\",len(present),\"missing_wide_unvouched\",missing)\\nprint(\"sample\",present[:10])\\n'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-47q355HM' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-75Fa2uCx' (errno=Operation not permitted)
B+Cl candidates 16 present 64 missing_wide_unvouched []
sample [('B1_low+Cl0_doublet', 'B1s__main_b_low', (1.2, 2.5)), ('B1_low+Cl0_doublet', 'Cl2p__main_cl2p32', (1.2, 2.2)), ('B1_low+Cl0_doublet', 'Cl2p__main_cl2p12', (1.2, 2.2)), ('B1_low+Cl0r_doublet_relaxed', 'B1s__main_b_low', (1.2, 2.5)), ('B1_low+Cl0r_doublet_relaxed', 'Cl2p__main_cl2p32', (1.2, 2.2)), ('B1_low+Cl0r_doublet_relaxed', 'Cl2p__main_cl2p12', (1.2, 2.2)), ('B1_low+Cl0w_doublet_freewidth', 'B1s__main_b_low', (1.2, 2.5)), ('B1_low+Cl0w_doublet_freewidth', 'Cl2p__main_cl2p32', (1.2, 2.2)), ('B1_low+Cl0w_doublet_freewidth', 'Cl2p__main_cl2p12', (1.2, 3.0)), ('B1_low+Cl0rw_doublet_relaxed_freewidth', 'B1s__main_b_low', (1.2, 2.5))]

2026-07-20T18:58:01.501828Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
`B 1s + Cl 2p` is a useful extra case: 16 composed candidates, 64 broad/vouched slots, and no wide unvouched slots in that composition. I’m reading the tail of `resolve()` to confirm there isn’t a second retagging/copy pass after composition.
exec
/bin/zsh -lc "nl -ba autofit/grammar.py | sed -n '485,545p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
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

exec
/bin/zsh -lc 'git grep -n "replace(" ad7e668 -- autofit tests || true' in /Users/skyefortier/xps-verify
exec
/bin/zsh -lc 'git grep -n "ComponentSlot(" ad7e668 -- autofit tests || true' in /Users/skyefortier/xps-verify
 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-wIcGDPAu' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-HRdRrIM9' (errno=Operation not permitted)
ad7e668:autofit/engine.py:2446:        model=dataclasses.replace(report.model, name=report.model.name + "+bfix"),
ad7e668:autofit/grammar.py:469:    sanitized = [re.sub(r"[^A-Za-z0-9_]", "", s.replace(" ", ""))
ad7e668:autofit/grammar.py:568:            slug = re.sub(r"[^A-Za-z0-9_]", "", slug.replace(" ", ""))
ad7e668:autofit/grammar.py:592:    reconstructing the slot field-by-field: replace() carries every field
ad7e668:autofit/grammar.py:616:    return replace(
ad7e668:tests/autofit/test_bayesian_real_gate.py:72:    assert ic.diagnostics["winner"].replace("+bfix", "") == \
ad7e668:tests/autofit/test_broad_justification.py:100:# switching _retag_slot to dataclasses.replace(). This fixture exercises the
ad7e668:tests/autofit/test_fit_physics.py:48:    src = open(GEN).read().replace(
ad7e668:tests/autofit/test_fit_physics.py:50:        f'OUT = {str(out)!r}').replace(
ad7e668:tests/autofit/test_preseed_dominants.py:335:    promoted = dataclasses.replace(
ad7e668:tests/autofit/test_stage2_completeness.py:257:    stab = dataclasses.replace(report.stability, per_slot=bad_slots,
ad7e668:tests/autofit/test_stage2_completeness.py:261:    return dataclasses.replace(report, stability=stab, plausibility=plaus)
ad7e668:tests/autofit/test_stage2_completeness.py:350:    cond = dataclasses.replace(
ad7e668:tests/js/find_peaks_coverage.test.js:84:  assert.match(label, new RegExp(FP_TIER_META.curated.tag.replace(/[[\]]/g, '\\$&')));
ad7e668:tests/js/fp_material_mixed.test.js:25:    .replace(/^const FP_STRINGS = /, '').replace(/;$/, '') + ')');
ad7e668:tests/test_expand_coverage.py:49:        strip = lambda c: re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip()

 succeeded in 0ms:
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-cJ0yG7qv' (errno=Operation not permitted)
git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
git: error: couldn't create cache file '/tmp/xcrun_db-lwqT255p' (errno=Operation not permitted)
ad7e668:autofit/candidates.py:463:        slots.append(ComponentSlot(
ad7e668:autofit/engine.py:1901:        ComponentSlot(
ad7e668:autofit/engine.py:2110:    proposed = ComponentSlot(
ad7e668:autofit/regions/b1s.py:92:            return ComponentSlot(
ad7e668:autofit/regions/c1s.py:309:            return ComponentSlot(
ad7e668:autofit/regions/cl2p.py:143:            return ComponentSlot(
ad7e668:autofit/regions/cl2p.py:154:                return ComponentSlot(
ad7e668:autofit/regions/cl2p.py:166:            return ComponentSlot(
ad7e668:autofit/regions/n1s.py:76:        pv_main = ComponentSlot(
ad7e668:autofit/regions/n1s.py:82:        ag_main = ComponentSlot(
ad7e668:autofit/regions/u4f.py:197:            return ComponentSlot(
ad7e668:tests/autofit/stress_cases.py:108:    return ComponentSlot(role=role, region=REGION, phase_id=PHASE,
ad7e668:tests/autofit/test_bayesian_method.py:29:    return ComponentSlot(role=role, region="T", phase_id="t",
ad7e668:tests/autofit/test_broad_justification.py:183:    original = ComponentSlot(**sentinel_by_field)
ad7e668:tests/autofit/test_broad_justification.py:276:    wide_no_justification = ComponentSlot(
ad7e668:tests/autofit/test_broad_justification.py:299:    narrow_but_justified = ComponentSlot(
ad7e668:tests/autofit/test_broad_justification.py:317:    s = ComponentSlot(role="r", region="Test", phase_id="s",
ad7e668:tests/autofit/test_cl2p_freewidth.py:131:    return ComponentSlot(role=role, **defaults)
ad7e668:tests/autofit/test_criteria.py:23:    return ComponentSlot(role=role, region="T", phase_id="t",
ad7e668:tests/autofit/test_engine_doublet.py:23:    p32 = ComponentSlot(
ad7e668:tests/autofit/test_engine_doublet.py:28:    p12 = ComponentSlot(
ad7e668:tests/autofit/test_engine_doublet.py:127:        return ComponentSlot(
ad7e668:tests/autofit/test_fit_full_window_option.py:41:    return ComponentSlot(role=role, region=region, phase_id="p",
ad7e668:tests/autofit/test_preseed_dominants.py:179:        return ComponentSlot(role=role, region="r", phase_id="p",
ad7e668:tests/autofit/test_preseed_dominants.py:216:    slot = ComponentSlot(role="wide_unvouched", region="r", phase_id="p",
ad7e668:tests/autofit/test_preseed_dominants.py:293:    slot = ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
ad7e668:tests/autofit/test_preseed_dominants.py:397:        return ComponentSlot(role=role, region="unassigned", phase_id="unassigned",
ad7e668:tests/autofit/test_resolver.py:107:        main = ComponentSlot(
ad7e668:tests/autofit/test_resolver.py:112:        doublet = ComponentSlot(
ad7e668:tests/autofit/test_sparse_map.py:28:    return ComponentSlot(role=role, region="T", phase_id="t",
ad7e668:tests/autofit/test_stage2_completeness.py:293:    slot = ComponentSlot(role="main_g", region="r", phase_id="p",
ad7e668:tests/autofit/test_stage2_completeness.py:317:    slot = ComponentSlot(role="detected_peak_0", region="unassigned",
ad7e668:tests/autofit/test_stage2_completeness.py:369:    slot = ComponentSlot(role="main_g", region="r", phase_id="p",

exec
/bin/zsh -lc 'PYTHONDONTWRITEBYTECODE=1 python3 -c $'"'from autofit.grammar import MaterialClass, Phase, resolve\\nphases=[Phase(id=\"U\", material_class=MaterialClass.INSULATOR, regions=(\"U 4f\",)), Phase(id=\"N\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",)), Phase(id=\"N2\", material_class=MaterialClass.INSULATOR, regions=(\"N 1s\",))]\\ntry:\\n    g=resolve(phases,[\"U 4f\",(\"N 1s\",\"N\"),(\"N 1s\",\"N2\")])\\n    missing=[(c.name,s.role,s.fwhm_range) for c in g.candidates for s in c.slots if s.fwhm_range[1]>2.0 and s.broad_justification is None]\\n    present=[(c.name,s.role,s.fwhm_range) for c in g.candidates for s in c.slots if s.broad_justification is not None]\\n    print(\"3-phase U+N+N2 candidates\",len(g.candidates),\"present\",len(present),\"missing\",missing[:10])\\n    print(\"sample\",present[:8])\\nexcept Exception as e:\\n    print(\"ERROR\",type(e).__name__,str(e))\\n'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-kmbLc8vA' (errno=Operation not permitted)
python3: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead
python3: error: couldn't create cache file '/tmp/xcrun_db-A6pVimUp' (errno=Operation not permitted)
3-phase U+N+N2 candidates 16 present 88 missing []
sample [('U0_mains+N0_pv+N0_pv', 'U4f__main_u4f72', (1.5, 3.5)), ('U0_mains+N0_pv+N0_pv', 'U4f__main_u4f52', (1.5, 3.5)), ('U0_mains+N0_pv+N0_pv', 'N1sN__main_n1s', (0.7, 2.5)), ('U0_mains+N0_pv+N0_pv', 'N1sN2__main_n1s', (0.7, 2.5)), ('U0_mains+N0_pv+N0_asymGL', 'U4f__main_u4f72', (1.5, 3.5)), ('U0_mains+N0_pv+N0_asymGL', 'U4f__main_u4f52', (1.5, 3.5)), ('U0_mains+N0_pv+N0_asymGL', 'N1sN__main_n1s', (0.7, 2.5)), ('U0_mains+N0_pv+N0_asymGL', 'N1sN2__main_n1s', (0.7, 2.5))]

2026-07-20T18:58:14.753032Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
One nuance in the detection branch: `_unphysical_width_flags` keys the DS+G/asym-GL special cases off the fitted component’s `line_shape` before checking `detected_peak_`. I’m checking whether production detection slots can ever produce those shapes; if not, that is not a live regression.
exec
/bin/zsh -lc "rg -n \"FittedComponent\\(|line_shape=slot\\.line_shape|line_shape=|components.append|return FitOutcome\" autofit/engine.py" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
675:        out.append(FittedComponent(
678:            line_shape=slot.line_shape,
912:        return FitOutcome(
920:    return FitOutcome(
1076:            orphans.append(FittedComponent(
1079:                line_shape=comp.line_shape,
1094:        claimed = FittedComponent(
1097:            line_shape=comp.line_shape,
1906:            line_shape=PROPOSED_PEAK_SHAPE,
2078:            line_shape=PROPOSED_PEAK_SHAPE,
2115:        line_shape=spec.line_shape,

exec
/bin/zsh -lc "nl -ba autofit/engine.py | sed -n '640,725p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   640	
   641	
   642	@dataclass
   643	class FitOutcome:
   644	    converged: bool
   645	    components: list[FittedComponent]
   646	    residual_sum_sq: float
   647	    weighted_chi_sq: float
   648	    n_params: int
   649	    n_data: int
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
   691	    LineShape.DS_G: frozenset({"alpha"}),          # beta is a WIDTH here — counted
   692	    LineShape.LACX: frozenset({"alpha", "beta"}),  # both are exponents here
   693	}
   694	
   695	
   696	def _role_for_param(pname: str, role_by_prefix: dict[str, str]) -> Optional[str]:
   697	    for prefix in sorted(role_by_prefix, key=len, reverse=True):
   698	        if pname.startswith(prefix):
   699	            return role_by_prefix[prefix]
   700	    return None
   701	
   702	
   703	def _detect_boundary_hits(params: Parameters, model: CandidateModel) -> list[str]:
   704	    """Varying params within 1% of a finite bound → 'role:param@min|max'."""
   705	    hits: list[str] = []
   706	    role_by_prefix = {_slot_prefix(s.role): s.role for s in model.slots}
   707	    shape_by_role = {s.role: s.line_shape for s in model.slots}
   708	
   709	    for pname, par in params.items():
   710	        if not par.vary:
   711	            continue
   712	        lo, hi = par.min, par.max
   713	        if not (np.isfinite(lo) and np.isfinite(hi)) or hi <= lo:
   714	            continue
   715	        tol = 0.01 * (hi - lo)
   716	        at_min = (par.value - lo) < tol
   717	        at_max = (hi - par.value) < tol
   718	        if not (at_min or at_max):
   719	            continue
   720	        role = _role_for_param(pname, role_by_prefix)
   721	        short = pname[len(_slot_prefix(role)):] if role is not None else pname
   722	        shape = shape_by_role.get(role)
   723	        if shape is not None and short in _BOUNDARY_EXCLUDED.get(shape, frozenset()):
   724	            continue
   725	        # amplitude at min (=0) → component absent: surfaced via stability

exec
/bin/zsh -lc "nl -ba tests/autofit/test_stage2_completeness.py | sed -n '305,330p'" in /Users/skyefortier/xps-verify
 succeeded in 0ms:
   305	                           line_shape=LineShape.DS_G)
   306	    assert eng._unphysical_width_flags([thin], m) == []
   307	
   308	
   309	def test_detection_slot_absorbing_width_flagged():
   310	    """A detection-family component fitted at ≥70% of its scale-relative
   311	    ceiling (= 1.75× its detected width) is absorbing neighbors — the
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

2026-07-20T18:58:31.625733Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 86 column 5
codex
1. No findings.

Verified:
- Original repro now preserves `broad_justification` for `U4f__main_u4f72`, `U4f__main_u4f52`, `N1s__main_n1s`, and U 4f satellite slots in composed U 4f + N 1s candidates. `_retag_slot` now uses `replace(...)` at `autofit/grammar.py:616`.
- Grep found no other production site that copies and modifies an existing `ComponentSlot`; the other production `ComponentSlot(...)` sites are fresh construction in `autofit/candidates.py:463`, `autofit/engine.py:1901`, `autofit/engine.py:2110`, plus region-module constructors.
- Extra composition check: `B 1s + Cl 2p` produced 16 composed candidates with 64 vouched broad slots and no wide unvouched carry-through losses. A 3-phase `U 4f + N 1s + N 1s` composition also preserved all broad justifications.
- Structural guard works: simulating the old manual `_retag_slot` caused exactly `broad_justification` to be lost; current `_retag_slot` preserves it.
- `PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV` exactly at `autofit/engine.py:116` and `autofit/engine.py:120`.
- Detection slots are constructed as `PSEUDO_VOIGT` at `autofit/candidates.py:468`; fitted components inherit slot line shape at `autofit/engine.py:675-678`; `_unphysical_width_flags` returns from the `detected_peak_` branch before the generic `broad_justification` exemption branch at `autofit/engine.py:832-840`.
- Scope confirmed: `ad7e668` touches only `autofit/grammar.py` and `tests/autofit/test_broad_justification.py`.

I could not run pytest here because `pytest` and `lmfit` are not installed in this sandbox, but the grammar-level repros and structural simulation ran successfully.

VERDICT: GO
tokens used
77,088
1. No findings.

Verified:
- Original repro now preserves `broad_justification` for `U4f__main_u4f72`, `U4f__main_u4f52`, `N1s__main_n1s`, and U 4f satellite slots in composed U 4f + N 1s candidates. `_retag_slot` now uses `replace(...)` at `autofit/grammar.py:616`.
- Grep found no other production site that copies and modifies an existing `ComponentSlot`; the other production `ComponentSlot(...)` sites are fresh construction in `autofit/candidates.py:463`, `autofit/engine.py:1901`, `autofit/engine.py:2110`, plus region-module constructors.
- Extra composition check: `B 1s + Cl 2p` produced 16 composed candidates with 64 vouched broad slots and no wide unvouched carry-through losses. A 3-phase `U 4f + N 1s + N 1s` composition also preserved all broad justifications.
- Structural guard works: simulating the old manual `_retag_slot` caused exactly `broad_justification` to be lost; current `_retag_slot` preserves it.
- `PROPOSAL_FWHM_MAX = FWHM_MAX_ORDINARY_EV` exactly at `autofit/engine.py:116` and `autofit/engine.py:120`.
- Detection slots are constructed as `PSEUDO_VOIGT` at `autofit/candidates.py:468`; fitted components inherit slot line shape at `autofit/engine.py:675-678`; `_unphysical_width_flags` returns from the `detected_peak_` branch before the generic `broad_justification` exemption branch at `autofit/engine.py:832-840`.
- Scope confirmed: `ad7e668` touches only `autofit/grammar.py` and `tests/autofit/test_broad_justification.py`.

I could not run pytest here because `pytest` and `lmfit` are not installed in this sandbox, but the grammar-level repros and structural simulation ran successfully.

VERDICT: GO
